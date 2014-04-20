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

import data, math, pygame, utils
from consts import *

JUSTIFY_LEFT=0
JUSTIFY_RIGHT=1
IMAGE_MENU_PATTERN = pygame.image.load("images/menu_pattern.png").convert()
IMAGE_MENU_PATTERN.set_colorkey((255, 255, 255))
MENU_NAME_X = 10
MENU_NAME_Y = 10
MENU_OPTION_X = 10
MENU_OPTION_Y = 110
MENU_OPTION_HORIZ_SPACE=30
class OptionMenu:
    def __init__(self, name, options, text_color, bg_color, option_justify, top, screen_width):
        self.name = name
        self.options = options
        self.option_text = []
        self.option_left = []
        self.text_color = text_color
        self.bg_color = bg_color
        self.current_index = 0
        self.option_justify=option_justify
        self.top = top
        self.left = int(screen_width / 2) - int(IMAGE_MENU_PATTERN.get_width() / 2)
        self.surf_cache = {}
    def init(self):
        self.option_left = []
        self.option_text = []
        self.option_left.append(0)
        for i in range(0, len(self.options)):
            text = self.options[i][0]
            text_surf = utils.FONT_TEXT_BIG.render(text, 1, self.text_color)
            self.option_text.append(text_surf)
        for i in range(1, len(self.options)):
            self.option_left.append(self.option_left[i-1] + self.option_text[i-1].get_width() + MENU_OPTION_HORIZ_SPACE)
    def getCurrentValue(self):
        return self.options[self.current_index][1]
    def getBaseSurf(self):
        if self.text_color in self.surf_cache.keys():
            return self.surf_cache[self.text_color]
        else:
            new_surf = pygame.Surface((IMAGE_MENU_PATTERN.get_width(), IMAGE_MENU_PATTERN.get_height()))
            new_surf.fill(self.text_color)
            new_surf.blit(IMAGE_MENU_PATTERN, (0, 0))
            text_surf = utils.FONT_TEXT_BIG.render(self.name, 1, self.text_color)
            label_y = int(new_surf.get_height() / 2) - 10 - text_surf.get_height()
            new_surf.blit(text_surf, (40, label_y))
            self.surf_cache[self.text_color] = new_surf
            return new_surf
    def setColors(self, text_color, bg_color):
        self.text_color = text_color
        self.bg_color = bg_color
    def move(self, direction, surf):
        rects = []
        if self.current_index > 0 and direction == utils.DIRECTION_LEFT:
            rects.append(self.drawOption(self.current_index, False, surf, self.left, self.top))
            rects.append(self.drawOption(self.current_index-1, True, surf, self.left, self.top))
            self.current_index -= 1
        elif self.current_index < len(self.options)-1 and direction == utils.DIRECTION_RIGHT:
            rects.append(self.drawOption(self.current_index, False, surf, self.left, self.top))
            rects.append(self.drawOption(self.current_index+1, True, surf, self.left, self.top))
            self.current_index += 1
        return rects
    def drawOption(self, i, selected, surf, left, top):
        text_surf = self.option_text[i]
        blit_x = left + MENU_OPTION_X + self.option_left[i]
        blit_y = top + MENU_OPTION_Y
        r = text_surf.get_rect()
        r.move_ip(blit_x, blit_y)
        if selected:
            pygame.draw.rect(surf, self.bg_color, r)
        else:
            pygame.draw.rect(surf, (0, 0, 0), r)
        surf.blit(text_surf, (blit_x, blit_y))
        return r
    def drawAll(self, surf):
        rects = []
        base = self.getBaseSurf()
        surf.blit(base, (self.left, self.top))
        for i in range(0, len(self.option_text)):
            selected = (i == self.current_index)
            rects.append(self.drawOption(i, selected, surf, self.left, self.top))
        r = base.get_rect()
        r.move_ip(surf.get_rect().centerx - int(base.get_width() / 2), self.top)
        rects.append(r)
        return rects

