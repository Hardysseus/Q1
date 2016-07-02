#!/usr/bin/python
# -*- coding: utf-8 -*-
# Q1 - A game
__author__ = "René Rose, info@rundwerk.de"
__version__ = "0.1.0"
#######################################################################################################
# Conventions
# Directions named S (South), N (North), W (West), O (East)
# Avatar is named A in all comments
# Code conventions
# by http://visualgit.readthedocs.io/en/latest/pages/naming_convention.html
#######################################################################################################
# Import and Initalize
import pygame, json, time, random, sys
import dbconn
from pygame.locals import *
pygame.init()
#######################################################################################################
# Display Configuration
size= (1760,960)
screen = pygame.display.set_mode(size)
screen.fill((255,255,255))
pygame.display.set_caption("Q1 - the ESA three game")
#######################################################################################################
# Entities
# General
# game can be called by esa 2 or 3
if sys.argv == True:
    chosenmap = sys.argv[1] # map, which was choosen from GUI ESA 2
else:
    chosenmap = "Map1" # a map named Map1 have to exist!! -> generated by ESA 2 Dialog
print ("You plays: ", chosenmap)

SHAPE_SIZE = 32
MAX_X_TILES = 55
MAX_Y_TILES = 23
f = pygame.font.Font(None, 24)
tick = 0 # to slowify some actions
reset_time = 0 # counts the time to restart after lost/win
time_to_reset = 5 # time to restart in seconds
win_the_game = False # trigger the game state
# DB connection
dbc = dbconn.DbConn( )
# Map
map = dbc.crudR( " Select * from maps WHERE mapname = '" + chosenmap + "'" )
map_list = json.loads( map[0][3] )
init_map_list = json.loads( map[0][3] )

