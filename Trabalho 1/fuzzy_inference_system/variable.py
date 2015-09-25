import sys
sys.path.append("C:\\Users\\apmoraes\\Downloads\\INF01017-matrix-interpreter\\Trabalho 1")

from fuzzy_inference_system import Partition


class Variable:
	"""
	Represents a fuzzy variable
	"""
	def __init__(self, partitions):
		self.value = None
		self.partition_count = len(partitions)
		self.partitions = {}
		for part_name in partitions:
			self.partitions[part_name] = Partition(self, partitions[part_name])
			
	def partition(self, name):
		return self.partitions[name]