def drawSaveData(surf, left, top, color, playtime, mastered):
    rects = []
    label_time = utils.FONT_TEXT_BIG.render("Play time:", 1, color)
    label_mastered = utils.FONT_TEXT_BIG.render("Mastered:", 1, color)
    value_time = utils.FONT_TEXT_BIG.render(utils.getTimeText(playtime), 1, color)
    value_mastered = utils.FONT_TEXT_BIG.render("%s" % mastered, 1, color)
    x_off = max(label_time.get_width(), label_mastered.get_width()) + 10
    y_off = label_time.get_height() + 10
    clear_width = x_off + max(value_time.get_width(), value_mastered.get_width()) + 50
    clear_height = (utils.FONT_TEXT_BIG.get_height() * 2) + 10
    clear_rect = pygame.Rect((left, top),
                             (clear_width, clear_height))
    surf.fill((0, 0, 0), clear_rect)
    rects.append(clear_rect)
    rects.append(utils.surfBlit(surf, label_time, left, top))
    rects.append(utils.surfBlit(surf, label_mastered, left, top + y_off))
    rects.append(utils.surfBlit(surf, value_time, left + x_off, top))
    rects.append(utils.surfBlit(surf, value_mastered, left + x_off, top + y_off))
    return rects

IMAGE_SAVE_FILE_PATTERN = pygame.image.load("images/save_file.png").convert()
class SaveFileDisplay:
    def __init__(self, top, number, empty, time, mastered):
        self.top = top
        self.number = number
        self.empty = empty
        self.time = time
        self.mastered = mastered
        self.color = (0, 0, 0)
        self.surf_cache = {}
    def setColor(self, color):
        self.color = color
    def getSurf(self):
        if self.color not in self.surf_cache.keys():
            new_surf = pygame.Surface((IMAGE_SAVE_FILE_PATTERN.get_width(),
                                       IMAGE_SAVE_FILE_PATTERN.get_height()))
            text_label = utils.FONT_TEXT_BIG.render("Game %s" % self.number, 1, self.color)
            new_surf.blit(text_label, (10, 10))
            if self.empty:
                text_empty = utils.FONT_TEXT_BIG.render("(empty)", 1, self.color)
                new_surf.blit(text_empty, (300, 10))
            else:
                drawSaveData(new_surf, 300, 10, 
                             self.color, self.time, self.mastered)
            self.surf_cache[self.color] = new_surf
        return self.surf_cache[self.color]
    def draw(self, surf):
        rects = []
        draw_surf = self.getSurf()
        r = draw_surf.get_rect()
        r.top = self.top
        r.centerx = surf.get_rect().centerx
        surf.blit(draw_surf, r)
        rects.append(r)
        return rects




COLOR_TEXT_FOCUS = (255, 255, 255)
COLOR_BG_FOCUS = (0, 128, 128)
COLOR_TEXT_NO_FOCUS = (144, 144, 144)
COLOR_BG_NO_FOCUS = (64, 96, 96)
IMAGE_GO_BUTTON = pygame.image.load("images/go_button.png").convert()
IMAGE_TITLE = pygame.image.load("images/title.png").convert()
IMAGE_SAVE_BUTTON = pygame.image.load("images/to_data_button.png").convert()
TITLE_TOP = 20
GO_BUTTON_CORNER = (200, 700)
OPTIONS_GRADE = [("auto", 1),
                 ("1", 1), 
                 ("2", 2),
                 ("3", 3), 
                 ("4", 4), 
                 ("5", 5), 
                 ("6", 6), 
                 ("8", 7), 
                 ("jinmeiyou", 10), 
                 ("advanced", 11)]
OPTIONS_ONKUN = [("all", data.READING_ONYOMI | data.READING_KUNYOMI),
                 ("on", data.READING_ONYOMI),
                 ("kun", data.READING_KUNYOMI)]
OPTIONS_SPEED = [("slow", 3),
                 ("medium", 2),
                 ("fast", 1)]
