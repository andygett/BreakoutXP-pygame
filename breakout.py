import sys, pygame, random
import numpy as np
#from pygame.constants import CONTROLLERAXISMOTION


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
  color = colors["blue2"]
  def __init__(self, row, col):
    # Call the parent's constructor
    super().__init__()
    self.image = pygame.Surface([Brick.width, Brick.height])
    self.image.fill(Brick.color)
    self.rect = self.image.get_rect()
    self.rect.x = Brick.width * col
    self.rect.y = Wall.topGap + Brick.height * row
    self.powerUps=[]

class Game(object):
  numLives = 5
  fps = 30
  fSpeed = 5
  size = width, height = Brick.width * 12, 840
  

  def __init__(self):
    pygame.init()
    pygame.mouse.set_visible(0)
    self.screen = pygame.display.set_mode(Game.size)
    pygame.display.set_caption('Break Out, go ahead and give it to me')
    self.clock = pygame.time.Clock()

  def updateProgressBar(self):
    top=2
    percent = (self.totalBricks - len(self.bricks)) / self.totalBricks
#    barWidth = self.paddle.rect.width * (self.totalBricks - len(self.bricks)) / self.totalBricks
    barWidth = self.paddle.rect.width * percent
    progressDone = self.paddle.image.subsurface((0,top,barWidth,2))
    progressDone.fill(fadeColor(self.paddle.color, Brick.color, percent))
  
  # returns true if still alive
  def updateLives(self, delta=0):
    self.lives += delta
    if self.lives < 1:
      self.newGameWait = True
      self.waitList.append([pygame.time.get_ticks() + 4*1000, 
        lambda :self.newGame()])
      return False
    size = 3
    pad = 4
    top = 6
    b = self.paddle.image.subsurface((0,top,self.paddle.rect.width,size))
    b.fill(self.paddle.color)
    for v in range(self.lives):
      x = pad + v*(size+pad)
      if (x + size < self.paddle.rect.width):
        b = self.paddle.image.subsurface((x,top,size,size))
        b.fill(fadeColor(self.paddle.color, colors["gray15"], 0))
    return True


  def newGame(self):
    self.lives = Game.numLives
    self.waitList = []
    self.allsprites = pygame.sprite.Group()
    self.bricks = pygame.sprite.Group()
    self.balls = pygame.sprite.Group()
    self.powerUps = pygame.sprite.Group()
    self.paddle = Paddle()
    self.allsprites.add(self.paddle)
    self.updateLives()
    Wall.render()
    self.totalBricks = len(self.bricks)
    self.initPowerUps()
    self.addBall()
    self.newGameWait = False

  def run(self):
    self.newGame()
    run=True

    while run:
      self.clock.tick(Game.fps)
      for event in pygame.event.get():
        if event.type == pygame.QUIT: 
          run=False
        elif event.type == pygame.KEYDOWN:
          if event.key == pygame.K_ESCAPE:
            run=False
        
      self.paddle.handle_keys()
      self.balls.update()
      self.powerUps.update()
      self.processWaitList()
      

      # Draw Everything
      #self.screen.fill(black)
      self.screen.fill(colors["gray10"])
      
      self.allsprites.draw(self.screen)
      pygame.display.flip()
    pygame.quit()
    sys.exit()

  def processWaitList(self):
    slicedWaitList = []
    for p in self.waitList:
      if pygame.time.get_ticks() > p[0]:
        p[1]()
      else:
        slicedWaitList.append(p)
    self.waitList = slicedWaitList

  def addBall(self):
    ball = Ball()
    self.allsprites.add(ball)
    self.balls.add(ball)

  def initPowerUps(self):
    for b in range(0, len(self.bricks)):
      brick=self.bricks.sprites()[b]
      r = random.random()
      if r > 0.7:
        brick.powerUps.append(PUpWiderPaddle(brick))
      elif r > 0.6:
        brick.powerUps.append(PUpMultiBall(brick))
        #self.bricks.sprites()[b].powerUps.append(PUpMultiBall(self.bricks.sprites()[b]))

  
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

  def move(self):
    self.x += self.speed[0]*self.fSpeed
    self.rect.x = self.x
    self.y += self.speed[1]*self.fSpeed
    self.rect.y = self.y
    if self.rect.right > Game.width:
      self.rect.right = Game.width
      self.speed[0] = -1
    elif self.rect.left < 0:
      self.rect.left = 0
      self.speed[0] = 1
    if self.rect.top < 0:
      self.rect.top = 0
      self.speed[1] = 1
    if self.rect.bottom > Game.height:
      self.rect.bottom = Game.height
      self.y = self.rect.bottom - Ball.size
      self.speed[1] = 0
      self.image.fill(darkRed)

  def checkDeath(self):
    if self.rect.top > game.paddle.rect.bottom:
      #TODO: lose life, maybe conditionally bounce as a power up.  bounce for now.
      if self.alive:
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
        for powerUp in brick.powerUps:
          game.allsprites.add(powerUp)
          game.powerUps.add(powerUp)

      self.bounce()
