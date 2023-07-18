#!/usr/bin/env python3


import csv
import time
import os
import subprocess
# import sudoku
import queue
import logging
from timeit import default_timer as timer, timeit
from logging.handlers import QueueHandler, QueueListener
import argparse
import numpy as np
from typing import List, Tuple


# def smaller_csv():
#     FILE: str = "sudoku.csv"
#     file_new = "sudoku_smaller.csv"
#     # with open(file_new, "x") as f:
#     #     pass

#     with open(FILE) as f:
#         with open(file_new, "a+") as f2:
#             for i, line in enumerate(f):
#                 if i > 1000000:
#                     break
#                 if "0" in line:
#                     f2.write(line)

def main():
    global solution
    global o_sudoku
    global CONNECTED

    args = getArgs()

    log_queue = queue.Queue(-1)
    queue_handler = QueueHandler(log_queue)
    queue_handler.setLevel(logging.INFO)

    logger = logging.getLogger()
    logger.addHandler(queue_handler)
    logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(threadName)s: %(message)s')
    console_handler.setFormatter(formatter)
    # console_handler.setLevel(logging.WARNING)

    listener = QueueListener(log_queue, console_handler)
    listener.start()

    START_AT: int = args.start
    NUM_LINES: int = args.num_lines
    ENABLE_STEP_SUMMARY: bool = args.step_summary
    CONNECTED = SudokuGrid()
    FILE: str = args.file
    NUM_STEP: int = args.step_number
    # ruleset = sudoku.Rules()
    reader = getSudokus(NUM_LINES, FILE)
    

    # debug values
    time_added = num_skipped = num_solved = step_solved = time_step = num_current = 0

    before = timer()
    for num_current, row in enumerate(reader):
        o_sudoku, solution = row
        # ignore header row
        # or type(int(row[0])) != int:# or counter == 118:
        if num_current <= START_AT:
            continue
        elif num_current == START_AT and START_AT != 0:
            logging.info("skipped to desired start")
            logging.info(f"it took {timer()-before}s")


        

        # scheduled summary
        if num_current % NUM_STEP == 0 and ENABLE_STEP_SUMMARY:
            logging.info(
                f"Average stats for the last {NUM_STEP} Solutions:")
            logging.info(f"% solved: {round(step_solved/NUM_STEP*100, 4)}")
            logging.info(
                f"Average time per Puzzle: {round((time_step)/(NUM_STEP)*1000, 3)}ms")
            logging.info("")
            time_step = 0
            step_solved = 0

        # end summary
        if num_current+1 >= NUM_LINES:
            
            break

        # if not solution:
        #     solution = None
        # else:
        #     solution = None
        o_sudoku = o_sudoku
        # splits the string into list of ints
        sudoku = [int(char) for char in o_sudoku]
        before_solve = timer()
        solve(sudoku)
        after_solve = timer()
        time_added += after_solve-before_solve
        time_step += after_solve-before_solve

        # validate(sudoku)

        # for i, char in enumerate(row[0]):
        #     pass
        finalSud = listToString(sudoku)

        # error in soduku
        if "0" in finalSud:
            # logging.info("sudoku number "+str(reader.line_num)+" not solved")
            # logging.info(finalSud)
            # logging.info(row[1])
            num_skipped += 1
            continue
        
        elif finalSud == solution:
            # logging.info(finalSud)
            # logging.info("solved in: " + str(round(after_solve-before_solve,5)))
            num_solved += 1
            step_solved += 1
            continue
        elif not solution and validate(finalSud):
            # logging.info("no solution supplied")

            num_solved += 1
            step_solved += 1
            continue
        else:
            logging.error("Sudoku "+str((num_current+1))+" has a mistake")
            logging.info(finalSud)
            logging.info(solution)
            num_skipped += 1
            continue

    logging.info("all Puzzles solved or skipped")
    logging.info(
        f"Solved: {num_solved}/{(num_current+1)}:{round(num_solved/(num_current+1)*100, 2)}%")
    logging.info(f"Solving time: {time_added}s")
    logging.info(f"Total time: {timer()-before}s")
    logging.info(
        f"average time per Puzzle: {round((time_added/(NUM_LINES-START_AT))*1000, 3)} ms")
    logging.info(f"Lines read: {(num_current+1)}")
    time.sleep(1)