#MENU_ORDER_GRADE=0
MENU_ORDER_ONKUN=0
MENU_ORDER_SPEED=1
NUM_MENUS=2
class MenuLoop:
    def __init__(self):
        #HACK
        screen_width = 800
        self.onkun_option_menu = OptionMenu("Readings", OPTIONS_ONKUN,
                                            COLOR_TEXT_NO_FOCUS,
                                            COLOR_BG_NO_FOCUS, JUSTIFY_RIGHT,
                                            200, screen_width)
        self.speed_option_menu = OptionMenu("Meteor speed", OPTIONS_SPEED,
                                            COLOR_TEXT_NO_FOCUS,
                                            COLOR_BG_NO_FOCUS, JUSTIFY_RIGHT,
                                            400, screen_width)
        self.button_go = utils.Button(IMAGE_GO_BUTTON)
        self.button_go.setTopCenter(600, int(screen_width / 2))
        self.button_save_file = utils.Button(IMAGE_SAVE_BUTTON)
        self.button_save_file.setUpperRight(0, screen_width)
        self.input = utils.InputEvents(utils.INPUT_MODE_CONTINUOUS)
        self.input.setConfirmKeys(utils.INPUT_MODE_DISCRETE)
        self.input.setDirectionKeys(utils.INPUT_MODE_DISCRETE)
        self.onkun_option_menu.init()
        self.speed_option_menu.init()
        self.setFocus(0, True)
    def getMenu(self, menu_index):
        if menu_index == MENU_ORDER_ONKUN:
            return self.onkun_option_menu
        else:
            return self.speed_option_menu
    def setFocus(self, menu_index, has_focus):
        m = self.getMenu(menu_index)
        if has_focus:
            m.setColors(COLOR_TEXT_FOCUS, COLOR_BG_FOCUS)
        else:
            m.setColors(COLOR_TEXT_NO_FOCUS, COLOR_BG_NO_FOCUS)
        m.init()
    def updateGameStatus(self):
        reading = self.onkun_option_menu.getCurrentValue()
        if int(reading) & data.READING_ONYOMI == 0:
            self.setHiddenSet(data.READING_ONYOMI)
        if int(reading) & data.READING_KUNYOMI == 0:
            self.setHiddenSet(data.READING_KUNYOMI)
    def setHiddenSet(self, reading):
        for i in range (1, 11):
            s = data.GlobalContentData.value.getSet(i, reading)
            data.GlobalGameStatus.value.changeStatus(i, data.SET_HIDDEN, s)
    def setMasteredSet(self, reading, grade):
        for i in range(1, grade):
            s = data.GlobalContentData.value.getSet(i, reading)
            data.GlobalGameStatus.value.changeStatus(i, data.SET_MASTERED, s)
    def getSpeed(self):
        return int(self.speed_option_menu.getCurrentValue())
    def redrawAll(self, surf):
        rects = []
        rects.extend(drawSaveData(surf, 0, 0, (255, 255, 255),
                                  data.GlobalSaveFile.value.getPlayTime(),
                                  data.GlobalSaveFile.value.count()))
        for i in range(0, NUM_MENUS):
            rects.extend(self.getMenu(i).drawAll(surf))
        rects.extend(self.button_go.draw(surf))
        rects.extend(self.button_save_file.draw(surf))
        return rects
    def run(self, surf):
        keep_going = True
        current_menu = 0
        res = LOOP_RES_MENU
        redraw_rects = []
        redraw_counter = utils.FrameCounter(10)

        self.button_go.setHighlight(False)
        self.button_save_file.setHighlight(False)
        self.setFocus(0, True)
        surf.fill((0, 0, 0))
        redraw_rects.extend(self.redrawAll(surf))
        redraw_rects.append(surf.get_rect())
        pygame.display.update(redraw_rects)

        clock = pygame.time.Clock()

        while keep_going:
            clock.tick(40)
            redraw_counter.increment()
            redraw_rects = []

            self.input.update()
            if self.input.quit:
                res = LOOP_RES_QUIT
                keep_going = False

            direction = self.input.getDirection()

            # if direction includes up or down, switch menus.
            # else if direction includes left or right, move within menu.
            # else if enter pressed, go to game mode if on the right button.
            if direction[1] != utils.DIRECTION_NONE:
                if direction[1] == utils.DIRECTION_DOWN:
                    if current_menu < NUM_MENUS-1:
                        if current_menu >= 0:
                            self.setFocus(current_menu, False)
                            redraw_rects.extend(self.getMenu(current_menu).drawAll(surf))
                        else:
                            self.button_save_file.setHighlight(False)
                            redraw_rects.extend(self.button_save_file.draw(surf))
                        self.setFocus(current_menu+1, True)
                        redraw_rects.extend(self.getMenu(current_menu+1).drawAll(surf))
                        current_menu += 1
                    elif current_menu == NUM_MENUS-1:
                        self.setFocus(current_menu, False)
                        redraw_rects.extend(self.getMenu(current_menu).drawAll(surf))
                        self.button_go.setHighlight(True)
                        redraw_rects.extend(self.button_go.draw(surf))
                        current_menu += 1
                elif direction[1] == utils.DIRECTION_UP:
                    if current_menu > 0 and current_menu < NUM_MENUS:
                        self.setFocus(current_menu, False)
                        self.setFocus(current_menu-1, True)
                        redraw_rects.extend(self.getMenu(current_menu).drawAll(surf))
                        redraw_rects.extend(self.getMenu(current_menu-1).drawAll(surf))
                        # completely redraw both
                        current_menu -= 1
                    elif current_menu == 0:
                        self.setFocus(current_menu, False)
                        redraw_rects.extend(self.getMenu(current_menu).drawAll(surf))
                        self.button_save_file.setHighlight(True)
                        redraw_rects.extend(self.button_save_file.draw(surf))
                        current_menu -= 1
                    elif current_menu == NUM_MENUS:
                        self.setFocus(current_menu-1, True)
                        redraw_rects.extend(self.getMenu(current_menu-1).drawAll(surf))
                        self.button_go.setHighlight(False)
                        redraw_rects.extend(self.button_go.draw(surf))
                        current_menu -= 1
            elif direction[0] != utils.DIRECTION_NONE:
                if current_menu < NUM_MENUS:
                    redraw_rects.extend(self.getMenu(current_menu).move(direction[0], surf))
            elif self.input.xButtonPressed():
                if current_menu == NUM_MENUS:
                    self.updateGameStatus()
                    res = LOOP_RES_GAME
                    keep_going = False
                elif current_menu < 0:
                    res = LOOP_RES_SAVE_FILE
                    keep_going = False

            pygame.display.update(redraw_rects)

        return res