# Concrete
# Avatar class
class Avatar(object):
    """ The avatar class """
    def __init__(self):
        self.avatar_direction = "S" # face direction
        self.isdead = False # "life-status" of A
        self.wins = False # True if A wins the game
        self.life_num = 3 # Numbers of lifes
        self.avatar_image = pygame.image.load( "static/img/avatar.png" )
        self.avatar = pygame.transform.scale( self.avatar_image, (SHAPE_SIZE, SHAPE_SIZE) )
        self.avatar_rect = self.avatar.get_rect( )
        self.die_sound = pygame.mixer.Sound( 'static/sounds/die.wav' )

        # entities settings
        # optional make a "Shot"-Class
        self.image_shot = pygame.image.load( "static/img/shot.png" )
        self.shot = pygame.transform.scale( self.image_shot, (SHAPE_SIZE, SHAPE_SIZE) )
        self.shot_rect = self.shot.get_rect( )
        self.shot_sound = pygame.mixer.Sound( 'static/sounds/throw.wav' )
        self.shot_direction = ''
        self.shot_length = 0
        self.shot_maxlength = 9
        self.shot_rect.x = -1 * SHAPE_SIZE
        self.shot_rect.y = -1 * SHAPE_SIZE
        self.no_shot_elements = [61, 62, 161] # tiles which cannot be damaged or passed by a shot
        self.set_avatar_initial_position( ) # set A

    def set_avatar_initial_position(self):
        ''' Initial position of A '''
        validpos = False
        while validpos == False:
            avatar_x = random.randint( 1, 5 ) # A spawning in 0 - 5 x-tiles
            avatar_y = random.randint( 1, MAX_Y_TILES )
            failneighbours = [1, 61, 62, 127] # make avoid spawning without direct movement
            validpos = validate_position( avatar_y, avatar_x, map_list, failneighbours )
        self.avatar_rect.x = avatar_x * SHAPE_SIZE
        self.avatar_rect.y = avatar_y * SHAPE_SIZE

    ''' Direction '''
    def set_avatar_direction(self, goes):
        ''' Turns the avatar to new direction'''
        if self.avatar_direction == "S":
            if goes == "O":
                self.avatar = pygame.transform.rotate(self.avatar, 90)
            elif goes == "N":
                self.avatar = pygame.transform.rotate(self.avatar, 180)
            elif goes == "W":
                self.avatar = pygame.transform.rotate(self.avatar, -90)
        elif self.avatar_direction == "W":
            if goes == "O":
                self.avatar = pygame.transform.rotate(self.avatar, 180)
            elif goes == "N":
                self.avatar = pygame.transform.rotate(self.avatar, -90)
            elif goes == "S":
                self.avatar = pygame.transform.rotate(self.avatar, 90)
        elif self.avatar_direction == "N":
            if goes == "O":
                self.avatar = pygame.transform.rotate(self.avatar, -90)
            elif goes == "W":
                self.avatar = pygame.transform.rotate(self.avatar, 90)
            elif goes == "S":
                self.avatar = pygame.transform.rotate(self.avatar, 180)
        elif self.avatar_direction == "O":
            if goes == "W":
                self.avatar = pygame.transform.rotate(self.avatar, 180)
            elif goes == "N":
                self.avatar = pygame.transform.rotate(self.avatar, 90)
            elif goes == "S":
                self.avatar = pygame.transform.rotate(self.avatar, -90)

        self.avatar_direction = goes # save new A direction

    def get_avatar_direction(self):
        """ Send face direction of A """
        return self.avatar_direction

    def get_avatar_rect(self):
        ''' Send A's rectangle '''
        return self.avatar_rect

    ''' Functions for die/live '''
    def get_avatar_status(self):
        ''' Send status of A '''
        return self.isdead

    def set_avatar_status(self, state):
        ''' Set status of A '''
        self.isdead = state
        if state == True:
            self.die_sound.play( )
            self.set_life_num( 1 )

    def get_life_num(self):
        ''' send numbers of lifes of A '''
        return self.life_num

    def set_life_num(self, newnum):
        ''' reduce live number '''
        self.life_num = self.life_num - newnum

    ''' Tools and weapons '''
    def shot_now(self):
        ''' Sets the shot sprite on A and gives it the direction
            !!! when avatar direction is used explicitely, so shot can be endless
        '''
        self.shot_sound.play( )
        self.shot_rect.x = self.avatar_rect.x
        self.shot_rect.y = self.avatar_rect.y
        self.shot_direction = self.get_avatar_direction( )
        self.shot_length = 0

    def blit_shot(self):
        ''' Blit the shot '''
        self.shot_length = self.shot_length + 1

        if self.shot_direction == "S":
            self.shot_rect.y = self.shot_rect.y + SHAPE_SIZE
        elif self.shot_direction == "N":
            self.shot_rect.y = self.shot_rect.y - SHAPE_SIZE
        elif self.shot_direction == "W":
            self.shot_rect.x = self.shot_rect.x - SHAPE_SIZE
        elif self.shot_direction == "O":
            self.shot_rect.x = self.shot_rect.x + SHAPE_SIZE

        # check, wheter a shot can be blitted on actual tile
        # if not, shot is set in off-position
        for t in self.no_shot_elements:
            _y = int( self.shot_rect.y / SHAPE_SIZE )
            _x = int( self.shot_rect.x / SHAPE_SIZE )
            if _y >= MAX_Y_TILES:
                pass
            else:
                if map_list[_y][_x][0] == t:
                    self.shot_rect.x = -1 * SHAPE_SIZE
                    self.shot_rect.y = -1 * SHAPE_SIZE

        # get the enmy targets
        enemy_list = enemylist.get_enemy_list( )
        _spawner_rect = spawner.get_spawner_position( )

        # collision dectection -> shot - spawner
        if self.shot_rect.colliderect( _spawner_rect ):
            spawner.reduce_health( ) # spawener lose health
            self.shot_length = 0
            self.shot_direction = ""
            self.shot_rect.x = -1 * SHAPE_SIZE
            self.shot_rect.y = -1 * SHAPE_SIZE
        # collision dectection -> shot - elements of enemy list
        for e in enemy_list:
            if self.shot_rect.colliderect( e.enemy_rect ):
                e.reduce_health( ) # enemy lose health
                self.shot_length = 0
                self.shot_direction = ""
                self.shot_rect.x = -1 * SHAPE_SIZE
                self.shot_rect.y = -1 * SHAPE_SIZE
                break

        # Break the shot, if maxlength is reached, shot is positioned in off-position
        if self.shot_length == self.shot_maxlength:
            self.shot_length = 0
            self.shot_direction = ""
            self.shot_rect.x = -1 * SHAPE_SIZE
            self.shot_rect.y = -1 * SHAPE_SIZE

        screen.blit( self.shot, self.shot_rect )

    def blit_avatar(self):
        ''' Blit A '''
        screen.blit( self.avatar, self.avatar_rect )

