from operator import and_
import subprocess as sp
import pygame
import math
from timeit import default_timer as timer
from pygame import mouse, display, Surface, sprite, font, time
import os



def main():
    global tiles, rows, blocks, columns, UIs, edit_mode, holding_mb1, dbcT, sudoku, solution, tClock
    # Display
    pygame.init()
    display_game = display.set_mode((800,600))
    display_game.fill(pygame.Color("black"))
    cubesize = 60
    gameBoard = Surface((cubesize*9, cubesize*9))
    gameBoard.fill(pygame.Color("white"))
    running = True
    dbcClock = time.Clock()
    tClock = time.Clock()
    dbcT = 1000
    

    # Sudoku
    sudoku, solution = get_sudoku()
    

    #board
    boardLocation = (20,20)
    
    tiles = sprite.Group()
    rows = [sprite.Group() for row in range(9)]
    columns = [sprite.Group() for colum in range(9)]
    blocks = [sprite.Group() for block in range(9)]
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


    # add UI
    ui_x = mon.current_w - cubesize - 10
    gap = 10
    size_margin = cubesize+gap
    UIs.add(UIButton(cubesize, (ui_x - size_margin*2, gap), "Mark", ui_font, 1))
    UIs.add(UIButton(cubesize, (ui_x - size_margin*2, size_margin*1 + gap), "SMark", ui_font, 2))
    UIs.add(ClearButton(cubesize, (ui_x - size_margin*2, size_margin*2 + gap), "clear", ui_font))
    UIs.add(CheckButton(cubesize, (ui_x - size_margin*2, size_margin*3 + gap), "Check", ui_font))

    UIs.add(FillCandButton(cubesize, (ui_x, gap), "FillCand", ui_font))    
    UIs.add(fillValButton(cubesize, (ui_x, size_margin*1 + gap), "FillVal", ui_font))
    UIs.add(RemCandButton(cubesize, (ui_x, size_margin*2 + gap), "RemoveCand", ui_font))
    UIs.add(SolveButton(cubesize, (ui_x, size_margin*3 + gap), "Solve", ui_font))
    UIs.add(ResetButton(cubesize, (ui_x, size_margin*5 + gap), "Reset", ui_font))



    UIs.add(ColorButton(cubesize, (ui_x - size_margin,  + gap), "", ui_font, pygame.Color("grey")))
    UIs.add(ColorButton(cubesize, (ui_x - size_margin, size_margin*1 + gap), "", ui_font, pygame.Color("green")))
    UIs.add(ColorButton(cubesize, (ui_x - size_margin, size_margin*2 + gap), "", ui_font, pygame.Color("red")))
    UIs.add(ColorButton(cubesize, (ui_x - size_margin, size_margin*3 + gap), "", ui_font, pygame.Color("yellow")))

def get_sudoku():
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

        # clean_out[0] = '.........9.46.7....768.41..3.97.1.8.7.8...3.1.513.87.2..75.261...54.32.8.........'
        # clean_out[1] = "583219467914637825276854139349721586728965341651348792497582613165493278832176954"
        #double: '.........9.46.7....768.41..3.97.1.8.7.8...3.1.513.87.2..75.261...54.32.8.........'
        sudoku = clean_out[0].replace(".", "0")
        # assert isinstance(sudoku, str)
        
        solution = clean_out[1]
    
    else:
        print("empty output")
        sudoku = '.........9.46.7....768.41..3.97.1.8.7.8...3.1.513.87.2..75.261...54.32.8.........'
        solution = '836719524451382679297645813382194765679523148145867392918436257764258931523971486'

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
        self.title = string
        self.txtfont = font
        self._txt_pos = (0, 0)
        self.txt = self.txtfont.render(self.title, True, (0, 0, 0))
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
        self.title = val
        self.txt = self.txtfont.render(self.title, True, (0, 0, 0))
        self.update_sprite()

