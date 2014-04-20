
import codecs, math, os, random, re, unicodedata

from utils import *

SET_NEW = 0
SET_WRONG = 1
SET_MASTERED = 2
SET_HIDDEN = 3

BAD_ROW = -1

NEW_LOCK_PLAYER = 1
NEW_LOCK_GAME = 2

MAX_NUM_TRIES = 10
MIN_NUM_NEW = 6

ENTRIES_PER_INT = 15

class RowQueue:
    def __init__(self, f):
        self.size_factor=f
        self.data = []
    def remove(self, x):
        if x in self.data:
            self.data.remove(x)
    def add(self, x):
        if x not in self.data:
            self.data.append(x)            
    def size(self):
        return len(self.data)
    def random(self):
        return random.choice(self.data)
    def randomExclude(self, excluded_set):
        debugPrint("randomExclude, set = ")
        debugPrint(self.data)
        data_set = set(self.data)
        valid_set = data_set - set(excluded_set)
        if len(valid_set) > 0:
            r = random.choice(sorted(valid_set))
            self.remove(r)
            return r
        else:
            return BAD_ROW
    def pare(self):
        if len(self.data) > self.size_factor * 3:
            s = len(self.data)
            t = s - self.size_factor * 2
            self.data = self.data[t:]
    def big(self):
        return len(self.data) > self.size_factor * 2
    def small(self):
        return len(self.data) < self.size_factor
    def printReport(self):
        debugPrint(self.data)


