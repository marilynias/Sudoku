import csv
import time
import os
# import sudoku
import queue
import logging
from timeit import default_timer as timer
from logging.handlers import QueueHandler, QueueListener
import argparse
from typing import List, Tuple


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

    with open(FILE) as f:
        reader = csv.reader(f)
        before = timer()

        # debug values
        time_added = num_skipped = num_solved = step_solved = time_step = num_current = 0

        for i, row in enumerate(reader):
            # ignore header row
            # or type(int(row[0])) != int:# or counter == 118:
            if i < START_AT:
                continue
            elif i == START_AT:
                logging.info("skipped to desired start")
                logging.info(f"it took {timer()-before}s")

            num_current = reader.line_num - START_AT

            # if any chars are not numbers
            if not all(c in "0123456789" for c in row[0]):
                print("row is not a sudoku:")
                print(row[0])
                continue

            # scheduled summary
            if reader.line_num % NUM_STEP == 0 and ENABLE_STEP_SUMMARY:
                logging.info(
                    f"Average stats for the last {NUM_STEP} Solutions:")
                logging.info(f"% soved: {round(step_solved/NUM_STEP*100, 4)}")
                logging.info(
                    f"Average time per Puzzle: {round((time_step)/(NUM_STEP)*1000, 3)}ms")
                logging.info("")
                time_step = 0
                step_solved = 0

            # end summary
            if reader.line_num >= NUM_LINES:
                logging.info("all Puzzles solved or skipped")
                logging.info(f"Soved: {round(num_solved/num_current*100, 2)}%")
                logging.info(f"Added time: {time_added}s")
                logging.info(f"Total time: {timer()-before}s")
                logging.info(
                    f"average time per Puzzle: {round((time_added/(NUM_LINES-START_AT))*1000, 3)} ms")
                logging.info(NUM_STEP)

                logging.info(f"Lines read: {num_current}")
                time.sleep(1)
                return

            if len(row) == 2:
                solution = row[1]
            else:
                solution = None
            o_sudoku = [row[0]]
            # splits the string into list of ints
            sudoku = [int(char) for char in row[0]]
            before_solve = timer()
            solve(sudoku)
            after_solve = timer()
            time_added += after_solve-before_solve
            time_step += after_solve-before_solve

            validate(sudoku)

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
            elif not solution:
                # logging.info(finalSud)
                num_solved += 1
                step_solved += 1
                continue
            elif finalSud == solution:
                # logging.info(finalSud)
                # logging.info("solved in: " + str(round(after_solve-before_solve,5)))
                num_solved += 1
                step_solved += 1
                continue
            else:
                logging.error("Sudoku "+str(reader.line_num)+" has a mistake")
                logging.info(finalSud)
                logging.info(row[1])
                num_skipped += 1
                continue


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


def validate(sudoku: List[int]) -> bool:
    print(sudoku)

    if 0 in sudoku:
        print("unsolved Tiles")
        return False
    else: return True
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
    parser.add_argument('-f', '--file', type=str, default="sudoku.csv",
                        help=".csv file with sudokus (format: [unsolved 0-9, solved 1-9]) defaults to sudoku.csv")
    parser.add_argument('-ss', '--step_summary', action='store_true')
    parser.add_argument('-sn', '--step_number', type=int, default=500,
                        help="sets the number of solved sudokus between summaries")
    parser.add_argument('-n', '--num_lines', type=int, default=2000,
                        help="how many lines the solver should read, useful for large csv files")
    parser.add_argument('-s', '--start', type=int, default=0,
                        help="from which line the solver should start")
    args = parser.parse_args()
    print(args)

    if not os.path.exists(args.file):
        print("file does not exist")
    elif not args.file.lower().endswith(".csv"):
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
        self._columns: List[List[int]] = [[] for i in range(9)]
        self._blocks: List[List[int]] = [[] for i in range(9)]
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

    def getBlockIndFromInd(self, ind: int):
        # 0 1 2
        # 3 4 5
        # 6 7 8
        return int(ind / 27) * 3 + (int(ind % 9 / 3))


if __name__ == "__main__":
    main()
