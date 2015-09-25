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
REAR_RIGHT = (-PI, -PI, -PI, -PI/2)
RIGHT = (-PI, -PI/2, -PI/4, 0)
FRONT = (-PI/4, 0, 0, PI/4)
LEFT = (0, PI/4, PI/2, PI)
REAR_LEFT = (PI/2, PI, PI, PI)

NEG_ST = (-10, -10, -10, 2)
NEG_WK = (-4, -2, -2, 0)
ZER = (-2, 0, 0, 2)
POS_WK = (0, 2, 2, 4)
POS_ST = (2, 10, 10, 10)

CLOSE = (0, 0, 80, 160)
NEAR = (0, 160, 1300, 1500)
FAR = (1300, 1500, 2000, 2000)

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
            'ball_angle': Variable({'rear_right': REAR_RIGHT, 'right': RIGHT, 'front': FRONT, 'left': LEFT, 'rear_left': REAR_LEFT}, name = 'ball'),
            'target_angle': Variable({'rear_right': REAR_RIGHT, 'right': RIGHT, 'front': FRONT, 'left': LEFT, 'rear_left': REAR_LEFT}, name = 'target'),
            'ball_distance': Variable({'close': CLOSE, 'near': NEAR, 'far': FAR})
            }
                
        output = Variable({'negative_strong': NEG_ST, 'negative': NEG_WK, 'zero': ZER, 'positive': POS_WK, 'positive_strong': POS_ST}, 'left_wheel')
        rule_maker = RuleGenerator([
            self.__variable['ball_angle'],
            self.__variable['target_angle'],
            self.__variable['ball_distance']
            ], output)
        
        left_wheel_rules = [
            rule_maker.make(['rear_right', 'rear_right', 'far'], 'negative'), #1
            rule_maker.make(['rear_right', 'right', 'far'], 'negative'), #2
            rule_maker.make(['rear_right', 'front', 'far'], 'negative'), #3
            rule_maker.make(['rear_right', 'left', 'far'], 'positive_strong'), #4
            rule_maker.make(['rear_right', 'rear_left', 'far'], 'positive_strong'), #5

            rule_maker.make(['right', 'rear_right', 'far'], 'positive_strong'), #6
            rule_maker.make(['right', 'right', 'far'], 'positive'), #7
            rule_maker.make(['right', 'front', 'far'], 'positive_strong'), #8
            rule_maker.make(['right', 'left', 'far'], 'positive_strong'), #9
            rule_maker.make(['right', 'rear_left', 'far'], 'positive_strong'), #10
            
            rule_maker.make(['front', 'rear_right', 'far'], 'positive'), #11
            rule_maker.make(['front', 'right', 'far'], 'positive'), #12
            rule_maker.make(['front', 'front', 'far'], 'positive_strong'), #13
            rule_maker.make(['front', 'left', 'far'], 'positive_strong'), #14
            rule_maker.make(['front', 'rear_left', 'far'], 'positive_strong'), #15
            
            rule_maker.make(['left', 'rear_right', 'far'], 'positive'), #16
            rule_maker.make(['left', 'right', 'far'], 'negative'), #17
            rule_maker.make(['left', 'front', 'far'], 'negative'), #18
            rule_maker.make(['left', 'left', 'far'], 'negative'), #19
            rule_maker.make(['left', 'rear_left', 'far'], 'positive'), #20
            
            rule_maker.make(['rear_left', 'rear_right', 'far'], 'positive'), #21
            rule_maker.make(['rear_left', 'right', 'far'], 'positive'), #22
            rule_maker.make(['rear_left', 'front', 'far'], 'negative_strong'), #23
            rule_maker.make(['rear_left', 'left', 'far'], 'negative_strong'), #24
            rule_maker.make(['rear_left', 'rear_left', 'far'], 'negative_strong'), #25

            ###
            rule_maker.make(['rear_right', 'rear_right', 'near'], 'zero'), #1
            rule_maker.make(['rear_right', 'right', 'near'], 'zero'), #2
            rule_maker.make(['rear_right', 'front', 'near'], 'zero'), #3
            rule_maker.make(['rear_right', 'left', 'near'], 'positive'), #4
            rule_maker.make(['rear_right', 'rear_left', 'near'], 'positive'), #5

            rule_maker.make(['right', 'rear_right', 'near'], 'positive'), #6
            rule_maker.make(['right', 'right', 'near'], 'positive'), #7
            rule_maker.make(['right', 'front', 'near'], 'positive'), #8
            rule_maker.make(['right', 'left', 'near'], 'positive'), #9
            rule_maker.make(['right', 'rear_left', 'near'], 'positive'), #10
            
            rule_maker.make(['front', 'rear_right', 'near'], 'zero'), #11
            rule_maker.make(['front', 'right', 'near'], 'zero'), #12
            rule_maker.make(['front', 'front', 'near'], 'positive_strong'), #13
            rule_maker.make(['front', 'left', 'near'], 'positive'), #14
            rule_maker.make(['front', 'rear_left', 'near'], 'positive'), #15
            
            rule_maker.make(['left', 'rear_right', 'near'], 'zero'), #16
            rule_maker.make(['left', 'right', 'near'], 'negative'), #17
            rule_maker.make(['left', 'front', 'near'], 'negative'), #18
            rule_maker.make(['left', 'left', 'near'], 'zero'), #19
            rule_maker.make(['left', 'rear_left', 'near'], 'zero'), #20
            
            rule_maker.make(['rear_left', 'rear_right', 'near'], 'zero'), #21
            rule_maker.make(['rear_left', 'right', 'near'], 'zero'), #22
            rule_maker.make(['rear_left', 'front', 'near'], 'negative'), #23
            rule_maker.make(['rear_left', 'left', 'near'], 'negative'), #24
            rule_maker.make(['rear_left', 'rear_left', 'near'], 'negative'), #25

            ###
            rule_maker.make(['rear_right', 'rear_right', 'close'], 'negative'), #1
            rule_maker.make(['rear_right', 'right', 'close'], 'negative'), #2
            rule_maker.make(['rear_right', 'front', 'close'], 'negative'), #3
            rule_maker.make(['rear_right', 'left', 'close'], 'negative'), #4
            rule_maker.make(['rear_right', 'rear_left', 'close'], 'negative'), #5

            rule_maker.make(['right', 'rear_right', 'close'], 'positive'), #6
            rule_maker.make(['right', 'right', 'close'], 'zero'), #7
            rule_maker.make(['right', 'front', 'close'], 'negative'), #8
            rule_maker.make(['right', 'left', 'close'], 'zero'), #9
            rule_maker.make(['right', 'rear_left', 'close'], 'positive'), #10
            
            rule_maker.make(['front', 'rear_right', 'close'], 'positive'), #11
            rule_maker.make(['front', 'right', 'close'], 'positive'), #12
            rule_maker.make(['front', 'front', 'close'], 'positive_strong'), #13
            rule_maker.make(['front', 'left', 'close'], 'zero'), #14
            rule_maker.make(['front', 'rear_left', 'close'], 'zero'), #15
            
            rule_maker.make(['left', 'rear_right', 'close'], 'zero'), #16
            rule_maker.make(['left', 'right', 'close'], 'negative'), #17
            rule_maker.make(['left', 'front', 'close'], 'negative'), #18
            rule_maker.make(['left', 'left', 'close'], 'negative'), #19
            rule_maker.make(['left', 'rear_left', 'close'], 'zero'), #20
            
            rule_maker.make(['rear_left', 'rear_right', 'close'], 'negative'), #21
            rule_maker.make(['rear_left', 'right', 'close'], 'negative'), #22
            rule_maker.make(['rear_left', 'front', 'close'], 'negative'), #23
            rule_maker.make(['rear_left', 'left', 'close'], 'negative'), #24
            rule_maker.make(['rear_left', 'rear_left', 'close'], 'negative'), #25
            ]

        right_wheel_rules = [
            rule_maker.make(['rear_right', 'rear_right', 'far'], 'negative_strong'), #1
            rule_maker.make(['rear_right', 'right', 'far'], 'negative_strong'), #2
            rule_maker.make(['rear_right', 'front', 'far'], 'negative_strong'), #3
            rule_maker.make(['rear_right', 'left', 'far'], 'positive'), #4
            rule_maker.make(['rear_right', 'rear_left', 'far'], 'positive'), #5

            rule_maker.make(['right', 'rear_right', 'far'], 'positive'), #6
            rule_maker.make(['right', 'right', 'far'], 'negative'), #7
            rule_maker.make(['right', 'front', 'far'], 'negative'), #8
            rule_maker.make(['right', 'left', 'far'], 'negative'), #9
            rule_maker.make(['right', 'rear_left', 'far'], 'positive'), #10
            
            rule_maker.make(['front', 'rear_right', 'far'], 'positive_strong'), #11
            rule_maker.make(['front', 'right', 'far'], 'positive_strong'), #12
            rule_maker.make(['front', 'front', 'far'], 'positive_strong'), #13
            rule_maker.make(['front', 'left', 'far'], 'positive'), #14
            rule_maker.make(['front', 'rear_left', 'far'], 'positive'), #15
            
            rule_maker.make(['left', 'rear_right', 'far'], 'positive_strong'), #16
            rule_maker.make(['left', 'right', 'far'], 'positive_strong'), #17
            rule_maker.make(['left', 'front', 'far'], 'positive_strong'), #18
            rule_maker.make(['left', 'left', 'far'], 'positive'), #19
            rule_maker.make(['left', 'rear_left', 'far'], 'positive_strong'), #20
            
            rule_maker.make(['rear_left', 'rear_right', 'far'], 'positive_strong'), #21
            rule_maker.make(['rear_left', 'right', 'far'], 'positive_strong'), #22
            rule_maker.make(['rear_left', 'front', 'far'], 'negative'), #23
            rule_maker.make(['rear_left', 'left', 'far'], 'negative'), #24
            rule_maker.make(['rear_left', 'rear_left', 'far'], 'negative'), #25

            ###
            rule_maker.make(['rear_right', 'rear_right', 'near'], 'negative'), #1
            rule_maker.make(['rear_right', 'right', 'near'], 'negative'), #2
            rule_maker.make(['rear_right', 'front', 'near'], 'negative'), #3
            rule_maker.make(['rear_right', 'left', 'near'], 'zero'), #4
            rule_maker.make(['rear_right', 'rear_left', 'near'], 'zero'), #5

            rule_maker.make(['right', 'rear_right', 'near'], 'zero'), #6
            rule_maker.make(['right', 'right', 'near'], 'zero'), #7
            rule_maker.make(['right', 'front', 'near'], 'negative'), #8
            rule_maker.make(['right', 'left', 'near'], 'negative'), #9
            rule_maker.make(['right', 'rear_left', 'near'], 'zero'), #10
            
            rule_maker.make(['front', 'rear_right', 'near'], 'positive'), #11
            rule_maker.make(['front', 'right', 'near'], 'positive'), #12
            rule_maker.make(['front', 'front', 'near'], 'positive_strong'), #13
            rule_maker.make(['front', 'left', 'near'], 'zero'), #14
            rule_maker.make(['front', 'rear_left', 'near'], 'zero'), #15
            
            rule_maker.make(['left', 'rear_right', 'near'], 'positive'), #16
            rule_maker.make(['left', 'right', 'near'], 'positive'), #17
            rule_maker.make(['left', 'front', 'near'], 'positive'), #18
            rule_maker.make(['left', 'left', 'near'], 'positive'), #19
            rule_maker.make(['left', 'rear_left', 'near'], 'positive'), #20
            
            rule_maker.make(['rear_left', 'rear_right', 'near'], 'positive'), #21
            rule_maker.make(['rear_left', 'right', 'near'], 'positive'), #22
            rule_maker.make(['rear_left', 'front', 'near'], 'zero'), #23
            rule_maker.make(['rear_left', 'left', 'near'], 'zero'), #24
            rule_maker.make(['rear_left', 'rear_left', 'near'], 'zero'), #25

            ###
            rule_maker.make(['rear_right', 'rear_right', 'close'], 'negative'), #1
            rule_maker.make(['rear_right', 'right', 'close'], 'negative'), #2
            rule_maker.make(['rear_right', 'front', 'close'], 'negative'), #3
            rule_maker.make(['rear_right', 'left', 'close'], 'negative'), #4
            rule_maker.make(['rear_right', 'rear_left', 'close'], 'negative'), #5

            rule_maker.make(['right', 'rear_right', 'close'], 'zero'), #6
            rule_maker.make(['right', 'right', 'close'], 'negative'), #7
            rule_maker.make(['right', 'front', 'close'], 'negative'), #8
            rule_maker.make(['right', 'left', 'close'], 'negative'), #9
            rule_maker.make(['right', 'rear_left', 'close'], 'zero'), #10
            
            rule_maker.make(['front', 'rear_right', 'close'], 'zero'), #11
            rule_maker.make(['front', 'right', 'close'], 'zero'), #12
            rule_maker.make(['front', 'front', 'close'], 'positive_strong'), #13
            rule_maker.make(['front', 'left', 'close'], 'positive'), #14
            rule_maker.make(['front', 'rear_left', 'close'], 'positive'), #15
            
            rule_maker.make(['left', 'rear_right', 'close'], 'positive'), #16
            rule_maker.make(['left', 'right', 'close'], 'zero'), #17
            rule_maker.make(['left', 'front', 'close'], 'zero'), #18
            rule_maker.make(['left', 'left', 'close'], 'zero'), #19
            rule_maker.make(['left', 'rear_left', 'close'], 'positive'), #20
            
            rule_maker.make(['rear_left', 'rear_right', 'close'], 'negative'), #21
            rule_maker.make(['rear_left', 'right', 'close'], 'negative'), #22
            rule_maker.make(['rear_left', 'front', 'close'], 'negative'), #23
            rule_maker.make(['rear_left', 'left', 'close'], 'negative'), #24
            rule_maker.make(['rear_left', 'rear_left', 'close'], 'negative'), #25
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
            if(abs(spin) > 1):
                left_wheel = 0
                right_wheel = 0
                print('stabilization mode. spin:', spin)
            match.act(left_wheel, right_wheel)
            i += 1

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

    
