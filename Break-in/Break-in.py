import pygame
from pygame.locals import *
import random
import math
import sys

#Defines
XSIZE = 500
YSIZE = 500
WALL_SIZE = 10
SPEED = 5

NO_BOUNCE = 0
UP_BOUNCE = 1
LEFT_BOUNCE = 2
RIGHT_BOUNCE = 3
DOWN_BOUNCE = 4

#Helper functions for tuples
def tupAdd(A, B):
    return (A[0] + B[0], A[1] + B[1])

def tupSub(A, B):
    return (A[0] - B[0], A[1] - B[1])

def tupDivInt(A, factor):
    return (math.floor(A[0]/factor), math.floor(A[1]/factor))

#Class for the blocks at the bottom of the screen
class Block:
    def __init__(self, pos, size):
        self.pos = pos
        self.size = size
    
    def CheckCollision(self, pos):
        #If the ball is above or to the left, there's no collision
        if self.pos[0] > pos[0] or self.pos[1] > pos[1]:
            return NO_BOUNCE
        #Otherwise if the ball is further than size of the block below or to the right, there's no collision
        elif self.pos[0] + self.size[0] < pos[0] or self.pos[1] + self.size[1] < pos[1]:
            return NO_BOUNCE
        
        #The position of the ball is inside that of the block, so we need to handle it
        posInBlock = tupSub(pos, self.pos)
        distFromTop = posInBlock[1]
        distFromLeft = posInBlock[0]
        distFromRight = self.size[0] - posInBlock[0]
        distFromBottom = self.size[1] - posInBlock[1]

        if distFromTop < distFromLeft and distFromTop < distFromRight and distFromTop < distFromBottom:
            #The ball is closest the top, so this is a top bounce
            return UP_BOUNCE
        elif distFromBottom < distFromRight and distFromBottom < distFromLeft:
            return DOWN_BOUNCE
        elif distFromLeft < distFromRight:
            return LEFT_BOUNCE
        else:
            return RIGHT_BOUNCE


