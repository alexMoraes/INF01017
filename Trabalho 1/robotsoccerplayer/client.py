import sys
sys.path.append("C:\\Users\\Alex\\Documents\\INF01017\\Trabalho 1")

import math
from robotsoccerplayer import Server
from robotsoccerplayer import Coord

GET_WORLD = 0
ACT = 4
GET_MATCH_STATUS = 6

class Robot(object):
    """
    Robot description.
    """
    def __init__(self):
        self.force = [0, 0]
        self.pos = Coord()
        self.old_pos = Coord()
        self.angle = 0
        self.old_angle = 0
        self.obstacle = Coord()

    def __str__(self):
        return '<Robot %s>'%str(self.pos)

    def __repr__(self):
        return str(self)

class Match:
    """
    Implements the soccer match communication protocol and offers information
    about the board and the match.

    All methods of this class are relative to own robot, i.e, the ``robot_id`` 
    robot.
    """

    def __init__(self):
        self.scores = [0, 0]
        
        self.world_height = 0
        self.world_width = 0
        
        self.goals = [Coord(), Coord()]
        self.goal_deep = 0
        self.goal_length = 0
        
        self.robot_id = 0
        self.robot_radius = 0
        self.robot_count = 0
        
        self.ball = Coord()
        self.robots = None
        self.server = None

    def start(self, host='localhost', port=1024):
        """
        Connects to robot soccer match simulator and gather initial match
        information.
        """
        self.server = Server()
        self.server.connect((host, port))

        self.robot_id = self.server.recv_int()
        self.server.send_int(GET_WORLD)
        self.robot_count = self.server.recv_int()
        self.robot_radius = self.server.recv_float()
        self.world_width = self.server.recv_float()
        self.world_height = self.server.recv_float()
        self.goal_length = self.server.recv_float()
        self.goal_deep = self.server.recv_float()

        self.goals[0].x = -self.world_width
        self.goals[1].x = self.world_width

        self.robots = [Robot() for i in range(self.robot_count)]
        
        self.server.send_int(GET_MATCH_STATUS)
        self.__update_match()

    def disconnect(self):
        """
        Disconnects from robot soccer match simulator.
        """
        self.server.close()

    def act(self, force_left, force_right):
        """
        Does action for the robot. Receives the forces of left and right motor.
        """
        self.server.send_int(ACT)
        self.server.send_int(self.robot_id)
        self.server.send_float(force_left)
        self.server.send_float(force_right)
        self.__update_match()
    
    def __update_match(self):
        """
        Gets match status.
        """
        self.ball.x = self.server.recv_float()
        self.ball.y = self.server.recv_float()
        self.server.recv_int()

        for robot in self.robots:
            robot.pos.x = self.server.recv_float()
            robot.pos.y = self.server.recv_float()
            robot.angle = self.server.recv_float()
            robot.old_pos.x = self.server.recv_float()
            robot.old_pos.y = self.server.recv_float()
            robot.old_angle = self.server.recv_float()
            robot.obstacle.x = self.server.recv_float()
            robot.obstacle.y = self.server.recv_float()
            robot.force[0] = self.server.recv_float()
            robot.force[1] = self.server.recv_float()
            self.server.recv_int()

        self.scores[0] = self.server.recv_int()
        self.scores[1] = self.server.recv_int()

    def get_ball_angle(self):
        """
        Calculates angle difference between robot and ball, in radians.
        """
        robot = self.get_own_robot()
        alpha = (self.ball - robot.pos).angle() - robot.angle
        return self.__adjust_angle(alpha)

    def get_target_angle(self):
        """
        Calculates angle difference in radians between robot and correspondent
        goal.
        """
        robot = self.get_own_robot()
        goal = self.get_own_goal()
        alpha = (goal-self.ball).angle() - (self.ball-robot.pos).angle()
        return self.__adjust_angle(alpha)

    def get_obstacle_angle(self):
        """
        Calculates angle difference in radians between robot and the nearest 
        obstacle.
        """
        robot = self.get_own_robot()
        alpha = (robot.obstacle-robot.pos).angle() - robot.angle
        return self.__adjust_angle(alpha)

    def get_spin(self):
        """
        Calculates the angle momentum in radians.
        """
        robot = self.get_own_robot()
        alpha = robot.angle-robot.old_angle
        return self.__adjust_angle(alpha)

    def get_ball_distance(self):
        """
        Calculates distance in milimeters between robot and ball.
        """
        robot = self.get_own_robot()
        return (self.ball-robot.pos).size() - self.robot_radius

    def get_target_distance(self):
        """
        Calculates distance in milimeters between robot and goal.
        """
        robot = self.get_own_robot()
        goal = self.get_own_goal()
        return (goal-robot.pos).size() - self.robot_radius

    def get_obstacle_distance(self):
        """
        Calculates distance in milimeters between robot and the nearest 
        obstacle.
        """
        robot = self.get_own_robot()
        return (robot.obstacle-robot.pos).size() - self.robot_radius

    def get_own_robot(self):
        """
        Gets the own robot description
        """
        return self.robots[self.robot_id]

    def get_own_goal(self):
        """
        Gets own attacking goal's center.  Notice the goal of robots[1] (right) 
        is goal[0] (left) and vice versa.
        """
        return self.goals[1-self.robot_id]
    
    def get_own_score(self):
        """
        Gets scores of the own robot.
        """
        return self.scores[self.robot_id]
    
    def get_rival_robot(self):
        """
        Gets the rival robot description.
        """
        if self.robot_count == 2:
            return self.robots[1-self.robot_id]
    
    def get_rival_goal(self):
        """
        Gets attacking goal's center of the rival. Notice the goal of robots[1] 
        (right) is goal[0] (left) and vice versa.
        """
        return self.goals[self.robot_id]
    
    def get_rival_score(self):
        """
        Gets scores of the rival's robot.
        """
        return self.scores[1-self.robot_id]
    
    def __adjust_angle(self, angle):
        if angle > math.pi:
            angle -= 2*math.pi
        elif angle < -math.pi:
            angle += 2*math.pi
        
        return angle
