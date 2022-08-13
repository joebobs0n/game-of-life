#!/usr/bin/python3
import numpy as np
from pathlib import Path
from datetime import datetime
import argparse
import time
import os
import sys

LIVE = '█'
DEAD = ' '

def printBoard(board, generation, size, savedir=None):
    if savedir != None:
        msg = '\n'.join([''.join(line) for line in board])
        with open(f'{savedir}/gen{generation:06d}.txt', 'w') as f:
            f.write(msg)
    term_dims = size
    board_dims = {'x': len(board[0]), 'y': len(board)}
    X, Y = tuple(()), tuple(())
    if term_dims['x'] < board_dims['x']:
        diff = board_dims['x'] - term_dims['x']
        start = np.floor(diff/2)
        X = (int(start), int(start+term_dims['x']))
    else:
        X = (0, board_dims['x'])
    if term_dims['y'] < board_dims['y']:
        diff = board_dims['y'] - term_dims['y']
        start = np.floor(diff/2)
        Y = (int(start), int(start+term_dims['y']))
    else:
        Y = (0, board_dims['y'])
    msg_board = board[Y[0]:Y[1],X[0]:X[1]]
    msg = '\n'.join([''.join(line) for line in msg_board])
    print(msg)


def getLiving(subboard):
    subboard = subboard.tolist()
    subboard[1][1] = DEAD
    return sum([l.count(LIVE) for l in subboard])

def tick(board):
    height = len(board)
    width = len(board[0])
    working_board = np.array([[DEAD for _ in range(width+2)] for _ in range(height+2)])
    working_board[1:height+1,1:width+1] = board
    next_board = []
    for y in range(1, height+1):
        temp = []
        for x in range(1, width+1):
            subboard = working_board[y-1:y+2,x-1:x+2]
            n_living = getLiving(subboard)
            cell = subboard[1,1]
            if cell == LIVE and n_living != 2 and n_living != 3:
                temp.append(DEAD)
            elif cell == DEAD and n_living == 3:
                temp.append(LIVE)
            else:
                temp.append(cell)
        next_board.append(temp)
    return np.array(next_board)

def getNewBoard(X, Y):
    board = [[LIVE if np.random.randint(0, 5) >= 4 else DEAD for _ in range(X)] for _ in range(Y)]
    return np.array(board)

def loadBoard(path):
    success = True
    board = [[]]
    if Path(path).exists() and Path(path).suffix == '.board':
        with open(path, 'r') as f:
            board = f.read()
        board = [
            [
                DEAD if c == DEAD else LIVE for c in l
            ] for l in board.split('e\n') if l != ''
        ]
    else:
        success = False
    return np.array(board), success

def run(args, board, generations, size, gen_times):
    times = []
    tic = time.time()
    generations += 1
    board = tick(board)
    times.append(time.time() - tic)
    time.sleep(args.sleep)
    gen_times.append(times[-1])
    tic = time.time()
    printBoard(board, generations, size, savedir=args.output)
    times.append(time.time() - tic)
    msgs = [
        '\033[1m\033[92m'
        f'generation [{generations:6d}]'.center(int(np.floor(size['x'])/5), ' '),
        f'gen time [{times[0]:.03f}]'.center(int(np.floor(size['x'])/5), ' '),
        f'print time [{times[1]:.03f}]'.center(int(np.floor(size['x'])/5), ' '),
        f'frame time [{sum(times)+args.sleep:.03f}]'.center(int(np.floor(size['x'])/5), ' '),
        f'fps [{1/(sum(times)+args.sleep):.03f}]'.center(int(np.floor(size['x'])/5), ' '),
        '\033[0m'
    ]
    if 1/(sum(times)+args.sleep) > args.maxfps and args.maxfps != -1:
        args.sleep += 0.0001
    print(''.join(msgs).center(size['x']+12, ' '), end='', flush=True)

    return board, generations, gen_times

def getArgs(term_size):
    ap = argparse.ArgumentParser(
        formatter_class=argparse.MetavarTypeHelpFormatter
    )

    arguments = ap.add_argument_group('arguments')
    arguments.add_argument(
        '-x', '--width', type=int, default=term_size['x'],
        help='Width of simulation grid. If width exceeds terminal width, grid width is cropped for display. Default is terminal width.'
    )
    arguments.add_argument(
        '-y', '--height', type=int, default=term_size['y'],
        help='Height of simulation grid. If height exceeds terminal height, grid height is cropped for display. Default is terminal height minus one (for data).'
    )
    arguments.add_argument(
        '-g', '--generations', type=int, default=-1,
        help='Number of generations to simulate before exiting. Default is -1 (endless).'
    )
    arguments.add_argument(
        '-s', '--sleep', type=float, default=0,
        help='Additional sleep time per tick. Default is 0.'
    )
    arguments.add_argument(
        '-f', '--maxfps', type=float, default=-1,
        help='Max frames per second. Simulation will adjust incrementally to be under max fps rate. Default is -1 (uncapped).'
    )
    arguments.add_argument(
        '-o', '--output', default=None, type=Path,
        help='Output directory for export. Default is <width>x<height>-<date>.'
    )
    arguments.add_argument(
        '-l', '--load', default=None, type=Path,
        help='Load board file instead of generating random starting board.'
    )

    flags = ap.add_argument_group('flags')
    flags.add_argument('-e', '--export', action='store_true', default=False,
        help='Save each generation to file (in "output" directory). Default is false.')

    args = ap.parse_args()
    return args


def main():
    t_start = time.time()
    os.chdir(sys.path[0])
    print(f'\033[1m\033[92m-i-\033[0m Initializing Game of Life...', end='', flush=True)
    tic = time.time()
    term_size = os.get_terminal_size()
    term_size = {'x': term_size.columns, 'y': term_size.lines-1}
    args = getArgs(term_size)
    if args.output == None:
        now = datetime.now()
        nowstr = now.strftime('%d%b%y-%H.%M.%S')
        args.output = f'exports/{args.width}x{args.height}-{nowstr}'
    if not args.export:
        args.output = None
    if args.export and not Path(args.output).exists():
        os.system(f'mkdir -p {args.output}')
    success = True
    if args.load != None:
        board, success = loadBoard(args.load)
    if args.load == None or not success:
        board = getNewBoard(args.width, args.height)
    generations = 0
    toc = time.time()
    print(f'done ({toc-tic:.03f} seconds)')
    gen_times = []
    try:
        while(generations != args.generations):
            board, generations, gen_times = run(args, board, generations, term_size, gen_times)
    except KeyboardInterrupt:
        pass
    print('\n')
    total_time = time.time() - t_start
    seconds = total_time % 60
    minutes = np.floor(total_time / 60)
    hours = int(np.floor(minutes / 60))
    minutes = int(minutes % 60)
    print(f'\033[1m\033[92m-i-\033[0m total time for sim:      {hours}:{minutes:02d}:{seconds:.03f}')
    print(f'\033[1m\033[92m-i-\033[0m average generation time: {np.mean(gen_times):.03f} seconds')

if __name__ == '__main__':
    main()
