import sys
sys.path.append("C:\\Users\\Alex\\Documents\\INF01017")

import math
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
        self.match = Match()
        self.match.start(host, port)
        self.fuzzy = Fuzzy()

    def play(self):
        """
        Play using fuzzy controller
        """
        i = 0
        while(i < 1e4):
            action = self.fuzzy.get_action(self.match)
            self.match.act(action[0], action[1])
            i += 1

PI = math.pi
RIGHT = (-PI, -PI, -PI/2, 0)
FRONT = (-PI/2, 0, 0, PI/2)
LEFT = (0, PI/2, PI, PI)  
class Fuzzy:
    def get_action(self, match):
        self.__mu_ball_left = self.__trapezium(match.get_ball_angle(), LEFT)
        self.__mu_ball_front = self.__trapezium(match.get_ball_angle(), FRONT)
        self.__mu_ball_right = self.__trapezium(match.get_ball_angle(), RIGHT)

        self.__mu_target_left = self.__trapezium(match.get_target_angle(), LEFT)
        self.__mu_target_front = self.__trapezium(match.get_target_angle(), FRONT)
        self.__mu_target_right = self.__trapezium(match.get_target_angle(), RIGHT)
        
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
        alpha_left = []
        alpha_front = []
        alpha_right = []

        alpha_left.append(min(self.__mu_ball_left, self.__mu_target_front))
        alpha_left.append(min(self.__mu_ball_left, self.__mu_target_right))
        alpha_left.append(min(self.__mu_ball_front, self.__mu_target_right))
        self.__mu_robot_left = max(alpha_left)

        alpha_front.append(min(self.__mu_ball_left, self.__mu_target_left))
        alpha_front.append(min(self.__mu_ball_front, self.__mu_target_front))
        alpha_front.append(min(self.__mu_ball_right, self.__mu_target_right))
        self.__mu_robot_front = max(alpha_front)
        
        alpha_right.append(min(self.__mu_ball_front, self.__mu_target_left))
        alpha_right.append(min(self.__mu_ball_right, self.__mu_target_left))
        alpha_right.append(min(self.__mu_ball_right, self.__mu_target_front))
        self.__mu_robot_right = max(alpha_right)

        self.__update_action()

    def __update_action(self):
        denominator = (self.__mu_robot_left + self.__mu_robot_front + self.__mu_robot_right)
        self.__left_action = (- self.__mu_robot_left + self.__mu_robot_front + self.__mu_robot_right)/denominator
        self.__right_action = (self.__mu_robot_left + self.__mu_robot_front - self.__mu_robot_right)/denominator

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
