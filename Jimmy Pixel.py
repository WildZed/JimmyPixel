import random, sys, time, math, pygame
from pygame.locals import *
# Use common stuff from CandySeller until we've moved it into a Lib directory.

# With the portals there needs to be an animation where the portal key shakes and creates a portal.

sys.path.append( '../GameEngine' )

from geometry import *
import viewport, game
import game_map as gm
import game_dynamics as gd
import game_objects as go
import game_constants as gc


WINWIDTH = 800  # Width of the program's window, in pixels.
WINHEIGHT = 600 # Height in pixels.

BACKGROUND_COLOUR = ( 135, 178, 142 )

JIMSIZE = 60    # How big Jimmy is.
DERSIZE = 50    # How big the Derangatang is.
SMILESIZE = 60  # How big the Smilee is.
DIGSIZE = 30    # How big the diggable spots are.
MONEYSIZE = 20  # How big the money is.
CAVESIZE = 70   # How big the cave is.

MOVERATE = Vector( 12, 12 ) # How fast the player moves in the x and y direction.
FLOATMOVERATE = Vector( 6, 6 ) # How fast things move when floating.
BOUNCERATE = 6       # How fast the player bounces (large is slower).
FLOATRATE = 16       # How fast things float (like bouncing).
BOUNCEHEIGHT = 10    # How high the player bounces.
FLOATHEIGHT = 20     # How high things float (like bouncing).




