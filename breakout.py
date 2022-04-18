import sys, pygame, random, datetime
import numpy as np, math
import breakodb

colors = pygame.color.THECOLORS
#black = 0, 0, 0
#white = (255, 255, 255)
#blue = (80, 80, 255)
#orange = (255, 153, 51)
#darkOrange = (102,51, 0)
#darkRed = (120, 0, 0)

class Brick(pygame.sprite.Sprite):
  width = 80
  height = 30

  targetFadeDuration = 1.5 * 1000
  fadeIterations = 50
  iterationDuration = targetFadeDuration / fadeIterations

  def __init__(self, row, col):
    super().__init__()
#    topColor = colors["palegreen"]
#    bottomColor = colors["turquoise4"]
    self.image = pygame.Surface([Brick.width, Brick.height])
#    self.image.fill(Brick.color)
    topColor = self.getTopColor()
    bottomColor = self.getBottomColor()
#    if row == 1 and col == 1:
#      print (game.level, topColor, bottomColor)
    self.color = fadeColor(topColor, bottomColor, row / Wall.numRows)
    self.image.fill(self.color)
    self.rect = self.image.get_rect()
    self.rect.x = Brick.width * col
    self.rect.y = Wall.topGap + Brick.height * row
    self.powerUps=[]
    self.waitList = WaitList()
#    self.fadeByFactor = lambda factor: lambda: self.image.fill(fadeColor(self.color, game.bgColor, factor))
    self.fadeByFactor = lambda startColor, endColor, factor: lambda: self.image.fill(fadeColor(startColor, endColor, factor))

  def update(self):
    self.waitList.process()

# some 4-digit prime numbers for seeding:
# 1009 1013 1019 1021 1031 1033 1039 1049 1051 1061 1063 1069 1087 1091 1093 1097 1103 1109 1117 1123 1129 1151 1153 1163 1171 1181 1187 1193 1201 1213 1217 1223 1229 1231 1237 1249 1259 1277 1279 1283 1289 1291 1297 1301 1303 1307 1319 1321 1327 1361 1367 1373 1381 1399 1409 1423 1427 1429 1433 1439 1447 1451 1453 1459
  def getTopColor(self):
    varColor = (game.level * 1229) % 256
    satCat = game.level % 6
    if satCat == 0:
      return 255, varColor, 0, 255
    if satCat == 1:
      return 0, varColor, 255, 255
    if satCat == 2:
      return varColor, 255, 0, 255    # green
    if satCat == 3:
      return varColor, 0, 255, 255
    if satCat == 4:
      return 255, 0, varColor, 255
    if satCat == 5:
      return 0, 255, varColor, 255

  def getBottomColor(self):
    varColor = (game.level * 1013) % 256
    satCat = game.level % 6
    if satCat == 0:
      return 0, varColor, 128, 255
    if satCat == 1:
      return varColor, 128, 0, 255
    if satCat == 2:
      return 0, 128, varColor, 255
    if satCat == 3:
      return 128, varColor, 0, 255    # green
    if satCat == 4:
      return 128, 0, varColor, 255   # purplish
    if satCat == 5:
      return varColor, 0, 128, 255   # purplish

  
  def delayShowBrick(self, duration):
    self.image.fill(game.bgColor)
    game.waitList.add(duration, lambda: game.allsprites.add(self))
    #fic = lambda factor: lambda: self.fadeInColor(2*factor/100)
#    fic = lambda factor: self.fadeInColor(2*factor/100)
#    self.fic = lambda factor: lambda: self.image.fill(fadeColor(self.color, game.bgColor, factor))
    
    for i in range(Brick.fadeIterations):
      self.waitList.add(duration + i*Brick.iterationDuration, 
          self.fadeByFactor(game.bgColor, self.color, 2*i/100))

    return duration + Brick.targetFadeDuration

#    for i in range(51):
#      self.waitList.add(duration + i*10, self.fadeByFactor(2*i/100))

 # def fadeInColor(self, factor):
    #oldrect = self.rect
    #print ("fade ticks: ", pygame.time.get_ticks(), round(factor,3))
#    self.image.fill(fadeColor(self.color, game.bgColor, factor))
    #self.rect = self.image.get_rect()
    #self.rect = oldrect
  def delayGlow(self, delay, duration=0.4*1000):
#    glowColor = colors["goldenrod1"]
    glowColor = colors["lemonchiffon"]
    maxGlow = 0.4
    iterationDuration = (game.fps / 1000) / 4

    iterationDuration = 0.02 * 1000
    iterations = round(duration / iterationDuration)
#    iterations = 20
    a=0
    for i in range(iterations+1):
      fadeFactor = 1 - maxGlow + maxGlow*i/iterations
      self.waitList.add(delay + i*iterationDuration,
          self.fadeByFactor(glowColor, self.color, 
          fadeFactor))
#          i/iterations))
#          maxGlow*iterations + maxGlow*i/iterations))

    pass

