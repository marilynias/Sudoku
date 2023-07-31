#!/usr/bin/env python3


import argparse
import csv
import logging
import os
import queue
import subprocess
import time
from logging.handlers import QueueHandler, QueueListener
from timeit import default_timer as timer
import timeit
from typing import List, Tuple


def main():
    def _check_before_solve():
        if num_current <= start_at:
            return True
        if num_current == start_at and start_at != 0:
            logging.info("skipped to desired start")
            logging.info("it took %ds", timer() - before)

        # scheduled summary
        if num_current % num_step == 0 and enable_step_summary:
            logging.info("Average stats for the last %d Solutions:", num_step)
            logging.info("%% solved: %f", round(
                step_solved / num_step * 100, 4))
            logging.info("Average time per Puzzle: %fms",
                         round(time_step / num_step * 1000, 3))
            logging.info("")
            time_step = 0
            step_solved = 0
        return False


    global solution
    global o_sudoku
    global connected

    args = _get_args()

    log_queue = queue.Queue(-1)
    queue_handler = QueueHandler(log_queue)
    queue_handler.setLevel(logging.INFO)

    logger = logging.getLogger()
    logger.addHandler(queue_handler)
    logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    formatter = logging.Formatter("%(threadName)s: %(message)s")
    console_handler.setFormatter(formatter)

    listener = QueueListener(log_queue, console_handler)
    listener.start()

    start_at: int = args.start
    num_lines: int = args.num_lines
    enable_step_summary: bool = args.step_summary
    connected = SudokuGrid()
    FILE: str = args.file
    num_step: int = args.step_number
    reader = _get_sudokus(num_lines, FILE)

    # debug values
    time_added = _ = num_solved = step_solved = time_step = num_current = 0

    before = timer()
    for num_current, (o_sudoku, solution) in enumerate(reader):
        # o_sudoku, solution = row
        
        if _check_before_solve():
            continue

        # end summary
        if num_current + 1 >= num_lines:
            break

        o_sudoku = o_sudoku
        # splits the string into list of ints
        sudoku = [int(char) for char in o_sudoku]
        before_solve = timer()

        # t = timeit.Timer(lambda: solve(sudoku))

        # NUMRUNS = 10
        # solve_time = t.timeit(NUMRUNS)/NUMRUNS
        solve(sudoku)
        
        after_solve = timer()
        time_added += after_solve - before_solve
        time_step += after_solve - before

        finalSud = _list_to_string(sudoku)
        # error in soduku
        if validate(finalSud):
            num_solved += 1
            step_solved += 1
        # else:
        #     logging.error("Sudoku " + str(num_current + 1) + " has a mistake")
        #     logging.info(finalSud)
        #     logging.info(solution)
        #     1

        continue
    logging.info("all Puzzles solved or skipped")
    logging.info(
        "Solved: %d/%d: %f%%",
        num_solved,
        num_current + 1,
        round(num_solved / (num_current + 1) * 100, 2),
    )
    logging.info("Solving time: %fs", time_added)
    logging.info("Total time: %fs", timer() - before)
    logging.info(
        "average time per Puzzle: %f ms", round(time_added / (num_lines - start_at) * 1000, 3)
    )
    logging.info("Lines read: %d", num_current + 1)
    time.sleep(1)


    

def _get_sudokus(num: int, csv_file):
    if not csv_file:
        gen_start = timer()
        csv_file = "tmp.csv"
        cmd = [
            "node",
            "qqwing-1.3.4/qqwing-main-1.3.4.min.js",
            "--generate",
            str(num),
            "--csv",
            "--solution",
            "--difficulty",
            "intermediate",
        ]
        logging.info(
            "generating %d Sudokus ... this might take a while (~%ds)", num, round(num / 7, 2)
        )
        logging.info("if you feed me a csv with sudokus, you can skip this step")
        with open(csv_file, "w") as file:
            with subprocess.Popen(cmd, stdout=file, stderr=subprocess.PIPE) as proc:
                c = proc.communicate()
                return_code = proc.wait()
                logging.info("Done! It took %d seconds", round(timer() - gen_start, 2))
                if return_code:
                    raise subprocess.CalledProcessError(return_code, cmd)
    reader = csv.DictReader(open(csv_file, "r"))
    headers = reader.fieldnames
    for row in reader:
        o_sudoku = row[headers[0]].replace(".", "0")
        solution = row.get(headers[1], None) if len(headers) >= 2 else None
        if len(o_sudoku) != 81 and all((c in "0123456789" for c in o_sudoku)):
            print("row is not a sudoku:")
            print(o_sudoku)
            continue

        yield (o_sudoku, solution)


