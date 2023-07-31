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

class Sudoku(list):
    ...

class Solver():
    def __init__(self) -> None:
        args = _get_args()

        log_queue = queue.Queue(-1)
        queue_handler = QueueHandler(log_queue)
        queue_handler.setLevel(logging.INFO)

        self.logger = logging.getLogger()
        self.logger.addHandler(queue_handler)
        self.logger.setLevel(logging.INFO)

        console_handler = logging.StreamHandler()
        formatter = logging.Formatter("%(threadName)s: %(message)s")
        console_handler.setFormatter(formatter)

        listener = QueueListener(log_queue, console_handler)
        listener.start()

        self.start_at: int = args.start
        self.num_lines: int = args.num_lines
        self.enable_step_summary = args.step_summary
        # self.connected = Sudoku(sudoku)
        FILE: str = args.file
        self.num_step: int = args.step_number
        self.reader = self._get_sudokus(self.num_lines, FILE)

        # debug values
        self.time_added = self.num_solved = self.step_solved = self.time_step = self.num_current = 0
        
        logging.info("generating sudokus")
        before_gen = timer()
        self.sud_lst = [Sudoku_solver([int(char) for char in o_sudoku]) for (o_sudoku, solution) in self.reader]
        logging.info("end generating sudokus in :%f seconds", timer()-before_gen)
        logging.info("number of sudokus: "+str(len(self.sud_lst)))

    def main_loop(self):
        before = timer()
        for self.num_current, sud in enumerate(self.sud_lst):

            before_solve = timer()
            sud.solve()
            after_solve = timer()

            self.time_added += after_solve - before_solve
            self.time_step += after_solve - before

            # finalSud = sud.sudoku
            # error in soduku
            if sud.validate():
                self.num_solved += 1
                self.step_solved += 1
            # else:
            #     logging.error("Sudoku " + str(num_current + 1) + " has a mistake")
            #     logging.info(finalSud)
            #     logging.info(solution)
            #     1

            continue
        self._log_after_solve(before)

    def test(self):
        o_sudoku = "000000027040800000000000001000400900600000500001000000000012050080000300300070000"
        sud = Sudoku([int(char) for char in o_sudoku])
        t = timeit.Timer(lambda: sud.solve())
        # sud.solve()
        # print(t)
        

        NUMRUNS = 1000
        solve_time = t.timeit(NUMRUNS)/NUMRUNS
        logging.info("solvetime: " + str(solve_time*1000)+"ms")
        print("success" if sud.validate() else "Failed: "+str(sud.sudoku))

    def _check_before_solve(self):
        if self.num_current <= self.start_at:
            return True
        if self.num_current == self.start_at and self.start_at != 0:
            logging.info("skipped to desired start")
            logging.info("it took %ds", timer() - self.before)

        # scheduled summary
        if self.num_current % self.num_step == 0 and self.enable_step_summary:
            logging.info(
                "Average stats for the last %d Solutions:", self.num_step)
            logging.info("%% solved: %f", round(
                step_solved / self.num_step * 100, 4))
            logging.info("Average time per Puzzle: %fms",
                         round(time_step / self.num_step * 1000, 3))
            logging.info("")
            time_step = 0
            step_solved = 0
        return False
    
    def _log_after_solve(self, before):
        logging.info("all Puzzles solved or skipped")
        logging.info(
            "Solved: %d/%d: %f%%",
            self.num_solved,
            self.num_current + 1,
            round(self.num_solved / (self.num_current + 1) * 100, 2),
        )
        logging.info("Solving time: %fs", self.time_added)
        logging.info("Total time: %fs", timer() - before)
        logging.info(
            "average time per Puzzle: %f ms", round(
                self.time_added / (self.num_lines - self.start_at) * 1000, 3)
        )
        logging.info("Lines read: %d", self.num_current + 1)
        time.sleep(1)
    
    def _get_sudokus(self, num: int, csv_file):
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
                "generating %d Sudokus ... this might take a while (~%ds on an old Desktop)", num, round(num / 7, 2)
            )
            logging.info("if you feed me a csv with sudokus, you can skip this step")
            with open(csv_file, "w") as file:
                with subprocess.Popen(cmd, stdout=file, stderr=subprocess.PIPE) as proc:
                    c = proc.communicate()
                    return_code = proc.wait()
                    logging.info("Done! It took %f seconds", round(timer() - gen_start, 2))
                    if return_code:
                        raise subprocess.CalledProcessError(return_code, cmd)
        reader = open(csv_file, "r")
        # headers = reader.fieldnames
        i = 0
        for row in reader:
            if i+1 > num:
                return []
            
            o_sudoku = None
            solution = None
            for item in row.strip("\n\t").replace(".", "0").split(","):
                if "0" in item and self._check_valid_sudoku(item):
                    o_sudoku = item
                elif self._check_valid_sudoku(item):
                    solution = item
            if not o_sudoku:
                logging.info("row is not a sudoku:")
                logging.info(o_sudoku)
                continue
            else:
                i+=1
                yield (o_sudoku, solution)
        logging.error(IndexError("not enough sudokus in the file: "+str(i)))

    def _check_valid_sudoku(self, o_sudoku):
        return len(o_sudoku) == 81 and all((c in "0123456789" for c in o_sudoku))


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
    logging.info(args)

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

    _rows = [[] for i in range(9)]

    _columns = [[] for i in range(9)]

    _blocks = [[] for i in range(9)]

    for i in range(81):
        _rows[int(i / 9)].append(i)
        _columns[i % 9].append(i)
        _blocks[int(i / 27) * 3 + int(i % 9 / 3)].append(i)

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


