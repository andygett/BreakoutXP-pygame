import sys, pygame, random
#import  numpy as np
import breakodb, gameui as gui, breakoutils as utils, powerups as pups

class Game(object):
  XP_EVENT = 10
  XP_LEVEL = 4000
  numLives = 3
  fps = 120
  fSpeed = 4
  size = width, height = gui.Brick.width * 12, 840
  version = "1.8"

  rmRUN=  2** 0
  rmSTATS=2** 1
  rmPAUSE=2** 2
  rmQUIT= 2**10


  def __init__(self, idUser):
    self.db = breakodb.Db()
    eventTypes = self.db.getEventDict()
    self.events=utils.Events(self.onAddEvent, eventTypes)

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

    self.bgColor = gui.colors["gray10"]
    pygame.display.set_caption('Break Out, go ahead and give it to me')
    self.fontHuge = pygame.font.Font(pygame.font.get_default_font(), 24)
    self.fontLarge = pygame.font.Font(pygame.font.get_default_font(), 20)
    self.font = pygame.font.SysFont("calibri", 14)
    self.fontSmall = pygame.font.SysFont("SegoeUI", 9)

    self.clock = pygame.time.Clock()
    self.pupSpawnRates = pups.PowerUps.setSpawnFactors(self)
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
    progressDone.fill(gui.fadeColor(self.paddle.color, gui.colors["navy"], percent))
  
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
        b.fill(gui.fadeColor(self.paddle.color, gui.colors["gray15"], 50))
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
    #careerEvents = game.db.getUserStats(self.idUser)
    careerEvents = self.db.getUserStats(self.idUser)
    evCount = 0
    for i in range(len(careerEvents)):
      evCount += int(careerEvents[i][1])
    self.xpDict = self.db.getXPDict(self.idUser)
    self.xp = (
      1000 * self.xpDict["Sessions"] 
      + 2000 * self.xpDict["Games"] 
      + Game.XP_LEVEL * self.xpDict["Levels"]
      + Game.XP_EVENT * evCount
    )

  def newLevel(self):
    self.level += 1
    self.xp += Game.XP_LEVEL
    self.events.levelCache = {}
    self.idLevel = self.db.newLevel(self.idGame, self.level)
    self.levelPauseDuration = 0
    self.maxBalls = 1

    self.allsprites = pygame.sprite.Group()
    self.bricks = pygame.sprite.Group()
    self.balls = pygame.sprite.Group()
    self.powerUps = pygame.sprite.Group()
    self.paddle = gui.Paddle(self)
    self.allsprites.add(self.paddle)
    self.updateLives()
    self.waitList = utils.WaitList()
    self.totalBricks = gui.Wall.render(self)
    self.hitThisManyBricksForNextLevel = int(self.totalBricks*self.levelThreshold)
    self.waitList.add(1000, self.addBall)
    self.newGameWait = False
    self.invinciBalls = False
    self.grantLife()

  def delayNewLevel(self):
    for b in self.balls:
      b.fSpeed = 0.5
      b.alive = False
    self.waitList.add(3 * 1000, self.newLevel)
    self.endLevel()

  @staticmethod
  def getNumCols():
    return int(Game.width/gui.Brick.width)


  def endLevel(self):
      self.db.endLevel(self.idLevel, self.maxBalls,
          int(self.levelPauseDuration / 1000 + 0.5))
      self.db.saveEvents(self.idLevel, self.events.details)
      self.events.clear()

  def endPause(self):
    pauseDuration = pygame.time.get_ticks() - self.pauseStart
    self.waitList.addPauseDuration(pauseDuration)
    self.events.add("EndPause")
    for b in self.balls:
      b.waitList.addPauseDuration(pauseDuration)
    self.levelPauseDuration += pauseDuration

  def showStats(self):
    userStatsSurf = pygame.Surface([200, Game.height - 150])
    userStatsSurf.fill(self.bgColor)
    gameStatsSurf = userStatsSurf.copy()
    levelStatsSurf = userStatsSurf.copy()

    gameWaitTop = self.renderData(self.xpDict, userStatsSurf, heading="User Stats")
    gameWaitTop = self.renderData(self.db.getUserStats(self.idUser), 
        userStatsSurf, top=gameWaitTop+15)
    
