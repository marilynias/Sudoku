from sudoku import GameBoard, solveBttn, tiles, rules
from solve_all import solve, _get_sudokus, num_used, validate
from sudoku_solver import Sudoku_solver

from timeit import default_timer as timer
import logging
from logging.handlers import QueueHandler, QueueListener
import queue, pygame, math

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

# bttn = SolveButton(0,0,"","arial")
# _sud_log = {"times":[], "accuracy":[]}

db = {
                "sudoku.py": {"times":[], "accuracy":[], "final":[]}, 
                "solve_all.py":{"times":[], "accuracy":[], "final":[]}, 
                "sudoku_solver.py": {"times":[], "accuracy":[], "final":[]},
                "times": {"init": []}}


def to_int(st:str):
    return [int(s) for s in st]

def to_str(ls:list):
    return "".join([str(i) for i in ls])
    

def solver2():
    return solveBttn.select(True)
    # return tiles







for sud, sol in _get_sudokus(100, difficulty="expert"):
    #init
    time_pre_init = timer()
    logger.info("")
    logger.info("init")
    c1 = Sudoku_solver(sud)
    c2 = GameBoard(10, sud, sol)
    solver1 = c1.solve              # sudoku_solver.py
    # solver2 = SolveButton.select                                  # sudoku.py
    solver3 = solve                       # solve_all.py
    time_start = timer()
    db["times"]["init"].append(time_start - time_pre_init)
    s = to_int(solver1())
    time_s1 = timer()
    if s.count(0):
        to_int(solver1())
    elif not validate(s):
        raise ValueError("Mistake in sudoku:" + to_str(s))
    db["sudoku_solver.py"]["accuracy"].append(100- 100* (s.count(0)/81))
    db["sudoku_solver.py"]["times"].append(time_s1-time_start)
    db["sudoku_solver.py"]["final"].append(to_str(s))

    time_start = timer()
    s = [int(t.value) for t in solver2()]
    time_s2 = timer()
    if s.count(0):
        solver2()
    elif not validate(s):
        raise ValueError("Mistake in sudoku:" + to_str(s))
    db["sudoku.py"]["accuracy"].append(100- 100* (s.count(0)/81))
    db["sudoku.py"]["times"].append(time_s2-time_start)
    db["sudoku.py"]["final"].append(to_str(s))

    time_start = timer()
    s = solver3(to_int(sud))
    time_s3 = timer()
    if s.count(0):
        solver3(to_int(sud))
    elif not validate(s):
        raise ValueError("Mistake in sudoku:" + to_str(s))
    db["solve_all.py"]["accuracy"].append(100- 100* (s.count(0)/len(s)))
    db["solve_all.py"]["times"].append(time_s3-time_start)
    db["solve_all.py"]["final"].append(to_str(s))

for key, value in db.items():
    if key == "times":
        continue
    logging.info(key)
    logging.info(f"avg times:  {sum(value['times']) /  len(value['times'])}" )
    logging.info(f"avg acc:    {sum(value['accuracy'])/len(value['accuracy'])}" )
    logging.info(f"solve %: {((len(value['final']) - sum(1 for l in value['final'] if '0' in l))/len(value['final']))*100 }% ")
    logging.info("")

logging.info("avg init time: " + str(sum( db["times"]["init"])/len( db["times"]["init"])))

logging.info("solve_all used:")
logging.info(num_used)

logging.info("sudoku used:")
logging.info(rules.numUsed)
...