import sqlite3

class Db:
  def __init__(self):
    self.conn = sqlite3.connect('breakO.db')
    self.userStats = None

  def getUsers(self):
    cur = self.conn.cursor()
    cur.execute("select * from Users")
    return cur.fetchall()

  def getUser(self, idUser):
    cur = self.conn.cursor()
    cur.execute("select * from Users where idUser=(?)", (idUser, ))
    return cur.fetchall()

  def insertUser(self, userName):
    cur = self.conn.cursor()
    cur.execute("insert into Users (Name) values (?)", (userName, ))
    self.conn.commit()
    return cur.lastrowid

  def getVisibleUsers(self):
    cur = self.conn.cursor()
    cur.execute("select * from Users WHERE Visible=1")
    return cur.fetchall()

  def newSession(self, idUser):
    if idUser > 0:
      cur = self.conn.cursor()
      cur.execute("insert into Sessions (idUser) values (?)", (idUser, ))
      self.conn.commit()
      return cur.lastrowid
    return 0

  def endSession(self, idSession):
    if (idSession >= 0):
      cur = self.conn.cursor()
      cur.execute("update Sessions set sessionEnd = dateTime('now') where "+
        "idSession=(?)", (idSession, ))
      self.conn.commit()

  def newGame(self, idSession, abnormalEndId):
    if idSession > 0:
      cur = self.conn.cursor()
      cur.execute("insert into Games (idSession, endTrigger) values (?, ?)", 
          (idSession, abnormalEndId))
      self.conn.commit()
      return cur.lastrowid
    return 0

  def endGame(self, idGame, level, endTrigger):
    if (idGame >= 0):
      cur = self.conn.cursor()
      cur.execute(
        "update Games set gameEnd = dateTime('now'), levelReached=(?), endTrigger=(?) " +
        "where idGame=(?)", (level, endTrigger, idGame))
      self.conn.commit()
      # self.userStats = None

  def newLevel(self, idGame, levelNumber):
    if idGame > 0:
      cur = self.conn.cursor()
      cur.execute("insert into Levels (idGame, levelNumber) values (?, ?)",
          (idGame, levelNumber))
      self.conn.commit()
      return cur.lastrowid
    return 0

  def endLevel(self, idLevel, maxBalls, pauseDuration):
    if (idLevel >= 0):
      cur = self.conn.cursor()
      cur.execute(
        """
        update Levels set levelEnd = dateTime('now'), maxBallsInPlay=?, pauseDuration=? 
        where idLevel=(?)        
        """, (maxBalls, pauseDuration, idLevel))
      self.conn.commit()
      self.userStats = None

  def getEventDict(self):
    cur = self.conn.cursor()
    cur.execute("select * from EventTypes")
    evDict = {}
    for row in cur.fetchall():
      evDict[row[1]] = (row[0], row[2])
    return evDict

  def saveEvents(self, idLevel, details):
    sql = "insert into events (idLevel, idEventType, time) values (%d, ?, ?)" % idLevel
    cur = self.conn.cursor()
    cur.executemany(sql, details)
    self.conn.commit()

  def getUserStats(self, idUser):
    if self.userStats is None:
      sql = """
SELECT et.EventName, count(et.idEventType) Times from sessions s 
  inner join games g on g.idSession = s.idSession
  inner join levels on levels.idGame = g.idGame
  inner join Events e on e.idLevel = levels.idLevel
  inner join EventTypes et on et.idEventType = e.idEventType
where s.idUser = (?)
GROUP BY e.idEventType;
      """
      cur = self.conn.cursor()
      cur.execute(sql, (idUser,))
      self.userStats = cur.fetchall()
    return self.userStats

  def getXPDict(self, idUser):
    xp={}
    sql="SELECT  count(s.idSession)  from sessions s "
    where="where idUser=(?) "
    self.xpAdd(xp, sql,where, "Sessions", idUser)

    sql += "inner join games g on g.idSession = s.idSession "
    self.xpAdd(xp, sql,where, "Games", idUser)

    sql += "inner join levels on levels.idGame = g.idGame "
    where += "and Levels.levelEnd not null "
    self.xpAdd(xp, sql,where, "Levels", idUser)
    return xp



    cur = self.conn.cursor()

    tableName="Levels"
    s = "select count(*) from %s where idUser=(?) and levelEnd not null" % tableName
    cur.execute(s, (idUser,))
    xp[tableName]=int(cur.fetchall()[0][0])
  
  def xpAdd(self, xp, sql, where, tableName, idUser):
    cur = self.conn.cursor()
    s = sql + where
    cur.execute(s, (idUser,))
    xp[tableName]=int(cur.fetchall()[0][0])
    
  def getConfigValue(self, setting):
    cur = self.conn.cursor()
    sql="SELECT SettingValue from Config WHERE Setting=(?)"
    cur.execute(sql, (setting,))
    return cur.fetchone()[0]

  def setConfigValue(self, setting, value):
    cur = self.conn.cursor()
    sql="UPDATE Config SET SettingValue = (?) WHERE Setting=(?)"
    cur.execute(sql, (value, setting))
    self.conn.commit()