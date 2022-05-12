import subprocess as sp
import pygame
import math
from pygame import mouse, display, Surface, sprite, font, time


def main():
    global tiles, rows, blocks, columns, UIs, edit_mode, holding_mb1, dbcT, sudoku, solution
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
    sudoku, solution = get_sudoku()
    

    #board
    boardLocation = (20,20)
    
    tiles = sprite.Group()
    rows = [sprite.Group() for row in range(9)]
    columns = [sprite.Group() for colum in range(9)]
    blocks = [sprite.Group() for colum in range(9)]
    UIs = sprite.Group()
    # 0 = write full size(tile is that number), 1 = pencil mark (tile can be that number), 2 = strong mark(tile has to be one of these numbers)
    edit_mode = 0  
    holding_mb1 = False
    # holding_txt = font.SysFont('Arial', 10).render("holding", True,pygame.Color("red"))
    build_Board(tiles, cubesize)

    

    while running:
        get_input(gameBoard, dbcClock)
        # display.fill(pygame.Color("Black"))

        display_game.blit(gameBoard, boardLocation)
        # tiles.update()
        # UIs.update()
        

        tiles.draw(gameBoard)
        draw_lines(gameBoard, cubesize)
        UIs.draw(display_game)
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

def build_Board(tiles:sprite.Group, cubesize:int):
    
    tile_font = font.SysFont('Arial', math.floor(cubesize/2))
    ui_font = font.SysFont('Arial', math.floor(cubesize/4))
    mon = display.Info()

    for ind in range(len(sudoku)):
                     # add tiles
            tiles.add(
                Tile(cubesize, ind, sudoku[ind], tile_font))

    # for tile in tiles:
    #     assert isinstance(tile, Tile)
    #     # block = []
    #     blockpos = [math.floor(tile.x/3)*3, math.floor(tile.y/3)*3]

    #     for i in range(3):
    #         # row = []
    #         for j in range(3):
    #             tile.block.append(getTileAtPos(blockpos[0]+i, blockpos[1]+j))
    #         # block.append(row)

    # add UI
    ui_x = mon.current_w - cubesize - 10
    size_margin = cubesize+20
    UIs.add(UIButton(cubesize, (ui_x, 10), "Mark", ui_font, 1))
    UIs.add(UIButton(cubesize, (ui_x, size_margin), "SMark", ui_font, 2))
    UIs.add(ClearButton(cubesize, (ui_x, size_margin*2), "clear", ui_font))
    UIs.add(CheckButton(cubesize, (ui_x, size_margin*3), "Check", ui_font))
    UIs.add(NextMoveButton(cubesize, (ui_x, size_margin*4), "Next", ui_font))


    UIs.add(ColorButton(cubesize, (ui_x - size_margin, 10), "", ui_font, pygame.Color("grey")))
    UIs.add(ColorButton(cubesize, (ui_x - size_margin, size_margin*1), "", ui_font, pygame.Color("green")))
    UIs.add(ColorButton(cubesize, (ui_x - size_margin, size_margin*2), "", ui_font, pygame.Color("red")))
    UIs.add(ColorButton(cubesize, (ui_x - size_margin, size_margin*3), "", ui_font, pygame.Color("yellow")))

def get_sudoku():
    clean_out = []
    with sp.Popen(["node", "qqwing-1.3.4\\qqwing-main-1.3.4.min.js", "--generate", "1", "--one-line", "--solution", "--difficulty", "simple"], stdout=sp.PIPE) as proc:
        assert proc.stdout is not None
        print(type(proc.stdout))
        out = proc.stdout.readlines()

    for sudoku in out:
        cs = sudoku.decode('UTF-8')
        clean_out.append(cs[:-1])

    sudoku = clean_out[0]
    solution = clean_out[1]

    # new_sudoku = []
    # new_solution = []

    # sud_line = []
    # sol_line = []
    # for i in range(len(sudoku)):
    #     sud_line.append(sudoku[i])
    #     sol_line.append(solution[i])
    #     if i%9 == 8:
    #         new_sudoku.append(sud_line)
    #         new_solution.append(sol_line)
    #         sud_line = []
    #         sol_line = []

    # new_sudoku = [  [".",".","1",  ".",".",".",  ".",".","."],
    #                 [".",".",".",  ".",".",".",  ".",".","."],
    #                 [".",".",".",  ".",".",".",  ".",".","."],

    #                 [".",".",".",  ".",".",".",  ".",".","."],
    #                 [".","1",".",  ".",".",".",  ".",".","."],
    #                 [".",".",".",  ".",".",".",  ".",".","."],

    #                 ["5",".",".",  ".",".",".",  ".",".","."],
    #                 [".",".",".",  ".",".",".",  ".",".","."],
    #                 [".",".",".",  ".",".","1",  ".",".","."]]
    return sudoku, solution

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


