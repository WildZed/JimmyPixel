import random, sys, time, math, pygame
from pygame.locals import *
# Use common stuff from CandySeller until we've moved it into a Lib directory.

sys.path.append( '../GameEngine' )

from geometry import *
import viewport, game, game_map, game_dynamics
from game_objects import *
from game_constants import *

WINWIDTH = 800  # Width of the program's window, in pixels.
WINHEIGHT = 600 # Height in pixels.

BACKGROUND_COLOUR = ( 135, 178, 142 )

JIMSIZE = 60    # How big Jimmy is.
DERSIZE = 50    # How big the Derangatang is.
CGSIZE = 100    # How big the Cat Girl is.
DIGSIZE = 30    # How big the diggable spots are.

MOVERATE = Vector( 17, 10 ) # How fast the player moves in the x and y direction.
BOUNCERATE = 6       # How fast the player bounces (large is slower).
BOUNCEHEIGHT = 10    # How high the player bounces.




class JimmyPixel( game.Game ):
    def __init__( self, viewPort ):
        self.images = self.loadImages()

        # Set up generic game one time set up.
        game.Game.__init__( self, 'Jimmy Pixel', 'Jimmy Pixel Right.png', viewPort )

        # Game one time setup.
        self.setDrawOrder( 'BackGround', 'Fog', 'Sprite', 'Digspot', 'Player')
        # This tells the game update which object types need to move with the camera.
        # This makes objects stay put with respect to the world coordinates.
        self.setCameraUpdates( 'BackGround', 'Fog', 'Sprite', 'Digspot' )
        self.setCursor()
        viewPort.loadMusic( 'Dungeon of Pixels.mp3' )


    # Per game initialisation.
    def init( self ):
        game.Game.init( self )

        self.winMode = False           # If the player has won.
        self.invulnerableMode = False  # If the player is invulnerable.
        self.invulnerableStartTime = 0 # Time the player became invulnerable.
        self.gameOverMode = False      # If the player has lost.
        self.gameOverStartTime = 0     # Time the player lost.
        self.moneyScore = 0
        self.gameMap = self.createMap()


    def loadImages( self ):
        images = game_map.ImageStore()
        images.load( 'Jimmy Pixel Right', 'RL' )
        images.load( 'Jimmy Pixel Right Walk', 'RL' )
        images.load( 'Derangatang Right', 'RL' )
        images.load( 'Hannah the Cat Girl', 'RL' )
        images.load( 'Dungeon of Pixels Map' )
        images.load( 'Darkness' )
        images.load( 'Diggable Spot' )

        return images


    def createMap( self ):
        viewPort = self.viewPort
        gameMap = game_map.Map()
        images = self.images

        gameMap.setImageStore( images )

        gameMap.createScene( 'Dungeon of Pixels Map', BACKGROUND_COLOUR )
        gameMap.addObject( BackGround( ORIGIN, images.Dungeon_of_Pixels_Map, size=2000, name='Dungeon of Pixels' ) )

        self.player = self.createPlayer()
        gameMap.addPlayer( self.player )

        # Attach to the player and position relative to the player, so that it follows the player around.
        self.darkness = Fog( ORIGIN, images.Darkness, size=2000, name='Darkness', positionStyle='relative_centre' )
        self.player.attachObject( self.darkness )

        # Start off with some diggable spots on the screen.
        self.createDigspots( gameMap, 2 )

        # Start off with some derangatangs on the screen.
        gameMap.addSprite( self.createDerangatang() )
        gameMap.addSprite( self.createDerangatang() )
        gameMap.addSprite( self.createCatGirl() )
        #gameMap.addSprite( self.createDerangatang() )

        return gameMap


    def createPlayer( self ):
        viewPort = self.viewPort
        images = self.images
        # How big the player starts off.
        playerStartPos = Point( viewPort.halfWidth, viewPort.halfHeight )

        # Sets up the movement style of the player.
        # playerBounds = game_dynamics.RectangleBoundary( Rectangle( Point( 0, 220 ), Point( 900, 550 ) ) )
        playerBounds = game_dynamics.CollisionBoundary( viewPort )
        moveStyle = game_dynamics.KeyMovementStyle( boundaryStyle=playerBounds )
        moveStyle.setMoveRate( MOVERATE )
        moveStyle.setBounceRates( BOUNCERATE, BOUNCEHEIGHT )

        return Player( playerStartPos, moveStyle, size=JIMSIZE, ratio=1.0, imageL=images.Jimmy_Pixel_RightL, imageR=images.Jimmy_Pixel_RightR, name='Jimmy Pixel', positionStyle='centre' )


    def createDigspots( self, gameMap, num ):
        for ii in range( num ):
            pos = Point( random.randint( 0, WINWIDTH ), random.randint( 400, 500 ) )
            dig = Digspot( pos, self.images.Diggable_Spot, size=DIGSIZE, name='Digspot' )
            gameMap.addObject( dig )


    def createDerangatang( self ):
        viewPort = self.viewPort
        images = self.images
        random.seed( time.clock() )
        derangatangStartPos = Point( viewPort.halfWidth, viewPort.halfHeight ) + Point( random.randint( -100, 100 ), random.randint( -100, 100 ) )

        derangatangBounds = game_dynamics.CollisionBoundary( viewPort )
        moveStyle = game_dynamics.RandomWalkMovementStyle( boundaryStyle=derangatangBounds )
        moveStyle.setMoveRate( MOVERATE )
        moveStyle.setBounceRates( BOUNCERATE, BOUNCEHEIGHT )

        derangatang = Sprite( derangatangStartPos, moveStyle, size=DERSIZE, ratio=1.0, imageL=images.Derangatang_RightL, imageR=images.Derangatang_RightR, name='Derangatang' )
        # Only collide with the map.
        # derangatang.setCollisionMask( InteractionType.IMPERVIOUS )

        return derangatang


    def createCatGirl( self ):
        viewPort = self.viewPort
        images = self.images
        random.seed( time.clock() )
        catGirlStartPos = Point( viewPort.halfWidth, viewPort.halfHeight ) + Point( random.randint( -100, 100 ), random.randint( -100, 100 ) )

        catGirlBounds = game_dynamics.CollisionBoundary( viewPort )
        moveStyle = game_dynamics.RandomWalkMovementStyle( boundaryStyle=catGirlBounds )
        moveStyle.setMoveRate( MOVERATE )
        moveStyle.setBounceRates( BOUNCERATE, BOUNCEHEIGHT )

        catGirl = Sprite( catGirlStartPos, moveStyle, size=CGSIZE, ratio=1.0, imageL=images.Hannah_the_Cat_GirlL, imageR=images.Hannah_the_Cat_GirlR, name='Hannah' )
        # Only collide with the map.
        # derangatang.setCollisionMask( InteractionType.IMPERVIOUS )

        return catGirl


    def setCursor( self ):
        thickarrow_strings = (               # Sized 24x24.
            "   XX                   ",
            "  X..X                  ",
            "  X..X                  ",
            "  X..X                  ",
            "  X..X                  ",
            "  X..X                  ",
            "  X..X                  ",
            "  X..X                  ",
            "  X..X                  ",
            "  X..X                  ",
            "XXXXXXXX                ",
            "XXXXXXXX                ",
            "   XX                   ",
            "   XX                   ",
            "  X..X                  ",
            "  X..X                  ",
            "   XX                   ",
            "                        ",
            "                        ",
            "                        ",
            "                        ",
            "                        ",
            "                        ",
            "                        ")
        datatuple, masktuple = pygame.cursors.compile( thickarrow_strings,
                                      black='X', white='.', xor='o' )
        pygame.mouse.set_cursor( (24,24), (0,0), datatuple, masktuple )


    def processEvent( self, event ):
        game.Game.processEvent( self, event )

        viewPort = self.viewPort
        gameMap = self.gameMap
        player = gameMap.player

        if event.type == KEYDOWN:
            # Check if the key moves the player in a given direction.
            player.setMovement( event.key )

            if event.key == K_r and self.winMode:
                # Reset the game once you've won.
                self.running = False
            elif event.key == K_f:
                self.darkness.toggleVisibility()
        elif event.type == KEYUP:
            # Check if the key stops the player in a given direction.
            player.stopMovement( event.key )
        elif event.type == MOUSEBUTTONUP:
            digSpots = gameMap.objectsOfType( 'Digspot' )

            for dig in digSpots:
                # Does the click point collide with a colour that is not the background colour.
                # if viewPort.collisionOfPoint( self.clickPos, dig ):
                # Does the click point collide with the dig spot's rectangle.
                if dig.collidesWithPoint( self.clickPos, True ):
                    viewPort.playSound( 'Dig' )
                    print( "Digging..." )
                    dig.digCount += 1

                    if dig.digCount >= 3:
                        # Do something.
                        dig.delete()


    def updateState( self ):
        game.Game.updateState( self )

        if self.gameOverMode:
            return

        viewPort = self.viewPort
        gameMap = self.gameMap
        player = gameMap.player

        # Move the player according to the movement instructions.
        player.move()

        # Adjust camera if beyond the "camera slack".
        playerCentre = player.getCentre()
        # Point( player.x + int( ( float( player.size ) + 0.5 ) / 2 ), player.y + int( ( float( player.size ) + 0.5 ) / 2 ) )
        viewPort.adjustCamera( playerCentre )


    # Update the positions of all the map objects according to the camera and new positions.
    def updateMap( self ):
        # Update the generic map stuff.
        game.Game.updateMap( self )

        viewPort = self.viewPort
        gameMap = self.gameMap
        player = gameMap.player

        # Update the player.
        player.update( viewPort.camera, gameOverMode=self.gameOverMode, invulnerableMode=self.invulnerableMode )


    def run( self ):
        self.viewPort.playMusic( loops=-1 )
        game.Game.run( self )




def main():
    viewPort = viewport.ViewPort( WINWIDTH, WINHEIGHT )
    game = JimmyPixel( viewPort )

    while True:
        game.run()
        # Re-initialised the game state.
        game.reset()


if __name__ == '__main__':
    main()