class Game(object):
  XP_EVENT = 10
  XP_LEVEL = 4000
  numLives = 3
  fps = 120
  fSpeed = 4
  size = width, height = Brick.width * 12, 840
  version = "1.7"

  def __init__(self, idUser):
    self.db = breakodb.Db()
    eventTypes = self.db.getEventDict()
    self.events=Events(eventTypes)

    if idUser:
      self.users=self.db.getUser(idUser)
    else:
      self.users=self.db.getUsers()

    self.userIndex = 0 
    self.idUser = self.users[self.userIndex][0]
    self.userName=self.users[self.userIndex][1]
    
    self.idSession = self.db.newSession(self.idUser)

    pygame.init()
    pygame.mouse.set_visible(0)
    self.screen = pygame.display.set_mode(Game.size)
    image = pygame.image.load("img/PowerupBoxMultiBall.png")
    image = pygame.transform.scale(image,(32, 32))
    pygame.display.set_icon(image)

    self.bgColor = colors["gray10"]
    pygame.display.set_caption('Break Out, go ahead and give it to me')
    self.fontHuge = pygame.font.Font(pygame.font.get_default_font(), 24)
    self.fontLarge = pygame.font.Font(pygame.font.get_default_font(), 20)
#    self.font = pygame.font.Font(pygame.font.get_default_font(), 14)  # ugly numbers
#    self.fontSmall = pygame.font.Font(pygame.font.get_default_font(), 9)

#    self.fontHuge = pygame.font.SysFont("Arial", 24)
#    self.fontLarge = pygame.font.SysFont("Arial", 20)
#    self.font = pygame.font.SysFont("SegoeUI", 14)
    self.font = pygame.font.SysFont("calibri", 14)
    self.fontSmall = pygame.font.SysFont("SegoeUI", 9)

    self.clock = pygame.time.Clock()
    self.pupSpawnRates = PowerUps.setSpawnFactors()
    self.levelThreshold = 0.9
    #self.levelThreshold = 0.03
  #  gFont = pygame.freetype.Font("Comic Sans MS", 24)
#    text_surface = font.render('Hello world', antialias=True, color=(255, 0, 0))

  def updateProgressBar(self):
    top=2
    percent = (self.totalBricks - 
        len(self.bricks)) / (self.hitThisManyBricksForNextLevel + 1)
    if percent>1:
      percent=1
    barWidth = self.paddle.rect.width * percent
    progressDone = self.paddle.image.subsurface((0,top,barWidth,2))
    progressDone.fill(fadeColor(self.paddle.color, colors["navy"], percent))
  
  # returns true if still alive
  def updateLives(self, delta=0):
    self.lives += delta
    if self.lives < 1 and not self.newGameWait:
      self.endGame(self.events.evDict["NoLives"][0])
      self.idGame = 0
      self.newGameWait = True
      # self.waitList.add(4*1000, self.newGame)
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
        b.fill(fadeColor(self.paddle.color, colors["gray15"], 50))
    return True

  def endGame(self, endTrigger):
#      self.db.saveEvents(self.idGame, self.events.details)
      self.endLevel()
      self.db.endGame(self.idGame, self.level, endTrigger)

  def newGame(self):
    self.setXP()
    self.events.gameCache = {}
    self.idGame = self.db.newGame(self.idSession, self.events.evDict["AbnormalEnd"][0])
    self.lives = Game.numLives
    self.level = 0
#    self.level = random.randint(1, 50)
    self.newLevel()

  def setXP(self):
    careerEvents = game.db.getUserStats(self.idUser)
    evCount = 0
    for i in range(len(careerEvents)):
      evCount += int(careerEvents[i][1])
    self.xpDict = self.db.getXPDict(self.idUser)
    self.xp = (
      1000 * self.xpDict["Sessions"] 
      + 2000 * self.xpDict["Games"] 
      + game.XP_LEVEL * self.xpDict["Levels"]
      + game.XP_EVENT * evCount
    )

  def newLevel(self):
    self.level += 1
    self.xp += game.XP_LEVEL
    self.events.levelCache = {}
    self.idLevel = self.db.newLevel(self.idGame, self.level)
    self.levelPauseDuration = 0
    self.maxBalls = 1

    self.allsprites = pygame.sprite.Group()
    self.bricks = pygame.sprite.Group()
    self.balls = pygame.sprite.Group()
    self.powerUps = pygame.sprite.Group()
    self.paddle = Paddle()
    self.allsprites.add(self.paddle)
    self.updateLives()
    self.waitList = WaitList()
    self.totalBricks = Wall.render()
    #self.totalBricks = len(self.bricks)
    self.hitThisManyBricksForNextLevel = int(self.totalBricks*self.levelThreshold)
    #self.initPowerUps()
    game.waitList.add(1000, self.addBall)
    self.newGameWait = False
    self.invinciBalls = False
    self.grantLife()

  def delayNewLevel(self):
    for b in self.balls:
      b.fSpeed = 0.5
      b.alive = False
    game.waitList.add(3 * 1000, game.newLevel)
    self.endLevel()

  def endLevel(self):
      self.db.endLevel(self.idLevel, self.maxBalls,
          int(self.levelPauseDuration / 1000 + 0.5))
      self.db.saveEvents(self.idLevel, self.events.details)
      self.events.clear()

  def run(self):
    self.newGame()
    runMode="r"
    self.pauseStart = 0
    mouseVisibleKill = 0
    while runMode != "q":
      self.clock.tick(Game.fps)
      if pygame.time.get_ticks() > mouseVisibleKill:
        pygame.mouse.set_visible(0)
        mouseVisibleKill = 0
      for event in pygame.event.get():
        if event.type == pygame.MOUSEMOTION:
          pygame.mouse.set_visible(1)
          mouseVisibleKill = pygame.time.get_ticks()+3*1000
        if event.type == pygame.QUIT: 
          if runMode=="s":
            self.endPause()
          runMode="q"
        elif event.type == pygame.KEYDOWN:
          if event.key == pygame.K_ESCAPE:
            if runMode=="s" and not self.newGameWait:
              self.endPause()
            self.newGameWait = False
            runMode="q"
          if event.key == pygame.K_u:
            #self.level += 1
            game.newLevel()
          if event.key == pygame.K_d:
            self.level -= 2
            game.newLevel()
          if event.key == pygame.K_RETURN:
            if self.newGameWait:
              runMode="r"
              self.newGame()
            else:
              if runMode=="r":
                self.pauseStart = pygame.time.get_ticks()
                runMode="s"
                game.events.add("StartPause")
              else:
                self.endPause()
                runMode="r"

      self.showUserLevelOnClearScreen()
      if self.newGameWait:
        runMode = "s"
      if runMode == "r":
        self.runGame()
      elif runMode=="s":
        self.showStats()
      pygame.display.flip()

    self.endGame(self.events.evDict["UserQuit"][0])
    self.db.endSession(self.idSession)
