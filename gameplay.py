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
import consts, data, utils

GAMEPLAY_READY_TO_FIRE=0
GAMEPLAY_MISSILE_IN_AIR=1
GAMEPLAY_METEOR_EXPLOSION=2
GAMEPLAY_GAME_OVER=3
GAMEPLAY_RETURN_TO_MENU=4
GAMEPLAY_MISSILE_COLLISION=5
GAMEPLAY_INIT_METEOR_EXPLOSION=6
GAMEPLAY_INIT_MISSILE_COLLISION=7

NUM_METEORS=6
PREVIOUS_QUEUE_SIZE=2

GAME_SCREEN_MIN_X = 10
GAME_SCREEN_MIN_Y = 10
GAME_SCREEN_MAX_X = 600
GAME_SCREEN_MAX_Y = 700

GAME_SCREEN_WIDTH=600
GAME_SCREEN_HEIGHT=700

METEOR_BORDER_Y = 600
meteor_container_rect = pygame.Rect((GAME_SCREEN_MIN_X, GAME_SCREEN_MIN_Y), (GAME_SCREEN_WIDTH, METEOR_BORDER_Y))

METEOR_SPRITE_WIDTH=96
EXPLOSION_SPRITE_WIDTH=120

SAVE_BOX_TOP = 610
SAVE_BOX_LEFT = 610
SAVE_BOX_WIDTH = 150
SAVE_BOX_HEIGHT = 75

CRAFT_MOVE=10
MISSILE_MOVE = 12

BAD_HIT_QUEUE_SIZE = 20

ANIMATION_FRAME_COUNT = 8

IMAGE_MISSILE = pygame.image.load("images/missile.png").convert()
IMAGE_MISSILE.set_colorkey((0, 0, 0))
FRAMES_EXPLOSION = pygame.image.load("images/explosion_frames.png").convert()
FRAMES_EXPLOSION.set_colorkey((0, 0, 0))
class Missile:
    def __init__(self, x):
        self.x=x
        self.y=0
        self.exp_x=0
        self.exp_y=0
        r = IMAGE_MISSILE.get_rect()
        self.primary_frame = pygame.Surface((r.width, r.height))
        self.primary_frame.blit(IMAGE_MISSILE, (0, 0))
        self.primary_frame.set_colorkey((0, 0, 0))
        self.reset()
    def width(self):
        return self.primary_frame.get_rect().width
    def setContent(self, text):
        self.primary_frame.blit(IMAGE_MISSILE, (0, 0))
        utils.drawVerticalText(self.primary_frame, text, 
                               int(IMAGE_MISSILE.get_rect().width / 2), 20)
    def reset(self):
        rects = [self.getFullRect()]
        self.is_exploding = False
        self.y=METEOR_BORDER_Y
        self.in_motion=False
        self.min_y=0
        self.colliding_meteor=-1
        return rects
    def setCollidingMeteor(self, index, y):
        self.colliding_meteor = index
        self.min_y = y
    def setExplosion(self, x, y):
        self.is_exploding = True
        self.exp_x = x
        self.exp_y = y
        self.exp_frame = 0
    def getHitRect(self):
        quarter = (int)(self.width() / 4)
        return pygame.Rect((self.x + quarter, self.y + quarter), (quarter * 2, quarter*2))
    def getExplosionRect(self):
        return pygame.Rect((self.exp_x, self.exp_y),
                           (EXPLOSION_SPRITE_WIDTH,
                            FRAMES_EXPLOSION.get_rect().height))
    def getVerticalOffset(self):
        if self.min_y > self.y:
            return self.min_y - self.y
        else:
            return 0
    def getShortenedRect(self):
        r = self.primary_frame.get_rect()
        r.height -= self.getVerticalOffset()
        r.top = self.getVerticalOffset()
        return r
    def getClippedRect(self):
        global meteor_container_rect
        r = self.getShortenedRect()
        del_y = self.y
        r.move_ip(self.x, del_y)
        r = r.clip(meteor_container_rect)
        r.move_ip(-self.x, -del_y)

        return r
    def getCurrentRect(self):
        global meteor_container_rect
        r = self.getShortenedRect()
        r.move_ip(self.x, self.y + self.getVerticalOffset())
        r = r.clip(meteor_container_rect)
        return r
    def getFullRect(self):
        global meteor_container_rect
        r = self.primary_frame.get_rect()
        r.move_ip(self.x, self.y)
        r = r.clip(meteor_container_rect)
        return r
    def checkCollisionStatus(self):
        result = True
        if self.min_y >= self.y + 265:
            result = False
#            self.reset()
        return result
    def getCenterX(self):
        return self.x + (int)(self.primary_frame.get_width() / 2)
    def printReport(self):
        print " MISSILE  loc=(%s, %s), exploding=%s, min_y=%s" % (self.x, self.y, self.is_exploding, self.min_y)
    def onScreen(self):
        return (self.y + 265 > 0)
    def move(self):
        rects = []
        if self.in_motion:
            r = self.getClippedRect()
            r.move_ip(self.x, self.y)
            rects.append(r)
            self.y -= MISSILE_MOVE
        return rects
    def draw(self, surf):
        rects = []
        if self.in_motion:
            rects.append(self.getFullRect())
            r = self.getClippedRect()
            blit_y = self.y + r.top
            surf.blit(self.primary_frame, (self.x, blit_y), r)
        return rects

