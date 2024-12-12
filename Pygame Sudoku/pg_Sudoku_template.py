import logging.handlers
import subprocess as sp
import pygame
import math
import pprint
# from timeit import default_timer as timer
from pygame import display, Surface, sprite, font, Color, Rect
import os
import csv
import logging
import queue
from logging.handlers import QueueHandler, QueueListener


class GameBoard(sprite.Sprite):
    def __init__(self, cubesize: int = 10, sud=None, sol=None, difficulty="expert") -> None:
        self.checktime = 0.
        self.successfull_timeTaken = {}
        self.successfull_numUsed = {}
        self.timeTaken = {}
        self.numUsed = {}
        self.difficulty = difficulty

        log_queue = queue.Queue(-1)

        queue_handler = QueueHandler(log_queue)
        # queue_handler.setLevel(logging.INFO)

        logger = logging.getLogger()
        logger.addHandler(queue_handler)
        logger.setLevel(logging.INFO)

        console_handler = logging.StreamHandler()
        formatter = logging.Formatter('%(threadName)s: %(message)s')
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.WARNING)

        # with open("sudoku.log", mode="w") as f:
        #     f.write("")

        file_handler = logging.FileHandler("sudoku.log", "w")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)

        listener = QueueListener(log_queue, console_handler, file_handler)
        listener.start()

        pygame.init()

        self.running = True
        self.dbcClock = pygame.time.Clock()
        self.tClock = pygame.time.Clock()
        self.dbcT = 1000
        self.auto = False
        self.cubesize = 60

        # 0 = write full size(tile is that number), 1 = pencil mark (tile can be that number), 2 = strong mark(tile has to be one of these numbers)
        self.edit_mode = 0
        self.holding_mb1 = False

        self.sud_index = 0
        self.margin = 20

        self.image = Surface((cubesize*9, cubesize*9))
        self.image.fill(Color("white"))
        self.color_line = Color("black")
        self.rect = self.image.get_rect(topleft=(self.margin, self.margin))

        self.sudoku, self.solution = (
            sud, sol) if sud else (self.get_next_sudoku())
        # self.sudoku, self.solution = self.get_sudoku_from_cvs()
        # board

        self._build_Board()

        self.build_UI()

        self.update_image()

    def get_avg_times(self):
        return pprint.pformat({key: value/self.numUsed[key] * 1000 for key, value in self.timeTaken.items() if self.numUsed.get(key)})

    def get_avg_suc_times(self):
        return pprint.pformat({key: value/self.successfull_numUsed[key] * 1000 for key, value in self.successfull_timeTaken.items() if self.successfull_numUsed.get(key)})

    def draw(self):
        pygame.event.pump()
        display.update()
        self.display_game.blit(self.image, (self.margin, self.margin))

        self.UIs.draw(self.display_game)
        # for ui in self.UIs:
        #     self.display_game.blit(ui.image, ui.rect)

        display.flip()

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
        self.rect = self.image.get_rect(topleft=(self.margin, self.margin))

    def _get_sudoku_from_qqwing(self):
        clean_out = []
        out = []
        filePath = os.path.dirname(os.path.abspath(__file__))
        # difficulties: simple,easy, intermediate, or expert
        with sp.Popen(["node", os.path.join("qqwing-1.3.4", "qqwing-main-1.3.4.js"),
                       "--generate", "1", "--one-line", "--solution", "--difficulty", self.difficulty], stdout=sp.PIPE) as proc:
            assert proc.stdout is not None
            out = proc.stdout.readlines()

        if len(out) > 0:
            for sudoku in out:
                cs = sudoku.decode('UTF-8')
                clean_out.append(cs[:-1])
            # clean_out[0] = '093004560060003140004608309981345000347286951652070483406002890000400010029800034'
            # clean_out[1] = "093004560060003140004608309981345000347286951652070483406002890000400010029800034"
            if len(clean_out) != 2:
                logging.error("qqwing failed to generate sudoku")
                logging.error(pprint.pformat("".join(clean_out)))
                pygame.quit()
                exit()
                return
            sudoku = clean_out[0].replace(".", "0")

            solution = clean_out[1]

        else:
            sudoku = '000002534034010280200034100023000740906000312147203908708326401300009600460070803'
            solution = '671892534534617289289534176823961745956748312147253968798326451315489627462175893'

        return sudoku, solution

    def _get_sudoku_from_cvs(self):
        with open('sudoku17.csv', newline='') as f:
            reader = csv.reader(f)
            counter = 0
            for row in reader:
                if counter > self.sud_index:
                    if len(row) >= 2:
                        ...
                    return row[0], row[1] if len(row) >= 2 else None
                counter += 1
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
                Tile(self.cubesize, ind, self.sudoku[ind], tile_font, self.rows, self.columns, self.blocks, self))

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

        self.sud_index += 1
        self.sudoku, self.solution = self.get_next_sudoku()

        # self.sudoku, self.solution = self.get_sudoku_from_cvs()
        for i, tile in enumerate(self.tiles):
            assert isinstance(tile, Tile)
            tile.reset(self.sudoku[i])
        self.update_image()

    def game_loop(self):
        self.display_game = display.set_mode(
            (self.rect.right + self.cubesize * 5, self.rect.bottom + self.margin*2))
        self.display_game.fill(Color("black"))
        while self.running:
            events = pygame.event.get()
            self.UIs.update(events)
            self.get_input(self.dbcClock, events)
            # self.tiles.update(events)
            self.draw()

    def build_UI(self):
        self.UIs = sprite.Group()
        ui_font = 'Arial'

        # add UI
        ui_x = self.rect.right
        size_margin = self.cubesize+self.margin//2

        self.UIs.add(ColorButton(self.cubesize, 
                                 (ui_x + size_margin * 1,  + self.margin), 
                                 "", ui_font, Color("grey"), self))

        self.UIs.add(ColorButton(self.cubesize, 
                                 (ui_x + size_margin*1, size_margin*1 + self.margin), 
                                 "", ui_font, Color("green"), self))

        self.UIs.add(ColorButton(self.cubesize, 
                                 (ui_x + size_margin*1,
                                                 size_margin*2 + self.margin), "", ui_font, Color("red"), self))

        self.UIs.add(ColorButton(self.cubesize, 
                                 (ui_x + size_margin*1, size_margin*3 + self.margin),
                                 "", ui_font, Color("yellow"), self))

        self.UIs.add(UIButton(self.cubesize, 
                              (ui_x + size_margin*2, self.margin),
                              "Mark", ui_font, 1, self))

        self.UIs.add(UIButton(self.cubesize, 
                              (ui_x + size_margin*2, size_margin*1 + self.margin),
                              "SMark", ui_font, 2, self))

        self.UIs.add(ClearButton(self.cubesize, 
                                 (ui_x + size_margin * 2, size_margin*2 + self.margin), 
                                 "clear", ui_font, self))

        self.UIs.add(CheckButton(self.cubesize, 
                                 (ui_x + size_margin * 2, size_margin*3 + self.margin), 
                                 "Check", ui_font, self))

        self.UIs.add(ResetButton(self.cubesize, 
                                 (ui_x + size_margin * 1, size_margin*5 + self.margin), 
                                 "Reset", ui_font, self))

        self.UIs.add(SolveBttn(self.cubesize, 
                               (ui_x + size_margin * 1, size_margin*4 + self.margin), 
                               "Solve", ui_font, self))

    def get_input(self, dbcClock: pygame.time.Clock, events):
        # events = pygame.event.get()
        mouse_pos = pygame.mouse.get_pos()
        mods = pygame.key.get_mods()
        for event in events:
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                assert isinstance(self.rect, Rect)
                if self.rect.collidepoint(mouse_pos):
                    self.select_tile_at(
                        pygame.mouse.get_pos(), mods)
                self.holding_mb1 = True
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
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
                elif event.key == pygame.K_a and mods & pygame.KMOD_LCTRL:
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
                ui.select(mods)
                return

        # self.reset()

    def select_tile_at(self, position: tuple, mods: pygame.key):
        t_tile = None
        position
        for tile in self.tiles:
            assert isinstance(tile, Tile_parent)
            assert isinstance(tile.rect, Rect)
            if tile.rect.collidepoint(position[0]-self.margin, position[1]-self.margin):
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

    def update_selected(self, string: str):
        for tile in self.tiles:
            assert isinstance(tile, Tile)
            if tile.selected:
                tile.update_value(string)

    def refresh_all(self):
        for tile in self.tiles:
            assert isinstance(tile, Tile)
            tile.update_sprite()

    def getTileAtPos(self, x, y):
        for tile in self.tiles:
            assert isinstance(tile, Tile)
            if tile.x == x and tile.y == y:
                return tile
        return

    def _check_unique(self):
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
        return self._check_solution() if self.solution else self._check_unique()

    def _check_solution(self):
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

    def solve(self):
        logging.error("not implemented")