#      if len(game.balls) < 3:
#        newBall=Ball()
#        game.allsprites.add(newBall)
#        game.balls.add(newBall)
      game.updateProgressBar()

  def hitPaddle(self):
    # Bounce if ball hits  paddle
    if  pygame.sprite.collide_rect(self, game.paddle):
      self.y = game.paddle.rect.top - Ball.size
      self.bounce()

  def update(self):
    self.move()
    self.checkDeath()
    self.hitTheBricks()
    self.hitPaddle()
    
  def bounce(self):
    self.speed[1] = -self.speed[1]


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

class PowerUp(pygame.sprite.Sprite):
  #startColor=orange
  #deadColor = darkOrange
  size = 8
  width = Brick.width/2
  height = Brick.height

  deathDelay = 2.5 * 1000
  
  def __init__(self, brick):
    super().__init__()
    self.image = pygame.Surface([PowerUp.width, PowerUp.height])
    self.startColor=self.getStartColor()
    self.deadColor = colors["darkorange4"]
    self.image.fill(self.startColor)
    self.rect = self.image.get_rect()
    self.rect.x = brick.rect.x
    self.y = brick.rect.y

    self.fSpeed=Game.fSpeed/4
    self.speed=[0,1]
    self.alive=True
    self.killTime = 0
    self.powerUpDuration = 10 * 1000

  def getStartColor(self):
    return colors["orange"]

  def move(self):
    self.y += self.speed[1]*self.fSpeed
    self.rect.y = self.y
    if self.rect.bottom > Game.height:
      self.rect.bottom = Game.height
      self.y = self.rect.bottom - PowerUp.height
      self.speed[1] = 0
      self.image.fill(self.deadColor)

  def checkDeath(self):
    if self.rect.top > game.paddle.rect.bottom:
      if self.alive:
        self.fSpeed = 0.02
        self.killTime = pygame.time.get_ticks() + Ball.deathDelay/2 # maybe game.delay?
        self.alive=False
      percent = (Game.height - self.rect.bottom) / (Game.height - game.paddle.rect.bottom)
      self.image.fill(fadeColor(self.startColor, self.deadColor, percent))
      if pygame.time.get_ticks() > self.killTime:
        self.kill()


  def hitPaddle(self):
    if  pygame.sprite.collide_rect(self, game.paddle):
      #self.y = paddle.rect.top - Ball.size
      self.activate()
      self.kill()

  def update(self):
    self.move()
    self.checkDeath()
    self.hitPaddle()
    
  def activate(self):
    pass

class PUpWiderPaddle(PowerUp):
  def __init__(self, brick):
    super().__init__(brick)
    self.startColor = colors["papayawhip"]
    self.image.fill(self.startColor)
  
  def getStartColor(self):
      return colors["papayawhip"]

  def activate(self):
      game.paddle.changeWidth(20)
      game.waitList.append([pygame.time.get_ticks() + self.powerUpDuration, 
        lambda :game.paddle.changeWidth(-20)])

class PUpMultiBall(PowerUp):
  min = 3
  max = 5
  def __init__(self, brick):
    super().__init__(brick)
    self.image.fill(self.startColor)
  
  def activate(self):
    delay = 1 * 1000
    game.addBall()
    for b in range(1, random.randint(PUpMultiBall.min, PUpMultiBall.max)):
      game.waitList.append([pygame.time.get_ticks() + delay*b, 
        lambda :game.addBall()])

  def getStartColor(self):
      return colors["goldenrod"]


game=Game()
game.run()
