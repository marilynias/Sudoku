import subprocess as sp
import pygame
import math
from pygame import mouse, display, Surface, sprite, font, time


def main():
    global tiles, UIs, edit_mode, holding_mb1, dbcT, solution
    # Display
    pygame.init()
    display_game = display.set_mode((800,600))
    display_game.fill(pygame.Color("black"))
    cubesize = 60
    gameBoard = Surface((cubesize*9, cubesize*9))
    gameBoard.fill(pygame.Color("white"))
    running = True
    dbcClock = time.Clock()
    dbcT = 1000

    # Sudoku
    out = get_sudoku()
    sudoku = out[0]
    solution = out[1]

    #board
    boardLocation = (20,20)
    
    tiles = sprite.Group()
    UIs = sprite.Group()
    # 0 = write full size(tile is that number), 1 = pencil mark (tile can be that number), 2 = strong mark(tile has to be one of these numbers)
    edit_mode = 0  
    holding_mb1 = False
    # holding_txt = font.SysFont('Arial', 10).render("holding", True,pygame.Color("red"))
    build_Board(sudoku, tiles, cubesize)

    
    # print_sudoku(sudoku)
    

    while running:
        get_input(gameBoard, dbcClock)
        # display.fill(pygame.Color("Black"))

        display_game.blit(gameBoard, boardLocation)
        # tiles.update()
        # UIs.update()
        
        tiles.draw(gameBoard)
        draw_lines(gameBoard, cubesize)
        UIs.draw(display_game)
        # if holding_mb1:
        #     display_game.blit(holding_txt, (20, 20))
        display.update()
        display.flip()


def get_input(gameBoard: Surface, dbcClock:time.Clock):
    global holding_mb1
    events = pygame.event.get()
    mouse_pos = mouse.get_pos()
    for event in events:
        if event.type == pygame.QUIT:
            exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if gameBoard.get_rect().collidepoint(mouse_pos):
                    select_tile_at(mouse.get_pos())
                holding_mb1 = True  
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                # global dbcT
                dbcT = dbcClock.tick()
                holding_mb1 = False
                if dbcT < 300:
                    tile = select_tile_at(event.pos)
                    if isinstance(tile, Tile):
                        tile.select_all()
                else:
                    pass
                select_ui_at(event.pos)

        if event.type == pygame.KEYDOWN:
            if event.unicode in ("1", "2", "3", "4", "5", "6", "7", "8", "9"):
                update_selected(event.unicode)
            if event.key == 8:  #backspace
                for tile in tiles:
                    assert isinstance(tile, Tile)
                    if tile.selected:
                        tile.clear()

    
    if holding_mb1 and gameBoard.get_rect().collidepoint(mouse_pos):
        # assert isinstance(dbcT, int)
        
        tile = select_tile_at(mouse_pos)
        if tile is not None:
            tile.select()

def update_selected(string:str):
    for tile in tiles:
        assert isinstance(tile, Tile_parent)
        if tile.selected:
            tile.update_value(string)

def select_tile_at(position:tuple):
    t_tile = None
    for tile in tiles:
        assert isinstance(tile, Tile_parent)
        assert isinstance(tile.rect, pygame.Rect)
        if tile.rect.collidepoint(position[0]-20, position[1]-20):
            t_tile = tile
        else:
            mod = pygame.key.get_mods()
            if mod != 256 and not holding_mb1:  # Left ALT
                tile.deselect()
            else:
                pass
            # t_tile = None
    return t_tile

def select_ui_at(position:tuple):
    for ui in UIs:
        assert isinstance(ui, Tile_parent)
        assert isinstance(ui.rect, pygame.Rect)
        if ui.rect.collidepoint(position):
            ui.select()
            return

def build_Board(sudoku, tiles, cubesize):
    
    tile_font = font.SysFont('Arial', math.floor(cubesize/2))
    ui_font = font.SysFont('Arial', math.floor(cubesize/4))
    mon = display.Info()

    for i in range(9):
        # add tiles
        for j in range(9):
            ind = i*9+j
            tiles.add(
                Tile(cubesize, ((i*cubesize), (j*cubesize)), sudoku[ind], tile_font, ind))

    # add UI
    ui_x = mon.current_w - cubesize - 10
    size_margin = cubesize+20
    UIs.add(UIButton(cubesize, (ui_x, 10), "Mark", ui_font, 1))
    UIs.add(UIButton(cubesize, (ui_x, size_margin), "SMark", ui_font, 2))
    UIs.add(ClearButton(cubesize, (ui_x, size_margin*2), "clear", ui_font))
    UIs.add(CheckButton(cubesize, (ui_x, size_margin*3), "Check", ui_font))
    UIs.add(ColorButton(cubesize, (ui_x - size_margin, 10), "", ui_font, pygame.Color("grey")))
    UIs.add(ColorButton(cubesize, (ui_x - size_margin, size_margin*1), "", ui_font, pygame.Color("green")))
    UIs.add(ColorButton(cubesize, (ui_x - size_margin, size_margin*2), "", ui_font, pygame.Color("red")))
    UIs.add(ColorButton(cubesize, (ui_x - size_margin, size_margin*3), "", ui_font, pygame.Color("yellow")))
    

    