class Tile_parent(sprite.Sprite):
    def __init__(self, size: int, position: tuple, _string: str, font: str, gameBoard: GameBoard) -> None:
        self.gameBoard = gameBoard
        # self.position = pygame.Vector2(position)
        super().__init__()
        self.rect = Rect(position, pygame.Vector2(size, size))
        self.bg = Color("white")
        self.color_default = Color("white")
        self.txtfont = pygame.font.SysFont(font, math.floor(size/4))
        self.font = font
        # self._txt_pos = (0, 0)
        self.set_value(_string)

        self._txt_pos = (self.rect.size[0]/2 - self.txt.get_size()[0]/2,
                         self.rect.size[1]/2 - self.txt.get_size()[1]/2)
        self.selected = False
        self._locked = False
        self.image = Surface(self.rect.size)
        self.update_sprite()

    def update(self, events):
        pass

    def select(self, mod: int = 0):
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
            self.gameBoard.update_image()
        except:
            pass

    def set_value(self, val: str | int):
        val = str(val)
        self.title = str(val)
        if val.isdigit():
            self.value = int(val)
        assert isinstance(self.rect, Rect)
        fontsize = math.floor(self.rect.height/4)
        while self.txtfont.size(val)[0] > self.rect.size[0]:
            fontsize -= 1
            self.txtfont = pygame.font.SysFont(self.font, fontsize)
            self.txt = self.txtfont.render(self.title, True, (0, 0, 0))
        self.txt = self.txtfont.render(self.title, True, (0, 0, 0))
        try:
            self.update_sprite()
        except:
            pass

    def update_color(self, color: Color):
        self.bg = color
        self.update_sprite()