class Grave(object):
    """ Class to handle the grave-sprite """
    def __init__(self):
        self.image_grave = pygame.image.load( "static/img/grave.png" )
        self.grave = pygame.transform.scale( self.image_grave, (SHAPE_SIZE, SHAPE_SIZE) )
        self.grave_rect = self.grave.get_rect( )
        self.set_grave_initial_position( )

    def set_grave_initial_position(self):
        """ position grave in the off """
        self.grave_rect.x = -SHAPE_SIZE
        self.grave_rect.y = -SHAPE_SIZE

    def grave_is_scooped(self):
        """ A has died, bury him ... """
        _avatar = avatar.get_avatar_rect( )
        self.grave_rect.x = _avatar.left
        self.grave_rect.y = _avatar.top

    def blit_grave(self):
        """ Blit the grave """
        screen.blit( self.grave, self.grave_rect )

class Spawner(object):
    """ "Boss"-enemy class"""
    def __init__(self):
        self.image_spawner = pygame.image.load( "static/img/spawner.jpg" )
        self.spawner = pygame.transform.scale( self.image_spawner, (SHAPE_SIZE, SHAPE_SIZE) )
        self.spawner_rect = self.spawner.get_rect( )
        self.isdead = False
        self.health = 15 # number of hits to destroy the spwaner
        self.ticker_num_max = 8 # seconds to reactivate one enemy
        self.ticker_num = 0 # to count the iteration
        self.set_spawner_initial_position( )
        self.die_sound = pygame.mixer.Sound( 'static/sounds/explosion.wav' )

    def set_spawner_initial_position(self):
        """ Initial position of spawner
            This can be refactored to a class method, its equal to setAvatarInitialPosition() """
        validpos = False
        while validpos == False:
            spawner_x = random.randint( 40, MAX_X_TILES ) #
            spawner_y = random.randint( 1, MAX_Y_TILES ) #
            failneighbours = [1, 61, 62, 127, 161]
            validpos = validate_position( spawner_y, spawner_x, map_list, failneighbours )
        self.spawner_rect.x = spawner_x * SHAPE_SIZE
        self.spawner_rect.y = spawner_y * SHAPE_SIZE

    def get_spawner_position(self):
        """ send spawner rectangle """
        return self.spawner_rect

    """ Functions for die/live """
    def get_spawner_status(self):
        """ Send status of Spawner """
        return self.isdead

    def set_spawner_status(self, state):
        """ set status of Spawner """
        self.isdead = state

    def reduce_health(self):
        """ reduces the health-value
            if health == 0, spawner dies and will be positioned in the off """
        self.health = self.health - 1
        if self.health == 0:
            self.die_sound.play( )
            self.set_spawner_status( True )
            self.spawner_rect.x = -1 * SHAPE_SIZE
            self.spawner_rect.y = -1 * SHAPE_SIZE

    def ticker(self):
        """ seconds counter
            ticker wil be called by game iteration every 30th iteration
            every call of ticker counts tickerNum up, in case tickerNumMax is reached, a enemy will be reactivated """
        self.ticker_num = self. ticker_num + 1
        if self.ticker_num == self.ticker_num_max:
            if self.get_spawner_status( ) == False:
                enemylist.create_new_enemy( )
                self.ticker_num = 0

    def blit_spawner(self):
        """ Blit the spawner """
        screen.blit( self.spawner, self.spawner_rect )

