import sys
import os
sys.path.append("C:\\Users\\Alex\\Documents\\INF01017")

import math
import time
from robotsoccerplayer import Coord
from robotsoccerplayer import Robot
from robotsoccerplayer import Match

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
        self.__fuzzy = Fuzzy()

    def play(self):
        """
        Play using fuzzy controller
        """
        i = 0
        fuzzy = self.__fuzzy
        match = self.__match
        while(i < 1e4):
            fuzzy.update(match)
            action = fuzzy.get_action()
            #print(action)
            match.act(action[0], action[1])
            #print(self.match.get_spin())
            #time.sleep(1)
            i += 1

PI = math.pi
RIGHT = (-PI, -PI, -PI/2, 0)
FRONT = (-PI/2, 0, 0, PI/2)
LEFT = (0, PI/2, PI, PI)

NEG_SPIN = (-PI, -PI, -0.2, 0)
NTR_SPIN = (-0.2, 0, 0, 0.2)
POS_SPIN = (0, 0.5, PI, PI)

class Fuzzy:
    def __init__(self):
        # Initialize a dict for storing variable measures
        self.__variables = {}

        # Define partitions for each variable
        # Each variable caontains a tuple of partitions
        # being each partition itself a tuple of four parameters
        self.__partitions = {}
        self.__partitions['ball_angle'] = {'NB':RIGHT, 'ZE': FRONT, 'PB': LEFT}
        self.__partitions['target_angle'] = {'NB':RIGHT, 'ZE': FRONT, 'PB': LEFT}

        # Initialize rules matrix
        # Number of dimensions equals number of variables
        # Number of "rows" in a given dimension equals number of partitions for that variable
        # Each element represent the output partition for that specific input partitions activation
        parts = self.__partitions
        self.__rules = [[None]*len(parts['ball_angle'])]*len(parts['target_angle'])
        self.__rules = [
            [ 'NS', 'ZE', 'ZE' ],
            [ 'ZE', 'NS', 'ZE' ],
            [ 'ZE', 'ZE', 'PS' ]
            ]
        
    def update(self, match):
        """
        Update the measures to get new outputs
        """

        # Initialize inputs dictionary
        self.__variables['ball_angle'] = match.get_ball_angle()
        self.__variables['target_angle'] = match.get_target_angle()

    def get_action(self):
        

        
##        self.__memberships = [None]*NVARS
##        for i in range(0, NVARS):
##            mu = []
##            value = self.__inputs[i]
##            for params in self.__partitions[i]:
##                mu.append(self.__trapezium(value, params))
##            self.__memberships[i] = mu

##        membership = self.__memberships
##        self.__mu_ball_left = membership[BALL_ANGLE][P]
##        self.__mu_ball_front = membership[BALL_ANGLE][Z]
##        self.__mu_ball_right = membership[BALL_ANGLE][N]
##
##        self.__mu_target_left = membership[TARGET_ANGLE][P]
##        self.__mu_target_front = membership[TARGET_ANGLE][Z]
##        self.__mu_target_right = membership[TARGET_ANGLE][N]
##
##        self.__mu_spin_neg = membership[ROBOT_SPIN][N]
##        self.__mu_spin_ntr = membership[ROBOT_SPIN][Z]
##        self.__mu_spin_pos = membership[ROBOT_SPIN][P]

