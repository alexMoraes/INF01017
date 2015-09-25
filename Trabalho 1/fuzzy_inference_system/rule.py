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

        def __str__(self):
                ret = ''
                for ant in self.__antecedents:
                        ret += str(ant)
                        ret += ' '
                ret += '=> '
                ret += str(self.consequent)
                return ret

        def __repr__(self):
                return self.__str__()

        def activation_force(self):
                force = float('infinity')
                for ant in self.__antecedents:
                        force = min(force, ant.membership())
                return force

class RuleGenerator:
        """
        Generate rules for a given set of variables
        """
        def __init__(self, inputs, output):
                self.__input = inputs
                self.__output = output

        def make(self, inputs, output):
                antecedents = []
                for index, part_name in enumerate(inputs):
                        antecedents.append(self.__input[index].partition(part_name))
                consequent = self.__output.partition(output)
                return Rule(antecedents, consequent)

        def make(self, inputs, output):
                if(len(inputs) is not len(self.__input)):
                   raise RuntimeError('Rule antecedents doesn\'t match number of variables')
                   
                antecedents = []
                for index, var in enumerate(self.__input):
                        antecedents.append(var.partition(inputs[index]))
                return Rule(antecedents, self.__output.partition(output))
