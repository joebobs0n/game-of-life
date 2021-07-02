#!/usr/bin/python3
import numpy as np
from pathlib import Path
import argparse
import time
import os
import sys

LIVE = '█'
DEAD = ' '

def printBoard(board, generation, size, save=False):
    if save:
        msg = '\n'.join([''.join(line) for line in board])
        with open(f'output/gen{generation:06d}.txt', 'w') as f:
            f.write(msg)
    else:
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

def run(args, board, generations, size, gen_times):
    times = []
    tic = time.time()
    generations += 1
    board = tick(board)
    times.append(time.time() - tic)
    time.sleep(args.sleep)
    gen_times.append(times[-1])
    if args.export == False:
        os.system('clear')
    tic = time.time()
    printBoard(board, generations, size, save=args.export)
    times.append(time.time() - tic)
    msgs = [
        f'\033[1m\033[92mgeneration [{generations:6d}]\033[0m'.center(int(np.floor(size['x'])/5)+13, ' '),
        f'\033[1m\033[92mgen time [{times[0]:.03f}]\033[0m'.center(int(np.floor(size['x'])/5)+13, ' '),
        f'\033[1m\033[92mprint time [{times[1]:.03f}]\033[0m'.center(int(np.floor(size['x'])/5)+13, ' '),
        f'\033[1m\033[92mframe time [{sum(times)+args.sleep:.03f}]\033[0m'.center(int(np.floor(size['x'])/5)+13, ' '),
        f'\033[1m\033[92mfps [{1/(sum(times)+args.sleep):.03f}]\033[0m'.center(int(np.floor(size['x'])/5)+13, ' ')
    ]
    if 1/(sum(times)+args.sleep) > 59:
        args.sleep += 0.0001
    if args.export == True:
        print(''.join(msgs))
    else:
        print(''.join(msgs), end='', flush=True)

    return board, generations, gen_times


def main():
    os.chdir(sys.path[0])
    term_size = os.get_terminal_size()
    term_size = {'x': term_size.columns, 'y': term_size.lines-1}

    ap = argparse.ArgumentParser()
    ap.add_argument('-x', '--width', type=int, default=term_size['x'])
    ap.add_argument('-y', '--height', type=int, default=term_size['y'])
    ap.add_argument('-g', '--generations', type=int, default=-1)
    ap.add_argument('-e', '--export', action='store_true', default=False)
    ap.add_argument('-s', '--sleep', type=float, default=0)
    args = ap.parse_args()

    print(f'\033[1m\033[92m-i-\033[0m Initializing Game of Life...', end='', flush=True)
    tic = time.time()
    if args.export and not Path('output').exists():
        os.mkdir('output')
    board = getNewBoard(args.width, args.height)
    generations = 0
    toc = time.time()
    print(f'done ({toc-tic:.03f} seconds)')
    printBoard(board, generations, term_size, save=args.export)

    gen_times = []
    try:
        if args.generations == -1:
            while(1):
                board, generations, gen_times = run(args, board, generations, term_size, gen_times)
        else:
            for _ in range(args.generations):
                board, generations, gen_times = run(args, board, generations, term_size, gen_times)
    except KeyboardInterrupt:
        pass

    print()
    print(f'\033[1m\033[92m-i-\033[0m total time for sim:      {np.sum(gen_times):.03f} seconds')
    print(f'\033[1m\033[92m-i-\033[0m average generation time: {np.mean(gen_times):.03f} seconds')

if __name__ == '__main__':
    main()
