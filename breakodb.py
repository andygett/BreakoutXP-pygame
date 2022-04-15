import sqlite3

class Db:
  def __init__(self):
    self.conn = sqlite3.connect('breakO.db')
    self.userStats = None

  def getUsers(self):
    cur = self.conn.cursor()
    cur.execute("select * from Users")
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

  def newGame(self, idSession):
    if idSession > 0:
      cur = self.conn.cursor()
      cur.execute("insert into Games (idSession) values (?)", (idSession, ))
      self.conn.commit()
      return cur.lastrowid
    return 0

  def endGame(self, idGame, level):
    if (idGame >= 0):
      cur = self.conn.cursor()
      cur.execute("update Games set gameEnd = dateTime('now'), levelReached=(?) " +
        "where idGame=(?)", (level, idGame))
      self.conn.commit()
      self.userStats = None


  def getEventDict(self):
    cur = self.conn.cursor()
    cur.execute("select * from EventTypes")
    evDict = {}
    for row in cur.fetchall():
      evDict[row[1]] = (row[0], row[2])
    return evDict

  def saveEvents(self, idGame, details):
    sql = "insert into events (idGame, idEventType, time) values (%d, ?, ?)" % idGame
    cur = self.conn.cursor()
    cur.executemany(sql, details)
    self.conn.commit()

  def getUserStats(self, idUser):
    if self.userStats is None:
      sql = """
SELECT et.EventName, count(et.idEventType) Times from sessions s 
  inner join games g on g.idSession = s.idSession
  inner join Events e on e.idGame = g.idGame
  inner join EventTypes et on et.idEventType = e.idEventType
where s.idUser = (?)
GROUP BY e.idEventType
      """
      cur = self.conn.cursor()
      cur.execute(sql, (idUser,))
      self.userStats = cur.fetchall()
    return self.userStats