def get_sudoku():
    clean_out = []
    with sp.Popen(["node", "qqwing-1.3.4\\qqwing-main-1.3.4.min.js", "--generate", "1", "--one-line", "--solution", "--difficulty", "easy"], stdout=sp.PIPE) as proc:
        assert proc.stdout is not None
        print(type(proc.stdout))
        out = proc.stdout.readlines()

    for sudoku in out:
        cs = sudoku.decode('UTF-8')
        clean_out.append(cs[:-1])
    return clean_out

def draw_lines(gameBoard, cubesize):
    for i in range(9):
        # add lines
        if i == 0:
            width = 0
        elif i % 3 == 0:
            width = 3
        else:
            width = 1
        pygame.draw.line(gameBoard, pygame.Color("black"),
                         (i*cubesize, 0), (i*cubesize, cubesize*9), width)
        pygame.draw.line(gameBoard, pygame.Color("black"),
                         (0, i*cubesize), (cubesize*9, i*cubesize), width)
    


class Tile_parent(sprite.Sprite):
    def __init__(self, size:int, position:tuple, string:str, font:font.Font) -> None:
        self.position = pygame.Vector2(position)
        sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(position, pygame.Vector2(size, size))
        self.bg = pygame.Color("white")
        self.value = string
        self.txtfont = font
        self._txt_pos = (0, 0)
        self.txt = self.txtfont.render(self.value, True, (0, 0, 0))
        self.selected = False
        self._locked = False
        self.image = Surface(self.rect.size)
        # self.update_sprite()
        
        
    def select(self):
        if not self.selected and not self._locked:
            self.selected = True
            self.update_sprite()

    def deselect(self):
        if self.selected and not self._locked:
            self.selected = False
            self.update_sprite()

    def update_sprite(self):
        assert isinstance(self.image, Surface)
        self.image.fill(self.bg)
        self.image.blit(self.txt, self._txt_pos)

    def update_value(self, val:str):
        self.value = val
        self.txt = self.txtfont.render(self.value, True, (0, 0, 0))
        self.update_sprite()

class Tile(Tile_parent):
    def __init__(self, size:int, position:tuple, string:str, tfont: font.Font, ind: int) -> None:
        super().__init__(size, position, string, tfont)
        self._penmark_font = font.SysFont('Arial', math.floor(size/4))
        self._spenmark_font = font.SysFont('Arial', math.floor(size/3))
        self.pen_marks = []
        self.spen_marks = []
        self.index = ind
        marktxt = self._penmark_font.render("0", True, (0, 0, 0))
        markx = marktxt.get_width()
        marky = marktxt.get_height()
        self._pen_positions = [(2, 2), (size-markx -2, 2),
                              (2, size-marky), (size-markx-2, size-marky),
                              (size/2-markx/2, 2), (size/2-markx/2, size-marky),
                              (2, size/2-marky/2), (size-markx-2, size/2-marky/2),
                              (size/2-markx/2, size/2-marky/2)]

        if self.value == ".":
            # self.value = ""
            self._locked = False
            self.bg = pygame.Color("white")
            self.update_value("")
        else:
            # self.value = string
            self._locked = True
            self.bg = pygame.Color("lightgrey")
            self.update_sprite()
        
        
        # self.update_sprite()

    def select(self):
        if not self.selected:
            self.selected = True
            # self.bg = pygame.Color("yellow")
            self.update_sprite()

    def select_all(self):
        # similar_tiles = [self]
        for tile in tiles:
            assert isinstance(tile,Tile)
            if self.value == "":
                for mark in self.pen_marks:
                    if mark in tile.pen_marks:
                        tile.select()
            elif tile.value == self.value:
                tile.select()
        


    def deselect(self):
        if self.selected:
            self.selected = False
            # self.bg = pygame.Color("white")
            self.update_sprite()

    def update_sprite(self):
        assert isinstance(self.rect, pygame.Rect)
        self.image = Surface(self.rect.size)
        self.image.fill(self.bg)

        if self.selected:
            pygame.draw.rect(self.image, pygame.Color("red"),
                             self.image.get_rect().move(1, 1).inflate(-1,-1), 3)

        if self.value == "":
            for i in range(len(self.pen_marks)):
                marktxt = self._penmark_font.render(self.pen_marks[i], True, (0, 0, 0))
                self.image.blit(marktxt, self._pen_positions[i] )

            sPenStr = ""
            for s in self.spen_marks:
                sPenStr = sPenStr + str(s)
            smarktxt = self._penmark_font.render(sPenStr, True, (0, 0, 0))
            self.image.blit(smarktxt, (self.rect.width/2 - smarktxt.get_width()/2, self.rect.height/2 - smarktxt.get_height()/2))

        self.txt = self.txtfont.render(self.value, True, (0, 0, 0))
        self.image.blit(self.txt, (self.rect.size[0]/2 - self.txt.get_size()[0]/2,
                                   self.rect.size[1]/2 - self.txt.get_size()[1]/2))

    def update_value(self, val: str):
        if val is not None and not self._locked:
            if edit_mode == 0:
                if self.value == val:
                    self.value = ""
                else:
                    self.value = val
                
            elif edit_mode == 1 and self.value == "":
                if val in self.pen_marks:
                    self.pen_marks.remove(val)
                else:
                    self.pen_marks.append(val)
                self.pen_marks = sorted(self.pen_marks)
            elif edit_mode == 2 and self.value == "":
                if val in self.spen_marks:
                    self.spen_marks.remove(val)
                else:
                    self.spen_marks.append(val)
                self.spen_marks = sorted(self.spen_marks)
            else:
                return
            self.update_sprite()

    def update_color(self, color: pygame.Color, forced = False):
        
        if self.bg == color and not forced:
            if not self._locked:
                self.bg = pygame.Color("white")
            else:
                self.bg = pygame.Color("lightgrey")
        else:
            self.bg = color
        self.update_sprite()

    def clear(self):
        if not self._locked:
            self.pen_marks = []
            self.spen_marks = []
            self.value = ""
            self.update_sprite()

