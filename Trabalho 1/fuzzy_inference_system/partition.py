import sys
sys.path.append("C:\\Users\\apmoraes\\Downloads\\INF01017-matrix-interpreter\\Trabalho 1")

class Partition:
        """
        Represents a fuzzy partition of a given variable
        """
        def __init__(self, var, partition_params, name = ''):
                self.name = name
                self.__var = var
                self.__params = partition_params

        def __str__(self):
                return self.name + ' = ' + str(self.membership())

        def __repr__(self):
                return self.__str__()
		
        def __trapezium(self, point):
                """
                Calculate the membership of a value given a triangle shaped membership
                function
                """
                params = self.__params
                alpha = params[0]
                beta = params[1]
                gamma = params[2]
                delta = params[3]
                if(point <= alpha or point >= delta):
                    return 0
                elif(point >= alpha and point <= beta):
                    return (point - alpha)/(beta - alpha)
                elif(point > beta and point < gamma):
                    return 1
                else:
                    return (delta - point)/(delta - gamma)
        
        def membership(self):
                """
                Returns the membership grade of the variable value within the partition
                """
                return self.__trapezium(self.__var.value)
	
        def center(self):
                """
                Returns the coordinate of the center of the trapezium minor side
                """
                params = self.__params
                return (params[1] + params[2])/2