FRAMES_METEOR = pygame.image.load("images/meteor_frames.png").convert()
FRAMES_METEOR.set_colorkey((0, 0, 0))
class Meteor:
    def __init__(self, x, y):
        self.x=x
        self.y=y
        self.in_motion=1
        self.content=""
        self.row_ind=0  # move to gameplay
        self.primary_frame = pygame.Surface((96, 96))
        self.generateFrames()
    def generateFrames(self):
        self.frames = []
        frame_rect = pygame.Rect((0, 0), (METEOR_SPRITE_WIDTH, METEOR_SPRITE_WIDTH))
        for i in range(0, 8):
            s = pygame.Surface((METEOR_SPRITE_WIDTH, METEOR_SPRITE_WIDTH))
            s.blit(FRAMES_METEOR, (0, 0), frame_rect)
            s.set_colorkey((0, 0, 0))
            frame_rect.move_ip(METEOR_SPRITE_WIDTH, 0)
            self.frames.append(s)
    def setContent(self, c, ri):
        self.content=c
        self.row_ind=ri
        frame_rect = pygame.Rect((0, 0), (METEOR_SPRITE_WIDTH, METEOR_SPRITE_WIDTH))
        self.text = utils.FONT_METEOR.render(self.content, 1, (224, 224, 255))
        self.primary_frame.blit(FRAMES_METEOR, (0, 0), frame_rect)
        blit_x = self.getCenteredOffset(self.text.get_width())
        blit_y = self.getCenteredOffset(self.text.get_height())
        self.primary_frame.blit(self.text, (blit_x, blit_y))
        self.primary_frame.set_colorkey((0, 0, 0))
        self.frames[0] = self.primary_frame
    def getFrame(self, i):
        if i >=0 and i < 8:
            return self.frames[i]
        else:
            return self.frames[7]
    def getHitRect(self):
        global METEOR_SPRITE_WIDTH, METEOR_WIDTH
        quarter = (int)(METEOR_SPRITE_WIDTH / 4)
        return pygame.Rect((self.x + quarter, self.y + quarter), (quarter * 2, quarter*2))
    def getCenteredOffset(self, s):
        global METEOR_SPRITE_WIDTH
        if s > METEOR_SPRITE_WIDTH:
            return 0
        else:
            return (int)((METEOR_SPRITE_WIDTH - s) / 2)
    def getCenteredLeft(self, s):
        return self.x + self.getCenteredOffset(s)
    def getCenteredTop(self, s):
        return self.y + self.getCenteredOffset(s)
    def getTextBlitCoords(self):
        blit_x = self.getCenteredLeft(self.text.get_width())
        blit_y = self.getCenteredTop(self.text.get_height())
        return (blit_x, blit_y)
    def getClippedRect(self):
        global meteor_container_rect
        r = self.primary_frame.get_rect()
        r.move_ip(self.x, self.y)
        r = r.clip(meteor_container_rect)
        r.move_ip(-self.x, -self.y)
        return r
    def getRedrawRect(self):
        r = self.getClippedRect()
        r.move_ip(self.x, self.y)
        return r
    def getCenterX(self):
        return self.x + (int)(self.primary_frame.get_width() / 2)

IMAGE_CRAFT = pygame.image.load("images/spaceship.gif").convert()
IMAGE_CRAFT.set_colorkey((0,0,0))
class Craft:
    def __init__(self, x):
        self.x = x
        self.y = 620
        self.max_x = 600
    def setMaxX(self, save_open):
        if save_open:
            self.max_x = 800
        else:
            self.max_x = 600
    def move(self, direction):
        craft_rect = IMAGE_CRAFT.get_rect()
        r = pygame.Rect((self.x, self.y), (craft_rect.width, craft_rect.height))
        if direction[0] == utils.DIRECTION_LEFT and self.x > CRAFT_MOVE:
            self.x -= CRAFT_MOVE
        elif direction[0] == utils.DIRECTION_RIGHT and self.x + craft_rect.width < self.max_x:
            self.x += CRAFT_MOVE
        return [r]
    def inSave(self):
        return (self.x + IMAGE_CRAFT.get_rect().width > 600)

def getMeteorClippedRect(r, x, y):
    global meteor_container_rect
    res = r.move(x, y)
    res = res.clip(meteor_container_rect)
    res.move_ip(-x, -y)
    return res

class SaveBox:
    def __init__(self):
        self.save_open_counter = utils.FrameCounter(500)
        self.save_closed_counter = utils.FrameCounter(5000)
        self.save_open = False
    def incrementSaveCounters(self):
        res = False
        if self.save_open:
            if self.save_open_counter.up():
                res = True
                self.save_open = False
                self.save_closed_counter.reset()
            else:
                self.save_open_counter.increment()
        else:
            if self.save_closed_counter.up():
                res = True
                self.save_open = True
                self.save_open_counter.reset()
            else:
                self.save_closed_counter.increment()
        return res

