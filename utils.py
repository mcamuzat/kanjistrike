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


from pygame import K_LEFT, K_RIGHT, K_UP, K_DOWN, K_a, K_d, K_w, K_s, K_RETURN, K_SPACE, K_RSHIFT, K_r, KEYDOWN, KEYUP
import pygame.event
from font_filename import FONT_FILENAME
import math

FONT_VERTICAL = pygame.font.Font(FONT_FILENAME, 28)
FONT_METEOR = pygame.font.Font(FONT_FILENAME, 36)
FONT_TEXT_BIG = pygame.font.Font(None, 36)
FONT_TEXT_SMALL = pygame.font.Font(None, 28)

DEBUGGING_ON = False
def debugPrint(x):
    if DEBUGGING_ON:
        print x

# two modes
#   * maintained key down (craft movement)
#   * individual key presses (menu nav)
INPUT_MODE_CONTINUOUS = 0
INPUT_MODE_DISCRETE = 1

class KeyInput():
    def __init__(self, m):
        self.mode = m
        self.down = False
    def setDown(self, d):
        self.down = d
    def getDown(self):
        return self.down
    def clear(self):
        if self.mode == INPUT_MODE_DISCRETE:
            self.down = False

DIRECTION_NONE=0
DIRECTION_LEFT=1
DIRECTION_RIGHT=2
DIRECTION_DOWN=3
DIRECTION_UP=4

class InputEvents():
    def __init__(self, m):
        self.quit = False
        self.mode = m
        self.key_input = {}
        self.clearKeys()
    def clearKeys(self):
        for k in self.key_input.keys():
            self.key_input[k].clear()
    def setDirectionKeys(self, mode):
        self.key_input[K_LEFT] = KeyInput(mode)
        self.key_input[K_RIGHT] = KeyInput(mode)
        self.key_input[K_UP] = KeyInput(mode)
        self.key_input[K_DOWN] = KeyInput(mode)
        self.key_input[K_a] = KeyInput(mode)
        self.key_input[K_d] = KeyInput(mode)
        self.key_input[K_w] = KeyInput(mode)
        self.key_input[K_s] = KeyInput(mode)
    def setConfirmKeys(self, mode):
        self.key_input[K_RETURN] = KeyInput(mode)
        self.key_input[K_SPACE] = KeyInput(mode)
        self.key_input[K_RSHIFT] = KeyInput(mode)
        self.key_input[K_r] = KeyInput(mode)
    def update(self):
        self.clearKeys()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit = True
            elif event.type == KEYDOWN:
                if event.key in self.key_input.keys():
                    self.key_input[event.key].setDown(True)
            elif event.type == KEYUP:
                if event.key in self.key_input.keys():
                    self.key_input[event.key].setDown(False)
    def getDirection(self):
        lr = DIRECTION_NONE
        ud = DIRECTION_NONE
        if (self.directionKeyDown(DIRECTION_LEFT) 
            and not self.directionKeyDown(DIRECTION_RIGHT)):
            lr = DIRECTION_LEFT
        elif (self.directionKeyDown(DIRECTION_RIGHT) 
            and not self.directionKeyDown(DIRECTION_LEFT)):
            lr = DIRECTION_RIGHT

        if (self.directionKeyDown(DIRECTION_DOWN) 
            and not self.directionKeyDown(DIRECTION_UP)):
            ud = DIRECTION_DOWN
        elif (self.directionKeyDown(DIRECTION_UP) 
            and not self.directionKeyDown(DIRECTION_DOWN)):
            ud = DIRECTION_UP
        return (lr, ud)
    def directionKeyDown(self, d):
        if d == DIRECTION_LEFT:
            return (self.keyDown(K_LEFT) or self.keyDown(K_a))
        elif d == DIRECTION_RIGHT:
            return (self.keyDown(K_RIGHT) or self.keyDown(K_d))
        elif d == DIRECTION_UP:
            return (self.keyDown(K_UP) or self.keyDown(K_w))
        elif d == DIRECTION_DOWN:
            return (self.keyDown(K_DOWN) or self.keyDown(K_s))
        else:
            return False
    def keyDown(self, k):
        if k in self.key_input.keys():
            return self.key_input[k].getDown()
        else:
            return False
    def xButtonPressed(self):
        return (self.keyDown(K_RETURN) or self.keyDown(K_SPACE))
    def yButtonPressed(self):
        return (self.keyDown(K_RSHIFT) or self.keyDown(K_r))

class FrameCounter:
    def __init__(self, x):
        self.max = x
        self.current = 0
    def increment(self):
        self.current += 1
    def advance(self):
        self.current = self.max
    def reset(self):
        self.current = 0
    def up(self):
        return (self.current >= self.max)

