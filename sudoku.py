import subprocess as sp
import pygame
import math
from timeit import default_timer as timer
from pygame import display, Surface, sprite, font, Color, Rect
import os
import csv


def main():
    global edit_mode, holding_mb1, dbcT, tClock, logging, gameBoard, auto
    # gameBoard = None
    # Display
    pygame.init()
    display_game = display.set_mode((1000,600))
    display_game.fill(Color("black"))
    
    running = True
    dbcClock = pygame.time.Clock()
    tClock = pygame.time.Clock()
    dbcT = 1000
    logging = False
    auto = False
    cubesize = 60

    gameBoard = GameBoard(cubesize)
    build_UI(cubesize)
    
    # 0 = write full size(tile is that number), 1 = pencil mark (tile can be that number), 2 = strong mark(tile has to be one of these numbers)
    edit_mode = 0  
    holding_mb1 = False
    # entities = _build_Board(cubesize)

    

    while running:
        events = pygame.event.get()

        get_input(dbcClock, events)
        # tiles.update(events)
        gameBoard.draw(display_game)
        # draw_board(gameBoard, cubesize)
        UIs.update(events)
        UIs.draw(display_game)
        display.update()
        display.flip()

def build_UI(cubesize:int):
    global UIs
    
    UIs = sprite.Group()
    
    ui_font = 'Arial'
    mon = display.Info()

    # add UI
    ui_x = mon.current_w - cubesize - 10
    gap = 10
    size_margin = cubesize+gap


    
    UIs.add(ColorButton(cubesize, (ui_x - size_margin*3,  + gap), "", ui_font, Color("grey")))
    UIs.add(ColorButton(cubesize, (ui_x - size_margin*3, size_margin*1 + gap), "", ui_font, Color("green")))
    UIs.add(ColorButton(cubesize, (ui_x - size_margin*3, size_margin*2 + gap), "", ui_font, Color("red")))
    UIs.add(ColorButton(cubesize, (ui_x - size_margin*3, size_margin*3 + gap), "", ui_font, Color("yellow")))

    UIs.add(UIButton(cubesize, (ui_x - size_margin*4, gap), "Mark", ui_font, 1))
    UIs.add(UIButton(cubesize, (ui_x - size_margin*4, size_margin*1 + gap), "SMark", ui_font, 2))
    UIs.add(ClearButton(cubesize, (ui_x - size_margin*4, size_margin*2 + gap), "clear", ui_font))
    UIs.add(CheckButton(cubesize, (ui_x - size_margin*4, size_margin*3 + gap), "Check", ui_font))

    UIs.add(FillCandButton(cubesize, (ui_x - size_margin*2, gap), "FillCand", ui_font))    
    UIs.add(fillValButton(cubesize, (ui_x - size_margin*2, size_margin*1 + gap), "FillVal", ui_font))
    UIs.add(RemCandButton(cubesize, (ui_x - size_margin*2, size_margin*2 + gap), "RemoveCand", ui_font))
    UIs.add(ResetButton(cubesize, (ui_x - size_margin*2, size_margin*5 + gap), "Reset", ui_font))
    UIs.add(SolveButton(cubesize, (ui_x - size_margin*2, size_margin*3 + gap), "Solve", ui_font))


def get_input(dbcClock:pygame.time.Clock, events):
    global holding_mb1
    # events = pygame.event.get()
    mouse_pos = pygame.mouse.get_pos()
    mods = pygame.key.get_mods()
    for event in events:
        if event.type == pygame.QUIT:
            exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                assert isinstance(gameBoard.rect, Rect)
                if gameBoard.rect.collidepoint(mouse_pos):
                    select_tile_at(pygame.mouse.get_pos(), False)
                holding_mb1 = True  
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                # global dbcT
                dbcT = dbcClock.tick()
                holding_mb1 = False
                if dbcT < 300:
                    tile = select_tile_at(event.pos, mods)
                    if isinstance(tile, Tile):
                        tile.select_all()
                else:
                    pass
                select_ui_at(event.pos, mods)

        if event.type == pygame.KEYDOWN:
            if event.unicode in ("1", "2", "3", "4", "5", "6", "7", "8", "9"):
                update_selected(event.unicode)
            if event.key == pygame.K_BACKSPACE:
                for tile in tiles:
                    assert isinstance(tile, Tile)
                    if tile.selected:
                        tile.clear()

    assert isinstance(gameBoard.rect, Rect)
    if holding_mb1 and gameBoard.rect.collidepoint(mouse_pos):
        # assert isinstance(dbcT, int)
        
        tile = select_tile_at(mouse_pos, mods)
        if tile != None:
            tile.select()

def update_selected(string:str):
    for tile in tiles:
        assert isinstance(tile, Tile)
        if tile.selected:
            tile.update_value(string)

