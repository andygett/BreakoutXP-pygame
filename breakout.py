import sys, pygame, random, datetime
import numpy as np
import breakodb
#import breakodb, eventlog

colors = pygame.color.THECOLORS
black = 0, 0, 0
white = (255, 255, 255)
blue = (80, 80, 255)
orange = (255, 153, 51)
darkOrange = (102,51, 0)
darkRed = (120, 0, 0)

class Brick(pygame.sprite.Sprite):
  width = 80
  height = 30
  def __init__(self, row, col):
    super().__init__()
    topColor = colors["yellow"]
    bottomColor = colors["red4"]
#    topColor = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255) )
#    bottomColor = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255) )
    self.image = pygame.Surface([Brick.width, Brick.height])
#    self.image.fill(Brick.color)
    self.image.fill(fadeColor(bottomColor, topColor, row / Wall.numRows))
    self.rect = self.image.get_rect()
    self.rect.x = Brick.width * col
    self.rect.y = Wall.topGap + Brick.height * row
    self.powerUps=[]

class Game(object):
  numLives = 3
  fps = 120
  fSpeed = 4
  size = width, height = Brick.width * 12, 840
  version = "1.3" 

  def __init__(self):
    self.db = breakodb.Db()
    eventTypes = self.db.getEventDict()
#    self.events=eventlog.Events(eventTypes)
    self.events=Events(eventTypes)

    self.users=self.db.getUsers()
    self.userIndex = 0 
    self.idUser = self.users[self.userIndex][0]
    self.userName=self.users[self.userIndex][1]
    self.idSession = self.db.newSession(self.idUser)

    pygame.init()
    pygame.mouse.set_visible(0)
    self.screen = pygame.display.set_mode(Game.size)
    self.bgColor = colors["gray10"]
    pygame.display.set_caption('Break Out, go ahead and give it to me')
    self.fontHuge = pygame.font.Font(pygame.font.get_default_font(), 24)
    self.fontLarge = pygame.font.Font(pygame.font.get_default_font(), 20)
    self.font = pygame.font.Font(pygame.font.get_default_font(), 14)
    self.fontSmall = pygame.font.Font(pygame.font.get_default_font(), 9)
    self.clock = pygame.time.Clock()

    self.levelThreshhold = 1
  #  gFont = pygame.freetype.Font("Comic Sans MS", 24)
