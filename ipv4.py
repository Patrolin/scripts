from __future__ import annotations # Python 4 - postpone evaluation of type hints
import re
from math import *

# General programming tips
# store data only once
# overload only constructors / use struct and set values yourself

class ipv4:
	def __init__(self, address: Union[int, str] = 0):
		if isinstance(address, int):
			self.value = address & 0xFFFFFFFF
		elif isinstance(address, str):
			self.value = ipv4.parse(address)
		else:
			raise TypeError(f'{self.__class__.__name__} does not support address of type {type(address).__name__}')
	
	@staticmethod
	def parse(address: str):
		m = re.match(r'(\d*)\.(\d*)\.(\d*)\.(\d*)', address)
		if not m or int(m[1]) > 255 or int(m[2]) > 255 or int(m[3]) > 255 or int(m[4]) > 255:
			raise ValueError(f'{address} is not a valid ipv4 adress')
		return (int(m[1]) << 24) + (int(m[2]) << 16) + (int(m[3]) << 8) + (int(m[4]))
	
	
	def __str__(self):
		return f'{self.value >> 24}.{(self.value >> 16) & 0xFF}.{(self.value >> 8) & 0xFF}.{(self.value) & 0xFF}'
	
	def __int__(self):
		return self.value
	
	
	# binary
	def __invert__(self):
		return self.value ^ 0xFFFFFFFF
	
	def __or__(self, other: Union[int, ipv4]):
		return ipv4(self.value | int(other))
	
	def __and__(self, other: Union[int, ipv4]):
		return ipv4(self.value & int(other))
	
	
	# decimal
	def add(self, other: Union[int, ipv4]):
		return ipv4(self.value + int(other))
	
	def sub(self, other: Union[int, ipv4]):
		return ipv4(self.value - int(other))
	
	
	@staticmethod
	def NM(prefix: int):
		return ipv4((0xFFFFFFFF >> prefix) ^ 0xFFFFFFFF) # 0xFFFFFFFF << (32 - prefix) # in int32
	
	def AS(self, prefix: int):
		return self & ((0xFFFFFFFF >> prefix) ^ 0xFFFFFFFF)
	
	def BA(self, prefix: int):
		return self | (0xFFFFFFFF >> prefix)
	
	def host(self, prefix: int):
		if prefix < 8:
			return f'{self.value >> 24}.{(self.value >> 16) & 0xFF}.{(self.value >> 8) & 0xFF}.{(self.value) & 0xFF}'
		elif prefix < 16:
			return f'.{(self.value >> 16) & 0xFF}.{(self.value >> 8) & 0xFF}.{(self.value) & 0xFF}'
		elif prefix < 24:
			return f'.{(self.value >> 8) & 0xFF}.{(self.value) & 0xFF}'
		else:
			return f'.{(self.value) & 0xFF}'
	
	
	@staticmethod
	def prefix(pool_size: int):
		return 32 - ceil(log2(pool_size))
	
	@staticmethod
	def pool_size(prefix: int):
		return 1 << (32 - prefix)


if __name__ == '__main__':
	default = ipv4('192.168.4.0')
	prefix = 24
	
	print(f'IP: {default}/{ipv4.prefix(ipv4.pool_size(prefix))}')
	print('------------------')
	print(f'AS: {default.AS(prefix)}')
	print(f'BA: {default.BA(prefix)}')
	print(f'NM: {ipv4.NM(prefix)}')
	print(f'host: {default.host(prefix)}')