#    gameWaitTop = self.renderData(game.db.getUserStats(self.idUser), 
#        userStatsSurf, heading="User Stats")
#    gameWaitTop = self.renderData(game.xpDict, userStatsSurf, top=gameWaitTop+15)
    
    self.screen.blit(userStatsSurf, (50,50))
    self.showGameStats(gameStatsSurf)
    self.showLevelStats(levelStatsSurf)

    if self.newGameWait:
      self.renderText("Game Over.  Press Enter for new game, Esc to quit",
         self.screen, gameWaitTop + 70, self.fontHuge, gui.colors["orangered"] )

    s = "Version %s. © 2021, 2022 Rado Shaq Enterprises. All rights reserved. Any retransmission or rebroadcast of this game is strictly encouraged. Your mileage may vary. Similarities to real life are purely coincidental." % Game.version
    self.renderText(s, self.screen, Game.height - 20, 
        self.fontSmall, gui.colors["peachpuff3"] )

  def showGameStats(self, gameSurf):
    curTop = self.renderData(self.events.gameCache, gameSurf, heading="Game Stats")
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
    curTop = self.renderData(self.events.levelCache, levelSurf, 
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
    userColor = gui.colors["cadetblue2"]
    self.renderText(s, self.screen, 0, self.fontHuge, userColor)
    self.renderText("XP: " + str(self.xp), self.screen, 0, self.fontLarge, 
        userColor, rightJustify=True)

  def renderData(self, data, destSurf=None, top=None, color=gui.colors["peachpuff"], 
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

  def addBall(self, fSpeed=None):
    ball = gui.Ball(self, fSpeed)
    self.allsprites.add(ball)
    self.balls.add(ball)
    self.maxBalls = max(self.maxBalls, len(self.balls))
    return ball

  def addBallRandomSpeed(self):
    ball = self.addBall(random.random()*4 + 1)

  def grantLife(self):
    if self.level > 0:
      if random.random() < 0.2 + 1/(self.level+1):
          delay = gui.Ball.deathDelay + (random.random()*4.5 + 0.5)*1000
          self.waitList.add(delay-0.5*1000, 
            lambda: gui.Wall.sunsetGlow(self))
          self.waitList.add(delay, 
#              lambda: pups.PowerUps.spawn(game, globals()["PUpExtraLife"]))
              lambda: pups.PowerUps.spawn(self, pups.PUpExtraLife))

    pass

  def spawnRandomPup(self, x, y):
    pups.PowerUps.spawnRandom(self, x, y)

  def onAddEvent(self):
    self.xp += Game.XP_EVENT

  def processGameEvents(self, runMode):
    for event in pygame.event.get():
      if event.type == pygame.MOUSEMOTION:
        pygame.mouse.set_visible(1)
        self.mouseVisibleKill = pygame.time.get_ticks()+3*1000
      if event.type == pygame.QUIT: 
        if runMode==Game.rmSTATS:
          self.endPause()
        runMode=Game.rmQUIT
      elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
          if runMode==Game.rmSTATS and not self.newGameWait:
            self.endPause()
          self.newGameWait = False
          runMode=Game.rmQUIT
        if event.key == pygame.K_u:
          #self.level += 1
          self.newLevel()
        if event.key == pygame.K_d:
          self.level -= 2
          self.newLevel()
        if event.key == pygame.K_RETURN:
          if self.newGameWait:
            runMode=Game.rmRUN
            self.newGame()
          else:
            if runMode==Game.rmRUN:
              self.pauseStart = pygame.time.get_ticks()
              runMode=Game.rmSTATS
              self.events.add("StartPause")
            else:
              self.endPause()
              runMode=Game.rmRUN
    return runMode

  def runGame(self):
    self.paddle.handle_keys()
    self.balls.update()
    self.powerUps.update()
    self.bricks.update()
    self.waitList.process()
    self.allsprites.draw(self.screen)

  def run(self):
    self.newGame()
    #runMode="r"
    runMode=Game.rmRUN
    self.pauseStart = 0
    self.mouseVisibleKill = 0
    while runMode != Game.rmQUIT:
      self.clock.tick(Game.fps)      
      if pygame.time.get_ticks() > self.mouseVisibleKill:
        pygame.mouse.set_visible(0)
        self.mouseVisibleKill = 0
      runMode=self.processGameEvents(runMode)    
      self.showUserLevelOnClearScreen()
      if self.newGameWait:
        runMode = Game.rmSTATS
      if runMode == Game.rmRUN:
        self.runGame()
      elif runMode==Game.rmSTATS:
        self.showStats()
      pygame.display.flip()
    self.endGame(self.events.evDict["UserQuit"][0])
    self.db.endSession(self.idSession)

  @staticmethod
  def play(idUser=None):
    Game(idUser).run()

if __name__ == '__main__':
  Game.play()
  pygame.quit()
  sys.exit()