class Tile:
    ...

class Tile(Tile_parent):
    def __init__(self, size: int, position: int, value: str, tfont: str, rows: list[pygame.sprite.Group], columns: list[pygame.sprite.Group], blocks: list[pygame.sprite.Group], gameBoard: GameBoard) -> None:
        self.x = position % 9
        self.y = math.floor(position/9)
        self.pen_marks = []
        self.spen_marks = []

        self.row = rows[self.y]
        self.column = columns[self.x]
        self.block = blocks[int(self.y/3)*3+int(self.x/3)]
        self.groups = (self.column, self.row, self.block)

        self._penmark_font = font.SysFont(tfont, math.floor(size/4))
        self._spenmark_font = font.SysFont(tfont, math.floor(size/3))
        self.color_clue = Color("lightgrey")
        self.color_rect = Color("red")

        self.value = int(value)

        self.possibleValues = list(range(1, 10)) if value == '0' else []
        self.index = position

        marktxt = self._penmark_font.render("0", True, (0, 0, 0))
        markx = marktxt.get_width()
        marky = marktxt.get_height()
        self._pen_positions = [(2, 2), (size-markx - 2, 2),
                               (2, size-marky), (size-markx-2, size-marky),
                               (size/2-markx/2, 2), (size/2-markx/2, size-marky),
                               (2, size/2-marky/2), (size-markx-2, size/2-marky/2),
                               (size/2-markx/2, size/2-marky/2)]

        self.possibleValueBools = {}

        super().__init__(
            size, (self.x*size, self.y*size), value, tfont, gameBoard)

        self.txtfont = font.SysFont(tfont, math.floor(size/2))

        if self.value == 0:
            self._locked = False
            self.bg = self.color_default

        else:
            self._locked = True
            # self.color_default = self.color_clue
            self.bg = self.color_clue

        self.row.add(self)
        self.column.add(self)
        self.block.add(self)
        self.update_sprite()

    def update(self):
        if self.selected:
            self.update_sprite()

    def select(self, mods: int = 0):
        if not self.selected:
            self.selected = True
            self.update_sprite()

    def select_all(self):
        if self.bg != self.color_default and self.bg != self.color_clue:
            for tile in self.gameBoard.tiles:
                assert isinstance(tile, Tile)
                if tile.bg == self.bg:
                    tile.select()
        elif self.value == 0 and self.pen_marks != []:
            for tile in self.gameBoard.tiles:
                assert isinstance(tile, Tile)
                if all(mark in tile.pen_marks for mark in self.pen_marks):
                    tile.select()
        elif self.value != 0:
            for tile in self.gameBoard.tiles:
                assert isinstance(tile, Tile)
                if tile.value == self.value:  # or self.value in tile.possibleValues:
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
                             self.image.get_rect().move(1, 1).inflate(-1, -1), 3)

        if self.value == 0:
            self.txt = self.txtfont.render("", True, (0, 0, 0))
            for i in range(len(self.pen_marks)):
                marktxt = self._penmark_font.render(
                    str(self.pen_marks[i]), True, (0, 0, 0))
                self.image.blit(marktxt, self._pen_positions[i])

            sPenStr = ""
            for s in self.spen_marks:
                sPenStr = sPenStr + str(s)
            smarktxt = self._penmark_font.render(sPenStr, True, (0, 0, 0))
            self.image.blit(smarktxt, (self.rect.width/2 - smarktxt.get_width() /
                            2, self.rect.height/2 - smarktxt.get_height()/2))

        else:
            self.txt = self.txtfont.render(str(self.value), True, (0, 0, 0))
        self.image.blit(self.txt, (self.rect.size[0]/2 - self.txt.get_size()[0]/2,
                                   self.rect.size[1]/2 - self.txt.get_size()[1]/2))

        try:
            self.gameBoard.update_image()
        except:
            pass

    def update_value(self, value: str):
        val = int(value)
        if val is not None and not self._locked:
            if self.gameBoard.edit_mode == 0:
                if self.value == val:
                    self.value = 0
                elif val in range(0, 10):
                    self.value = val
                pass

            elif self.gameBoard.edit_mode == 1 and self.value == 0:
                if val in self.pen_marks:
                    self.pen_marks.remove(val)
                else:
                    self.pen_marks.append(val)
                self.pen_marks = sorted(self.pen_marks)

            elif self.gameBoard.edit_mode == 2 and self.value == 0:
                if val in self.spen_marks:
                    self.spen_marks.remove(val)
                else:
                    self.spen_marks.append(val)
                self.spen_marks = sorted(self.spen_marks)
            else:
                return
            self.update_sprite()

    def update_color(self, color: Color, forced=False):

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

    def reset(self, value: str):
        self.value = int(value)
        self.pen_marks = []
        self.spen_marks = []
        self.deselect()

        if self.value == 0:
            self.possibleValues = [i for i in range(1, 10)]
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


    def connected_possible(self, value:int) -> list[list[Tile]]:
        return [[t for t in grp if isinstance(t, Tile) and value in t.possibleValues and t != self ] for grp in self.groups]