def getSudokus(num: int, csv_file):
    if not csv_file:
        gen_start = timer()
        csv_file = "tmp.csv"
        cmd = ["node", "qqwing-1.3.4/qqwing-main-1.3.4.min.js", "--generate",
               str(num), "--csv", "--solution", "--difficulty", "intermediate"]

        logging.info(f"generating {num} Sudokus ... this might take a while (~{round(num/7, 2)}s)")
        logging.info("if you feed me a csv with sudokus, you can skip this step")
        
        file = open(csv_file, "w")
        proc = subprocess.Popen(cmd, stdout=file,
                                stderr=subprocess.PIPE)
        # proc.stderr.readline()
        c = proc.communicate()
        return_code = proc.wait()
        logging.info(f"Done! It took {round(timer()-gen_start, 2)} seconds")
        if return_code:
            raise subprocess.CalledProcessError(return_code, cmd)
    reader = csv.DictReader(open(csv_file, "r"))
    headers = reader.fieldnames
    for row in reader:
        o_sudoku = row[headers[0]].replace(".", "0")
        solution = row.get(headers[1], None) if len(headers) >= 2 else None
        # if any chars are not numbers
        if not len(o_sudoku) == 81 and all(c in "0123456789" for c in o_sudoku):
            print("row is not a sudoku:")
            print(o_sudoku)
            continue

        yield (o_sudoku, solution)

def solve(sudoku: List[int]):
    possibleValues: List[List[int]] = [
        [i for i in range(1, 10)] if not int(char) else [] for char in sudoku]
    assignPossibleValues(sudoku, possibleValues)
    while 1:
        if not 0 in sudoku:
            break
        if soleCandidate(sudoku, possibleValues):
            continue
        elif hiddenSingles(sudoku, possibleValues):
            continue
        elif nakedSubset(sudoku, possibleValues):
            continue
        elif pointingSubset(sudoku, possibleValues):
            continue
        # elif boxLineReduction(sudoku, possibleValues ):
        #     continue
        else:
            break
    return sudoku


def validate(sudoku: List[int]) -> bool:
    # print(sudoku)

    if "0" in sudoku:
        print("unsolved Tiles:", sudoku)
        return False
    else:
        # print(sudoku)
        return True
    # else:
    #     for row in CONNECTED.rows:
    #         for tile in row:

    #     for col in CONNECTED.cols:


def assignPossibleValues(sudoku: List[int], possibleValues: List[List[int]]) -> bool:
    couldAssign = False
    # logging.info("Assigning Possible Values")
    for i_root in range(len(sudoku)):
        if sudoku[i_root] == 0:
            if possibleValues[i_root] == []:
                logging.warning(
                    "No possible numbers for this Tile!!, some number is wrong")
                return False

            t_connected = CONNECTED.getConnectedToInd(i_root)
            for subset in t_connected:
                for i_tile in subset:
                    if sudoku[i_tile] != 0 and sudoku[i_tile] in possibleValues[i_root]:
                        possibleValues[i_root].remove(sudoku[i_tile])
                        couldAssign = True
    return couldAssign


def soleCandidate(sudoku: List[int], possibleValues: List[List[int]]) -> bool:
    couldAssign = False
    for ind in range(len(sudoku)):
        if sudoku[ind] == 0:
            if len(possibleValues[ind]) == 1:
                couldAssign = assignValue(
                    sudoku, possibleValues, ind, possibleValues[ind][0])
    return couldAssign


def hiddenSingles(sudoku: List[int], possibleValues: List[List[int]]) -> bool:
    couldAssign = False
    for subset in CONNECTED.all:
        for ssub in subset:
            for num in range(1, 10):
                possTilesForVal = [
                    tile for tile in ssub if sudoku[tile] == 0 and num in possibleValues[tile]]
                if len(possTilesForVal) == 1:
                    couldAssign = assignValue(
                        sudoku, possibleValues, possTilesForVal[0], num)
    return couldAssign


def nakedSubset(sudoku: List[int], possibleValues: List[List[int]]) -> bool:
    couldRemove = False
    for subset in CONNECTED.all:
        for ssub in subset:
            for i, tile in enumerate(ssub):
                tilepos = possibleValues[tile]
                if sudoku[tile] == 0 and len(possibleValues[tile]) < 4:
                    lstSameVals = [t for t in ssub if t != tile and sudoku[t] == 0 and all(
                        j in possibleValues[tile] for j in possibleValues[t])]
                    lstSameVals.append(tile)
                    if len(lstSameVals) == len(possibleValues[tile]):
                        box = CONNECTED.getConnectedToInd(tile)[2]
                        check = (ssub, )
                        if all(t in box for t in lstSameVals):
                            check = (ssub, box)
                        for s in check:
                            for tileRemVal in s:
                                if tileRemVal in lstSameVals:
                                    continue
                                for val in possibleValues[tileRemVal]:
                                    if val in possibleValues[tile]:
                                        couldRemove = True
                                        possibleValues[tileRemVal].remove(val)

    return couldRemove