class GameStatus:
    def __init__(self):
        self.wrong_queue = RowQueue(6)
        self.new_queue = RowQueue(20)
        self.new_locks = 0
        self.mastered_cutoff=66
        self.grade_level_ind = 0
        self.grade_level_sets = []
        # also add state?
        # also add correct text?
    def checkNewQueue(self):
        # if too small, add in chars starting with the lowest grade.
        debugPrint("checkNewQueue")
        self.new_queue.printReport()
        if self.new_queue.small():
            debugPrint(" new queue is small")
            new_new_set = self.randomSetByStatus(SET_NEW, self.new_queue.data, self.new_queue.size_factor)
            self.new_queue.data.extend(new_new_set)
    def checkWrongQueue(self):
        debugPrint("checkWrongQueue")
        self.wrong_queue.printReport()
        if self.wrong_queue.big():
            self.new_locks |= NEW_LOCK_GAME
        elif self.wrong_queue.small():
            new_wrong_set = self.randomSetByStatus(SET_WRONG, self.wrong_queue.data, self.wrong_queue.size_factor)
            self.wrong_queue.data.extend(new_wrong_set)
            self.new_locks &= NEW_LOCK_PLAYER
        self.wrong_queue.pare()
    def randomSetByStatus(self, s, excluded_list, max_num):
        r = []
        i = 0
        while len(r) < max_num and i < len(self.grade_level_sets):
            num_wanted = max_num - len(r)
            r.extend(self.grade_level_sets[i].randomSetByStatus(s, excluded_list, num_wanted))
            i += 1
        return r
    def randomMastered(self):
        debugPrint("randomMastered")
        return randomByStatus(self, SET_MASTERED)
    def randomNew(self, excluded_set):
        debugPrint("randomNew")
        r = self.new_queue.randomExclude(excluded_set)
        return r
    def randomWrong(self, excluded_rows):
        debugPrint("randomWrong")
        r = BAD_ROW
        r = self.wrong_queue.randomExclude(excluded_rows)
        if r == BAD_ROW:
            return self.randomByStatusExclude(SET_WRONG, excluded_rows)
        else:
            return r
    def randomByStatus(self, s):
        num_rows = 0
        not_found = True
        result = BAD_ROW
        for gls in self.grade_level_sets:
            num_rows += gls.sizeByStatus(s)

        if num_rows > 0:
            r = random.randint(0, num_rows-1)
            debugPrint("for status %s, randomByStatus returns row %s out of %s total rows" % (s, r, num_rows))
            rows_acc = 0
            for gls in self.grade_level_sets:
                rows_acc += gls.sizeByStatus(s)
                if r < rows_acc and not_found:
                    not_found = False
                    sorted_set = sorted(gls.sets[s])
                    index = rows_acc - r
                    if index < len(sorted_set):
                        result = sorted_set[index]
        return result
    def randomByStatusExclude(self, s, excluded_set):
        ok = False
        num_tries = 0
        result = BAD_ROW
        while num_tries < MAX_NUM_TRIES and not ok:
            r = self.randomByStatus(s)
            if r not in excluded_set:
                result = r
                ok = True
            num_tries += 1
        return result
    def randomAll(self, ind, excluded_rows):
        debugPrint("randomAll")
        max_ind = self.grade_level_sets[ind].end_row_ind
        debugPrint("max ind = %s" % max_ind)
        r = random.randint(0, max_ind - 1)
        num_tries = 0
        while num_tries < MAX_NUM_TRIES and r in excluded_rows:
            r = random.randint(0, max_ind - 1)
            num_tries += 1
        return r
    def maxIndWithStatus(self, s):
        res = 0
        done = False
        while i < len(self.grade_level_sets) and not done:
            if self.grade_level_sets[i].sizeByStatus(s) > 0:
                res = i
            else:
                done = True
        return res
    def pick(self, excluded_rows):
        s = self.whichSet()        
        debugPrint("pick, s = %s" % s)
        j = BAD_ROW
        if s == SET_WRONG:
            j = self.randomWrong(excluded_rows)
        elif s == SET_NEW:
            j = self.randomNew(excluded_rows)
        else:
            j = self.randomByStatusExclude(s, excluded_rows)
        if j == BAD_ROW:
            if self.grade_level_sets[0].sizeByStatus(SET_NEW) > MIN_NUM_NEW:
                j = self.randomNew(excluded_rows)
            else:
                max_ind = self.maxIndWithStatus(SET_MASTERED)
                j = self.randomAll(max_ind, excluded_rows)
        return j
    def whichSet(self):
        r = random.randint(0, 99)
        if r < self.mastered_cutoff:
            return SET_MASTERED
        else:
            if self.new_locks > 0:
                return SET_WRONG
            else:
                s = random.randint(0,1)
                if s == 1 and self.wrong_queue.size() > 0:
                    return SET_WRONG
                else:
                    return SET_NEW
    def recordCorrect(self, row_ind):
        debugPrint("recordCorrect")
        if row_ind != BAD_ROW:
            i = self.getGradeIndex(row_ind)
            if i < len(self.grade_level_sets):
                self.grade_level_sets[i].recordCorrect(row_ind)
    def recordIncorrect(self, row_ind):
        debugPrint("recordIncorrect")
        if row_ind != BAD_ROW:
            self.wrong_queue.add(row_ind)
            i = self.getGradeIndex(row_ind)
            if i < len(self.grade_level_sets):
                self.grade_level_sets[i].recordIncorrect(row_ind)
    def getGradeIndex(self, row_ind):
        result = len(self.grade_level_sets)
        for i in range(0, len(self.grade_level_sets)):
            if row_ind < self.grade_level_sets[i].end_row_ind and row_ind >= self.grade_level_sets[i].begin_row_ind:
                result = i
        return result
    def addRow(self, ri, g):
        add_ind = len(self.grade_level_sets)
        for i in range(0, len(self.grade_level_sets)):
            if self.grade_level_sets[i].grade == g:
                add_ind = i
        if add_ind >= len(self.grade_level_sets):
            add_ind = len(self.grade_level_sets)
            self.grade_level_sets.append(GradeLevelSet(g))
        self.grade_level_sets[add_ind].addNew(ri)
    def getStatus(self, row_ind):
        grade = self.getGradeIndex(row_ind)
        return self.grade_level_sets[grade].getStatus(row_ind)
    def printReport(self):
        for gls in self.grade_level_sets:
            gls.printReport()
    def printQueues(self):
        self.new_queue.printReport()
        self.wrong_queue.printReport()
    def changeStatus(self, grade, status, add_set):
        debugPrint("changeStatus")
        for i in range(0, len(self.grade_level_sets)):
            if self.grade_level_sets[i].grade == grade:
                self.grade_level_sets[i].addSetToStatusSet(status, add_set)

class GlobalGameStatus:
    value = GameStatus()

READING_NULL=0
READING_ONYOMI=1
READING_KUNYOMI=2
def getReadingType(r):
    res = READING_NULL
    if len(r) > 0:
        c = r[0]
        res = READING_KUNYOMI
        if ord(c) > 12448 and ord(c) < 12543:
            res = READING_ONYOMI
    return res