#    text_surface = font.render('Hello world', antialias=True, color=(255, 0, 0))

  def updateProgressBar(self):
    top=2
    percent = (self.totalBricks - len(self.bricks)) / (self.hitThisManyBricksForNextLevel + 1)
    barWidth = self.paddle.rect.width * percent
    progressDone = self.paddle.image.subsurface((0,top,barWidth,2))
    progressDone.fill(fadeColor(self.paddle.color, colors["navy"], percent))
  
  # returns true if still alive
  def updateLives(self, delta=0):
    self.lives += delta
    if self.lives < 1 and not self.newGameWait:
      self.endGame()
      self.events.clear()
      self.idGame = 0
      self.newGameWait = True
      self.waitList.add(4*1000, self.newGame)
      return False
    size = 3
    pad = 4
    top = 6
    b = self.paddle.image.subsurface((0, top, self.paddle.rect.width, size))
    b.fill(self.paddle.color)
    for v in range(self.lives - 1):
      x = pad + v*(size+pad)
      if (x + size < self.paddle.rect.width):
        b = self.paddle.image.subsurface((x,top,size,size))
        b.fill(fadeColor(self.paddle.color, colors["gray15"], 0))
    return True

  def endGame(self):
      self.db.saveEvents(self.idGame, self.events.details)
      self.db.endGame(self.idGame, self.level)

  def newGame(self):
    self.events.gameCache = {}
    self.idGame = self.db.newGame(self.idSession)
    self.lives = Game.numLives
    self.level = 1
    self.newLevel()

  def newLevel(self):
    self.allsprites = pygame.sprite.Group()
    self.bricks = pygame.sprite.Group()
    self.balls = pygame.sprite.Group()
    self.powerUps = pygame.sprite.Group()
    self.paddle = Paddle()
    self.allsprites.add(self.paddle)
    self.updateLives()
    self.waitList = WaitList()
    Wall.render()
    self.totalBricks = len(self.bricks)
    self.hitThisManyBricksForNextLevel = self.totalBricks*self.levelThreshhold
    self.initPowerUps()
    self.addBall()
    self.newGameWait = False

  def delayNewLevel(self):
    self.level += 1
    for b in self.balls:
      b.fSpeed = 0.5
      b.alive = False
    game.waitList.add(3 * 1000, game.newLevel)

  def run(self):
    self.newGame()
    runMode="r"
    pauseStart = 0
    while runMode != "q":
      self.clock.tick(Game.fps)
      for event in pygame.event.get():
        if event.type == pygame.QUIT: 
          runMode="q"
        elif event.type == pygame.KEYDOWN:
          if event.key == pygame.K_ESCAPE:
            runMode="q"
          if event.key == pygame.K_RETURN:
            if runMode=="r":
              pauseStart = pygame.time.get_ticks()
              runMode="s"
            else:
              self.waitList.addPauseDuration(pygame.time.get_ticks() - pauseStart)
              for b in self.balls:
                b.waitList.addPauseDuration(pygame.time.get_ticks() - pauseStart)
              runMode="r"
          
      self.showUserLevelOnClearScreen()
      if runMode == "r":
        self.runGame()
      elif runMode=="s":
        self.showStats()
      pygame.display.flip()

    #self.db.endGame(self.idGame, self.level)
    self.endGame()
    self.db.endSession(self.idSession)
    pygame.quit()
    sys.exit()

  def showStats(self):
    s = "Version %s. © 2021 Stoic the Vast. All rights reserved. Any retransmission or rebroadcast of this game is strictly encouraged. Your mileage may vary. Similarities to real life are purely coincidental." % Game.version
    self.renderData(s, (4, game.height - 20), 
        colors["peachpuff3"])
    self.renderData(game.events.gameCache, heading="Game Stats")
    self.renderData(game.db.getUserStats(self.idUser), (200, 50), heading="User Stats")

  def showUserLevelOnClearScreen(self):
    self.screen.fill(self.bgColor)
    s = self.userName + " Level "  + str(self.level)
    self.renderText(s, (0,0), self.fontHuge, colors["orangered"])

  def renderData(self, data, dest=(50, 50), color=colors["peachpuff"], 
        font=None, heading=None ):
    #tRect = pygame.Rect(Game.width/4, Game.height/4, Game.width/2, Game.height/2)
    padding = 4
    colWidth = 120
    if font is None:
      font = self.font
    if type(data) is str:
      self.renderText(data, dest, font, color)
    elif type(data) is dict:
      numCols = 2
#      colWidth = (game.width - 100) / numCols
      curTop = dest[1]
      if heading is not None:
        rect = self.renderText(heading, (dest[0] + padding, curTop), 
            self.fontLarge, color)
        curTop += rect.bottom + padding

      for k, v in data.items():
        self.renderText(k, (dest[0], curTop), font, color)
        rect = self.renderText(str(v), (dest[0] + colWidth, curTop), 
            font, color)
        curTop += rect.bottom + padding

    elif type(data) is list:
      curTop = dest[1]
      if heading is not None:
        rect = self.renderText(heading, (dest[0] + padding, curTop), 
            self.fontLarge, color)
        curTop += rect.bottom + padding

      for i in range(len(data)):
        self.renderText(data[i][0], (dest[0], curTop), font, color)
        rect = self.renderText(str(data[i][1]), (dest[0] + colWidth, curTop), 
            font, color)
        curTop += rect.bottom + padding


  def renderText(self, s, dest, font, color):
    tSurface = font.render(s, True, color, self.bgColor)
    self.screen.blit(tSurface, dest=dest)
    return tSurface.get_rect()

  def runGame(self):
    self.paddle.handle_keys()
    self.balls.update()
    self.powerUps.update()
    self.waitList.process()

    self.allsprites.draw(self.screen)
    pygame.display.flip()

    
  def addBall(self):
    ball = Ball()
    self.allsprites.add(ball)
    self.balls.add(ball)
    return ball

  def addBallRandomSpeed(self):
    ball = self.addBall()
    ball.fSpeed = random.random()*4 + 1

  def initPowerUps(self):
    for b in range(0, len(self.bricks)):
      brick=self.bricks.sprites()[b]
      r = random.random()
      if r > 0.99:
        brick.powerUps.append(PUpExtraLife(brick))
      elif r > 0.8:
        brick.powerUps.append(PUpMultiBall(brick))
      elif r > 0.6:
        brick.powerUps.append(PUpSlowMo(brick))
      elif r > 0.2:
        brick.powerUps.append(PUpWiderPaddle(brick))