class Sudoku_solver(SudokuGrid):
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

    def __init__(self, sudoku) -> None:
        self.o_sudoku = sudoku
        # self.sudoku = self.o_sudoku.copy()
    
    def _run_logic(self, possibleValues, sudoku) -> bool:
        if self._sole_candidate(sudoku, possibleValues):
            return True
        elif self._hidden_singles(sudoku, possibleValues):
            return True
        elif self._naked_subset(sudoku, possibleValues):
            return True
        else:
            return self._pointing_subset(sudoku, possibleValues)

    def _assign_possible_values(self, sudoku: List[int], possibleValues: List[List[int]]) -> bool:
        could_assign = False
        for i_root in range(len(sudoku)):
            if sudoku[i_root] != 0:
                continue
            if possibleValues[i_root] == []:
                logging.warning(
                    "No possible numbers for this Tile!!, some number is wrong")
                return False

            # t_connected = get_connected_to_ind(i_root)
            for i_tile in self.get_connected_set_to_ind(i_root):
                if sudoku[i_tile] != 0 and sudoku[i_tile] in possibleValues[i_root]:
                    possibleValues[i_root].remove(sudoku[i_tile])
                    could_assign = True
        return could_assign

    def _sole_candidate(self, sudoku: List[int], possibleValues: List[List[int]]) -> bool:
        could_assign = False
        for ind in range(len(sudoku)):
            if sudoku[ind] == 0:
                if len(possibleValues[ind]) == 1:
                    could_assign = self._assign_value(
                        sudoku, possibleValues, ind, possibleValues[ind][0])
        return could_assign

    def _hidden_singles(self, sudoku: List[int], possibleValues: List[List[int]]) -> bool:
        could_assign = False
        for subset in self.all:
            for ssub in subset:
                for num in range(1, 10):
                    possTilesForVal = [
                        tile for tile in ssub if sudoku[tile] == 0 and num in possibleValues[tile]
                    ]
                    if len(possTilesForVal) == 1:
                        could_assign = self._assign_value(
                            sudoku, possibleValues, possTilesForVal[0], num)
        return could_assign


    def _naked_subset(self, sudoku: List[int], possibleValues: List[List[int]]) -> bool:
        could_remove = False
        for subset in self.all:
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
                    box = self.get_connected_to_ind(tile)[2]
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


    def _pointing_subset(self, sudoku: List[int], possibleValues: List[List[int]]) -> bool:
        could_remove = False
        for tile, c in enumerate(sudoku):
            for num in possibleValues[tile]:
                for subset in self.get_connected_to_ind(tile):
                    numInTiles = [t for t in subset if num in possibleValues[t]]
                    if len(numInTiles) > 1:
                        for sub in self.get_connected_to_ind(tile):
                            if subset == sub:
                                continue
                            if all((t in sub for t in numInTiles)):

                                for t in sub:
                                    if num in possibleValues[t] and t not in subset:
                                        could_remove = True

                                        possibleValues[t].remove(num)
        return could_remove


    def _box_line_reduction(self, sudoku: List[int], possibleValues: List[List[int]]) -> bool:
        could_remove = False
        for sub in (self.columns, self.rows):
            for ssub in sub:
                for num in range(1, 10):
                    possTilesForVal = [
                        tile for tile in ssub if sudoku[tile] == 0 and num in possibleValues[tile]
                    ]
                    if len(possTilesForVal) > 1 and all((
                        t in self.get_connected_to_ind(possTilesForVal[0])[2]
                        for t in possTilesForVal
                    )):
                        for t in self.get_connected_to_ind(possTilesForVal[0])[2]:
                            if num in possibleValues[t]:
                                logging.info("removed %d", num)
                                possibleValues[t].remove(num)
                                could_remove = True

        return could_remove


    def _assign_value(
            self,
            sudoku: List[int],
            possibleValues: List[List[int]],
            tileInd: int, 
            num: int
            ) -> bool:
        if sudoku[tileInd] != 0:
            logging.warn("The Tile you are trying to change is not empty")
            return False
        sudoku[tileInd] = num
        possibleValues[tileInd] = []
        for i_tile in self.get_connected_set_to_ind(tileInd):
            if sudoku[i_tile] == 0 and num in possibleValues[i_tile]:
                possibleValues[i_tile].remove(num)
        return True
    
    def _list_to_string(self, lst: List[int]) -> str:
        return "".join([str(i) for i in lst])


    def validate(self, solution=None) -> bool:
        sudoku = self._list_to_string(self.sudoku)
        if not hasattr(self, "sudoku"):
            logging.error("cannot validate; solve() was never run")
            return False

        if "0" in sudoku:
            # print("unsolved Tiles:", sudoku)
            return False
        # check if all numbers are unique in its row/column/box
        elif solution and sudoku != solution:
            logging.error(
                "Mistake in the solution, not matching provided solution:")
            logging.error(sudoku)
            return False
        elif any(val in self.get_connected_values_from_sud(i, sudoku) for i, val in enumerate(sudoku)):
            logging.error(
                "Mistake in the solution, same value twice in row/col/box:")
            logging.error(sudoku)
            return False
        else:
            return True


    def solve(self):
        self.sudoku = self.o_sudoku.copy()
        possible_values: List[List[int]] = [
            list(range(1, 10)) if not int(char) else [] for char in self.sudoku
            ]
        self._assign_possible_values(self.sudoku, possible_values)
        while 1:
            if 0 not in self.sudoku:
                return self.sudoku
            if self._run_logic(possible_values, self.sudoku):
                continue

            # elif boxLineReduction(self.sudoku, possibleValues ):
            break
        return self.sudoku


if __name__ == "__main__":
    Solver().main_loop()