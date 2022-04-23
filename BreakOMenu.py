import pygame

try:
  import pygame_menu
  pygame_menuExists = True
except ImportError:
  pygame_menuExists = False 
  print("Install pygame_menu to view menus, change users, etc.\n")

import breakout, breakodb

class BreakOMenu():
  #font = pygame_menu.font.FONT_MUNRO
  #mytheme = pygame_menu.themes.Theme(background_color=(
  #   0, 0, 0, 0), title_shadow=True, title_background_color=(187, 0, 0), widget_font=font, title_font=font)
  
  def __init__(self):
    pygame.init()
    self.db = breakodb.Db()

    self.screen=pygame.display.set_mode(breakout.Game.size)
    self.lastIdUser = int(self.db.getConfigValue("lastIdUser"))
    self.buildMenu()
    self.showMenu()

  def buildMenu(self):
    self.menu = pygame_menu.Menu(
        width=breakout.Game.width, height=breakout.Game.height,
        title='When I break out',
    #    theme=mytheme
    )
    
    items = self.getUsers()
    self.dsUsers = self.menu.add.dropselect("User name", 
      items, 
      default=self.lastUserIndex,    # TODO: get from config file?
      onchange=self.userChange,
      selection_box_height=5,
    )
    
    self.newUser = self.menu.add.text_input("Enter new user name ",
      onchange=self.newUserChange
    )

    self.newUser.hide()
    self.play = self.menu.add.button('Play', self.go)
    self.menu.add.button('Quit', pygame_menu.events.EXIT)

  def newUserChange(self, text):
    if text=="":
      self.play.hide()
    else:
      self.play.show()

  def userChange(self, user, i):
    if user[0][1] == 0:
      self.newUser.show()
      if self.newUser.get_value()=="":
        self.play.hide()
      else:
        self.play.show()
    else:
      self.newUser.hide()
      self.play.show()

    pass

  def getUsers(self):
    userItems=None
    users=self.db.getVisibleUsers()
    userItems = []
    self.lastUserIndex = None
    for i in range(len(users)):
      idUser = users[i][0]
      userItems.append((users[i][1], idUser ), )
      if self.lastIdUser == idUser:
        self.lastUserIndex = i
    userItems.append(( "New User", 0))
    return userItems

  def go(self):
    userItem = self.dsUsers.get_items()[self.dsUsers.get_index()]
    idUser = userItem[1]
    if idUser==0:       # check for new user
      idUser=self.db.insertUser(self.newUser.get_value())
    self.db.setConfigValue("lastIdUser", idUser)
    breakout.Game.play(idUser)
    self.showMenu()

  def showMenu(self):
    self.menu.mainloop(self.screen)

if pygame_menuExists:
  BreakOMenu()
else:
  breakout.Game.play()