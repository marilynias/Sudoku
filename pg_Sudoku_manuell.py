import subprocess as sp
import pygame
import math
from timeit import default_timer as timer
from pygame import display, Surface, sprite, font, Color, Rect
import os
import csv










class GameBoard(sprite.Sprite):
    def __init__(self, cubesize:int = 10, sud=None, sol=None) -> None:
        pygame.init()
        self.display_game = display.set_mode((1000,600))
        self.display_game.fill(Color("black"))
        
        self.running = True
        self.dbcClock = pygame.time.Clock()
        self.tClock = pygame.time.Clock()
        self.dbcT = 1000
        self.auto = False
        self.cubesize = 60

        self.build_UI()
        
        # 0 = write full size(tile is that number), 1 = pencil mark (tile can be that number), 2 = strong mark(tile has to be one of these numbers)
        self.edit_mode = 0  
        self.holding_mb1 = False


        self.ind = 0

        self.image = Surface((cubesize*9, cubesize*9))
        self.image.fill(Color("white"))
        self.color_line = Color("black")

        # Sudoku
        if sud and sol:
            self.sudoku, self.solution = sud, sol
        else:
            self.sudoku, self.solution = self.get_next_sudoku()
        # self.sudoku, self.solution = self.get_sudoku_from_cvs()
        #board
        self.position = (20,20)

        self._build_Board()

        self.update_image()

    def draw(self, surface):
        surface.blit(self.image, self.position)

    def update_image(self):
        self.image = Surface((self.cubesize*9, self.cubesize*9))
        self.tiles.draw(self.image)
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
        out = []
        filePath = os.path.dirname(os.path.abspath(__file__))
        # difficulties: simple,easy, intermediate, or expert
        with sp.Popen(["node", os.path.join(filePath, "qqwing-1.3.4", "qqwing-main-1.3.4.js"), 
            "--generate", "1", "--one-line", "--solution", "--difficulty", "intermediate"], stdout=sp.PIPE) as proc:
            assert proc.stdout is not None
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
            sudoku =    '000002534034010280200034100023000740906000312147203908708326401300009600460070803'
            solution =  '671892534534617289289534176823961745956748312147253968798326451315489627462175893'

        return sudoku, solution

    def _get_sudoku_from_cvs(self):
        with open('sudoku17.csv', newline='') as f:
            reader = csv.reader(f)
            counter = 0
            for row in reader:
                if counter > self.ind:
                    if len(row) >= 2:
                        ...
                    return row[0], row[1] if len(row) >= 2 else None
                counter +=1
        return '070000043040009610800634900094052000358460020000800530080070091902100005007040802', '679518243543729618821634957794352186358461729216897534485276391962183475137945862'

    def get_next_sudoku(self):
        return self._get_sudoku_from_qqwing()

    def _build_Board(self):
        self.tiles = sprite.Group()
        self.rows = [sprite.Group() for row in range(9)]
        self.columns = [sprite.Group() for colum in range(9)]
        self.blocks = [sprite.Group() for block in range(9)]

        tile_font = 'Arial'

        for ind in range(len(self.sudoku)):
                        # add self.tiles
            self.tiles.add(
                Tile(self.cubesize, ind, self.sudoku[ind], tile_font, self.rows, self.columns, self.blocks))

    def reset(self):
        self.ind +=1
        self.sudoku, self.solution = self.get_next_sudoku()
        
        # self.sudoku, self.solution = self.get_sudoku_from_cvs()
        for i, tile in enumerate(self.tiles):
            assert isinstance(tile, Tile)
            tile.reset(self.sudoku[i])
        self.update_image()

    def game_loop(self):
        while self.running:
            events = pygame.event.get()

            self.get_input(self.dbcClock, events)
            # self.tiles.update(events)
            self.draw(self.display_game)
            self.UIs.update(events)
            self.UIs.draw(self.display_game)
            display.update()
            display.flip()

    def build_UI(self):

        self.UIs = sprite.Group()

        ui_font = 'Arial'
        mon = display.Info()

        # add UI
        ui_x = mon.current_w - self.cubesize - 10
        gap = 10
        size_margin = self.cubesize+gap

        self.UIs.add(ColorButton(self.cubesize, (ui_x - size_margin *
                3,  + gap), "", ui_font, Color("grey")))
        self.UIs.add(ColorButton(self.cubesize, (ui_x - size_margin*3,
                size_margin*1 + gap), "", ui_font, Color("green")))
        self.UIs.add(ColorButton(self.cubesize, (ui_x - size_margin*3,
                size_margin*2 + gap), "", ui_font, Color("red")))
        self.UIs.add(ColorButton(self.cubesize, (ui_x - size_margin*3,
                size_margin*3 + gap), "", ui_font, Color("yellow")))

        self.UIs.add(UIButton(self.cubesize, (ui_x - size_margin*4, gap), "Mark", ui_font, 1))
        self.UIs.add(UIButton(self.cubesize, (ui_x - size_margin*4,
                size_margin*1 + gap), "SMark", ui_font, 2))
        self.UIs.add(ClearButton(self.cubesize, (ui_x - size_margin *
                4, size_margin*2 + gap), "clear", ui_font))
        self.UIs.add(CheckButton(self.cubesize, (ui_x - size_margin *
                4, size_margin*3 + gap), "Check", ui_font))

        self.UIs.add(ResetButton(self.cubesize, (ui_x - size_margin *
                2, size_margin*5 + gap), "Reset", ui_font))
        
    def get_input(self, dbcClock: pygame.time.Clock, events):
        # events = pygame.event.get()
        mouse_pos = pygame.mouse.get_pos()
        mods = pygame.key.get_mods()
        for event in events:
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    assert isinstance(self.rect, Rect)
                    if self.rect.collidepoint(mouse_pos):
                        self.select_tile_at(
                            pygame.mouse.get_pos(), mods)
                    self.holding_mb1 = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    # global dbcT
                    dbcT = dbcClock.tick()
                    self.holding_mb1 = False
                    if dbcT < 300:
                        tile = self.select_tile_at(event.pos, mods)
                        if isinstance(tile, Tile):
                            tile.select_all()
                    else:
                        pass
                    self.select_ui_at(event.pos, mods)

            if event.type == pygame.KEYDOWN:
                if event.unicode in ("1", "2", "3", "4", "5", "6", "7", "8", "9"):
                    self.update_selected(event.unicode)
                elif event.key == pygame.K_BACKSPACE:
                    for tile in self.tiles:
                        assert isinstance(tile, Tile)
                        if tile.selected:
                            tile.clear()
                elif event.key == pygame.K_a:
                    if mods & pygame.KMOD_LCTRL:
                        for tile in self.tiles:
                            assert isinstance(tile, Tile)
                            tile.select()

        assert isinstance(self.rect, Rect)
        if self.holding_mb1 and self.rect.collidepoint(mouse_pos):
            # assert isinstance(dbcT, int)

            tile = self.select_tile_at(mouse_pos, mods)
            if tile != None:
                tile.select()

    def select_ui_at(self, position: tuple, mods: int):
        for ui in self.UIs:
            assert isinstance(ui, Tile_parent)
            assert isinstance(ui.rect, Rect)
            if ui.rect.collidepoint(position):
                ui.select(pygame.KMOD_LSHIFT)
                return

    def reset(self):
        self.edit_mode = 0
        # rules.timeTaken = {"assign":0., "soleCand":0., "hiddCand":0., "nakedSub":0., "hiddSub2":0., "hiddSub3":0., "pointSub":0., "xwing":0.}
        for bttn in self.UIs:
            if isinstance(bttn, UIButton):
                bttn.deselect()
            if isinstance(bttn, CheckButton):
                bttn.deselect()
            else:
                continue
        
        self.reset()

    def select_tile_at(self, position:tuple, mods:pygame.key):
        t_tile = None
        for tile in self.tiles:
            assert isinstance(tile, Tile_parent)
            assert isinstance(tile.rect, Rect)
            if tile.rect.collidepoint(position[0]-20, position[1]-20):
                t_tile = tile
            else:
                if mods & pygame.KMOD_ALT:
                    pass
                elif not self.holding_mb1:  # Left ALT
                    tile.deselect()
                else:
                    pass
                # t_tile = None
        return t_tile

    def update_selected(self, string:str):
        for tile in self.tiles:
            assert isinstance(tile, Tile)
            if tile.selected:
                tile.update_value(string)

    def getTileAtPos(self, x, y):
        for tile in self.tiles:
            assert isinstance(tile, Tile)
            if tile.x == x and tile.y == y:
                return tile
        return
    
    def check_unique(self):
        boardState = ""
        validity = True
        for tile in self.tiles:
            assert isinstance(tile, Tile)
            boardState += str(tile.value)

        for i, tile in enumerate(self.tiles):
            assert isinstance(tile, Tile)
            if tile.value == 0:
                tile.update_color(tile.color_default, True)
                validity = False
                continue
            if any(tile.value == t.value for t in tile.row if t != tile) or \
                    any(tile.value == t.value for t in tile.column if t != tile) or \
                    any(tile.value == t.value for t in tile.block if t != tile):

                print(tile.value)
                print([t.value for t in tile.row if t != tile])
                print([t.value for t in tile.column if t != tile])
                print([t.value for t in tile.block if t != tile])

                tile.update_color(Color("red"), True)
                validity = False
                # return False

            elif not tile._locked:
                tile.update_color(Color("green"), True)

        return validity
    
    def check_board(self):

        validity = None
        if self.solution:
            validity = self.check_solution()
        else:
            validity = self.check_unique()

        return validity

    def check_solution(self):
        boardState = ""
        validity = True
        for tile in self.tiles:
            assert isinstance(tile, Tile)
            boardState += str(tile.value)

        # if boardState == gameBoard.solution:
        for tile in self.tiles:
            assert isinstance(tile, Tile)
            tile.reset_color()
            # tile.update_color("green")

            # else:

        for i, tile in enumerate(self.tiles):
            assert isinstance(tile, Tile)
            if boardState[i] != self.solution[i]:
                if tile.value == 0:
                    tile.update_color(tile.color_default, True)
                    validity = False
                else:
                    tile.update_color(Color("red"), True)
                    validity = False

            elif not tile._locked:
                tile.update_color(Color("green"), True)

        return validity


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

        
    def select(self, mod:bool=False):
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

    def set_value(self, val:str|int):
        val = str(val)
        self.title = str(val)
        if val.isdigit():
            self.value = int(val)
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
    def __init__(self, size: int, position: int, value: str, tfont: str, rows: list[pygame.sprite.Group], columns: list[pygame.sprite.Group], blocks: list[pygame.sprite.Group]) -> None:
        self.x = position%9
        self.y = math.floor(position/9)
        super().__init__(
            size, (self.x*size, self.y*size), value, tfont)
        
        self.row = columns[self.y]
        self.column = rows[self.x]
        self.block = blocks[int(self.y/3)*3+int(self.x/3)]
        # self.subsets = (self.column, self.row, self.block)
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
        self.possibleValues = list(range(1,10)) if value== '0' else []
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
            self._locked = False
            self.bg = self.color_default
            
        else:
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
            for tile in gameBoard.tiles:
                assert isinstance(tile,Tile)
                if tile.bg == self.bg:
                    tile.select()
        elif self.value == 0 and self.pen_marks!=[]:
            for tile in gameBoard.tiles:
                assert isinstance(tile,Tile)
                if all(mark in tile.pen_marks for mark in self.pen_marks):
                    tile.select()
        elif self.value != 0:
            for tile in gameBoard.tiles:
                assert isinstance(tile, Tile)
                if tile.value == self.value:# or self.value in tile.possibleValues:
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
            if gameBoard.edit_mode == 0:
                if self.value == val:
                    self.value = 0
                elif val in range(0,10):
                    self.value = val
                pass
                
            elif gameBoard.edit_mode == 1 and self.value == 0:
                if val in self.pen_marks:
                    self.pen_marks.remove(val)
                else:
                    self.pen_marks.append(val)
                self.pen_marks = sorted(self.pen_marks)

            elif gameBoard.edit_mode == 2 and self.value == 0:
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
            self.bg = self.color_default
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
        if not self.selected:
            self.selected = True
            gameBoard.edit_mode = self.mode
            self.update_color(self.color_selected)
            for ui in gameBoard.UIs:
                if ui is not self:
                    assert isinstance(ui, Tile_parent)
                    ui.deselect()
        else:
            gameBoard.edit_mode = 0
            self.deselect()

    def deselect(self):
        self.selected = False
        self.update_color(self.color_default)

class ClearButton(Tile_parent):
    def __init__(self, size:int, position:tuple, string:str, font:str) -> None:
        super().__init__(size, position, string, font) 
        assert isinstance(self.rect, Rect)
        self.update_sprite()

    def select(self, mod=False):
        for tile in gameBoard.tiles:
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
        for tile in gameBoard.tiles:
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
        b =gameBoard.check_board()
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

class ResetButton(Tile_parent):
    def __init__(self, size:int, position:tuple, string:str, font:str) -> None:
        super().__init__(size, position, string, font)
        self.update_sprite()
     
    def select(self, mod=False):
        gameBoard.reset()

class SelectRulesButton(Tile_parent):
    def __init__(self, size, position: tuple, string: str, font: str) -> None:
        super().__init__(size, position, string, font)
        self.rect = Rect(position, pygame.Vector2(size*2, size))
        self.image = Surface(self.rect.size)

        self.update_sprite()


gameBoard = GameBoard()

if __name__ == "__main__":
    gameBoard.game_loop()
else:
    gameBoard.edit_mode=0
    # solveBttn = SolveButton(10, (10, 10), "Solve", "arial")