class MeteorHistory:
    def __init__(self):
        self.previous_index_choices = []
    def pickAnswerMeteor(self):
        global PREVIOUS_QUEUE_SIZE
        if len(self.previous_index_choices) > PREVIOUS_QUEUE_SIZE:
            new_first = len(self.previous_index_choices) - PREVIOUS_QUEUE_SIZE
            self.previous_index_choices = self.previous_index_choices[new_first:]
        set_valid = set(range(0, 6)) - set(self.previous_index_choices)
        c = random.choice(sorted(set_valid))
        return c
    def addToPreviousIndices(self, c):
        self.previous_index_choices.append(c)

class ShotHistory:
    def __init__(self):
        self.missile_pause = 0
        self.current_missile_pause = 0
        self.bad_hit_queue = []
        self.num_shots = 0
        self.num_correct = 0
    def pauseFraction(self):
        if self.missile_pause > 0:
            return 1.0 - (float(self.current_missile_pause) / float(self.missile_pause))
        else:
            return 1
    def updateBadHitQueue(self, hit_type):
        utils.debugPrint("updateHitQueue")
        self.bad_hit_queue.append(hit_type)
        if len(self.bad_hit_queue) > BAD_HIT_QUEUE_SIZE:
            self.bad_hit_queue = self.bad_hit_queue[1:]
    def decrementMissilePause(self):
        if self.current_missile_pause > 0:
            self.current_missile_pause -=1
    def setMissilePause(self):
        num_bad_hits = 0
        for h in self.bad_hit_queue:
            num_bad_hits += h
        mp = ANIMATION_FRAME_COUNT * (1 + num_bad_hits)
        utils.debugPrint("%s bad hits, setting missile pause to %s" % (num_bad_hits, mp))
        self.missile_pause = mp
        self.current_missile_pause = mp
    def recordCorrect(self):
        utils.debugPrint("recordCorrect")
        self.updateBadHitQueue(0)
        self.setMissilePause()
        self.num_shots += 1
        self.num_correct += 1
    def recordIncorrect(self):
        utils.debugPrint("recordIncorrect")
        self.updateBadHitQueue(1)
        self.setMissilePause()
        self.num_shots += 1
    def getCorrectPercentage(self):
        if self.num_shots == 0:
            return 0
        else:
            return int((self.num_correct * 100) / self.num_shots)


class MeteorData():
    def __init__(self, frame_count):
        self.data = []
        self.should_redraw = False
        self.animation_counter = utils.FrameCounter(frame_count)
    def initialize(self, num_meteors):
        self.data = []
        offsets = []
        current_offset = -METEOR_SPRITE_WIDTH
        for i in range(0, num_meteors):
            offsets.append(current_offset)
            current_offset -= int(METEOR_SPRITE_WIDTH / 2)
        for i in range(0, num_meteors):
            o = random.choice(offsets)
            self.data.append(Meteor((i * 100) + GAME_SCREEN_MIN_X, o))
            offsets.remove(o)
    def size(self):
        return len(self.data)
    def getMeteor(self, i):
        return self.data[i]
    def shouldRedraw(self):
        return self.should_redraw
    def minMovingY(self):
        result=800
        for i in range(0, len(self.data)):
            if self.data[i].in_motion == 1 and self.data[i].y < result:
                result = self.data[i].y
        return result
    def numInMotion(self):
        result=0
        for i in range(0, len(self.data)):
            if self.data[i].in_motion == 1:
                result += 1
        return result
    def pickStationary(self):
        result=0
        found_result=0
        for i in range(0, len(self.data)):
            if self.data[i].in_motion == 0 and found_result == 0:
                result = i
                found_result = 1
        return result
    def move(self):
        rects = []
        if self.animation_counter.up():
            self.should_redraw = True
            self.animation_counter.reset()
            if self.numInMotion() < len(self.data) and self.minMovingY() > 0:
                ind = self.pickStationary()
                self.data[ind].in_motion = 1
            for i in range(0, len(self.data)):
                if self.data[i].in_motion == 1:
                    r = self.data[i].getClippedRect()
                    r.move_ip(self.data[i].x, self.data[i].y)
                    rects.append(r)
                    self.data[i].y += 1
        else:
            self.should_redraw = False
            self.animation_counter.increment()
        return rects