class TitleLoop:
    def __init__(self, num_games):
        self.num_games = num_games
        self.current_index = 0
        self.input = utils.InputEvents(utils.INPUT_MODE_CONTINUOUS)
        self.input.setConfirmKeys(utils.INPUT_MODE_DISCRETE)
        self.input.setDirectionKeys(utils.INPUT_MODE_DISCRETE)
    def loadGames(self):
        self.games = []
        for i in range(0, self.num_games):
            filename = data.getSaveFileName(i)
            local_save = data.SaveFile(data.GlobalContentData.value.getNumBitsArray())
            got_file = local_save.readFile(filename)
            self.games.append(SaveFileDisplay(300 + (i * 150),
                                              i + 1,
                                              not got_file, 
                                              local_save.getPlayTime(), 
                                              local_save.count()))
        for i in range(0, len(self.games)):
            if i == 0:
                self.games[i].setColor(COLOR_TEXT_FOCUS)
            else:
                self.games[i].setColor(COLOR_TEXT_NO_FOCUS)
    def getSaveFileName(self):
        return data.getSaveFileName(self.current_index)
    def getSaveFile(self):
        sf = data.SaveFile(data.GlobalContentData.value.getNumBitsArray())
        filename = self.getSaveFileName()
        sf.readFile(filename)
        sf.setFilename(filename)
        return sf
    def drawTitle(self, surf):
        rects = []
        r = IMAGE_TITLE.get_rect()
        r.centerx = surf.get_rect().centerx
        r.top = TITLE_TOP
        surf.blit(IMAGE_TITLE, r)
        rects.append(r)
        return rects
    def redrawAll(self, surf):
        rects = []
        rects.extend(self.drawTitle(surf))
        for i in range(0, len(self.games)):
            rects.extend(self.games[i].draw(surf))
        return rects
    def run(self, surf):
        keep_going = True
        current_menu = 0
        res = LOOP_RES_TITLE
        self.loadGames()
        redraw_rects = []
        redraw_counter = utils.FrameCounter(10)

        surf.fill((0, 0, 0))
        redraw_rects = self.redrawAll(surf)
        redraw_rects.append(surf.get_rect())
        pygame.display.update(redraw_rects)

        clock = pygame.time.Clock()

        while keep_going:
            clock.tick(40)
            redraw_counter.increment()
            redraw_rects = []

            self.input.update()
            if self.input.quit:
                res = LOOP_RES_QUIT
                keep_going = False

            direction = self.input.getDirection()

            if direction[1] != utils.DIRECTION_NONE:
                if direction[1] == utils.DIRECTION_DOWN and current_menu < len(self.games)-1:
                    self.games[current_menu].setColor(COLOR_TEXT_NO_FOCUS)
                    self.games[current_menu+1].setColor(COLOR_TEXT_FOCUS)
                    redraw_rects.extend(self.games[current_menu].draw(surf))
                    redraw_rects.extend(self.games[current_menu+1].draw(surf))
                    current_menu += 1
                elif direction[1] == utils.DIRECTION_UP and current_menu > 0:
                    self.games[current_menu].setColor(COLOR_TEXT_NO_FOCUS)
                    self.games[current_menu-1].setColor(COLOR_TEXT_FOCUS)
                    redraw_rects.extend(self.games[current_menu].draw(surf))
                    redraw_rects.extend(self.games[current_menu-1].draw(surf))
                    current_menu -= 1
            elif self.input.xButtonPressed():
                self.current_index = current_menu
                res = LOOP_RES_MENU
                keep_going = False

            pygame.display.update(redraw_rects)

        return res

