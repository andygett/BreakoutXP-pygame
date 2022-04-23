import datetime, pygame

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

class Events():
  def __init__(self, onAdd, evDict):
    self.onAdd = onAdd
    self.evDict = evDict
    self.clear()
    self.gameCache = {}
    self.levelCache = {}

  def clear(self):
    self.details=[]    

  def add(self, eventName):
    if self.onAdd is not None:
      self.onAdd()
    idEvent = self.evDict[eventName][0]
    # characters [0:23] return current time to the second in UTC to match sqlite db time
    dbTime = datetime.datetime.now(datetime.timezone.utc).isoformat()[:23]
    self.details.append((idEvent, dbTime))
    self.gameCache[eventName] = self.gameCache.get(eventName, 0) + 1
    self.levelCache[eventName] = self.levelCache.get(eventName, 0) + 1

