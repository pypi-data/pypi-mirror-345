import asyncio
import json
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
from loguru import logger
from optrabot.managedtrade import ManagedTrade
from optrabot.broker.brokerconnector import BrokerConnector
from optrabot import crud, schemas
from optrabot.optionhelper import OptionHelper
from optrabot.broker.brokerfactory import BrokerFactory
from optrabot.broker.order import Execution, OptionRight, Order, OrderAction, OrderStatus, OrderType
from optrabot.database import get_db_engine
import optrabot.symbolinfo as symbolInfo
from optrabot.stoplossadjuster import StopLossAdjuster
from optrabot.tradehelper import SecurityStatusData, TradeHelper
from optrabot.tradetemplate.templatefactory import Template
from optrabot.util.singletonmeta import SingletonMeta
from sqlalchemy.orm import Session
from typing import List	

class TradeManager(metaclass=SingletonMeta):
	"""
	The Trade Manager is a singleton class which is responsible for opening new trades and
	managing existing trades. It is monitoring the open trades and their attachde orders.
	"""
	def __init__(self):
		self._trades: List[ManagedTrade] = []
		self._backgroundScheduler = AsyncIOScheduler()
		self._backgroundScheduler.start()
		# Start monitoring of open trades in next 5 seconds mark
		now = datetime.now()
		next_run_time = (now + timedelta(seconds=(5 - now.second % 5))).replace(microsecond=0)
		self._backgroundScheduler.add_job(self._monitorOpenTrades, 'interval', seconds=5, id='MonitorOpenTrades', misfire_grace_time = None, next_run_time=next_run_time)
		self._backgroundScheduler.add_job(self._performEODTasks, 'cron', hour=16, minute=00, timezone=pytz.timezone('US/Eastern'), id='EODTasks', misfire_grace_time = None)
		self._backgroundScheduler.add_job(self._performEODSettlement, 'cron', hour=16, minute=34, timezone=pytz.timezone('US/Eastern'), id='EODSettlement', misfire_grace_time = None)
		BrokerFactory().orderStatusEvent += self._onOrderStatusChanged
		BrokerFactory().commissionReportEvent += self._onCommissionReportEvent
		BrokerFactory().orderExecutionDetailsEvent += self._onOrderExecutionDetailsEvent
		self._lock = asyncio.Lock()
		self._execution_transaction_map = {} # Maps the Execution ID to the Transaction ID
		self._last_trade_monitoring_time = datetime.now()	# Timestamp of last Trade monitoring

	def shutdown(self):
		"""
		Shutdown the TradeManager. Background scheduler will be stopped
		"""
		logger.debug('Shutting down TradeManager')
		self._backgroundScheduler.remove_all_jobs()
		self._backgroundScheduler.shutdown()

	async def openTrade(self, entryOrder: Order, template: Template):
		brokerConnector = BrokerFactory().getBrokerConnectorByAccount(template.account)
		if brokerConnector == None:
			logger.error(f'No active broker connection found for account {template.account}. Unable to place entry order.')
			return
		
		if brokerConnector.isConnected() == False:
			logger.error(f'Broker connection for account {template.account} is not connected. Unable to place entry order.')
			return
		
		if template.maxOpenTrades > 0:
			openTrades = 0
			for managedTrade in self._trades:
				if managedTrade.template == template and managedTrade.status == 'OPEN':
					openTrades += 1
			if openTrades >= template.maxOpenTrades:
				logger.warning(f'Maximum number of open trades for template {template.name} reached. Unable to place new trade.')
				return

		if brokerConnector.isTradingEnabled() == False:
			logger.error(f'Trading is disabled for account {template.account}. Unable to place entry order.')
			return
		
		orderPrepared = await brokerConnector.prepareOrder(entryOrder)
		if orderPrepared != True:
			logger.error(f'Failed to prepare entry order for account {template.account}. Unable to place entry order.')
			return
		
		logger.info(f'Opening trade at strikes {self._strikes_from_order(entryOrder)}')

		# Midprice calculation and minimum premium check
		entryOrder.price = self._calculateMidPrice(brokerConnector, entryOrder)
		logger.info(f'Calculated midprice for entry order: {entryOrder.price}')
		if template.meetsMinimumPremium(entryOrder.price) == False:
			logger.error(f'Entry order for account {template.account} does not meet minimum premium requirement. Unable to place entry order')
			return

		# Create the Trade in the database
		async with self._lock: # Mit Lock arbeiten, damit die Trade IDs nicht doppelt vergeben werden
			with Session(get_db_engine()) as session:
				newTradeSchema = schemas.TradeCreate(account=template.account, symbol=entryOrder.symbol, strategy=template.strategy)
				newTrade = crud.create_trade(session, newTradeSchema)
			newManagedTrade = ManagedTrade(trade=newTrade, entryOrder=entryOrder, template=template, account=template.account)
			self._trades.append(newManagedTrade)
		entryOrder.orderReference = self._composeOrderReference(newManagedTrade, 'Open')
		entryOrderPlaced = await brokerConnector.placeOrder(newManagedTrade, entryOrder)
		if entryOrderPlaced == True:
			logger.debug(f'Entry order for account placed. Now track its execution')
			entryOrder.status = OrderStatus.OPEN
			#asyncio.create_task(self._trackEntryOrder(newManagedTrade), name='TrackEntryOrder' + str(newManagedTrade.trade.id))
			self._backgroundScheduler.add_job(self._trackEntryOrder, 'interval', seconds=5, id='TrackEntryOrder' + str(newManagedTrade.trade.id), args=[newManagedTrade], max_instances=1, misfire_grace_time=None)

	def _onCommissionReportEvent(self, order: Order, execution_id: str, commission: float, fee: float):
		"""
		Handles the commission and fee reporting event from the Broker Connector.
		It adds the commission and fee to the transaction in the database.
		"""
		# Determine the transaction based on the execution ID
		try:
			transaction_id = self._execution_transaction_map.get(execution_id)
		except KeyError:
			logger.error(f'No trade transaction found for fill execution id {execution_id}')
			return
		
		for managed_trade in self._trades:
			if order == managed_trade.entryOrder or order == managed_trade.takeProfitOrder or order == managed_trade.stopLossOrder:
				logger.debug(f'Trade {managed_trade.trade.id}: Commission Report for Order received. Commission: {commission} Fee: {fee}')
				with Session(get_db_engine()) as session:
					db_trade = crud.getTrade(session, managed_trade.trade.id)
					transaction = crud.getTransactionById(session, managed_trade.trade.id, transaction_id)
					if transaction == None:
						logger.error('Transaction with id {} for trade {} not found in database!', transaction_id, managed_trade.trade.id)
						return
					transaction.commission += commission
					transaction.fee = +fee
					TradeHelper.updateTrade(db_trade)
					session.commit()
					logger.debug(f'Commissions saved to transaction {transaction.id} for trade {managed_trade.trade.id}')
				break

	def _onOrderExecutionDetailsEvent(self, order: Order, execution: Execution):
		"""
		Handles the order execution details which are sent from the Broker Connector
		when a order has been executed.
		"""
		logger.debug(f'Trade Manager Order Execution Details:')
		for managed_trade in self._trades:
			if order == managed_trade.entryOrder or order == managed_trade.takeProfitOrder or order == managed_trade.stopLossOrder:
				if order == managed_trade.entryOrder:
					logger.debug(f'Trade {managed_trade.trade.id}: Execution Details for Entry Order received')
				with Session(get_db_engine()) as session:
					max_transaction_id = crud.getMaxTransactionId(session, managed_trade.trade.id)
					db_trade = crud.getTrade(session, managed_trade.trade.id)
					if max_transaction_id == 0:
						# Opening transaction of the trade
						db_trade.status = 'OPEN'
					elif order == managed_trade.takeProfitOrder or order == managed_trade.stopLossOrder:
						# Set status to closed if take profit or stop loss order is filled, in order to prevent them to be reestablished
						# by the monitorOpenTrades background job.
						managed_trade.status = 'CLOSED'
					max_transaction_id += 1
					new_transaction = schemas.TransactionCreate(tradeid=managed_trade.trade.id, transactionid=max_transaction_id,
																id=max_transaction_id,
																symbol=order.symbol,
																type=execution.action,
																sectype=execution.sec_type,
																contracts=execution.amount,
																price=execution.price, 
																expiration=execution.expiration,
																strike=execution.strike,
																fee=0,
																commission=0,
																notes='',
																timestamp=execution.timestamp)
					self._execution_transaction_map[execution.id] = new_transaction.id # Memorize the the Execution ID for later commission report
					crud.createTransaction(session, new_transaction)
					managed_trade.transactions.append(new_transaction)

					# Check if trade is closed with all these transactions
					TradeHelper.updateTrade(db_trade)
					session.commit()
					if order == managed_trade.entryOrder:
						self._backgroundScheduler.add_job(self._reportExecutedTrade, id='ReportTrade' + str(managed_trade.trade.id) + '-' + execution.id, args=[managed_trade, execution.amount], misfire_grace_time = None, max_instances=100)

	async def _onOrderStatusChanged(self, order: Order, status: OrderStatus, filledAmount: int = 0):
		"""
		Handles the status change event of an order
		"""
		from optrabot.tradinghubclient import TradinghubClient, NotificationType
		logger.debug(f'Trade Manager Order status changed: {order.symbol} - {status}')
		for managedTrade in self._trades:
			brokerConnector = BrokerFactory().getBrokerConnectorByAccount(managedTrade.template.account)
			if managedTrade.entryOrder == order:
				if status == OrderStatus.CANCELLED and managedTrade.status != 'OPEN':
					managedTrade.entryOrder.status = OrderStatus.CANCELLED
					logger.debug(f'Entry order for trade {managedTrade.trade.id} was cancelled. Deleting trade from databsase')
					try:
						self._backgroundScheduler.remove_job('TrackEntryOrder' + str(managedTrade.trade.id))
					except Exception as e:
						pass
					with Session(get_db_engine()) as session:
						crud.delete_trade(session, managedTrade.trade)
					self._trades.remove(managedTrade)
				if status == OrderStatus.FILLED:
					managedTrade.entryOrder.status = OrderStatus.FILLED
					logger.info(f'Entry Order of trade {managedTrade.trade.id} has been filled at ${managedTrade.entryOrder.averageFillPrice} (Qty: {filledAmount}) and trade is now running.' )
					if managedTrade.status != 'OPEN':
						managedTrade.status = 'OPEN'
						managedTrade.trade.status = 'OPEN'
						with Session(get_db_engine()) as session:
							crud.update_trade(session, managedTrade.trade)

						logger.debug('Create TP SL Order Job')
						self._backgroundScheduler.add_job(self._createTakeProfitAndStop, id='CreateTakeProfitAndStop' + str(managedTrade.trade.id), args=[managedTrade], misfire_grace_time = None)

						# Send Telegram Notification via OptraBot Server
						await TradinghubClient().send_notification(NotificationType.INFO, f'🚀 Trade {managedTrade.trade.id} opened at {brokerConnector.broker}.\n*Strategy:* {managedTrade.template.strategy}\n*Strikes:* {self._strikes_from_order(managedTrade.entryOrder)}\n*Account:* {managedTrade.account}\n*Price:* ${managedTrade.entryOrder.averageFillPrice:.2f}\n*Quantity:* {filledAmount}')
					else:
						logger.debug('Trade is already open. No need to create TP SL Order Job')
			elif managedTrade.takeProfitOrder == order:
				if status == OrderStatus.FILLED:
					managedTrade.takeProfitOrder.status = OrderStatus.FILLED
					logger.debug(f'Take Profit order for trade {managedTrade.trade.id} was filled. Closing trade now')
					managedTrade.status = 'CLOSED'
					managedTrade.trade.status = 'CLOSED'
					with Session(get_db_engine()) as session:
						crud.update_trade(session, managedTrade.trade)
					logger.success('Take Profit Order has been filled. Trade with id {} finished', managedTrade.trade.id)
					await TradinghubClient().send_notification(NotificationType.INFO, f'🎯 Trade {managedTrade.trade.id}\n*Take Profit* order executed at ${order.averageFillPrice:.2f}.') 
				elif status == OrderStatus.CANCELLED:
					managedTrade.takeProfitOrder.status = OrderStatus.CANCELLED
					logger.debug(f'Take Profit order for trade {managedTrade.trade.id} was cancelled.')
				if status == OrderStatus.FILLED or status == OrderStatus.CANCELLED:
					if not brokerConnector.uses_oco_orders() and managedTrade.stopLossOrder:
						logger.info(f'Trade {managedTrade.trade.id} does not use OCO orders. Cancelling Stop Loss order')
						await brokerConnector.cancel_order(managedTrade.stopLossOrder)

			elif managedTrade.stopLossOrder == order:
				if status == OrderStatus.FILLED:
					managedTrade.stopLossOrder.status = OrderStatus.FILLED
					logger.debug(f'Stop Loss order for trade {managedTrade.trade.id} was filled. Closing trade now')
					managedTrade.status = 'CLOSED'
					managedTrade.trade.status = 'CLOSED'
					with Session(get_db_engine()) as session:
						crud.update_trade(session, managedTrade.trade)
					logger.error('Stop Loss Order has been filled. Trade with id {} finished', managedTrade.trade.id)
					await TradinghubClient().send_notification(NotificationType.INFO, f'🏁 Trade {managedTrade.trade.id}\n*Stop Loss* order executed at ${order.averageFillPrice:.2f}.') 
				elif status == OrderStatus.CANCELLED:
					managedTrade.stopLossOrder.status = OrderStatus.CANCELLED
					logger.debug(f'Stop Loss order for trade {managedTrade.trade.id} was cancelled')
				if status == OrderStatus.FILLED or status == OrderStatus.CANCELLED:
					if not brokerConnector.uses_oco_orders() and managedTrade.takeProfitOrder:
						logger.info(f'Trade {managedTrade.trade.id} does not use OCO orders. Cancelling Take Profit order')
						await brokerConnector.cancel_order(managedTrade.takeProfitOrder)


	def getManagedTrades(self) -> List[ManagedTrade]:
		"""
		Returns a list of all trades currenty managed by the TradeManager 
		"""
		return self._trades
	
	def _calculateMidPrice(self, broker_connector: BrokerConnector, order: Order) -> float:
		"""
		Calculates the midprice for the given order
		"""
		midPrice = 0
		for leg in order.legs:
			legMidPrice = (leg.askPrice + leg.bidPrice) / 2
			if leg.action == OrderAction.SELL:
				midPrice -= legMidPrice
			else:
				midPrice += legMidPrice
		return self._round_order_price(broker_connector, order, midPrice)
	
	async def _check_and_adjust_stoploss(self, managedTrade: ManagedTrade):
		"""
		Checks if there are Stop Loss adjusters in the template of the trade and if any adjustment of the stop loss is required.
		If so it performs the adjustment of the stoploss order.

		If the trade is a credit trade and multi legged and the a long leg of the stop loss order got no bid price
		anymore because of declining value, the leg needs to be removed from the Stop Loss order.
		"""
		broker_connector = BrokerFactory().getBrokerConnectorByAccount(managedTrade.template.account)
		assert broker_connector != None
		if len(managedTrade.stoploss_adjusters) > 0:
			adjuster_index = 0
			for adjuster in managedTrade.stoploss_adjusters:
				# Find first adjuster which has not been triggered yet
				adjuster_index += 1
				if not adjuster.isTriggered():
					logger.debug(f'Checking {adjuster_index}. SL adjuster for trade {managedTrade.trade.id} at profit level {adjuster._trigger}%')
					adjusted_stoploss_price = adjuster.execute(managedTrade.current_price)
					if adjusted_stoploss_price:
						adjusted_stoploss_price = self._round_order_price(broker_connector, managedTrade.stopLossOrder, adjusted_stoploss_price)
						logger.info(f'{adjuster_index}. Stoploss adjustment for trade {managedTrade.trade.id} at profit level {adjuster._trigger}% to ${adjusted_stoploss_price:.2f}')
						if managedTrade.template.is_credit_trade() == False and adjusted_stoploss_price <= 0:
							# Stop Loss order has not been placed yet.
							logger.info(f'Stoploss price is invalid. Not placing stop loss order for trade {managedTrade.trade.id}')
							break
						
						if managedTrade.stopLossOrder.status == None:
							# Stop Loss order has not been placed yet.
							managedTrade.stopLossOrder.price = adjusted_stoploss_price
							order_placed = await broker_connector.placeOrder(managedTrade, managedTrade.stopLossOrder, parent_order = managedTrade.entryOrder)
							if order_placed == True:
								managedTrade.stopLossOrder.status = OrderStatus.OPEN
						else:
							await broker_connector.adjustOrder(managedTrade, managedTrade.stopLossOrder, adjusted_stoploss_price)
					break
		if managedTrade.template.is_credit_trade() and len(managedTrade.stopLossOrder.legs) > 1:
			for leg in managedTrade.stopLossOrder.legs:
				if leg.action == OrderAction.BUY: # Watch long leg
					strike_price_data = broker_connector.get_option_strike_price_data(leg.symbol, leg.expiration, leg.strike)
					bid_price = strike_price_data.callBid if leg.right == OptionRight.CALL else strike_price_data.putBid
					if bid_price <= 0:
						# This leg needs to be removed from the stop loss order
						logger.info(f'Long leg of stop loss order at strike {leg.strike} for trade {managedTrade.trade.id} has no bid price anymore. Removing leg from stop loss order.')
						managedTrade.stopLossOrder.legs.remove(leg)
						managedTrade.long_legs_removed = True
						await broker_connector.cancel_order(managedTrade.stopLossOrder) # Cancel the old order. Order Monitoring will create new one

			if managedTrade.long_legs_removed:
				# The remaining Short legs must be reverted
				for leg in managedTrade.stopLossOrder.legs:
					if leg.action == OrderAction.SELL:
						leg.action = OrderAction.BUY
					else:
						leg.action = OrderAction.SELL
				if managedTrade.template.is_credit_trade():
					if managedTrade.stopLossOrder:
						managedTrade.stopLossOrder.price = managedTrade.stopLossOrder.price * -1
						if managedTrade.stopLossOrder.action == OrderAction.SELL_TO_CLOSE:
							managedTrade.stopLossOrder.action = OrderAction.BUY_TO_CLOSE
						else:
							managedTrade.stopLossOrder.action = OrderAction.SELL_TO_CLOSE
					if managedTrade.takeProfitOrder:
						managedTrade.takeProfitOrder.price = managedTrade.takeProfitOrder.price * -1
						if managedTrade.takeProfitOrder.action == OrderAction.SELL_TO_CLOSE:
							managedTrade.takeProfitOrder.action = OrderAction.BUY_TO_CLOSE
						else:
							managedTrade.takeProfitOrder.action = OrderAction.SELL_TO_CLOSE

	def _composeOrderReference(self, managedTrade: ManagedTrade, action: str) -> str:
		"""
		Composes the order reference for the given trade and action
		"""
		orderReference = 'OTB (' + str(managedTrade.trade.id) + '): ' + managedTrade.template.name + ' - ' + action
		return orderReference
	
	def _round_order_price(self, broker_connector: BrokerConnector, order: Order, price: float) -> float:
		"""
		Rounds the given price to the tick size or if it is a single legged order to the minimum allowed price increment
		"""
		symbolInformation = symbolInfo.symbol_infos[order.symbol]
		roundBase = symbolInformation.multiplier * symbolInformation.quote_step
		# If there is on leg only, the round base depends on the price and the brokers rules
		if len(order.legs) == 1:
			leg = order.legs[0]
			roundBase = broker_connector.get_min_price_increment(price) * symbolInformation.multiplier
		return OptionHelper.roundToTickSize(price, roundBase)

	async def _performEODTasks(self):
		"""
		Performs the end of day tasks at market close
		- Cancel any open orders
		"""
		logger.info('Performing EOD tasks ...')
		has_active_trades = False
		for managedTrade in self._trades:
			if managedTrade.isActive():
				logger.info(f'Trade {managedTrade.trade.id} is still active.')
				has_active_trades = True
				managedTrade.expired = True
				brokerConnector = BrokerFactory().getBrokerConnectorByAccount(managedTrade.template.account)
				if not brokerConnector:
					continue

				if managedTrade.stopLossOrder:
					if managedTrade.stopLossOrder.status != OrderStatus.FILLED:
						logger.info(f'Cancelling Stop Loss order for trade {managedTrade.trade.id}')
						await brokerConnector.cancel_order(managedTrade.stopLossOrder)
				if managedTrade.takeProfitOrder:
					if managedTrade.stopLossOrder and managedTrade.stopLossOrder.ocaGroup == managedTrade.takeProfitOrder.ocaGroup:
						logger.info(f'Take Profit order is cancelled automatically.')
					else:
						if managedTrade.takeProfitOrder.status != OrderStatus.FILLED:
							logger.info(f'Cancelling Take Profit order for trade {managedTrade.trade.id}')
							await brokerConnector.cancel_order(managedTrade.takeProfitOrder)
		if has_active_trades == False:
			logger.info('no active trades found. Nothing to do')

	async def _performEODSettlement(self):
		"""
		Performs the end of day settlement tasks.
		Open Trades, which are expired get settled and closed.
		"""
		logger.info('Performing EOD Settlement ...')
		for managedTrade in self._trades:
			if managedTrade.expired == True and managedTrade.status == 'OPEN':
				logger.info(f'Settling and closing trade {managedTrade.trade.id}')
				broker_connector = BrokerFactory().getBrokerConnectorByAccount(managedTrade.template.account)
				settlement_price = broker_connector.getLastPrice(managedTrade.entryOrder.symbol)
				logger.debug(f'Last price for symbol {managedTrade.entryOrder.symbol} is {settlement_price}')
				managedTrade.status = 'EXPIRED'
				managedTrade.trade.status = 'EXPIRED'
				with Session(get_db_engine()) as session:
					crud.update_trade(session, managedTrade.trade)
				logger.info(f'Trade {managedTrade.trade.id} has been settled and closed.')

		for value in BrokerFactory().get_broker_connectors().values():
			broker_connector: BrokerConnector = value
			if broker_connector.isConnected() == True:
				await broker_connector.eod_settlement_tasks()

	def _strikes_from_order(self, order: Order) -> str:
		"""
		Returns the strike prices from the legs of the given order
		"""
		strikes = ''
		for leg in order.legs:
			if strikes != '':
				strikes += '/'
			strikes += str(leg.strike)
		return strikes

	async def _trackEntryOrder(self, managedTrade: ManagedTrade):
		"""
		Tracks the execution of the entry order
		"""
		jobId = 'TrackEntryOrder' + str(managedTrade.trade.id)
		logger.debug(f'Tracking entry order for trade {managedTrade.trade.id} on account {managedTrade.template.account}')
		if not managedTrade in self._trades:
			logger.info(f'Entry order for trade {managedTrade.trade.id} has been cancelled.')
			self._backgroundScheduler.remove_job(jobId)
			return
		
		if managedTrade.entryOrder.status == OrderStatus.FILLED:
			logger.debug(f'Entry order for trade {managedTrade.trade.id} is filled already. Stop tracking it')
			self._backgroundScheduler.remove_job(jobId)
			return

		brokerConnector = BrokerFactory().getBrokerConnectorByAccount(managedTrade.template.account)
		if brokerConnector == None:
			logger.error(f'No active broker connection found for account {managedTrade.template.account}. Unable to adjust entry order')
			return
		
		if brokerConnector.isConnected() == False:
			logger.error(f'Broker connection for account {managedTrade.template.account} is not connected. Unable to adjust entry order')
			return
		
		if brokerConnector.isTradingEnabled() == False:
			logger.error(f'Trading is disabled for account {managedTrade.template.account}. Unable to adjust entry order')
			return
		
		# Angepassten Preis berechnen und prüfen ob er über dem Minimum liegt
		symbol_info = symbolInfo.symbol_infos[managedTrade.entryOrder.symbol]
		round_base = symbol_info.multiplier * symbol_info.quote_step
		calc_adjusted_price = managedTrade.entryOrder.price + managedTrade.template.adjustmentStep

		# If the calculated Price is below the midprice, adjust it to the midprice...to prevent the market running away
		calculated_mid_price = self._calculateMidPrice(brokerConnector, managedTrade.entryOrder)
		if calc_adjusted_price < calculated_mid_price:
			logger.info('Calculated adjusted price is below current mid price. Adjusting to order price to mid price.')
			calc_adjusted_price = calculated_mid_price

		if len(managedTrade.entryOrder.legs) == 1:
			# For Single Leg orders the round base depends on the price and the brokers rules
			leg = managedTrade.entryOrder.legs[0]
			round_base = brokerConnector.get_min_price_increment(calc_adjusted_price) * symbol_info.multiplier
		adjustedPrice = OptionHelper.roundToTickSize(calc_adjusted_price, round_base)
		logger.info('Adjusting entry order. Current Limit Price: {} Adjusted Limit Price: {}', OptionHelper.roundToTickSize(managedTrade.entryOrder.price), adjustedPrice)

		if not managedTrade.template.meetsMinimumPremium(adjustedPrice):
			logger.info('Adjusted price does not meet minimum premium requirement. Canceling entry order')
			# TODO: Implement cancel order
			raise NotImplementedError

		if await brokerConnector.adjustOrder(managedTrade, managedTrade.entryOrder, adjustedPrice) == True:
			managedTrade.entryOrder.price = adjustedPrice

	async def _createTakeProfitAndStop(self, managedTrade: ManagedTrade):
		"""
		Creates the take profit and stop loss orders for the given trade
		"""
		from optrabot.tradetemplate.processor.templateprocessor import TemplateProcessor
		logger.debug(f'Acquiring Lock for TP SL creation for trade {managedTrade.trade.id}')
		async with self._lock:
			logger.debug(f'Creating take profit and stop loss orders for trade {managedTrade.trade.id}')
			brokerConnector = BrokerFactory().getBrokerConnectorByAccount(managedTrade.template.account)
			if brokerConnector == None:
				logger.error(f'No active broker connection found for account {managedTrade.template.account}. Unable to create take profit and stop loss orders')
				return
			
			managedTrade.entry_price = brokerConnector.getFillPrice(managedTrade.entryOrder)
			logger.debug(f'Fill price for entry order was {managedTrade.entry_price}')

			templateProcessor = TemplateProcessor().createTemplateProcessor(managedTrade.template)

			managedTrade.setup_stoploss_adjusters()

			notification_message = '⚖️ Trade ' + str(managedTrade.trade.id) + ': following orders attached...'

			# Create and Prepare the Take Profit Order if a take profit is defined in the template
			orderPlaced = False
			if managedTrade.template.hasTakeProfit():
				managedTrade.takeProfitOrder = templateProcessor.composeTakeProfitOrder(managedTrade, managedTrade.entry_price)
				managedTrade.takeProfitOrder.orderReference = self._composeOrderReference(managedTrade, 'TP')
			
				orderPrepared = await brokerConnector.prepareOrder(managedTrade.takeProfitOrder, False)
				if orderPrepared != True:
					logger.error(f'Failed to prepare take profit order.')
					return
			else:
				logger.info(f'Template {managedTrade.template.name} does not have a take profit defined. No take profit order will be created.')

			# Create and Prepare the Stop Loss Order
			if managedTrade.template.hasStopLoss():
				managedTrade.stopLossOrder = templateProcessor.composeStopLossOrder(managedTrade, managedTrade.entry_price)
				managedTrade.stopLossOrder.orderReference = self._composeOrderReference(managedTrade, 'SL')
				orderPrepared = await brokerConnector.prepareOrder(managedTrade.stopLossOrder, False)
				if orderPrepared != True:
					logger.error(f'Failed to prepare stop loss order.')
					return
			else:
				logger.info(f'Template {managedTrade.template.name} does not have a stop loss defined. No stop loss order will be created.')
			
			# Set an OCA Group for the Take Profit and Stop Loss Orders if both are defined
			if managedTrade.takeProfitOrder != None and managedTrade.stopLossOrder != None:
				now = datetime.now()
				ocaGroup = str(managedTrade.trade.id) + '_' + now.strftime('%H%M%S')
				managedTrade.takeProfitOrder.ocaGroup = ocaGroup
				managedTrade.stopLossOrder.ocaGroup = ocaGroup

			if brokerConnector.oco_as_complex_order() and managedTrade.takeProfitOrder != None and managedTrade.stopLossOrder != None:
				# Place the OCO order as one complex order
				orderPlaced = await brokerConnector.place_complex_order(managedTrade.takeProfitOrder, managedTrade.stopLossOrder, managedTrade.template)
				if orderPlaced == True:
					if managedTrade.takeProfitOrder != None:
						managedTrade.takeProfitOrder.status = OrderStatus.OPEN
						notification_message += f'\n*Take Profit:* ${managedTrade.takeProfitOrder.price:.2f}'
					if managedTrade.stopLossOrder != None:
						managedTrade.stopLossOrder.status = OrderStatus.OPEN
						notification_message += f'\n*Stop Loss:* ${managedTrade.stopLossOrder.price:.2f}'
			else:
				if managedTrade.takeProfitOrder != None:
					if managedTrade.template.has_soft_take_profit():
						logger.info(f'Template is using soft take profit. No take profit order will be created.')
						notification_message += f'\n*Take Profit (soft):* ${managedTrade.takeProfitOrder.price:.2f}'
						orderPlaced = True
					else:
						orderPlaced = await brokerConnector.placeOrder(managedTrade, managedTrade.takeProfitOrder, parent_order = managedTrade.entryOrder)
						if orderPlaced == True:
							logger.debug(f'Take Profit order for account {managedTrade.account} placed.')
							managedTrade.takeProfitOrder.status = OrderStatus.OPEN
							notification_message += f'\n*Take Profit:* ${managedTrade.takeProfitOrder.price:.2f}'
				else:
					notification_message += '\n*Take Profit:* n/d'

				if managedTrade.stopLossOrder != None:
					if managedTrade.template.is_credit_trade() == False and managedTrade.stopLossOrder.price == 0:
						# Debit Trades with Stop Loss Price of 0 must not be placed here
						logger.info(f'Stop Loss order for trade {managedTrade.trade.id} has a price of 0. No stop loss order will send to broker.')
						notification_message += f'\n*Stop Loss:* ${managedTrade.stopLossOrder.price:.2f}'
					else:
						orderPlaced = await brokerConnector.placeOrder(managedTrade, managedTrade.stopLossOrder, parent_order = managedTrade.entryOrder)
						if orderPlaced == True:
							logger.debug(f'Stop Loss order for account {managedTrade.account} placed.')
							managedTrade.stopLossOrder.status = OrderStatus.OPEN
							notification_message += f'\n*Stop Loss:* ${managedTrade.stopLossOrder.price:.2f}'
				else:
					notification_message += '\n*Stop Loss:* n/d'

			# Send Telegram Notification via OptraBot Server
			if orderPlaced == True:
				from optrabot.tradinghubclient import TradinghubClient, NotificationType
				await TradinghubClient().send_notification(NotificationType.INFO, notification_message) 

		logger.debug(f'Releasing Lock for TP SL creation for trade {managedTrade.trade.id}')

	async def _monitorOpenTrades(self):
		"""
		Monitors the open trades and their orders
		"""
		now = datetime.now()
		for managedTrade in self._trades:
			if managedTrade.status != 'OPEN' or managedTrade.expired == True:
				continue

			
			self._update_current_price(managedTrade)
			# if managedTrade.current_price != None:
			# 	if managedTrade.template.is_credit_trade():
			# 		current_profit = (managedTrade.entry_price - managedTrade.current_price) / managedTrade.entry_price * 100
			# 	else:
			# 		current_profit = (managedTrade.current_price - managedTrade.entry_price) / managedTrade.entry_price * 100
			# 	logger.debug(f'Current profit for trade {managedTrade.trade.id} is {current_profit:.2f}%')
				

			# Check if stop loss order is in place
			if managedTrade.stopLossOrder != None:
				if managedTrade.stopLossOrder.status == OrderStatus.CANCELLED:
					logger.warning(f'Stop Loss order for open trade {managedTrade.trade.id} was cancelled. Reestablishing it.')
					await self._reestablishStopLossOrder(managedTrade)
				else:
					# Check if the stop loss order needs to be adjusted
					await self._check_and_adjust_stoploss(managedTrade)

			if managedTrade.template.has_soft_take_profit() == False:
				if managedTrade.takeProfitOrder != None:
					if managedTrade.takeProfitOrder.status == OrderStatus.CANCELLED:
						logger.warning(f'Take Profit order for open trade {managedTrade.trade.id} was cancelled. Restablishing it.')
						await self._reestablishTakeProfitOrder(managedTrade)
			else:
				# Check every full minute if the take profit level of the soft take profit has been reached
				if now.minute != self._last_trade_monitoring_time.minute and managedTrade.takeProfitOrder.status == None:
					logger.debug(f'Check if Take Profit has been reached for trade {managedTrade.trade.id}')
					logger.debug(f'Current Price: {managedTrade.current_price:.2f} Take Profit Price: {managedTrade.takeProfitOrder.price:.2f}')
					take_profit_reached = True if (managedTrade.template.is_credit_trade() and managedTrade.current_price <= managedTrade.takeProfitOrder.price) or (not managedTrade.template.is_credit_trade() and managedTrade.current_price >= managedTrade.takeProfitOrder.price) else False
					if take_profit_reached:
						logger.info(f'Take Profit level has been reached for trade {managedTrade.trade.id}. Placing closing take profit order now.')
						
						brokerConnector = BrokerFactory().getBrokerConnectorByAccount(managedTrade.template.account)
						if brokerConnector == None:
							logger.error(f'No active broker connection found for account {managedTrade.template.account}. Unable to create take profit and stop loss orders')
							continue
						
						managedTrade.takeProfitOrder.type = OrderType.MARKET
						orderPrepared = await brokerConnector.prepareOrder(managedTrade.takeProfitOrder, False)
						if orderPrepared != True:
							logger.error(f'Failed to prepare take profit order.')
							continue

						orderPlaced = await brokerConnector.placeOrder(managedTrade, managedTrade.takeProfitOrder, parent_order = managedTrade.entryOrder)
						if orderPlaced == True:
							logger.debug(f'Take Profit order for account {managedTrade.account} placed.')
							managedTrade.takeProfitOrder.status = OrderStatus.OPEN
							notification_message = '⚖️ Trade ' + str(managedTrade.trade.id) + ':'
							notification_message += f'\n*Soft Take Profit:* Placed market close order @ ${managedTrade.current_price:.2f}'
							from optrabot.tradinghubclient import TradinghubClient, NotificationType
							await TradinghubClient().send_notification(NotificationType.INFO, notification_message)
			
		self._last_trade_monitoring_time = now

	async def _reestablishStopLossOrder(self, managedTrade: ManagedTrade):
		"""
		Reestablishes the stop loss order for the given trade
		"""
		brokerConnector = BrokerFactory().getBrokerConnectorByAccount(managedTrade.template.account)
		if brokerConnector == None:
			logger.error(f'No active broker connection found for account {managedTrade.template.account}. Unable to reestablish stop loss order')
			return
		
		managedTrade.stopLossOrder.status = OrderStatus.OPEN
		managedTrade.stopLossOrder.price = self._round_order_price(brokerConnector, managedTrade.stopLossOrder, managedTrade.stopLossOrder.price)
		orderPrepared = await brokerConnector.prepareOrder(managedTrade.stopLossOrder, False)
		if orderPrepared != True:
			logger.error(f'Failed to prepare stop loss order.')
			return
		
		orderPlaced = await brokerConnector.placeOrder(managedTrade, managedTrade.stopLossOrder, parent_order = managedTrade.entryOrder)
		if orderPlaced == True:
			logger.info(f'Stop Loss order for trade {managedTrade.trade.id} reestablished successfully.')

	async def _reestablishTakeProfitOrder(self, managedTrade: ManagedTrade):
		"""
		Reestablishes the take profit order for the given trade
		"""
		brokerConnector = BrokerFactory().getBrokerConnectorByAccount(managedTrade.template.account)
		if brokerConnector == None:
			logger.error(f'No active broker connection found for account {managedTrade.template.account}. Unable to reestablish stop loss order')
			return
		
		managedTrade.takeProfitOrder.status = OrderStatus.OPEN
		managedTrade.takeProfitOrder.price = self._round_order_price(brokerConnector, managedTrade.takeProfitOrder, managedTrade.takeProfitOrder.price)
		orderPrepared = await brokerConnector.prepareOrder(managedTrade.takeProfitOrder, False)
		if orderPrepared != True:
			logger.error(f'Failed to prepare take profit order.')
			return
		
		orderPlaced = await brokerConnector.placeOrder(managedTrade, managedTrade.takeProfitOrder, parent_order = managedTrade.entryOrder)
		if orderPlaced == True:
			logger.info(f'Take Profit order for trade {managedTrade.trade.id} reestablished successfully.')

	async def _reportExecutedTrade(self, managedTrade: ManagedTrade, contracts: int):
		"""
		Reports the filled amount of the executed trade to the OptraBot Hub
		It tries to report the event 3 times before giving up.
		"""
		from optrabot.tradinghubclient import TradinghubClient
		
		#executedContracts = 0
		#for leg in managedTrade.entryOrder.legs:
		#	executedContracts += abs(leg.quantity * filledAmount)

		additional_data = {
			'trade_id': managedTrade.trade.id,
			'account': managedTrade.template.account,
			'contracts': int(contracts)
		}
		reporterror = False
		tryCount = 0
		while tryCount < 3:
			try:
				await TradinghubClient().reportAction('CT', additional_data=json.dumps(additional_data))
				break
			except Exception as excp:
				reporterror = True
				tryCount += 1
		if reporterror == True:
			logger.error('Error reporting position open event to OptraBot Hub within 3 tries.')

	def _update_current_price(self, managed_trade: ManagedTrade):
		"""
		Updates the current price of the managed Trade based on the price data from the broker
		"""
		brokerConnector = BrokerFactory().getBrokerConnectorByAccount(managed_trade.template.account)
		if brokerConnector == None or brokerConnector.isConnected() == False:
			logger.error(f'No active broker connection found for account {managed_trade.template.account}. Unable to update current price')
			return
		
		#symbol_info = symbolInfo.symbol_infos[managed_trade.entryOrder.symbol]
		total_price = 0
		for leg in managed_trade.entryOrder.legs:
			current_leg_price_data = brokerConnector.get_option_strike_price_data(symbol=managed_trade.entryOrder.symbol, expiration=leg.expiration, strike=leg.strike)
			assert current_leg_price_data != None
			current_leg_price = current_leg_price_data.getCallMidPrice() if leg.right == OptionRight.CALL else current_leg_price_data.getPutMidPrice()
			if leg.action == OrderAction.SELL:
				# If it was sell, price has to be negated
				current_leg_price *= -1
			total_price += current_leg_price * leg.quantity
		
		logger.trace(f'Current price for trade {managed_trade.trade.id} is {total_price:.2f}')
		managed_trade.current_price = abs(total_price)
		# securityStatus = {}
		# for element in managed_trade.transactions:
		# 	transaction: schemas.Transaction = element
		# 	security = transaction.sectype + str(transaction.expiration) + str(transaction.strike)
		# 	change = transaction.contracts
		# 	fees = transaction.fee + transaction.commission
		# 	if transaction.type == OrderAction.SELL or transaction.type == 'EXP':
		# 		change = change * -1
		# 	try:
		# 		statusData = securityStatus[security]
		# 		statusData.openContracts += change
		# 	except KeyError:
		# 		statusData = SecurityStatusData(securityId=security, sec_type=transaction.sectype, strike=transaction.strike, expiration=transaction.expiration, openContracts=change, fees=transaction.fee, unrealPNL=0, realPNL = 0)
		# 		securityStatus.update({security:statusData})
		# 	statusData.unrealPNL -= ((transaction.price * symbol_info.multiplier * change) + fees)
		
		# total_unreal_pnl = 0
		# for security, statusData in securityStatus.items():
		# 	if statusData.openContracts == 0:
		# 		# contract transactions are closed
		# 		statusData.realPNL = statusData.unrealPNL
		# 		statusData.unrealPNL = 0
		# 	else:
		# 		# Contract is still open. Get current price data and
		# 		# calculate the unrealized PNL
		# 		option_price_data = brokerConnector.get_option_strike_price_data(symbol=managed_trade.entryOrder.symbol, expiration=statusData.expiration, strike=statusData.strike)
		# 		assert option_price_data != None
		# 		current_price = option_price_data.getCallMidPrice() if statusData.sec_type == OptionRight.CALL else option_price_data.getPutMidPrice()
		# 		assert current_price != None
		# 		#original_cost = (transaction.price * symbol_info.multiplier * statusData.openContracts)
		# 		current_ta_price = current_price * statusData.openContracts
		# 		#current_cost = (current_price * symbol_info.multiplier * statusData.openContracts * -1)
		# 		#unreal_pnl = current_cost - original_cost
		# 		total_price 
