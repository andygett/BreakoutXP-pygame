import random, numpy as np, pygame
import gameui as gui

# static class with helper static methods which should be called the via the class name,
# e.g. PowerUps.setSpawnFactors()
class PowerUps():
  #def __init__():
  #  pass

  @staticmethod
  def setSpawnFactors(game):
    # game-balanced set:
    PUpWiderPaddle.spawnRate=50
    PUpMultiBall.spawnRate=0.2
    PUpExtraLife.spawnRate=0.1
    PUpSlowMo.spawnRate=30
    PUpFireBall.spawnRate=0.4
    PUpInvinciBalls.spawnRate=0.4
    PUpBigBall.spawnRate=0.4
    PUpHighBall.spawnRate=0.4
    noPowerup = 30

    # debug set:
    #PUpWiderPaddle.spawnRate=0.50
    #PUpMultiBall.spawnRate=1
    #PUpExtraLife.spawnRate=0.4
    #PUpSlowMo.spawnRate=0.30
    #PUpFireBall.spawnRate=0.4
    #PUpInvinciBalls.spawnRate=0.7
    #PUpBigBall.spawnRate=0.2
    #PUpHighBall.spawnRate=0.4
    #noPowerup = 0.1

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
  def spawnRandom(game, x, y):
#    if len(game.bricks)<1:
#      PowerUps.spawn(globals()["PUpExtraLife"], x, y)   # psych!
#      return
    r = random.random()
    f=len(game.bricks)/game.totalBricks
    #print (round(r,3), round(0.03/f,3))

    if r < 0.03/f:
#      PowerUps.spawn(globals()["PUpMultiBall"], x, y)
      PowerUps.spawn(game, PUpMultiBall, x, y)
    else:
      pups = PowerUp.__subclasses__()
      for i in range(len(pups)): 
        if r > pups[i].factor:
          #print ("--- ", pups[i].__name__, pups[i].factor , r)
          PowerUps.spawn(game, pups[i], x, y)
          break
      
  @staticmethod
  def spawn(game, pupClass, x=None, y=gui.Wall.bottom()):
    if x==None:
      x=game.screen.get_rect().centerx
    p = pupClass(game, x, y)
    game.allsprites.add(p)
    game.powerUps.add(p)
    pass

# abstract class which should not be directly instantiated.  
# Instead, create a subclass and override the methods as appropriate.
class PowerUp(pygame.sprite.Sprite):
  width = gui.Brick.width
  height = 2 * gui.Brick.height

  deathDelay = 2.5 * 1000

  def __init__(self, game, x, y):
    super().__init__()
    self.game=game
    self.image = pygame.Surface([PowerUp.width, PowerUp.height])
    self.startColor=self.getStartColor()
    self.deadColor = gui.colors["darkorange4"]
    self.getImage()
    self.rect = self.image.get_rect()
    self.rect.x = x
    self.y = y

    self.fSpeed=self.game.fSpeed/4
    self.speed=[0,1]
    self.alive=True
#    self.killTime = 0
    self.powerUpDuration = 10 * 1000
#    print (self.__class__.__name__)

  def getImage(self):
    self.image.fill(self.startColor)

  def getStartColor(self):
    return gui.colors["orange"]

  def move(self):
    self.y += self.speed[1]*self.fSpeed
    self.rect.y = self.y
    if self.rect.top > self.game.height:
      self.kill()

  def checkDeath(self):
    pBottom = self.game.paddle.rect.bottom
    if self.rect.top > pBottom:
      if self.alive:
        self.addMissedPupEvent()
        self.fSpeed /= 4
#        print ("dead powerup: ", self.__class__.__name__)
        self.alive=False
      factor = 1 - (self.rect.top - pBottom)/(self.game.height - pBottom)
      self.image = pygame.transform.scale(self.image,(
        int(gui.Ball.size + 72*factor), int(gui.Ball.size + 52*factor)))

  def addMissedPupEvent(self):
    evName = self.getMissedEventName()
    if evName != "None":
      self.game.events.add(evName)

  def getMissedEventName(self):
    return "None"

  def hitPaddle(self):
    if  pygame.sprite.collide_rect(self, self.game.paddle):
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
    fontColor = gui.colors["green"]
    if (value < 0):
      fontColor = gui.colors["red"]
    self.game.renderText(str(value), self.image, 0, self.game.font, fontColor)
    pass

class PUpWiderPaddle(PowerUp):
  def __init__(self, game, x, y):
    super().__init__(game, x, y)
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
      return gui.colors["papayawhip"]

  def activate(self):
    #game.paddle.changeWidth(20)
    if self.game.paddle.changeWidth(self.delta):
      self.game.waitList.add(self.powerUpDuration, 
          lambda :self.game.paddle.changeWidth(-self.delta))
      self.game.events.add("WiderPaddles")

  def getMissedEventName(self):
     return "WiderPaddleMissed"