class UIButton(Tile_parent):
    def __init__(self, size:int, position:tuple, string:str, font:font.Font, mode:int) -> None:
        super().__init__(size, position, string, font)
        assert isinstance(self.rect, pygame.Rect)
        self._txt_pos = (self.rect.size[0]/2 - self.txt.get_size()[0]/2,
                        self.rect.size[1]/2 - self.txt.get_size()[1]/2)
        self.mode = mode
        self.update_sprite()

    def select(self):
        global edit_mode
        if not self.selected:
            self.selected = True
            edit_mode = self.mode
            self.bg = pygame.Color("green")
            for ui in UIs:
                if ui is not self:
                    assert isinstance(ui, Tile_parent)
                    ui.deselect()
        else:
            edit_mode = 0
            self.deselect()
        self.update_sprite()

    def deselect(self):
        self.selected = False
        self.bg = pygame.Color("lightgrey")
        self.update_sprite()

class ClearButton(Tile_parent):
    def __init__(self, size, position, string, font) -> None:
        super().__init__(size, position, string, font) 
        assert isinstance(self.rect, pygame.Rect)
        self._txt_pos = (self.rect.size[0]/2 - self.txt.get_size()[0]/2,
                         self.rect.size[1]/2 - self.txt.get_size()[1]/2)
        self.update_sprite()

    def select(self):
        for tile in tiles:
            assert isinstance(tile, Tile)
            if tile.selected:
                tile.clear()

class ColorButton(Tile_parent):
    def __init__(self, size: int, position: tuple, string: str, font: font.Font, color: pygame.Color) -> None:
        super().__init__(size, position, string, font)
        self.bg = color
        self.update_sprite() 

    def select(self):
        for tile in tiles:
            assert isinstance(tile, Tile)
            if tile.selected:
                tile.update_color(self.bg)


class CheckButton(Tile_parent):
    def __init__(self, size, position, string, font) -> None:
        super().__init__(size, position, string, font)
        assert isinstance(self.rect, pygame.Rect)
        self._txt_pos = (self.rect.size[0]/2 - self.txt.get_size()[0]/2,
                         self.rect.size[1]/2 - self.txt.get_size()[1]/2)
        self.update_sprite()

    def select(self):
        sudString = ""
        for tile in tiles:
            assert isinstance(tile, Tile)
            if tile.value == "":
                c = "."
            else:
                c = tile.value
            sudString = sudString+str(c)

        for i in range(len(solution)):
            wrongtiles = []
            righttiles = []
            
            self.bg = pygame.Color("green")
            for i, tile in enumerate(tiles):
                assert isinstance(tile, Tile)
                if solution[i] != sudString[i]:
                    if tile.value == "":
                        tile.update_color(pygame.Color("white"), True)
                    else:
                        tile.update_color(pygame.Color("red"), True)
                        self.bg = pygame.Color("red")
                # elif not tile._locked:
                #     self.bg = pygame.Color("green")
                    # tile.update_color(pygame.Color("green"), True)
            self.update_sprite()


            # if solution[i] != sudString[i]:
            #     for tile in tiles:
            #         assert isinstance(tile, Tile)
            #         if tile.index == i and tile.value != "":
            #             tile.update_color(pygame.Color("red"))
            # else:
            #     for tile in tiles:
            #         assert isinstance(tile, Tile)
            #         if tile.index == i and tile.value != "":
            #             tile.update_color(pygame.Color("green"))

def print_sudoku(sudoku):
    
    for i in range(0, len(sudoku), 9):
        if i % 27 == 0:
            print("_________")
        print(sudoku[i] + sudoku[i+1] + sudoku[i+2] + "|" + sudoku[i+3] + sudoku[i+4] + sudoku[i+5] + "|" + sudoku[i+6] + sudoku[i+7] + sudoku[i+8])
        
    print("_________")




if __name__ == "__main__":
    main()