GAME_END_LEFT1 = 100
GAME_END_LEFT2 = 400
GAME_END_DELAY = 40
IMAGE_OK_BUTTON = pygame.image.load("images/ok_button.png").convert()
class GameEndScreen:
    def __init__(self):
        self.texts = []
        self.button_ok = utils.Button(IMAGE_OK_BUTTON)
        self.ready = False
        self.refresh_counter = utils.FrameCounter(4)
        self.initialized = False
        self.visible = False
    def init(self, mastered, unmastered, correct_perc, playtime):
        # only init if there are no texts.
        self.texts = []
        self.current_top = 100
        self.texts.append(utils.PauseText("Play time:", GAME_END_LEFT1, 
                                          self.current_top, GAME_END_DELAY))
        self.texts.append(utils.PauseText(playtime, GAME_END_LEFT2, 
                                          self.current_top, GAME_END_DELAY))
        self.current_top += self.texts[0].get_height()
        self.texts.append(utils.PauseText("Correct:", GAME_END_LEFT1, 
                                          self.current_top, GAME_END_DELAY))
        self.texts.append(utils.PauseText("%s%%" % correct_perc, GAME_END_LEFT2, 
                                          self.current_top, GAME_END_DELAY))
        self.current_top += self.texts[2].get_height()
        self.texts.append(utils.PauseText("Mastered:", GAME_END_LEFT1, 
                                          self.current_top, GAME_END_DELAY))
        self.texts.append(utils.PauseText("%s" % mastered, GAME_END_LEFT2, 
                                          self.current_top, GAME_END_DELAY))
        self.current_top += self.texts[4].get_height()
        self.button_ok.setTopCenter(self.current_top + 20,
                                    meteor_container_rect.centerx)
        self.current_index = 0
        self.ready = True
    def isReady(self):
        return self.ready
    def allUp(self):
        return self.current_index >= len(self.texts)
    def getCurrentText(self):
        return self.texts[self.current_index]
    def increment(self):
        if not self.allUp():
            self.getCurrentText().increment()
            if self.getCurrentText().up():
                self.current_index += 1
    def advance(self):
        if not self.allUp():
            self.getCurrentText().advance()
            if self.getCurrentText().up():
                self.current_index += 1
    def drawInit(self, surf):
        rects = []
        surf.fill((0, 0, 0), meteor_container_rect)
        rects.append(meteor_container_rect)
        return rects
    def draw(self, surf):
        if not self.visible:
            return []
        rects = []
        if not self.initialized:
            self.initialized = True
            rects.extend(self.drawInit(surf))
        max_ind = min(self.current_index + 1, len(self.texts))
        self.refresh_counter.increment()
        refresh = self.refresh_counter.up()
        if refresh:
            self.refresh_counter.reset()
            rects.append(utils.drawHorizontalText(surf, 
                                                  "GAME OVER", 
                                                  GAME_END_LEFT1 + 20,
                                                  GAME_SCREEN_MIN_Y + 20))
            if self.allUp():
                rects.extend(self.button_ok.draw(surf))
        for i in range(0, max_ind):
            rects.extend(self.texts[i].draw(surf, refresh))
        return rects