class EnemyList(object):
    """ Enemy List - a list is used to manage the enemies """
    def __init__(self):
        self.enemies_number = 45 # number of enemies on stage
        self.enemies_list = [] # list of all enemies
        self.enemy_list( ) # call the list
        self.enemy_types = ("Bug of Death", "Snake of Hell", "Spawner")

    def enemy_list(self):
        """ fill the list with enemies"""
        for i in range( 0, self.enemies_number ):
            self.create_new_enemy( )

    def create_new_enemy(self):
        """ create enemy by random value """
        if len( self.enemies_list ) < self.enemies_number:
            typerand = random.randint( 1, 100 )
            if typerand > 40:
                self.enemies_list.append( BugOfDeath( ) )
            else:
                self.enemies_list.append( SnakeOfHell( ) )

    def move_enemies(self, tick):
        """ call the move-function of every enemy"""
        if tick == 20:
            for i in range( 0, len( self.enemies_list ) ):
                self.enemies_list[i].move_enemy( )

    def get_enemy_list(self):
        """ send enemy list """
        return self.enemies_list

    def remove_enemy_from_list(self, enemy):
        """ a enemy has died, remove it from the list """
        self.enemies_list.remove( enemy )

    def enemy_blit_list(self, screen):
        """ blit all enemies """
        for i in range( 0, len( self.enemies_list ) ):
            self.enemies_list[i].blit( screen )

class Enemy(object):
    """ Abstract enemy class"""
    def __init__(self, imageEnemy, failneighbours):
        self.enemy = ''
        self.enemy_rect = ''
        self.image_enemy = imageEnemy
        self.failneighbours = failneighbours
        self.health = 5
        self.create_enemy( )
        self.dieSound = pygame.mixer.Sound( 'static/sounds/monsterdie.wav' )

    def create_enemy(self):
        """ create the enemy finally"""
        self.enemy = pygame.transform.scale( self.image_enemy, (SHAPE_SIZE, SHAPE_SIZE) )
        self.enemy_rect = self.enemy.get_rect( )
        validpos = False
        while validpos == False:
            enemy_x = random.randint( 5, MAX_X_TILES )
            enemy_y = random.randint( 1, MAX_Y_TILES )
            validpos = validate_position( enemy_y, enemy_x, map_list, self.failneighbours )
        self.enemy_rect.x = enemy_x * SHAPE_SIZE
        self.enemy_rect.y = enemy_y * SHAPE_SIZE
        self.move_enemy( )

    def move_enemy(self):
        """ move the enemy in random direction
            Do not move above unwalkable or deadly tiles, tiles are validated, do not move out of sight
            """
        direction = random.randint( 0, 3 )
        if direction == 0:
            # North, got not up to a forbidden tile
            # go not out of view
            x = int( self.enemy_rect.x / SHAPE_SIZE )
            newy = int( self.enemy_rect.y / SHAPE_SIZE - 1 )
            validpos = validate_position( newy, x, map_list, self.failneighbours )
            if validpos == False:
               pass
            else:
                if self.enemy_rect.y - SHAPE_SIZE > 0:
                    self.enemy_rect.y = self.enemy_rect.y - SHAPE_SIZE

        elif direction == 1:
            # South
            x = int( self.enemy_rect.x / SHAPE_SIZE )
            newy = int( self.enemy_rect.y / SHAPE_SIZE + 1 )
            validpos = validate_position( newy, x, map_list, self.failneighbours )
            if validpos == False:
               pass
            else:
                if self.enemy_rect.y + SHAPE_SIZE < MAX_Y_TILES*SHAPE_SIZE:
                    self.enemy_rect.y = self.enemy_rect.y + SHAPE_SIZE

        elif direction == 2:
            # West
            y = int( self.enemy_rect.y / SHAPE_SIZE )
            newx = int( self.enemy_rect.x / SHAPE_SIZE - 1 )
            validpos = validate_position( y, newx, map_list, self.failneighbours )
            if validpos == False:
               pass
            else:
                if self.enemy_rect.x - SHAPE_SIZE > 0:
                    self.enemy_rect.x = self.enemy_rect.x - SHAPE_SIZE
        elif direction == 3:
            # East
            y = int( self.enemy_rect.y / SHAPE_SIZE )
            newx = int( self.enemy_rect.x / SHAPE_SIZE + 1 )
            validpos = validate_position( y, newx, map_list, self.failneighbours )
            if validpos == False:
                pass
            else:
                if self.enemy_rect.x + SHAPE_SIZE < MAX_X_TILES*SHAPE_SIZE:
                    self.enemy_rect.x = self.enemy_rect.x + SHAPE_SIZE

    def reduce_health(self):
        """ reduces health of enemies, if health == 0, enemy will be removed from enemylist
            NOTE: Build as abstract! > enemies shall have their own health"""
        self.health = self.health - 1
        print (self.health)
        if self.health <= 0:
            enemylist.remove_enemy_from_list( self )
            self.enemy_rect.x = -1 * SHAPE_SIZE
            self.enemy_rect.y = -1 * SHAPE_SIZE
            self.dieSound.play()

    def get_rect(self):
        """ send enemy rectangle"""
        return self.enemy_rect

    def blit(self,screen):
        """ Blit the enemy
            check if A collides with this enemy, then A dies and will be buried
        """
        _avatar_rect = avatar.get_avatar_rect( )
        if self.enemy_rect.colliderect(_avatar_rect):
            avatar.set_avatar_status( True )
            grave.grave_is_scooped( )
            avatar.get_avatar_rect( ).x = -SHAPE_SIZE
            avatar.get_avatar_rect( ).y = -SHAPE_SIZE
        screen.blit( self.enemy, self.enemy_rect )

