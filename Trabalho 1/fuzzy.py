import sys
import os
sys.path.append("C:\\Users\\Alex\\Documents\\INF01017")
sys.path.append("C:\\Users\\Alex\\Documents\\INF01017\\Trabalho 1")

import math
import time
from robotsoccerplayer import Coord
from robotsoccerplayer import Robot
from robotsoccerplayer import Match
from fuzzy_inference_system import Variable
from fuzzy_inference_system import Rule
from fuzzy_inference_system import RuleGenerator
from fuzzy_inference_system import FuzzySystem

PI = math.pi
REAR_RIGHT = (-PI, -PI, -3*PI/4, -5*PI/8)
RIGHT = (-3*PI/4, -5*PI/8, -PI/4, 0)
FRONT = (-PI/4, 0, 0, PI/4)
LEFT = (0, PI/4, 5*PI/8, 3*PI/4)
REAR_LEFT = (5*PI/8, 3*PI/4, PI, PI)

NEG_ST = (-10, -10, -10, -6)
NEG = (-10, -6, -4, -3)
NEG_WK = (-4, -3, -1, 0)
ZER = (-1, 0, 0, 1)
POS_WK = (0, 1, 3, 4)
POS = (3, 4, 6, 10)
POS_ST = (6, 10, 10, 10)

CLOSE = (0, 0, 80, 120)
NEAR = (80, 120, 750, 1500)
FAR = (750, 1500, 2000, 2000)