##        self.__mu_ball_left = membership[BALL_ANGLE][N]
##        self.__mu_ball_front = self.__trapezium(match.get_ball_angle(), FRONT)
##        self.__mu_ball_right = self.__trapezium(match.get_ball_angle(), RIGHT)
##
##        self.__mu_target_left = self.__trapezium(match.get_target_angle(), LEFT)
##        self.__mu_target_front = self.__trapezium(match.get_target_angle(), FRONT)
##        self.__mu_target_right = self.__trapezium(match.get_target_angle(), RIGHT)
##
##        self.__mu_spin_neg = self.__trapezium(match.get_spin(), NEG_SPIN)
##        self.__mu_spin_ntr = self.__trapezium(match.get_spin(), NTR_SPIN)
##        self.__mu_spin_pos = self.__trapezium(match.get_spin(), POS_SPIN)

        
        
        self.__apply_rules()
        return (self.__left_action, self.__right_action)
    
    ##alfa1(i,j)=min(Eb(i),Ea(j));
    ##alfa2(i,j)=min(Eb(i),Fa(j));
    ##alfa3(i,j)=min(Eb(i),Da(j));
    ##alfa4(i,j)=min(Fb(i),Ea(j));
    ##alfa5(i,j)=min(Fb(i),Fa(j));
    ##alfa6(i,j)=min(Fb(i),Da(j));
    ##alfa7(i,j)=min(Db(i),Ea(j));
    ##alfa8(i,j)=min(Db(i),Fa(j));
    ##alfa9(i,j)=min(Db(i),Da(j));
    def __apply_rules(self):
        alpha_left_wheel_neg = []
        alpha_left_wheel_zer = []
        alpha_left_wheel_pos = []
        
        alpha_right_wheel_neg = []
        alpha_right_wheel_zer = []
        alpha_right_wheel_pos = []
        
        # Rules for left wheel
        ## Negative spin
        ### Negative activation
        alpha_left_wheel_neg.append(min(self.__mu_spin_neg, self.__mu_ball_left, self.__mu_target_left))
        alpha_left_wheel_neg.append(min(self.__mu_spin_neg, self.__mu_ball_front, self.__mu_target_front))
        alpha_left_wheel_neg.append(min(self.__mu_spin_neg, self.__mu_ball_left, self.__mu_target_right))
        alpha_left_wheel_neg.append(min(self.__mu_spin_neg, self.__mu_ball_front, self.__mu_target_right))
        
        ### Positive activation
        alpha_left_wheel_pos.append(min(self.__mu_spin_neg, self.__mu_ball_front, self.__mu_target_left))
        alpha_left_wheel_pos.append(min(self.__mu_spin_neg, self.__mu_ball_right, self.__mu_target_left))
        alpha_left_wheel_pos.append(min(self.__mu_spin_neg, self.__mu_ball_left, self.__mu_target_front))
        alpha_left_wheel_pos.append(min(self.__mu_spin_neg, self.__mu_ball_right, self.__mu_target_front))
        alpha_left_wheel_pos.append(min(self.__mu_spin_neg, self.__mu_ball_right, self.__mu_target_right))
        
        
        ## Neutral spin
        ### Negative activation
        alpha_left_wheel_neg.append(min(self.__mu_spin_ntr, self.__mu_ball_left, self.__mu_target_left))
        alpha_left_wheel_neg.append(min(self.__mu_spin_ntr, self.__mu_ball_left, self.__mu_target_front))
        alpha_left_wheel_neg.append(min(self.__mu_spin_ntr, self.__mu_ball_left, self.__mu_target_right))
        #alpha_left_wheel_neg.append(min(self.__mu_spin_ntr, self.__mu_ball_front, self.__mu_target_right))
        alpha_left_wheel_neg.append(min(self.__mu_spin_ntr, self.__mu_ball_right, self.__mu_target_right))
        
        ### Positive activation
        alpha_left_wheel_pos.append(min(self.__mu_spin_ntr, self.__mu_ball_front, self.__mu_target_right))
        
        alpha_left_wheel_pos.append(min(self.__mu_spin_ntr, self.__mu_ball_front, self.__mu_target_left))
        alpha_left_wheel_pos.append(min(self.__mu_spin_ntr, self.__mu_ball_right, self.__mu_target_left))
        alpha_left_wheel_pos.append(min(self.__mu_spin_ntr, self.__mu_ball_front, self.__mu_target_front))
        alpha_left_wheel_pos.append(min(self.__mu_spin_ntr, self.__mu_ball_right, self.__mu_target_front))
        
        
        ## Positive spin
        ### Negative activation
        alpha_left_wheel_neg.append(min(self.__mu_spin_pos, self.__mu_ball_left, self.__mu_target_left))
        alpha_left_wheel_neg.append(min(self.__mu_spin_pos, self.__mu_ball_left, self.__mu_target_front))
        
        ### Positive activation
        alpha_left_wheel_pos.append(min(self.__mu_spin_pos, self.__mu_ball_front, self.__mu_target_left))
        alpha_left_wheel_pos.append(min(self.__mu_spin_pos, self.__mu_ball_right, self.__mu_target_left))
        alpha_left_wheel_pos.append(min(self.__mu_spin_pos, self.__mu_ball_front, self.__mu_target_front))
        alpha_left_wheel_pos.append(min(self.__mu_spin_pos, self.__mu_ball_right, self.__mu_target_front))
        alpha_left_wheel_pos.append(min(self.__mu_spin_pos, self.__mu_ball_left, self.__mu_target_right))
        alpha_left_wheel_pos.append(min(self.__mu_spin_pos, self.__mu_ball_front, self.__mu_target_right))
        alpha_left_wheel_pos.append(min(self.__mu_spin_pos, self.__mu_ball_right, self.__mu_target_right))

        self.__mu_left_wheel_neg = max(alpha_left_wheel_neg)
        self.__mu_left_wheel_ntr = 0
        self.__mu_left_wheel_pos = max(alpha_left_wheel_pos)
        
        
        
        # Rules for right wheel
        ## Negative spin
        ### Negative activation
        alpha_right_wheel_neg.append(min(self.__mu_spin_neg, self.__mu_ball_left, self.__mu_target_front))
        alpha_right_wheel_neg.append(min(self.__mu_spin_neg, self.__mu_ball_right, self.__mu_target_front))
        alpha_right_wheel_neg.append(min(self.__mu_spin_neg, self.__mu_ball_right, self.__mu_target_right))
        
        ### Positive activation
        alpha_right_wheel_pos.append(min(self.__mu_spin_neg, self.__mu_ball_left, self.__mu_target_left))
        alpha_right_wheel_pos.append(min(self.__mu_spin_neg, self.__mu_ball_front, self.__mu_target_left))
        alpha_right_wheel_pos.append(min(self.__mu_spin_neg, self.__mu_ball_right, self.__mu_target_left))
        alpha_right_wheel_pos.append(min(self.__mu_spin_neg, self.__mu_ball_front, self.__mu_target_front))
        alpha_right_wheel_pos.append(min(self.__mu_spin_neg, self.__mu_ball_left, self.__mu_target_right))
        alpha_right_wheel_pos.append(min(self.__mu_spin_neg, self.__mu_ball_right, self.__mu_target_right))
        
        
        ## Neutral spin
        ### Negative activation
        #alpha_right_wheel_neg.append(min(self.__mu_spin_ntr, self.__mu_ball_front, self.__mu_target_left))
        alpha_right_wheel_neg.append(min(self.__mu_spin_ntr, self.__mu_ball_right, self.__mu_target_left))
        alpha_right_wheel_neg.append(min(self.__mu_spin_ntr, self.__mu_ball_right, self.__mu_target_front))
        
        ### Positive activation
        alpha_right_wheel_pos.append(min(self.__mu_spin_ntr, self.__mu_ball_front, self.__mu_target_left))
        
        alpha_right_wheel_pos.append(min(self.__mu_spin_ntr, self.__mu_ball_left, self.__mu_target_left))
        alpha_right_wheel_pos.append(min(self.__mu_spin_ntr, self.__mu_ball_left, self.__mu_target_front))
        alpha_right_wheel_pos.append(min(self.__mu_spin_ntr, self.__mu_ball_front, self.__mu_target_front))
        alpha_right_wheel_pos.append(min(self.__mu_spin_ntr, self.__mu_ball_left, self.__mu_target_right))
        alpha_right_wheel_pos.append(min(self.__mu_spin_ntr, self.__mu_ball_front, self.__mu_target_right))
        alpha_right_wheel_pos.append(min(self.__mu_spin_ntr, self.__mu_ball_right, self.__mu_target_right))
        
        
        ## Positive spin
        ### Negative activation
        alpha_right_wheel_neg.append(min(self.__mu_spin_pos, self.__mu_ball_front, self.__mu_target_left))
        alpha_right_wheel_neg.append(min(self.__mu_spin_pos, self.__mu_ball_right, self.__mu_target_left))
        alpha_right_wheel_neg.append(min(self.__mu_spin_pos, self.__mu_ball_front, self.__mu_target_front))
        alpha_right_wheel_neg.append(min(self.__mu_spin_pos, self.__mu_ball_right, self.__mu_target_front))
        alpha_right_wheel_neg.append(min(self.__mu_spin_pos, self.__mu_ball_right, self.__mu_target_right))
        
        ### Positive activation
        alpha_right_wheel_pos.append(min(self.__mu_spin_pos, self.__mu_ball_left, self.__mu_target_left))
        alpha_right_wheel_pos.append(min(self.__mu_spin_pos, self.__mu_ball_left, self.__mu_target_front))
        alpha_right_wheel_pos.append(min(self.__mu_spin_pos, self.__mu_ball_left, self.__mu_target_right))
        alpha_right_wheel_pos.append(min(self.__mu_spin_pos, self.__mu_ball_front, self.__mu_target_right))

        self.__mu_right_wheel_neg = max(alpha_right_wheel_neg)
        self.__mu_right_wheel_ntr = 0
        self.__mu_right_wheel_pos = max(alpha_right_wheel_pos)

        self.__update_action()

    def __update_action(self):
        print('mu left wheel negative:', self.__mu_left_wheel_neg)
        print('mu left wheel neutral:', self.__mu_left_wheel_ntr)
        print('mu left wheel positive:', self.__mu_left_wheel_pos)
        
        print('mu right wheel negative:', self.__mu_right_wheel_neg)
        print('mu right wheel neutral:', self.__mu_right_wheel_ntr)
        print('mu right wheel positive:', self.__mu_right_wheel_pos)
        
        left_denominator = self.__mu_left_wheel_neg + self.__mu_left_wheel_ntr + self.__mu_left_wheel_pos
        if(left_denominator is not 0):
            self.__left_action = 5*( - self.__mu_left_wheel_neg + self.__mu_left_wheel_pos)/left_denominator
        else:
            self.__left_action = 0

        right_denominator = self.__mu_right_wheel_neg + self.__mu_right_wheel_ntr + self.__mu_right_wheel_pos
        if(right_denominator is not 0):
            self.__right_action = 5*( - self.__mu_right_wheel_neg + self.__mu_right_wheel_pos)/right_denominator
        else:
            self.__right_action = 0

    ##Triangle function in Matlab for reference
    ##function [mi] = triangulo (x,alfa,beta,gama)
    ##mi = 0;
    ##if ((x <= alfa) || (x >= gama)) mi=0; end;
    ##if ((x >= alfa) && (x <= beta)) mi=(x - alfa)/(beta - alfa); end;
    ##if ((x > beta) && (x < gama)) mi=(gama - x)/(gama - beta); end;
    ##end
    def __trapezium(self, x, params):
        """
        Calculate the membership of a value given a triangle shaped membership
        function
        """
        alpha = params[0]
        beta = params[1]
        gamma = params[2]
        delta = params[3]
        if(x <= alpha or x >= delta):
            return 0
        elif(x >= alpha and x <= beta):
            return (x - alpha)/(beta - alpha)
        elif(x > beta and x < gamma):
            return 1
        else:
            return (delta - x)/(delta - gamma)
