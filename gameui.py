import random, numpy as np, math
import pygame
import breakoutils as utils #, powerups as pups
colors = pygame.color.THECOLORS

class Brick(pygame.sprite.Sprite):
  width = 80
  height = 30

  targetFadeDuration = 1.5 * 1000
  fadeIterations = 50
  iterationDuration = targetFadeDuration / fadeIterations

  def __init__(self, game, row, col):
    super().__init__()
#    topColor = colors["palegreen"]
#    bottomColor = colors["turquoise4"]
    self.game=game
    self.image = pygame.Surface([Brick.width, Brick.height])
#    self.image.fill(Brick.color)
    topColor = self.getTopColor()
    bottomColor = self.getBottomColor()
#    if row == 1 and col == 1:
#      print (self.game.level, topColor, bottomColor)
    self.color = fadeColor(topColor, bottomColor, row / Wall.numRows)
    self.image.fill(self.color)
    self.rect = self.image.get_rect()
    self.rect.x = Brick.width * col
    self.rect.y = Wall.topGap + Brick.height * row
    self.powerUps=[]
    self.waitList = utils.WaitList()
#    self.fadeByFactor = lambda factor: lambda: self.image.fill(fadeColor(self.color, self.game.bgColor, factor))
    self.fadeByFactor = lambda startColor, endColor, factor: lambda: self.image.fill(fadeColor(startColor, endColor, factor))

  def update(self):
    self.waitList.process()

# some 4-digit prime numbers for seeding:
# 1009 1013 1019 1021 1031 1033 1039 1049 1051 1061 1063 1069 1087 1091 1093 1097 1103 1109 1117 1123 1129 1151 1153 1163 1171 1181 1187 1193 1201 1213 1217 1223 1229 1231 1237 1249 1259 1277 1279 1283 1289 1291 1297 1301 1303 1307 1319 1321 1327 1361 1367 1373 1381 1399 1409 1423 1427 1429 1433 1439 1447 1451 1453 1459
  def getTopColor(self):
    varColor = (self.game.level * 1229) % 256
    satCat = self.game.level % 6
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
    varColor = (self.game.level * 1013) % 256
    satCat = self.game.level % 6
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
    self.image.fill(self.game.bgColor)
    self.game.waitList.add(duration, lambda: self.game.allsprites.add(self))
    #fic = lambda factor: lambda: self.fadeInColor(2*factor/100)
#    fic = lambda factor: self.fadeInColor(2*factor/100)
#    self.fic = lambda factor: lambda: self.image.fill(fadeColor(self.color, self.game.bgColor, factor))
    
    for i in range(Brick.fadeIterations):
      self.waitList.add(duration + i*Brick.iterationDuration, 
          self.fadeByFactor(self.game.bgColor, self.color, 2*i/100))

    return duration + Brick.targetFadeDuration

#    for i in range(51):
#      self.waitList.add(duration + i*10, self.fadeByFactor(2*i/100))

 # def fadeInColor(self, factor):
    #oldrect = self.rect
    #print ("fade ticks: ", pygame.time.get_ticks(), round(factor,3))
#    self.image.fill(fadeColor(self.color, self.game.bgColor, factor))
    #self.rect = self.image.get_rect()
    #self.rect = oldrect
  def delayGlow(self, delay, duration=0.4*1000):
#    glowColor = colors["goldenrod1"]
    glowColor = colors["lemonchiffon"]
    maxGlow = 0.4
    iterationDuration = (self.game.fps / 1000) / 4

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

class RecordClass(): pass

class Wall(object):
  topGap=100
  #numRows=2
  numRows=5
  targetRenderDuration = 1.5 * 1000

  @staticmethod
  def render(game):
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
      
    numCols = game.getNumCols()
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
        brick = Brick(game, row, col)
        game.bricks.add(brick)
        if dRandom.stagger:
          colGroupDelay = Wall.targetRenderDuration / dRandom.groupSize
          #dRandom.staggerDelay = (dRandom.r * colGroupDelay * dRandom.columns * (col % dRandom.columns))
        brick.delayShowBrick(getDelay())
    return len(game.bricks)

  
  #@staticmethod
  #def getNumCols():
  #  return int(self.game.width/Brick.width)

  @staticmethod
  def bottom():
    return Wall.topGap + Wall.numRows*Brick.height

  @staticmethod
  def sunsetGlow(game, delay=0):
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
  def brickExplosion(game, deadBrick):
    duration = 0.2 * 1000
    topLeftBrick = (Brick.width/2, Wall.topGap+Brick.height/2)
    bottomRightBrick = (game.getNumCols() * Brick.width, Wall.numRows* Brick.height+Wall.topGap)
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

