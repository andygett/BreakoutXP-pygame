import sqlite3
import datetime
import breakodb
def test():
  conn = sqlite3.connect('breakO.db')
  c = conn.cursor()

  # Create table
  #c.execute('''CREATE TABLE stocks
  #             (date text, trans text, symbol text, qty real, price real)''')

  # Insert a row of data
  #c.execute("INSERT INTO stocks VALUES ('2006-01-05','BUY','RHAT',100,35.14)")

  #c.execute("INSERT INTO users VALUES ('DaddyO')")
  #c.execute("INSERT INTO users (Name) VALUES ('DaddyO')")
  #c.execute("INSERT INTO users (Name) VALUES (?)", ('Stoic The Vast'))  # incorrect bindings
  #c.execute("INSERT INTO users VALUES (NULL, ?)", ("Stoic The Vast"))
  c.execute("INSERT INTO Users (Name) VALUES (?)", ("Stoic The Vast",))
  #c.execute("INSERT INTO history (employeeID, time, inout) VALUES (?,?,?)", (q[0],t,x))
  #c.execute("update users set Name='Stoic The Vast'")

  # Save (commit) the changes
  conn.commit()

  # We can also close the connection if we are done with it.
  # Just be sure any changes have been committed or they will be lost.
  conn.close()

def populateEventTypes():
  list={
    ("BrickBounce",	"Ball cleared brick and bounced"),
    ("ScreenBorderHit", "Ball hit side or top"),
    ("PaddleHit", "Ball hit paddle"),
    ("NewBall", "A new ball "),
    ("DeadBall", "Ball fell below paddle"),
    ("MultiBall", "Multi ball powerup")
  }
  conn = sqlite3.connect('breakO.db')
  cur = conn.cursor()
  cur.executemany("insert into EventTypes values (NULL, ?, ?)", list)
  conn.commit()

def populateEventTypes2():
  list={
    ("MultiBallMiss", "Multi ball powerups missed")
  }
  conn = sqlite3.connect('breakO.db')
  cur = conn.cursor()
  cur.executemany("insert into EventTypes values (NULL, ?, ?)", list)
  conn.commit()

def populateEventTypes3():
  list={
    ("WiderPaddles", "Paddle wider powerup"),
    ("ExtraLives", "Extra life powerup"),
    ("SloMo", "Slow down balls powerup"),
    ("BigBalls", "Bigger balls powerup"),
    ("InvincibleBalls", "Ball bounces at bottom of screen"),
    ("RocketBall", "Ball does not bounce when it hits a brick"),
    ("NarrowPaddle", "Narrow paddle power down"),
    ("ReduceThreshold", "Reduce number of bricks required to clear level"),
    ("WiderPaddleMissed", "Paddle wider powerup missed"),
    ("ExtraLiveMissed", "Extra life powerup missed"),
    ("SloMoMissed", "Slow down balls powerup missed"),
    ("BigBallMissed", "Bigger balls powerup missed"),
    ("InvincibleBallMissed", "Ball bounces at bottom of screen missed"),
    ("RocketBallMissed", "Ball does not bounce when it hits a brick missed"),
    ("NarrowPaddleMissed", "Narrow paddle power down missed"),
    ("ReduceThresholdMissed", "Reduce brick threshold  missed"),
    ("StartPause", "Game paused"),
    ("EndPause", "Game resumed")
  }
  conn = sqlite3.connect('breakO.db')
  cur = conn.cursor()
  cur.executemany("insert into EventTypes values (NULL, ?, ?)", list)
  conn.commit()

# v 1.6
def populateEventTypes4():
  list={
    ("PowerupActivated", "Unspecified powerup activated"),
    ("PowerupMissed", "Unspecified powerup missed"),
    ("NoLives", "No Lives Left"),
    ("UserQuit", "User quit with lives left"),
    ("AbnormalEnd", "Unknown")
  }
  conn = sqlite3.connect('breakO.db')
  cur = conn.cursor()
  cur.executemany("insert into EventTypes values (NULL, ?, ?)", list)
  conn.commit()


#populateEventTypes()

def readEventTypes():
  conn = sqlite3.connect('breakO.db')
#  conn.row_factory = sqlite3.Row
  cur = conn.cursor()
  cur.execute("select * from EventTypes")
#  r = cur.fetchone() 
#  all = cur.fetchall()
#  result = [dict(row) for row in cur.fetchall()]
  result = {}
  for row in cur.fetchall():
    result[row[1]] = (row[0], row[2])
  for e in result:
    print (e)
  for i, v in result.items():
    print (v[1], v[0])

def getDbTimeDelta():
  conn = sqlite3.connect(":memory:")
  cur = conn.cursor()
  pyNow=datetime.datetime.now()
  cur.execute("select datetime('now')")
  sqliteNow = cur.fetchone()[0]
  delta =  datetime.datetime.fromisoformat(sqliteNow) - pyNow
  return round(delta.seconds / (60*60))

def restartDb():
  db = breakodb.Db()
  db.restartDb()

#readEventTypes()

#populateEventTypes4()

# restartDb()    # BE CAREFUL WITH THIS.