class WaitList:
  def __init__(self):
    self.items = []

  def add(self, delay, action):
    self.items.append([pygame.time.get_ticks()+delay, action])

  def process(self):
    sliced = []
    for i in self.items:
      if pygame.time.get_ticks() > i[0]:
        i[1]()
      else:
        sliced.append(i)
    self.items = sliced

  def addPauseDuration(self, duration):
    for i in self.items:
      i[0] += duration

class Paddle(pygame.sprite.Sprite):
  hover = 40
  def __init__(self):
    # Call the parent's constructor
    super().__init__()
    self.width = 80
    self.height = 10
    self.color = colors["gray89"]

    # pygame.rect.Rect((width/2, height - 40, self.width, 10))
    self.image = pygame.Surface([self.width, self.height])
    self.image.fill(self.color)
    self.rect = self.image.get_rect()
    self.rect.x = Game.width/2
    self.rect.y = Game.height-self.height - Paddle.hover

  def handle_keys(self):
    keys = pygame.key.get_pressed()
    move=keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
    self.rect.move_ip(Game.fSpeed * 2 * (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]), 0)
    if self.rect.left < 0:
      self.rect.left = 0
    if self.rect.right  >  Game.width:
      self.rect.right = Game.width
    if game.newGameWait:
      if keys[pygame.K_SPACE]:
        game.newGame()

  def changeWidth(self, delta):
    self.width += delta
    self.image = pygame.Surface([self.width, self.height])
    self.image.fill(self.color)
    oldRect = self.rect
    self.rect = self.image.get_rect()
    self.rect.x = oldRect.x
    self.rect.y = oldRect.y
    game.updateProgressBar()
    game.updateLives()


def fadeColor(startColor, endColor, percent):
  #color=startColor + (np.array(endColor) - np.array(startColor)) * percent
  if percent > 1:
    percent = 1
  return endColor + (np.array(startColor) - np.array(endColor)) * percent

class Ball(pygame.sprite.Sprite):
  color=colors["gold"]
  #deadColor = colors["darkred"]
  deadColor = colors["red4"]
  size = 8
  deathDelay = 2.5 * 1000
  
  def __init__(self):
    super().__init__()
    self.image = pygame.Surface([Ball.size, Ball.size])
    self.image.fill(Ball.color)
    self.rect = self.image.get_rect()
    self.x = random.random() * Game.width - 1
#    self.y=1.0 * Wall.bottom()
    self.y=Wall.bottom()
