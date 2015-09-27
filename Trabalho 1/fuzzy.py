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
##RIGHT = (-PI, -PI, -PI/2, 0)
##FRONT = (-PI/2, 0, 0, PI/2)
##LEFT = (0, PI/2, PI, PI)

NEG_ST = (-32, -32, -32, -16)
NEG = (-32, -16, -8, -4)
NEG_WK = (-8, -4, -2, -0)
ZER = (-2, -0, 0, 2)
POS_WK = (0, 2, 4, 8)
POS = (4, 8, 16, 32)
POS_ST = (16, 32, 32, 32)

CLOSE = (0, 0, 80, 120)
NEAR = (80, 120, 750, 1500)
FAR = (750, 1500, 2000, 2000)

CLOCKWISE = (-4, -4, -0.1, 0)
SPIN_ZERO = (-0.1, 0, 0, 0.1)
ANTICLOCKWISE = (0, 0.1, 4, 4)

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
            'ball_distance': Variable({'close': CLOSE, 'near': NEAR, 'far': FAR}, 'ball_distance'),
            
            'left_wheel': Variable({'negative_strong': NEG_ST, 'negative': NEG, 'negative_weak': NEG_WK, 'zero': ZER, 'positive_weak': POS_WK, 'positive': POS, 'positive_strong': POS_ST}, 'left_wheel'),
            'right_wheel': Variable({'negative_strong': NEG_ST, 'negative': NEG, 'negative_weak': NEG_WK, 'zero': ZER, 'positive_weak': POS_WK, 'positive': POS, 'positive_strong': POS_ST}, 'right_wheel'),

            'left_correction': Variable({'negative_strong': NEG_ST, 'negative': NEG, 'negative_weak': NEG_WK, 'zero': ZER, 'positive_weak': POS_WK, 'positive': POS, 'positive_strong': POS_ST}, 'left_correction'),
            'right_correction': Variable({'negative_strong': NEG_ST, 'negative': NEG, 'negative_weak': NEG_WK, 'zero': ZER, 'positive_weak': POS_WK, 'positive': POS, 'positive_strong': POS_ST}, 'right_correction'),

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
            left_wheel_rule_maker.make(['rear_right', 'rear_right', 'far'], 'zero'),             #1 -> negative, negative
            left_wheel_rule_maker.make(['rear_right', 'right', 'far'], 'zero'),                  #2 -> negative, negative
            left_wheel_rule_maker.make(['rear_right', 'front', 'far'], 'zero'),         #3 -> negative, negative
            left_wheel_rule_maker.make(['rear_right', 'left', 'far'], 'zero'),        #4 -> negative, negative
            left_wheel_rule_maker.make(['rear_right', 'rear_left', 'far'], 'zero'),   #5 -> negative, negative

            left_wheel_rule_maker.make(['right', 'rear_right', 'far'], 'zero'),       #6 -> positive_strong - positive_weak
            left_wheel_rule_maker.make(['right', 'right', 'far'], 'zero'),                   #7 -> positive - negative
            left_wheel_rule_maker.make(['right', 'front', 'far'], 'negative_weak'),            ##8 -> negative_weak, negative
            left_wheel_rule_maker.make(['right', 'left', 'far'], 'zero'),             #9 -> positive strong - positive_weak
            left_wheel_rule_maker.make(['right', 'rear_left', 'far'], 'zero'),        #10 -> positive strong - positive_weak
            
            left_wheel_rule_maker.make(['front', 'rear_right', 'far'], 'zero'),              #11 -> positive - positive_strong
            left_wheel_rule_maker.make(['front', 'right', 'far'], 'positive_weak'),                   ##12 -> positive_weak, positive
            left_wheel_rule_maker.make(['front', 'front', 'far'], 'positive'),            ##13 -> positive, positive
            left_wheel_rule_maker.make(['front', 'left', 'far'], 'zero'),             #14 -> positive_strong - positive
            left_wheel_rule_maker.make(['front', 'rear_left', 'far'], 'zero'),        #15 -> positive_strong - positive
            
            left_wheel_rule_maker.make(['left', 'rear_right', 'far'], 'zero'),          #16 -> positive_weak - positive_strong
            left_wheel_rule_maker.make(['left', 'right', 'far'], 'zero'),               #17 -> positive_weak - positive_strong
            left_wheel_rule_maker.make(['left', 'front', 'far'], 'zero'),             #18 -> negative_strong - negative_weak
            left_wheel_rule_maker.make(['left', 'left', 'far'], 'zero'),                #19 -> negative_weak - positive_strong
            left_wheel_rule_maker.make(['left', 'rear_left', 'far'], 'zero'),           #20 -> positive_weak - positive_strong
            
            left_wheel_rule_maker.make(['rear_left', 'rear_right', 'far'], 'zero'),              #21 -> zero, positive_strong
            left_wheel_rule_maker.make(['rear_left', 'right', 'far'], 'zero'),                   #22 -> zero, positive_strong
            left_wheel_rule_maker.make(['rear_left', 'front', 'far'], 'zero'),        #23 -> positive_strong, positive
            left_wheel_rule_maker.make(['rear_left', 'left', 'far'], 'zero'),           #24 -> positive_weak, positive_strong
            left_wheel_rule_maker.make(['rear_left', 'rear_left', 'far'], 'zero'),    #25 -> positive_strong, zero

            ###
            left_wheel_rule_maker.make(['rear_right', 'rear_right', 'near'], 'negative_weak'),            ##26 -> negative_weak, negative
            left_wheel_rule_maker.make(['rear_right', 'right', 'near'], 'negative_weak'),                 ##27 -> negative_weak, negative
            left_wheel_rule_maker.make(['rear_right', 'front', 'near'], 'zero'),        #28 -> negative_weak - positive_strong
            left_wheel_rule_maker.make(['rear_right', 'left', 'near'], 'negative'),       ##29 -> negative, negative_weak
            left_wheel_rule_maker.make(['rear_right', 'rear_left', 'near'], 'positive'),  ##30 -> positive, positive_weak

            left_wheel_rule_maker.make(['right', 'rear_right', 'near'], 'positive'),      ##31 -> positive, positive_weak
            left_wheel_rule_maker.make(['right', 'right', 'near'], 'positive'),                  ##32 -> positive, zero
            left_wheel_rule_maker.make(['right', 'front', 'near'], 'negative_weak'),             ##33 -> negative_weak, negative
            left_wheel_rule_maker.make(['right', 'left', 'near'], 'positive'),            ##34 -> positive, positive_weak
            left_wheel_rule_maker.make(['right', 'rear_left', 'near'], 'positive'),       ##35 -> positive, positive_weak
            
            left_wheel_rule_maker.make(['front', 'rear_right', 'near'], 'zero'),        #36 -> positive_weak - positive_strong
            left_wheel_rule_maker.make(['front', 'right', 'near'], 'positive_weak'),             ##37 -> positive_weak, positive
            left_wheel_rule_maker.make(['front', 'front', 'near'], 'positive'),           ##38 -> positive, positive
            left_wheel_rule_maker.make(['front', 'left', 'near'], 'positive'),            ##39 -> positive, positive_weak
            left_wheel_rule_maker.make(['front', 'rear_left', 'near'], 'zero'),       #40 -> positive_strong - positive_weak
            
            left_wheel_rule_maker.make(['left', 'rear_right', 'near'], 'zero'),         ##41 -> zero, positive
            left_wheel_rule_maker.make(['left', 'right', 'near'], 'positive_weak'),              ##42 -> positive_weak, positive
            left_wheel_rule_maker.make(['left', 'front', 'near'], 'negative'),            ##43 -> negative, negative_weak
            left_wheel_rule_maker.make(['left', 'left', 'near'], 'zero'),               ##44 -> zero, positive
            left_wheel_rule_maker.make(['left', 'rear_left', 'near'], 'positive_weak'),          ##45 -> positive_weak, positive
            
            left_wheel_rule_maker.make(['rear_left', 'rear_right', 'near'], 'positive_weak'),             ##46 -> positive_weak, positive
            left_wheel_rule_maker.make(['rear_left', 'right', 'near'], 'negative'),                  ##47 -> negative, positive
            left_wheel_rule_maker.make(['rear_left', 'front', 'near'], 'zero'),         #48 -> negative_weak, positive_strong
            left_wheel_rule_maker.make(['rear_left', 'left', 'near'], 'negative'),          ##49 -> negative, negative_weak
            left_wheel_rule_maker.make(['rear_left', 'rear_left', 'near'], 'positive_weak'),   ##50 -> positive_weak, positive

            ###
            left_wheel_rule_maker.make(['rear_right', 'rear_right', 'close'], 'zero'),           #51 -> zero, positive_weak
            left_wheel_rule_maker.make(['rear_right', 'right', 'close'], 'zero'),                #52 -> zero, positive_weak
            left_wheel_rule_maker.make(['rear_right', 'front', 'close'], 'zero'),                #53 -> zero, positive_weak
            left_wheel_rule_maker.make(['rear_right', 'left', 'close'], 'zero'),        #54 -> positive_weak, zero
            left_wheel_rule_maker.make(['rear_right', 'rear_left', 'close'], 'zero'),   #55 -> positive_weak, zero

            left_wheel_rule_maker.make(['right', 'rear_right', 'close'], 'positive_weak'),                ##56 -> positive_weak, zero
            left_wheel_rule_maker.make(['right', 'right', 'close'], 'zero'),                     ##57 -> zero, negative_weak
            left_wheel_rule_maker.make(['right', 'front', 'close'], 'zero'),                     ##58 -> zero, negative_weak
            left_wheel_rule_maker.make(['right', 'left', 'close'], 'zero'),                      ##59 -> zero, negative_weak
            left_wheel_rule_maker.make(['right', 'rear_left', 'close'], 'positive_weak'),        ##60 -> positive_weak, zero
            
            left_wheel_rule_maker.make(['front', 'rear_right', 'close'], 'zero'),       #61 -> positive_weak, zero
            left_wheel_rule_maker.make(['front', 'right', 'close'], 'positive_weak'),            ##62 -> positive_weak, zero
            left_wheel_rule_maker.make(['front', 'front', 'close'], 'positive'),                 ##63 -> positive, positive
            left_wheel_rule_maker.make(['front', 'left', 'close'], 'zero'),                      ##64 -> zero, positive_weak
            left_wheel_rule_maker.make(['front', 'rear_left', 'close'], 'positive'),                 ##65 -> positive, zero
            
            left_wheel_rule_maker.make(['left', 'rear_right', 'close'], 'zero'),                 ##66 -> zero, positive
            left_wheel_rule_maker.make(['left', 'right', 'close'], 'positive'),             ##67 -> positive, positive_weak
            left_wheel_rule_maker.make(['left', 'front', 'close'], 'negative_weak'),             ##68 -> negative_weak, zero
            left_wheel_rule_maker.make(['left', 'left', 'close'], 'negative_weak'),              ##69 -> negative_weak, zero
            left_wheel_rule_maker.make(['left', 'rear_left', 'close'], 'zero'),         ##70 -> zero, positive
            
            left_wheel_rule_maker.make(['rear_left', 'rear_right', 'close'], 'zero'),            #71 -> zero, positive_weak
            left_wheel_rule_maker.make(['rear_left', 'right', 'close'], 'zero'),                 ##72 -> zero, positive
            left_wheel_rule_maker.make(['rear_left', 'front', 'close'], 'zero'),        #73 -> positive_weak, zero
            left_wheel_rule_maker.make(['rear_left', 'left', 'close'], 'zero'),         #74 -> positive_weak, zero
            left_wheel_rule_maker.make(['rear_left', 'rear_left', 'close'], 'zero'),    #75 -> positive_weak, zero
            ]

        right_wheel_rules = [
            right_wheel_rule_maker.make(['rear_right', 'rear_right', 'far'], 'zero'),             #1 ->  -> negative, negative
            right_wheel_rule_maker.make(['rear_right', 'right', 'far'], 'zero'),                  #2 -> negative, negative
            right_wheel_rule_maker.make(['rear_right', 'front', 'far'], 'zero'),         #3 -> negative, negative
            right_wheel_rule_maker.make(['rear_right', 'left', 'far'], 'zero'),        #4 -> negative, negative
            right_wheel_rule_maker.make(['rear_right', 'rear_left', 'far'], 'zero'),   #5 -> negative, negative

            right_wheel_rule_maker.make(['right', 'rear_right', 'far'], 'zero'),       #6 -> positive_strong - positive_weak
            right_wheel_rule_maker.make(['right', 'right', 'far'], 'zero'),                   #7 -> positive - negative
            right_wheel_rule_maker.make(['right', 'front', 'far'], 'negative'),            ##8 -> negative_weak, negative
            right_wheel_rule_maker.make(['right', 'left', 'far'], 'zero'),             #9 -> positive strong - positive_weak
            right_wheel_rule_maker.make(['right', 'rear_left', 'far'], 'zero'),        #10 -> positive strong - positive_weak
            
            right_wheel_rule_maker.make(['front', 'rear_right', 'far'], 'zero'),              #11 -> positive - positive_strong
            right_wheel_rule_maker.make(['front', 'right', 'far'], 'positive'),                   ##12 -> positive_weak, positive
            right_wheel_rule_maker.make(['front', 'front', 'far'], 'positive'),            ##13 -> positive, positive
            right_wheel_rule_maker.make(['front', 'left', 'far'], 'zero'),             #14 -> positive_strong - positive
            right_wheel_rule_maker.make(['front', 'rear_left', 'far'], 'zero'),        #15 -> positive_strong - positive
            
            right_wheel_rule_maker.make(['left', 'rear_right', 'far'], 'zero'),          #16 -> positive_weak - positive_strong
            right_wheel_rule_maker.make(['left', 'right', 'far'], 'zero'),               #17 -> positive_weak - positive_strong
            right_wheel_rule_maker.make(['left', 'front', 'far'], 'zero'),             #18 -> negative_strong - negative_weak
            right_wheel_rule_maker.make(['left', 'left', 'far'], 'zero'),                #19 -> negative_weak - positive_strong
            right_wheel_rule_maker.make(['left', 'rear_left', 'far'], 'zero'),           #20 -> positive_weak - positive_strong
            
            right_wheel_rule_maker.make(['rear_left', 'rear_right', 'far'], 'zero'),              #21 -> zero, positive_strong
            right_wheel_rule_maker.make(['rear_left', 'right', 'far'], 'zero'),                   #22 -> zero, positive_strong
            right_wheel_rule_maker.make(['rear_left', 'front', 'far'], 'zero'),        #23 -> positive_strong, positive
            right_wheel_rule_maker.make(['rear_left', 'left', 'far'], 'zero'),           #24 -> positive_weak, positive_strong
            right_wheel_rule_maker.make(['rear_left', 'rear_left', 'far'], 'zero'),    #25 -> positive_strong, zero

            ###
            right_wheel_rule_maker.make(['rear_right', 'rear_right', 'near'], 'negative'),            ##26 -> negative_weak, negative
            right_wheel_rule_maker.make(['rear_right', 'right', 'near'], 'negative'),                 ##27 -> negative_weak, negative
            right_wheel_rule_maker.make(['rear_right', 'front', 'near'], 'zero'),        #28 -> negative_weak - positive_strong
            right_wheel_rule_maker.make(['rear_right', 'left', 'near'], 'negative_weak'),       ##29 -> negative, negative_weak
            right_wheel_rule_maker.make(['rear_right', 'rear_left', 'near'], 'positive_weak'),  ##30 -> positive, positive_weak

            right_wheel_rule_maker.make(['right', 'rear_right', 'near'], 'positive_weak'),      ##31 -> positive, positive_weak
            right_wheel_rule_maker.make(['right', 'right', 'near'], 'zero'),                  ##32 -> positive, zero
            right_wheel_rule_maker.make(['right', 'front', 'near'], 'negative'),             ##33 -> negative_weak, negative
            right_wheel_rule_maker.make(['right', 'left', 'near'], 'positive_weak'),            ##34 -> positive, positive_weak
            right_wheel_rule_maker.make(['right', 'rear_left', 'near'], 'positive_weak'),       ##35 -> positive, positive_weak
            
            right_wheel_rule_maker.make(['front', 'rear_right', 'near'], 'zero'),        #36 -> positive_weak - positive_strong
            right_wheel_rule_maker.make(['front', 'right', 'near'], 'positive'),             ##37 -> positive_weak, positive
            right_wheel_rule_maker.make(['front', 'front', 'near'], 'positive'),           ##38 -> positive, positive
            right_wheel_rule_maker.make(['front', 'left', 'near'], 'positive_weak'),            ##39 -> positive, positive_weak
            right_wheel_rule_maker.make(['front', 'rear_left', 'near'], 'zero'),       #40 -> positive_strong - positive_weak
            
            right_wheel_rule_maker.make(['left', 'rear_right', 'near'], 'positive'),         ##41 -> zero, positive
            right_wheel_rule_maker.make(['left', 'right', 'near'], 'positive'),              ##42 -> positive_weak, positive
            right_wheel_rule_maker.make(['left', 'front', 'near'], 'negative_weak'),            ##43 -> negative, negative_weak
            right_wheel_rule_maker.make(['left', 'left', 'near'], 'positive'),               ##44 -> zero, positive
            right_wheel_rule_maker.make(['left', 'rear_left', 'near'], 'positive'),          ##45 -> positive_weak, positive
            
            right_wheel_rule_maker.make(['rear_left', 'rear_right', 'near'], 'positive'),             ##46 -> positive_weak, positive
            right_wheel_rule_maker.make(['rear_left', 'right', 'near'], 'positive'),                  ##47 -> zero, positive
            right_wheel_rule_maker.make(['rear_left', 'front', 'near'], 'zero'),         #48 -> negative_weak, positive_strong
            right_wheel_rule_maker.make(['rear_left', 'left', 'near'], 'negative_weak'),          ##49 -> negative, negative_weak
            right_wheel_rule_maker.make(['rear_left', 'rear_left', 'near'], 'positive'),   ##50 -> positive_weak, positive

            ###
            right_wheel_rule_maker.make(['rear_right', 'rear_right', 'close'], 'zero'),           #51 -> zero, positive_weak
            right_wheel_rule_maker.make(['rear_right', 'right', 'close'], 'zero'),                #52 -> zero, positive_weak
            right_wheel_rule_maker.make(['rear_right', 'front', 'close'], 'zero'),                #53 -> zero, positive_weak
            right_wheel_rule_maker.make(['rear_right', 'left', 'close'], 'zero'),        #54 -> positive_weak, zero
            right_wheel_rule_maker.make(['rear_right', 'rear_left', 'close'], 'zero'),   #55 -> positive_weak, zero

            right_wheel_rule_maker.make(['right', 'rear_right', 'close'], 'zero'),       ##56 -> positive_weak, zero
            right_wheel_rule_maker.make(['right', 'right', 'close'], 'negative_weak'),            ##57 -> zero, negative_weak
            right_wheel_rule_maker.make(['right', 'front', 'close'], 'negative_weak'),            ##58 -> zero, negative_weak
            right_wheel_rule_maker.make(['right', 'left', 'close'], 'negative_weak'),             ##59 -> zero, negative_weak
            right_wheel_rule_maker.make(['right', 'rear_left', 'close'], 'zero'),             ##60 -> positive_weak, zero
            
            right_wheel_rule_maker.make(['front', 'rear_right', 'close'], 'zero'),       #61 -> positive_weak, zero
            right_wheel_rule_maker.make(['front', 'right', 'close'], 'zero'),            ##62 -> positive_weak, zero
            right_wheel_rule_maker.make(['front', 'front', 'close'], 'positive'),                 ##63 -> positive, positive
            right_wheel_rule_maker.make(['front', 'left', 'close'], 'positive_weak'),                      ##64 -> zero, positive_weak
            right_wheel_rule_maker.make(['front', 'rear_left', 'close'], 'zero'),                 ##65 -> positive, zero
            
            right_wheel_rule_maker.make(['left', 'rear_right', 'close'], 'positive'),                 ##66 -> zero, positive
            right_wheel_rule_maker.make(['left', 'right', 'close'], 'positive_weak'),             ##67 -> positive, positive_weak
            right_wheel_rule_maker.make(['left', 'front', 'close'], 'zero'),             ##68 -> negative_weak, zero
            right_wheel_rule_maker.make(['left', 'left', 'close'], 'zero'),              ##69 -> negative_weak, zero
            right_wheel_rule_maker.make(['left', 'rear_left', 'close'], 'positive'),         ##70 -> zero, positive
            
            right_wheel_rule_maker.make(['rear_left', 'rear_right', 'close'], 'zero'),            #71 -> zero, positive_weak
            right_wheel_rule_maker.make(['rear_left', 'right', 'close'], 'positive'),                 ##72 -> zero, positive
            right_wheel_rule_maker.make(['rear_left', 'front', 'close'], 'zero'),        #73 -> positive_weak, zero
            right_wheel_rule_maker.make(['rear_left', 'left', 'close'], 'zero'),         #74 -> positive_weak, zero
            right_wheel_rule_maker.make(['rear_left', 'rear_left', 'close'], 'zero'),    #75 -> positive_weak, zero ###
            ]

        left_wheel_spin_rules = [
            left_wheel_spin_rule_maker.make(['negative_strong', 'negative_strong', 'negative'], 'negative_strong'), #1 -> negative, positive
            left_wheel_spin_rule_maker.make(['negative_strong', 'negative_strong', 'zero'], 'zero'),                #2 -> zero, zero
            left_wheel_spin_rule_maker.make(['negative_strong', 'negative_strong', 'positive'], 'positive_strong'), #3 -> positive, negative

            left_wheel_spin_rule_maker.make(['negative_strong', 'negative', 'negative'], 'negative_strong'),        #4 -> negative, positive
            left_wheel_spin_rule_maker.make(['negative_strong', 'negative', 'zero'], 'zero'),                       #5 -> zero, zero
            left_wheel_spin_rule_maker.make(['negative_strong', 'negative', 'positive'], 'zero'),                   #6 -> zero, zero

            left_wheel_spin_rule_maker.make(['negative_strong', 'zero', 'negative'], 'negative_strong'),            #7 -> negative, positive
            left_wheel_spin_rule_maker.make(['negative_strong', 'zero', 'zero'], 'zero'),                           #8 -> zero, zero
            left_wheel_spin_rule_maker.make(['negative_strong', 'zero', 'positive'], 'zero'),                       #9 -> zero, zero
            
            left_wheel_spin_rule_maker.make(['negative_strong', 'positive', 'negative'], 'negative_strong'),        #10 -> negative, positive
            left_wheel_spin_rule_maker.make(['negative_strong', 'positive', 'zero'], 'zero'),                       #11 -> zero, zero
            left_wheel_spin_rule_maker.make(['negative_strong', 'positive', 'positive'], 'zero'),                   #12 -> zero, zero
            
            left_wheel_spin_rule_maker.make(['negative_strong', 'positive_strong', 'negative'], 'negative_strong'), #13 -> negative, positive
            left_wheel_spin_rule_maker.make(['negative_strong', 'positive_strong', 'zero'], 'zero'),                #14 -> zero, zero
            left_wheel_spin_rule_maker.make(['negative_strong', 'positive_strong', 'positive'], 'zero'),            #15 -> zero, zero

            ###
            left_wheel_spin_rule_maker.make(['negative', 'negative_strong', 'negative'], 'zero'),                   #16 -> zero, zero
            left_wheel_spin_rule_maker.make(['negative', 'negative_strong', 'zero'], 'zero'),                       #17 -> zero, zero
            left_wheel_spin_rule_maker.make(['negative', 'negative_strong', 'positive'], 'positive_strong'),        #18 -> positive, negative
            
            left_wheel_spin_rule_maker.make(['negative', 'negative', 'negative'], 'negative_strong'),               #19 -> negative, positive
            left_wheel_spin_rule_maker.make(['negative', 'negative', 'zero'], 'zero'),                              #20 -> zero, zero
            left_wheel_spin_rule_maker.make(['negative', 'negative', 'positive'], 'positive_strong'),               #21 -> positive, negative
            
            left_wheel_spin_rule_maker.make(['negative', 'zero', 'negative'], 'negative_strong'),                   #22 -> negative, positive
            left_wheel_spin_rule_maker.make(['negative', 'zero', 'zero'], 'zero'),                                  #23 -> zero, zero
            left_wheel_spin_rule_maker.make(['negative', 'zero', 'positive'], 'zero'),                              #24 -> zero, zero
            
            left_wheel_spin_rule_maker.make(['negative', 'positive', 'negative'], 'negative_strong'),               #25 -> negative, positive
            left_wheel_spin_rule_maker.make(['negative', 'positive', 'zero'], 'zero'),                              #26 -> zero, zero
            left_wheel_spin_rule_maker.make(['negative', 'positive', 'positive'], 'zero'),                          #27 -> zero, zero
            
            left_wheel_spin_rule_maker.make(['negative', 'positive_strong', 'negative'], 'negative_strong'),        #28 -> negative, positive
            left_wheel_spin_rule_maker.make(['negative', 'positive_strong', 'zero'], 'zero'),                       #29 -> zero, zero
            left_wheel_spin_rule_maker.make(['negative', 'positive_strong', 'positive'], 'zero'),                   #30 -> zero, zero

            ###
            left_wheel_spin_rule_maker.make(['zero', 'negative_strong', 'negative'], 'zero'),                       #31 -> zero, zero
            left_wheel_spin_rule_maker.make(['zero', 'negative_strong', 'zero'], 'zero'),                           #32 -> zero, zero
            left_wheel_spin_rule_maker.make(['zero', 'negative_strong', 'positive'], 'positive_strong'),            #33 -> positive, negative
            
            left_wheel_spin_rule_maker.make(['zero', 'negative', 'negative'], 'zero'),                              #34 -> zero, zero
            left_wheel_spin_rule_maker.make(['zero', 'negative', 'zero'], 'zero'),                                  #35 -> zero, zero
            left_wheel_spin_rule_maker.make(['zero', 'negative', 'positive'], 'positive_strong'),                   #36 -> positive, negative
            
            left_wheel_spin_rule_maker.make(['zero', 'zero', 'negative'], 'negative_strong'),                       #37 -> negative, positive
            left_wheel_spin_rule_maker.make(['zero', 'zero', 'zero'], 'zero'),                                      #38 -> zero, zero
            left_wheel_spin_rule_maker.make(['zero', 'zero', 'positive'], 'positive_strong'),                       #39 -> positive, negative
            
            left_wheel_spin_rule_maker.make(['zero', 'positive', 'negative'], 'negative_strong'),                   #40 -> negative, positive
            left_wheel_spin_rule_maker.make(['zero', 'positive', 'zero'], 'zero'),                                  #41 -> zero, zero
            left_wheel_spin_rule_maker.make(['zero', 'positive', 'positive'], 'zero'),                              #42 -> zero, zero
            
            left_wheel_spin_rule_maker.make(['zero', 'positive_strong', 'negative'], 'negative_strong'),            #43 -> negative, positive
            left_wheel_spin_rule_maker.make(['zero', 'positive_strong', 'zero'], 'zero'),                           #44 -> zero, zero
            left_wheel_spin_rule_maker.make(['zero', 'positive_strong', 'positive'], 'zero'),                       #45 -> zero, zero

            ###
            left_wheel_spin_rule_maker.make(['positive', 'negative_strong', 'negative'], 'zero'),                   #46 -> zero, zero
            left_wheel_spin_rule_maker.make(['positive', 'negative_strong', 'zero'], 'zero'),                       #47 -> zero, zero
            left_wheel_spin_rule_maker.make(['positive', 'negative_strong', 'positive'], 'positive_strong'),        #48 -> positive, negative
            
            left_wheel_spin_rule_maker.make(['positive', 'negative', 'negative'], 'zero'),                          #46 -> zero, zero
            left_wheel_spin_rule_maker.make(['positive', 'negative', 'zero'], 'zero'),                              #47 -> zero, zero
            left_wheel_spin_rule_maker.make(['positive', 'negative', 'positive'], 'positive_strong'),               #48 -> positive, negative
            
            left_wheel_spin_rule_maker.make(['positive', 'zero', 'negative'], 'zero'),                              #49 -> zero, zero
            left_wheel_spin_rule_maker.make(['positive', 'zero', 'zero'], 'zero'),                                  #50 -> zero, zero
            left_wheel_spin_rule_maker.make(['positive', 'zero', 'positive'], 'positive_strong'),                   #51 -> positive, negative
            
            left_wheel_spin_rule_maker.make(['positive', 'positive', 'negative'], 'negative_strong'),               #52 -> negative, positive
            left_wheel_spin_rule_maker.make(['positive', 'positive', 'zero'], 'zero'),                              #53 -> zero, zero
            left_wheel_spin_rule_maker.make(['positive', 'positive', 'positive'], 'positive_strong'),               #54 -> positive, negative
            
            left_wheel_spin_rule_maker.make(['positive', 'positive_strong', 'negative'], 'negative_strong'),        #55 -> negative, positive
            left_wheel_spin_rule_maker.make(['positive', 'positive_strong', 'zero'], 'zero'),                       #56 -> zero, zero
            left_wheel_spin_rule_maker.make(['positive', 'positive_strong', 'positive'], 'zero'),                   #57 -> zero, zero
            

            ###
            left_wheel_spin_rule_maker.make(['positive_strong', 'negative_strong', 'negative'], 'zero'),            #58 -> zero, zero
            left_wheel_spin_rule_maker.make(['positive_strong', 'negative_strong', 'zero'], 'zero'),                #59 -> zero, zero
            left_wheel_spin_rule_maker.make(['positive_strong', 'negative_strong', 'positive'], 'positive_strong'), #60 -> positive, negative
            
            left_wheel_spin_rule_maker.make(['positive_strong', 'negative', 'negative'], 'zero'),                   #61 -> zero, zero
            left_wheel_spin_rule_maker.make(['positive_strong', 'negative', 'zero'], 'zero'),                       #62 -> zero, zero
            left_wheel_spin_rule_maker.make(['positive_strong', 'negative', 'positive'], 'positive_strong'),        #63 -> positive, negative
            
            left_wheel_spin_rule_maker.make(['positive_strong', 'zero', 'negative'], 'zero'),                       #64 -> zero, zero
            left_wheel_spin_rule_maker.make(['positive_strong', 'zero', 'zero'], 'zero'),                           #65 -> zero, zero
            left_wheel_spin_rule_maker.make(['positive_strong', 'zero', 'positive'], 'positive_strong'),            #66 -> positive, negative
            
            left_wheel_spin_rule_maker.make(['positive_strong', 'positive', 'negative'], 'zero'),                   #67 -> zero, zero
            left_wheel_spin_rule_maker.make(['positive_strong', 'positive', 'zero'], 'zero'),                       #68 -> zero, zero
            left_wheel_spin_rule_maker.make(['positive_strong', 'positive', 'positive'], 'positive_strong'),        #69 -> positive, negative
            
            left_wheel_spin_rule_maker.make(['positive_strong', 'positive_strong', 'negative'], 'negative_strong'), #70 -> negative, positive
            left_wheel_spin_rule_maker.make(['positive_strong', 'positive_strong', 'zero'], 'zero'),                #71 -> zero, zero
            left_wheel_spin_rule_maker.make(['positive_strong', 'positive_strong', 'positive'], 'positive_strong')  #72 -> positive, negative
            ]

        right_wheel_spin_rules = [
            right_wheel_spin_rule_maker.make(['negative_strong', 'negative_strong', 'negative'], 'positive_strong'), #1 -> negative, positive
            right_wheel_spin_rule_maker.make(['negative_strong', 'negative_strong', 'zero'], 'zero'),                #2 -> zero, zero
            right_wheel_spin_rule_maker.make(['negative_strong', 'negative_strong', 'positive'], 'negative_strong'), #3 -> positive, negative

            right_wheel_spin_rule_maker.make(['negative_strong', 'negative', 'negative'], 'positive_strong'),        #4 -> negative, positive
            right_wheel_spin_rule_maker.make(['negative_strong', 'negative', 'zero'], 'zero'),                       #5 -> zero, zero
            right_wheel_spin_rule_maker.make(['negative_strong', 'negative', 'positive'], 'zero'),                   #6 -> zero, zero

            right_wheel_spin_rule_maker.make(['negative_strong', 'zero', 'negative'], 'positive_strong'),            #7 -> negative, positive
            right_wheel_spin_rule_maker.make(['negative_strong', 'zero', 'zero'], 'zero'),                           #8 -> zero, zero
            right_wheel_spin_rule_maker.make(['negative_strong', 'zero', 'positive'], 'zero'),                       #9 -> zero, zero
            
            right_wheel_spin_rule_maker.make(['negative_strong', 'positive', 'negative'], 'positive_strong'),        #10 -> negative, positive
            right_wheel_spin_rule_maker.make(['negative_strong', 'positive', 'zero'], 'zero'),                       #11 -> zero, zero
            right_wheel_spin_rule_maker.make(['negative_strong', 'positive', 'positive'], 'zero'),                   #12 -> zero, zero
            
            right_wheel_spin_rule_maker.make(['negative_strong', 'positive_strong', 'negative'], 'positive_strong'), #13 -> negative, positive
            right_wheel_spin_rule_maker.make(['negative_strong', 'positive_strong', 'zero'], 'zero'),                #14 -> zero, zero
            right_wheel_spin_rule_maker.make(['negative_strong', 'positive_strong', 'positive'], 'zero'),            #15 -> zero, zero

            ###
            right_wheel_spin_rule_maker.make(['negative', 'negative_strong', 'negative'], 'zero'),                   #16 -> zero, zero
            right_wheel_spin_rule_maker.make(['negative', 'negative_strong', 'zero'], 'zero'),                       #17 -> zero, zero
            right_wheel_spin_rule_maker.make(['negative', 'negative_strong', 'positive'], 'negative_strong'),        #18 -> positive, negative
            
            right_wheel_spin_rule_maker.make(['negative', 'negative', 'negative'], 'positive_strong'),               #19 -> negative, positive
            right_wheel_spin_rule_maker.make(['negative', 'negative', 'zero'], 'zero'),                              #20 -> zero, zero
            right_wheel_spin_rule_maker.make(['negative', 'negative', 'positive'], 'negative_strong'),               #21 -> positive, negative
            
            right_wheel_spin_rule_maker.make(['negative', 'zero', 'negative'], 'positive_strong'),                   #22 -> negative, positive
            right_wheel_spin_rule_maker.make(['negative', 'zero', 'zero'], 'zero'),                                  #23 -> zero, zero
            right_wheel_spin_rule_maker.make(['negative', 'zero', 'positive'], 'zero'),                              #24 -> zero, zero
            
            right_wheel_spin_rule_maker.make(['negative', 'positive', 'negative'], 'positive_strong'),               #25 -> negative, positive
            right_wheel_spin_rule_maker.make(['negative', 'positive', 'zero'], 'zero'),                              #26 -> zero, zero
            right_wheel_spin_rule_maker.make(['negative', 'positive', 'positive'], 'zero'),                          #27 -> zero, zero
            
            right_wheel_spin_rule_maker.make(['negative', 'positive_strong', 'negative'], 'positive_strong'),        #28 -> negative, positive
            right_wheel_spin_rule_maker.make(['negative', 'positive_strong', 'zero'], 'zero'),                       #29 -> zero, zero
            right_wheel_spin_rule_maker.make(['negative', 'positive_strong', 'positive'], 'zero'),                   #30 -> zero, zero

            ###
            right_wheel_spin_rule_maker.make(['zero', 'negative_strong', 'negative'], 'zero'),                       #31 -> zero, zero
            right_wheel_spin_rule_maker.make(['zero', 'negative_strong', 'zero'], 'zero'),                           #32 -> zero, zero
            right_wheel_spin_rule_maker.make(['zero', 'negative_strong', 'positive'], 'negative_strong'),            #33 -> positive, negative
            
            right_wheel_spin_rule_maker.make(['zero', 'negative', 'negative'], 'zero'),                              #34 -> zero, zero
            right_wheel_spin_rule_maker.make(['zero', 'negative', 'zero'], 'zero'),                                  #35 -> zero, zero
            right_wheel_spin_rule_maker.make(['zero', 'negative', 'positive'], 'negative_strong'),                   #36 -> positive, negative
            
            right_wheel_spin_rule_maker.make(['zero', 'zero', 'negative'], 'positive_strong'),                       #37 -> negative, positive
            right_wheel_spin_rule_maker.make(['zero', 'zero', 'zero'], 'zero'),                                      #38 -> zero, zero
            right_wheel_spin_rule_maker.make(['zero', 'zero', 'positive'], 'negative_strong'),                       #39 -> positive, negative
            
            right_wheel_spin_rule_maker.make(['zero', 'positive', 'negative'], 'positive_strong'),                   #40 -> negative, positive
            right_wheel_spin_rule_maker.make(['zero', 'positive', 'zero'], 'zero'),                                  #41 -> zero, zero
            right_wheel_spin_rule_maker.make(['zero', 'positive', 'positive'], 'zero'),                              #42 -> zero, zero
            
            right_wheel_spin_rule_maker.make(['zero', 'positive_strong', 'negative'], 'positive_strong'),            #43 -> negative, positive
            right_wheel_spin_rule_maker.make(['zero', 'positive_strong', 'zero'], 'zero'),                           #44 -> zero, zero
            right_wheel_spin_rule_maker.make(['zero', 'positive_strong', 'positive'], 'zero'),                       #45 -> zero, zero

            ###
            right_wheel_spin_rule_maker.make(['positive', 'negative_strong', 'negative'], 'zero'),                   #46 -> zero, zero
            right_wheel_spin_rule_maker.make(['positive', 'negative_strong', 'zero'], 'zero'),                       #47 -> zero, zero
            right_wheel_spin_rule_maker.make(['positive', 'negative_strong', 'positive'], 'negative_strong'),        #48 -> positive, negative
            
            right_wheel_spin_rule_maker.make(['positive', 'negative', 'negative'], 'zero'),                          #46 -> zero, zero
            right_wheel_spin_rule_maker.make(['positive', 'negative', 'zero'], 'zero'),                              #47 -> zero, zero
            right_wheel_spin_rule_maker.make(['positive', 'negative', 'positive'], 'negative_strong'),               #48 -> positive, negative
            
            right_wheel_spin_rule_maker.make(['positive', 'zero', 'negative'], 'zero'),                              #49 -> zero, zero
            right_wheel_spin_rule_maker.make(['positive', 'zero', 'zero'], 'zero'),                                  #50 -> zero, zero
            right_wheel_spin_rule_maker.make(['positive', 'zero', 'positive'], 'negative_strong'),                   #51 -> positive, negative
            
            right_wheel_spin_rule_maker.make(['positive', 'positive', 'negative'], 'positive_strong'),               #52 -> negative, positive
            right_wheel_spin_rule_maker.make(['positive', 'positive', 'zero'], 'zero'),                              #53 -> zero, zero
            right_wheel_spin_rule_maker.make(['positive', 'positive', 'positive'], 'negative_strong'),               #54 -> positive, negative
            
            right_wheel_spin_rule_maker.make(['positive', 'positive_strong', 'negative'], 'positive_strong'),        #55 -> negative, positive
            right_wheel_spin_rule_maker.make(['positive', 'positive_strong', 'zero'], 'zero'),                       #56 -> zero, zero
            right_wheel_spin_rule_maker.make(['positive', 'positive_strong', 'positive'], 'zero'),                   #57 -> zero, zero
            

            ###
            right_wheel_spin_rule_maker.make(['positive_strong', 'negative_strong', 'negative'], 'zero'),      #58 -> zero, zero
            right_wheel_spin_rule_maker.make(['positive_strong', 'negative_strong', 'zero'], 'zero'),                #59 -> zero, zero
            right_wheel_spin_rule_maker.make(['positive_strong', 'negative_strong', 'positive'], 'negative_strong'), #60 -> positive, negative
            
            right_wheel_spin_rule_maker.make(['positive_strong', 'negative', 'negative'], 'zero'),                   #61 -> zero, zero
            right_wheel_spin_rule_maker.make(['positive_strong', 'negative', 'zero'], 'zero'),                       #62 -> zero, zero
            right_wheel_spin_rule_maker.make(['positive_strong', 'negative', 'positive'], 'negative_strong'),        #63 -> positive, negative
            
            right_wheel_spin_rule_maker.make(['positive_strong', 'zero', 'negative'], 'zero'),                       #64 -> zero, zero
            right_wheel_spin_rule_maker.make(['positive_strong', 'zero', 'zero'], 'zero'),                           #65 -> zero, zero
            right_wheel_spin_rule_maker.make(['positive_strong', 'zero', 'positive'], 'negative_strong'),            #66 -> positive, negative
            
            right_wheel_spin_rule_maker.make(['positive_strong', 'positive', 'negative'], 'zero'),                   #67 -> zero, zero
            right_wheel_spin_rule_maker.make(['positive_strong', 'positive', 'zero'], 'zero'),                       #68 -> zero, zero
            right_wheel_spin_rule_maker.make(['positive_strong', 'positive', 'positive'], 'negative_strong'),        #69 -> positive, negative
            
            right_wheel_spin_rule_maker.make(['positive_strong', 'positive_strong', 'negative'], 'positive_strong'), #70 -> negative, positive
            right_wheel_spin_rule_maker.make(['positive_strong', 'positive_strong', 'zero'], 'zero'),                #71 -> zero, zero
            right_wheel_spin_rule_maker.make(['positive_strong', 'positive_strong', 'positive'], 'negative_strong')  #72 -> positive, negative
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
            print('INPUTS:', '-----', sep = '\n')
            print(variable['ball_angle'])
            print(variable['target_angle'])
            print(variable['ball_distance'])
            print(variable['spin'])
            
            print('\nOUTPUTS:', '-----', sep = '\n')
            print(variable['left_wheel'])
            print(variable['left_correction'])
            print(variable['right_wheel'])
            print(variable['right_correction'])
            
            print('output:', left_wheel, right_wheel)
            print('-'*30)

            # Act
            match.act(left_wheel, right_wheel)
            i += 1
            if(abs(variable['left_wheel'].partition('zero').membership() - 1) < 1e-5 and abs(variable['right_wheel'].partition('zero').membership() - 1) < 1e-5):
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

    