class Tile(Tile_parent):
    def __init__(self, size:int, position:int, value:str, tfont: font.Font) -> None:
        self.x = position%9
        self.y = math.floor(position/9)

        super().__init__(
            size, (self.x*size, self.y*size), value, tfont)
        self.row = columns[self.y]
        self.column = rows[self.x]
        self.block = blocks[int(self.y/3)*3+int(self.x/3)]
        # print(str(int(self.y/3)*3+int(self.x/3)))
        self.row.add(self)
        self.column.add(self)
        self.block.add(self)

        self._penmark_font = font.SysFont('Arial', math.floor(size/4))
        self._spenmark_font = font.SysFont('Arial', math.floor(size/3))

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
        
        if self.value == 0:
            self.possibleValues = [i for i in range(1,10)]
            self._locked = False
            self.bg = pygame.Color("white")
        else:
            self.possibleValues = []
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
        if self.bg != pygame.Color("white") and self.bg != pygame.Color("lightgrey"):
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
                if tile.value == self.value:
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
                    
                    sudoku = sudoku[:self.y*9+self.x] + \
                        str(val) + sudoku[self.y*9+self.x + 1:]
                else:
                    sudoku = sudoku[:self.y*9+self.x] + \
                        "0" + sudoku[self.y*9+self.x + 1:]
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
            self.possibleValues = []
            self.value = 0
            self.update_sprite()

    def reset(self, value:str):
        self.value = int(value)
        self.pen_marks = []
        self.spen_marks = []

        if self.value == 0:
            self.possibleValues = [i for i in range(1,10)]
            self._locked = False
            self.bg = pygame.Color("white")
        else:
            self.possibleValues = []
            self._locked = True
            self.bg = pygame.Color("lightgrey")
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
                if tile.value == 0:
                    tile.update_color(pygame.Color("white"), True)
                else:
                    tile.update_color(pygame.Color("red"), True)
                    self.bg = pygame.Color("red")
            elif not tile._locked:
                tile.update_color(pygame.Color("green"), True)
        self.update_sprite()

class SolveButton(Tile_parent):
    def __init__(self, size, position, string, font) -> None:
        super().__init__(size, position, string, font)
        self.update_sprite()
        self.numFreeTiles = 0

        for bttn in UIs.sprites():
            if isinstance(bttn, CheckButton):
                self.checkBttn = bttn
            elif isinstance(bttn, RemCandButton):
                self.removeCandBttn = bttn
            elif isinstance(bttn, fillValButton):
                self.fillValBttn = bttn
            elif isinstance(bttn, FillCandButton):
                self.fillcandBttn = bttn
    def select(self):
        self.numFreeTiles = self.getNumFreeTiles()
        self.fillcandBttn.assignPossibleValues ()
        while self.numFreeTiles > 0:        # first go through
            newNumFreeTiles = self.getNumFreeTiles()
            if self.fillValBttn.select():
                self.numFreeTiles = newNumFreeTiles
            else:
                if self.removeCandBttn.remove_candidates():
                    continue
                # if self.remove_candidates():
                #     continue
                else:
                    self.checkBttn.select()
                    break
                             
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
                                    print(
                                        f"{i} only possible in Box {ib + 1} column {possibleTileForVar[0].x + 1}, therefore removing it from its column")
                                    couldRemove = True
                                    removing = True
                                    t.update_sprite()
        print("--------")
        return couldRemove
    def getNumFreeTiles(self):
        num = 0
        for tile in tiles:
            assert isinstance(tile, Tile)
            if tile.value == 0:
                num+=1
        return num

class RemCandButton(Tile_parent):
    def __init__(self, size, position, string, font) -> None:
        super().__init__(size, position, string, font)
        self.update_sprite()
        
    def select(self):
        # self.assignPossibleValues()
        if self.remove_candidates():
            pass
        else:
            print("no more")
                             
    def remove_candidates(self):
        if self.lockedSingle():       # assign possible values and renove candidates
            return True
        elif self.nakedSubset():
            return True
        if self.hiddenSubset():
            return True
        else:
            return False

    def lockedSingle(self):
        # build a list of the index of the tiles in a block that can have that number
        # self.assignPossibleValues()
        couldRemove = False
        # removing = True
        # while removing:
        #     removing = False
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
                                    print(f"removing {val} at {tileRemVal.x+1}/{tileRemVal.y+1} ")
                                    tileRemVal.possibleValues.remove(val)
                                    tileRemVal.update_sprite()
                                    couldRemove = True
                        if couldRemove:
                            print(f"naked subset: {tile.possibleValues} in:")
                            if subset == tile.block:
                                print(f"at block {(int(tile.y/3) * 3) + int(tile.x/3) +1}")
                            elif subset == tile.row:
                                print(f"at row {tile.y+1}")
                            elif subset == tile.column:
                                print(f"at column {tile.x+1}")

                            # for t in sameTiles:
                            #     print(f" {t.x}/{t.y}")
                            return couldRemove

    def hiddenSubset(self):
        couldRemove = False
        for group in (blocks, rows, columns):
            for subset in group:        # subset = specific row/column/block
                allTileValues = []      # [[tiles containing 1], [tiles containing 2], [etc]]
                for i in range(1,10):
                    allTileValues.append([tile for tile in subset if isinstance(tile, Tile) and i in tile.possibleValues])
                for i, numberList in enumerate(allTileValues):
                    if len(numberList) <2:
                        continue
                    # enter lists of tiles, which numbers can be in the same tiles
                    # ex: of two tiles have 6 and 2 tiles have 7, see if they are the same
                    # sametiles =  [compareList for j, compareList in enumerate(allTileValues) if i!=j and numberList == compareList]
                    # Hidden Pair:
                    for j, compareList in enumerate(allTileValues):     #
                        if i!=j and numberList == compareList and len(compareList) == 2:
                            # if len(sametiles) > 1:
                            
                            for tile in compareList:
                                assert isinstance(tile,Tile)
                                if any(n not in (i+1,j+1) for n in tile.possibleValues):
                                        couldRemove = True
                                        print(f"{i+1}, {j+1}, prev:{tile.possibleValues}")
                                        for n in tile.possibleValues:
                                            if n not in (i+1,j+1):
                                                tile.possibleValues.remove(n)
                                        print(f"{tile.possibleValues} at {tile.x+1}, {tile.y+1}")
                                tile.update_sprite()
                            


                    
        return couldRemove