# Concrete enemy classes
# So we can have many different enemies in one list

# Note 25.06.2016
# Check implementation about configuration, so enemies will be defined als tuple
# and will be created by a global enemy-class

class BugOfDeath(Enemy):
    def __init__(self):
        self.image_enemy_source = "static/img/spider.png"
        self.image_enemy = pygame.image.load( self.image_enemy_source )
        self.failneighbours = [61, 62, 127] # For the bug forbidden fields
        self.name = "Bug of Death"
        super().__init__( self.image_enemy, self.failneighbours )
    # next sprint
    # every enemys own movement
    # def moveEnemy(self):
    #    print ("Move myself")

class SnakeOfHell(Enemy):
    def __init__(self):
        self.image_enemy_source = "static/img/snake.png"
        self.image_enemy = pygame.image.load( self.image_enemy_source )
        self.failneighbours = [1, 61, 62, 127] # For the snake forbidden fields
        self.name = "Snake of Hell"
        super().__init__( self.image_enemy, self.failneighbours )

""" Global functions """
def get_neighbours(y, x, map):
    """ get the direct neighbours of coords y, x from the map
        yes, its the 8-neighbourhood, but  we really need the 4-neighbourhood at the moment"""
    neighbours = [map[y-1][x-1], map[y-1][x], map[y-1][x+1], map[y][x-1], map[y][x], map[y][x+1], map[y+1][x-1], map[y+1][x], map[y+1][x+1]]
    return neighbours

def validate_position(y, x, map_list, failneighbours):
    """ method to validate the actual position or the position of the next move of A
        neighbous of x, y should not be elements from list failneigbours
        x, y should not be element of failneighbours, of course """
    failed = 0

    for fail in failneighbours:
        # first the actual position
        if map_list[y][x][0] == fail:
            return False
            break
        # the NOSW-neighbours
        if map_list[y-1][x][0] == fail:
            failed = failed + 1
        if y < MAX_Y_TILES:
            if map_list[y+1][x][0] == fail:
                failed = failed + 1
        if map_list[y][x-1][0] == fail:
            failed = failed + 1
        if x < MAX_X_TILES:
            if map_list[y][x+1][0] == fail:
              failed = failed + 1
    # when all neighbours in failneighbours list
    if failed == 4:
        return False
    else:
        return True