#    self.rect.y = Wall.bottom()
    self.fSpeed=Game.fSpeed
    self.speed=[1,1]
    self.alive=True
    self.killTime = 0
    game.events.add("NewBall")
    self.waitList = WaitList()


  def move(self):
    self.x += self.speed[0]*self.fSpeed
    self.rect.x = self.x
    self.y += self.speed[1]*self.fSpeed
    self.rect.y = self.y
    if self.rect.right > Game.width:
      game.events.add("ScreenBorderHit")
      self.rect.right = Game.width
      self.speed[0] = -1
    elif self.rect.left < 0:
      game.events.add("ScreenBorderHit")
      self.rect.left = 0
      self.speed[0] = 1
    if self.rect.top < 0:
      game.events.add("ScreenBorderHit")
      self.rect.top = 0
      self.speed[1] = 1
    if self.rect.bottom > Game.height:
      self.rect.bottom = Game.height
      self.y = self.rect.bottom - Ball.size
      self.speed[1] = 0
      self.image.fill(darkRed)

  def checkDeath(self):
    if self.rect.top > game.paddle.rect.bottom:
      if self.alive:
        game.events.add("DeadBall")
        #self.speed[1] = -1
        self.fSpeed = 0.5
        self.killTime = pygame.time.get_ticks() + Ball.deathDelay
        self.alive=False
      percent = (Game.height - self.rect.bottom) / (Game.height - game.paddle.rect.bottom)
      self.image.fill(fadeColor(Ball.color, Ball.deadColor, percent))
      if pygame.time.get_ticks() > self.killTime:
        #balls.remove(self)
        #allsprites.remove(self)
        self.kill()
        if len(game.balls) < 1:
          if game.updateLives(-1):
            game.addBall()

  def hitTheBricks(self):
    deadBricks = pygame.sprite.spritecollide(self, game.bricks, True)
    if len(deadBricks) > 0:
      for brick in deadBricks:
        game.events.add("BrickBounce")
        for powerUp in brick.powerUps:
          game.allsprites.add(powerUp)
          game.powerUps.add(powerUp)

      self.bounce()
      if len(game.bricks) <= int(game.totalBricks - game.hitThisManyBricksForNextLevel):
        game.delayNewLevel()
      else:
        game.updateProgressBar()

  def hitPaddle(self):
    # Bounce if ball hits  paddle
    if  pygame.sprite.collide_rect(self, game.paddle):
      self.y = game.paddle.rect.top - Ball.size
      self.bounce()
      game.events.add("PaddleHit")


  def update(self):
    self.move()
    self.checkDeath()
    self.hitTheBricks()
    self.hitPaddle()
    self.waitList.process()
    
  def bounce(self):
    self.speed[1] = -self.speed[1]

  def changeSpeed(self, delta):
    if (self.alive):
      speed  = self.fSpeed + delta
#      print (datetime.datetime.now(), id(self), str(self.fSpeed), delta, speed, "alive")
      if speed > 0.7:
        self.fSpeed = speed
        return True
#    else:
#      print (datetime.datetime.now(), id(self), str(self.fSpeed), delta, "dead")
    return False

  def delayChangeSpeed(self, delay, delta):
    self.waitList.add(delay, lambda: self.changeSpeed(delta))


class Wall(object):
  topGap=100
  numRows=5
  @staticmethod
  def render():
    for row in range(Wall.numRows):
      for col in range(int(Game.width/Brick.width)):
        brick = Brick(row, col)
        game.bricks.add(brick)
        game.allsprites.add(brick)        
  @staticmethod
  def bottom():
    return Wall.topGap + Wall.numRows*Brick.height

class Events():
  def __init__(self, evDict):
    self.evDict = evDict
    self.clear()
    self.gameCache = {}

  def clear(self):
    self.details=[]    

  def add(self, eventName):
    idEvent = self.evDict[eventName][0]
    dbTime = datetime.datetime.now(datetime.timezone.utc).isoformat()[:23]
    self.details.append((idEvent, dbTime))
    self.gameCache[eventName] = self.gameCache.get(eventName, 0) + 1

class PowerUp(pygame.sprite.Sprite):
#  size = 8
  width = Brick.width
  height = 2 * Brick.height

  deathDelay = 2.5 * 1000

  def __init__(self, brick):
    super().__init__()
    self.image = pygame.Surface([PowerUp.width, PowerUp.height])
    self.startColor=self.getStartColor()
    self.deadColor = colors["darkorange4"]
    self.getImage()
    self.rect = self.image.get_rect()
    self.rect.x = brick.rect.x
    self.y = brick.rect.y

    self.fSpeed=Game.fSpeed/4
    self.speed=[0,1]
    self.alive=True