STATUS_BAR_WIDTH=40
MISSILE_BAR_CORNER = (650, 300)
LIFE_BAR_TOP = 300
LIFE_BAR_LEFT = 700
IMAGE_GUIDE = pygame.image.load("images/control_guide.png").convert()
FRAMES_MISSILE_BAR_RESET = pygame.image.load("images/missile_bar_reset.png").convert()
missile_bar_frames = pygame.image.load("images/missile_bar.png").convert()
life_bar_frames = pygame.image.load("images/life_bar.png").convert()
FRAMES_METEOR_REFRESH = pygame.image.load("images/meteor_refresh.png").convert()
class GameLoop():
    def __init__(self):
        self.input_main = utils.InputEvents(utils.INPUT_MODE_CONTINUOUS)
        self.input_main.setConfirmKeys(utils.INPUT_MODE_DISCRETE)
        self.input_main.setDirectionKeys(utils.INPUT_MODE_CONTINUOUS)
    def reset(self, speed):
        self.meteors = MeteorData(speed)
        self.missile = Missile(0)
        self.craft = Craft(20)
        self.save_box = SaveBox()
        self.end_screen = GameEndScreen()
        self.shot_history = ShotHistory()
        self.meteor_history = MeteorHistory()
        self.life_points = 20
        self.correct_text = ""
        self.correct_meteor_indices = []
        self.error_meteor_indices = []
        self.animation_counter = 0
        self.exploding_meteor_index=6
        self.num_meteors_to_reset=3
        self.is_good_hit=True
        self.animations = []
        self.mastered = set()
        self.unmastered = set()
        self.start_time = time.time()
        self.meteors.initialize(6)
        self.setCorrectIndex(self.meteor_history.pickAnswerMeteor())
        self.missile_reset_pause = 0
        self.missile_reset_indices = range(0, 6)
    def moveMeteors(self):
        self.meteors.move()
    def drawObjects(self, surf, explosion_index):
        rects = []
        for i in range(0, self.meteors.size()):
            add_rect = False
            m = self.meteors.getMeteor(i)
            r = m.getClippedRect()
            if (self.meteors.shouldRedraw() or i == self.missile.colliding_meteor):
                surf.blit(m.getFrame(0), (m.x, m.y + r.top), r)
                add_rect = True
            if add_rect:
                r.move_ip(m.x, m.y)
                rects.append(r)
        for a in self.animations:
            rects.extend(a.draw(surf))
        rects.extend(self.missile.draw(surf))
        rects.append(utils.surfBlit(surf, IMAGE_CRAFT, self.craft.x, self.craft.y))
        return rects
    def drawMissileBarFrame(self, surf, frame):
        height = missile_bar_frames.get_rect().height
        r = pygame.Rect((frame * STATUS_BAR_WIDTH, 0), (STATUS_BAR_WIDTH, height))
        surf.blit(missile_bar_frames, MISSILE_BAR_CORNER, r)
        r.move_ip(MISSILE_BAR_CORNER[0]
                  - (frame * STATUS_BAR_WIDTH),
                  MISSILE_BAR_CORNER[1])
        return [r]
    def drawMissileBarResetFrame(self, surf, frame):
        height = FRAMES_MISSILE_BAR_RESET.get_rect().height
        r = pygame.Rect((frame * STATUS_BAR_WIDTH, 0), (STATUS_BAR_WIDTH, height))
        surf.blit(FRAMES_MISSILE_BAR_RESET, MISSILE_BAR_CORNER, r)
        r.move_ip(MISSILE_BAR_CORNER[0]
                  - (frame * STATUS_BAR_WIDTH),
                  MISSILE_BAR_CORNER[1])
        return [r]
    def drawMissileBar(self, surf, game_state, 
                       full_fraction, missile_reset_pause, 
                       correct_text, force_redraw):
        rects = []
        if full_fraction < 1:
            i_frame = int(33 * full_fraction)
            rects = self.drawMissileBarFrame(surf, i_frame)
        elif missile_reset_pause > 0:
            rects = self.drawMissileBarResetFrame(surf, 15 - self.missile_reset_pause)
        elif force_redraw:
            if game_state == GAMEPLAY_MISSILE_IN_AIR:
                rects = self.drawMissileBarFrame(surf, 0)
            else:
                rects = self.drawMissileBarFrame(surf, 33)
                utils.drawVerticalText(surf, correct_text,
                                       MISSILE_BAR_CORNER[0]
                                       + (STATUS_BAR_WIDTH / 2),
                                       MISSILE_BAR_CORNER[1] + 5)
        return rects
    def drawLifeBar(self, surf):
        rects = []
        height = life_bar_frames.get_rect().height
        r = pygame.Rect((self.life_points * STATUS_BAR_WIDTH, 0), (STATUS_BAR_WIDTH, height))
        surf.blit(life_bar_frames, (LIFE_BAR_LEFT, LIFE_BAR_TOP), r)
        r.move_ip(LIFE_BAR_LEFT - (self.life_points * STATUS_BAR_WIDTH),
                  MISSILE_BAR_CORNER[1])
        rects.append(r)
        return rects
    def drawSaveBox(self, surf, refresh):
        rects = []
        if refresh:
            r = pygame.Rect((SAVE_BOX_LEFT, SAVE_BOX_TOP), (SAVE_BOX_WIDTH, SAVE_BOX_HEIGHT))
            rects.append(r)
            if self.save_box.save_open:
                surf.fill((0, 196, 0), r)
        return rects
    def cleanAnimations(self):
        res = []
        new_animations = []
        for a in self.animations:
            if a.running:
                new_animations.append(a)
            else:
                res.append(a.getCleanRect())
        self.animations = new_animations
        return res
    def pickMeteorsToReset(self):
        result = []
        indices = range(0, self.meteors.size())
        for i in self.error_meteor_indices:
            if i in indices:
                indices.remove(i)
        if self.exploding_meteor_index < self.meteors.size():
            indices.remove(self.exploding_meteor_index)
            result = random.sample(indices, min(self.num_meteors_to_reset-1,
                                                len(indices)))
            result.append(self.exploding_meteor_index)
        else:
            result = random.sample(indices, min(self.num_meteors_to_reset,
                                                len(indices)))
        self.error_meteor_indices = []
        return result
    def setMeteors(self, meteors_to_reset, excluded_rows):
        data.GlobalGameStatus.value.checkNewQueue()
        data.GlobalGameStatus.value.checkWrongQueue()
        data.GlobalGameStatus.value.printQueues()
        data.GlobalGameStatus.value.printReport()
        for i in meteors_to_reset:
            j = data.GlobalGameStatus.value.pick(excluded_rows)
            utils.debugPrint("resetting meteor #%s, got row %s" % (i, j))
            if j == data.BAD_ROW:
                self.meteors.getMeteor(i).setContent("?", data.BAD_ROW)
            else:
                excluded_rows.append(j)
                c = data.GlobalContentData.value.getRow(j).char
                self.meteors.getMeteor(i).setContent(c, j)
        for i in range(0, self.meteors.size()):
            m = self.meteors.getMeteor(i)
            utils.debugPrint("meteor #%s has row index %s, which has status %s"
                             % (i, m.row_ind, data.GlobalGameStatus.value.getStatus(m.row_ind)))
    def resetMeteors(self):
        meteors_to_reset = self.pickMeteorsToReset()
        excluded_rows = []
        for i in range(0, self.meteors.size()):
            row_ind = self.meteors.getMeteor(i).row_ind
            extremes = data.GlobalContentData.value.findCharRange(row_ind)
            excluded_rows.extend(range(extremes[0], extremes[1]))
            excluded_rows.append(row_ind)
        self.setMeteors(meteors_to_reset, excluded_rows)
        for i in meteors_to_reset:
            m = self.meteors.getMeteor(i)
            if i != self.exploding_meteor_index:
                a = utils.Animation(m.x, m.y, FRAMES_METEOR_REFRESH, 8,
                                    meteor_container_rect, False)
                self.animations.append(a)
            else:
                a = utils.Animation(m.x, m.y, FRAMES_METEOR, 8,
                                    meteor_container_rect, False)
                self.animations.append(a)
        self.setCorrectIndex(self.meteor_history.pickAnswerMeteor())
    def setCorrectIndex(self, c):
        utils.debugPrint("correct index is %s" % c)
        row_ind = self.meteors.getMeteor(c).row_ind
        self.correct_text = "%s" % data.GlobalContentData.value.getRow(row_ind).reading
        self.correct_meteor_indices = []
        for i in range(0, self.meteors.size()):
            m = self.meteors.getMeteor(i)
            alt_ind = data.GlobalContentData.value.findAlternateReadingRow(m.row_ind, self.correct_text)
            if alt_ind != data.BAD_ROW:
                utils.debugPrint("for meteor %s, alt_ind = %s" % (i, alt_ind))
                utils.debugPrint("adding index %s to correct answers" % i)
                self.correct_meteor_indices.append(i)
                if alt_ind != m.row_ind:
                    m.setContent(data.GlobalContentData.value.getRow(alt_ind).char, alt_ind)
    def getPlayTime(self):
        return int(max(0, time.time() - self.start_time))
    def getPlayTimeText(self):
        time_diff_secs = self.getPlayTime()
        minutes = int(math.floor(time_diff_secs / 60))
        seconds = time_diff_secs - (minutes * 60)
        if seconds < 10:
            return "%s:0%s" % (minutes, seconds)
        else:
            return "%s:%s" % (minutes, seconds)
    def recordMaster(self, row_ind):
        utils.debugPrint("recordMaster")
        add_set = set([row_ind])
        self.mastered |= add_set
        self.unmastered -= add_set
    def recordUnmaster(self, row_ind):
        utils.debugPrint("recordUnmaster")
        add_set = set([row_ind])
        self.unmastered |= add_set
        self.mastered -= add_set
    def recordHit(self, correct, row_ind, index_mc):
        status = data.GlobalGameStatus.value.getStatus(row_ind)
        self.error_meteor_indices = []
        if correct:
            self.meteor_history.addToPreviousIndices(index_mc)
            # if previously new
            if status == data.SET_NEW:
                self.recordMaster(row_ind)
            data.GlobalGameStatus.value.recordCorrect(row_ind)
            self.shot_history.recordCorrect()
            if self.life_points < 20:
                self.life_points += 1
        else:
            for i in self.correct_meteor_indices:
                self.error_meteor_indices.append(i)
            if index_mc not in self.error_meteor_indices:
                self.error_meteor_indices.append(index_mc)
            # if previously mastered
            if status == data.SET_MASTERED:
                self.recordUnmaster(row_ind)
            data.GlobalGameStatus.value.recordIncorrect(row_ind)
            self.shot_history.recordIncorrect()
    def setExplosion(self, collision_index):
        self.exploding_meteor_index = collision_index
        m = self.meteors.getMeteor(collision_index)
        exp_x = (int)((self.missile.getCenterX() + m.getCenterX()) / 2)
        exp_x -= (int)(EXPLOSION_SPRITE_WIDTH / 2)
        exp_y = m.y + METEOR_SPRITE_WIDTH - (EXPLOSION_SPRITE_WIDTH / 2)
        self.missile.setExplosion(exp_x, exp_y)
        a = utils.Animation(exp_x, exp_y, FRAMES_EXPLOSION, 4,
                            meteor_container_rect, True)
        self.animations.append(a)

    def indexMissileCollision(self):
        result = self.meteors.size()
        r = self.missile.getHitRect()
        for i in range(0, self.meteors.size()):
            if r.colliderect(self.meteors.getMeteor(i).getHitRect()):
                result = i
        return result

    def indexBottomCollision(self):
        result = self.meteors.size()
        found_result = 0
        for i in range(0, self.meteors.size()):
            m = self.meteors.getMeteor(i)
            if m.y > GAME_SCREEN_MIN_Y + METEOR_BORDER_Y - METEOR_SPRITE_WIDTH and found_result == 0:
                found_result = 1
                result = i
        return result

    def stateMissileInAir(self):
        rects = []
        state = GAMEPLAY_MISSILE_IN_AIR
        index_mc = self.indexMissileCollision()
        if index_mc < 6:
            self.exploding_meteor_index = index_mc
            state = GAMEPLAY_INIT_MISSILE_COLLISION
        elif not self.missile.onScreen():
            r = self.missile.getCurrentRect()
            rects.append(self.missile.getCurrentRect())
            rects.extend(self.missile.reset())
            state = GAMEPLAY_READY_TO_FIRE
        else:
            rects.extend(self.missile.move())
        rects.extend(self.meteors.move())
        return (state, rects)
    def stateHitAnimation(self):
        rects = []
        state = GAMEPLAY_METEOR_EXPLOSION
        if self.animation_counter >= ANIMATION_FRAME_COUNT:
            if self.exploding_meteor_index < self.meteors.size():
                m = self.meteors.getMeteor(self.exploding_meteor_index)
                m.y = -METEOR_SPRITE_WIDTH
                rects.append(m.getRedrawRect())
            self.animation_counter = 0
            for a in self.animations:
                a.stop()
            self.resetMeteors()
            rects.append(self.missile.getFullRect())
            rects.extend(self.cleanAnimations())
            rects.extend(self.missile.reset())
            state = GAMEPLAY_READY_TO_FIRE
            self.exploding_meteor_index = self.meteors.size()
        else:
            self.animation_counter += 1
        return (state, rects)
    def stateReadyToFire(self):
        rects = []
        state = GAMEPLAY_READY_TO_FIRE
        self.shot_history.decrementMissilePause()
        if self.missile_reset_pause > 0:
            self.missile_reset_pause -= 1
        index_bc = self.indexBottomCollision()
        if index_bc < self.meteors.size():
            self.life_points -= 10
            state = GAMEPLAY_INIT_METEOR_EXPLOSION
            self.exploding_meteor_index = index_bc
        else:
            rects = self.meteors.move()
        return (state, rects)
    def stateGameOver(self):
        rects = []
        if not self.end_screen.isReady():
            utils.debugPrint("mastered = ")
            utils.debugPrint(self.mastered)
            utils.debugPrint("unmastered = ")
            utils.debugPrint(self.unmastered)
            num_mastered = 0
            for r in self.mastered:
                already_mastered = data.GlobalSaveFile.value.get(r)
                data.GlobalSaveFile.value.set(r, True)
                if not already_mastered:
                    num_mastered += 1
            for r in self.unmastered:
                data.GlobalSaveFile.value.set(r, False)

            self.end_screen.init(num_mastered,
                                 len(self.unmastered),
                                 self.shot_history.getCorrectPercentage(),
                                 self.getPlayTimeText())
            data.GlobalSaveFile.value.addPlayTime(self.getPlayTime())
            self.end_screen.visible = True
        self.end_screen.increment()
        return (GAMEPLAY_GAME_OVER, rects)
    def stateInitMeteorExplosion(self):
        rects = []
        m = self.meteors.getMeteor(self.exploding_meteor_index)
        a = utils.Animation(m.x, m.y, FRAMES_METEOR, 8,
                            meteor_container_rect, False)
        self.animations.append(a)
        return (GAMEPLAY_METEOR_EXPLOSION, rects)
    def stateInitMissileCollision(self):
        index_mc = self.exploding_meteor_index
        m = self.meteors.getMeteor(index_mc)
        missile_min_y = m.y + IMAGE_MISSILE.get_rect().width
        self.missile.setCollidingMeteor(index_mc, missile_min_y)
        if index_mc in self.correct_meteor_indices:
            self.is_good_hit = True
            self.recordHit(True, m.row_ind, index_mc)
            self.setExplosion(index_mc)
        else:
            self.recordHit(False, m.row_ind, index_mc)
            self.is_good_hit = False
        return (GAMEPLAY_MISSILE_COLLISION, [])
    def stateMissileCollision(self):
        rects = []
        state = GAMEPLAY_MISSILE_COLLISION
        if self.is_good_hit:
            rects.append(self.missile.getFullRect())
            self.missile.y -= MISSILE_MOVE
        else:
            rects.append(self.missile.getCurrentRect())
            self.missile.min_y += MISSILE_MOVE
        if not self.missile.checkCollisionStatus():
            for a in self.animations:
                a.stop()
            rects.extend(self.cleanAnimations())
            if self.is_good_hit:
                state = GAMEPLAY_INIT_METEOR_EXPLOSION
            else:
                self.exploding_meteor_index = self.meteors.size()
                rects.extend(self.missile.reset())
                self.resetMeteors()
                state = GAMEPLAY_READY_TO_FIRE
            rects.append(self.missile.getExplosionRect())
        return (state, rects)
    def pickResetMissile(self):
        for i in self.correct_meteor_indices:
            if i in self.missile_reset_indices:
                self.missile_reset_indices.remove(i)
        if len(self.missile_reset_indices) == 0:
            self.missile_reset_indices = range(0, 6)
        reset_index = random.choice(self.missile_reset_indices)
        return reset_index
    def processInput(self, current_state):
        state = current_state
        rects = []
        rects.extend(self.craft.move(self.input_main.getDirection()))
        if current_state == GAMEPLAY_READY_TO_FIRE:
            missile_busy = (self.shot_history.current_missile_pause > 0
                            or self.missile_reset_pause > 0)
            if (self.input_main.xButtonPressed() and not missile_busy):
                self.missile.x = self.craft.x
                self.missile.in_motion=True
                state = GAMEPLAY_MISSILE_IN_AIR
            elif self.input_main.yButtonPressed() and not missile_busy:
                reset_index = self.pickResetMissile()
                self.missile_reset_indices.remove(reset_index)
                self.life_points -= 2
                self.setCorrectIndex(reset_index)
                self.missile_reset_pause = 15
        elif current_state == GAMEPLAY_GAME_OVER:
            if self.end_screen.isReady() and self.input_main.xButtonPressed():
                if self.end_screen.allUp():
                    state = GAMEPLAY_RETURN_TO_MENU
                else:
                    self.end_screen.advance()
        return (state, rects)
    def redrawAll(self, surf, game_state):
        redraw_rects = []
        surf.fill((0, 0, 0))
        surf.fill((64, 64, 64))
        surf.fill((0, 0, 0), meteor_container_rect)
        redraw_rects.extend(self.drawLifeBar(surf))
        redraw_rects.extend(self.drawMissileBar(surf,
                                                game_state, 
                                                self.shot_history.pauseFraction(), 
                                                0,
                                                self.correct_text, 
                                                True))
        redraw_rects.append(surf.get_rect())
        pygame.display.update(redraw_rects)
    def redrawBars(self, surf, game_state):
        redraw_rects = []
        redraw_rects.extend(self.drawLifeBar(surf))
        redraw_rects.extend(self.drawMissileBar(surf,
                                                game_state, 
                                                self.shot_history.pauseFraction(), 
                                                self.missile_reset_pause,
                                                self.correct_text, 
                                                True))
        return redraw_rects
    def run(self, surf):
        keep_going = True
        game_state = GAMEPLAY_READY_TO_FIRE
        loop_res = consts.LOOP_RES_GAME
        is_good_hit = True
        redraw_counter = utils.FrameCounter(10)

        self.setMeteors(range(0, 6), [])
        self.setCorrectIndex(self.meteor_history.pickAnswerMeteor())
        self.redrawAll(surf, game_state)

        clock = pygame.time.Clock()

        while keep_going:

            clock.tick(40)
            redraw_counter.increment()
            redraw_rects = []

            surf.fill((64, 64, 64))
            surf.fill((0, 0, 0), meteor_container_rect)

            
            self.input_main.update()
            if self.input_main.quit:
                loop_res = consts.LOOP_RES_QUIT
                keep_going = False

            if self.craft.x > SAVE_BOX_LEFT or self.life_points <= 0:
                game_state = GAMEPLAY_GAME_OVER

            # handle user input.
            input_res = self.processInput(game_state)
            game_state = input_res[0]
            redraw_rects.extend(input_res[1])

            # handle state-specific stuff
            if game_state == GAMEPLAY_MISSILE_IN_AIR:
                res = self.stateMissileInAir()
            elif game_state == GAMEPLAY_METEOR_EXPLOSION:
                res = self.stateHitAnimation()
            elif game_state == GAMEPLAY_READY_TO_FIRE:
                res = self.stateReadyToFire()
            elif game_state == GAMEPLAY_GAME_OVER:
                res = self.stateGameOver()
            elif game_state == GAMEPLAY_INIT_METEOR_EXPLOSION:
                res = self.stateInitMeteorExplosion()
            elif game_state == GAMEPLAY_MISSILE_COLLISION:
                res = self.stateMissileCollision()
            elif game_state == GAMEPLAY_INIT_MISSILE_COLLISION:
                res = self.stateInitMissileCollision()
            else:
                keep_going = False                
                loop_res = consts.LOOP_RES_MENU
                res = (GAMEPLAY_RETURN_TO_MENU, [])
            game_state = res[0]
            redraw_rects.extend(res[1])

            save_changed = self.save_box.incrementSaveCounters()
            if save_changed:
                self.craft.setMaxX(self.save_box.save_open)
            redraw_rects.extend(self.drawLifeBar(surf))

            if self.craft.inSave():
                redraw_rects.extend(self.drawSaveBox(surf, True))

            if redraw_counter.up():
                redraw_rects.extend(self.drawSaveBox(surf, True))
                redraw_rects.extend(self.redrawBars(surf, game_state))
                redraw_rects.append(utils.surfBlit(surf, IMAGE_GUIDE, 
                                                   MISSILE_BAR_CORNER[0], 50))
                redraw_counter.reset()

            redraw_rects.extend(self.drawMissileBar(surf, game_state, 
                                                    self.shot_history.pauseFraction(), 
                                                    self.missile_reset_pause,
                                                    self.correct_text,
                                                    False))


            if game_state == GAMEPLAY_GAME_OVER or game_state == GAMEPLAY_RETURN_TO_MENU:
                redraw_rects.extend(self.end_screen.draw(surf))
            else:
                redraw_rects.extend(self.drawObjects(surf, 6))

            pygame.display.update(redraw_rects)
        return loop_res

