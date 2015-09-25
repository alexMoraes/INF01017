import sys
sys.path.append("C:\\Users\\apmoraes\\Downloads\\INF01017-matrix-interpreter\\Trabalho 1")

from fuzzy_inference_system import Variable
from fuzzy_inference_system import Partition

class FuzzySystem:
        """
        Given a set of fuzzy rules, calculates an output relative of a set of input variables
        """
        def __init__(self, rules, output, name = ''):
                self.__name = name
                self.__rules = rules
                self.__output = output
                
        def output(self):
                """
                Calculates the output of the rule set given a set of variable values
                """
                # Initialize a dictionary to store output partitions heights
                alpha = {}
                output = self.__output
                for part_name in output.partitions:
                        alpha[part_name] = 0

                # Gets the maximum activation force for each output partition
                for rule in self.__rules:
                        part_name = rule.consequent.name
                        alpha[part_name] = max(alpha[part_name], rule.activation_force())
                        
                # Calculate the output value using height method
                nominator = 0
                denominator = 0
                for part_name, value in alpha.items():
                        denominator += value
                        center = output.partition(part_name).center()
                        nominator += value * center

                return nominator/denominator if denominator is not 0 else sys.float_info.min