def select_tile_at(position:tuple, mods:int):
    t_tile = None
    for tile in tiles:
        assert isinstance(tile, Tile_parent)
        assert isinstance(tile.rect, Rect)
        if tile.rect.collidepoint(position[0]-20, position[1]-20):
            t_tile = tile
        else:
            if mods & pygame.KMOD_ALT:
                pass
            elif not holding_mb1:  # Left ALT
                tile.deselect()
            else:
                pass
            # t_tile = None
    return t_tile

def select_ui_at(position:tuple, mods:int):
    for ui in UIs:
        assert isinstance(ui, Tile_parent)
        assert isinstance(ui.rect, Rect)
        if ui.rect.collidepoint(position):
            if mods & pygame.KMOD_LSHIFT:
                if isinstance(ui, SolveButton):
                    ui.select(True)
                    return
            ui.select()
            return

def getTileAtPos(x, y):
    for tile in tiles:
        assert isinstance(tile, Tile)
        if tile.x == x and tile.y == y:
            return tile
    return

def reset():
    global edit_mode, sudoku, solution
    edit_mode = 0
    for bttn in UIs:
        if isinstance(bttn, UIButton):
            bttn.deselect()
        if isinstance(bttn, CheckButton):
            bttn.deselect()
        else:
            continue

    gameBoard.reset()
    if logging:
        print("----- CLEARED -----")

def check_board():
    if gameBoard.sudoku == gameBoard.solution:            
        for tile in tiles:
            assert isinstance(tile, Tile)
            tile.reset_color()
        return True
    # else:
    validity = None
    for i, tile in enumerate(tiles):
        assert isinstance(tile, Tile)
        if gameBoard.sudoku[i] != gameBoard.solution[i]:
            if tile.value == 0:
                tile.update_color(tile.color_default, True)
            else:
                tile.update_color(Color("red"), True)
                validity = False
                
        elif not tile._locked:
            tile.update_color(Color("green"), True)
    return validity

class Rules():
    def __init__(self) -> None:
        pass

class GameBoard(sprite.Sprite):
    def __init__(self, cubesize:int) -> None:
        self.cubesize = cubesize
        self.ind = 0

        self.image = Surface((cubesize*9, cubesize*9))
        self.image.fill(Color("white"))
        self.color_line = Color("black")

        # Sudoku
        self.sudoku, self.solution = self._get_sudoku_from_qqwing()
        # self.sudoku, self.solution = self.get_sudoku_from_cvs()
        #board
        self.position = (20,20)

        self._build_Board()

        self.update_image()

    def draw(self, surface):
        surface.blit(self.image, self.position)

    def update_image(self):
        self.image = Surface((self.cubesize*9, self.cubesize*9))
        tiles.draw(self.image)
        for i in range(9):
            # add lines
            if i == 0:
                width = 0
            elif i % 3 == 0:
                width = 3
            else:
                width = 1
            pygame.draw.line(self.image, self.color_line,
                            (i*self.cubesize, 0), (i*self.cubesize, self.cubesize*9), width)
            pygame.draw.line(self.image, self.color_line,
                            (0, i*self.cubesize), (self.cubesize*9, i*self.cubesize), width)
        self.rect = self.image.get_rect()

    def _get_sudoku_from_qqwing(self):
        clean_out = []
        filePath = os.path.dirname(os.path.abspath(__file__))
        # difficulties: simple,easy, intermediate, or expert
        with sp.Popen(["node", os.path.join(filePath, "qqwing-1.3.4", "qqwing-main-1.3.4.js") , "--generate", "1", "--one-line", "--solution", "--difficulty", "expert"], stdout=sp.PIPE) as proc:
            assert proc.stdout is not None
            # print(type(proc.stdout))
            out = proc.stdout.readlines()

        if len(out) > 0:
            for sudoku in out:
                cs = sudoku.decode('UTF-8')
                clean_out.append(cs[:-1])
            # clean_out[0] = '093004560060003140004608309981345000347286951652070483406002890000400010029800034'
            # clean_out[1] = "093004560060003140004608309981345000347286951652070483406002890000400010029800034"
            sudoku = clean_out[0].replace(".", "0")
            
            solution = clean_out[1]
        
        else:
            print("empty output")
            sudoku = '.........9.46.7....768.41..3.97.1.8.7.8...3.1.513.87.2..75.261...54.32.8.........'
            solution = '836719524451382679297645813382194765679523148145867392918436257764258931523971486'

        return sudoku, solution

    def _get_sudoku_from_cvs(self):
        with open('sudoku.csv', newline='') as f:
            reader = csv.reader(f)
            print(reader.line_num)
            counter = 0
            for row in reader:
                if counter > self.ind:
                    return row[0], row[1]
                counter +=1
        return '070000043040009610800634900094052000358460020000800530080070091902100005007040802', '679518243543729618821634957794352186358461729216897534485276391962183475137945862'

    def _build_Board(self):
        global tiles, rows, blocks, columns
        tiles = sprite.Group()
        rows = [sprite.Group() for row in range(9)]
        columns = [sprite.Group() for colum in range(9)]
        blocks = [sprite.Group() for block in range(9)]

        tile_font = 'Arial'

        for ind in range(len(self.sudoku)):
                        # add tiles
            tiles.add(
                Tile(self.cubesize, ind, self.sudoku[ind], tile_font))

    def reset(self):
        self.sudoku, self.solution = self._get_sudoku_from_qqwing()
        self.ind +=1
        # self.sudoku, self.solution = self.get_sudoku_from_cvs()
        for i, tile in enumerate(tiles):
            assert isinstance(tile, Tile)
            tile.reset(self.sudoku[i])
        self.update_image()


