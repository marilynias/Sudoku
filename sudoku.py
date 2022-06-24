import subprocess as sp
import pygame
import math
from timeit import default_timer as timer
from pygame import display, Surface, sprite, font, Color, Rect
import os
import csv
import queue
import logging
from logging.handlers import QueueHandler, QueueListener


def main():
    # logging: Handling it on a different Thread, to not clog up the processing power
    
    global listener
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
    
    # logging.basicConfig(filename='sudoku.log', encoding='utf-8', level=logging.INFO)





    global edit_mode, holding_mb1, dbcT, tClock, gameBoard, auto, rules
    # Display
    pygame.init()
    display_game = display.set_mode((1000,600))
    display_game.fill(Color("black"))
    
    running = True
    dbcClock = pygame.time.Clock()
    tClock = pygame.time.Clock()
    dbcT = 1000
    auto = False
    cubesize = 60

    rules = Rules()
    gameBoard = GameBoard(cubesize)
    build_UI(cubesize)
    
    # 0 = write full size(tile is that number), 1 = pencil mark (tile can be that number), 2 = strong mark(tile has to be one of these numbers)
    edit_mode = 0  
    holding_mb1 = False
    logging.info("INIT")

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
            listener.stop()
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
            elif event.key == pygame.K_BACKSPACE:
                for tile in tiles:
                    assert isinstance(tile, Tile)
                    if tile.selected:
                        tile.clear()
            elif event.key == pygame.K_a:
                if mods & pygame.KMOD_LCTRL:
                    for tile in tiles:
                        assert isinstance(tile, Tile)
                        tile.select()

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
    # rules.timeTaken = {"assign":0., "soleCand":0., "hiddCand":0., "nakedSub":0., "hiddSub2":0., "hiddSub3":0., "pointSub":0., "xwing":0.}
    for bttn in UIs:
        if isinstance(bttn, UIButton):
            bttn.deselect()
        if isinstance(bttn, CheckButton):
            bttn.deselect()
        else:
            continue
    
    gameBoard.reset()
    logging.info("----- CLEARED -----")