# Create objects
avatar = Avatar()
grave = Grave()
spawner = Spawner()
enemylist = EnemyList()
# this is temporary to show enemy information at the info panel
bugofdeath = BugOfDeath()
snakeofhell = SnakeOfHell()

# Images
logo = pygame.image.load( "static/img/logo.png" )
lostscreen = pygame.image.load( "static/img/lost.png" )
winscreen = pygame.image.load( "static/img/win.png" )
image1 = pygame.image.load( "static/img/water.jpg" )
image1 = pygame.transform.scale( image1, (SHAPE_SIZE, SHAPE_SIZE) )
image21 = pygame.image.load( "static/img/earth.jpg" )
image21 = pygame.transform.scale( image21, (SHAPE_SIZE, SHAPE_SIZE) )
image61 = pygame.image.load( "static/img/stone.jpg" )
image61 = pygame.transform.scale( image61, (SHAPE_SIZE, SHAPE_SIZE) )
image62 = pygame.image.load( "static/img/stone2.jpg" )
image62 = pygame.transform.scale( image62, (SHAPE_SIZE, SHAPE_SIZE) )
image127 = pygame.image.load( "static/img/lava.jpg" )
image127 = pygame.transform.scale( image127, (SHAPE_SIZE, SHAPE_SIZE) )
image128 = pygame.image.load( "static/img/meadow.jpg" )
image128 = pygame.transform.scale( image128, (SHAPE_SIZE, SHAPE_SIZE) )
image161 = pygame.image.load( "static/img/forest.jpg" )
image161 = pygame.transform.scale( image161, (SHAPE_SIZE, SHAPE_SIZE) )

# initial info about position and enemies
info_x = f.render( "Position X: {}".format( int( avatar.get_avatar_rect( ).x / SHAPE_SIZE ) ), True, Color( "black" ) )
info_y = f.render( "Position Y: {}".format( int( avatar.get_avatar_rect( ).y / SHAPE_SIZE ) ), True, Color( "black" ) )
info_map = f.render( "Type: {}".format( map_list[int( avatar.get_avatar_rect( ).y / SHAPE_SIZE)][int( avatar.get_avatar_rect( ).x / SHAPE_SIZE )][4] ), True, Color( "black" ) )
info_avatar = f.render( "Avatar:", True, Color( "black" ) )
infoavatar_life = f.render( "Avatar health: {}".format( avatar.get_life_num( ) ), True, Color( "black" ) )
info_enemies_num = f.render( "Numbers of enemies: {}".format( len( enemylist.get_enemy_list( ) ) ), True, Color( "black" ) )
#######################################################################################################
# Action
keepGoing = True
clock = pygame.time.Clock()

