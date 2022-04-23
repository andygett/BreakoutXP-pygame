# BreakoutXP-pygame

A fun project to ramp up on Python and sqlite.  

BreakoutXP is based on the classic breakout game in which the user moves a paddle to bounce balls up to a wall to hit and destroy the bricks.  BreakoutXP tracks eXperience Points for the current user's game level, game, session and career, persisting these values to the database.  When a ball hits something, you get more XP.  Acquiring powerups increments XP. Clear most (90%) of the blocks to advance to the next level which grants XP.  Each level renders with different colors using a fade-in pattern picked at random.  

![Demo with powerups, level transition](https://user-images.githubusercontent.com/46758459/164893711-6a1ff629-bbb6-4349-b61a-645b96700c9f.gif)

### Powerups

1. Wider paddle *(really paddle width change. It can get smaller!)*
2. Multiball 3-5 balls
3. Extra life
4. SloMo
5. Fire ball - the ball destroys the brick, but does not bounce
6. Invinciballs - all balls bounce back up even if the paddle misses
7. Big ball
8. Highball - Balls only interact with bricks on their way down.

Beware powerups with a red number.

### Keyboard commands during play
1. Left & right arrows move paddle
2. Enter shows stats
3. Esc quits to menu or command prompt depending on start method
4. U and D jump up or down a level - fun for viewing different transitions

## Requirements
* python3 which includes sqlite3
* pygame:
  * Windows install: `py -m pip install -U pygame --user`
  * Mac install: `python3 -m pip install -U pygame --user`

## Optional

pygame-pymenu

## To run from command prompt
1. Without menu, just play the game: `breakout.py`
2. Use menu which allows creating and changing users: `breakomenu.py`
*This "just plays the game" if pygame-menu is not available.*