def check_board():
    boardState = ""
    for tile in tiles:
        assert isinstance(tile,Tile)
        boardState += str(tile.value)



    if boardState == gameBoard.solution:            
        for tile in tiles:
            assert isinstance(tile, Tile)
            tile.reset_color()
        return True
    # else:
    validity = None
    for i, tile in enumerate(tiles):
        assert isinstance(tile, Tile)
        if boardState[i] != gameBoard.solution[i]:
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
        self.timeTaken = {"assign":0., "soleCand":0., "hiddCand":0., "nakedSub":0., "hiddSub2":0., "hiddSub3":0., "pointSub":0., "xwing":0., "ywing":0.}
        self.checktime = 0.

    def assignPossibleValues(self) -> bool:
        before = timer()
        couldAssign = False
        # logging.info("Assigning Possible Values...")

        if any(len(tile.possibleValues) == 0 for tile in tiles if isinstance(tile,Tile) and tile.value == 0):
            logging.info("No possible numbers for a Tile, resetting all possibleValues")
            for tile in tiles:
                assert isinstance(tile, Tile)
                tile.possibleValues = [i for i in range(1,10)]
        for rootTile in tiles:
            assert isinstance(rootTile, Tile)
            if rootTile.value == 0:
                if rootTile.possibleValues == []:
                    logging.warning("No possible numbers for this Tile!!, some number is wrong")
                    return False
                
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
        after = timer()
        self.timeTaken["assign"] += after-before
        return couldAssign

    def soleCandidate(self) -> list:
        before = timer()
        listSoles = []
        # logging.info("Finding sole candidates...")
        for tile in tiles:
            assert isinstance(tile, Tile)
            if tile.value == 0:
                if len(tile.possibleValues) == 1:
                    val = tile.possibleValues[0]
                    # logging.info(f"Sole Candidate: ({tile.x+1}, {tile.y+1}): {str(val)}")
                    listSoles.append((tile, val))
        after = timer()
        self.timeTaken["soleCand"] += after-before
        return listSoles

    def hiddenSingles(self) -> list:
        before = timer()
        # logging.info("Finding hidden singles...")
        listHidden = []
        for subset in (rows, blocks, columns):
            for ssub in subset:
                for i in range(1,10):
                    possTilesForVal = [tile for tile in ssub if isinstance(tile,Tile) and tile.value == 0 and i in tile.possibleValues]
                    if len(possTilesForVal) == 1:
                        listHidden.append((possTilesForVal[0], i))
        after = timer()
        self.timeTaken["hiddCand"] += after-before
        return listHidden

    def nakedSubset(self):
        # wenn in x feldern in einer reihe/spalte/block x mögliche zahlen enthalten, können diese zahlen aus den restlichen felderd der reihe/spalte/block gelöscht werden
        before = timer()
        couldRemove = False
        # logging.info("removing naked subsets...")
        for subset in (rows, blocks, columns):
            for ssub in subset:
                lsub = list(ssub)
                for i, tile in enumerate(lsub):
                    assert isinstance(tile,Tile)
                    # lstSameVals = [tile]
                    if tile.value == 0 and len(tile.possibleValues) <5:
                        lstSameVals = [t for t in lsub if isinstance(t,Tile) and t!=tile and t.value == 0 and all(j in tile.possibleValues for j in t.possibleValues)]
                        lstSameVals.append(tile)
                        if len(lstSameVals) == len(tile.possibleValues):
                            for tileRemVal in ssub:
                                if tileRemVal in lstSameVals:
                                    continue
                                assert isinstance(tileRemVal, Tile)
                                for val in tileRemVal.possibleValues:
                                    if val in tile.possibleValues:
                                        # logging.info(f"removing {val} at {tileRemVal.x+1}/{tileRemVal.y+1}")
                                        tileRemVal.possibleValues.remove(val)
                                        couldRemove = True
                            if couldRemove:
                                # if ssub == tile.block:
                                #     logging.info(f"due to naked subset {tile.possibleValues} at block {(int(tile.y/3) * 3) + int(tile.x/3) +1}")
                                # elif ssub == tile.row:
                                #     logging.info(f"due to naked subset {tile.possibleValues} at row {tile.y+1}")
                                # elif ssub == tile.column:
                                #     logging.info(f"due to naked subset {tile.possibleValues} at column {tile.x+1}")
                                
                                after = timer()
                                self.timeTaken["nakedSub"] += after-before
                                return couldRemove
        after = timer()
        self.timeTaken["nakedSub"] += after-before

    def hiddenSubset(self, length:int):
        # logging.info(f"Finding hidden subsets with n={length}...")
        before = timer()
        for groups in (blocks, rows, columns):
            for group in groups:
                # list of numbers that fit in this row/column/box
                if sum(1 for tile in group if isinstance(tile,Tile) and tile.value == 0) < length+1:
                    continue
                poss_vals = [i for i in range(1,10) if any(i in tile.possibleValues for tile in group if isinstance(tile, Tile))]
                if 2 < len(poss_vals):  #filter out 1 and 0 length possibilities
                    maxlen = 2**len(poss_vals)-1
                    for i in range(1, maxlen):
                        if i.bit_count() == length:   # if there are the same amount of bits set as the desired length
                            # 2**j&i checks if the bit at position j is set
                            # take position and take the values of the prev list at the same location
                            comb = [poss_vals[j] for j in range(len(poss_vals)) if 2**j&i]
                            
                            # check for hidden subsets
                            tilesWithNums = set([tile for num in comb for tile in group if isinstance(tile,Tile) and num in tile.possibleValues])
                            if len(tilesWithNums) == length:
                                # check first, because only a very small number of potential hidden subsets are actually hidden subsets and checking is faster
                                if any(num not in comb  for tile in tilesWithNums if isinstance(tile,Tile) for num in tile.possibleValues):
                                    after = timer()
                                    self.timeTaken["hiddSub"+str(length)] += after-before
                                    return comb, tilesWithNums
        after = timer()
        self.timeTaken["hiddSub"+str(length)] += after-before
        return (),()

    def pointingSubset(self):
        before = timer()
        couldRemove = False
        # logging.info("finding pointing subsets...")
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
                                        # if subset == tile.block:
                                        #     logging.info(f"removing {i} at block {(int(tile.y/3) * 3) + int(tile.x/3) +1}")
                                        # elif subset == tile.row:
                                        #     logging.info(f"removing {i} at row {tile.y+1}")
                                        # elif subset == tile.column:
                                        #     logging.info(f"removing {i} at column {tile.x+1}")
                                        couldRemove = True
                                        t.possibleValues.remove(i)
                        if couldRemove:
                            after = timer()
                            self.timeTaken["pointSub"] += after-before
                            return couldRemove

        after = timer()
        self.timeTaken["pointSub"] += after-before
        # logging.info(f"Time taken: {round((after-before)*1000, 2)}ms")
        # logging.info("")                       
        
        return couldRemove

    def xwing(self):
        before = timer()
        # logging.info("removing xwing...")
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
                                        tilesWithNum3 = [t for t in tile3.getSubsets()[i_ss] if isinstance(t, Tile) and i in t.possibleValues and t != tile2 and t!=tile3]
                                        
                                        if len(tilesWithNum3) == 1 and tilesWithNum3[0] in rootTile.getSubsets()[i_s]:
                                            tile4 = tilesWithNum3[0]
                                            tilesWithNum4 = [t for t in tile4.getSubsets()[i_s] if isinstance(t, Tile) and i in t.possibleValues]
                                            
                                            if len(tilesWithNum2) > 2 or len(tilesWithNum4) > 2:    # if there are other Tiles with that Value int the row/column
                                                for t in tilesWithNum2:
                                                    if t != tile2 and t != tile3 and i in t.possibleValues:
                                                        t.possibleValues.remove(i)
                                                        logging.info(f"removing {i} from ({t.x+1}, {t.y+1})")
                                                for t in tilesWithNum4:
                                                    if t != rootTile and t != tile4 and i in t.possibleValues:
                                                        t.possibleValues.remove(i)
                                                        logging.info(f"removing {i} from ({t.x+1}, {t.y+1})")
                                                logging.info(f"Due to XWING {i} at ({rootTile.x+1}, {rootTile.y+1}), ({tile2.x+1}, {tile2.y+1}), ({tile3.x+1}, {tile3.y+1}), ({tile4.x+1}, {tile4.y+1})")
                                                after = timer()
                                                self.timeTaken["xwing"] += after-before
                                                return True
        after = timer()
        self.timeTaken["xwing"] += after-before
        return False

    def ywing(self):
        before = timer()
        for tile in tiles:
            if isinstance(tile, Tile) and len(tile.possibleValues) == 2:
                ycandidates = []
                for subset in tile.getSubsets():
                    for t1 in subset:
                        # any tile with exactly 2 possible values could be a ywing arm
                        if isinstance(t1, Tile) and t1 not in ycandidates and t1.possibleValues != tile.possibleValues and len(t1.possibleValues) == 2 and any(i in tile.possibleValues for i in t1.possibleValues):
                            ycandidates.append(t1)
                # a ywing needs 2 arms
                if len(ycandidates) < 2:
                    break
                
                for t in ycandidates:
                    assert isinstance(t, Tile)
                    for num in t.possibleValues:
                        # eliminate any tile that has a number not represented in any other arm or the roottile
                        if any(num in t3.possibleValues or num in tile.possibleValues for t3 in ycandidates if isinstance(t3, Tile) and t3 != t):
                            pass
                        else:
                            ycandidates.remove(t)
                            break
                if len(ycandidates) < 2:
                    break
                elif len(ycandidates) == 2 and any(s in ycandidates[0].getSubsets() for s in ycandidates[1].getSubsets()):
                    # if the 2 arms of the YWing are in the same row/column/block they cant form a ywing
                        break
                logging.info(f"base vals: {tile.possibleValues}")
                # test all combinations to see if the formed ywing yields any results
                for i, arm1 in enumerate(ycandidates):
                    assert isinstance(arm1, Tile)
                    for arm2 in ycandidates[i+1:]:
                        if isinstance(arm2, Tile) and arm1.possibleValues!=arm2.possibleValues and all(s not in arm1.getSubsets() for s in arm2.getSubsets()):
                            ynum = 0
                            arm1Sub = None
                            arm2Sub = None
                            for j in arm1.possibleValues:
                                if j in arm2.possibleValues:
                                    ynum = j
                            if ynum ==0:
                                logging.error("Arm1 and Arm2 dont share any number")
                                break
                            if ynum in tile.possibleValues:
                                break
                            for iSubset, sub in enumerate(tile.getSubsets()):
                                if sub in arm1.getSubsets():
                                    arm1Sub = iSubset
                                elif sub in arm2.getSubsets():
                                    arm2Sub = iSubset
                            if arm1Sub == None or arm2Sub == None:
                                logging.error("Arm1 and roottile or Arm2 and roottile dont share subset")
                                break

                            for t in arm1.getSubsets()[arm2Sub]:
                                if t in arm2.getSubsets()[arm1Sub] and isinstance(t,Tile):
                                    if ynum in t.possibleValues:
                                        t.possibleValues.remove(ynum)
                                        logging.info(f"YWing: tile ({tile.x+1},{tile.y+1}) cant have val {ynum}" )
                                    # else:
                                    #     logging.info(f"YWing: tile {tile.x+1}, {tile.y+1} cant have val {ynum}" )
                            

                    
        after = timer()
        self.timeTaken["ywing"] += after-before

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
        with sp.Popen(["node", os.path.join(filePath, "qqwing-1.3.4", "qqwing-main-1.3.4.js"), 
            "--generate", "1", "--one-line", "--solution", "--difficulty", "expert"], stdout=sp.PIPE) as proc:
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
            logging.warning("empty output")
            sudoku =    '.........9.46.7....768.41..3.97.1.8.7.8...3.1.513.87.2..75.261...54.32.8.........'
            solution =  '836719524451382679297645813382194765679523148145867392918436257764258931523971486'

        return sudoku, solution

    def _get_sudoku_from_cvs(self):
        with open('sudoku.csv', newline='') as f:
            reader = csv.reader(f)
            logging.info(f"Lines read: {reader.line_num}")
            counter = 0
            for row in reader:
                if counter > self.ind:
                    logging.info(f"Sudoku: {row[0]}")
                    logging.info(f"Solution: {row[1]}")
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
        self.possibleValues = []
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

    def getSubsets(self):
        return (self.column, self.row, self.block)

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
            elif isinstance(bttn, CheckButton):
                self.checkBttn = bttn

    
    def select(self, mod = False):
        before = timer()
        solved = False
        
        while 1:
            if self.getNext():
                if mod: continue
                else: break
            else:
                solved = check_board()
                break
        
        after = timer()
        for key, val in rules.timeTaken.items():
            rules.timeTaken[key] = round(val, 6)
        logging.warning(f"times: {rules.timeTaken}")
        for tile in tiles:
            assert isinstance(tile,Tile)
            tile.update_sprite()
        if solved:
            logging.warning(f"Time to solve: {round(after-before, 4)}s")
        elif solved == None:
            logging.warning(f"Couldnt solve. Time: {round(after-before, 4)}s")
        else:
            logging.warning(f"Time for Step: {round(after-before, 4)}s")
        if any(val > 1 for key, val in rules.timeTaken.items()):
            pass

    def getNext(self):
        before = timer()
        if rules.assignPossibleValues():
            assignPossibleValues = timer()
            return True
        t_assignPossibleValues = timer()
        listSoles = rules.soleCandidate()
        t_soleCand = timer()
        if len(listSoles) > 0:
            # logging.info("Sole candidates:")
            self.writeVal(listSoles)
            return True
        
        listHidden= rules.hiddenSingles()
        t_hiddenCand = timer()
        if len(listHidden) > 0:
            # logging.info("Hidden singles:")
            self.writeVal(listHidden)
            return True
        nSubset = rules.nakedSubset()
        t_nSubset = timer()
        if nSubset:
            return True
        subset, group = rules.hiddenSubset(2)
        # logging.info(f"Time taken: {round((t_nSubset-t_hiddenCand)*1000, 2)}ms")
        t_hSubset2 = timer()
        if len(subset)>0:
            logging.warning(f"Hidden pair: {subset}")
            self._rem_subset_from_group(subset, group)
            return True
        # logging.info(f"Time taken: {round((t_hSubset2-t_nSubset)*1000, 2)}ms")
        subset, group = rules.hiddenSubset(3)
        t_hSubset3 = timer()
        if len(subset)>0:
            logging.warning(f"Hidden triplets: {subset}")
            self._rem_subset_from_group(subset, group)
            return True
        # logging.info(f"Time taken: {round((t_hSubset3-t_hSubset2)*1000, 2)}ms")
        if rules.pointingSubset():
            logging.info("due to pointing subset")
            return True
        xwing = rules.xwing()
        if xwing:
            return True
        ywing = rules.ywing()
        if ywing:
            pass
        
        
        else: 
            logging.warning("Nothing was able to be eliminated")
            return False
            
    def writeVal(self, lst):
        for i in lst:                
            # logging.info(f"({i[0].x+1}, {i[0].y+1}): {i[1]}")
            i[0].clear()
            i[0].update_value(str(i[1]))
        # logging.info("")

    def _rem_subset_from_group(self, subset, group):
        for tile in group:
            assert isinstance(tile,Tile)
            for num in tile.possibleValues:
                if num not in subset:
                    tile.possibleValues.remove(num)
                    # logging.warning(f"removing {num} from ({tile.x+1}, {tile.y+1})")