class FillCandButton(Tile_parent):
    def __init__(self, size, position, string, font) -> None:
        super().__init__(size, position, string, font)
        self.update_sprite()
        
    def select(self):
        # self.assignPossibleValues()
        self.assignPossibleValues()

    def assignPossibleValues(self):
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
            else:
                rootTile.possibleValues = []
                rootTile.pen_marks = []

            rootTile.update_sprite()

class fillValButton(Tile_parent):
    def __init__(self, size, position, string, font) -> None:
        super().__init__(size, position, string, font)
        self.update_sprite()
        
    def select(self):
        num, tile = self.getNext()
        if tile != None and num != None:
            # tile.update_color(pygame.Color("yellow"))
            tile.clear()
            tile.update_value(str(num))
            self.removeCand(tile, num)
            print(f"({tile.x+1}, {tile.y+1}): {str(num)}")
            return True
        else:
            return False
        # self.assignPossibleValues()
        before = timer()
        
    def getNext(self):
        num, tile = self.soleCandidate()
        if num != None:
            print("Sole Candidate:")
            return num, tile

        num, tile = self.uniqueCandidate()
        if num != None:
            print("Unique Candidate:")
            return num, tile
        return num, tile

    def soleCandidate(self):
        for tile in tiles:
            assert isinstance(tile, Tile)
            if tile.value == 0:
                if len(tile.possibleValues) == 1:
                    return tile.possibleValues[0], tile
        return (None, None)

    def uniqueCandidate(self):
        for i in range(1, 10):
            for block in blocks:
                # count occurences of that number
                num = sum(1 for tile in block
                          if isinstance(tile, Tile) and i in tile.possibleValues)
                if num == 1:        # if there is exactly one occurence, find it
                    for t in block:
                        assert isinstance(t, Tile)
                        if i in t.possibleValues:
                            return i, t
            
            for row in rows:
                # count occurences of that number
                num = sum(1 for tile in row
                          if isinstance(tile, Tile) and i in tile.possibleValues)
                if num == 1:        # if there is exactly one occurence, find it
                    for t in row:
                        assert isinstance(t, Tile)
                        if i in t.possibleValues:
                            return i, t

            for column in columns:
                # count occurences of that number
                num = sum(1 for tile in column
                          if isinstance(tile, Tile) and i in tile.possibleValues)
                if num == 1:        # if there is exactly one occurence, find it
                    for t in column:
                        assert isinstance(t, Tile)
                        if i in t.possibleValues:
                            return i, t
        return (None, None)

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
    def __init__(self, size, position, string, font) -> None:
        super().__init__(size, position, string, font)
        self.update_sprite()
    
    def select(self):
        global edit_mode, sudoku, solution
        edit_mode = 0
        for bttn in UIs:
            if isinstance(bttn, UIButton):
                bttn.deselect()

        sudoku, solution = get_sudoku()
        for i, tile in enumerate(tiles):
            assert isinstance(tile, Tile)
            tile.reset(sudoku[i])
        print("----- CLEARED -----")


if __name__ == "__main__":
    main()