#    pygame.quit()
#    sys.exit()

  def endPause(self):
    pauseDuration = pygame.time.get_ticks() - self.pauseStart
    self.waitList.addPauseDuration(pauseDuration)
    game.events.add("EndPause")
    for b in self.balls:
      b.waitList.addPauseDuration(pauseDuration)
    self.levelPauseDuration += pauseDuration

  def showStats(self):
    userStatsSurf = pygame.Surface([200, Game.height - 150])
    userStatsSurf.fill(self.bgColor)
    gameStatsSurf = userStatsSurf.copy()
    levelStatsSurf = userStatsSurf.copy()

    gameWaitTop = self.renderData(game.xpDict, userStatsSurf, heading="User Stats")
    gameWaitTop = self.renderData(game.db.getUserStats(self.idUser), 
        userStatsSurf, top=gameWaitTop+15)
    
#    gameWaitTop = self.renderData(game.db.getUserStats(self.idUser), 
#        userStatsSurf, heading="User Stats")
#    gameWaitTop = self.renderData(game.xpDict, userStatsSurf, top=gameWaitTop+15)
    
    self.screen.blit(userStatsSurf, (50,50))
    self.showGameStats(gameStatsSurf)
    self.showLevelStats(levelStatsSurf)

    if self.newGameWait:
      self.renderText("Game Over.  Press Enter for new game, Esc to quit",
         self.screen, gameWaitTop + 70, self.fontHuge, colors["orangered"] )

    s = "Version %s. © 2021 Rado Shaq Enterprises. All rights reserved. Any retransmission or rebroadcast of this game is strictly encouraged. Your mileage may vary. Similarities to real life are purely coincidental." % Game.version
    self.renderText(s, self.screen, game.height - 20, 
        self.fontSmall, colors["peachpuff3"] )

  def showGameStats(self, gameSurf):
    curTop = self.renderData(game.events.gameCache, gameSurf, heading="Game Stats")
    # TODO: show sysStats via flag set by hotkey?
    sysStats = [
      ["Frames per second", self.fps],
      ["Speed factor", self.fSpeed],
      ["Bricks needed threshold", self.levelThreshold],
    ]
    curTop = self.renderData(sysStats, gameSurf, curTop + 40, font=self.fontSmall)
    curTop = self.renderData(self.pupSpawnRates, gameSurf, curTop, font=self.fontSmall)
    self.screen.blit(gameSurf, (50+225,50))

  def showLevelStats(self, levelSurf):
    curTop = self.renderData(game.events.levelCache, levelSurf, 
        heading="Level " + str(self.level) + " Stats")
    levelStats=[
      ["Bricks remaning", len(self.bricks)],
      ["Bricks to hit", self.hitThisManyBricksForNextLevel + len(self.bricks) 
        - self.totalBricks],
      ["Balls in Play", len(self.balls)],
      ["Maximum Balls", self.maxBalls],
    ]
    curTop = self.renderData(levelStats, levelSurf, curTop)
    self.screen.blit(levelSurf, (50+225*2,50))
    return curTop

  def showUserLevelOnClearScreen(self):
    self.screen.fill(self.bgColor)
    s = self.userName + " Level "  + str(self.level)
    userColor = colors["cadetblue2"]
    self.renderText(s, self.screen, 0, self.fontHuge, userColor)
    self.renderText("XP: " + str(self.xp), self.screen, 0, self.fontLarge, 
        userColor, rightJustify=True)

  def renderData(self, data, destSurf=None, top=None, color=colors["peachpuff"], 
        font=None, heading=None ):
    padding = 4
    if font is None:
      font = self.font
    if destSurf==None:
      destSurf = self.screen
    if top==None:
      top=0
    curTop = top
    if heading is not None:
      rect = self.renderText(heading, destSurf, top, self.fontLarge, color)
      curTop += rect.height + padding
    if type(data) is str:
      self.renderText(data, destSurf, top, font, color)
    elif type(data) is list:
      for i in range(len(data)):
        self.renderText(data[i][0], destSurf, curTop, font, color)
        rect = self.renderText(str(data[i][1]), destSurf,  curTop,
            font, color, rightJustify=True)
        curTop += rect.height + padding
    elif type(data) is dict:
      for k, v in data.items():
        self.renderText(k, destSurf, curTop, font, color)
        rect = self.renderText(str(v), destSurf, curTop, font, color, rightJustify=True)
        curTop += rect.bottom + padding
    return curTop

  def renderText(self, s, destSurf, top, font, color, rightJustify=False):
    tSurface = font.render(s, True, color, self.bgColor)
    tRect = tSurface.get_rect()
    if rightJustify:
      tRect.right = destSurf.get_rect().right
    else:
      tRect.x = destSurf.get_rect().x
    tRect.y = top
    destSurf.blit(tSurface, tRect)
    return tSurface.get_rect()

  def runGame(self):
    self.paddle.handle_keys()
    self.balls.update()
    self.powerUps.update()
    self.bricks.update()
    self.waitList.process()

    self.allsprites.draw(self.screen)
    pygame.display.flip()

  def addBall(self, fSpeed=None):
    ball = Ball(fSpeed)
    self.allsprites.add(ball)
    self.balls.add(ball)
    self.maxBalls = max(self.maxBalls, len(self.balls))
    return ball

  def addBallRandomSpeed(self):
    ball = self.addBall(random.random()*4 + 1)

  def grantLife(self):
    if self.level > 0:
      if random.random() < 0.2 + 1/(self.level+1):
          delay = Ball.deathDelay + (random.random()*4.5 + 0.5)*1000
          game.waitList.add(delay-0.5*1000, Wall.sunsetGlow)
          game.waitList.add(delay, 
              lambda: PowerUps.spawn(globals()["PUpExtraLife"]))

    pass

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
  minWidth = 30
  def __init__(self):
    # Call the parent's constructor
    super().__init__()
    self.width = 80
    self.height = 10
    self.color = colors["gray89"]

    self.image = pygame.Surface([self.width, self.height])
    self.image.fill(self.color)
    self.rect = self.image.get_rect()
    self.rect.x = Game.width/2
    self.rect.y = Game.height-self.height - Paddle.hover

  def handle_keys(self):
    keys = pygame.key.get_pressed()
    # move=keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
    self.rect.move_ip(Game.fSpeed * 2 * (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]), 0)
    if self.rect.left < 0:
      self.rect.left = 0
    if self.rect.right  >  Game.width:
      self.rect.right = Game.width
    if game.newGameWait:
      if keys[pygame.K_SPACE]:
        game.newGame()

  def changeWidth(self, delta):
    newWidth = self.width + delta
    if newWidth < Paddle.minWidth:
      return False
    self.width = newWidth
    self.image = pygame.Surface([self.width, self.height])
    self.image.fill(self.color)
    oldRect = self.rect
    self.rect = self.image.get_rect()
    self.rect.x = oldRect.x
    self.rect.y = oldRect.y
    game.updateProgressBar()
    game.updateLives()
    return True