def pointingSubset(sudoku: List[int], possibleValues: List[List[int]]) -> bool:
    couldRemove = False
    for tile, c in enumerate(sudoku):
        for num in possibleValues[tile]:
            for subset in CONNECTED.getConnectedToInd(tile):
                numInTiles = [t for t in subset if num in possibleValues[t]]
                if len(numInTiles) > 1:
                    for sub in CONNECTED.getConnectedToInd(tile):
                        if subset == sub:
                            continue
                        if all(t in sub for t in numInTiles):

                            for t in sub:
                                if num in possibleValues[t] and not t in subset:
                                    couldRemove = True

                                    possibleValues[t].remove(num)
    return couldRemove


def boxLineReduction(sudoku: List[int], possibleValues: List[List[int]]) -> bool:  # WRONG
    couldRemove = False
    for sub in (CONNECTED.columns, CONNECTED.rows):
        for ssub in sub:
            for num in range(1, 10):
                possTilesForVal = [
                    tile for tile in ssub if sudoku[tile] == 0 and num in possibleValues[tile]]
                if len(possTilesForVal) > 1 and all(t in CONNECTED.getConnectedToInd(possTilesForVal[0])[2] for t in possTilesForVal):
                    for t in CONNECTED.getConnectedToInd(possTilesForVal[0])[2]:
                        if num in possibleValues[t]:
                            logging.info(f"removed {num}")
                            possibleValues[t].remove(num)
                            couldRemove = True

    return couldRemove


def assignValue(sudoku: List[int], possibleValues: List[List[int]], tileInd: int, num: int) -> bool:
    if sudoku[tileInd] != 0:
        logging.warn("The Tile you are trying to change is not empty")
        return False
    sudoku[tileInd] = num
    possibleValues[tileInd] = []
    for sub in CONNECTED.getConnectedToInd(tileInd):
        for tile in sub:
            if sudoku[tile] == 0 and num in possibleValues[tile]:
                possibleValues[tile].remove(num)
    return True


def checkForErrors(sudoku: List[List[int]], solution: str):
    for i, val in enumerate(sudoku):
        if val != 0:
            if val != solution[i]:
                logging.warning(
                    f"Wrong number at position: {i}, {val}!= {solution[i]}")
                return
    logging.info("clear")


def listToString(lst: List[int]) -> str:
    string = ""
    for item in lst:
        string += str(item)
    return string


def getArgs() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', type=str, default="",
                        help=".csv file with sudokus (format: [unsolved 0-9, solved 1-9]) defaults to sudoku.csv")
    parser.add_argument('-ss', '--step_summary', action='store_false')
    parser.add_argument('-sn', '--step_number', type=int, default=500,
                        help="sets the number of solved sudokus between summaries")
    parser.add_argument('-n', '--num_lines', type=int, default=100,
                        help="how many lines the solver should read, useful for large csv files")
    parser.add_argument('-s', '--start', type=int, default=0,
                        help="from which line the solver should start")
    args = parser.parse_args()
    print(args)

    if not os.path.exists(args.file) and args.file:
        print("file does not exist")
    elif not args.file.lower().endswith(".csv") and args.file:
        print("not a csv file")

    return args