class UIButton(Tile_parent):
    def __init__(self, size: int, position: tuple, _string: str, font: str, mode: int, gameBoard: GameBoard) -> None:
        super().__init__(size, position, _string, font, gameBoard)
        assert isinstance(self.rect, Rect)
        # self._txt_pos = (self.rect.size[0]/2 - self.txt.get_size()[0]/2,
        # self.rect.size[1]/2 - self.txt.get_size()[1]/2)
        self.mode = mode
        self.color_selected = Color("green")
        self.update_sprite()

    def select(self, mods: int = 0):
        if not self.selected:
            self.selected = True
            self.gameBoard.edit_mode = self.mode
            self.update_color(self.color_selected)
            for ui in self.gameBoard.UIs:
                if ui is not self:
                    assert isinstance(ui, Tile_parent)
                    ui.deselect()
        else:
            self.gameBoard.edit_mode = 0
            self.deselect()

    def deselect(self):
        self.selected = False
        self.update_color(self.color_default)



class ClearButton(Tile_parent):
    def __init__(self, size: int, position: tuple, string: str, font: str, gameBoard: GameBoard) -> None:
        super().__init__(size, position, string, font, gameBoard)
        assert isinstance(self.rect, Rect)
        self.update_sprite()

    def select(self, mods: int = 0):
        for tile in self.gameBoard.tiles:
            assert isinstance(tile, Tile)
            if tile.selected:
                tile.clear()


class ColorButton(Tile_parent):
    def __init__(self, size: int, position: tuple, string: str, font: str, color: Color, gameBoard: GameBoard) -> None:
        super().__init__(size, position, string, font, gameBoard)
        self.bg = color
        self.color_default = color
        self.update_sprite()

    def select(self, mods: int = 0):
        for tile in self.gameBoard.tiles:
            assert isinstance(tile, Tile)
            if tile.selected:
                tile.update_color(self.bg)


class CheckButton(Tile_parent):
    def __init__(self, size: int, position: tuple, string: str, font: str, gameBoard: GameBoard) -> None:
        super().__init__(size, position, string, font, gameBoard)
        assert isinstance(self.rect, Rect)

        self.color_correct = Color("green")
        self.color_incorrect = Color("red")

        self.update_sprite()

    def select(self, mods: int = 0):
        # if solution == sudoku:
        self.deselect
        b = self.gameBoard.check_board()
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
    # def __init__(self, size:int, position:tuple, string:str, font:str) -> None:
    #     super().__init__(size, position, string, font)
    #     self.update_sprite()

    def select(self, mods: int = 0):
        self.gameBoard.reset()


class SelectRulesButton(Tile_parent):
    ...
    # def __init__(self, size, position: tuple, string: str, font: str) -> None:
    #     super().__init__(size, position, string, font)
    #     self.rect = Rect(position, pygame.Vector2(size*2, size))
    #     self.image = Surface(self.rect.size)

    #     self.update_sprite()


class SolveBttn(Tile_parent):
    def select(self, mods: int = 0):
        while self.gameBoard.solve() and mods & pygame.KMOD_LSHIFT:
            self.gameBoard.refresh_all()
            self.gameBoard.draw()
            pygame.display.flip()
            ...
        if mods & pygame.KMOD_LSHIFT:

            next(x for x in self.gameBoard.UIs if isinstance(
                x, CheckButton)).select()
            self.onDone()

    def onDone(self):
        ...


if __name__ == "__main__":
    gameBoard = GameBoard()
    gameBoard.game_loop()