class ContentRow:
    def __init__(self, c, r, g):
        self.char = c
        self.reading = r
        self.grade = int(g)
        self.reading_type = getReadingType(r)

class ContentData:
    def __init__(self):
        self.rows = []
        self.sets = {}
        self.grade_data = []
        self.grade_names = []
    def init(self, filename):
        f = codecs.open(filename, 'r', 'utf-16')
        try:
            grade = 0
            for line in f:
                reg_exp = re.compile('\s+')
                line_els = reg_exp.split(line)
                if len(line_els) >= 2:
                    if line_els[0] == u'grade':
                        grade = int(line_els[1])
                        self.grade_data.append((grade, 0))
                        if len(line_els) > 2:
                            self.grade_names.append(line_els[2])
                        else:
                            self.grade_names.append("?")
                    elif grade > 0 and len(line_els[1]) > 0:
                        self.rows.append(ContentRow(line_els[0], line_els[1], grade))
        finally:
            f.close()
        for i in range(0, len(self.rows)):
            k = (self.rows[i].grade, self.rows[i].reading_type)
            if k not in self.sets.keys():
                print "adding set for key (%s, %s)" % (k[0], k[1])
                self.sets[k] = set()
            self.sets[k] |= set([i])
        for i in range(0, len(self.grade_data)):
            grade = self.grade_data[i][0]
            set_size = (len(self.getSet(grade, READING_ONYOMI))
                        + len(self.getSet(grade, READING_KUNYOMI)))
            self.grade_data[i] = (grade, set_size)
    def getNumGrades(self):
        return len(self.grade_data)
    def getGradeName(self, i):
        if i < len(self.grade_names):
            return self.grade_names[i]
        else:
            return "?"
    def getNumBitsArray(self):
        res = []
        for i in range(0, len(self.grade_data)):
            res.append(self.grade_data[i][1])
        return res
    def getSet(self, grade, reading_type):
        k = (grade, reading_type)  
        if k in self.sets.keys():
            return self.sets[k]
        else:
            return set()
    def getRow(self, row_ind):
        return self.rows[row_ind]
    def size(self):
        return len(self.rows)
    def findAlternateReadingRow(self, row_ind, r):
        c = self.rows[row_ind].char
        i = row_ind
        result = BAD_ROW
        while i > 0 and self.rows[i].char == c:
            i -= 1
        if self.rows[i].char != c:
            i += 1
        while i < len(self.rows) and self.rows[i].char == c:
            if self.rows[i].reading == r:
                result = i
            i += 1
        return result
    def findCharRange(self, row_ind):
        c = self.rows[row_ind].char
        max = row_ind
        min = row_ind
        keep_going = True
        while keep_going:
            keep_going = False
            if min > 0:
                if self.rows[min-1].char == c:
                    min -= 1
                    keep_going = True
        keep_going = True
        while keep_going:
            keep_going = False
            if max < len(self.rows)-1:
                if self.rows[max+1].char == c:
                    max += 1
                    keep_going = True
        return (min, max+1)

class GlobalContentData:
    value = ContentData()