# Loop
while keepGoing:
    # Time
    clock.tick(30)

    # Avatar live cycle
    if avatar.get_avatar_status( ) == True:
        # A died one time
        time.sleep( 2 )
        # if A's health == 0, game is over, restart after 2 seconds
        if avatar.get_life_num( ) == 0:
            time.sleep( 2 )
            map_list = init_map_list # reset inital map -> all earth tiles will be removed
            avatar = Avatar( )
            grave = Grave( )
            spawner = Spawner( )
            enemylist = EnemyList( )
            infoavatar_life = f.render( "Avatar health: {}".format( avatar.get_life_num( ) ), True, Color( "black" ) )
        else:
            # A's reborn
            avatar.set_avatar_status( False )
            grave.set_grave_initial_position( )
            avatar.set_avatar_initial_position( )

    # A game was won, A's alive, spwaner is dead, no enemies on stage
    # restart game after 6 seconds
    if win_the_game == True:
        time.sleep( 6 )
        map_list = init_map_list # reset inital map -> all earth tiles will be removed
        avatar = Avatar( )
        grave = Grave( )
        spawner = Spawner( )
        enemylist = EnemyList( )
        infoavatar_life = f.render( "Avatar health: {}".format( avatar.get_life_num( ) ), True, Color( "black" ) )
        win_the_game = False

    # Event
    for event in pygame.event.get():
        if event.type == QUIT:
            keepGoing = False
            break
        elif event.type == KEYDOWN:
            # actual position of A
            x = int( avatar.get_avatar_rect( ).x / SHAPE_SIZE )
            y = int( avatar.get_avatar_rect( ).y / SHAPE_SIZE )
            # all neighbours of A
            neighboursofavatar = get_neighbours( y, x, map_list )

            # NOTE: check for walkable or deadly tiles should be implemented as global function in next iteration

            if event.key == K_RIGHT:
                print ("true")
                if neighboursofavatar[5][1] == 0:
                    pass # this neighbour is not walkable
                else:
                    avatar.get_avatar_rect( ).left = avatar.get_avatar_rect( ).left + SHAPE_SIZE
                    if neighboursofavatar[5][3] == 1: # A walks on deadly tile
                        grave.grave_is_scooped( )
                        avatar.get_avatar_rect( ).x = -SHAPE_SIZE
                        avatar.get_avatar_rect( ).y = -SHAPE_SIZE
                        avatar.set_avatar_status( True )
                    elif avatar.get_avatar_rect( ).left > 1728:
                        avatar.get_avatar_rect( ).left = 1728
                    avatar.set_avatar_direction( "O" )
                    paint = True;

            elif event.key == K_LEFT:
                if neighboursofavatar[3][1] == 0:
                    pass  # this neighbour is not walkable
                else:
                    avatar.get_avatar_rect( ).left = avatar.get_avatar_rect( ).left - SHAPE_SIZE
                    if neighboursofavatar[3][3] == 1: # A walks on deadly tile
                        grave.grave_is_scooped( )
                        avatar.get_avatar_rect( ).x = -SHAPE_SIZE
                        avatar.get_avatar_rect( ).y = -SHAPE_SIZE
                        avatar.set_avatar_status( True )
                    elif avatar.get_avatar_rect( ).left < 0:
                        avatar.get_avatar_rect( ).left = 0
                    avatar.set_avatar_direction( "W" )
                    paint = True;

            elif event.key == K_UP:
                if neighboursofavatar[1][1] == 0:
                    pass  # this neighbour is not walkable
                else:
                    avatar.get_avatar_rect( ).top = avatar.get_avatar_rect( ).top - SHAPE_SIZE
                    if neighboursofavatar[1][3] == 1: # A walks on deadly tile
                        grave.grave_is_scooped( )
                        avatar.get_avatar_rect( ).x = -SHAPE_SIZE
                        avatar.get_avatar_rect( ).y = -SHAPE_SIZE
                        avatar.set_avatar_status( True )
                    elif  avatar.get_avatar_rect( ).top < 0:
                        avatar.get_avatar_rect( ).top = 0
                    avatar.set_avatar_direction( "N" )
                    paint = True;

            elif event.key == K_DOWN:
                if neighboursofavatar[7][1] == 0:
                    pass  # this neighbour is not walkable
                else:
                    avatar.get_avatar_rect( ).top = avatar.get_avatar_rect( ).top + SHAPE_SIZE
                    if neighboursofavatar[7][3] == 1: # A walks on deadly tile
                        grave.grave_is_scooped( )
                        avatar.get_avatar_rect( ).x = -SHAPE_SIZE
                        avatar.get_avatar_rect( ).y = -SHAPE_SIZE
                        avatar.set_avatar_status( True )
                    elif  avatar.get_avatar_rect( ).top > 736: # Size minus menubar !!!
                        avatar.get_avatar_rect( ).top = 736
                    avatar.set_avatar_direction( "S" )
                    paint = True;

            # manipulate tiles, removable types will be setted to earth-tile
            elif event.key == K_SPACE:
                k =  pygame.key.get_pressed()
                if k[K_LEFT]:
                    x -= 1
                elif k[K_RIGHT]:
                    x += 1
                elif k[K_UP]:
                    y -= 1
                elif k[K_DOWN]:
                    y += 1
                if map_list[y][x][2] == 1:
                    map_list [y][x] = [21, 1, 0, 0, "Erde"]
            # activate shot
            elif event.key == K_s:
                avatar.shot_now( )

        elif event.type == KEYUP:
            paint = False

    # update info panel
    info_x = f.render( "Position X: {}".format( int(avatar.get_avatar_rect( ).x / SHAPE_SIZE)), True, Color( "black" ) )
    info_y = f.render( "Position Y: {}".format( int(avatar.get_avatar_rect( ).y / SHAPE_SIZE)), True, Color( "black" ) )
    info_map = f.render( "Type: {}".format( map_list[int(avatar.get_avatar_rect( ).y / SHAPE_SIZE)][int(avatar.get_avatar_rect( ).x / SHAPE_SIZE)][4] ), True, Color( "black" ) )
    infoavatar_life = f.render( "Avatar health: {}".format( avatar.get_life_num( ) ), True, Color( "black" ) )
    info_enemies_num = f.render( "Numbers of enemies: {}".format( len( enemylist.get_enemy_list( ) ) ), True, Color( "black" ) )

    # Redesign
    screen.fill((200,200,200))
    # position iterators
    b = 0
    c = 0

    for list in map_list:
        for number in list:
            pos_x = c * SHAPE_SIZE
            pos_y = b * SHAPE_SIZE
            if number[0] == 1: # Wasser
                screen.blit( image1, (pos_x, pos_y) )
            elif number[0] == 161:  # Forest
                screen.blit( image161, (pos_x, pos_y) )
            elif number[0] == 128: # Wiese
                screen.blit( image128, (pos_x, pos_y) )
            elif number[0] == 127: # Lava
                screen.blit( image127, (pos_x, pos_y) )
            elif number[0] == 61: # Stone 1
                screen.blit( image61, (pos_x, pos_y) )
            elif number[0] == 21:  # Earth
                screen.blit( image21, (pos_x, pos_y) )
            elif number[0] == 62: # Stone 2
                screen.blit( image62, (pos_x, pos_y) )
            c += 1
        c = 0
        b += 1

    # slowyfy calling spawner action
    tick += 1
    if tick > 30:
        tick = 0
        spawner.ticker()

    # call the move of all enemies, except the spawner
    enemylist.move_enemies( tick )
    # blit all objects
    enemylist.enemy_blit_list( screen )
    spawner.blit_spawner( )
    avatar.blit_avatar( )
    avatar.blit_shot( )
    grave.blit_grave( )

    # manage final screens
    if avatar.get_life_num( ) == 0:
        screen.blit( lostscreen, (0, 0) ) # game was lost
    else:
        if spawner.get_spawner_status( ) == True and len( enemylist.get_enemy_list( ) ) == 0:
            screen.blit( winscreen, (0, 0) ) # game was won
            win_the_game = True

    # blit the environment
    pygame.draw.rect( screen, (250, 250, 250), (0, 768, 1760, 200) )
    pygame.draw.rect( screen, (75, 111, 15), (0, 765, 1760, 2) )
    pygame.draw.rect( screen, (200, 200, 200), (0, 767, 1760, 2) )
    screen.blit( info_x, (20, 840) )
    screen.blit( info_y, (20, 865) )
    screen.blit( info_map, (20, 890) )
    screen.blit( info_avatar, (20, 790) )
    screen.blit( avatar.avatar_image, (100, 785) )
    screen.blit( infoavatar_life, (20, 815) )
    screen.blit( info_enemies_num, (270, 790) )
    screen.blit( bugofdeath.image_enemy, (265, 810) )
    screen.blit( snakeofhell.image_enemy, (265, 845) )
    screen.blit( spawner.image_spawner, (265, 880) )
    # temporary, not really good solved ...
    count = 0
    offset = 35
    enemylegendinit = 818
    for e in enemylist.enemy_types:
        infoEnemy = f.render( enemylist.enemy_types[count], True, Color( "black" ) )
        screen.blit( infoEnemy, (305, enemylegendinit) )
        enemylegendinit += offset
        count += 1
    screen.blit( logo, (1618, 780) )
    # done ...
    pygame.display.update()