class PUpMultiBall(PowerUp):
  min = 3
  max = 5
  def __init__(self, game, x, y):
    super().__init__(game, x, y)
    self.numBalls=random.randint(PUpMultiBall.min, PUpMultiBall.max)
    self.showPUpValue(self.numBalls)

  def activate(self):
    self.game.events.add("MultiBall")
    delay = 1 * 1000
    self.game.addBallRandomSpeed()
    for b in range(1, self.numBalls):
      self.game.waitList.add(delay*b, self.game.addBallRandomSpeed)

  def getImage(self):
    self.image = pygame.image.load("img/PowerupBoxMultiBall.png")
    self.image = pygame.transform.scale(self.image,(PowerUp.width, PowerUp.height))

  def getStartColor(self):
      return gui.colors["goldenrod"]

  def getMissedEventName(self):
     return "MultiBallMiss"

class PUpExtraLife(PowerUp):
  def __init__(self, game, x, y):
    super().__init__(game, x, y)

  def getImage(self):
    self.image = pygame.image.load("img/PowerupBox1UP.png")
    self.image = pygame.transform.scale(self.image,(PowerUp.width, PowerUp.height))

  def getStartColor(self):
      return gui.colors["cyan2"]

  def activate(self):
    self.game.updateLives(1)
    self.game.events.add("ExtraLives")

  def getMissedEventName(self):
     return "ExtraLiveMissed"

class PUpSlowMo(PowerUp):
  def __init__(self, game, x, y):
    super().__init__(game, x, y)
    self.sDelta = 0.1 - random.random()*2
    self.showPUpValue(round(-10*self.sDelta))

  def getStartColor(self):
      return gui.colors["plum3"]

  def activate(self):
    self.game.events.add("SloMo")
    for b in self.game.balls:
      if b.changeSpeed(self.sDelta):
        b.delayChangeSpeed(self.powerUpDuration, -self.sDelta)

  def getMissedEventName(self):
     return "SloMoMissed"

class PUpFireBall(PowerUp):
  def __init__(self, game, x, y):
    super().__init__(game, x, y)

  def getStartColor(self):
      return gui.colors["firebrick1"]

  def activate(self):
    self.game.events.add("FireBall")
    for b in self.game.balls:
      if b.alive:
        b.fireBall = True
        b.image.fill(self.getStartColor())
        b.delayEndFireBall(self.powerUpDuration)
        break

  def getMissedEventName(self):
     return "FireBallMissed"

class PUpInvinciBalls(PowerUp):
  def __init__(self, game, x, y):
    super().__init__(game, x, y)

  def getStartColor(self):
    return gui.fadeColor(gui.colors["black"], gui.colors["papayawhip"], 0.3)

  def getImage(self):
    super().getImage()
    rect = self.image.get_rect()
    height = rect.height * 0.1
    pygame.draw.rect(self.image, gui.colors["papayawhip"], [
        0, 0, rect.width, height
    ])
    pygame.draw.rect(self.image, gui.colors["papayawhip"], [
        0, rect.bottom-height, rect.width, height
    ])

  def activate(self):
    self.game.invinciBalls = True  
    self.barsprites = pygame.sprite.Group()
    height = self.game.paddle.height * 0.1
    self.addBar(self.game.paddle.rect.top, height)
    self.addBar(self.game.paddle.rect.bottom - height, height)
    self.game.waitList.add(self.powerUpDuration, self.endIvinciballs)
    self.game.events.add("InvincibleBalls")

  def getMissedEventName(self):
     return "InvincibleBallMissed"
  
  def endIvinciballs(self):
    for b in self.barsprites:
      b.kill()
    self.game.invinciBalls = False

  def addBar(self, y, height):
    bar = pygame.sprite.Sprite()
    bar.image = pygame.Surface([self.game.width, height])
    bar.rect = bar.image.get_rect()
    bar.rect.x = 0
    bar.rect.y = y
    bar.image.fill(gui.fadeColor(gui.colors["black"], gui.colors["papayawhip"], 0.3))
    self.barsprites.add(bar)
    self.game.allsprites.add(bar)

class PUpBigBall(PowerUp):
  def __init__(self, game, x, y):
    super().__init__(game, x, y)
    self.delta = random.randint(-2, 24)
    self.showPUpValue(self.delta)

  def getStartColor(self):
      return gui.Ball.bigColor
      #gui.colors["yellow1"]

  def activate(self):
    self.game.events.add("BigBalls")
    for b in self.game.balls:
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
  def __init__(self, game, x, y):
    super().__init__(game, x, y)
    self.duration = random.randint(5, 20)
    self.showPUpValue(self.duration)

  def getStartColor(self):
      return gui.colors["skyblue1"]

  def activate(self):
    self.game.events.add("HighBalls")
    for b in self.game.balls:
      if b.alive and not b.highBall:
        b.highBall = True
        b.image.fill(self.getStartColor())
        b.delayEndHighBall(self.duration*1000)
#        b.waitList.add(self.duration*1000, b.endHighBall)
        
        break

  def getMissedEventName(self):
     return "HighBallMissed"