def fadeColor(startColor, endColor, factor):
  #color=startColor + (np.array(endColor) - np.array(startColor)) * percent
  if factor > 1:
    factor = 1
#  return endColor + (np.array(startColor) - np.array(endColor)) * factor
  return startColor + (np.array(endColor) - np.array(startColor)) * factor

class Ball(pygame.sprite.Sprite):
  color=colors["gold"]
  bigColor=colors["yellow1"]
  deadColor = colors["red4"]
  size = 8
  deathDelay = 2.5 * 1000
  
  def __init__(self, fSpeedx=None):
    super().__init__()
    self.size = Ball.size
    self.image = pygame.Surface([self.size, self.size])
    self.image.fill(Ball.color)
    self.rect = self.image.get_rect()
    self.x = random.random() * Game.width - 1
    self.y=Wall.bottom()
    if fSpeedx is None:
      self.fSpeed=Game.fSpeed
    else:
      self.fSpeed=fSpeedx
    self.speed=[1,1]
    self.alive=True
    self.killTime = 0
    game.events.add("NewBall")
    self.waitList = WaitList()
    self.fireBall = False
    self.bigBall = False
    self.highBall = False

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
      self.y = self.rect.bottom - self.size
      self.speed[1] = 0
      self.image.fill(colors["darkred"])

  def checkDeath(self):
    if self.rect.top > game.paddle.rect.bottom:
      if self.alive:
        if game.invinciBalls:
          self.bounce()
        else:
          game.events.add("DeadBall")
          self.fSpeed = 0.5
          self.killTime = pygame.time.get_ticks() + Ball.deathDelay
          self.alive=False
      if not self.alive:
        percent = (Game.height - self.rect.bottom) / (Game.height - game.paddle.rect.bottom)
        self.image.fill(fadeColor(Ball.deadColor, Ball.color, percent))
        if pygame.time.get_ticks() > self.killTime:
          self.kill()
          if len(game.balls) < 1:
            if game.updateLives(-1):
              game.addBall()
              game.grantLife()

  def hitTheBricks(self):
    if self.highBall and self.speed[1]<0:
      return

    deadBricks = pygame.sprite.spritecollide(self, game.bricks, True)
    if len(deadBricks) > 0:
      Wall.brickExplosion(deadBricks[0])
      for brick in deadBricks:
        game.events.add("BrickBounce")
        PowerUps.spawnRandom(brick.rect.x, brick.rect.y)

      if not self.fireBall:
        self.bounce()
      if len(game.bricks) <= int(game.totalBricks - game.hitThisManyBricksForNextLevel):
        game.delayNewLevel()
      else:
        game.updateProgressBar()

  def hitPaddle(self):
    # Bounce if ball hits  paddle
    if  pygame.sprite.collide_rect(self, game.paddle):
      self.y = game.paddle.rect.top - self.size
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
      if speed > 0.7:
        self.fSpeed = speed
        return True
    return False

  def delayChangeSpeed(self, delay, delta):
    self.waitList.add(delay, lambda: self.changeSpeed(delta))

  def delayEndFireBall(self, delay):
    self.waitList.add(delay, self.endFireBall)

  def endFireBall(self):
    self.fireBall = False
    self.image.fill(Ball.color)

  def delayEndHighBall(self, delay):
    self.waitList.add(delay, self.endHighBall)

  def endHighBall(self):
    self.highBall = False
    self.image.fill(Ball.color)

  def changeSize(self, delta):
    self.size += delta
    self.image = pygame.Surface([self.size, self.size])
    color = Ball.color
    if self.size != Ball.size:
      color = Ball.bigColor
    self.image.fill(color)
    oldRect = self.rect
    self.rect = self.image.get_rect()
    self.rect.x = oldRect.x
    self.rect.y = oldRect.y

  def delayEndBigBall(self, delay, delta):
    self.waitList.add(delay, lambda: self.endBigBall(delta))

  def endBigBall(self, delta):
    self.changeSize(delta)
    self.color = Ball.color
    self.bigBall = False
    pass

