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
##REAR_RIGHT = (-PI, -PI, -3*PI/4, -5*PI/8)
##RIGHT = (-3*PI/4, -5*PI/8, -PI/4, 0)
##FRONT = (-PI/4, 0, 0, PI/4)
##LEFT = (0, PI/4, 5*PI/8, 3*PI/4)
##REAR_LEFT = (5*PI/8, 3*PI/4, PI, PI)
RIGHT = (-PI, -PI, -PI/2, 0)
FRONT = (-PI/2, 0, 0, PI/2)
LEFT = (0, PI/2, PI, PI)

##NEG_ST = (-32, -32, -32, -16)
##NEG = (-32, -16, -8, -4)
##NEG_WK = (-8, -4, -2, -0)
##ZER = (-2, -0, 0, 2)
##POS_WK = (0, 2, 4, 8)
##POS = (4, 8, 16, 32)
##POS_ST = (16, 32, 32, 32)
NST = (-1e10, -20, -10, -9)
NEG = (-10, -9, -1, 0)
ZER = (-1, 0, 0, 1)
POS = (0, -1, 9, 10)
PST = (9, 10, 20, 1e10)

CLOSE = (0, 0, 80, 120)
NEAR = (80, 120, 750, 1500)
FAR = (750, 1500, 2000, 2000)

