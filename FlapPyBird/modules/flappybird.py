from FlapPyBird.resources.config import *
import pygame, random
import numpy as np

class Bird(object):
    def __init__(self, player_index_gen, neural_network):
        # select random player sprites
        self.playerIndexGen = player_index_gen['playerIndexGen']
        self.x, self.y = int(SCREENWIDTH * 0.2), player_index_gen['playery']

        self.neural_network = neural_network

        self.index = 0
        self.distance = 0

        """ SET BIRD PARAMETERS """
        self.y_velocity    =  -9   # player's velocity along Y, default same as playerFlapped
        self.max_y_velocity =  10   # max vel along Y, max descend speed
        self.gravity    =   1   # players downward accleration
        self.flap_speed =  -9   # players speed on flapping
        self.energy_used = 0

        """ SET FLAGS """
        self.ground_collision = False
        self.pipe_collision = False
        self.collision = False
        self.flapped = False


    def next(self):
        self.index = next(self.playerIndexGen)


    def flap_decision(self, pipes):

        # Setup the input layer
        X = [0 for _ in range(6)]
        X[0] = self.y / SCREENHEIGHT
        X[1] = pipes.upper[0]['x'] / SCREENWIDTH
        X[2] = pipes.upper[0]['y'] / SCREENHEIGHT
        X[3] = pipes.upper[1]['x'] / SCREENWIDTH
        X[4] = pipes.upper[1]['y'] / SCREENHEIGHT
        X[5] = 1
        # Feed the neural network information
        self.neural_network.learn(X)

        # Obtain Prediction
        if self.neural_network.decision() == 1:
            # Decide to flap
            if self.y > -2 * IMAGES['player'][0].get_height():
                self.y_velocity = self.flap_speed
                self.flapped = True
                self.energy_used += 10
                SOUNDS['wing'].play() if SOUND_ON else None


    def move(self):
        if self.y_velocity < self.max_y_velocity and not self.flapped:
            self.y_velocity += self.gravity
        if self.flapped:
            self.flapped = False
        playerHeight = IMAGES['player'][self.index].get_height()
        self.y += min(self.y_velocity, BASEY - self.y - playerHeight)


    def check_crash(self, pipes, basex, score):
        self.check_collision(pipes)

        if self.collision:
            # Values returned to species.py

            self.crashInfo = {
                'network': self.neural_network,
                'distance': self.distance*-1,
                'energy': self.energy_used,
            }
            return True
        else:
            return False


    def check_collision(self, pipes):
        """returns True if player collders with base or pipes."""
        player = {}
        player['w'] = IMAGES['player'][0].get_width()
        player['h'] = IMAGES['player'][0].get_height()

        # if player crashes into ground
        if self.y + player['h'] >= BASEY - 1:
            self.ground_collision = True
        else:
            playerRect = pygame.Rect(self.x, self.y,
                                     player['w'], player['h'])
            pipeW = IMAGES['pipe'][0].get_width()
            pipeH = IMAGES['pipe'][0].get_height()

            for uPipe, lPipe in zip(pipes.upper, pipes.lower):
                # upper and lower pipe rects
                uPipeRect = pygame.Rect(uPipe['x'], uPipe['y'], pipeW, pipeH)
                lPipeRect = pygame.Rect(lPipe['x'], lPipe['y'], pipeW, pipeH)

                # player and upper/lower pipe hitmasks
                pHitMask = HITMASKS['player'][self.index]
                uHitmask = HITMASKS['pipe'][0]
                lHitmask = HITMASKS['pipe'][1]

                # if bird collided with upipe or lpipe
                uCollide = self.pixelCollision(playerRect, uPipeRect, pHitMask, uHitmask)
                lCollide = self.pixelCollision(playerRect, lPipeRect, pHitMask, lHitmask)

                if uCollide or lCollide:
                    self.pipe_collision = True

        if self.ground_collision or self.pipe_collision:
            self.collision = True


    def pixelCollision(self, rect1, rect2, hitmask1, hitmask2):
        """Checks if two objects collide and not just their rects"""

        rect = rect1.clip(rect2)

        if rect.width == 0 or rect.height == 0:
            return False

        x1, y1 = rect.x - rect1.x, rect.y - rect1.y
        x2, y2 = rect.x - rect2.x, rect.y - rect2.y

        for x in range(rect.width):
            for y in range(rect.height):
                if hitmask1[x1+x][y1+y] and hitmask2[x2+x][y2+y]:
                    return True
        return False