class BreakIn:
    def __init__(self):
        #Set up here
        pygame.init()
        self.screen = pygame.display.set_mode((XSIZE, YSIZE))
        pygame.display.set_caption("Break in")

        self.clock = pygame.time.Clock()

        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((200,200,200))

        self.topLeft = (WALL_SIZE, WALL_SIZE)
        self.topRight = (XSIZE - WALL_SIZE, WALL_SIZE)
        self.bottomLeft = (WALL_SIZE, YSIZE - WALL_SIZE)
        self.bottomRight = (XSIZE - WALL_SIZE, YSIZE - WALL_SIZE)

        #Load assets
        self.ball = pygame.image.load('Assets/ball.png')
        self.block = pygame.image.load('Assets/block.png')
        if pygame.font:
            self.font = pygame.font.Font(None, 40)

        #A list for all the blocks on screen
        self.blocks = []

        self.ballPos = (XSIZE/2, WALL_SIZE)

        #Calculate a random direction for the ball to move in, so that it will be moving with SPEED in that direction
        xSpeed = random.random() * 5
        ySpeed = math.sqrt(float(SPEED) ** 2 - xSpeed ** 2)
        if random.randint(0,1) == 1:
            xSpeed = -xSpeed
        self.ballSpeed = (xSpeed, -ySpeed)
        self.blockSpeed = 0

        self.lives = 3

        #Flag for ending, True is player wins, False is player loses
        self.ended = None

        #Start the main gameplay loop
        self.Run()

    def Run(self):
        self.finished = False

        #Add blocks to the game
        for i in range(1, 11):
            for j in range(0, 3):
                self.blocks.append(Block((i * 40, 350 + j * 50), self.block.get_size()))

        while not self.finished:
            #Handle input
            if self.ended == None:
                self.HandleInput()

            #Draw screen
            self.Draw()

            self.clock.tick(60)

    def HandleInput(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()

        #Movement for blocks
        moving = True
        if pygame.key.get_pressed()[K_LEFT]:
            if self.blockSpeed > -5:
                self.blockSpeed -= 0.2
            for b in self.blocks:
                if b.pos[0] < WALL_SIZE:
                    moving = False
                    self.blockSpeed = 0
        elif pygame.key.get_pressed()[K_RIGHT]:
            if self.blockSpeed < 5:
                self.blockSpeed += 0.2
            for b in self.blocks:
                if b.pos[0] > XSIZE - WALL_SIZE - b.size[0]:
                    moving = False
                    self.blockSpeed = 0
        else:
            self.blockSpeed = 0
        
        if moving == True:
            for b in self.blocks:
                b.pos = b.pos[0] + self.blockSpeed, b.pos[1]

    def Draw(self):
        #clear screen
        self.screen.blit(self.background, (0,0))

        #Draw walls
        pygame.draw.line(self.screen, (10,10,10), self.topLeft, self.topRight)
        pygame.draw.line(self.screen, (10,10,10), self.topLeft, self.bottomLeft)
        pygame.draw.line(self.screen, (10,10,10), self.topRight, self.bottomRight)
        pygame.draw.line(self.screen, (255,10,10), self.bottomLeft, self.bottomRight)

        #Perform ball movement
        if self.ended == None:
            self.ballPos = tupAdd(self.ballPos, self.ballSpeed)
            self.CheckAndCalculateCollision()

        #Draw ball
        #Adjust by size of ball/2 to draw so the middle of the ball is ballPos
        self.screen.blit(self.ball, tupSub(self.ballPos, tupDivInt(self.ball.get_size(), 2)))

        #Draw blocks
        for b in self.blocks:
            self.screen.blit(self.block, b.pos) 

        #Draw lives
        lifeTxt = self.font.render("Lives: " + str(self.lives), True, (10,10,10))
        self.screen.blit (lifeTxt, (XSIZE - 120, WALL_SIZE * 2))

        #Draw end message
        if self.ended == True:
            endString = "You Win!"
        elif self.ended == False:
            endString = "You lose..."
        if self.ended != None:
            endTxt = self.font.render(endString, True, (10,10,10))
            self.screen.blit (endTxt, (WALL_SIZE * 5, WALL_SIZE * 5))

        #Refresh the screen
        pygame.display.flip()

    #Sub functions below
    def CheckAndCalculateCollision(self):
        #Check for left wall
        if self.ballPos[0] < WALL_SIZE:
            #Reverse X velocity
            self.ballSpeed = (- self.ballSpeed[0], self.ballSpeed[1])
        #Check for right wall
        if self.ballPos[0] > XSIZE - WALL_SIZE:
            #Reverse X velocity
            self.ballSpeed = (- self.ballSpeed[0], self.ballSpeed[1])
        #Check for top wall
        if self.ballPos[1] <  WALL_SIZE:
            #Reverse Y velocity
            self.ballSpeed = (self.ballSpeed[0], - self.ballSpeed[1])
        #Check for bottom wall
        if self.ballPos[1] >  YSIZE - WALL_SIZE:
            #Mark as lost
            self.lives -= 1
            if self.lives > 0:
                #Reset the ball, and make sure the speed is in the right direction
                self.ballPos = (XSIZE/2, WALL_SIZE)
                #Calculate a random direction for the ball to move in, so that it will be moving with SPEED in that direction
                xSpeed = random.random() * 5
                ySpeed = math.sqrt(float(SPEED) ** 2 - xSpeed ** 2)
                if random.randint(0,1) == 1:
                    xSpeed = -xSpeed
                self.ballSpeed = (xSpeed, -ySpeed)
            else:
                self.ended = False
        
        for b in self.blocks:
            ret = b.CheckCollision(self.ballPos)
            if ret == UP_BOUNCE:
                if self.ballSpeed[1] > 0:
                    #Reverse Y velocity
                    self.ballSpeed = (self.ballSpeed[0], - self.ballSpeed[1])
                    #Modify the ball speed with the speed of the block
                    if self.blockSpeed != 0:
                        if self.blockSpeed > 0:
                            xSpeed = self.ballSpeed[0] + 1
                        else:
                            xSpeed = self.ballSpeed[0] - 1
                        #Only go forward with this if the new speed is under the maximum
                        if xSpeed < SPEED and xSpeed > -SPEED:
                            ySpeed = math.sqrt(SPEED**2 - xSpeed**2)
                            #Make sure the direction is correct
                            if self.ballSpeed[1] < 0:
                                ySpeed = -ySpeed
                            self.ballSpeed = (xSpeed, ySpeed)
                        else:
                            pass
                else:
                    #The ball wasn't moving down, so it can't up bounce, must have been a corner hit. 
                    #Reverse X velocity instead
                    self.ballSpeed = (- self.ballSpeed[0], self.ballSpeed[1])
            elif ret == DOWN_BOUNCE:
                if self.ballSpeed[1] < 0:
                    #Reverse Y velocity
                    self.ballSpeed = (self.ballSpeed[0], - self.ballSpeed[1])
                    #Modify the ball speed with the speed of the block
                    if self.blockSpeed != 0:
                        xSpeed = self.ballSpeed[0] + self.blockSpeed/(SPEED * 2)
                        #Only go forward with this if the new speed is under the maximum
                        if xSpeed < SPEED and xSpeed > -SPEED:
                            ySpeed = math.sqrt(SPEED**2 - xSpeed**2)
                            #Make sure the direction is correct
                            if self.ballSpeed[1] < 0:
                                ySpeed = -ySpeed
                            self.ballSpeed = (xSpeed, ySpeed)
                else:
                    #The ball wasn't moving up, so it can't down bounce, must have been a corner hit. 
                    #Reverse X velocity instead
                    self.ballSpeed = (- self.ballSpeed[0], self.ballSpeed[1])
            elif ret == LEFT_BOUNCE:
                if self.ballSpeed[0] > 0:
                    #Reverse X velocity
                    self.ballSpeed = (-self.ballSpeed[0], self.ballSpeed[1])
                else:
                    #The ball wasn't moving right, so it can't left bounce, must have been a corner hit. 
                    #Reverse Y velocity instead
                    self.ballSpeed = (self.ballSpeed[0], -self.ballSpeed[1])
            elif ret == RIGHT_BOUNCE:
                if self.ballSpeed[0] < 0:
                    #Reverse X velocity
                    self.ballSpeed = (-self.ballSpeed[0], self.ballSpeed[1])
                else:
                    #The ball wasn't moving left, so it can't right bounce, must have been a corner hit. 
                    #Reverse Y velocity instead
                    self.ballSpeed = (self.ballSpeed[0], -self.ballSpeed[1])
            
            if ret != NO_BOUNCE:
                self.blocks.remove(b)
                if len(self.blocks) == 0:
                    #The player has won
                    self.ended = True

#Run the game
game = BreakIn()