CLOCKWISE = (-10, -10, -0.1, 0)
SPIN_ZERO = (-0.1, 0, 0, 0.1)
ANTICLOCKWISE = (0, 0.1, 10, 10)

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
            'ball_angle': Variable({'right': RIGHT, 'front': FRONT, 'left': LEFT}, name = 'ball_angle'),
            'target_angle': Variable({'right': RIGHT, 'front': FRONT, 'left': LEFT}, name = 'target_angle'),
            'ball_distance': Variable({'close': CLOSE, 'near': NEAR, 'far': FAR}, 'ball_distance'),
            
            'left_wheel': Variable({'negative_strong': NST, 'negative': NEG, 'zero': ZER, 'positive': POS, 'positive_strong': PST}, 'left_wheel'),
            'right_wheel': Variable({'negative_strong': NST, 'negative': NEG, 'zero': ZER, 'positive': POS, 'positive_strong': PST}, 'right_wheel'),

            'spin': Variable({'negative': CLOCKWISE, 'zero': SPIN_ZERO, 'positive': ANTICLOCKWISE}, 'spin')
            }
        
        left_wheel_rule_maker = RuleGenerator([
            self.__variable['ball_angle'],
            self.__variable['target_angle'],
            self.__variable['spin']
            ], self.__variable['left_wheel'])

        right_wheel_rule_maker = RuleGenerator([
            self.__variable['ball_angle'],
            self.__variable['target_angle'],
            self.__variable['spin']
            ], self.__variable['right_wheel'])
        
        left_wheel_rules = [
            left_wheel_rule_maker.make(['right', 'right', 'negative'], 'positive'), #1 -> positive, zero
            left_wheel_rule_maker.make(['right', 'right', 'zero'], 'positive_strong'), #2 -> positive_strong, zero
            left_wheel_rule_maker.make(['right', 'right', 'positive'], 'positive_strong'), #3 -> positive_strong, negative
            
            left_wheel_rule_maker.make(['right', 'front', 'negative'], 'zero'), #4 -> zero, negative
            left_wheel_rule_maker.make(['right', 'front', 'zero'], 'negative'), #5 -> negative, negative_strong
            left_wheel_rule_maker.make(['right', 'front', 'positive'], 'zero'), #6 -> zero, negative_strong
            
            left_wheel_rule_maker.make(['right', 'left', 'negative'], 'positive'), #7 -> positive, zero
            left_wheel_rule_maker.make(['right', 'left', 'zero'], 'positive_strong'), #8 -> positive_strong, positive
            left_wheel_rule_maker.make(['right', 'left', 'positive'], 'positive_strong'), #9 -> positive_strong, negative

            ###
            left_wheel_rule_maker.make(['front', 'right', 'negative'], 'negative'), #10 -> negative, positive_strong
            left_wheel_rule_maker.make(['front', 'right', 'zero'], 'zero'), #11 -> zero, positive
            left_wheel_rule_maker.make(['front', 'right', 'positive'], 'zero'), #12 -> zero, positive
            
            left_wheel_rule_maker.make(['front', 'front', 'negative'], 'zero'), #13 -> zero, positive_strong
            left_wheel_rule_maker.make(['front', 'front', 'zero'], 'positive'), #14 -> positive, positive
            left_wheel_rule_maker.make(['front', 'front', 'positive'], 'positive_strong'), #15 -> positive_strong, zero
            
            left_wheel_rule_maker.make(['front', 'left', 'negative'], 'positive'), #16 -> positive, zero
            left_wheel_rule_maker.make(['front', 'left', 'zero'], 'positive'), #17 -> positive, zero
            left_wheel_rule_maker.make(['front', 'left', 'positive'], 'positive_strong'), #18 -> positive_strong, negative

            ###
            left_wheel_rule_maker.make(['left', 'right', 'negative'], 'zero'), #19 -> zero, positive_strong
            left_wheel_rule_maker.make(['left', 'right', 'zero'], 'positive'), #20 -> positive, positive_strong
            left_wheel_rule_maker.make(['left', 'right', 'positive'], 'zero'), #21 -> zero, positive
            
            left_wheel_rule_maker.make(['left', 'front', 'negative'], 'zero'),
            left_wheel_rule_maker.make(['left', 'front', 'zero'], 'negative_strong'), #23 -> negative_strong, negative
            left_wheel_rule_maker.make(['left', 'front', 'positive'], 'negative_strong'), #24 -> negative_strong, negative
            
            left_wheel_rule_maker.make(['left', 'left', 'negative'], 'negative'), #25 -> negative, positive_strong
            left_wheel_rule_maker.make(['left', 'left', 'zero'], 'zero'), #26 -> zero, positive_strong
            left_wheel_rule_maker.make(['left', 'left', 'positive'], 'zero') #27 -> zero, positive
            ]

        right_wheel_rules = [
            right_wheel_rule_maker.make(['right', 'right', 'negative'], 'zero'), #1 -> positive, zero
            right_wheel_rule_maker.make(['right', 'right', 'zero'], 'zero'), #2 -> positive_strong, zero
            right_wheel_rule_maker.make(['right', 'right', 'positive'], 'negative'), #3 -> positive_strong, negative
            
            right_wheel_rule_maker.make(['right', 'front', 'negative'], 'negative'), #4 -> zero, negative
            right_wheel_rule_maker.make(['right', 'front', 'zero'], 'negative_strong'), #5 -> negative, negative_strong
            right_wheel_rule_maker.make(['right', 'front', 'positive'], 'zero'),
            
            right_wheel_rule_maker.make(['right', 'left', 'negative'], 'zero'), #7 -> positive, zero
            right_wheel_rule_maker.make(['right', 'left', 'zero'], 'positive'), #8 -> positive_strong, positive
            right_wheel_rule_maker.make(['right', 'left', 'positive'], 'negative'), #9 -> positive_strong, negative

            ###
            right_wheel_rule_maker.make(['front', 'right', 'negative'], 'positive_strong'), #10 -> negative, positive_strong
            right_wheel_rule_maker.make(['front', 'right', 'zero'], 'positive'), #11 -> zero, positive
            right_wheel_rule_maker.make(['front', 'right', 'positive'], 'positive'), #12 -> zero, positive
            
            right_wheel_rule_maker.make(['front', 'front', 'negative'], 'zero'),
            right_wheel_rule_maker.make(['front', 'front', 'zero'], 'positive'), #14 -> positive, positive
            right_wheel_rule_maker.make(['front', 'front', 'positive'], 'zero'), #15 -> positive_strong, zero
            
            right_wheel_rule_maker.make(['front', 'left', 'negative'], 'zero'), #16 -> positive, zero
            right_wheel_rule_maker.make(['front', 'left', 'zero'], 'zero'), #17 -> positive, zero
            right_wheel_rule_maker.make(['front', 'left', 'positive'], 'negative'), #18 -> positive_strong, negative

            ###
            right_wheel_rule_maker.make(['left', 'right', 'negative'], 'positive_strong'), #19 -> zero, positive_strong
            right_wheel_rule_maker.make(['left', 'right', 'zero'], 'positive_strong'), #20 -> positive, positive_strong
            right_wheel_rule_maker.make(['left', 'right', 'positive'], 'positive'), #21 -> zero, positive
            
            right_wheel_rule_maker.make(['left', 'front', 'negative'], 'zero'),
            right_wheel_rule_maker.make(['left', 'front', 'zero'], 'negative'), #23 -> negative_strong, negative
            right_wheel_rule_maker.make(['left', 'front', 'positive'], 'negative'), #24 -> negative_strong, negative
            
            right_wheel_rule_maker.make(['left', 'left', 'negative'], 'positive_strong'), #25 -> negative, positive_strong
            right_wheel_rule_maker.make(['left', 'left', 'zero'], 'positive_strong'), #26 -> zero, positive_strong
            right_wheel_rule_maker.make(['left', 'left', 'positive'], 'positive') #27 -> zero, positive
            ]
            
        self.__left_wheel_fis = FuzzySystem(left_wheel_rules, self.__variable['left_wheel'], 'left')
        self.__right_wheel_fis = FuzzySystem(right_wheel_rules, self.__variable['right_wheel'], 'right')
		
    def play(self):
        """
        Play using fuzzy controller
        """
        fuzzy_left = self.__left_wheel_fis
        fuzzy_right = self.__right_wheel_fis
        
        variable = self.__variable
        match = self.__match
        while(True):
            # Gets updated environment values
            variable['ball_angle'].value = match.get_ball_angle()
            variable['target_angle'].value = match.get_target_angle()
            variable['ball_distance'].value = match.get_ball_distance()
            variable['spin'].value = match.get_spin()

            # Updates fuzzy outputs
            fuzzy_left.update()
            fuzzy_right.update()

            # Calculate final forces for each wheel
            left_wheel = variable['left_wheel'].value
            right_wheel = variable['right_wheel'].value

            # Debug information
            if(abs(variable['left_wheel'].partition('zero').membership() - 1) < 1e-5 and abs(variable['right_wheel'].partition('zero').membership() - 1) < 1e-5):
                print('INPUTS:', '-----', sep = '\n')
                print(variable['ball_angle'])
                print(variable['target_angle'])
                print(variable['ball_distance'])
                print(variable['spin'])
                
                print('\nOUTPUTS:', '-----', sep = '\n')
                print(variable['left_wheel'])
                print(variable['right_wheel'])
                
                print('output:', left_wheel, right_wheel)
                print('-'*30)
                input('')

            # Act
            match.act(left_wheel, right_wheel)

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

    