class Tile_parent(sprite.Sprite):
    def __init__(self, size:int, position:tuple, string:str, font:str) -> None:
        self.position = pygame.Vector2(position)
        sprite.Sprite.__init__(self)
        self.rect = Rect(position, pygame.Vector2(size, size))
        self.bg = Color("white")
        self.color_default = Color("white")
        self.txtfont = pygame.font.SysFont(font, math.floor(size/4))
        self.font = font
        # self._txt_pos = (0, 0)
        self.set_value(string)
        
        self._txt_pos = (self.rect.size[0]/2 - self.txt.get_size()[0]/2,
                         self.rect.size[1]/2 - self.txt.get_size()[1]/2)
        self.selected = False
        self._locked = False
        self.image = Surface(self.rect.size)
        # self.update_sprite()
    def update(self, events):
        pass

        
    def select(self):
        if not self.selected and not self._locked:
            self.selected = True
            self.update_sprite()

    def deselect(self):
        if self.selected and not self._locked:
            self.selected = False
            self.bg = self.color_default
            self.update_sprite()

    def update_sprite(self):
        assert isinstance(self.image, Surface)
        self.image.fill(self.bg)
        self.image.blit(self.txt, self._txt_pos)

        try:
            gameBoard.update_image()
        except:
            pass

    def set_value(self, val:str):
        self.title = val
        
        assert isinstance (self.rect, Rect)
        fontsize = math.floor(self.rect.height/4)
        while self.txtfont.size(val)[0] > self.rect.size[0]:
            fontsize -=1
            self.txtfont = pygame.font.SysFont(self.font, fontsize)
            self.txt = self.txtfont.render(self.title, True, (0, 0, 0))
        self.txt = self.txtfont.render(self.title, True, (0, 0, 0))
        try:
            self.update_sprite()
        except:
            pass

    def update_color(self, color:Color):
        self.bg = color
        self.update_sprite()

