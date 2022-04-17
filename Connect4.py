import math
import random
import numpy as np
import os
import pygame

board = np.array([[0,0,0,0,0,0,0] ,[0,0,0,0,0,0,0] ,[0,0,0,0,0,0,0] ,[0,0,0,0,0,0,0] ,[0,0,0,0,0,0,0] ,[0,0,0,0,0,0,0]])

ROWS = 6
COLS = 7

SYSTEM = 0
PLAYER = 1

EMPTY = 0
SYSTEM_PIECE = 2
PLAYER_PIECE = 1

FLAG = 4

BLUE = (0,0,255)
BLACK = (0,0,0)
RED = (255,0,0)
YELLOW = (255,255,0)


def print_board(board):
    print("    1  2  3  4  5  6  7  ")
    print("  ~~~~~~~~~~~~~~~~~~~~~~~")
    for i in range(5,-1,-1) :
        print("    " + str(board[i][0]) + "  " + str(board[i][1]) + "  " + str(board[i][2]) + "  " + str(board[i][3]) + "  " + str(board[i][4]) + "  " + str(board[i][5]) + "  " + str(board[i][6]) + "  ")
    print(" ")


def is_valid_col(board, col):
	return board[ROWS-1][col] == 0


def get_available_row(board, col):
	for r in range(ROWS):
		if board[r][col] == 0:
			return r


def drop_piece(board, row, col, piece):
	board[row][col] = piece


def is_win(board, piece):
	# Check horizontal locations for win
	for c in range(COLS-3):
		for r in range(ROWS):
			value = 0
			for i in range(FLAG):
				if board[r][c+i] == piece:
					value += piece
			if value == FLAG*piece:
				return True

	# Check vertical locations for win
	for c in range(COLS):
		for r in range(ROWS-3):
			value = 0
			for i in range(FLAG):
				if board[r+i][c] == piece:
					value += piece
			if value == FLAG*piece:
				return True

	# Check positively sloped diaganols
	for c in range(COLS-3):
		for r in range(ROWS-3):
			value = 0
			for i in range(FLAG):
				if board[r+i][c+i] == piece:
					value += piece
			if value == FLAG*piece:
				return True

	# Check negatively sloped diaganols
	for c in range(COLS-3):
		for r in range(3, ROWS):
			value = 0
			for i in range(FLAG):
				if board[r-i][c+i] == piece:
					value += piece
			if value == FLAG*piece:
				return True

	return False


def evaluate_space(space, piece):
	score = 0
	opp_piece = PLAYER_PIECE
	if piece == PLAYER_PIECE:
		opp_piece = SYSTEM_PIECE

	if space.count(piece) == 4:
		score += 100
	elif space.count(piece) == 3 and space.count(EMPTY) == 1:
		score += 5
	elif space.count(piece) == 2 and space.count(EMPTY) == 2:
		score += 2

	if space.count(opp_piece) == 3 and space.count(EMPTY) == 1:
		score -= 100

	return score


def score_move(board, piece):
	score = 0
	# Scoring horizontal spaces
	for c in range(COLS-3):
		for r in range(ROWS):
			space = []
			for i in range(FLAG):
				space.append(board[r][c+i])
			score += evaluate_space(space, piece)

	# Scoring vertical spaces
	for c in range(COLS):
		for r in range(ROWS-3):
			space = []
			for i in range(FLAG):
				space.append(board[r+i][c])
			score += evaluate_space(space, piece)

	# Scoring positively sloped diaganol spaces
	for c in range(COLS-3):
		for r in range(ROWS-3):
			space = []
			for i in range(FLAG):
				space.append(board[r+i][c+i])
			score += evaluate_space(space, piece)

	# Scoring negatively sloped diaganol spaces
	for c in range(COLS-3):
		for r in range(3, ROWS):
			space = []
			for i in range(FLAG):
				space.append(board[r-i][c+i])
			score += evaluate_space(space, piece)

	return score


def get_valid_cols(board):
	valid_cols = []
	for col in range(COLS):
		if is_valid_col(board, col):
			valid_cols.append(col)
	return valid_cols


def is_end_node(board):
	return is_win(board, PLAYER_PIECE) or is_win(board, SYSTEM_PIECE) or len(get_valid_cols(board)) == 0


def best_move(board, piece):
	valid_cols = get_valid_cols(board)
	best_score = -10000
	best_col = random.choice(valid_cols)
	for col in valid_cols:
		row = get_available_row(board, col)
		temp_board = board.copy()
		drop_piece(temp_board, row, col, piece)
		score = score_move(temp_board, piece)
		if score > best_score:
			best_score = score
			best_col = col

	return best_col