class GradeLevelSet:
    def __init__(self, g):
        self.grade = int(g)
        self.sets = {}
        self.sets[SET_NEW] = set()
        self.sets[SET_WRONG] = set()
        self.sets[SET_MASTERED] = set()
        self.sets[SET_HIDDEN] = set()
        self.sizes = {}
        self.sizes[SET_NEW] = 0
        self.sizes[SET_WRONG] = 0
        self.sizes[SET_MASTERED] = 0
        self.sizes[SET_HIDDEN] = 0
        self.begin_row_ind=BAD_ROW
        self.end_row_ind=BAD_ROW
    def addNew(self, row_ind):
        self.addToStatusSet(SET_NEW, row_ind)
        if self.begin_row_ind == BAD_ROW:
            self.begin_row_ind = row_ind
        if self.end_row_ind == BAD_ROW:
            self.end_row_ind = row_ind
        self.end_row_ind+=1
        self.sizes[SET_NEW] += 1
    def addToStatusSet(self, s, row_ind):
        add_set = set([row_ind])
        self.sets[s] = self.sets[s] | add_set
    def removeFromStatusSet(self, s, row_ind):
        remove_set = set([row_ind])
        self.sets[s] = self.sets[s] - remove_set
    def sizeByStatus(self, s):
        return len(self.sets[s])
    def inSet(self, row_ind):
        return row_ind >= self.begin_row_ind and row_ind < self.end_row_ind
    def getStatus(self, row_ind):
        res = SET_NEW
        for k in self.sets.keys():
            if row_ind in self.sets[k]:
                res = k
        return res
    def setStatus(self, row_ind, status):
        i = int((row_ind - self.begin_row_ind) / ENTRIES_PER_INT)
        j = (row_ind - self.begin_row_ind) % ENTRIES_PER_INT
        mask = int((1 << (2 * ENTRIES_PER_INT + 1)) - 1)
        mask -= (3 << (j * 2))
    def addSetToStatusSet(self, status, add_set):
        for k in self.sets.keys():
            if k == status:
                self.sets[k] |= add_set
            else:
                self.sets[k] -= add_set
    def recordCorrect(self, row_ind):
        s = self.getStatus(row_ind)
        new_status = SET_MASTERED
        if s != SET_MASTERED:
            if row_ind in self.sets[s]:
                self.removeFromStatusSet(s, row_ind)
            if s == SET_WRONG:
                new_status = SET_NEW
            self.setStatus(row_ind, new_status)
            self.addToStatusSet(new_status, row_ind)
    def recordIncorrect(self, row_ind):
        s = self.getStatus(row_ind)
        if s != SET_WRONG:
            self.sizes[s] -= 1
            self.sizes[SET_WRONG] += 1
            if row_ind in self.sets[s]:
                self.removeFromStatusSet(s, row_ind)
            self.setStatus(row_ind, SET_WRONG)
            self.addToStatusSet(SET_WRONG, row_ind)
    def randomSetByStatus(self, s, exclude_list, max_num):
        exclude_set = set(exclude_list)
        valid_set = self.sets[s] - exclude_set
        if len(valid_set) > max_num:
            return random.sample(sorted(valid_set), max_num)
        else:
            return sorted(valid_set)
    def randomRowByStatus(self, s, exclude_set):
        num_tries=0
        excluded = True
        index = self.begin_row_ind
        set_len = len(self.sets[s])
        if set_len > 0:
            # alternate case when the set is large:
            # choose len(exclude_set)+1
            while num_tries < MAX_NUM_TRIES and excluded:
                num_tries += 1
                index = random.choice(sorted(self.sets[s]))
                if index not in exclude_set:
                    excluded=False
        if excluded:
            index = BAD_ROW
        return index
    def randomRowAll(self, exclude_set):
        num_tries=0
        excluded = True
        debugPrint("randomRowAll")
        index = self.begin_row_ind
        if self.end_row_ind - self.begin_row_ind > 1:
            while num_tries < MAX_NUM_TRIES and excluded:
                num_tries += 1
                index = random.randint(self.begin_row_ind, self.end_row_ind-1)
                if index not in exclude_set:
                    excluded=False
        return index
    def printReport(self):
        debugPrint("for grade %s:  %s new | %s wrong | %s mastered | %s hidden"  % (self.grade, 
                                                                                    len(self.sets[SET_NEW]), 
                                                                                    len(self.sets[SET_WRONG]), 
                                                                                    len(self.sets[SET_MASTERED]),
                                                                                    len(self.sets[SET_HIDDEN])))
class HexString:
    def __init__(self, num_bits):
        self.data = []
        for i in range(0, int(math.ceil(num_bits / 4)) + 1):
            self.data.append('0')
    def size(self):
        return len(self.data)
    def numBits(self):
        return self.size() * 4
    def count(self):
        res = 0
        for i in range(0, len(self.data) * 4):
            if self.get(i):
                res += 1
        return res
    def get(self, index):
        char_ind = int(math.floor(index / 4.0))
        bit_ind = index % 4
        num = int(self.data[char_ind], 16)
        return (num & (1 << bit_ind) > 0)
    def set(self, index, val):
        char_ind = int(math.floor(index / 4.0))
        bit_ind = index % 4
        num = int(self.data[char_ind], 16)
        if val:
            num = (num | 1 << bit_ind)
        else:
            num = num - (num & (1 << bit_ind))
        self.data[char_ind] = "%X" % num
    def toString(self):
        res = ""
        for c in self.data:
            res += c
        return res
    def fromString(self, s):
        if len(self.data) == len(s):
            for i in range(0, len(s)):
                self.data[i] = s[i]
    def getRelativeArray(self):
        res = []
        for i in range(0, len(self.data) * 4):
            if self.get(i):
                res.append(i)
        return res