class RemCandButton(Tile_parent):
    def __init__(self, size:int, position:tuple, string:str, font:str) -> None:
        super().__init__(size, position, string, font)
        self.update_sprite()
        
    def select(self, mod=False):
        # self.assignPossibleValues()
        if self.remove_candidates():
            pass
        else:
            logging.info("no more")
                             
    def remove_candidates(self):
        before = timer()
        if rules.hiddenSubset(2):
            hiddenTimer = timer()
            # logging.info(f"Hidden: {(hiddenTimer-before)*1000}")
            return True
        hiddenTimer = timer()
        if rules.pointingSubset():
            pointingTimer = timer()
            # logging.info(f"Pointing: {(pointingTimer-hiddenTimer)*1000}")
            return True
        pointingTimer = timer()
        if rules.nakedSubset():
            nakedTimer = timer()
            logging.info(f"Naked: {(nakedTimer-pointingTimer)*1000}")
            return True
        nakedTimer = timer()
        if rules.xwing():
            xwingTimer = timer()
            logging.info(f"X-Wing: {(xwingTimer-nakedTimer)*1000}")
            return True

        # logging.info(f"Hidden: {(hiddenTimer-before)*1000}, Pointing: {(nakedTimer-pointingTimer)*1000}, Naked: {(pointingTimer-hiddenTimer)*1000}")
        return False

class FillCandButton(Tile_parent):
    def __init__(self, size:int, position:tuple, string:str, font:str) -> None:
        super().__init__(size, position, string, font)
        self.update_sprite()
        
    def select(self, mod=False):
        # self.assignPossibleValues()
        rules.assignPossibleValues()

class fillValButton(Tile_parent):
    def __init__(self, size:int, position:tuple, string:str, font:str) -> None:
        super().__init__(size, position, string, font)
        self.update_sprite()

    def select(self, mod=False):
        if rules.hiddenSingles():
            return True
        elif rules.soleCandidate():
            return True
        else:return False

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
