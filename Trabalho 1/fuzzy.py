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
RIGHT = (-PI, -PI/2, -PI/2, 0)
FRONT = (-PI/6, 0, 0, PI/6)
LEFT = (0, PI/2, PI/2, PI)
REAR_LEFT = (PI/2, PI, PI, PI)

NEG = (-3, -3, -3, 0)
ZER = (-0.2, 0, 0, 0.2)
POS = (0, 3, 3, 3)

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
        
        self.__variable = {
            'ball_angle': Variable({'rear_right': REAR_RIGHT, 'right': RIGHT, 'front': FRONT, 'left': LEFT, 'rear_left': REAR_LEFT}, name = 'ball'),
            'target_angle': Variable({'rear_right': REAR_RIGHT, 'right': RIGHT, 'front': FRONT, 'left': LEFT, 'rear_left': REAR_LEFT}, name = 'target')
            }
                
        output = Variable({'negative': NEG, 'zero': ZER, 'positive': POS}, 'left_wheel')
        rule_maker = RuleGenerator([
            self.__variable['ball_angle'],
            self.__variable['target_angle']
            ], output)
        
        left_wheel_rules = [
            rule_maker.make(['rear_right', 'rear_right'], 'zero'), #1
            rule_maker.make(['rear_right', 'right'], 'zero'), #2
            rule_maker.make(['rear_right', 'front'], 'zero'), #3
            rule_maker.make(['rear_right', 'left'], 'positive'), #4
            rule_maker.make(['rear_right', 'rear_left'], 'positive'), #5

            rule_maker.make(['right', 'rear_right'], 'positive'), #6
            rule_maker.make(['right', 'right'], 'positive'), #7
            rule_maker.make(['right', 'front'], 'positive'), #8
            rule_maker.make(['right', 'left'], 'positive'), #9
            rule_maker.make(['right', 'rear_left'], 'positive'), #10
            
            rule_maker.make(['front', 'rear_right'], 'zero'), #11
            rule_maker.make(['front', 'right'], 'zero'), #12
            rule_maker.make(['front', 'front'], 'positive'), #13
            rule_maker.make(['front', 'left'], 'positive'), #14
            rule_maker.make(['front', 'rear_left'], 'positive'), #15
            
            rule_maker.make(['left', 'rear_right'], 'zero'), #16
            rule_maker.make(['left', 'right'], 'negative'), #17
            rule_maker.make(['left', 'front'], 'negative'), #18
            rule_maker.make(['left', 'left'], 'zero'), #19
            rule_maker.make(['left', 'rear_left'], 'zero'), #20
            
            rule_maker.make(['rear_left', 'rear_right'], 'zero'), #21
            rule_maker.make(['rear_left', 'right'], 'zero'), #22
            rule_maker.make(['rear_left', 'front'], 'negative'), #23
            rule_maker.make(['rear_left', 'left'], 'negative'), #24
            rule_maker.make(['rear_left', 'rear_left'], 'negative'), #25
            ]

        right_wheel_rules = [
            rule_maker.make(['rear_right', 'rear_right'], 'negative'), #1
            rule_maker.make(['rear_right', 'right'], 'negative'), #2
            rule_maker.make(['rear_right', 'front'], 'negative'), #3
            rule_maker.make(['rear_right', 'left'], 'zero'), #4
            rule_maker.make(['rear_right', 'rear_left'], 'zero'), #5

            rule_maker.make(['right', 'rear_right'], 'zero'), #6
            rule_maker.make(['right', 'right'], 'zero'), #7
            rule_maker.make(['right', 'front'], 'negative'), #8
            rule_maker.make(['right', 'left'], 'negative'), #9
            rule_maker.make(['right', 'rear_left'], 'zero'), #10
            
            rule_maker.make(['front', 'rear_right'], 'positive'), #11
            rule_maker.make(['front', 'right'], 'positive'), #12
            rule_maker.make(['front', 'front'], 'positive'), #13
            rule_maker.make(['front', 'left'], 'zero'), #14
            rule_maker.make(['front', 'rear_left'], 'zero'), #15
            
            rule_maker.make(['left', 'rear_right'], 'positive'), #16
            rule_maker.make(['left', 'right'], 'positive'), #17
            rule_maker.make(['left', 'front'], 'positive'), #18
            rule_maker.make(['left', 'left'], 'positive'), #19
            rule_maker.make(['left', 'rear_left'], 'positive'), #20
            
            rule_maker.make(['rear_left', 'rear_right'], 'positive'), #21
            rule_maker.make(['rear_left', 'right'], 'positive'), #22
            rule_maker.make(['rear_left', 'front'], 'zero'), #23
            rule_maker.make(['rear_left', 'left'], 'zero'), #24
            rule_maker.make(['rear_left', 'rear_left'], 'zero'), #25
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
        while(i < 1e4):
            variable['ball_angle'].value = match.get_ball_angle()
            variable['target_angle'].value = match.get_target_angle()
            left_wheel = fuzzy_left.output()
            right_wheel = fuzzy_right.output()
            match.act(left_wheel, right_wheel)
            i += 1