#make a function that is & over two hex strings
#use this to filter out on or kun rows

#initialize a list with grades and how many rows they contain
#get numbers for graph
class SaveFile:
    def __init__(self, num_bit_array):
        self.grade_strings = []
        for i in range(0, len(num_bit_array)):
            self.grade_strings.append(HexString(num_bit_array[i]))
        self.num_bits_array = num_bit_array
        self.play_time = 0
        self.filename = ""
    def numGrades(self):
        return len(self.grade_strings)
    def setFilename(self, f):
        self.filename = f
    def count(self):
        res = 0
        for gs in self.grade_strings:
            res += gs.count()
        return res
    def getGradeOffset(self, g):
        if g < len(self.grade_strings):
            result = 0
            for i in range(0, g):
                result += self.num_bits_array[i]
            return result
        else:
            return 0
    def getMasteredSet(self, g):
        if g < len(self.grade_strings):
            grade_offset = self.getGradeOffset(g)
            relative_array = self.grade_strings[g].getRelativeArray()
            for i in range(0, len(relative_array)):
                relative_array[i] += grade_offset
            return set(relative_array)
        else:
            return set()
    def maxNonZeroGrade(self):
        res = 0
        for i in range(0, len(self.grade_strings)):
            if self.grade_strings[i].count() > 0:
                res = i
        return res
    def maxSize(self, max_ind):
        size = 0
        i = 0
        while i <= max_ind:
            if size < self.num_bits_array[i]:
                size = self.num_bits_array[i]
            i += 1
        return size
    def maxCount(self):
        res = 0
        for gs in self.grade_strings:
            if gs.count() > res:
                res = gs.count()
        return res
    def gradeCount(self, i):
        if i < len(self.grade_strings):
            return self.grade_strings[i].count()
        else:
            return 0
    def gradeSize(self, i):
        if i < len(self.num_bits_array):
            return self.num_bits_array[i]
        else:
            return 0
    def setGrade(self, i, val):
        for j in range(0, self.grade_strings[i].numBits()):
            self.grade_strings[i].set(j, val)
    def getLocation(self, row_ind):
        r = row_ind
        res = (-1, -1)
        found = False
        i = 0
        while i < len(self.num_bits_array) and not found:
            if r < self.num_bits_array[i]:
                found = True
                res = (i, r)
            else:
                r -= self.num_bits_array[i]
            i += 1
        return res
    def get(self, row_ind):
        location = self.getLocation(row_ind)
        if location[0] >= 0:
            return self.grade_strings[location[0]].get(location[1])
        else:
            return False
    def addPlayTime(self, t):
        self.play_time += t
    def getPlayTime(self):
        return self.play_time
    def set(self, row_ind, val):
        location = self.getLocation(row_ind)
        if location[0] >= 0:
            self.grade_strings[location[0]].set(location[1], val)
    def readFile(self, filename):
        result = False
        if os.path.isfile(filename):
            result = True
            f = codecs.open(filename, 'r')
            try:
                i = 0
                for line in f:
                    reg_exp = re.compile('\s+')
                    line_els = reg_exp.split(line)
                    if len(line_els) > 0:
                        if line_els[0] == 'empty':
                            result = False
                    if len(line_els) >= 1:
                        if line_els[0] == 'time' and len(line_els) >= 2:
                            self.play_time = int(line_els[1])
                        if line_els[0] == 'row' and len(line_els) >= 3:
                            if i < len(self.grade_strings):
                                self.grade_strings[i].fromString(line_els[2])
                            i += 1
            finally:
                f.close()
        return result
    def writeFile(self):
        f = codecs.open(self.filename, 'w')
        line = "time %s\n" % self.play_time
        f.write(line)
        for i in range(0, len(self.grade_strings)):
            line = "row %s %s\n" % (GlobalContentData.value.getGradeName(i),
                                    self.grade_strings[i].toString())
            f.write(line)
        f.close()
    def writeFileEmpty(self):
        f = codecs.open(self.filename, 'w')
        f.write("empty\n")
        f.close()

class GlobalSaveFile:
    value = 0
    def init(content_data):
        GlobalSaveFile.value = SaveFile(content_data.getNumBitsArray())
    init = staticmethod(init)

def getSaveFileName(i):
    return "game%s.txt" % i