def _run_logic(possibleValues, sudoku) -> bool:
    if _sole_candidate(sudoku, possibleValues):
        return True
    elif _hidden_singles(sudoku, possibleValues):
        return True
    elif _naked_subset(sudoku, possibleValues):
        return True
    else: return _pointing_subset(sudoku, possibleValues)

def solve(sudoku: List[int]):
    possible_values: List[List[int]] = [
        list(range(1, 10)) if not int(char) else [] for char in sudoku
    ]
    _assign_possible_values(sudoku, possible_values)
    while 1:
        if 0 not in sudoku:
            return sudoku
        if _run_logic(possible_values, sudoku):
            continue

        # elif boxLineReduction(sudoku, possibleValues ):
        break
    return sudoku


def validate(sudoku: List[int]) -> bool:

    if "0" in sudoku:
        # print("unsolved Tiles:", sudoku)
        return False
    elif any(val in connected.get_connected_values_from_sud(i, sudoku) for i, val in enumerate(sudoku)):
        logging.error("Mistake in the solution, same value twice in row/col/box:")
        logging.error(sudoku)
        return False
    else:
        return True
    # else:
    #     for row in connected.rows:
    #         for tile in row:

    #     for col in connected.cols:


def _assign_possible_values(sudoku: List[int], possibleValues: List[List[int]]) -> bool:
    could_assign = False
    for i_root in range(len(sudoku)):
        if sudoku[i_root] != 0:
            continue
        if possibleValues[i_root] == []:
            logging.warning("No possible numbers for this Tile!!, some number is wrong")
            return False

        # t_connected = connected.get_connected_to_ind(i_root)
        for i_tile in connected.get_connected_set_to_ind(i_root):
            if sudoku[i_tile] != 0 and sudoku[i_tile] in possibleValues[i_root]:
                possibleValues[i_root].remove(sudoku[i_tile])
                could_assign = True
    return could_assign


def _sole_candidate(sudoku: List[int], possibleValues: List[List[int]]) -> bool:
    could_assign = False
    for ind in range(len(sudoku)):
        if sudoku[ind] == 0:
            if len(possibleValues[ind]) == 1:
                could_assign = _assign_value(sudoku, possibleValues, ind, possibleValues[ind][0])
    return could_assign


def _hidden_singles(sudoku: List[int], possibleValues: List[List[int]]) -> bool:
    could_assign = False
    for subset in connected.all:
        for ssub in subset:
            for num in range(1, 10):
                possTilesForVal = [
                    tile for tile in ssub if sudoku[tile] == 0 and num in possibleValues[tile]
                ]
                if len(possTilesForVal) == 1:
                    could_assign = _assign_value(sudoku, possibleValues, possTilesForVal[0], num)
    return could_assign


def _naked_subset(sudoku: List[int], possibleValues: List[List[int]]) -> bool:
    could_remove = False
    for subset in connected.all:
        for ssub in subset:
            for i, tile in enumerate(ssub):
                if sudoku[tile] != 0 or len(possibleValues[tile]) >= 4:
                    continue
                lstSameVals = [
                    *[
                        t
                        for t in ssub
                        if t != tile
                        and sudoku[t] == 0
                        and all((j in possibleValues[tile] for j in possibleValues[t]))
                    ],
                    tile,
                ]
                if len(lstSameVals) != len(possibleValues[tile]):
                    continue
                box = connected.get_connected_to_ind(tile)[2]
                check = (ssub,)
                if all((t in box for t in lstSameVals)):
                    check = (ssub, box)
                for s in check:
                    for tileRemVal in s:
                        if tileRemVal in lstSameVals:
                            continue
                        for val in possibleValues[tileRemVal]:
                            if val in possibleValues[tile]:
                                could_remove = True
                                possibleValues[tileRemVal].remove(val)

    return could_remove


def _pointing_subset(sudoku: List[int], possibleValues: List[List[int]]) -> bool:
    could_remove = False
    for tile, c in enumerate(sudoku):
        for num in possibleValues[tile]:
            for subset in connected.get_connected_to_ind(tile):
                numInTiles = [t for t in subset if num in possibleValues[t]]
                if len(numInTiles) > 1:
                    for sub in connected.get_connected_to_ind(tile):
                        if subset == sub:
                            continue
                        if all((t in sub for t in numInTiles)):

                            for t in sub:
                                if num in possibleValues[t] and t not in subset:
                                    could_remove = True

                                    possibleValues[t].remove(num)
    return could_remove