class SudokuGrid():
    # 0  1  2 |3  4  5 |6  7  8
    # 9  10 11|12 13 14|15 16 17
    # 18 19 20|21 22 23|24 25 26
    # --------|--------|--------
    # 27 28 29|30 31 32|33 34 35
    # 36 37 38|39 40 41|42 43 44
    # 45 46 47|48 49 50|51 52 53
    # --------|--------|--------
    # 54 55 56|57 58 59|60 61 62
    # 63 64 65|66 67 68|69 70 71
    # 72 73 74|75 76 77|78 79 80

    def __init__(self) -> None:

        self._rows: List[List[int]] = [[] for i in range(9)]
        # array([[0,  1,  2,  3,  4,  5,  6,  7,  8],
        #        [9, 10, 11, 12, 13, 14, 15, 16, 17],
        #        [18, 19, 20, 21, 22, 23, 24, 25, 26],
        #        [27, 28, 29, 30, 31, 32, 33, 34, 35],
        #        [36, 37, 38, 39, 40, 41, 42, 43, 44],
        #        [45, 46, 47, 48, 49, 50, 51, 52, 53],
        #        [54, 55, 56, 57, 58, 59, 60, 61, 62],
        #        [63, 64, 65, 66, 67, 68, 69, 70, 71],
        #        [72, 73, 74, 75, 76, 77, 78, 79, 80]])

        self._columns: List[List[int]] = [[] for i in range(9)]
        # array([[0,  9, 18, 27, 36, 45, 54, 63, 72],
        #        [1, 10, 19, 28, 37, 46, 55, 64, 73],
        #        [2, 11, 20, 29, 38, 47, 56, 65, 74],
        #        [3, 12, 21, 30, 39, 48, 57, 66, 75],
        #        [4, 13, 22, 31, 40, 49, 58, 67, 76],
        #        [5, 14, 23, 32, 41, 50, 59, 68, 77],
        #        [6, 15, 24, 33, 42, 51, 60, 69, 78],
        #        [7, 16, 25, 34, 43, 52, 61, 70, 79],
        #        [8, 17, 26, 35, 44, 53, 62, 71, 80]])

        self._blocks: List[List[int]] = [[] for i in range(9)]
        # array([[0,  1,  2,  9, 10, 11, 18, 19, 20],
        #        [3,  4,  5, 12, 13, 14, 21, 22, 23],
        #        [6,  7,  8, 15, 16, 17, 24, 25, 26],
        #        [27, 28, 29, 36, 37, 38, 45, 46, 47],
        #        [30, 31, 32, 39, 40, 41, 48, 49, 50],
        #        [33, 34, 35, 42, 43, 44, 51, 52, 53],
        #        [54, 55, 56, 63, 64, 65, 72, 73, 74],
        #        [57, 58, 59, 66, 67, 68, 75, 76, 77],
        #        [60, 61, 62, 69, 70, 71, 78, 79, 80]])

        for i in range(81):
            self._rows[int(i/9)].append(i)
            self._columns[i % 9].append(i)
            self._blocks[self.getBlockIndFromInd(i)].append(i)

    @property
    def rows(self) -> List[List[int]]:
        return self._rows

    @property
    def columns(self) -> List[List[int]]:
        return self._columns

    @property
    def blocks(self) -> List[List[int]]:
        return self._blocks

    @property
    def all(self) -> Tuple[List[List[int]], List[List[int]], List[List[int]]]:
        return (self._rows, self._columns, self._blocks)

    def getConnectedToInd(self, index: int) -> Tuple[List[int], List[int], List[int]]:
        return self._rows[int(index/9)], self._columns[index % 9], self._blocks[self.getBlockIndFromInd(index)]

    def getConnectedFromSud(self, index: int, sudoku: List[int]):
        return self._rows[int(index/9)], self._columns[index % 9], self._blocks[self.getBlockIndFromInd(index)]

    def getBlockIndFromInd(self, ind: int):
        # 0 1 2
        # 3 4 5
        # 6 7 8
        return int(ind / 27) * 3 + (int(ind % 9 / 3))


class Sudoku():
    # 0  1  2 |3  4  5 |6  7  8
    # 9  10 11|12 13 14|15 16 17
    # 18 19 20|21 22 23|24 25 26
    # --------|--------|--------
    # 27 28 29|30 31 32|33 34 35
    # 36 37 38|39 40 41|42 43 44
    # 45 46 47|48 49 50|51 52 53
    # --------|--------|--------
    # 54 55 56|57 58 59|60 61 62
    # 63 64 65|66 67 68|69 70 71
    # 72 73 74|75 76 77|78 79 80

    # array([[0, 7, 0, 0, 0, 0, 0, 4, 3],
    #        [0, 4, 0, 0, 0, 9, 6, 1, 0],
    #        [8, 0, 0, 6, 3, 4, 9, 0, 0],
    #        [0, 9, 4, 0, 5, 2, 0, 0, 0],
    #        [3, 5, 8, 4, 6, 0, 0, 2, 0],
    #        [0, 0, 0, 8, 0, 0, 5, 3, 0],
    #        [0, 8, 0, 0, 7, 0, 0, 9, 1],
    #        [9, 0, 2, 1, 0, 0, 0, 0, 5],
    #        [0, 0, 7, 0, 4, 0, 8, 0, 2]])

    def __init__(self, sudoku: str) -> None:
        # following arrays keep the references. IE: a change to a number will change the same number in all arrays
        self.o_sudoku = np.array([int(c) for c in sudoku]).reshape(81)
        self.rows = self.o_sudoku.reshape(9, 9)
        self.columns = self.o_sudoku.reshape(9, 9).swapaxes(0, 1)

        # Blocks will not keep the references!
        self.blocks = self.o_sudoku.reshape(
            3, 3, 3, 3).swapaxes(1, 2).reshape(9, 9)

        # print("Original arrays:")
        # print(self.rows)
        # pass

    def doToColumns(self, func):
        columns = self.rows.swapaxes(0, 1)

        r = func(columns)

        self.rows = r.swapaxes(1, 0)

        return self.rows

    def doToBlocks(self, func):
        pass


if __name__ == "__main__":
    # smaller_csv()
   main()