class Wall(object):
  topGap=100
  #numRows=2
  numRows=5
  targetRenderDuration = 1.5 * 1000

  @staticmethod
  def render():
    #def typeWriter(): return delayXX + dRandom.staggerDelay 
    def typeWriter(): 
      bDelay = (row*Wall.targetRenderDuration/Wall.numRows 
        + Wall.targetRenderDuration * ((len(game.bricks)-1)%dRandom.groupSize) 
        * dRandom.groups /totalBricks)
#      print (n, bDelay)
      return bDelay
    def reverseTypeWriter():
      return (totalBricks -len(game.bricks)) * dRandom.r*0.04 * 1000
    def marchColumnsAcrossSmooth(): return col * colDelay
    def marchColumnsAcross(): return random.random() * colDelay + col * colDelay
#    def randomFill(): return random.random() * 25 * delayIncrement 
#    def randomFill(): return random.random() * dRandom.r * Wall.targetRenderDuration / totalBricks
    def randomFill(): return random.random() * Wall.targetRenderDuration / totalBricks
    def marchDownSmooth(): return row * rowDelay
    def marchDown(): return random.random() * rowDelay + row * rowDelay
    def instant(): return 0
    def rightToLeftSmooth(): return (numCols - col) * colDelay
    def rightToLeft(): return (numCols - col) * colDelay + random.random()*colDelay
    def marchUpSmooth(): return (Wall.numRows - row) * rowDelay
    def marchUp(): return (Wall.numRows-row)*rowDelay + random.random() * rowDelay
    def stacks(): return col * colDelay if col % 2 else (numCols - col) * colDelay
    def loom(): return col * colDelay if row % 2 else (numCols - col) * colDelay
    def ribbons(): return row*500 if col % 2 else (Wall.numRows-row)*500
    def stripes(): 
      return (row + 1 + round(Wall.numRows / 2 + 0.5))*rowDelay/2 if row % 2 else row*rowDelay/2
    def nighttime(): return 9*1000
    def middleOut():
      mid = numCols / 2
      return abs(col-mid) * dRandom.r*0.04 * 1000
    def edgesIn():
      mid = numCols / 2
      return numCols * colDelay - abs(col-mid) * dRandom.r