def _box_line_reduction(sudoku: List[int], possibleValues: List[List[int]]) -> bool:
    could_remove = False
    for sub in (connected.columns, connected.rows):
        for ssub in sub:
            for num in range(1, 10):
                possTilesForVal = [
                    tile for tile in ssub if sudoku[tile] == 0 and num in possibleValues[tile]
                ]
                if len(possTilesForVal) > 1 and all((
                    t in connected.get_connected_to_ind(possTilesForVal[0])[2]
                    for t in possTilesForVal
                )):
                    for t in connected.get_connected_to_ind(possTilesForVal[0])[2]:
                        if num in possibleValues[t]:
                            logging.info("removed %d", num)
                            possibleValues[t].remove(num)
                            could_remove = True

    return could_remove


def _assign_value(
    sudoku: List[int], possibleValues: List[List[int]], tileInd: int, num: int
) -> bool:
    if sudoku[tileInd] != 0:
        logging.warn("The Tile you are trying to change is not empty")
        return False
    sudoku[tileInd] = num
    possibleValues[tileInd] = []
    for i_tile in connected.get_connected_set_to_ind(tileInd):
        if sudoku[i_tile] == 0 and num in possibleValues[i_tile]:
            possibleValues[i_tile].remove(num)
    return True


def _check_for_errors(sudoku: List[List[int]], solution: str):
    for i, val in enumerate(sudoku):
        if val != 0:
            if val != solution[i]:
                logging.warning("Wrong number at position: %d, %s!= %s", i, val, solution[i])
                return
    logging.info("clear")


def _list_to_string(lst: List[int]) -> str:
    return "".join([str(i) for i in lst])


def _get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f",
        "--file",
        type=str,
        default="",
        help=".csv file with sudokus (format: [unsolved 0-9, solved 1-9]) defaults to sudoku.csv",
    )
    parser.add_argument("-ss", "--step_summary", action="store_false")
    parser.add_argument(
        "-sn",
        "--step_number",
        type=int,
        default=500,
        help="sets the number of solved sudokus between summaries",
    )
    parser.add_argument(
        "-n",
        "--num_lines",
        type=int,
        default=100,
        help="how many lines the solver should read, useful for large csv files",
    )
    parser.add_argument(
        "-s", "--start", type=int, default=0, help="from which line the solver should start"
    )
    args = parser.parse_args()
    print(args)

    if not os.path.exists(args.file) and args.file:
        print("file does not exist")
    elif not args.file.lower().endswith(".csv") and args.file:
        print("not a csv file")

    return args


class SudokuGrid:
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

        self._rows = [[] for i in range(9)]

        self._columns= [[] for i in range(9)]

        self._blocks = [[] for i in range(9)]

        for i in range(81):
            self._rows[int(i / 9)].append(i)
            self._columns[i % 9].append(i)
            self._blocks[self.get_block_ind_from_ind(i)].append(i)

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

    def get_connected_to_ind(self, index: int) -> Tuple[List[int], List[int], List[int]]:
        return (
            self._rows[int(index / 9)],
            self._columns[index % 9],
            self._blocks[self.get_block_ind_from_ind(index)],
        )
    
    def get_connected_set_to_ind(self, index: int) -> set[int]:
        return {
            *self._rows[int(index / 9)],
            *self._columns[index % 9],
            *self._blocks[self.get_block_ind_from_ind(index)],
        }-{index}

    def get_connected_values_from_sud(self, index: int, sudoku: List[int]):
        for i in self.get_connected_set_to_ind(index):
            yield sudoku[i] 

    @staticmethod
    def get_block_ind_from_ind(ind: int):
        return int(ind / 27) * 3 + int(ind % 9 / 3)


# class Sudoku:
#     # 0  1  2 |3  4  5 |6  7  8
#     # 9  10 11|12 13 14|15 16 17
#     # 18 19 20|21 22 23|24 25 26
#     # --------|--------|--------
#     # 27 28 29|30 31 32|33 34 35
#     # 36 37 38|39 40 41|42 43 44
#     # 45 46 47|48 49 50|51 52 53
#     # --------|--------|--------
#     # 54 55 56|57 58 59|60 61 62
#     # 63 64 65|66 67 68|69 70 71
#     # 72 73 74|75 76 77|78 79 80

#     def __init__(self, sudoku: str) -> None:
#         # following arrays keep the references. IE: a change to a number will change the same number in all arrays
#         self.o_sudoku = np.array([int(c) for c in sudoku]).reshape(81)
#         self.rows = self.o_sudoku.reshape(9, 9)
#         self.columns = self.o_sudoku.reshape(9, 9).swapaxes(0, 1)

#         # Blocks will not keep the references!
#         self.blocks = self.o_sudoku.reshape(3, 3, 3, 3).swapaxes(1, 2).reshape(9, 9)

#     def do_to_columns(self, func):
#         columns = self.rows.swapaxes(0, 1)

#         r = func(columns)

#         self.rows = r.swapaxes(1, 0)

#         return self.rows

#     @staticmethod
#     def do_to_blocks(func):
#         pass


if __name__ == "__main__":
    main()