class Tile(Tile_parent):
    def __init__(self, size:int, position:int, value:str, tfont: str) -> None:
        self.x = position%9
        self.y = math.floor(position/9)
        super().__init__(
            size, (self.x*size, self.y*size), value, tfont)
        
        self.row = columns[self.y]
        self.column = rows[self.x]
        self.block = blocks[int(self.y/3)*3+int(self.x/3)]
        self.subsets = (self.column, self.row, self.block)
        # print(str(int(self.y/3)*3+int(self.x/3)))
        self.row.add(self)
        self.column.add(self)
        self.block.add(self)

        self.txtfont = font.SysFont(tfont, math.floor(size/2))
        self._penmark_font = font.SysFont(tfont, math.floor(size/4))
        self._spenmark_font = font.SysFont(tfont, math.floor(size/3))
        self.color_clue = Color("lightgrey")
        self.color_rect = Color("red")

        self.value = int(value)
        self.pen_marks = []
        self.spen_marks = []
        self.index = position
        
        marktxt = self._penmark_font.render("0", True, (0, 0, 0))
        markx = marktxt.get_width()
        marky = marktxt.get_height()
        self._pen_positions = [(2, 2), (size-markx -2, 2),
                              (2, size-marky), (size-markx-2, size-marky),
                              (size/2-markx/2, 2), (size/2-markx/2, size-marky),
                              (2, size/2-marky/2), (size-markx-2, size/2-marky/2),
                              (size/2-markx/2, size/2-marky/2)]
        
        self.possibleValueBools = {}
        if self.value == 0:
            self.possibleValues = [i for i in range(1,10)]
            self._locked = False
            self.bg = self.color_default
            
        else:
            self.possibleValues = []
            self._locked = True
            # self.color_default = self.color_clue
            self.bg = self.color_clue

        
        self.update_sprite()

    def update(self):
        if self.selected:
            self.update_sprite()

    def select(self):
        if not self.selected:
            self.selected = True
            self.update_sprite()

    def select_all(self):
        if self.bg != self.color_default and self.bg != self.color_clue:
            for tile in tiles:
                assert isinstance(tile,Tile)
                if tile.bg == self.bg:
                    tile.select()
        elif self.value == 0 and self.pen_marks!=[]:
            for tile in tiles:
                assert isinstance(tile,Tile)
                if all(mark in tile.pen_marks for mark in self.pen_marks):
                    tile.select()
        elif self.value != 0:
            for tile in tiles:
                assert isinstance(tile, Tile)
                if tile.value == self.value or self.value in tile.possibleValues:
                        tile.select()
      
    def deselect(self):
        if self.selected:
            self.selected = False
            self.update_sprite()

    def update_sprite(self):
        assert isinstance(self.rect, Rect)
        self.image = Surface(self.rect.size)
        self.image.fill(self.bg)

        if self.selected:
            pygame.draw.rect(self.image, self.color_rect,
                             self.image.get_rect().move(1, 1).inflate(-1,-1), 3)

        if self.value == 0:
            self.txt = self.txtfont.render("", True, (0, 0, 0))
            for i in range(len(self.pen_marks)):
                marktxt = self._penmark_font.render(str(self.pen_marks[i]), True, (0, 0, 0))
                self.image.blit(marktxt, self._pen_positions[i] )

            sPenStr = ""
            for s in self.spen_marks:
                sPenStr = sPenStr + str(s)
            smarktxt = self._penmark_font.render(sPenStr, True, (0, 0, 0))
            self.image.blit(smarktxt, (self.rect.width/2 - smarktxt.get_width()/2, self.rect.height/2 - smarktxt.get_height()/2))

        else:
            self.txt = self.txtfont.render(str(self.value), True, (0, 0, 0))
        self.image.blit(self.txt, (self.rect.size[0]/2 - self.txt.get_size()[0]/2,
                                   self.rect.size[1]/2 - self.txt.get_size()[1]/2))

        try:
            gameBoard.update_image()
        except:
            pass

    def update_value(self, value: str):
        val = int(value)
        if val is not None and not self._locked:
            if edit_mode == 0:
                if self.value == val:
                    self.value = 0
                elif val in range(0,10):
                    self.value = val

                global sudoku
                if val != 0:
                    # sudoku[self.y*9+self.x] = val
                    
                    gameBoard.sudoku = gameBoard.sudoku[:self.y*9+self.x] + \
                        str(val) + gameBoard.sudoku[self.y*9+self.x + 1:]
                else:
                    sudoku = gameBoard.sudoku[:self.y*9+self.x] + \
                        "0" + gameBoard.sudoku[self.y*9+self.x + 1:]
                pass
                
            elif edit_mode == 1 and self.value == 0:
                if val in self.pen_marks:
                    self.pen_marks.remove(val)
                else:
                    self.pen_marks.append(val)
                self.pen_marks = sorted(self.pen_marks)

            elif edit_mode == 2 and self.value == 0:
                if val in self.spen_marks:
                    self.spen_marks.remove(val)
                else:
                    self.spen_marks.append(val)
                self.spen_marks = sorted(self.spen_marks)
            else:
                return
            self.update_sprite()

    def update_color(self, color: Color, forced = False):
        
        if self.bg == color and not forced:
            self.reset_color()
        else:
            self.bg = color
            self.update_sprite()

    def clear(self):
        if not self._locked:
            self.pen_marks = []
            self.spen_marks = []
            self.possibleValues = []
            self.value = 0
            self.update_sprite()

    def reset(self, value:str):
        self.value = int(value)
        self.pen_marks = []
        self.spen_marks = []
        self.deselect()

        if self.value == 0:
            self.possibleValues = [i for i in range(1,10)]
            self._locked = False
            # self.color_default = Color("white")
            self.bg = self.color_default
        else:
            self.possibleValues = []
            self._locked = True
            self.bg = self.color_clue
        self.update_sprite()

    def reset_color(self):
        if self._locked:
            self.bg = self.color_clue
        else:
            self.bg = self.color_default
        self.update_sprite()

class UIButton(Tile_parent):
    def __init__(self, size:int, position:tuple, string:str, font:str, mode:int) -> None:
        super().__init__(size, position, string, font)
        assert isinstance(self.rect, Rect)
        # self._txt_pos = (self.rect.size[0]/2 - self.txt.get_size()[0]/2,
                        # self.rect.size[1]/2 - self.txt.get_size()[1]/2)
        self.mode = mode
        self.color_selected = Color("green")
        self.update_sprite()

    def select(self, mod=False):
        global edit_mode
        if not self.selected:
            self.selected = True
            edit_mode = self.mode
            self.update_color(self.color_selected)
            for ui in UIs:
                if ui is not self:
                    assert isinstance(ui, Tile_parent)
                    ui.deselect()
        else:
            edit_mode = 0
            self.deselect()

    def deselect(self):
        self.selected = False
        self.update_color(self.color_default)