#    def slowpoke(): return dRandom.r*0.04 * 1000 * 200 * random.random() + 1500
    def slowpoke(): return random.random()*5*1000 + 1500
    def diamondIn():
      midCol = numCols / 2
      midRow = Wall.numRows / 2
      colDelay = numCols * 20 - abs(col-midCol) * dRandom.r*0.04 * 1000
      rowDelay = Wall.numRows * colDelay / 2 - abs(row-midRow) * dRandom.r*0.04 * 1000 * 2.5
      return colDelay + rowDelay
    def diamondOut():
      midCol = numCols / 2
      midRow = Wall.numRows / 2
      colDelay = abs(col-midCol) * dRandom.r*0.04 * 1000 * 2
      rowDelay = abs(row-midRow) * dRandom.r*0.04 * 1000 * 5
      return colDelay + rowDelay
    def slantNW(): return col * dRandom.r*0.04 * 1000 + row * dRandom.r*0.04 * 1000 * 2.5
    def slantNE(): 
      colDelay = (numCols - col) * dRandom.r*0.04 * 1000 
      rowDelay = row * dRandom.r*0.04 * 1000 * 2.5
      return colDelay + rowDelay
    def slantSE(): 
      colDelay = (numCols - col) * dRandom.r*0.04 * 1000 
      rowDelay = (Wall.numRows - row) * dRandom.r*0.04 * 1000 * 2.5
      return colDelay + rowDelay
    def slantSW(): 
      colDelay = col * dRandom.r*0.04 * 1000 
      rowDelay = (Wall.numRows - row) * dRandom.r*0.04 * 1000 * 2.5
      return colDelay + rowDelay
    def slantNWVenetian(): 
      brickDelay = col * dRandom.r*0.04 * 1000 + row * dRandom.r*0.04 * 1000 *2
      oddDelay = (numCols * dRandom.r*0.04 * 1000 / 2 
#          + Wall.numRows * delayIncrement) * ((row+col) % 2)
#          + Wall.numRows * delayIncrement) * (row + col % 2)
          + Wall.numRows * dRandom.r*0.04 * 1000) * ((row + col) % 4)
      return brickDelay + oddDelay
      
    numCols = Wall.getNumCols()
    colDelay = Wall.targetRenderDuration / numCols
    rowDelay =  Wall.targetRenderDuration / Wall.numRows

    totalBricks = Wall.numRows * numCols
    row, col = 0, 0
    delayFun = (
      # ribbons, nighttime, # these not so great
      typeWriter, marchColumnsAcrossSmooth, marchColumnsAcross, randomFill,
      marchDownSmooth, marchDown, instant,
      rightToLeftSmooth, rightToLeft, marchUpSmooth, marchUp,
      stacks, loom, 
      stripes, middleOut, edgesIn, slowpoke,
      diamondIn, diamondOut, slantNW, slantNE, slantSE, slantSW,
      reverseTypeWriter, 
      slantNWVenetian,
    )
    getDelay=delayFun[(game.level - 1) % len(delayFun)]
    getDelay=random.choice((typeWriter, marchColumnsAcrossSmooth, marchColumnsAcross, randomFill,  ))
    getDelay = typeWriter
    getDelay=random.choice(delayFun)

    dRandom = RecordClass()
    dRandom.r = random.random()
    dRandom.stagger = random.choice((True, False))
    dRandom.stagger = True
    dRandom.staggerDelay = 0
    dRandom.useRow =  random.choice((0, 1))
    if random.random() <0.2:
      dRandom.groupSize = round(random.random()*numCols/2+2)
    else:
      dRandom.groupSize = numCols
    dRandom.groups = numCols / dRandom.groupSize
    

    #print (getDelay.__name__, round(dRandom.r, 3), dRandom.groupSize)
    
    for row in range(Wall.numRows):
      for col in range(numCols):
        brick = Brick(row, col)
        game.bricks.add(brick)
        if dRandom.stagger:
          colGroupDelay = Wall.targetRenderDuration / dRandom.groupSize
          #dRandom.staggerDelay = (dRandom.r * colGroupDelay * dRandom.columns * (col % dRandom.columns))
        brick.delayShowBrick(getDelay())
    return len(game.bricks)

  
  @staticmethod
  def getNumCols():
    return int(Game.width/Brick.width)

  @staticmethod
  def bottom():
    return Wall.topGap + Wall.numRows*Brick.height

  @staticmethod
  def sunsetGlow(delay=0):
    duration = 0.5 * 1000
    #brickDuration = duration / Wall.getNumCols() / 2
    topLeftBrick = (Brick.width/2, Wall.topGap+Brick.height/2)
    target = (game.screen.get_rect().centerx, Wall.bottom())
    maxDistance = Wall.distance(topLeftBrick,  target)
    for brick in game.bricks:
      distance = Wall.distance(brick.rect.center,  target)
      delay = duration * (maxDistance - distance) / maxDistance 
      brick.delayGlow(delay)
      pass

  @staticmethod
  def brickExplosion(deadBrick):
    duration = 0.2 * 1000
    topLeftBrick = (Brick.width/2, Wall.topGap+Brick.height/2)
    bottomRightBrick = (Wall.getNumCols() * Brick.width, Wall.numRows* Brick.height+Wall.topGap)
    target = (deadBrick.rect.center)
    maxDistance = Wall.distance(topLeftBrick,  bottomRightBrick)
    maxDistance = Wall.numRows* Brick.height + 25
    for brick in game.bricks:
      distance = Wall.distance(brick.rect.center,  target)
      if (distance < maxDistance):
        delay = duration - (duration * (maxDistance - distance) / maxDistance)
        brick.delayGlow(delay)
      pass


  @staticmethod
  def distance(p1, p2):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)
    pass

class RecordClass(): pass

class Events():
  def __init__(self, evDict):
    self.evDict = evDict
    self.clear()
    self.gameCache = {}
    self.levelCache = {}

  def clear(self):
    self.details=[]    

  def add(self, eventName):
    game.xp += game.XP_EVENT
    idEvent = self.evDict[eventName][0]
    # characters [0:23] return current time to the second in UTC to match sqlite db time
    dbTime = datetime.datetime.now(datetime.timezone.utc).isoformat()[:23]
    self.details.append((idEvent, dbTime))
    self.gameCache[eventName] = self.gameCache.get(eventName, 0) + 1
    self.levelCache[eventName] = self.levelCache.get(eventName, 0) + 1