def minimax(board, depth, alpha, beta, maxPlayer):
	valid_cols = get_valid_cols(board)
	is_end = is_end_node(board)
	
	if depth == 0 or is_end:
		if is_end:
			if is_win(board, SYSTEM_PIECE):
				return (None, 100000000000000)
			elif is_win(board, PLAYER_PIECE):
				return (None, -100000000000000)
			else: # Game is over, no more valid moves
				return (None, 0)
		else: # Depth is zero
			return (None, score_move(board, SYSTEM_PIECE))
	
	if maxPlayer:
		value = -math.inf
		column = random.choice(valid_cols)
		for col in valid_cols:
			row = get_available_row(board, col)
			b_copy = board.copy()
			drop_piece(b_copy, row, col, SYSTEM_PIECE)
			new_score = minimax(b_copy, depth-1, alpha, beta, False)[1]
			if new_score > value:
				value = new_score
				column = col
			alpha = max(alpha, value)
			if alpha >= beta:
				break
		return column, value

	else: # Minimizing player
		value = math.inf
		column = random.choice(valid_cols)
		for col in valid_cols:
			row = get_available_row(board, col)
			b_copy = board.copy()
			drop_piece(b_copy, row, col, PLAYER_PIECE)
			new_score = minimax(b_copy, depth-1, alpha, beta, True)[1]
			if new_score < value:
				value = new_score
				column = col
			beta = min(beta, value)
			if alpha >= beta:
				break
		return column, value


SQUARESIZE = 80
WIDTH = COLS * SQUARESIZE
HEIGHT = (ROWS+1) * SQUARESIZE
SCREEN_SIZE = (WIDTH, HEIGHT)
RADIUS = int(SQUARESIZE/2 - 2)

def draw_board(board) :
	for col in range(COLS) :
		for row in range(ROWS) :
			pygame.draw.rect(SCREEN, BLUE, (col*SQUARESIZE, row*SQUARESIZE+SQUARESIZE, SQUARESIZE, SQUARESIZE))
			pygame.draw.circle(SCREEN, BLACK, (int(col*SQUARESIZE+SQUARESIZE/2), int((row+1)*SQUARESIZE+SQUARESIZE/2)), RADIUS)
	
	for col in range(COLS) :
		for row in range(ROWS):		
			if board[row][col] == PLAYER_PIECE :
				pygame.draw.circle(SCREEN, RED, (int(col*SQUARESIZE+SQUARESIZE/2), HEIGHT-int((row)*SQUARESIZE+SQUARESIZE/2)), RADIUS)
			elif board[row][col] == SYSTEM_PIECE : 
				pygame.draw.circle(SCREEN, YELLOW, (int(col*SQUARESIZE+SQUARESIZE/2), HEIGHT-int((row)*SQUARESIZE+SQUARESIZE/2)), RADIUS)
	pygame.display.update()	


pygame.init()
SCREEN = pygame.display.set_mode(SCREEN_SIZE)
draw_board(board)
#pygame.display.update()

# print("================================================================================")
# print("				C  O  N  N  E  C  T    4")
# print("================================================================================")
# print("")
# print("		1. Two Players		2. Single Player 		3. Autoplay			4. Quit")
# opt = int(input("Select Mode : "))

# if(not(opt == 1 or opt == 2 or opt == 3)):
# 	print("Invalid input")

STATUS = True
print_board(board)
turn = random.randint(SYSTEM, PLAYER)

while STATUS:
	#For players move
	if turn == PLAYER:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sys.exit()

			if event.type == pygame.MOUSEMOTION:
				pygame.draw.rect(SCREEN, BLACK, (0,0, WIDTH, SQUARESIZE))
				posX = event.pos[0]
				if turn == PLAYER:
					pygame.draw.circle(SCREEN, RED, (posX, int(SQUARESIZE/2)), RADIUS)

			pygame.display.update()

			if event.type == pygame.MOUSEBUTTONDOWN:
				pygame.draw.rect(SCREEN, BLACK, (0,0, WIDTH, SQUARESIZE))
				col = int(math.floor(posX/SQUARESIZE))

				if is_valid_col(board, col):
					row = get_available_row(board, col)
					drop_piece(board, row, col, PLAYER_PIECE)

					print("Player's move at column No."+str(col))
					print_board(board)
					draw_board(board)
					turn = (turn+1)%2
					
					if is_win(board, PLAYER_PIECE):
						print("It's Player WIN.")
						STATUS = False

	#For systems move
	if turn == SYSTEM and STATUS:
		
		col = minimax(board, 5, -100000000000000, 100000000000000, True)[0]
		
		if is_valid_col(board, col):
			row = get_available_row(board, col)
			drop_piece(board, row, col, SYSTEM_PIECE)

			print("System's move at column No."+str(col))
			print_board(board)
			draw_board(board)
			turn = (turn+1)%2

			if is_win(board, SYSTEM_PIECE):
				print("It's System WIN.")
				STATUS = False

	if not STATUS:
		pygame.time.wait(5000)
