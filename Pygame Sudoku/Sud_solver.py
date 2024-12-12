
import sys
import logging, os
from typing import Iterator
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from pg_Sudoku_template import GameBoard, Tile, SolveBttn, pygame
from timeit import default_timer as timer

# SolveBttn.onDone = lambda self: self.gameBoard.reset() if self.gameBoard.check_solution() else ...

# GameBoard, Tile, SolveBttn = GameBoard, Tile, SolveBttn
def remove_val_from_subs_poss(tile:Tile, val:int):
        # if not self.value:
        tile.clear()
        tile.set_value(val)
            # self.value = val
        for subs in tile.groups:
            for t in subs:
                    assert type(t) == Tile
                    if val in t.possibleValues:
                        t.possibleValues.remove(val)

def _rem_subset_from_group(subset:list[int], group:list[Tile]):
        for tile in group:
            assert isinstance(tile,Tile)
            for num in tile.possibleValues[:-1]:
                if num not in subset:
                    tile.possibleValues.remove(num)

def _get_poss_tiles(group:list[Tile], i:int) -> list[Tile]:
    return [t for t in group if t.value == 0 and i in t.possibleValues]


class ChainError(Exception):
    def __call__(self, *args, **kwds):
        return super().__call__(*args, **kwds)

class SudSolver(GameBoard):
    def __init__(self, cubesize: int = 10, sud=None, sol=None, difficulty="simple") -> None:
        super().__init__(cubesize, sud, sol, difficulty)
        logging.info("Starting Sudoku: " +
                     "".join([str(tile.value) for tile in self.tiles]))
        self.successfull_timeTaken = {
            "assign": 0, 
            "soleCand": 0, 
            "hiddCand": 0, 
            "nSubset": 0, 
            "hiddSub2": 0, 
            "hiddSub3": 0, 
            "point": 0, 
            "xwing":0,
            "ywing":0,
            "boxLine": 0,
            "backtrack": 0,
            "simple_coloring":0}
        self.successfull_numUsed = self.successfull_timeTaken.copy()
        self.timeTaken = self.successfull_timeTaken.copy()
        self.numUsed = self.successfull_timeTaken.copy()
        self.done = False
        
    def writeVal(self, lst):
        for i in lst:
            remove_val_from_subs_poss(i[0], i[1])
    def solve(self):
        if self.done:
            logging.info("Already solved")
            # self.reset() 
            self.done = False
        s = self.step()
        self.refresh_all()
        if not s:
            self.check_board()
            self.done = True
            logging.info("Final Sudoku: " + "".join([str(tile.value) for tile in self.tiles]))
            logging.info(
                "avg Time in ms each step takes when not finding a solution: ")
            logging.info(self.get_avg_times())
            logging.info("")
            logging.info(
                "avg Time in ms each step takes when finding a solution: ")
            logging.info(self.get_avg_suc_times())
        return s

    def step(self):
        before = timer()
        if  self.assignPossibleValues():
            self.successfull_timeTaken["assign"] += timer() - before
            self.successfull_numUsed["assign"] += 1
            return True
        t_assignPossibleValues = timer()
        self.timeTaken["assign"] = t_assignPossibleValues - before
        self.numUsed["assign"] += 1
        
        listSoles =  self.soleCandidate()
        t_soleCand = timer()
        if len(listSoles) > 0:
            self.successfull_timeTaken["soleCand"] += t_soleCand - t_assignPossibleValues
            self.successfull_numUsed["soleCand"] += 1
            # logging.info("Sole candidates:")
            self.writeVal(listSoles)
            return True
        self.timeTaken["soleCand"] += t_soleCand - t_assignPossibleValues
        self.numUsed["soleCand"] += 1

        listHidden =  self.hiddenSingles()
        t_hiddenCand = timer()
        if len(listHidden) > 0:
            self.successfull_timeTaken["hiddCand"] += t_hiddenCand - t_soleCand
            self.successfull_numUsed["hiddCand"] += 1
            # logging.info("Hidden singles:")
            self.writeVal(listHidden)
            return True
        self.timeTaken["hiddCand"] += t_hiddenCand - t_soleCand
        self.numUsed["hiddCand"] += 1

        nSubset =  self.nakedSubset()
        t_nSubset = timer()
        if nSubset:
            self.successfull_timeTaken["nSubset"] += t_nSubset - t_hiddenCand
            self.successfull_numUsed["nSubset"] += 1
            return True
        self.timeTaken["nSubset"] += t_nSubset - t_hiddenCand
        self.numUsed["nSubset"] += 1

        subset, group =  self.hiddenSubset(2)
        # logging.info(f"Time taken: {round((t_nSubset-t_hiddenCand)*1000, 2)}ms")
        t_hSubset2 = timer()
        if len(subset) > 0:
            self.successfull_timeTaken["hiddSub2"] += t_hSubset2 - t_nSubset
            self.successfull_numUsed["hiddSub2"] += 1
            # logging.warning(f"Hidden pair: {subset}")
            _rem_subset_from_group(subset, group)
            return True
        self.timeTaken["hiddSub2"] += t_hSubset2 - t_nSubset
        self.numUsed["hiddSub2"] += 1

        # logging.info(f"Time taken: {round((t_hSubset2-t_nSubset)*1000, 2)}ms")
        subset, group =  self.hiddenSubset(3)
        t_hSubset3 = timer()
        if len(subset) > 0:
            self.successfull_timeTaken["hiddSub3"] += t_hSubset3 - t_hSubset2
            self.successfull_numUsed["hiddSub3"] += 1
            # logging.warning(f"Hidden triplets: {subset}")
            _rem_subset_from_group(subset, group)
            return True
        self.timeTaken["hiddSub3"] += t_hSubset3 - t_hSubset2
        self.numUsed["hiddSub3"] += 1
        
        # logging.info(f"Time taken: {round((t_hSubset3-t_hSubset2)*1000, 2)}ms")
        if  self.pointingSubset():
            self.successfull_timeTaken["point"] += timer() - t_hSubset3
            self.successfull_numUsed["point"] += 1
            # logging.info("due to pointing subset")
            return True
        t_pointing = timer()
        self.timeTaken["point"] += t_pointing - t_hSubset3
        self.numUsed["point"] += 1

        box_line_reduction =  self.box_line_reduction()
        t_boxLine = timer()

        if box_line_reduction:
            self.successfull_timeTaken["boxLine"] += t_boxLine - t_pointing
            self.successfull_numUsed["boxLine"] += 1
            self.suc
            return True

        self.timeTaken["boxLine"] += t_boxLine - t_pointing
        self.numUsed["boxLine"] += 1        

        xwing =  self.xwing()
        t_xwing = timer()
        if xwing:
            self.successfull_timeTaken["xwing"] += t_xwing - t_boxLine
            self.successfull_numUsed["xwing"] += 1
            return True
        self.timeTaken["xwing"] += t_xwing - t_boxLine
        self.numUsed["xwing"] += 1

        ywing =  False#self.ywing()
        t_ywing = timer()
        if ywing:
            self.successfull_timeTaken["ywing"] += t_ywing - t_xwing
            self.successfull_numUsed["ywing"] += 1
            return True
        self.timeTaken["ywing"] += t_ywing - t_xwing
        self.numUsed["ywing"] += 1

        simple_coloring =  self.simple_coloring()
        t_simple_coloring = timer()
        if simple_coloring:
            self.successfull_timeTaken["simple_coloring"] += t_simple_coloring - t_ywing
            self.successfull_numUsed["simple_coloring"] += 1
            return True
        self.timeTaken["simple_coloring"] += t_simple_coloring - t_ywing
        self.numUsed["simple_coloring"] += 1

        # self.timeTaken["ywing"] = t_ywing - t_xwing
        logging.warning("Nothing was able to be eliminated")
        return False

    @property
    def all_sets(self) -> Iterator[pygame.sprite.Group]:
        for subset in (self.rows, self.blocks, self.columns):        
            for ssub in subset:
                yield ssub

    def assignPossibleValues(self) -> bool:
        couldAssign = False
        # logging.info("Assigning Possible Values...")

        if any(len(tile.possibleValues) == 0 for tile in self.tiles if isinstance(tile, Tile) and tile.value == 0):
            logging.info(
                "No possible numbers for a Tile, resetting all possibleValues")
            # raise Exception("No possible numbers for a Tile")
            for tile in self.tiles:
                assert isinstance(tile, Tile)
                tile.possibleValues = [i for i in range(1, 10)]
        for rootTile in self.tiles:
            assert isinstance(rootTile, Tile)
            if rootTile.value == 0:
                if rootTile.possibleValues == []:
                    logging.warning(
                        "No possible numbers for this Tile!!, some number is wrong")
                    raise ValueError(
                        "No possible numbers for this Tile!!, some number is wrong")
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

        return couldAssign

    def soleCandidate(self) -> list:
        listSoles = []
        # logging.info("Finding sole candidates...")
        for tile in self.tiles:
            assert isinstance(tile, Tile)
            if tile.value == 0 and len(tile.possibleValues) == 1:
                listSoles.append((tile, tile.possibleValues[0]))
        return set(listSoles)

    def hiddenSingles(self) -> list:
        # logging.info("Finding hidden singles...")
        listHidden = []
        for group in self.all_sets:
            for i in range(1, 10):
                possTilesForVal = [tile for tile in group if isinstance(
                    tile, Tile) and tile.value == 0 and i in tile.possibleValues]
                if len(possTilesForVal) == 1:
                    listHidden.append((possTilesForVal[0], i))
        return set(listHidden)

    def nakedSubset(self):
        # wenn in x feldern in einer reihe/spalte/block x mögliche zahlen enthalten, können diese zahlen aus den restlichen felderd der reihe/spalte/block gelöscht werden
        couldRemove = False
        # logging.info("removing naked subsets...")
        for group in self.all_sets:
            lsub = list(group)
            for tile in lsub:
                assert isinstance(tile, Tile)
                # lstSameVals = [tile]
                if tile.value != 0 or len(tile.possibleValues) > 4:
                    continue 

                lstSameVals = [t for t in lsub if isinstance(t, Tile) and t != tile and t.value == 0 and all(
                    j in tile.possibleValues for j in t.possibleValues)]
                lstSameVals.append(tile)
                if len(lstSameVals) != len(tile.possibleValues):
                    continue

                check = (group, tile.block) if all(
                    t in tile.block for t in lstSameVals) else (group,)
                for s in check:
                    for tileRemVal in s:
                        if tileRemVal in lstSameVals:
                            continue
                        assert isinstance(tileRemVal, Tile)
                        for val in tileRemVal.possibleValues:
                            if val in tile.possibleValues:
                                # logging.info(f"removing {val} at {tileRemVal.x+1}/{tileRemVal.y+1}")
                                tileRemVal.possibleValues.remove(
                                    val)
                                couldRemove = True
        return couldRemove

    def hiddenSubset(self, length: int):
        assert length in (2,3,4)
        # logging.info(f"Finding hidden subsets with n={length}...")
        for group in self.all_sets:
            # list of numbers that fit in this row/column/box
            if sum(1 for tile in group if isinstance(tile, Tile) and tile.value == 0) <= length:
                continue
            poss_vals = [i for i in range(1, 10) if any(
                i in tile.possibleValues for tile in group if isinstance(tile, Tile))]
            if 2 < len(poss_vals):  # filter out 1 and 0 length possibilities
                maxlen = 2**len(poss_vals)-1
                for i in range(1, maxlen):
                    if i.bit_count() != length:   # if there are the same amount of bits set as the desired length
                        continue
                    # 2**j&i checks if the bit at position j is set
                    # take position and take the values of the prev list at the same location
                    comb = [poss_vals[j]
                            for j in range(len(poss_vals)) if 2**j & i]

                    # check for hidden subsets
                    tilesWithNums = set([tile for num in comb for tile in group if isinstance(
                        tile, Tile) and num in tile.possibleValues])
                    if len(tilesWithNums) == length and any(num not in comb for tile in tilesWithNums if isinstance(tile, Tile) for num in tile.possibleValues):
                        # check first, because only a very small number of potential hidden subsets are actually hidden subsets and checking is faster
                        return comb, tilesWithNums

        return (), ()

    def pointingSubset(self):
        couldRemove = False
        # logging.info("finding pointing subsets...")
        for tile in self.tiles:
            assert isinstance(tile, Tile)
            for i in tile.possibleValues:
                for subset in tile.groups:
                    numInTiles = [t for t in subset if isinstance(
                        t, Tile) and i in t.possibleValues]

                    if len(numInTiles) < 2:
                        continue
                    for sub in tile.groups:
                        if subset == sub or not all(t in sub for t in numInTiles):
                            continue
                        for t in sub:
                            if isinstance(t, Tile) and i in t.possibleValues and not t in subset:
                                couldRemove = True
                                t.possibleValues.remove(i)
        return couldRemove

    def box_line_reduction(self) -> bool:
        could_remove = False
        for sub in (self.columns, self.rows):
            for group in sub:
                for num in range(1, 10):
                    possTilesForVal = [
                        tile for tile in group if tile.value == 0 and num in tile.possibleValues
                    ]
                    if len(possTilesForVal) < 2 or not all((
                        t in possTilesForVal[0].block
                        for t in possTilesForVal
                    )):
                        continue
                    for t in possTilesForVal[0].block:
                        if num in t.possibleValues and t not in group:
                            logging.info("boxline: removed %d", num)
                            t.possibleValues.remove(num)
                            could_remove = True
        assert not could_remove
        return could_remove

    def xwing(self):
        could_remove = False
        for cr, ssubs in enumerate((self.columns, self.rows)):
            for ind, sub in enumerate(ssubs):
                for num in range(1, 10):
                    possTilesForVal = _get_poss_tiles(sub, num)
                    # first row/col with exactly 2 tiles
                    if len(possTilesForVal) != 2:
                        continue

                    ocr = (possTilesForVal[0].column, possTilesForVal[0].row)[cr-1], \
                        (possTilesForVal[1].column, possTilesForVal[1].row)[cr-1]

                    for sub2 in ssubs[ind+1:]:
                        possTilesForVal2 = _get_poss_tiles(sub2, num)

                        if len(possTilesForVal2) != 2:
                            continue

                        # second row/col with exactly 2 tiles where the col/row is the same
                        p2cr = (possTilesForVal2[0].column, possTilesForVal2[0].row)[cr-1], \
                                                    (possTilesForVal2[1].column, possTilesForVal2[1].row)[cr-1]
                        
                        
                        # opposite col/row where (hopefully) the numbers can be eliminated
                        if sub == sub2 or p2cr != ocr:
                            continue

                        possEliminate = [
                            tile for tile in ocr[0] if tile.value == 0 and num in tile.possibleValues
                        ], [
                            tile for tile in ocr[1] if tile.value == 0 and num in tile.possibleValues
                        ]

                        for tset in possEliminate:
                            for t in tset:
                                if num not in t.possibleValues or t in possTilesForVal or t in possTilesForVal2:
                                    continue
                                t.possibleValues.remove(num)
                                logging.info(
                                    f"removing {num} from ({t.x+1}, {t.y+1})")
                                could_remove = True

        return could_remove
    
    def _ywing(self):
        could_remove = False
        for tile in self.tiles:
            if isinstance(tile, Tile) and len(tile.possibleValues) == 2:
                ycandidates = []
                for subset in (tile.row, tile.column, tile.block):
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
                elif len(ycandidates) == 2 and any(s in ycandidates[0].groups for s in ycandidates[1].groups):
                    # if the 2 arms of the YWing are in the same row/column/block they cant form a ywing
                    break
                logging.info(f"base vals: {tile.possibleValues}")
                # test all combinations to see if the formed ywing yields any results
                for i, arm1 in enumerate(ycandidates):
                    assert isinstance(arm1, Tile)
                    for arm2 in ycandidates[i+1:]:
                        if isinstance(arm2, Tile) and arm1.possibleValues != arm2.possibleValues and all(s not in arm1.groups for s in arm2.groups):
                            ynum = 0
                            arm1Sub = None
                            arm2Sub = None
                            for j in arm1.possibleValues:
                                if j in arm2.possibleValues:
                                    ynum = j
                            if ynum == 0:
                                logging.error(
                                    "Arm1 and Arm2 dont share any number")
                                break
                            if ynum in tile.possibleValues:
                                break
                            for iSubset, sub in enumerate(tile.groups):
                                if sub in arm1.groups:
                                    arm1Sub = iSubset
                                elif sub in arm2.groups:
                                    arm2Sub = iSubset
                            if arm1Sub == None or arm2Sub == None:
                                logging.error(
                                    "Arm1 and roottile or Arm2 and roottile dont share subset")
                                break

                            for t in arm1.groups[arm2Sub]:
                                if t in arm2.groups[arm1Sub] and isinstance(t, Tile):
                                    if ynum in t.possibleValues:
                                        t.possibleValues.remove(ynum)
                                        logging.info(
                                            f"YWing: tile ({tile.x+1},{tile.y+1}) cant have val {ynum}")
                                        could_remove = True

                                    # else:
                                    #     logging.info(f"YWing: tile {tile.x+1}, {tile.y+1} cant have val {ynum}" )
        return could_remove
    

    def _offchain_contradiction(self, chain: dict[Tile:bool], num):
        """ https://www.sudokuwiki.org/Simple_Colouring Rule 4 - Two colours 'elsewhere'"""
        could_remove = False
        checked = []
        for tile, onoff in chain.items():
            for ssub in tile.connected_possible(num):
                if len(ssub) < 2:
                    continue
                for t in ssub:
                    if t in checked or t == tile or t in chain.keys():
                        continue
                    elif num==8 and t.index == 17:
                        ...
                    # "colors" of tiles on the chain that the tile connects to
                    bools = [chain[t2] for keys in t.connected_possible(num) for t2 in keys if t2 in chain.keys()]

                    # if they dont have the same color, there is a contradiction and t cant be that number
                    if not any(bools) or all(bools):
                        checked.append(t)
                        continue

                    logging.info(f"simple coloring offchain contradiction: {t.index} cant have {num}")
                    t.possibleValues.remove(num)
                    checked.append(t)
                    could_remove = True

        return could_remove

    def _twice_on_chain(self, chain:dict[Tile:bool], num) -> bool:
        for tile, onoff in chain.items():
            assert isinstance(tile, Tile)
            if any(t for grp in tile.connected_possible(num) for t in grp if t in chain.keys() and chain[t] == onoff):
                logging.info(
                    f"simple coloring same color on chain: {next(t.index for grp in tile.connected_possible(num) for t in grp if t in chain.keys() and chain[t] == onoff)}, {tile.index}")
                logging.info(
                    f"{[t2.index for t2, c in chain.items() if c==onoff]} cant be {num}")
                for t2, c in chain.items():
                    if c == onoff:
                        t2.possibleValues.remove(num)
                        
                return True
        return False

    def _check_contradiction(self, chain:dict[Tile:bool], num) -> bool:
        could_remove = False

        if self._twice_on_chain(chain, num):
            could_remove = True

        if self._offchain_contradiction(chain, num):
            could_remove = True

        return could_remove

    def _chain(self, chain:dict[Tile:bool], tile, num:int, onoff = True):
        if not isinstance(tile, Tile) or num not in tile.possibleValues or tile in chain.keys():
            return chain
        chain[tile] = onoff
        for connected in tile.connected_possible(num):
            if len(connected) != 1 or connected[0] in chain.keys():
                continue
            self._chain(chain, connected[0], num, not onoff)

        return chain

    def _get_chains(self, num:int) -> list[dict]:
        chains: list[dict] = []
        for tile in self.tiles:
            if num not in tile.possibleValues or any(tile in chain for chain in chains):
                continue
            chains.append(self._chain({}, tile, num))
            
        return sorted(chains, key = lambda x: len(x))

    def simple_coloring(self):
        could_remove = False
        for i in range(1, 10):
            for chain in self._get_chains(i):
                if len(chain) < 2:
                    continue
                elif self._check_contradiction(chain, i):
                    could_remove = True

        return could_remove


if __name__ == "__main__":
    gb = SudSolver()
    gb.game_loop()