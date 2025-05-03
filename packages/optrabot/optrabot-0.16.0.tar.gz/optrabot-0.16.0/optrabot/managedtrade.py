
from typing import List
from optrabot.models import Trade
from optrabot.tradetemplate.templatefactory import Template
from optrabot.broker.order import Execution, OptionRight, Order
from optrabot.stoplossadjuster import StopLossAdjuster
import copy

class ManagedTrade:
	"""
	ManagedTrade is representing a trade which is currently managed by the TradeManager.
	"""
	def __init__(self, trade: Trade, template: Template, entryOrder: Order, account: str = ''): 
		self.trade = trade
		self.entryOrder = entryOrder
		self.template = template
		self.account = account
		self.takeProfitOrder: Order = None
		self.stopLossOrder: Order = None
		self.status = 'NEW'
		self.realizedPNL = 0.0
		self.transactions = []
		self.expired = False
		self.entry_price = None					# Holds the entry price for the trade
		self.current_price: float = None		# Holds the current price of the trade
		self.stoploss_adjusters: List[StopLossAdjuster] = []
		self.long_legs_removed = False			# will be set to true for credit_trades if the long legs are no longer available

	def isActive(self) -> bool:
		"""
		Returns True if the trade is active
		"""
		return self.status == 'OPEN'
	
	def setup_stoploss_adjusters(self):
		""" 
		Copies the stop loss adjusters from the template to the managed trade and sets the
		base price for earch of the adjusters
		"""
		for adjuster in self.template.get_stoploss_adjusters():
			adjuster_copy = copy.copy(adjuster)
			adjuster_copy.setBasePrice(self.entry_price)
			self.stoploss_adjusters.append(adjuster_copy)