import math
from loguru import logger


class OptionHelper:

	@staticmethod
	def roundToTickSize(value: float, roundBase: int = 5) -> float:
		""" Round a calculated options price e.g. a mid price to the closest tick value
		"""
		#rounded = round(value*100/roundBase)
		rounded = math.ceil(value * 100 / roundBase) if (value * 100) % roundBase >= roundBase / 2 else math.floor(value * 100 / roundBase)
		return (roundBase * rounded) / 100

	@staticmethod
	def roundToStrikePrice(value: float) -> float:
		""" Round a floating value to the nearest Strike price 
		"""
		roundBase = 5
		return (roundBase * round(value/roundBase))
	
	@staticmethod
	def checkContractIsQualified(contract):
		if contract.conId == 0:
			logger.error("Contract not determined. Strike {}, Right {}", contract.strike, contract.right)
			return False
		else:
			return True
	
	@staticmethod
	def calculateMidPrice(bidPrice: float, askPrice: float) -> float:
		difference = abs(bidPrice-askPrice)
		half = difference / 2
		if bidPrice < askPrice:
			midPrice = bidPrice + half
		else:
			midPrice = bidPrice - half
		return OptionHelper.roundToTickSize(midPrice)
	
	@staticmethod
	def closest_number(target: float, num1: float, num2: float) -> float:
		""" Returns the closest number to the target value
		"""
		if abs(num1 - target) < abs(num2 - target):
			return num1
		else:
			return num2