class Button:
    def __init__(self, i):
        self.image = i
        self.loc_rect = self.image.get_rect()
        self.highlighted = False
        self.redraw = True
        self.visible = True
    def getRect(self):
        r = self.image.get_rect()
        r.height = int(r.height / 2)
        return r
    def setTopCenter(self, t, c):
        self.loc_rect.top = t
        self.loc_rect.centerx = c
    def setUpperRight(self, t, r):
        self.loc_rect.top = t
        self.loc_rect.right = r
    def setHighlight(self, h):
        self.highlighted = h
        self.redraw = True
    def setVisible(self, v):
        self.visible = v
        self.redraw = True
    def drawImpl(self, surf, should_redraw):
        local_rect = self.getRect()
        rects = []
        if self.redraw:
            redraw_rect = self.getRect()
            redraw_rect.move_ip(self.loc_rect.left, 
                                self.loc_rect.top)
            if self.highlighted:
                local_rect.top = local_rect.height
            if self.visible and should_redraw:
                surf.blit(self.image, self.loc_rect, local_rect)
                rects.append(redraw_rect)
                self.redraw = False
            elif not self.visible:
                surf.fill((0, 0, 0), redraw_rect)
                rects.append(redraw_rect)
                self.redraw = False
        return rects
    def clear(self, surf):
        return self.drawImpl(surf, False)
    def draw(self, surf):
        return self.drawImpl(surf, True)

def twoDigitNum(n):
    if n < 10:
        return "0%s" % n
    else:
        return "%s" % n

def getTimeText(time_diff_secs):
    minutes = int(math.floor(time_diff_secs / 60))
    seconds = time_diff_secs - (minutes * 60)
    hours = int(math.floor(minutes / 60))
    minutes -= (hours * 60)
    if hours > 0:
        return "%s:%s:%s" % (hours,
                             twoDigitNum(minutes), twoDigitNum(seconds))
    else:
        return "%s:%s" % (twoDigitNum(minutes), twoDigitNum(seconds))

def surfBlit(to_surf, from_surf, left, top):
    r = from_surf.get_rect()
    r.move_ip(left, top)
    to_surf.blit(from_surf, (left, top))
    return r


def drawVerticalText(surf, text, center, top):
    current_top = top
    for i in range(0, len(text)):
        c = text[i]
        text_surf = FONT_VERTICAL.render(c, 1, (224, 224, 255))
        left = center - (text_surf.get_width() / 2)
        surf.blit(text_surf, (left, current_top))
        current_top += FONT_VERTICAL.get_linesize()

def drawHorizontalText(surf, text, left, top):
    font = pygame.font.Font(None, 48)
    text_surf = font.render(text, 1, (224, 224, 255))
    surf.blit(text_surf, (left, top))
    r = text_surf.get_rect()
    r.move_ip(left, top)
    return r

def getClippedRect(r, container_rect, x, y):
    res = r.move(x, y)
    res = res.clip(container_rect)
    res.move_ip(-x, -y)
    return res

class Animation:
    def __init__(self, x, y, frames, num_frames, container_rect, loop):
        self.x = x
        self.y = y
        self.frames = frames
        self.total_frames = num_frames
        self.current_frame = 0
        self.running = True
        self.loop = loop
        self.container_rect = container_rect
        self.rect = pygame.Rect((0, 0), (frames.get_width() / num_frames, frames.get_height()))
    def stop(self):
        self.running = False
    def draw(self, surf):
        rects = []
        if self.running and self.current_frame >= self.total_frames:
            self.current_frame = 0
            if not self.loop:
                r = self.rect.move(self.x, self.y)
                r = r.clip(self.container_rect)
                rects.append(r)
                self.running = False
        if self.running:
            clipped_rect = getClippedRect(self.rect, self.container_rect,
                                          self.x, self.y)
            frame_rect = clipped_rect.move(self.rect.width * self.current_frame, 0)
            clipped_rect.left += self.x
            clipped_rect.top += self.y
            surf.blit(self.frames,
                      (clipped_rect.left, clipped_rect.top),
                      frame_rect)
            r = self.rect.move(self.x, self.y)
            rects.append(clipped_rect)
            self.current_frame += 1
        return rects
    def getCleanRect(self):
        clipped_rect = getClippedRect(self.rect, self.container_rect,
                                      self.x, self.y)
        clipped_rect.left += self.x
        clipped_rect.top += self.y
        return clipped_rect

class PauseText:
    def __init__(self, text, left, top, delay):
        self.text = text
        self.left = left
        self.top = top
        self.counter = FrameCounter(delay)
        self.redraw_counter = FrameCounter(4)
        self.surf = FONT_TEXT_BIG.render(self.text, 1, (255, 255, 255))
        self.drawn = False
    def get_height(self):
        return self.surf.get_height()
    def increment(self):
        self.counter.increment()
    def advance(self):
        self.counter.advance()
    def up(self):
        return self.counter.up()
    def draw(self, surf, refresh):
        rects = []
        if (not self.drawn) or refresh:
            self.drawn = True
            rects.append(surfBlit(surf, self.surf, self.left, self.top))
        return rects