GRADE_ALL = 0
GRADE_NONE = 1
GRADE_FILE = 2
class BarData:
    def __init__(self):
        self.redraw = False
        self.state = GRADE_FILE
        self.mod = 3
    def increment(self):
        self.state += 1
        self.state = (self.state % self.mod)
        self.redraw = True
    def decrement(self):
        self.state -= 1
        self.state = (self.state % self.mod)
        self.redraw = True

class GraphData:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.max_grade = 0
        self.max_size = 0
    def setMaxGrade(self, g):
        if g < 5:
            self.max_grade = 5
        elif g >= data.GlobalContentData.value.getNumGrades():
            self.max_grade = data.GlobalContentData.value.getNumGrades() - 1
        else:
            self.max_grade = g
        self.max_size = data.GlobalSaveFile.value.maxSize(self.max_grade)
    def setMaxSize(self, s):
        self.max_size = s
    def getResizeFactor(self):
        if self.max_size > 0:
            return self.width / self.max_size
        else:
            return 0
    def getRowHeight(self):
        return min(int(math.floor(self.height / (self.max_grade + 1))),
                   100)

IMAGE_TITLE_BUTTON = pygame.image.load("images/title_back_button.png").convert()
IMAGE_DELETE_BUTTON = pygame.image.load("images/delete_button.png").convert()
IMAGE_DELETE_CONFIRM_BUTTON = pygame.image.load("images/delete_confirm_button.png").convert()
IMAGE_TO_MENU_BUTTON = pygame.image.load("images/to_menu_button.png").convert()
IMAGE_TOGGLE_BUTTON = pygame.image.load("images/toggle_button.png").convert()
IMAGE_CANCEL_BUTTON = pygame.image.load("images/file_edit_cancel_button.png").convert()
IMAGE_DONE_BUTTON = pygame.image.load("images/file_edit_done_button.png").convert()
IMAGE_TITLE_BUTTON.set_colorkey((0, 0, 0))
IMAGE_DELETE_BUTTON.set_colorkey((0, 0, 0))
IMAGE_DELETE_CONFIRM_BUTTON.set_colorkey((0, 0, 0))
IMAGE_TOGGLE_BUTTON.set_colorkey((0, 0, 0))
IMAGE_CANCEL_BUTTON.set_colorkey((0, 0, 0))
IMAGE_DONE_BUTTON.set_colorkey((0, 0, 0))
COLOR_BAR_UNSELECTED_FRONT = (160, 192, 160)
COLOR_BAR_SELECTED_FRONT = (160, 160, 192)
COLOR_BAR_UNSELECTED_BACK = (64, 64, 64)
COLOR_BAR_SELECTED_BACK = (96, 96, 96)
FOCUS_BUTTONS = 0
FOCUS_GRAPH = 1
RECT_GRAPH = pygame.Rect((0, 100), (800, 600))
class SaveFileLoop:
    def __init__(self):
        #HACK
        screen_width = 800
        self.button_back = utils.Button(IMAGE_TO_MENU_BUTTON)
        self.button_toggle = utils.Button(IMAGE_TOGGLE_BUTTON)
        self.button_title = utils.Button(IMAGE_TITLE_BUTTON)
        self.button_delete = utils.Button(IMAGE_DELETE_BUTTON)
        self.button_confirm_delete = utils.Button(IMAGE_DELETE_CONFIRM_BUTTON)
        self.button_done = utils.Button(IMAGE_DONE_BUTTON)
        self.button_cancel = utils.Button(IMAGE_CANCEL_BUTTON)
        self.button_back.setUpperRight(0, screen_width)
        self.button_toggle.setTopCenter(500, int(screen_width / 2))
        self.button_title.setTopCenter(560, int(screen_width / 2))
        self.button_delete.setTopCenter(620, int(screen_width / 2))
        self.button_cancel.setTopCenter(500, int(screen_width / 2))
        self.button_done.setTopCenter(660, int(screen_width / 2))
        self.button_confirm_delete.setTopCenter(620, int(screen_width / 2))
        self.input = utils.InputEvents(utils.INPUT_MODE_CONTINUOUS)
        self.input.setConfirmKeys(utils.INPUT_MODE_DISCRETE)
        self.input.setDirectionKeys(utils.INPUT_MODE_DISCRETE)
        self.current_index = 0
        self.num_buttons = 3
        self.clear_graph = False
        self.redraw_file = True
        self.toggle_on = False
        self.focus = FOCUS_BUTTONS
        self.graph_data = GraphData(400.00, 400.00)
        self.bar_data = []
        for i in range(0, data.GlobalContentData.value.getNumGrades()):
            self.bar_data.append(BarData())
        self.toggleOff()
    def resetGraphData(self, max_grade):
        self.clear_graph = True
        self.graph_data.setMaxGrade(max_grade)
        for b in self.bar_data:
            b.redraw = True
    def getButton(self, i):
        if self.toggle_on:
            if i == 0:
                return self.button_cancel
            elif i == 1:
                return self.button_done
            else:
                return self.button_back
        else:
            if i == 0:
                return self.button_toggle
            elif i == 1:
                return self.button_title
            elif i == 2:
                return self.button_delete
            else:
                return self.button_back
    def rewriteSaveFile(self):
        for i in range(0, data.GlobalContentData.value.getNumGrades()):
            if self.bar_data[i].state == GRADE_ALL:
                data.GlobalSaveFile.value.setGrade(i, 1)
            elif self.bar_data[i].state == GRADE_NONE:
                data.GlobalSaveFile.value.setGrade(i, 0)
        data.GlobalSaveFile.value.writeFile()
        self.redraw_file = True
    def toggleOn(self):
        self.toggle_on = True
        self.focus = FOCUS_GRAPH
        self.setButtonVisibility()
        for i in range(-1, self.num_buttons):
            self.getButton(i).setHighlight(False)
        for i in range(0, data.GlobalContentData.value.getNumGrades()):
            if data.GlobalSaveFile.value.gradeCount(i) > 0:
                self.bar_data[i].mod = 3
                self.bar_data[i].state = GRADE_FILE
            else:
                self.bar_data[i].mod = 2
                self.bar_data[i].state = GRADE_NONE
        self.current_index = 0
        self.resetGraphData(data.GlobalContentData.value.getNumGrades())
        self.num_buttons = 2
    def toggleOff(self):
        self.toggle_on = False
        for b in self.bar_data:
            b.state = GRADE_FILE
        self.focus = FOCUS_BUTTONS
        self.setButtonVisibility()
        self.resetGraphData(data.GlobalSaveFile.value.maxNonZeroGrade())
        self.num_buttons = 3
    def setButtonVisibility(self):
        self.button_done.setVisible(self.toggle_on)
        self.button_cancel.setVisible(self.toggle_on)
        self.button_toggle.setVisible(not self.toggle_on)
        self.button_title.setVisible(not self.toggle_on)
        self.button_delete.setVisible(not self.toggle_on)
        self.button_confirm_delete.setVisible(False)
        self.button_back.setVisible(True)
    def drawSaveFile(self, surf):
        if self.redraw_file:
            self.redraw_file = False
            return drawSaveData(surf, 0, 0, (255, 255, 255),
                                data.GlobalSaveFile.value.getPlayTime(),
                                data.GlobalSaveFile.value.count())
        else:
            return []
    def drawButtons(self, surf):
        rects = []
        rects.extend(self.button_back.clear(surf))
        rects.extend(self.button_done.clear(surf))
        rects.extend(self.button_cancel.clear(surf))
        rects.extend(self.button_toggle.clear(surf))
        rects.extend(self.button_title.clear(surf))
        rects.extend(self.button_delete.clear(surf))
        rects.extend(self.button_confirm_delete.clear(surf))

        rects.extend(self.button_back.draw(surf))
        rects.extend(self.button_done.draw(surf))
        rects.extend(self.button_cancel.draw(surf))
        rects.extend(self.button_toggle.draw(surf))
        rects.extend(self.button_title.draw(surf))
        rects.extend(self.button_delete.draw(surf))
        rects.extend(self.button_confirm_delete.draw(surf))
        return rects
    def drawGraph(self, surf):
        rects = []
        row_height = self.graph_data.getRowHeight()
        bar_height = row_height - 5
        resize_factor = self.graph_data.getResizeFactor()
        current_top = 100
        if self.clear_graph:
            self.clear_graph = False
            surf.fill((0, 0, 0), RECT_GRAPH)
            rects.append(RECT_GRAPH)
        for i in range(0, self.graph_data.max_grade + 1):
            if self.bar_data[i].redraw:
                self.bar_data[i].redraw = False
                if self.toggle_on and i == self.current_index:
                    front_color = COLOR_BAR_SELECTED_FRONT
                    back_color = COLOR_BAR_SELECTED_BACK
                else:
                    front_color = COLOR_BAR_UNSELECTED_FRONT
                    back_color = COLOR_BAR_UNSELECTED_BACK
                label = utils.FONT_TEXT_SMALL.render(data.GlobalContentData.value.getGradeName(i)
                                                     , 1, (255, 255, 255))
                part = int(data.GlobalSaveFile.value.gradeCount(i)
                           * resize_factor)
                full = int(data.GlobalSaveFile.value.gradeSize(i)
                           * resize_factor)
                if self.bar_data[i].state == GRADE_NONE:
                    part = 0
                elif self.bar_data[i].state == GRADE_ALL:
                    part = full
                rects.extend(self.drawBar(surf, current_top,
                                          100, bar_height,
                                          full, part,
                                          front_color, back_color))
                label_rect = label.get_rect()
                label_rect.centery = current_top + int(bar_height/2)
                rects.append(utils.surfBlit(surf, label, 50,
                                            label_rect.top))
            current_top += row_height
        return rects
    def drawBar(self, surf, top, left, height, full, part,
                front_color, back_color):
        rects = []
        r = pygame.Rect((left, top), (full, height))
        surf.fill(back_color, r)
        r.width = part
        surf.fill(front_color, r)
        r.width = full
        rects.append(r)
        return rects
    def run(self, surf):
        keep_going = True
        current_button = 0
        res = LOOP_RES_TITLE
        delete_pressed = False
        self.redraw_file = True
        redraw_rects = []
        redraw_counter = utils.FrameCounter(10)

        for i in range(-1, self.num_buttons):
            if i == current_button:
                self.getButton(i).setHighlight(True)
            else:
                self.getButton(i).setHighlight(False)

        self.toggle_on = False
        self.toggleOff()

        surf.fill((0, 0, 0))
        redraw_rects.append(surf.get_rect())
        pygame.display.update(redraw_rects)

        clock = pygame.time.Clock()
        self.getButton(0).setHighlight(True)

        while keep_going:
            clock.tick(40)
            redraw_counter.increment()
            redraw_rects = []

            self.input.update()
            if self.input.quit:
                res = LOOP_RES_QUIT
                keep_going = False


            direction = self.input.getDirection()

            if direction[1] != utils.DIRECTION_NONE:
                if self.focus == FOCUS_BUTTONS:
                    if direction[1] == utils.DIRECTION_DOWN and current_button < self.num_buttons - 1:
                        self.getButton(current_button).setHighlight(False)
                        self.getButton(current_button+1).setHighlight(True)
                        current_button += 1
                    elif direction[1] == utils.DIRECTION_UP and current_button > -1:
                        if not self.toggle_on:
                            self.button_confirm_delete.setVisible(False)
                            self.button_delete.setVisible(True)
                            delete_pressed = False
                        self.getButton(current_button).setHighlight(False)
                        self.getButton(current_button-1).setHighlight(True)
                        current_button -= 1
                else:
                    if direction[1] == utils.DIRECTION_DOWN and self.current_index < self.graph_data.max_grade:
                        self.bar_data[self.current_index].redraw = True
                        self.bar_data[self.current_index+1].redraw = True
                        self.current_index += 1
                    elif direction[1] == utils.DIRECTION_UP and self.current_index > 0:
                        self.bar_data[self.current_index].redraw = True
                        self.bar_data[self.current_index-1].redraw = True
                        self.current_index -= 1
            elif direction[0] != utils.DIRECTION_NONE:
                if self.focus == FOCUS_GRAPH:
                    if direction[0] == utils.DIRECTION_LEFT:
                        self.bar_data[self.current_index].decrement()
                    else:
                        self.bar_data[self.current_index].increment()
            elif self.input.xButtonPressed():
                if self.focus == FOCUS_BUTTONS:
                    if current_button == 0:
                        if self.toggle_on:
                            self.toggleOff()
                        else:
                            self.toggleOn()
                    elif current_button == 1:
                        if self.toggle_on:
                            self.rewriteSaveFile()
                            self.toggleOff()
                        else:
                            res = LOOP_RES_TITLE
                            keep_going = False
                    elif current_button == 2:
                        if not delete_pressed:
                            self.button_delete.setVisible(False)
                            self.button_confirm_delete.setVisible(True)
                            delete_pressed = True
                        else:
                            data.GlobalSaveFile.value.writeFileEmpty()
                            res = LOOP_RES_TITLE
                            keep_going = False
                    else:
                        res = LOOP_RES_MENU
                        keep_going = False
                else:
                    self.getButton(0).setHighlight(True)
                    self.focus = FOCUS_BUTTONS
            elif self.input.yButtonPressed():
                if self.focus == FOCUS_BUTTONS and self.toggle_on:
                    self.focus = FOCUS_GRAPH

            redraw_rects.extend(self.drawSaveFile(surf))
            redraw_rects.extend(self.drawButtons(surf))
            redraw_rects.extend(self.drawGraph(surf))
            pygame.display.update(redraw_rects)

        return res