class ClearButton(Tile_parent):
    def __init__(self, size:int, position:tuple, string:str, font:str) -> None:
        super().__init__(size, position, string, font) 
        assert isinstance(self.rect, Rect)
        # self._txt_pos = (self.rect.size[0]/2 - self.txt.get_size()[0]/2,
        #                  self.rect.size[1]/2 - self.txt.get_size()[1]/2)
        self.update_sprite()

    def select(self, mod=False):
        for tile in tiles:
            assert isinstance(tile, Tile)
            if tile.selected:
                tile.clear()

class ColorButton(Tile_parent):
    def __init__(self, size: int, position: tuple, string: str, font: str, color: Color) -> None:
        super().__init__(size, position, string, font)
        self.bg = color
        self.color_default = color
        self.update_sprite() 

    def select(self, mod=False):
        for tile in tiles:
                assert isinstance(tile, Tile)
                if tile.selected:
                    tile.update_color(self.bg)

class CheckButton(Tile_parent):
    def __init__(self, size:int, position:tuple, string:str, font:str) -> None:
        super().__init__(size, position, string, font)
        assert isinstance(self.rect, Rect)
        
        self.color_correct = Color("green")
        self.color_incorrect = Color("red")

        self.update_sprite()

    def select(self, mod=False):
        # if solution == sudoku:
        self.deselect
        b =check_board()
        if b:
            self.update_color(self.color_correct)
            self.selected = True
        elif b == False:
            self.update_color(self.color_incorrect)
            self.selected = True
        else:
            self.update_color(self.color_default)
            self.selected = False
        self.update_sprite()
        return b
        
class SolveButton(Tile_parent):
    def __init__(self, size:int, position:tuple, string:str, font:str) -> None:
        super().__init__(size, position, string, font)
        self.update_sprite()
        self.numFreeTiles = 0

        for bttn in UIs:
            if isinstance(bttn, RemCandButton):
                self.removeCandBttn = bttn
            elif isinstance(bttn, fillValButton):
                self.fillValBttn = bttn
            elif isinstance(bttn, FillCandButton):
                self.fillcandBttn = bttn
            elif isinstance(bttn, CheckButton):
                self.checkBttn = bttn

    
    def select(self, mod = False):
        if self.fillcandBttn.assignPossibleValues() and not mod:
            return

        before = timer()
        while 1:        # first go through
            if self.fillValBttn.getNext():
                if mod:
                    self.fillcandBttn.assignPossibleValues()
                else:
                    return
            elif self.removeCandBttn.remove_candidates():
                if mod:
                    pass
                else:
                    return
            else:
                if self.checkBttn.select() and auto:
                    reset()
                else:break

            

        
        after = timer()
        print(f"Time to solve: {round(after-before, 4)}s")
                             
    def remove_candidates(self):
        # build a list of the index of the tiles in a block that can have that number
        # self.assignPossibleValues()
        couldRemove = False
        removing = True
        while removing:
            removing = False
            for ib, block in enumerate(blocks):
                for i in range(1,10):
                    possibleTileForVar = []
                    for tile in block:
                        assert isinstance(tile, Tile)
                        if i in tile.possibleValues:
                            possibleTileForVar.append(tile)
                    # see if all of them are in the same row/column
                    if all(element.y == possibleTileForVar[0].y for element in possibleTileForVar) and len(possibleTileForVar) > 1:
                        if len([j for j in possibleTileForVar[0].row if i in j.possibleValues]) == len(possibleTileForVar):
                            continue
                        #remove all instances of the possible values except for those in this box
                        for t in possibleTileForVar[0].row:     
                            if t not in possibleTileForVar:
                                assert isinstance(t, Tile)
                                if i in t.possibleValues:
                                    t.possibleValues.remove(i)
                                    if logging:
                                        print(f"{i} only possible in Box {ib + 1} row {possibleTileForVar[0].y + 1}, therefore removing it from its row")
                                    couldRemove = True
                                    removing = True
                                    t.update_sprite()
                                    
                    if all(element.x == possibleTileForVar[0].x for element in possibleTileForVar) and len(possibleTileForVar) > 1:
                        if len([j for j in possibleTileForVar[0].column if i in j.possibleValues]) == len(possibleTileForVar):
                            continue

                        # remove all instances of the possible values except for those in this box
                        for t in possibleTileForVar[0].column:
                            if t not in possibleTileForVar:
                                assert isinstance(t, Tile)
                                if i in t.possibleValues:
                                    t.possibleValues.remove(i)
                                    if logging:
                                        print(
                                        f"{i} only possible in Box {ib + 1} column {possibleTileForVar[0].x + 1}, therefore removing it from its column")
                                    couldRemove = True
                                    removing = True
                                    t.update_sprite()
        if logging:
            print("--------")
        return couldRemove