def getTileAtPos(x, y):
    for tile in tiles:
        assert isinstance(tile, Tile)
        if tile.x == x and tile.y == y:
            return tile
    return

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
    def __init__(self, size:int, position:int, string:str, tfont: font.Font) -> None:
        self.x = position%9
        self.y = math.floor(position/9)
        super().__init__(
            size, (self.x*size, self.y*size), string, tfont)
        self.row = columns[self.x]
        self.column = rows[self.y]
        self.block = blocks[int(self.y/3)*3+int(self.x/3)]
        # print(str(int(self.y/3)*3+int(self.x/3)))
        self.row.add(self)
        self.column.add(self)
        self.block.add(self)
        self._penmark_font = font.SysFont('Arial', math.floor(size/4))
        self._spenmark_font = font.SysFont('Arial', math.floor(size/3))
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
        self.possibleValues = []

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
                    global sudoku
                    if val != "":
                        # sudoku[self.y*9+self.x] = val
                        
                        sudoku = sudoku[:self.y*9+self.x] + \
                            val + sudoku[self.y*9+self.x + 1:]
                    else:
                        sudoku = sudoku[:self.y*9+self.x] + \
                            "." + sudoku[self.y*9+self.x + 1:]
                    pass
                
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
        self.bg = pygame.Color("green")
        for i, tile in enumerate(tiles):
            assert isinstance(tile, Tile)
            if sudoku[i] != solution[i]:
                if tile.value == "":
                    tile.update_color(pygame.Color("white"), True)
                else:
                    tile.update_color(pygame.Color("red"), True)
                    self.bg = pygame.Color("red")
            elif not tile._locked:
                tile.update_color(pygame.Color("green"), True)
        self.update_sprite()

class NextMoveButton(Tile_parent):
    def __init__(self, size, position, string, font) -> None:
        super().__init__(size, position, string, font)
        self.update_sprite()
        self.numFreeTiles = 0
        
    def select(self):
        self.numFreeTiles = self.getNumFreeTiles()

        while self.numFreeTiles > 0:

            # get all possible values for each tile
            for i, row in enumerate(rows):
                for j, tile in enumerate(row):
                    assert isinstance(tile, Tile)
                    self.assignPossibleValues(i, j)

            # TODO: eliminate possible values 
            # self.remove_candidates()
            newNumFreeTiles = self.getNumFreeTiles()
            # check tiles for sole and unique Candidates
            num, tile = self.getNext()
            if tile != None:
                tile.update_color(pygame.Color("yellow"))
                tile.update_value(str(num))
                print("(" + str(tile.x+1) + ", " + str(tile.y+1) + "): " + str(num))
                
                self.numFreeTiles = newNumFreeTiles
                # break
            else:
                # self.update_sprite()
                for bttn in UIs.sprites():
                    if isinstance(bttn, CheckButton):
                        bttn.select()
                break
                
                # return
                    
                    
    def remove_candidates(self):
        for block in blocks:
            for tile in block:
                assert isinstance(tile, Tile)
                # block = tile.block#             self.getBlock(c,r)

                for i in range(1,10):
                    possibleBlockForVal = []
                    for j, t in enumerate(tile.block):
                        assert isinstance(t, Tile)
                        if str(i) in t.possibleValues:
                            possibleBlockForVal.append(j)

    def getNext (self):
        
        # num, tile = self.soleCandidate()
        # if num != None:
        #     return num, tile

        num, tile = self.uniqueCandidate()
        if num != None:
            print("Unique Candidate:")
            # return num, tile
        
        return num, tile

        # num = self.soleCandidate(tile.x, tile.y)
        # if num != None:
        #     print("sole Candidate:")
        #     return num
        
        

    def soleCandidate(self):
        for tile in tiles:
            assert isinstance(tile, Tile)
            if tile.value == "" or True:
                assert isinstance(tile, Tile)
                if len(tile.possibleValues) == 1:
                    for i in range(1, 10, 1):
                        if [str(i)] == tile.possibleValues:
                            return i, tile
        return (None, None)

    def uniqueCandidate(self):
        for block in blocks:
            possibleBlocks = [t.possibleValues for t in block if isinstance(t, Tile)]
            for i in range(1, 10, 1):
                # count occurences of that number
                poss = [True for j in possibleBlocks if str(i) in j]
                num = poss.count(True)
                if num == 1:        # if there is exactly one occurence, find it
                    # ind = 10
                    for t, tile in enumerate(block):
                        if str(i) in possibleBlocks[t] and possibleBlocks[t] != []:
                            # column = ind%3
                            # row = math.floor(ind/3)
                            # tile = getTileAtPos(column,row)
                            assert isinstance(tile, Tile)
                        # global uniqueAt
                            return i, tile
        return (None, None)
        #                 break
        # if (tile.x, tile.y) == uniqueAt[0]:
        #     assert len(uniqueAt) == 2
        #     return uniqueAt[1]

    def assignPossibleValues(self, x, y):
        impossibleValues = []
        #row
        rootTile = getTileAtPos(x,y)
        assert isinstance(rootTile, Tile)
        if rootTile.value == "":
            for tile in columns[x]:
                assert isinstance(tile, Tile)
                if tile.value != "" and tile.value not in impossibleValues:
                    impossibleValues.append(tile.value)
            for tile in rows[y]:
                assert isinstance(tile, Tile)
                if tile.value != "" and tile.value not in impossibleValues:
                    impossibleValues.append(tile.value)
            for tile in rootTile.block:
                assert isinstance(tile, Tile)
                if tile.value != "" and tile.value not in impossibleValues:
                    impossibleValues.append(tile.value)
                                            
        else:
            impossibleValues = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
            rootTile.possibleValues = []
        rootTile.possibleValues = [x for x in [
            "1", "2", "3", "4", "5", "6", "7", "8", "9"] if x not in impossibleValues]

    def getNumFreeTiles(self):
        num = 0
        for tile in tiles:
            assert isinstance(tile, Tile)
            if tile.value == "":
                num+=1
        return num


if __name__ == "__main__":
    main()