#    self.killTime = 0
    self.powerUpDuration = 10 * 1000

  def getImage(self):
    self.image.fill(self.startColor)

  def getStartColor(self):
    return colors["orange"]

  def move(self):
    self.y += self.speed[1]*self.fSpeed
    self.rect.y = self.y
    if self.rect.top > Game.height:
      self.kill()

  def checkDeath(self):
    pBottom = game.paddle.rect.bottom
    if self.rect.top > pBottom:
      if self.alive:
        self.addMissedPupEvent()
        self.fSpeed /= 4
#        self.killTime = pygame.time.get_ticks() + Ball.deathDelay # maybe game.delay?
        self.alive=False
      factor = 1 - (self.rect.top - pBottom)/(Game.height - pBottom)
      self.image = pygame.transform.scale(self.image,(
        int(Ball.size + 72*factor), int(Ball.size + 52*factor)))

  def addMissedPupEvent(self):
    evName = self.getMissedEventName()
    if evName != "None":
      game.events.add(evName)

  def getMissedEventName(self):
    return "None"

  def hitPaddle(self):
    if  pygame.sprite.collide_rect(self, game.paddle):
      #self.y = paddle.rect.top - Ball.size
      self.activate()
      self.kill()

  def update(self):
    self.move()
    self.hitPaddle()
    self.checkDeath()
    
  def activate(self):
    pass

class PUpWiderPaddle(PowerUp):
  def __init__(self, brick):
    super().__init__(brick)
#    self.image.fill(self.startColor)

  def getImage(self):
    self.image = pygame.image.load("img/PowerupBoxWiden.png")
#    self.image = pygame.image.load("BreakoutImages/PowerupImages/PowerupBoxWiden.png")
    self.image = pygame.transform.scale(self.image,(PowerUp.width, PowerUp.height))

  def getStartColor(self):
      return colors["papayawhip"]

  def activate(self):
#      for b in game.balls:
#        sDelta = -3
#        if b.changeSpeed(sDelta):
#          b.delayChangeSpeed(self.powerUpDuration, -sDelta)
#        b.waitList.add(self.powerUpDuration, lambda : b.changeSpeed(-sDelta) )

#      self.activateNormal()

#  def activateNormal(self):
      game.paddle.changeWidth(20)
#      game.waitList.add(self.powerUpDuration, game.paddle.changeWidth(-20))
      game.waitList.add(self.powerUpDuration, lambda :game.paddle.changeWidth(-20))

class PUpMultiBall(PowerUp):
  min = 3
  max = 5
  def __init__(self, brick):
    super().__init__(brick)
  #  self.image.fill(self.startColor)
  
  def activate(self):
    game.events.add("MultiBall")
    delay = 1 * 1000
#    game.addBall()
    game.addBallRandomSpeed()
    for b in range(1, random.randint(PUpMultiBall.min, PUpMultiBall.max)):
      game.waitList.add(delay*b, game.addBallRandomSpeed)

  def getImage(self):
    self.image = pygame.image.load("img/PowerupBoxMultiBall.png")
    self.image = pygame.transform.scale(self.image,(PowerUp.width, PowerUp.height))

  def getStartColor(self):
      return colors["goldenrod"]

  def getMissedEventName(self):
     return "MultiBallMiss"

class PUpExtraLife(PowerUp):
  def __init__(self, brick):
    super().__init__(brick)


  def getImage(self):
    self.image = pygame.image.load("img/PowerupBox1UP.png")
#    self.image = pygame.image.load("BreakoutImages/PowerupImages/PowerupBox1UP.png")
    self.image = pygame.transform.scale(self.image,(PowerUp.width, PowerUp.height))

  def getStartColor(self):
      return colors["cyan2"]

  def activate(self):
    game.updateLives(1)

class PUpSlowMo(PowerUp):
  def __init__(self, brick):
    super().__init__(brick)

  def getStartColor(self):
      return colors["plum3"]

  def activate(self):
      for b in game.balls:
#        sDelta = -3
        sDelta = 0.1 - random.random()*2
        if b.changeSpeed(sDelta):
          b.delayChangeSpeed(self.powerUpDuration, -sDelta)


game=Game()
game.run()