class RemCandButton(Tile_parent):
    def __init__(self, size:int, position:tuple, string:str, font:str) -> None:
        super().__init__(size, position, string, font)
        self.update_sprite()
        
    def select(self, mod=False):
        # self.assignPossibleValues()
        if self.remove_candidates():
            pass
        else:
            if logging:
                print("no more")
                             
    def remove_candidates(self):
        # logging = True
        before = timer()
        if self.hiddenSubset():
            hiddenTimer = timer()
            # if logging:
            #     print(f"Hidden: {(hiddenTimer-before)*1000}")
            return True
        hiddenTimer = timer()
        if self.pointingSubset():
            pointingTimer = timer()
            # if logging:
            #     print(f"Pointing: {(pointingTimer-hiddenTimer)*1000}")
            return True
        pointingTimer = timer()
        # elif self.lockedSingle():     #incorporated in pointing subset
        #     return True
        if self.nakedSubset():
            nakedTimer = timer()
            if logging:
                print(f"Naked: {(nakedTimer-pointingTimer)*1000}")
            return True
        nakedTimer = timer()

        if self.xwing():
            xwingTimer = timer()
            if logging:
                print(f"X-Wing: {(xwingTimer-nakedTimer)*1000}")
            return True

        # if logging:
        #     print(f"Hidden: {(hiddenTimer-before)*1000}, Pointing: {(nakedTimer-pointingTimer)*1000}, Naked: {(pointingTimer-hiddenTimer)*1000}")
        return False

    def lockedSingle(self):
        # build a list of the index of the tiles in a block that can have that number
        # self.assignPossibleValues()
        couldRemove = False
        if logging:
            print("removing locked singles...")
        for ib, block in enumerate(blocks):
            for i in range(1,10):
                possibleTileForVar = []
                for tile in block:
                    assert isinstance(tile, Tile)
                    if i in tile.possibleValues:
                        possibleTileForVar.append(tile)
                # see if all of them are in the same row/column
                if all(element.y == possibleTileForVar[0].y for element in possibleTileForVar) and len(possibleTileForVar) > 1:
                    if len([j for j in possibleTileForVar[0].row if i in j.possibleValues]) == len(possibleTileForVar):
                        continue
                    #remove all instances of the possible values except for those in this box
                    if logging:
                        print(f"{i} only possible in Box {ib + 1} row {possibleTileForVar[0].y + 1}, therefore removing it from its row")
                    for t in possibleTileForVar[0].row:     
                        if t not in possibleTileForVar:
                            assert isinstance(t, Tile)
                            if i in t.possibleValues:
                                t.possibleValues.remove(i)
                                
                                couldRemove = True
                                removing = True
                                t.update_sprite()
                    return couldRemove
                                
                if all(element.x == possibleTileForVar[0].x for element in possibleTileForVar) and len(possibleTileForVar) > 1:
                    if len([j for j in possibleTileForVar[0].column if i in j.possibleValues]) == len(possibleTileForVar):
                        continue
                    if logging:
                        print(f"{i} only possible in Box {ib + 1} column {possibleTileForVar[0].x +1}, therefore removing it from its column")
                    # remove all instances of the possible values except for those in this box
                    for t in possibleTileForVar[0].column:
                        assert isinstance(t, Tile)
                        if t not in possibleTileForVar and i in t.possibleValues:
                                t.possibleValues.remove(i)
                                
                                couldRemove = True
                                removing = True
                                t.update_sprite()
                    return couldRemove
        # print("--------")
        return couldRemove

    def nakedSubset(self):
        # wenn in x feldern in einer reihe/spalte/block x mögliche zahlen enthalten, können diese zahlen aus den restlichen felderd der reihe/spalte/block gelöscht werden
        couldRemove = False
        # logging = True
        if logging:
            print("removing naked subsets...")
        counter = 0
        for tile in tiles:
            assert isinstance(tile, Tile)
            if tile.value == 0:# and len(tile.possibleValues) <= 4:
                # length = len(tile.possibleValues)
                for subset in (tile.block, tile.row, tile.column):
                    sameTiles = [tile]
                    for tileCheckAgainst in subset:
                        assert isinstance(tileCheckAgainst, Tile)
                        if tileCheckAgainst.value == 0 and tile != tileCheckAgainst:
                            # if all Values in the other tile are present in the original tile. Original Tile has to be the longer list
                            if all(val in tile.possibleValues for val in tileCheckAgainst.possibleValues):
                                sameTiles.append(tileCheckAgainst)
                
                    if len(sameTiles) == len(tile.possibleValues):
                        for tileRemVal in subset:
                            if tileRemVal in sameTiles:
                                continue
                            assert isinstance(tileRemVal, Tile)
                            for val in tileRemVal.possibleValues:
                                if val in tile.possibleValues:
                                    if logging:
                                        print(f"removing {val} at {tileRemVal.x+1}/{tileRemVal.y+1}")
                                    tileRemVal.possibleValues.remove(val)
                                    tileRemVal.update_sprite()
                                    couldRemove = True
                        if couldRemove:
                            if logging:
                                if subset == tile.block:
                                    print(f"due to naked subset {tile.possibleValues} at block {(int(tile.y/3) * 3) + int(tile.x/3) +1}")
                                elif subset == tile.row:
                                    print(f"due to naked subset {tile.possibleValues} at row {tile.y+1}")
                                elif subset == tile.column:
                                    print(f"due to naked subset {tile.possibleValues} at column {tile.x+1}")
                            return couldRemove

    def hiddenSubset(self):
        couldRemove = False
        if logging:
            print("removing hidden pairs...")
        for group in (blocks, rows, columns):
            for subset in group:        # subset = specific row/column/block
                allTileValues = []      # [[tiles containing 1], [tiles containing 2], [etc]]
                for i in range(1,10):
                    allTileValues.append([tile for tile in subset if isinstance(tile, Tile) and i in tile.possibleValues])
                
                    # enter lists of tiles, which numbers can be in the same tiles
                    # ex: of two tiles have 6 and 2 tiles have 7, see if they are the same
                    # sametiles =  [compareList for j, compareList in enumerate(allTileValues) if i!=j and numberList == compareList]

                # Hidden Pair:
                for i, numberList in enumerate(allTileValues):
                    if len(numberList) <2:
                        continue
                    for j, compareList in enumerate(allTileValues):     #
                        if i!=j and len(compareList) > 1 and all(n in numberList for n in compareList):
                            # print(f"subset in set: {i+1}, {j+1}")
                            return False

                        if i!=j and numberList == compareList and len(compareList) == 2:
                            # if len(sametiles) > 1:
                            
                            for tile in compareList:
                                assert isinstance(tile,Tile)
                                if any(n not in (i+1,j+1) for n in tile.possibleValues):
                                        couldRemove = True
                                        if logging:
                                            print("hidden Pair")
                                            print(f"{i+1}, {j+1}, prev:{tile.possibleValues}")
                                        for n in tile.possibleValues:
                                            if n not in (i+1,j+1):
                                                tile.possibleValues.remove(n)
                                        if logging:
                                            print(f"{tile.possibleValues} at {tile.x+1}, {tile.y+1}")
                                tile.update_sprite()
                        if i!=j and all(n in numberList for n in compareList):
                            pass
                    
        return couldRemove

    def pointingSubset(self):
        couldRemove = False
        if logging:
            print("removing pointing subsets...")
        for tile in tiles:
            assert isinstance(tile, Tile)
            for i in tile.possibleValues:
                for i_ss, subset in enumerate((tile.block, tile.row, tile.column)):
                    numInTiles = [t for t in subset if isinstance(t, Tile) and i in t.possibleValues]


                    if len(numInTiles) > 1:
                        for sub in (tile.block, tile.row, tile.column):
                            if subset == sub:
                                continue
                            if all(t in sub for t in numInTiles):
                                
                                for t in sub:
                                    if isinstance(t, Tile) and i in t.possibleValues and not t in subset:
                                        if logging:
                                            if subset == tile.block:
                                                print(f"removing {i} at block {(int(tile.y/3) * 3) + int(tile.x/3) +1}")
                                            elif subset == tile.row:
                                                print(f"removing {i} at row {tile.y+1}")
                                            elif subset == tile.column:
                                                print(f"removing {i} at column {tile.x+1}")
                                        couldRemove = True
                                        t.possibleValues.remove(i)
                                        t.update_sprite()
                        if couldRemove:
                            if logging:
                                print(f"due to Pointing subset")
                            return couldRemove

                                
                # for sub in (tile.block, tile.row, tile.column):
                #     if all(i in t.possibleValues for t in sub if isinstance(t, Tile))
        return couldRemove

    def xwing(self):
        # logging = True
        if logging:
            print("removing xwing...")
        for i in range(1,10):
            for rootTile in tiles:
                assert isinstance(rootTile, Tile)
                if rootTile.value==0 and i in rootTile.possibleValues:
                    for i_ss, subset in enumerate((rootTile.column, rootTile.row)):
                        tilesWithNum = [t for t in subset if isinstance(t, Tile) and i in t.possibleValues and t != rootTile]
                        
                        if len(tilesWithNum) == 1:      #if there is exactly one other candidate
                            tile2 = tilesWithNum[0]     # second
                            for i_s, sub in enumerate((tile2.column, tile2.row)):
                                if sub == subset:
                                    continue
                                tilesWithNum2 = [t for t in sub if isinstance(t, Tile) and i in t.possibleValues]
                                
                                if len(tilesWithNum2) > 1:
                                    for tile3 in tilesWithNum2:     #third
                                        if tile3.index == tile2.index:
                                            continue
                                        tilesWithNum3 = [t for t in tile3.subsets[i_ss] if isinstance(t, Tile) and i in t.possibleValues and t != tile2 and t!=tile3]
                                        
                                        if len(tilesWithNum3) == 1 and tilesWithNum3[0] in rootTile.subsets[i_s]:
                                            tile4 = tilesWithNum3[0]
                                            tilesWithNum4 = [t for t in tile4.subsets[i_s] if isinstance(t, Tile) and i in t.possibleValues]
                                            
                                            if len(tilesWithNum2) > 2 or len(tilesWithNum4) > 2:    # if there are other Tiles with that Value int the row/column
                                                if logging:
                                                    print(f"XWING {i} at ({rootTile.x+1}, {rootTile.y+1}), ({tile2.x+1}, {tile2.y+1}), ({tile3.x+1}, {tile3.y+1}), ({tile4.x+1}, {tile4.y+1})")
                                                for t in tilesWithNum2:
                                                    if t != tile2 and t != tile3 and i in t.possibleValues:
                                                        t.possibleValues.remove(i)
                                                        t.update_sprite()
                                                        if logging:
                                                            print(f"removing {i} from ({t.x+1}, {t.y+1})")
                                                for t in tilesWithNum4:
                                                    if t != rootTile and t != tile4 and i in t.possibleValues:
                                                        t.possibleValues.remove(i)
                                                        t.update_sprite()
                                                        if logging:
                                                            print(f"removing {i} from ({t.x+1}, {t.y+1})")
                                                return True
        return False
     