class PowerUps():
  #def __init__():
  #  pass

  @staticmethod
  def setSpawnFactors():
    # debug set:
    PUpWiderPaddle.spawnRate=0.50
    PUpMultiBall.spawnRate=20
    PUpExtraLife.spawnRate=0.1
    PUpSlowMo.spawnRate=0.30
    PUpFireBall.spawnRate=0.4
    PUpInvinciBalls.spawnRate=0.4
    PUpBigBall.spawnRate=0.2
    PUpHighBall.spawnRate=2
    noPowerup = 0.1

    # game-balanced set:
    PUpWiderPaddle.spawnRate=50
    #PUpMultiBall.spawnRate=0.2
    PUpExtraLife.spawnRate=0.1
    #PUpSlowMo.spawnRate=30
    PUpFireBall.spawnRate=0.4
    PUpInvinciBalls.spawnRate=0.4
    #PUpBigBall.spawnRate=10
    PUpHighBall.spawnRate=0.4
    noPowerup = 30

    spawnRates = {}
    total = 0 + noPowerup
    pups = PowerUp.__subclasses__()
    for i in range(len(pups)): 
      total += pups[i].spawnRate
    #print ("Total powerup spawn rate: " + str(round(total)))
    factor = 1
    for i in range(len(pups)): 
      delta = pups[i].spawnRate / total
      factor -= delta
      pups[i].factor = factor
      spawnRates[pups[i].__name__] = round(delta * 100, 2)
      #print (" ", pups[i].__name__, str(factor), str(round(delta * 100, 2)) + "%")
    spawnRates["No Powerup"]=round(factor * 100,2)
    sRatesSorted = {
      k: str(v)+"%" for k, v in sorted(
        spawnRates.items(), key=lambda item: item[1], reverse=True)
    }
    return sRatesSorted

  @staticmethod
  def spawnRandom(x, y):
    if len(game.bricks)<1:
      PowerUps.spawn(globals()["PUpExtraLife"], x, y)   # psych!
      return
    r = random.random()
    f=len(game.bricks)/game.totalBricks
    #print (round(r,3), round(0.03/f,3))

    if r < 0.03/f:
      PowerUps.spawn(globals()["PUpMultiBall"], x, y)
    else:
      pups = PowerUp.__subclasses__()
      for i in range(len(pups)): 
        if r > pups[i].factor:
          #print ("--- ", pups[i].__name__, pups[i].factor , r)
          PowerUps.spawn(pups[i], x, y)
          break
      
  @staticmethod
  def spawn(pupClass, x=None, y=Wall.bottom()):
    if x==None:
      x=game.screen.get_rect().centerx
    p = pupClass(x, y)
    game.allsprites.add(p)
    game.powerUps.add(p)
    pass

class PowerUp(pygame.sprite.Sprite):
  width = Brick.width
  height = 2 * Brick.height

  deathDelay = 2.5 * 1000

  def __init__(self, x, y):
    super().__init__()
    self.image = pygame.Surface([PowerUp.width, PowerUp.height])
    self.startColor=self.getStartColor()
    self.deadColor = colors["darkorange4"]
    self.getImage()
    self.rect = self.image.get_rect()
    self.rect.x = x
    self.y = y

    self.fSpeed=Game.fSpeed/4
    self.speed=[0,1]
    self.alive=True
#    self.killTime = 0
    self.powerUpDuration = 10 * 1000
#    print (self.__class__.__name__)

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
#        print ("dead powerup: ", self.__class__.__name__)
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

  def showPUpValue(self, value):
    fontColor = colors["green"]
    if (value < 0):
      fontColor = colors["red"]
    game.renderText(str(value), self.image, 0, game.font, fontColor)
    pass

class PUpWiderPaddle(PowerUp):
  def __init__(self, x, y):
    super().__init__(x, y)
    # desired value range / (ln(1.2) - ln(0.2)) = 22.32442 
    # (20 - (-20)) / (1.60944 - (-0.18232)) = 22.32442 
    # generate delta between -20 and 20, but much more likely to closer to 20:
    r = 0.2 + (random.randint(0,20)/20)  # between 0.2 and 1.2
    self.delta = round(np.log(r) * 22.32442 + 16)
    self.showPUpValue(self.delta)

  def getImage(self):
    self.image = pygame.image.load("img/PowerupBoxWiden.png")
#    self.image = pygame.image.load("BreakoutImages/PowerupImages/PowerupBoxWiden.png")
    self.image = pygame.transform.scale(self.image,(PowerUp.width, PowerUp.height))

  def getStartColor(self):
      return colors["papayawhip"]

  def activate(self):
    #game.paddle.changeWidth(20)
    if game.paddle.changeWidth(self.delta):
      game.waitList.add(self.powerUpDuration, 
          lambda :game.paddle.changeWidth(-self.delta))
      game.events.add("WiderPaddles")

  def getMissedEventName(self):
     return "WiderPaddleMissed"


