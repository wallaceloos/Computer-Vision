import chess
import chess.svg
from openai import OpenAI
import os
import re

client = OpenAI()

#models
#gpt-4
#gpt-4o
#gpt-3.5-turbo
VERBOSE = 0
player_name1 = "gpt-4o"
player_name2 = "gpt-4o"


def player_GPT(player_name, chessboard):

    maxTriesIter = 60
    fen = chessboard.fen()

    #prompt 1
    prompt = "Given this FEN notation: " + fen + ", give me the best move only in the UCI format. The answer needs to be between ** **. Note, a valid UCI  notation contains a sequence of 4 characters: letter, digit, letter, and digit. However, the notation changes to 5 characters when a piece is promoted. The number ranges from 1 to 8, and the letters can be from 'a' to 'h'."
    completion = client.chat.completions.create(
    model=player_name,
        messages=[
            {"role": "system", "content": "Chess player."},
            {"role": "user", "content": prompt}
        ]
    )
    ans = completion.choices[0].message.content

    pattern = r'\*\*(.*?)\*\*'

    # Find the match
    match = re.search(pattern, ans)
    if match:
        ans_move = match.group(1)
    else:
        ans_move = "none"


    if VERBOSE:
        print("EXPLANATION:", ans)
        print("ANSWER:", ans_move)
    
    i = 0
    list_moves_tried = [ans_move]
    list_legal_moves = [str(elem)  for elem in chessboard.legal_moves]
    status = ans_move in list_legal_moves

    while(not status and i < maxTriesIter):
        #prompt 2
        #prompt = "This move is invalid:"+ ans_move +". These are the possible moves: "+ str(list_legal_moves) +". Given this FEN notation: " + fen + ", give me the best move only in the UCI format. The answer needs to be between ** **. Note, a valid UCI  notation contains a sequence of 4 characters: letter, digit, letter, and digit. However, the notation changes to 5 characters when a piece is promoted. The number ranges from 1 to 8, and the letters can be from 'a' to 'h'."
        #prompt 3
        prompt = "This move is invalid:"+ ans_move + ". Given this FEN notation: " + fen + ", give me the best move only in the UCI format. The answer needs to be between ** **. Note, a valid UCI  notation contains a sequence of 4 characters: letter, digit, letter, and digit. However, the notation changes to 5 characters when a piece is promoted. The number ranges from 1 to 8, and the letters can be from 'a' to 'h'."
        completion = client.chat.completions.create(
            model=player_name,
            messages=[
            {"role": "system", "content": "Chess player."},
            {"role": "user", "content": prompt}
            ]
        )
        ans = completion.choices[0].message.content

        match = re.search(pattern, ans)
        if match:
            ans_move = match.group(1)
        else:
            ans_move = "none"
        
        status = ans_move in list_legal_moves

        if VERBOSE:
            print("EXPLANATION:", ans)
            print("ANSWER:", ans_move)
            print("POSIBLE MOVES", list_legal_moves)
        
        list_moves_tried.append(ans_move)


        i += 1

    if status == False:
        ans_move = "INVALID"

    return ans_move

    
def game_on():

    maxMoves = 200
    turn_p1 = 1

    chessboard = chess.Board()
    boardsvg = chess.svg.board(board = chessboard)
    outputfile = open("/save_images/move_0.svg", "w")
    outputfile.write(boardsvg)
    outputfile.close()

    i = 0
    while(i < maxMoves):

        if turn_p1:
            move = player_GPT(player_name1, chessboard)
            if move == "INVALID":
                print("Player 1 did not find a valid move!")
                return
            m = chess.Move.from_uci(move)
            chessboard.push(m) 

            print("Player 1:", move)

        else:
            move = player_GPT(player_name2, chessboard)
            if move == "INVALID":
                print("Player 2 did not find a valid move!")
                return
            m = chess.Move.from_uci(move)
            chessboard.push(m) 

            print("Player 2:", move)

        #save image
        boardsvg = chess.svg.board(board = chessboard)
        outputfile = open("/save_images/move_"+str(i+1)+".svg", "w")
        outputfile.write(boardsvg)
        outputfile.close()

        if chessboard.is_checkmate(): #checkmate
            print("Checkmate!")
            chessboard.outcome()
            return
        
        if chessboard.is_stalemate():
            print("Stalemates")
            return
        
        if chessboard.is_insufficient_material():
            print("Draw by insufficient material")
            return
        
        if chessboard.is_seventyfive_moves():
            print("Draw: 75 moves without a pawn push or capture")
            return

        
        turn_p1 = 1 - turn_p1
        i += 1
        print("-------------------------------------------\n")

if __name__ == "__main__":
    game_on()