class FillCandButton(Tile_parent):
    def __init__(self, size:int, position:tuple, string:str, font:str) -> None:
        super().__init__(size, position, string, font)
        self.update_sprite()
        
    def select(self, mod=False):
        # self.assignPossibleValues()
        self.assignPossibleValues()

    def assignPossibleValues(self):
        couldAssign = False
        if logging:
            print("Assigning Possible Values")
        for rootTile in tiles:
            assert isinstance(rootTile, Tile)
            # rootTile.possibleValues = []
            if rootTile.value == 0:
                for subset in (rootTile.block, rootTile.row, rootTile.column):
                    for tile in subset:
                        assert isinstance(tile, Tile)
                        if tile.value != 0 and tile.value in rootTile.possibleValues:
                            rootTile.possibleValues.remove(tile.value)
                            rootTile.pen_marks = rootTile.possibleValues
                            couldAssign = True
            else:
                rootTile.possibleValues = []
                rootTile.pen_marks = []

            rootTile.update_sprite()
        return couldAssign

class fillValButton(Tile_parent):
    def __init__(self, size:int, position:tuple, string:str, font:str) -> None:
        super().__init__(size, position, string, font)
        self.update_sprite()

    def select(self, mod=False):
        self.getNext()
        
    def getNext(self):
        could_make = False
        lst = self.hiddenSingles()
        if len(lst) > 0:
            could_make = True
        else:
            lst = self.soleCandidate()
        if len(lst) > 0:
            could_make = True
            for i in lst:
                i[0].clear()
                i[0].update_value(str(i[1]))
            # self.removeCand()
        return could_make

    def soleCandidate(self):
        listSoles = []
        if logging:
            print("Finding sole candidates...")
        for tile in tiles:
            assert isinstance(tile, Tile)
            if tile.value == 0:
                if len(tile.possibleValues) == 1:
                    val = tile.possibleValues[0]
                    if logging:
                        print(f"Sole Candidate: ({tile.x+1}, {tile.y+1}): {str(val)}")
                    listSoles.append((tile, val))
        return listSoles

    def hiddenSingles(self):
        listHidden = []
        if logging:
            print("Finding hidden singles...")
        for tile in tiles:
            assert isinstance(tile,Tile)
            if tile.value != 0:
                continue
            for i in tile.possibleValues:
                for subset in tile.subsets:
                    if all(i not in t.possibleValues and i != t.value for t in subset if isinstance(t, Tile) and t != tile):
                        if not (tile, i) in listHidden:
                            if logging:
                                print(f"Hidden Single: ({tile.x+1}, {tile.y+1}): {str(i)}")
                            listHidden.append((tile, i))
        return listHidden

    def removeCand(self, tile:Tile, value:int):
        for t in tile.block:
            assert isinstance(t, Tile)
            if value in t.possibleValues:
                t.possibleValues.remove(value)
                t.update_sprite()
        for t in tile.row:
            assert isinstance(t, Tile)
            if value in t.possibleValues:
                t.possibleValues.remove(value)
                t.update_sprite()
        for t in tile.column:
            assert isinstance(t, Tile)
            if value in t.possibleValues:
                t.possibleValues.remove(value)
                t.update_sprite()

class ResetButton(Tile_parent):
    def __init__(self, size:int, position:tuple, string:str, font:str) -> None:
        super().__init__(size, position, string, font)
        self.update_sprite()
     
    def select(self, mod=False):
        reset()

class SelectRulesButton(Tile_parent):
    def __init__(self, size: int, position: tuple, string: str, font: str) -> None:
        super().__init__(size, position, string, font)
        self.rect = Rect(position, pygame.Vector2(size*2, size))
        self.image = Surface(self.rect.size)

        self.update_sprite()


if __name__ == "__main__":
    main()
