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
SMILESIZE = 60  # How big the Smilee is.
DIGSIZE = 30    # How big the diggable spots are.
MONEYSIZE = 20  # How big the money is.

MOVERATE = Vector( 15, 9 ) # How fast the player moves in the x and y direction.
FLOATMOVERATE = Vector( 5, 3 ) # How fast things move when floating.
BOUNCERATE = 6       # How fast the player bounces (large is slower).
FLOATRATE = 16       # How fast things float (like bouncing).
BOUNCEHEIGHT = 10    # How high the player bounces.
FLOATHEIGHT = 20     # How high things float (like bouncing).




class JimmyPixel( game.Game ):
    def __init__( self, viewPort ):
        # Set up generic game one time set up.
        game.Game.__init__( self, 'Jimmy Pixel', 'Jimmy Pixel Right', viewPort )

        # Game one time setup.
        self.setDrawOrder( 'Border', 'BackGround', 'Digspot', 'GhostSprite', 'Sprite', 'Player', 'Fog' )
        self.setCursor()
        viewPort.loadMusic( 'Dungeon of Pixels.mp3' )
        viewPort.setCameraMovementStyle( game_dynamics.KeyMovementStyle( moveRate=Vector( 20, 12 ) ) )


    def loadImages( self ):
        images = self.images
        images.load( 'Dungeon of Pixels Map' )
        images.load( 'Dungeon of Pixels Boundary' )
        images.load( 'Jimmy Pixel Right', 'RL' )
        images.load( 'Jimmy Pixel Right Walk', 'RL' )
        images.load( 'Derangatang Right', 'RL' )
        images.load( 'Smilee Right', 'RL' )
        images.load( 'Darkness' )
        images.load( 'Diggable Spot' )
        #images.load( 'Coin' )


    # Per game initialisation.
    def init( self ):
        self.winMode = False           # If the player has won.
        self.invulnerableMode = False  # If the player is invulnerable.
        self.invulnerableStartTime = 0 # Time the player became invulnerable.
        self.gameOverMode = False      # If the player has lost.
        self.gameOverStartTime = 0     # Time the player lost.
        self.moneyScore = 0
        self.cameraMovement = False

        game.Game.init( self )


    def initMap( self ):
        viewPort = self.viewPort
        gameMap = self.gameMap
        images = self.images

        gameMap.setImageStore( images )

        gameMap.createScene( 'Dungeon of Pixels Map', BACKGROUND_COLOUR )
        gameMap.addObject( Border( ORIGIN, images.Dungeon_of_Pixels_Boundary, size=2000, name='Dungeon of Pixels Border' ) )
        gameMap.addObject( BackGround( ORIGIN, images.Dungeon_of_Pixels_Map, size=2000, name='Dungeon of Pixels' ) )

        self.player = self.createPlayer()
        gameMap.addObject( self.player )

        # Attach to the player and position relative to the player, so that it follows the player around.
        self.darkness = Fog( ORIGIN, images.Darkness, size=4000, name='Darkness', positionStyle='relative_centre', visible=False )
        self.player.attachObject( self.darkness )

        # Start off with some diggable spots on the screen.
        self.createDigspots( gameMap, 20 )

        # Start off with some derangatangs on the screen.
        gameMap.addObject( self.createDerangatang() )
        gameMap.addObject( self.createDerangatang() )
        smilee = self.createSmilee()
        # smilee.toggleMovement()
        gameMap.addObject( smilee )


    def createPlayer( self ):
        viewPort = self.viewPort
        images = self.images
        # How big the player starts off.
        playerStartPos = Point( viewPort.halfWidth, viewPort.halfHeight )

        # Sets up the movement style of the player.
        # playerBounds = game_dynamics.RectangleBoundary( Rectangle( Point( 0, 220 ), Point( 900, 550 ) ) )
        playerBounds = game_dynamics.CollisionBoundary()
        moveStyle = game_dynamics.KeyMovementStyle( boundaryStyle=playerBounds )
        moveStyle.setMoveRate( MOVERATE )
        moveStyle.setBounceRates( BOUNCERATE, BOUNCEHEIGHT )

        return Player( playerStartPos, moveStyle, size=JIMSIZE, ratio=1.0, imageL=images.Jimmy_Pixel_RightL, imageR=images.Jimmy_Pixel_RightR, name='Jimmy Pixel', positionStyle='centre' )


    def createDigspots( self, gameMap, num ):
        for ii in range( num ):
            pos = Point( random.randint( -WINWIDTH, WINWIDTH * 2 ), random.randint( -WINHEIGHT, WINHEIGHT * 2 ) )
            dig = Digspot( pos, self.images.Diggable_Spot, size=DIGSIZE, name='Digspot' )
            gameMap.addObject( dig )


    def createCoin( self ):
        pos = Point( random.randint( 0, 20 ), random.randint( 0, 20 ) )
        coin = Coin( pos, self.images.Coin, size=MONEYSIZE, positionStyle='relative_centre' )

        return coin


    def createDerangatang( self ):
        viewPort = self.viewPort
        images = self.images
        random.seed( time.clock() )
        derangatangStartPos = Point( viewPort.halfWidth, viewPort.halfHeight ) + Point( random.randint( -100, 100 ), random.randint( -100, 100 ) )
        # derangatangStartPos = Point( viewPort.halfWidth, viewPort.halfHeight )

        derangatangBounds = game_dynamics.CollisionBoundary()
        moveStyle = game_dynamics.RandomWalkMovementStyle( boundaryStyle=derangatangBounds )
        moveStyle.setMoveRate( MOVERATE )
        moveStyle.setBounceRates( BOUNCERATE, BOUNCEHEIGHT )

        derangatang = Sprite( derangatangStartPos, moveStyle, size=DERSIZE, ratio=1.0, imageL=images.Derangatang_RightL, imageR=images.Derangatang_RightR, name='Derangatang' )
        # Only collide with the map.
        # derangatang.setCollisionMask( InteractionType.IMPERVIOUS )

        return derangatang


    def createSmilee( self ):
        viewPort = self.viewPort
        images = self.images
        random.seed( time.clock() )
        smileeStartPos = Point( viewPort.halfWidth, viewPort.halfHeight ) + Point( random.randint( -100, 100 ), random.randint( -100, 100 ) )

        smileeBounds = game_dynamics.CollisionBoundary()
        moveStyle = game_dynamics.RandomWalkMovementStyle( boundaryStyle=smileeBounds )
        moveStyle.setMoveRate( FLOATMOVERATE )
        moveStyle.setBounceRates( FLOATRATE, FLOATHEIGHT )

        smilee = GhostSprite( smileeStartPos, moveStyle, size=SMILESIZE, ratio=1.0, imageL=images.Smilee_RightL, imageR=images.Smilee_RightR, name='Smilee' )

        return smilee


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


    def dig( self, digSpot, pos ):
        viewPort = self.viewPort
        gameMap = self.gameMap
        player = gameMap.player

        print "Checking if we're close enough to dig..."
        playerPos = player.pos
        diggingDistance = playerPos.manhattanDistance( pos )
        print "Digging distance %d" % diggingDistance

        if diggingDistance < 120:
            print( "Digging..." )
            viewPort.playSound( 'Dig' )
            digSpot.digCount += 1

            if digSpot.digCount >= 3:
                # Do something.
                # Dug up some treasure!
                # player.attachObject( self.createCoin() )
                digSpot.delete()


    def processEvent( self, event ):
        game.Game.processEvent( self, event )

        viewPort = self.viewPort
        gameMap = self.gameMap
        player = gameMap.player

        if event.type == KEYDOWN:
            if event.key == K_r and self.winMode:
                # Reset the game once you've won.
                self.running = False
            elif event.key == K_f:
                self.darkness.toggleVisibility()
            elif event.key == K_v:
               backgrounds = gameMap.objectsOfType( 'BackGround' )
               backgrounds[0].toggleVisibility()
            elif event.key == K_b:
               backgrounds = gameMap.objectsOfType( 'BackGround' )
               backgrounds[0].toggleEnabled()
            elif K_c == event.key:
                player.stopMovement()
                self.cameraMovement = True

            if self.cameraMovement:
                viewPort.setCameraMovement( key=event.key )
            else:
                # Check if the key moves the player in a given direction.
                player.setMovement( key=event.key )
        elif event.type == KEYUP:
            if K_c == event.key:
                self.cameraMovement = False
                viewPort.stopCameraMovement()

            if self.cameraMovement:
                viewPort.stopCameraMovement( key=event.key )
            else:
                # Check if the key stops the player in a given direction.
                player.stopMovement( key=event.key )
        # elif event.type == MOUSEBUTTONUP:
        #     digSpots = gameMap.objectsOfType( 'Digspot' )
        #
        #     print "Checking if we're close enough to dig..."
        #     clickPos = viewPort.getWorldCoordinate( self.clickPos )
        #     playerPos = player.pos
        #     diggingDistance = playerPos.manhattanDistance( clickPos )
        #     print "Digging distance %d" % diggingDistance
        #
        #     for dig in digSpots:
        #         # Does the click point collide with a colour that is not the background colour.
        #         # if viewPort.collisionOfPoint( self.clickPos, dig ):
        #         # Does the click point collide with the dig spot's rectangle.
        #
        #         if diggingDistance < 120 and dig.collidesWithPoint( clickPos, True ):
        #             viewPort.playSound( 'Dig' )
        #             print( "Digging..." )
        #             dig.digCount += 1
        #
        #             if dig.digCount >= 3:
        #                 # Do something.
        #                 # Dug up some treasure!
        #                 # player.attachObject( self.createCoin() )
        #                 dig.delete()
        elif event.type == INTERACTION_EVENT:
            # print "Interaction event %s <-> %s" % ( event.obj1, event.obj2 )

            if event.obj1.isInteractionTypePair( event.obj2, 'Player', 'GhostSprite=Smilee' ):
                print "Interacted with Smilee"
                viewPort.playSound( 'Smilee Laugh', checkBusy=True )
        elif event.type == COLLISION_EVENT:
            # print "Collision event %s <-> %s" % ( event.obj1, event.obj2 )

            if event.obj1.isInteractionTypePair( event.obj2, 'Player', 'Sprite=Derangatang' ):
                print "Collided with Derangatang"
                viewPort.playSound( 'Derangatang Screech', checkBusy=True )
        elif event.type == CLICK_COLLISION_EVENT:
            print "Click collision event %s <-> %s" % ( event.obj, event.pos )

            if event.obj.name == 'Digspot':
                self.dig( event.obj, viewPort.getWorldCoordinate( self.clickPos ) )


    def updateState( self ):
        game.Game.updateState( self )

        if self.gameOverMode:
            return

        viewPort = self.viewPort
        gameMap = self.gameMap
        player = gameMap.player

        # Adjust camera if beyond the "camera slack".
        if self.cameraMovement:
            viewPort.moveCamera()
        else:
            playerCentre = player.getCentre()
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