class JimmyPixel( game.Game ):
    def __init__( self, viewPort ):
        # Set up generic game one time set up.
        super().__init__( 'Jimmy Pixel', 'Jimmy Pixel Right', viewPort )

        # Game one time setup.
        # self.setDrawOrder( 'Border', 'BackGround', 'Digspot', 'GhostSprite', 'Sprite', 'Player', 'Fog' )
        self.setCursor()
        self.setAllowDrag()
        viewPort.loadMusic( 'Dungeon of Pixels.mp3' )
        viewPort.setCameraMovementStyle( gd.KeyMovementStyle( moveRate=Vector( 20, 20 ) ) )
        viewPort.setCameraSlack( 90 )


    def loadImages( self ):
        images = self.images
        images.load( 'Dungeon of Pixels Map' )
        images.load( 'Treasure Cave' )
        images.load( 'Dungeon of Pixels Boundary' )
        images.load( 'Jimmy Pixel Right', 'RL' )
        images.load( 'Jimmy Pixel Right Walk', 'RL' )
        images.load( 'Derangatang Right', 'RL' )
        images.load( 'Smilee Right', 'RL' )
        images.load( 'Darkness' )
        images.load( 'Diggable Spot' )
        images.load( 'Portal' )
        images.load( 'Coin' )


    # Per game initialisation.
    def init( self ):
        self.winMode = False           # If the player has won.
        self.invulnerableMode = False  # If the player is invulnerable.
        self.invulnerableStartTime = 0 # Time the player became invulnerable.
        self.gameOverMode = False      # If the player has lost.
        self.gameOverStartTime = 0     # Time the player lost.
        self.moneyScore = 0

        game.Game.init( self )


    def initMap( self ):
        viewPort = self.viewPort
        gameMap = self.gameMap
        images = self.images

        gameMap.setImageStore( images )

        gameMap.createScene( 'Dungeon of Pixels Map', backGroundColour=BACKGROUND_COLOUR )
        gameMap.addObject( go.Border( ORIGIN, images.Dungeon_of_Pixels_Boundary, size=2000, name='Dungeon of Pixels Border', positionStyle='top_left' ) )
        gameMap.addObject( go.BackGround( ORIGIN, images.Dungeon_of_Pixels_Map, size=2000, name='Dungeon of Pixels', positionStyle='top_left' ) )

        self.player = self.createPlayer()
        gameMap.addObject( self.player )

        # Attach to the player and position relative to the player, so that it follows the player around.
        self.darkness = go.Fog( ORIGIN, images.Darkness, size=800, name='Darkness', visible=False )
        self.player.attachObject( self.darkness )

        # Start off with some diggable spots on the screen.
        self.createDigspots( gameMap, 20 )

        portalCave1 = go.Portal( Point( 1680, 1480 ), images.Portal, size=( JIMSIZE ), name='portalcave1' )
        gameMap.addObject( portalCave1 )

        treasureCave1 = go.SoftBackGround( ORIGIN, images.Treasure_Cave, size=( WINWIDTH / 2 ) )
        treasureCave1Rect = treasureCave1.getRect()
        treasureCave1Bounds = gd.RectangleBoundary( treasureCave1Rect, grow=-40 )
        gameMap.createScene( 'Treasure Cave 1', backGroundColour=BACKGROUND_COLOUR, boundaryStyle=treasureCave1Bounds )
        gameMap.changeScene( 'Treasure Cave 1' )
        gameMap.addObject( treasureCave1 )
        portalDungeon1 = go.Portal( ORIGIN, images.Portal, size=( JIMSIZE ), name='portaldungeon1' )
        gameMap.addObject( portalDungeon1 )

        gameMap.changeScene( 'Dungeon of Pixels Map' )

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
        # playerBounds = gd.RectangleBoundary( Rectangle( Point( 0, 220 ), Point( 900, 550 ) ) )
        playerBounds = gd.CollisionBoundary()
        moveStyle = gd.KeyMovementStyle( boundaryStyle=playerBounds )
        moveStyle.setMoveRate( MOVERATE )
        moveStyle.setBounceRates( BOUNCERATE, BOUNCEHEIGHT )
        leftImages = go.ImageAnimation( [ images.Jimmy_Pixel_RightL, images.Jimmy_Pixel_Right_WalkL ] )
        rightImages = go.ImageAnimation( [ images.Jimmy_Pixel_RightR, images.Jimmy_Pixel_Right_WalkR ] )
        collisionSpec = go.CollisionSpecification( width=0.38, left=0.32 )

        return go.Player( playerStartPos, moveStyle, size=JIMSIZE, ratio=1.0, imageL=leftImages, imageR=rightImages, name='Jimmy Pixel', collisionSpecification=collisionSpec )


    def createDigspots( self, gameMap, num ):
        for ii in range( num ):
            pos = Point( random.randint( -WINWIDTH, WINWIDTH * 2 ), random.randint( -WINHEIGHT, WINHEIGHT * 2 ) )
            dig = go.Digspot( pos, self.images.Diggable_Spot, size=DIGSIZE, name='Digspot' )
            gameMap.addObject( dig )


    def createCoin( self ):
        pos = Point( random.randint( 0, 20 ), random.randint( 0, 20 ) )
        coin = go.Coin( pos, self.images.Coin, size=MONEYSIZE )

        return coin


    def createDerangatang( self ):
        viewPort = self.viewPort
        images = self.images
        random.seed( time.clock() )
        derangatangStartPos = Point( viewPort.halfWidth, viewPort.halfHeight ) + Point( random.randint( -100, 100 ), random.randint( -100, 100 ) )
        # derangatangStartPos = Point( viewPort.halfWidth, viewPort.halfHeight )

        derangatangBounds = gd.CollisionBoundary()
        moveStyle = gd.RandomWalkMovementStyle( boundaryStyle=derangatangBounds )
        moveStyle.setMoveRate( MOVERATE )
        moveStyle.setBounceRates( BOUNCERATE, BOUNCEHEIGHT )

        derangatang = go.Sprite( derangatangStartPos, moveStyle, size=DERSIZE, ratio=1.0, imageL=images.Derangatang_RightL, imageR=images.Derangatang_RightR, name='Derangatang' )
        # Only collide with the map.
        # derangatang.setCollisionMask( InteractionType.IMPERVIOUS )

        return derangatang


    def createSmilee( self ):
        viewPort = self.viewPort
        images = self.images
        random.seed( time.clock() )
        smileeStartPos = Point( viewPort.halfWidth, viewPort.halfHeight ) + Point( random.randint( -100, 100 ), random.randint( -100, 100 ) )

        smileeBounds = gd.CollisionBoundary()
        moveStyle = gd.RandomWalkMovementStyle( boundaryStyle=smileeBounds )
        moveStyle.setMoveRate( FLOATMOVERATE )
        moveStyle.setBounceRates( FLOATRATE, FLOATHEIGHT )

        smilee = go.GhostSprite( smileeStartPos, moveStyle, size=SMILESIZE, ratio=1.0, imageL=images.Smilee_RightL, imageR=images.Smilee_RightR, name='Smilee' )

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

        print( "Checking if we're close enough to dig..." )
        playerPos = player.pos
        diggingDistance = playerPos.manhattanDistance( pos )
        print( "Digging distance %d" % diggingDistance )

        if diggingDistance < 120:
            print( "Digging..." )
            viewPort.playSound( 'Dig' )
            digSpot.digCount += 1

            if digSpot.digCount >= 3:
                # Do something.
                # Dug up some treasure!
                player.attachObject( self.createCoin() )
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
                backgrounds = gameMap.objectsOfType( go.BackGround )

                if backgrounds:
                    backgrounds[0].toggleVisibility()
            elif event.key == K_b:
                backgrounds = gameMap.objectsOfType( go.BackGround )

                if backgrounds:
                    backgrounds[0].toggleEnabled()
        elif event.type == gc.INTERACTION_EVENT:
            # print( "Interaction event %s <-> %s" % ( event.obj1, event.obj2 ) )

            if event.obj1.isInteractionTypePair( event.obj2, 'Player', 'GhostSprite=Smilee' ):
                # print( "Interacted with Smilee" )
                viewPort.playSound( 'Smilee Laugh', checkBusy=True )
        elif event.type == gc.COLLISION_EVENT:
            # print( "Collision event %s <-> %s" % ( event.obj1, event.obj2 ) )

            if event.obj1.isInteractionTypePair( event.obj2, 'Player', 'Sprite=Derangatang' ):
                # print( "Collided with Derangatang" )
                viewPort.playSound( 'Derangatang Screech', checkBusy=True )
            elif event.obj1.isInteractionTypePair( event.obj2, 'Player', 'Portal=portalcave1' ):
                self.movePlayerToScene( event.obj1, event.obj2, 'Treasure Cave 1', 'portaldungeon1' )
            elif event.obj1.isInteractionTypePair( event.obj2, 'Player', 'Portal=portaldungeon1' ):
                self.movePlayerToScene( event.obj1, event.obj2, 'Dungeon of Pixels Map', 'portalcave1' )
            elif event.obj1.isInteractionTypePair( event.obj2, 'Sprite=Derangatang', 'Portal=portalcave1' ):
                self.moveSpriteToScene( event.obj1, event.obj2, 'Treasure Cave 1', 'portaldungeon1' )
            elif event.obj1.isInteractionTypePair( event.obj2, 'Sprite=Derangatang', 'Portal=portaldungeon1' ):
                self.moveSpriteToScene( event.obj1, event.obj2, 'Dungeon of Pixels Map', 'portalcave1' )
        elif event.type == gc.CLICK_COLLISION_EVENT:
            # print( 'Click collision event:', event )
            if event.obj.name == 'Digspot':
                self.dig( event.obj, viewPort.getWorldCoordinate( self.clickPos ) )


    def updateState( self ):
        game.Game.updateState( self )

        if self.gameOverMode:
            return


    # Update the positions of all the map objects according to the camera and new positions.
    def updateMap( self ):
        # Update the generic map stuff.
        game.Game.updateMap( self )

        viewPort = self.viewPort
        gameMap = self.gameMap
        player = gameMap.player

        # Update the player (again) with the extra info..
        player.update( viewPort.camera, gameOverMode=self.gameOverMode, invulnerableMode=self.invulnerableMode )


    def run( self ):
        self.viewPort.playMusic( loops=-1 )
        game.Game.run( self )




def main():
    print( "Starting Jimmy Pixel..." )
    viewPort = viewport.ViewPort( WINWIDTH, WINHEIGHT, topLeft=Point( 400, 80 ) )
    game = JimmyPixel( viewPort )
    print( "Created Jimmy Pixel game..." )

    while True:
        game.run()
        # Re-initialised the game state.
        game.reset()


if __name__ == '__main__':
    main()
