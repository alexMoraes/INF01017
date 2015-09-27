import sys
sys.path.append("C:\\Users\\apmoraes\\Downloads\\INF01017-matrix-interpreter\\Trabalho 1")

from fuzzy_inference_system import Partition


class Variable:
        """
        Represents a fuzzy variable
        """
        def __init__(self, partitions, name = ''):
                self.__name = name
                self.value = None
                self.partition_count = len(partitions)
                self.partitions = {}
                for part_name in partitions:
                        self.partitions[part_name] = Partition(self, partitions[part_name], part_name)

        def __str__(self):
                ret = '%s (%.2f):'%(self.__name, self.value)
                for part_name, part in self.partitions.items():
                        ret += ' %s;'%str(part)
                return ret

        def __repr__(self):
                return self.__str__()

        def partition(self, name):
                return self.partitions[name]