class PUpMultiBall(PowerUp):
  min = 3
  max = 5
  def __init__(self, x, y):
    super().__init__(x, y)
    self.numBalls=random.randint(PUpMultiBall.min, PUpMultiBall.max)
    self.showPUpValue(self.numBalls)

  def activate(self):
    game.events.add("MultiBall")
    delay = 1 * 1000
    game.addBallRandomSpeed()
    for b in range(1, self.numBalls):
      game.waitList.add(delay*b, game.addBallRandomSpeed)

  def getImage(self):
    self.image = pygame.image.load("img/PowerupBoxMultiBall.png")
    self.image = pygame.transform.scale(self.image,(PowerUp.width, PowerUp.height))

  def getStartColor(self):
      return colors["goldenrod"]

  def getMissedEventName(self):
     return "MultiBallMiss"

class PUpExtraLife(PowerUp):
  def __init__(self, x, y):
    super().__init__(x, y)

  def getImage(self):
    self.image = pygame.image.load("img/PowerupBox1UP.png")
    self.image = pygame.transform.scale(self.image,(PowerUp.width, PowerUp.height))

  def getStartColor(self):
      return colors["cyan2"]

  def activate(self):
    game.updateLives(1)
    game.events.add("ExtraLives")

  def getMissedEventName(self):
     return "ExtraLiveMissed"

class PUpSlowMo(PowerUp):
  def __init__(self, x, y):
    super().__init__(x, y)
    self.sDelta = 0.1 - random.random()*2
    self.showPUpValue(round(-10*self.sDelta))

  def getStartColor(self):
      return colors["plum3"]

  def activate(self):
    game.events.add("SloMo")
    for b in game.balls:
      if b.changeSpeed(self.sDelta):
        b.delayChangeSpeed(self.powerUpDuration, -self.sDelta)

  def getMissedEventName(self):
     return "SloMoMissed"

class PUpFireBall(PowerUp):
  def __init__(self, x, y):
    super().__init__(x, y)

  def getStartColor(self):
      return colors["firebrick1"]

  def activate(self):
    game.events.add("FireBall")
    for b in game.balls:
      if b.alive:
        b.fireBall = True
        b.image.fill(self.getStartColor())
        b.delayEndFireBall(self.powerUpDuration)
        break

  def getMissedEventName(self):
     return "FireBallMissed"

class PUpInvinciBalls(PowerUp):
  def __init__(self, x, y):
    super().__init__(x, y)

  def getStartColor(self):
    return fadeColor(colors["black"], colors["papayawhip"], 0.3)

  def getImage(self):
    super().getImage()
    rect = self.image.get_rect()
    height = rect.height * 0.1
    pygame.draw.rect(self.image, colors["papayawhip"], [
        0, 0, rect.width, height
    ])
    pygame.draw.rect(self.image, colors["papayawhip"], [
        0, rect.bottom-height, rect.width, height
    ])

  def activate(self):
    game.invinciBalls = True  
    self.barsprites = pygame.sprite.Group()
    height = game.paddle.height * 0.1
    self.addBar(game.paddle.rect.top, height)
    self.addBar(game.paddle.rect.bottom - height, height)
    game.waitList.add(self.powerUpDuration, self.endIvinciballs)
    game.events.add("InvincibleBalls")

  def getMissedEventName(self):
     return "InvincibleBallMissed"
  
  def endIvinciballs(self):
    for b in self.barsprites:
      b.kill()
    game.invinciBalls = False

  def addBar(self, y, height):
    bar = pygame.sprite.Sprite()
    bar.image = pygame.Surface([Game.width, height])
    bar.rect = bar.image.get_rect()
    bar.rect.x = 0
    bar.rect.y = y
    bar.image.fill(fadeColor(colors["black"], colors["papayawhip"], 0.3))
    self.barsprites.add(bar)
    game.allsprites.add(bar)

class PUpBigBall(PowerUp):
  def __init__(self, x, y):
    super().__init__(x, y)
    self.delta = random.randint(-2, 24)
    self.showPUpValue(self.delta)

  def getStartColor(self):
      return Ball.bigColor
      #colors["yellow1"]

  def activate(self):
    game.events.add("BigBalls")
    for b in game.balls:
      if b.alive and not b.bigBall:
        b.bigBall = True
        b.image.fill(self.getStartColor())
        #delta = random.randint(-2, 24)
        b.changeSize(self.delta)
        b.delayEndBigBall(self.powerUpDuration, -self.delta)
        break

  def getMissedEventName(self):
     return "BigBallMissed"

class PUpHighBall(PowerUp):
  def __init__(self, x, y):
    super().__init__(x, y)
    self.duration = random.randint(5, 20)
    self.showPUpValue(self.duration)

  def getStartColor(self):
      return colors["skyblue1"]

  def activate(self):
    game.events.add("HighBalls")
    for b in game.balls:
      if b.alive and not b.highBall:
        b.highBall = True
        b.image.fill(self.getStartColor())
        b.delayEndHighBall(self.duration*1000)
#        b.waitList.add(self.duration*1000, b.endHighBall)
        
        break

  def getMissedEventName(self):
     return "HighBallMissed"

def play(idUser=None):
  global game
  game=Game(idUser)
  game.run()

if __name__ == '__main__':
  play()
  pygame.quit()
  sys.exit()
