import sys
sys.path.append("C:\\Users\\apmoraes\\Downloads\\INF01017-matrix-interpreter\\Trabalho 1")

from fuzzy_inference_system import Variable
from fuzzy_inference_system import Partition

class Rule:
	"""
	Fuzzy rule following a Mandami inference method
	"""
	def __init__(self, antecedents, consequent):
		self.__antecedents = antecedents
		self.consequent = consequent
		
	def activation_force(self):
		force = float('infinity')
		for ant in self.__antecedents:
			force = min(force, ant.membership())
		return force
