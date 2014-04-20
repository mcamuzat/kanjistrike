#    Kanji Strike - game to learn kanji readings
#    Copyright (C) 2008-2009  Kimberly Dorn

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

#    Contact email: kkdorn@gmail.com


import math, pygame, random, time
from pygame.locals import *

pygame.init()
screen = pygame.display.set_mode((800, 700))
pygame.display.set_caption("Kanji Strike v1.0")

import data, font_filename, gameplay, menus, utils
from font_filename import FONT_FILENAME
from data import BAD_ROW
from consts import *

IMAGE_LOADING = pygame.image.load("images/loading.png").convert()
r = IMAGE_LOADING.get_rect()
r.centerx = screen.get_rect().centerx
r.centery = screen.get_rect().centery
screen.fill((0, 0, 0))
screen.blit(IMAGE_LOADING, r)
pygame.display.update()

data.GlobalContentData.value.init('kanji_records.txt')

data.GlobalSaveFile.init(data.GlobalContentData.value)

game_loop = gameplay.GameLoop()
menu_loop = menus.MenuLoop()
title_loop = menus.TitleLoop(2)
save_file_loop = menus.SaveFileLoop()

def resetGameStatus():
    data.GlobalGameStatus.value = data.GameStatus()
    for i in range(0, data.GlobalContentData.value.size()):
        data.GlobalGameStatus.value.addRow(i, data.GlobalContentData.value.getRow(i).grade)
    for i in range(data.GlobalSaveFile.value.numGrades()):
        s = data.GlobalSaveFile.value.getMasteredSet(i)
        data.GlobalGameStatus.value.changeStatus(i + 1,
                                                 data.SET_MASTERED,
                                                 s)

loop_res = LOOP_RES_TITLE
while loop_res != LOOP_RES_QUIT:

    if loop_res == LOOP_RES_MENU:
        loop_res = menu_loop.run(screen)

    elif loop_res == LOOP_RES_GAME:
        speed = menu_loop.getSpeed()
        game_loop.reset(speed)
        loop_res = game_loop.run(screen)
        data.GlobalSaveFile.value.writeFile()

    elif loop_res == LOOP_RES_TITLE:
        # THIS CODE IS OPAQUE.  REWRITE
        loop_res = title_loop.run(screen)
        data.GlobalSaveFile.value = title_loop.getSaveFile()
        resetGameStatus()
#        for i in range(data.GlobalSaveFile.value.numGrades()):
#            s = data.GlobalSaveFile.value.getMasteredSet(i)
#            data.GlobalGameStatus.value.changeStatus(i + 1,
#                                                     data.SET_MASTERED,
#                                                     s)
    elif loop_res == LOOP_RES_SAVE_FILE:
        loop_res = save_file_loop.run(screen)
        resetGameStatus()
    else:
        loop_res = LOOP_RES_QUIT
