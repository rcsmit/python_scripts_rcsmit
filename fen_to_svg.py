import chess, sys
import chess.svg
import time

# Install python-chess to your Python3 virtualenv
# virtualenv -p python3 ~/path/to/myvenv
# source /path/to/myvenv/bin/activate
# Usage: python3 fen-to-svg.py 'myfenstring' outputfilename
# or /path/to/myvenv/bin/python3 fen-to-svg.py 'myfenstring' outputfilename
#fen = sys.argv[1]
fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
#file_name = '{}.svg'.format(sys.argv[2])

seconds = str(int(time.time()))



file_name ="FEN_output"+ seconds + ".svg"
board = chess.Board(fen)

boardsvg = chess.svg.board(board = board)
with open(file_name, "w") as f:
    f.write(boardsvg)
print ("Done. Filename" + file_name)