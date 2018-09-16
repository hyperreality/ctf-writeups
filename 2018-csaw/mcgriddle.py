#!/usr/bin/env/python2

import base64
import chess

board = chess.Board()

with open('mcgriddle_moves') as f:
    moves = [line.strip() for line in f.readlines()]
with open('mcgriddle_base64') as f:
    b64s = [line.strip() for line in f.readlines()]

def decode_broken_base64(data):
    missing_padding = 4 - len(data) % 4
    if missing_padding:
        data += '=' * missing_padding
    try:
        return base64.b64decode(data)
    except:
        pass

def print_if(i, s):
    if s is None:
        return
    if len([c for c in s if ord(c) < 128]) * 11 / 10 > len(s):
        print i, repr(s[i:])


for i, move in enumerate(moves):
    board.push_san(move)

    if i % 2 == 0:
        selected_b64 = ""

        squares = str(board).replace(' ', '').replace('\n', '')
        for j, square in enumerate(squares):
            if square == '.':
                selected_b64 += b64s[i / 2][j]

        # print(selected_b64)
        print_if(0, decode_broken_base64(selected_b64))
        print_if(1, decode_broken_base64("A" + selected_b64 + "A=="))
        print_if(2, decode_broken_base64("AA" + selected_b64 + "=="))
        print_if(3, decode_broken_base64("AAA" + selected_b64 + "="))
