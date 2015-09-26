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

NEG_ST = (-10, -10, -8, -6)
NEG = (-8, -6, -4, -2)
NEG_WK = (-4, -2, -1, 0)
ZER = (-1, 0, 0, 1)
POS_WK = (0, 1, 2, 4)
POS = (2, 4, 6, 8)
POS_ST = (6, 8, 10, 10)

CLOSE = (0, 0, 80, 120)
NEAR = (80, 120, 750, 1500)
FAR = (750, 1500, 2000, 2000)

CLOCKWISE = (-1, -1, -0.02, 0)
SPIN_ZERO = (-0.02, 0, 0, 0.02)
ANTICLOCKWISE = (0, 0.02, 1, 1)

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
            'ball_distance': Variable({'close': CLOSE, 'near': NEAR, 'far': FAR}),
            
            'left_wheel': Variable({'negative_strong': NEG_ST, 'negative': NEG, 'negative_weak': NEG_WK, 'zero': ZER, 'positive_weak': POS_WK, 'positive': POS, 'positive_strong': POS_ST}, 'left_wheel'),
            'right_wheel': Variable({'negative_strong': NEG_ST, 'negative': NEG, 'negative_weak': NEG_WK, 'zero': ZER, 'positive_weak': POS_WK, 'positive': POS, 'positive_strong': POS_ST}, 'right_wheel'),

            'left_correction': Variable({'negative_strong': NEG_ST, 'negative': NEG, 'negative_weak': NEG_WK, 'zero': ZER, 'positive_weak': POS_WK, 'positive': POS, 'positive_strong': POS_ST}, 'left_wheel'),
            'right_correction': Variable({'negative_strong': NEG_ST, 'negative': NEG, 'negative_weak': NEG_WK, 'zero': ZER, 'positive_weak': POS_WK, 'positive': POS, 'positive_strong': POS_ST}, 'right_wheel'),

            'spin': Variable({'negative': CLOCKWISE, 'zero': SPIN_ZERO, 'positive': ANTICLOCKWISE}, 'spin')
            }
        
        left_wheel_rule_maker = RuleGenerator([
            self.__variable['ball_angle'],
            self.__variable['target_angle'],
            self.__variable['ball_distance']
            ], self.__variable['left_wheel'])

        right_wheel_rule_maker = RuleGenerator([
            self.__variable['ball_angle'],
            self.__variable['target_angle'],
            self.__variable['ball_distance']
            ], self.__variable['right_wheel'])

        left_wheel_spin_rule_maker = RuleGenerator([
            self.__variable['left_wheel'],
            self.__variable['right_wheel'],
            self.__variable['spin']
            ], self.__variable['left_correction'])

        right_wheel_spin_rule_maker = RuleGenerator([
            self.__variable['left_wheel'],
            self.__variable['right_wheel'],
            self.__variable['spin']
            ], self.__variable['right_correction'])
        
        left_wheel_rules = [
            left_wheel_rule_maker.make(['rear_right', 'rear_right', 'far'], 'positive'),       #1 -> positive weak - positive strong
            left_wheel_rule_maker.make(['rear_right', 'right', 'far'], 'positive'),            #2 -> positive weak - positive strong
            left_wheel_rule_maker.make(['rear_right', 'front', 'far'], 'positive'),            #3 -> positive weak - positive strong
            left_wheel_rule_maker.make(['rear_right', 'left', 'far'], 'positive_strong'),      #4 -> positive strong - positive weak
            left_wheel_rule_maker.make(['rear_right', 'rear_left', 'far'], 'positive_strong'), #5 -> positive strong - positive weak

            left_wheel_rule_maker.make(['right', 'rear_right', 'far'], 'positive_strong'),     #6 -> positive strong - positive weak
            left_wheel_rule_maker.make(['right', 'right', 'far'], 'positive_strong'),                 #7 -> negative weak - negative strong
            left_wheel_rule_maker.make(['right', 'front', 'far'], 'negative'),                 #8 -> negative weak - negative strong
            left_wheel_rule_maker.make(['right', 'left', 'far'], 'positive_strong'),           #9 -> positive strong - positive
            left_wheel_rule_maker.make(['right', 'rear_left', 'far'], 'positive_strong'),      #10 -> positive strong - positive
            
            left_wheel_rule_maker.make(['front', 'rear_right', 'far'], 'positive_strong'), #11
            left_wheel_rule_maker.make(['front', 'right', 'far'], 'positive_strong'), #12
            left_wheel_rule_maker.make(['front', 'front', 'far'], 'positive_strong'), #13
            left_wheel_rule_maker.make(['front', 'left', 'far'], 'positive_strong'), #14
            left_wheel_rule_maker.make(['front', 'rear_left', 'far'], 'positive_strong'), #15
            
            left_wheel_rule_maker.make(['left', 'rear_right', 'far'], 'positive_strong'), #16
            left_wheel_rule_maker.make(['left', 'right', 'far'], 'positive_strong'), #17
            left_wheel_rule_maker.make(['left', 'front', 'far'], 'positive_strong'), #18
            left_wheel_rule_maker.make(['left', 'left', 'far'], 'positive_strong'), #19
            left_wheel_rule_maker.make(['left', 'rear_left', 'far'], 'positive_strong'), #20
            
            left_wheel_rule_maker.make(['rear_left', 'rear_right', 'far'], 'positive_strong'), #21
            left_wheel_rule_maker.make(['rear_left', 'right', 'far'], 'positive_strong'), #22
            left_wheel_rule_maker.make(['rear_left', 'front', 'far'], 'positive_strong'), #23
            left_wheel_rule_maker.make(['rear_left', 'left', 'far'], 'positive_strong'), #24
            left_wheel_rule_maker.make(['rear_left', 'rear_left', 'far'], 'positive_strong'), #25

            ###
            left_wheel_rule_maker.make(['rear_right', 'rear_right', 'near'], 'positive_strong'), #26
            left_wheel_rule_maker.make(['rear_right', 'right', 'near'], 'positive_strong'), #27
            left_wheel_rule_maker.make(['rear_right', 'front', 'near'], 'positive_strong'), #28
            left_wheel_rule_maker.make(['rear_right', 'left', 'near'], 'positive_strong'), #29
            left_wheel_rule_maker.make(['rear_right', 'rear_left', 'near'], 'positive_strong'), #30

            left_wheel_rule_maker.make(['right', 'rear_right', 'near'], 'positive_strong'), #31
            left_wheel_rule_maker.make(['right', 'right', 'near'], 'positive_strong'), #32
            left_wheel_rule_maker.make(['right', 'front', 'near'], 'positive_strong'), #33
            left_wheel_rule_maker.make(['right', 'left', 'near'], 'positive_strong'), #34
            left_wheel_rule_maker.make(['right', 'rear_left', 'near'], 'positive_strong'), #135
            
            left_wheel_rule_maker.make(['front', 'rear_right', 'near'], 'positive_strong'), #36
            left_wheel_rule_maker.make(['front', 'right', 'near'], 'positive_strong'), #37
            left_wheel_rule_maker.make(['front', 'front', 'near'], 'positive_strong'), #38
            left_wheel_rule_maker.make(['front', 'left', 'near'], 'positive_strong'), #39
            left_wheel_rule_maker.make(['front', 'rear_left', 'near'], 'positive_strong'), #40
            
            left_wheel_rule_maker.make(['left', 'rear_right', 'near'], 'positive_strong'), #41
            left_wheel_rule_maker.make(['left', 'right', 'near'], 'positive_strong'), #42
            left_wheel_rule_maker.make(['left', 'front', 'near'], 'positive_strong'), #43
            left_wheel_rule_maker.make(['left', 'left', 'near'], 'positive_strong'), #44
            left_wheel_rule_maker.make(['left', 'rear_left', 'near'], 'positive_strong'), #45
            
            left_wheel_rule_maker.make(['rear_left', 'rear_right', 'near'], 'positive_strong'), #46
            left_wheel_rule_maker.make(['rear_left', 'right', 'near'], 'positive_strong'), #47
            left_wheel_rule_maker.make(['rear_left', 'front', 'near'], 'positive_strong'), #48
            left_wheel_rule_maker.make(['rear_left', 'left', 'near'], 'positive_strong'), #49
            left_wheel_rule_maker.make(['rear_left', 'rear_left', 'near'], 'positive_strong'), #50

            ###
            left_wheel_rule_maker.make(['rear_right', 'rear_right', 'close'], 'positive_strong'), #51
            left_wheel_rule_maker.make(['rear_right', 'right', 'close'], 'positive_strong'), #52
            left_wheel_rule_maker.make(['rear_right', 'front', 'close'], 'positive_strong'), #53
            left_wheel_rule_maker.make(['rear_right', 'left', 'close'], 'positive_strong'), #54
            left_wheel_rule_maker.make(['rear_right', 'rear_left', 'close'], 'positive_strong'), #555

            left_wheel_rule_maker.make(['right', 'rear_right', 'close'], 'positive_strong'), #56
            left_wheel_rule_maker.make(['right', 'right', 'close'], 'positive_strong'), #57
            left_wheel_rule_maker.make(['right', 'front', 'close'], 'positive_strong'), #58
            left_wheel_rule_maker.make(['right', 'left', 'close'], 'positive_strong'), #59
            left_wheel_rule_maker.make(['right', 'rear_left', 'close'], 'positive_strong'), #60
            
            left_wheel_rule_maker.make(['front', 'rear_right', 'close'], 'positive_strong'), #61
            left_wheel_rule_maker.make(['front', 'right', 'close'], 'positive_strong'), #62
            left_wheel_rule_maker.make(['front', 'front', 'close'], 'positive_strong'), #63
            left_wheel_rule_maker.make(['front', 'left', 'close'], 'positive_strong'), #64
            left_wheel_rule_maker.make(['front', 'rear_left', 'close'], 'positive_strong'), #65
            
            left_wheel_rule_maker.make(['left', 'rear_right', 'close'], 'positive_strong'), #66
            left_wheel_rule_maker.make(['left', 'right', 'close'], 'positive_strong'), #67
            left_wheel_rule_maker.make(['left', 'front', 'close'], 'positive_strong'), #68
            left_wheel_rule_maker.make(['left', 'left', 'close'], 'positive_strong'), #69
            left_wheel_rule_maker.make(['left', 'rear_left', 'close'], 'positive_strong'), #70
            
            left_wheel_rule_maker.make(['rear_left', 'rear_right', 'close'], 'positive_strong'), #71
            left_wheel_rule_maker.make(['rear_left', 'right', 'close'], 'positive_strong'), #72
            left_wheel_rule_maker.make(['rear_left', 'front', 'close'], 'positive_strong'), #73
            left_wheel_rule_maker.make(['rear_left', 'left', 'close'], 'positive_strong'), #74
            left_wheel_rule_maker.make(['rear_left', 'rear_left', 'close'], 'positive_strong'), #75
            ]

        right_wheel_rules = [
            right_wheel_rule_maker.make(['rear_right', 'rear_right', 'far'], 'positive_strong'), #1 -> positive weak - positive strong
            right_wheel_rule_maker.make(['rear_right', 'right', 'far'], 'positive_strong'),      #2 -> positive weak - positive strong
            right_wheel_rule_maker.make(['rear_right', 'front', 'far'], 'positive_strong'),      #3 -> positive weak - positive strong
            right_wheel_rule_maker.make(['rear_right', 'left', 'far'], 'positive_weak'),         #4 -> positive strong - positive weak
            right_wheel_rule_maker.make(['rear_right', 'rear_left', 'far'], 'positive_weak'),    #5 -> positive strong - positive weak

            right_wheel_rule_maker.make(['right', 'rear_right', 'far'], 'positive_weak'),        #6 -> positive strong - positive weak
            right_wheel_rule_maker.make(['right', 'right', 'far'], 'negative_strong'),           #7 -> negative weak - negative strong
            right_wheel_rule_maker.make(['right', 'front', 'far'], 'negative_strong'),           #8 -> negative weak - negative strong
            right_wheel_rule_maker.make(['right', 'left', 'far'], 'positive'),                   #9 -> positive strong - positive
            right_wheel_rule_maker.make(['right', 'rear_left', 'far'], 'positive'),              #10 -> positive strong - positive
            
            right_wheel_rule_maker.make(['front', 'rear_right', 'far'], 'positive_strong'), #11
            right_wheel_rule_maker.make(['front', 'right', 'far'], 'positive_strong'), #12
            right_wheel_rule_maker.make(['front', 'front', 'far'], 'positive_strong'), #13
            right_wheel_rule_maker.make(['front', 'left', 'far'], 'positive_strong'), #14
            right_wheel_rule_maker.make(['front', 'rear_left', 'far'], 'positive_strong'), #15
            
            right_wheel_rule_maker.make(['left', 'rear_right', 'far'], 'positive_strong'), #16
            right_wheel_rule_maker.make(['left', 'right', 'far'], 'positive_strong'), #17
            right_wheel_rule_maker.make(['left', 'front', 'far'], 'positive_strong'), #18
            right_wheel_rule_maker.make(['left', 'left', 'far'], 'positive_strong'), #19
            right_wheel_rule_maker.make(['left', 'rear_left', 'far'], 'positive_strong'), #20
            
            right_wheel_rule_maker.make(['rear_left', 'rear_right', 'far'], 'positive_strong'), #21
            right_wheel_rule_maker.make(['rear_left', 'right', 'far'], 'positive_strong'), #22
            right_wheel_rule_maker.make(['rear_left', 'front', 'far'], 'positive_strong'), #23
            right_wheel_rule_maker.make(['rear_left', 'left', 'far'], 'positive_strong'), #24
            right_wheel_rule_maker.make(['rear_left', 'rear_left', 'far'], 'positive_strong'), #25

            ###
            right_wheel_rule_maker.make(['rear_right', 'rear_right', 'near'], 'positive_strong'), #26
            right_wheel_rule_maker.make(['rear_right', 'right', 'near'], 'positive_strong'), #27
            right_wheel_rule_maker.make(['rear_right', 'front', 'near'], 'positive_strong'), #28
            right_wheel_rule_maker.make(['rear_right', 'left', 'near'], 'positive_strong'), #29
            right_wheel_rule_maker.make(['rear_right', 'rear_left', 'near'], 'positive_strong'), #30

            right_wheel_rule_maker.make(['right', 'rear_right', 'near'], 'positive_strong'), #31
            right_wheel_rule_maker.make(['right', 'right', 'near'], 'negative_strong'), #32
            right_wheel_rule_maker.make(['right', 'front', 'near'], 'positive_strong'), #33
            right_wheel_rule_maker.make(['right', 'left', 'near'], 'positive_strong'), #34
            right_wheel_rule_maker.make(['right', 'rear_left', 'near'], 'positive_strong'), #135
            
            right_wheel_rule_maker.make(['front', 'rear_right', 'near'], 'positive_strong'), #36
            right_wheel_rule_maker.make(['front', 'right', 'near'], 'positive_strong'), #37
            right_wheel_rule_maker.make(['front', 'front', 'near'], 'positive_strong'), #38
            right_wheel_rule_maker.make(['front', 'left', 'near'], 'positive_strong'), #39
            right_wheel_rule_maker.make(['front', 'rear_left', 'near'], 'positive_strong'), #40
            
            right_wheel_rule_maker.make(['left', 'rear_right', 'near'], 'positive_strong'), #41
            right_wheel_rule_maker.make(['left', 'right', 'near'], 'positive_strong'), #42
            right_wheel_rule_maker.make(['left', 'front', 'near'], 'positive_strong'), #43
            right_wheel_rule_maker.make(['left', 'left', 'near'], 'positive_strong'), #44
            right_wheel_rule_maker.make(['left', 'rear_left', 'near'], 'positive_strong'), #45
            
            right_wheel_rule_maker.make(['rear_left', 'rear_right', 'near'], 'positive_strong'), #46
            right_wheel_rule_maker.make(['rear_left', 'right', 'near'], 'positive_strong'), #47
            right_wheel_rule_maker.make(['rear_left', 'front', 'near'], 'positive_strong'), #48
            right_wheel_rule_maker.make(['rear_left', 'left', 'near'], 'positive_strong'), #49
            right_wheel_rule_maker.make(['rear_left', 'rear_left', 'near'], 'positive_strong'), #50

            ###
            right_wheel_rule_maker.make(['rear_right', 'rear_right', 'close'], 'positive_strong'), #51
            right_wheel_rule_maker.make(['rear_right', 'right', 'close'], 'positive_strong'), #52
            right_wheel_rule_maker.make(['rear_right', 'front', 'close'], 'positive_strong'), #53
            right_wheel_rule_maker.make(['rear_right', 'left', 'close'], 'positive_strong'), #54
            right_wheel_rule_maker.make(['rear_right', 'rear_left', 'close'], 'positive_strong'), #555

            right_wheel_rule_maker.make(['right', 'rear_right', 'close'], 'positive_strong'), #56
            right_wheel_rule_maker.make(['right', 'right', 'close'], 'positive_strong'), #57
            right_wheel_rule_maker.make(['right', 'front', 'close'], 'positive_strong'), #58
            right_wheel_rule_maker.make(['right', 'left', 'close'], 'positive_strong'), #59
            right_wheel_rule_maker.make(['right', 'rear_left', 'close'], 'positive_strong'), #60
            
            right_wheel_rule_maker.make(['front', 'rear_right', 'close'], 'positive_strong'), #61
            right_wheel_rule_maker.make(['front', 'right', 'close'], 'positive_strong'), #62
            right_wheel_rule_maker.make(['front', 'front', 'close'], 'positive_strong'), #63
            right_wheel_rule_maker.make(['front', 'left', 'close'], 'positive_strong'), #64
            right_wheel_rule_maker.make(['front', 'rear_left', 'close'], 'positive_strong'), #65
            
            right_wheel_rule_maker.make(['left', 'rear_right', 'close'], 'positive_strong'), #66
            right_wheel_rule_maker.make(['left', 'right', 'close'], 'positive_strong'), #67
            right_wheel_rule_maker.make(['left', 'front', 'close'], 'positive_strong'), #68
            right_wheel_rule_maker.make(['left', 'left', 'close'], 'positive_strong'), #69
            right_wheel_rule_maker.make(['left', 'rear_left', 'close'], 'positive_strong'), #70
            
            right_wheel_rule_maker.make(['rear_left', 'rear_right', 'close'], 'positive_strong'), #71
            right_wheel_rule_maker.make(['rear_left', 'right', 'close'], 'positive_strong'), #72
            right_wheel_rule_maker.make(['rear_left', 'front', 'close'], 'positive_strong'), #73
            right_wheel_rule_maker.make(['rear_left', 'left', 'close'], 'positive_strong'), #74
            right_wheel_rule_maker.make(['rear_left', 'rear_left', 'close'], 'positive_strong'), #75
            ]

        left_wheel_spin_rules = [
            left_wheel_spin_rule_maker.make(['negative_strong', 'negative_strong', 'negative'], 'negative_strong'), #1 -> negative, positive
            left_wheel_spin_rule_maker.make(['negative_strong', 'negative_strong', 'zero'], 'zero'),         #2 -> zero, zero
            left_wheel_spin_rule_maker.make(['negative_strong', 'negative_strong', 'positive'], 'positive_strong'), #3 -> positive, negative

            left_wheel_spin_rule_maker.make(['negative_strong', 'negative', 'negative'], 'negative_strong'),        #4 -> negative, positive
            left_wheel_spin_rule_maker.make(['negative_strong', 'negative', 'zero'], 'zero'),                #5 -> zero, zero
            left_wheel_spin_rule_maker.make(['negative_strong', 'negative', 'positive'], 'positive_strong'),        #6 -> positive, negative

            left_wheel_spin_rule_maker.make(['negative_strong', 'zero', 'negative'], 'negative_strong'),            #7 -> negative, positive
            left_wheel_spin_rule_maker.make(['negative_strong', 'zero', 'zero'], 'zero'),                    #8 -> zero, zero
            left_wheel_spin_rule_maker.make(['negative_strong', 'zero', 'positive'], 'positive_strong'),            #9 -> positive, negative
            
            left_wheel_spin_rule_maker.make(['negative_strong', 'positive', 'negative'], 'negative_strong'),        #10 -> negative, positive
            left_wheel_spin_rule_maker.make(['negative_strong', 'positive', 'zero'], 'zero'),                #11 -> zero, zero
            left_wheel_spin_rule_maker.make(['negative_strong', 'positive', 'positive'], 'positive_strong'),        #12 -> positive, negative
            
            left_wheel_spin_rule_maker.make(['negative_strong', 'positive_strong', 'negative'], 'negative_strong'), #13 -> negative, positive
            left_wheel_spin_rule_maker.make(['negative_strong', 'positive_strong', 'zero'], 'zero'),         #14 -> zero, zero
            left_wheel_spin_rule_maker.make(['negative_strong', 'positive_strong', 'positive'], 'positive_strong'), #15 -> positive, negative

            ###
            left_wheel_spin_rule_maker.make(['negative', 'negative_strong', 'negative'], 'negative_strong'),        #16 -> negative, positive
            left_wheel_spin_rule_maker.make(['negative', 'negative_strong', 'zero'], 'zero'),                #17 -> zero, zero
            left_wheel_spin_rule_maker.make(['negative', 'negative_strong', 'positive'], 'positive_strong'),        #18 -> positive, negative
            
            left_wheel_spin_rule_maker.make(['negative', 'negative', 'negative'], 'negative_strong'),               #19 -> negative, positive
            left_wheel_spin_rule_maker.make(['negative', 'negative', 'zero'], 'zero'),                       #20 -> zero, zero
            left_wheel_spin_rule_maker.make(['negative', 'negative', 'positive'], 'positive_strong'),               #21 -> positive, negative
            
            left_wheel_spin_rule_maker.make(['negative', 'zero', 'negative'], 'negative_strong'),                   #22 -> negative, positive
            left_wheel_spin_rule_maker.make(['negative', 'zero', 'zero'], 'zero'),                           #23 -> zero, zero
            left_wheel_spin_rule_maker.make(['negative', 'zero', 'positive'], 'positive_strong'),                   #24 -> positive, negative
            
            left_wheel_spin_rule_maker.make(['negative', 'positive', 'negative'], 'negative_strong'),               #25 -> negative, positive
            left_wheel_spin_rule_maker.make(['negative', 'positive', 'zero'], 'zero'),                       #26 -> zero, zero
            left_wheel_spin_rule_maker.make(['negative', 'positive', 'positive'], 'positive_strong'),               #27 -> positive, negative
            
            left_wheel_spin_rule_maker.make(['negative', 'positive_strong', 'negative'], 'negative_strong'),        #28 -> negative, positive
            left_wheel_spin_rule_maker.make(['negative', 'positive_strong', 'zero'], 'zero'),                #29 -> zero, zero
            left_wheel_spin_rule_maker.make(['negative', 'positive_strong', 'positive'], 'positive_strong'),        #30 -> positive, negative

            ###
            left_wheel_spin_rule_maker.make(['zero', 'negative_strong', 'negative'], 'negative_strong'),            #31 -> negative, positive
            left_wheel_spin_rule_maker.make(['zero', 'negative_strong', 'zero'], 'zero'),                    #32 -> zero, zero
            left_wheel_spin_rule_maker.make(['zero', 'negative_strong', 'positive'], 'positive_strong'),            #33 -> positive, negative
            
            left_wheel_spin_rule_maker.make(['zero', 'negative', 'negative'], 'negative_strong'),                   #34 -> negative, positive
            left_wheel_spin_rule_maker.make(['zero', 'negative', 'zero'], 'zero'),                           #35 -> zero, zero
            left_wheel_spin_rule_maker.make(['zero', 'negative', 'positive'], 'positive_strong'),                   #36 -> positive, negative
            
            left_wheel_spin_rule_maker.make(['zero', 'zero', 'negative'], 'negative_strong'),                       #37 -> negative, positive
            left_wheel_spin_rule_maker.make(['zero', 'zero', 'zero'], 'zero'),                               #38 -> zero, zero
            left_wheel_spin_rule_maker.make(['zero', 'zero', 'positive'], 'positive_strong'),                       #39 -> positive, negative
            
            left_wheel_spin_rule_maker.make(['zero', 'positive', 'negative'], 'negative_strong'),                   #40 -> negative, positive
            left_wheel_spin_rule_maker.make(['zero', 'positive', 'zero'], 'zero'),                           #41 -> zero, zero
            left_wheel_spin_rule_maker.make(['zero', 'positive', 'positive'], 'positive_strong'),                   #42 -> positive, negative
            
            left_wheel_spin_rule_maker.make(['zero', 'positive_strong', 'negative'], 'negative_strong'),            #43 -> negative, positive
            left_wheel_spin_rule_maker.make(['zero', 'positive_strong', 'zero'], 'zero'),                    #44 -> zero, zero
            left_wheel_spin_rule_maker.make(['zero', 'positive_strong', 'positive'], 'positive_strong'),            #45 -> positive, negative

            ###
            left_wheel_spin_rule_maker.make(['positive', 'negative_strong', 'negative'], 'negative_strong'),        #46 -> negative, positive
            left_wheel_spin_rule_maker.make(['positive', 'negative_strong', 'zero'], 'zero'),                #47 -> zero, zero
            left_wheel_spin_rule_maker.make(['positive', 'negative_strong', 'positive'], 'positive_strong'),        #48 -> positive, negative
            
            left_wheel_spin_rule_maker.make(['positive', 'negative', 'negative'], 'negative_strong'),               #46 -> negative, positive
            left_wheel_spin_rule_maker.make(['positive', 'negative', 'zero'], 'zero'),                       #47 -> zero, zero
            left_wheel_spin_rule_maker.make(['positive', 'negative', 'positive'], 'positive_strong'),               #48 -> positive, negative
            
            left_wheel_spin_rule_maker.make(['positive', 'zero', 'negative'], 'negative_strong'),                   #49 -> negative, positive
            left_wheel_spin_rule_maker.make(['positive', 'zero', 'zero'], 'zero'),                           #50 -> zero, zero
            left_wheel_spin_rule_maker.make(['positive', 'zero', 'positive'], 'positive_strong'),                   #51 -> positive, negative
            
            left_wheel_spin_rule_maker.make(['positive', 'positive', 'negative'], 'negative_strong'),               #52 -> negative, positive
            left_wheel_spin_rule_maker.make(['positive', 'positive', 'zero'], 'zero'),                       #53 -> zero, zero
            left_wheel_spin_rule_maker.make(['positive', 'positive', 'positive'], 'positive_strong'),               #54 -> positive, negative
            
            left_wheel_spin_rule_maker.make(['positive', 'positive_strong', 'negative'], 'negative_strong'),        #55 -> negative, positive
            left_wheel_spin_rule_maker.make(['positive', 'positive_strong', 'zero'], 'zero'),                #56 -> zero, zero
            left_wheel_spin_rule_maker.make(['positive', 'positive_strong', 'positive'], 'positive_strong'),        #57 -> positive, negative
            

            ###
            left_wheel_spin_rule_maker.make(['positive_strong', 'negative_strong', 'negative'], 'negative_strong'), #58 -> negative, positive
            left_wheel_spin_rule_maker.make(['positive_strong', 'negative_strong', 'zero'], 'zero'),         #59 -> zero, zero
            left_wheel_spin_rule_maker.make(['positive_strong', 'negative_strong', 'positive'], 'positive_strong'), #60 -> positive, negative
            
            left_wheel_spin_rule_maker.make(['positive_strong', 'negative', 'negative'], 'negative_strong'),        #61 -> negative, positive
            left_wheel_spin_rule_maker.make(['positive_strong', 'negative', 'zero'], 'zero'),                #62 -> zero, zero
            left_wheel_spin_rule_maker.make(['positive_strong', 'negative', 'positive'], 'positive_strong'),        #63 -> positive, negative
            
            left_wheel_spin_rule_maker.make(['positive_strong', 'zero', 'negative'], 'negative_strong'),            #64 -> negative, positive
            left_wheel_spin_rule_maker.make(['positive_strong', 'zero', 'zero'], 'zero'),                    #65 -> zero, zero
            left_wheel_spin_rule_maker.make(['positive_strong', 'zero', 'positive'], 'positive_strong'),            #66 -> positive, negative
            
            left_wheel_spin_rule_maker.make(['positive_strong', 'positive', 'negative'], 'negative_strong'),        #67 -> negative, positive
            left_wheel_spin_rule_maker.make(['positive_strong', 'positive', 'zero'], 'zero'),                #68 -> zero, zero
            left_wheel_spin_rule_maker.make(['positive_strong', 'positive', 'positive'], 'positive_strong'),        #69 -> positive, negative
            
            left_wheel_spin_rule_maker.make(['positive_strong', 'positive_strong', 'negative'], 'negative_strong'), #70 -> negative, positive
            left_wheel_spin_rule_maker.make(['positive_strong', 'positive_strong', 'zero'], 'zero'),         #71 -> zero, zero
            left_wheel_spin_rule_maker.make(['positive_strong', 'positive_strong', 'positive'], 'positive_strong') #72 -> positive, negative
            ]

        right_wheel_spin_rules = [
            right_wheel_spin_rule_maker.make(['negative_strong', 'negative_strong', 'negative'], 'positive_strong'), #1 -> negative, positive
            right_wheel_spin_rule_maker.make(['negative_strong', 'negative_strong', 'zero'], 'zero'),         #2 -> zero, zero
            right_wheel_spin_rule_maker.make(['negative_strong', 'negative_strong', 'positive'], 'negative_strong'), #3 -> positive, negative

            right_wheel_spin_rule_maker.make(['negative_strong', 'negative', 'negative'], 'positive_strong'),        #4 -> negative, positive
            right_wheel_spin_rule_maker.make(['negative_strong', 'negative', 'zero'], 'zero'),                #5 -> zero, zero
            right_wheel_spin_rule_maker.make(['negative_strong', 'negative', 'positive'], 'negative_strong'),        #6 -> positive, negative

            right_wheel_spin_rule_maker.make(['negative_strong', 'zero', 'negative'], 'positive_strong'),            #7 -> negative, positive
            right_wheel_spin_rule_maker.make(['negative_strong', 'zero', 'zero'], 'zero'),                    #8 -> zero, zero
            right_wheel_spin_rule_maker.make(['negative_strong', 'zero', 'positive'], 'negative_strong'),            #9 -> positive, negative
            
            right_wheel_spin_rule_maker.make(['negative_strong', 'positive', 'negative'], 'positive_strong'),        #10 -> negative, positive
            right_wheel_spin_rule_maker.make(['negative_strong', 'positive', 'zero'], 'zero'),                #11 -> zero, zero
            right_wheel_spin_rule_maker.make(['negative_strong', 'positive', 'positive'], 'negative_strong'),        #12 -> positive, negative
            
            right_wheel_spin_rule_maker.make(['negative_strong', 'positive_strong', 'negative'], 'positive_strong'), #13 -> negative, positive
            right_wheel_spin_rule_maker.make(['negative_strong', 'positive_strong', 'zero'], 'zero'),         #14 -> zero, zero
            right_wheel_spin_rule_maker.make(['negative_strong', 'positive_strong', 'positive'], 'negative_strong'), #15 -> positive, negative

            ###
            right_wheel_spin_rule_maker.make(['negative', 'negative_strong', 'negative'], 'positive_strong'),        #16 -> negative, positive
            right_wheel_spin_rule_maker.make(['negative', 'negative_strong', 'zero'], 'zero'),                #17 -> zero, zero
            right_wheel_spin_rule_maker.make(['negative', 'negative_strong', 'positive'], 'negative_strong'),        #18 -> positive, negative
            
            right_wheel_spin_rule_maker.make(['negative', 'negative', 'negative'], 'positive_strong'),               #19 -> negative, positive
            right_wheel_spin_rule_maker.make(['negative', 'negative', 'zero'], 'zero'),                       #20 -> zero, zero
            right_wheel_spin_rule_maker.make(['negative', 'negative', 'positive'], 'negative_strong'),               #21 -> positive, negative
            
            right_wheel_spin_rule_maker.make(['negative', 'zero', 'negative'], 'positive_strong'),                   #22 -> negative, positive
            right_wheel_spin_rule_maker.make(['negative', 'zero', 'zero'], 'zero'),                           #23 -> zero, zero
            right_wheel_spin_rule_maker.make(['negative', 'zero', 'positive'], 'negative_strong'),                   #24 -> positive, negative
            
            right_wheel_spin_rule_maker.make(['negative', 'positive', 'negative'], 'positive_strong'),               #25 -> negative, positive
            right_wheel_spin_rule_maker.make(['negative', 'positive', 'zero'], 'zero'),                       #26 -> zero, zero
            right_wheel_spin_rule_maker.make(['negative', 'positive', 'positive'], 'negative_strong'),               #27 -> positive, negative
            
            right_wheel_spin_rule_maker.make(['negative', 'positive_strong', 'negative'], 'positive_strong'),        #28 -> negative, positive
            right_wheel_spin_rule_maker.make(['negative', 'positive_strong', 'zero'], 'zero'),                #29 -> zero, zero
            right_wheel_spin_rule_maker.make(['negative', 'positive_strong', 'positive'], 'negative_strong'),        #30 -> positive, negative

            ###
            right_wheel_spin_rule_maker.make(['zero', 'negative_strong', 'negative'], 'positive_strong'),            #31 -> negative, positive
            right_wheel_spin_rule_maker.make(['zero', 'negative_strong', 'zero'], 'zero'),                    #32 -> zero, zero
            right_wheel_spin_rule_maker.make(['zero', 'negative_strong', 'positive'], 'negative_strong'),            #33 -> positive, negative
            
            right_wheel_spin_rule_maker.make(['zero', 'negative', 'negative'], 'positive_strong'),                   #34 -> negative, positive
            right_wheel_spin_rule_maker.make(['zero', 'negative', 'zero'], 'zero'),                           #35 -> zero, zero
            right_wheel_spin_rule_maker.make(['zero', 'negative', 'positive'], 'negative_strong'),                   #36 -> positive, negative
            
            right_wheel_spin_rule_maker.make(['zero', 'zero', 'negative'], 'positive_strong'),                       #37 -> negative, positive
            right_wheel_spin_rule_maker.make(['zero', 'zero', 'zero'], 'zero'),                               #38 -> zero, zero
            right_wheel_spin_rule_maker.make(['zero', 'zero', 'positive'], 'negative_strong'),                       #39 -> positive, negative
            
            right_wheel_spin_rule_maker.make(['zero', 'positive', 'negative'], 'positive_strong'),                   #40 -> negative, positive
            right_wheel_spin_rule_maker.make(['zero', 'positive', 'zero'], 'zero'),                           #41 -> zero, zero
            right_wheel_spin_rule_maker.make(['zero', 'positive', 'positive'], 'negative_strong'),                   #42 -> positive, negative
            
            right_wheel_spin_rule_maker.make(['zero', 'positive_strong', 'negative'], 'positive_strong'),            #43 -> negative, positive
            right_wheel_spin_rule_maker.make(['zero', 'positive_strong', 'zero'], 'zero'),                    #44 -> zero, zero
            right_wheel_spin_rule_maker.make(['zero', 'positive_strong', 'positive'], 'negative_strong'),            #45 -> positive, negative

            ###
            right_wheel_spin_rule_maker.make(['positive', 'negative_strong', 'negative'], 'positive_strong'),        #46 -> negative, positive
            right_wheel_spin_rule_maker.make(['positive', 'negative_strong', 'zero'], 'zero'),                #47 -> zero, zero
            right_wheel_spin_rule_maker.make(['positive', 'negative_strong', 'positive'], 'negative_strong'),        #48 -> positive, negative
            
            right_wheel_spin_rule_maker.make(['positive', 'negative', 'negative'], 'positive_strong'),               #46 -> negative, positive
            right_wheel_spin_rule_maker.make(['positive', 'negative', 'zero'], 'zero'),                       #47 -> zero, zero
            right_wheel_spin_rule_maker.make(['positive', 'negative', 'positive'], 'negative_strong'),               #48 -> positive, negative
            
            right_wheel_spin_rule_maker.make(['positive', 'zero', 'negative'], 'positive_strong'),                   #49 -> negative, positive
            right_wheel_spin_rule_maker.make(['positive', 'zero', 'zero'], 'zero'),                           #50 -> zero, zero
            right_wheel_spin_rule_maker.make(['positive', 'zero', 'positive'], 'negative_strong'),                   #51 -> positive, negative
            
            right_wheel_spin_rule_maker.make(['positive', 'positive', 'negative'], 'positive_strong'),               #52 -> negative, positive
            right_wheel_spin_rule_maker.make(['positive', 'positive', 'zero'], 'zero'),                       #53 -> zero, zero
            right_wheel_spin_rule_maker.make(['positive', 'positive', 'positive'], 'negative_strong'),               #54 -> positive, negative
            
            right_wheel_spin_rule_maker.make(['positive', 'positive_strong', 'negative'], 'positive_strong'),        #55 -> negative, positive
            right_wheel_spin_rule_maker.make(['positive', 'positive_strong', 'zero'], 'zero'),                #56 -> zero, zero
            right_wheel_spin_rule_maker.make(['positive', 'positive_strong', 'positive'], 'negative_strong'),        #57 -> positive, negative
            

            ###
            right_wheel_spin_rule_maker.make(['positive_strong', 'negative_strong', 'negative'], 'positive_strong'), #58 -> negative, positive
            right_wheel_spin_rule_maker.make(['positive_strong', 'negative_strong', 'zero'], 'zero'),         #59 -> zero, zero
            right_wheel_spin_rule_maker.make(['positive_strong', 'negative_strong', 'positive'], 'negative_strong'), #60 -> positive, negative
            
            right_wheel_spin_rule_maker.make(['positive_strong', 'negative', 'negative'], 'positive_strong'),        #61 -> negative, positive
            right_wheel_spin_rule_maker.make(['positive_strong', 'negative', 'zero'], 'zero'),                #62 -> zero, zero
            right_wheel_spin_rule_maker.make(['positive_strong', 'negative', 'positive'], 'negative_strong'),        #63 -> positive, negative
            
            right_wheel_spin_rule_maker.make(['positive_strong', 'zero', 'negative'], 'positive_strong'),            #64 -> negative, positive
            right_wheel_spin_rule_maker.make(['positive_strong', 'zero', 'zero'], 'zero'),                    #65 -> zero, zero
            right_wheel_spin_rule_maker.make(['positive_strong', 'zero', 'positive'], 'negative_strong'),            #66 -> positive, negative
            
            right_wheel_spin_rule_maker.make(['positive_strong', 'positive', 'negative'], 'positive_strong'),        #67 -> negative, positive
            right_wheel_spin_rule_maker.make(['positive_strong', 'positive', 'zero'], 'zero'),                #68 -> zero, zero
            right_wheel_spin_rule_maker.make(['positive_strong', 'positive', 'positive'], 'negative_strong'),        #69 -> positive, negative
            
            right_wheel_spin_rule_maker.make(['positive_strong', 'positive_strong', 'negative'], 'positive_strong'), #70 -> negative, positive
            right_wheel_spin_rule_maker.make(['positive_strong', 'positive_strong', 'zero'], 'zero'),         #71 -> zero, zero
            right_wheel_spin_rule_maker.make(['positive_strong', 'positive_strong', 'positive'], 'negative_strong') #72 -> positive, negative
            ]
            
        self.__left_wheel_fis = FuzzySystem(left_wheel_rules, self.__variable['left_wheel'], 'left')
        self.__right_wheel_fis = FuzzySystem(right_wheel_rules, self.__variable['right_wheel'], 'right')
        self.__left_correction_fis = FuzzySystem(left_wheel_spin_rules, self.__variable['left_correction'], 'left_correction')
        self.__right_correction_fis = FuzzySystem(right_wheel_spin_rules, self.__variable['right_correction'], 'right_correction')

    def play(self):
        """
        Play using fuzzy controller
        """
        i = 0
        fuzzy_left_action = self.__left_wheel_fis
        fuzzy_right_action = self.__right_wheel_fis
        fuzzy_left_correction = self.__left_correction_fis
        fuzzy_right_correction = self.__right_correction_fis
        
        variable = self.__variable
        match = self.__match
        while(True):
            # Gets updated environment values
            variable['ball_angle'].value = match.get_ball_angle()
            variable['target_angle'].value = match.get_target_angle()
            variable['ball_distance'].value = match.get_ball_distance()
            variable['spin'].value = match.get_spin()

            # Updates fuzzy outputs
            fuzzy_left_action.update()
            fuzzy_right_action.update()
            fuzzy_left_correction.update()
            fuzzy_right_correction.update()

            # Calculate final forces for each wheel
            left_wheel = variable['left_wheel'].value + variable['left_correction'].value
            right_wheel = variable['right_wheel'].value + variable['right_correction'].value

            # Debug information
            for pname, part in variable['ball_distance'].partitions.items():
                print(pname, part.membership())
            print(variable['spin'].value)
            print('output:', left_wheel, right_wheel)

            # Act
            match.act(left_wheel, right_wheel)
            i += 1
            input('')

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

    