class Paddle(pygame.sprite.Sprite):
  hover = 40
  minWidth = 30
  def __init__(self, game):
    # Call the parent's constructor
    super().__init__()
    self.game=game
    self.width = 80
    self.height = 10
    self.color = colors["gray89"]

    self.image = pygame.Surface([self.width, self.height])
    self.image.fill(self.color)
    self.rect = self.image.get_rect()
    self.rect.x = self.game.width/2
    self.rect.y = self.game.height-self.height - Paddle.hover

  def handle_keys(self):
    keys = pygame.key.get_pressed()
    # move=keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
    self.rect.move_ip(self.game.fSpeed * 2 * (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]), 0)
    if self.rect.left < 0:
      self.rect.left = 0
    if self.rect.right  >  self.game.width:
      self.rect.right = self.game.width
    if self.game.newGameWait:
      if keys[pygame.K_SPACE]:
        self.game.newGame()

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
    self.game.updateProgressBar()
    self.game.updateLives()
    return True

class Ball(pygame.sprite.Sprite):
  color=colors["gold"]
  bigColor=colors["yellow1"]
  deadColor = colors["red4"]
  size = 8
  deathDelay = 2.5 * 1000
  
  def __init__(self, game, fSpeedx=None):
    super().__init__()
    self.game=game
    self.size = Ball.size
    self.image = pygame.Surface([self.size, self.size])
    self.image.fill(Ball.color)
    self.rect = self.image.get_rect()
    self.x = random.random() * self.game.width - 1
    self.y=Wall.bottom()
    if fSpeedx is None:
      self.fSpeed=self.game.fSpeed
    else:
      self.fSpeed=fSpeedx
    self.speed=[1,1]
    self.alive=True
    self.killTime = 0
    self.game.events.add("NewBall")
    self.waitList = utils.WaitList()
    self.fireBall = False
    self.bigBall = False
    self.highBall = False

  def move(self):
    self.x += self.speed[0]*self.fSpeed
    self.rect.x = self.x
    self.y += self.speed[1]*self.fSpeed
    self.rect.y = self.y
    if self.rect.right > self.game.width:
      self.game.events.add("ScreenBorderHit")
      self.rect.right = self.game.width
      self.speed[0] = -1
    elif self.rect.left < 0:
      self.game.events.add("ScreenBorderHit")
      self.rect.left = 0
      self.speed[0] = 1
    if self.rect.top < 0:
      self.game.events.add("ScreenBorderHit")
      self.rect.top = 0
      self.speed[1] = 1
    if self.rect.bottom > self.game.height:
      self.rect.bottom = self.game.height
      self.y = self.rect.bottom - self.size
      self.speed[1] = 0
      self.image.fill(colors["darkred"])

  def checkDeath(self):
    if self.rect.top > self.game.paddle.rect.bottom:
      if self.alive:
        if self.game.invinciBalls:
          self.bounce()
        else:
          self.game.events.add("DeadBall")
          self.fSpeed = 0.5
          self.killTime = pygame.time.get_ticks() + Ball.deathDelay
          self.alive=False
      if not self.alive:
        percent = (self.game.height - self.rect.bottom) / (self.game.height - self.game.paddle.rect.bottom)
        self.image.fill(fadeColor(Ball.deadColor, Ball.color, percent))
        if pygame.time.get_ticks() > self.killTime:
          self.kill()
          if len(self.game.balls) < 1:
            if self.game.updateLives(-1):
              self.game.addBall()
              self.game.grantLife()

  def hitTheBricks(self):
    if self.highBall and self.speed[1]<0:
      return

    deadBricks = pygame.sprite.spritecollide(self, self.game.bricks, True)
    if len(deadBricks) > 0:
      Wall.brickExplosion(self.game, deadBricks[0])
      for brick in deadBricks:
        self.game.events.add("BrickBounce")
        #pups.PowerUps.spawnRandom(brick.rect.x, brick.rect.y)
        self.game.spawnRandomPup(brick.rect.x, brick.rect.y)

      if not self.fireBall:
        self.bounce()
      if len(self.game.bricks) <= int(self.game.totalBricks - self.game.hitThisManyBricksForNextLevel):
        self.game.delayNewLevel()
      else:
        self.game.updateProgressBar()

  def hitPaddle(self):
    # Bounce if ball hits  paddle
    if  pygame.sprite.collide_rect(self, self.game.paddle):
      self.y = self.game.paddle.rect.top - self.size
      self.bounce()
      self.game.events.add("PaddleHit")

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

def fadeColor(startColor, endColor, factor):
  #color=startColor + (np.array(endColor) - np.array(startColor)) * percent
  if factor > 1:
    factor = 1
#  return endColor + (np.array(startColor) - np.array(endColor)) * factor
  return startColor + (np.array(endColor) - np.array(startColor)) * factor