class Player:
    """
    Fuzzy controller for the Robot Soccer Simulator
    """
    def __init__(self, host = 'localhost', port = 1024):
        """
        Initializes the match
        """
        self.__match = Match()
        self.__match.start(host, port)

        print('Field dimensions:', self.__match.world_width, 'x', self.__match.world_height)
        print('Robot radius:', self.__match.robot_radius)
        
        self.__variable = {
            'ball_angle': Variable({'rear_right': REAR_RIGHT, 'right': RIGHT, 'front': FRONT, 'left': LEFT, 'rear_left': REAR_LEFT}, name = 'ball_angle'),
            'target_angle': Variable({'rear_right': REAR_RIGHT, 'right': RIGHT, 'front': FRONT, 'left': LEFT, 'rear_left': REAR_LEFT}, name = 'target_angle'),
            'ball_distance': Variable({'close': CLOSE, 'near': NEAR, 'far': FAR}, name = 'ball_distance')
            }
                
        output = Variable({'negative_strong': NEG_ST, 'negative': NEG, 'negative_weak': NEG_WK, 'zero': ZER, 'positive_weak': POS_WK, 'positive': POS, 'positive_strong': POS_ST}, 'left_wheel')
        rule_maker = RuleGenerator([
            self.__variable['ball_angle'],
            self.__variable['target_angle'],
            self.__variable['ball_distance']
            ], output)
        
        left_wheel_rules = [
            rule_maker.make(['rear_right', 'rear_right', 'far'], 'zero'),
            rule_maker.make(['rear_right', 'right', 'far'], 'zero'),
            rule_maker.make(['rear_right', 'front', 'far'], 'zero'),
            rule_maker.make(['rear_right', 'left', 'far'], 'zero'),
            rule_maker.make(['rear_right', 'rear_left', 'far'], 'zero'),

            rule_maker.make(['right', 'rear_right', 'far'], 'zero'),
            rule_maker.make(['right', 'right', 'far'], 'zero'),           #7 - 
            rule_maker.make(['right', 'front', 'far'], 'zero'),
            rule_maker.make(['right', 'left', 'far'], 'zero'),
            rule_maker.make(['right', 'rear_left', 'far'], 'zero'),
            
            rule_maker.make(['front', 'rear_right', 'far'], 'zero'),
            rule_maker.make(['front', 'right', 'far'], 'zero'),
            rule_maker.make(['front', 'front', 'far'], 'zero'),
            rule_maker.make(['front', 'left', 'far'], 'zero'),
            rule_maker.make(['front', 'rear_left', 'far'], 'zero'),
            
            rule_maker.make(['left', 'rear_right', 'far'], 'zero'),
            rule_maker.make(['left', 'right', 'far'], 'zero'),
            rule_maker.make(['left', 'front', 'far'], 'zero'),
            rule_maker.make(['left', 'left', 'far'], 'zero'),
            rule_maker.make(['left', 'rear_left', 'far'], 'zero'),
            
            rule_maker.make(['rear_left', 'rear_right', 'far'], 'zero'),
            rule_maker.make(['rear_left', 'right', 'far'], 'zero'),
            rule_maker.make(['rear_left', 'front', 'far'], 'zero'),
            rule_maker.make(['rear_left', 'left', 'far'], 'zero'),
            rule_maker.make(['rear_left', 'rear_left', 'far'], 'zero'),

            ###
            rule_maker.make(['rear_right', 'rear_right', 'near'], 'zero'),
            rule_maker.make(['rear_right', 'right', 'near'], 'zero'),
            rule_maker.make(['rear_right', 'front', 'near'], 'zero'),
            rule_maker.make(['rear_right', 'left', 'near'], 'zero'),
            rule_maker.make(['rear_right', 'rear_left', 'near'], 'zero'),

            rule_maker.make(['right', 'rear_right', 'near'], 'zero'),
            rule_maker.make(['right', 'right', 'near'], 'positive_weak'), #32 -> positive_weak, zero
            rule_maker.make(['right', 'front', 'near'], 'zero'),
            rule_maker.make(['right', 'left', 'near'], 'zero'),
            rule_maker.make(['right', 'rear_left', 'near'], 'zero'),
            
            rule_maker.make(['front', 'rear_right', 'near'], 'zero'),
            rule_maker.make(['front', 'right', 'near'], 'zero'),
            rule_maker.make(['front', 'front', 'near'], 'positive_strong'), #38 -> positive_strong, positive_strong 
            rule_maker.make(['front', 'left', 'near'], 'zero'),
            rule_maker.make(['front', 'rear_left', 'near'], 'zero'),
            
            rule_maker.make(['left', 'rear_right', 'near'], 'zero'),
            rule_maker.make(['left', 'right', 'near'], 'zero'),
            rule_maker.make(['left', 'front', 'near'], 'zero'),
            rule_maker.make(['left', 'left', 'near'], 'zero'), #44 -> zero, positive_weak
            rule_maker.make(['left', 'rear_left', 'near'], 'zero'),
            
            rule_maker.make(['rear_left', 'rear_right', 'near'], 'zero'),
            rule_maker.make(['rear_left', 'right', 'near'], 'zero'),
            rule_maker.make(['rear_left', 'front', 'near'], 'zero'),
            rule_maker.make(['rear_left', 'left', 'near'], 'zero'),
            rule_maker.make(['rear_left', 'rear_left', 'near'], 'zero'),

            ###
            rule_maker.make(['rear_right', 'rear_right', 'close'], 'zero'),
            rule_maker.make(['rear_right', 'right', 'close'], 'zero'),
            rule_maker.make(['rear_right', 'front', 'close'], 'zero'),
            rule_maker.make(['rear_right', 'left', 'close'], 'zero'),
            rule_maker.make(['rear_right', 'rear_left', 'close'], 'zero'),

            rule_maker.make(['right', 'rear_right', 'close'], 'zero'),
            rule_maker.make(['right', 'right', 'close'], 'zero'),
            rule_maker.make(['right', 'front', 'close'], 'zero'),
            rule_maker.make(['right', 'left', 'close'], 'zero'),
            rule_maker.make(['right', 'rear_left', 'close'], 'zero'),
            
            rule_maker.make(['front', 'rear_right', 'close'], 'zero'),
            rule_maker.make(['front', 'right', 'close'], 'zero'),
            rule_maker.make(['front', 'front', 'close'], 'zero'),
            rule_maker.make(['front', 'left', 'close'], 'zero'),
            rule_maker.make(['front', 'rear_left', 'close'], 'zero'),
            
            rule_maker.make(['left', 'rear_right', 'close'], 'zero'),
            rule_maker.make(['left', 'right', 'close'], 'zero'),
            rule_maker.make(['left', 'front', 'close'], 'zero'),
            rule_maker.make(['left', 'left', 'close'], 'zero'),
            rule_maker.make(['left', 'rear_left', 'close'], 'zero'),
            
            rule_maker.make(['rear_left', 'rear_right', 'close'], 'zero'),
            rule_maker.make(['rear_left', 'right', 'close'], 'zero'),
            rule_maker.make(['rear_left', 'front', 'close'], 'zero'),
            rule_maker.make(['rear_left', 'left', 'close'], 'zero'),
            rule_maker.make(['rear_left', 'rear_left', 'close'], 'zero'),
            ]

        right_wheel_rules = [
            rule_maker.make(['rear_right', 'rear_right', 'far'], 'zero'),
            rule_maker.make(['rear_right', 'right', 'far'], 'zero'),
            rule_maker.make(['rear_right', 'front', 'far'], 'zero'),
            rule_maker.make(['rear_right', 'left', 'far'], 'zero'),
            rule_maker.make(['rear_right', 'rear_left', 'far'], 'zero'),

            rule_maker.make(['right', 'rear_right', 'far'], 'zero'),
            rule_maker.make(['right', 'right', 'far'], 'zero'),
            rule_maker.make(['right', 'front', 'far'], 'zero'),
            rule_maker.make(['right', 'left', 'far'], 'zero'),
            rule_maker.make(['right', 'rear_left', 'far'], 'zero'),
            
            rule_maker.make(['front', 'rear_right', 'far'], 'zero'),
            rule_maker.make(['front', 'right', 'far'], 'zero'),
            rule_maker.make(['front', 'front', 'far'], 'zero'),
            rule_maker.make(['front', 'left', 'far'], 'zero'),
            rule_maker.make(['front', 'rear_left', 'far'], 'zero'),
            
            rule_maker.make(['left', 'rear_right', 'far'], 'zero'),
            rule_maker.make(['left', 'right', 'far'], 'zero'),
            rule_maker.make(['left', 'front', 'far'], 'zero'),
            rule_maker.make(['left', 'left', 'far'], 'zero'),
            rule_maker.make(['left', 'rear_left', 'far'], 'zero'),
            
            rule_maker.make(['rear_left', 'rear_right', 'far'], 'zero'),
            rule_maker.make(['rear_left', 'right', 'far'], 'zero'),
            rule_maker.make(['rear_left', 'front', 'far'], 'zero'),
            rule_maker.make(['rear_left', 'left', 'far'], 'zero'),
            rule_maker.make(['rear_left', 'rear_left', 'far'], 'zero'),

            ###
            rule_maker.make(['rear_right', 'rear_right', 'near'], 'zero'),
            rule_maker.make(['rear_right', 'right', 'near'], 'zero'),
            rule_maker.make(['rear_right', 'front', 'near'], 'zero'),
            rule_maker.make(['rear_right', 'left', 'near'], 'zero'),
            rule_maker.make(['rear_right', 'rear_left', 'near'], 'zero'),

            rule_maker.make(['right', 'rear_right', 'near'], 'zero'),
            rule_maker.make(['right', 'right', 'near'], 'zero'), #32 -> positive_weak, zero
            rule_maker.make(['right', 'front', 'near'], 'zero'),
            rule_maker.make(['right', 'left', 'near'], 'zero'),
            rule_maker.make(['right', 'rear_left', 'near'], 'zero'),
            
            rule_maker.make(['front', 'rear_right', 'near'], 'zero'),
            rule_maker.make(['front', 'right', 'near'], 'zero'),
            rule_maker.make(['front', 'front', 'near'], 'positive_strong'), #38 -> positive_strong, positive_strong 
            rule_maker.make(['front', 'left', 'near'], 'zero'),
            rule_maker.make(['front', 'rear_left', 'near'], 'zero'),
            
            rule_maker.make(['left', 'rear_right', 'near'], 'zero'),
            rule_maker.make(['left', 'right', 'near'], 'zero'),
            rule_maker.make(['left', 'front', 'near'], 'zero'),
            rule_maker.make(['left', 'left', 'near'], 'positive_weak'), #44 -> zero, positive_weak
            rule_maker.make(['left', 'rear_left', 'near'], 'zero'),
            
            rule_maker.make(['rear_left', 'rear_right', 'near'], 'zero'),
            rule_maker.make(['rear_left', 'right', 'near'], 'zero'),
            rule_maker.make(['rear_left', 'front', 'near'], 'zero'),
            rule_maker.make(['rear_left', 'left', 'near'], 'zero'),
            rule_maker.make(['rear_left', 'rear_left', 'near'], 'zero'),

            ###
            rule_maker.make(['rear_right', 'rear_right', 'close'], 'zero'),
            rule_maker.make(['rear_right', 'right', 'close'], 'zero'),
            rule_maker.make(['rear_right', 'front', 'close'], 'zero'),
            rule_maker.make(['rear_right', 'left', 'close'], 'zero'),
            rule_maker.make(['rear_right', 'rear_left', 'close'], 'zero'),

            rule_maker.make(['right', 'rear_right', 'close'], 'zero'),
            rule_maker.make(['right', 'right', 'close'], 'zero'),
            rule_maker.make(['right', 'front', 'close'], 'zero'),
            rule_maker.make(['right', 'left', 'close'], 'zero'),
            rule_maker.make(['right', 'rear_left', 'close'], 'zero'),
            
            rule_maker.make(['front', 'rear_right', 'close'], 'zero'),
            rule_maker.make(['front', 'right', 'close'], 'zero'),
            rule_maker.make(['front', 'front', 'close'], 'zero'),
            rule_maker.make(['front', 'left', 'close'], 'zero'),
            rule_maker.make(['front', 'rear_left', 'close'], 'zero'),
            
            rule_maker.make(['left', 'rear_right', 'close'], 'zero'),
            rule_maker.make(['left', 'right', 'close'], 'zero'),
            rule_maker.make(['left', 'front', 'close'], 'zero'),
            rule_maker.make(['left', 'left', 'close'], 'zero'),
            rule_maker.make(['left', 'rear_left', 'close'], 'zero'),
            
            rule_maker.make(['rear_left', 'rear_right', 'close'], 'zero'),
            rule_maker.make(['rear_left', 'right', 'close'], 'zero'),
            rule_maker.make(['rear_left', 'front', 'close'], 'zero'),
            rule_maker.make(['rear_left', 'left', 'close'], 'zero'),
            rule_maker.make(['rear_left', 'rear_left', 'close'], 'zero'),
            ]
            
        self.__left_wheel_fis = FuzzySystem(left_wheel_rules, output, 'left')
        self.__right_wheel_fis = FuzzySystem(right_wheel_rules, output, 'right')

    def play(self):
        """
        Play using fuzzy controller
        """
        i = 0
        fuzzy_left = self.__left_wheel_fis
        fuzzy_right = self.__right_wheel_fis
        variable = self.__variable
        match = self.__match
        while(True):
            variable['ball_angle'].value = match.get_ball_angle()
            variable['target_angle'].value = match.get_target_angle()
            variable['ball_distance'].value = match.get_ball_distance()
            #print(variable['ball_distance'].value)
            left_wheel = fuzzy_left.output()
            right_wheel = fuzzy_right.output()
            spin = match.get_spin()
            match.act(left_wheel, right_wheel)
            i += 1
            print(variable['ball_angle'])
            print(variable['target_angle'])
            print(variable['ball_distance'])
            print('output:', left_wheel, right_wheel)
            print('spin:', match.get_spin())
            input('')
            print('-'*30)

nargs = len(sys.argv) - 1
if(nargs is 0):
    p = Player()
elif(nargs is 1):
    port = int(sys.argv[1])
    p = Player(port = port)
else:
    host = sys.argv[1]
    port = int(sys.argv[2])
    p = Player(host, port)
p.play()

    
