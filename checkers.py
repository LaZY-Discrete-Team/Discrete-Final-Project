"""
Modified version of https://github.com/brettpilch/pygame-checkers
"""

import copy
import pygame
import math
import random
import time

# Define some colors
BLACK	= (   0,   0,   0)
WHITE	= ( 255, 255, 255)
GREEN	= (   0, 255,   0)
RED	  	= ( 255,   0,   0)
BLUE	= (   0,   0, 255)
YELLOW  = ( 255, 255,   0)
TRANS	= (   1,   2,   3)

# CONSTANTS:
WIDTH = 600
HEIGHT = 600
ROWS = 8
COLS = 8
MARK_SIZE = int(WIDTH / ROWS / 2)

class Game:
	"""class to keep track of the status of the game."""
	def __init__(self):
		"""
		Start a new game with an empty board and random player going first.
		"""
		self.status = 'playing'
		self.turn = 0 # random.randrange(2)
		self.players = ['r','b']
		self.tokens = [12, 12]
		self.selected_token = None
		self.jumping = False
		pygame.display.set_caption("%s's turn" % self.players[self.turn % 2])
		self.game_board = [['r','-','r','-','r','-','r','-'],
						   ['-','r','-','r','-','r','-','r'],
						   ['r','-','r','-','r','-','r','-'],
						   ['-','-','-','-','-','-','-','-'],
						   ['-','-','-','-','-','-','-','-'],
						   ['-','b','-','b','-','b','-','b'],
						   ['b','-','b','-','b','-','b','-'],
						   ['-','b','-','b','-','b','-','b']]

	def evaluate_click(self, mouse_pos):
		"""
		Select a token if none is selected.
		Move token to a square if it is a valid move.
		Start a new game if the game is over.
		"""
		if self.status == 'playing':
			to_loc = get_clicked_row(mouse_pos), get_clicked_column(mouse_pos)
			player = self.players[self.turn % 2]
			if self.selected_token:
				move = self.is_valid_move(player, self.selected_token, to_loc)
				if move[0]:
					winner = self.play(player, self.selected_token, to_loc, move[1])
					if winner is None:
						pygame.display.set_caption("%s's turn" % player)
					elif winner == 'draw':
						pygame.display.set_caption("It's a stalemate! Click to start again")
					else:
						pygame.display.set_caption("%s wins! Click to start again" % winner)
				elif to_loc[0] == self.selected_token[0] and to_loc[1] == self.selected_token[1]:
					self.selected_token = None
					if self.jumping:
						self.jumping = False
						self.next_turn()
				else:
					print('invalid move')
			else:
				if self.game_board[to_loc[0]][to_loc[1]].lower() == player:
					self.selected_token = to_loc
		elif self.status == 'game over':
			self.__init__()

	def is_valid_move(self, player, from_loc, to_loc):
		"""
		Check if clicked location is a valid square for player to move to.
		"""
		from_row = from_loc[0]
		from_col = from_loc[1]
		to_row = to_loc[0]
		to_col = to_loc[1]
		token_char = self.game_board[from_row][from_col]
		if self.game_board[to_row][to_col] != '-':
			return False, None
		if (((token_char.isupper() and abs(from_row - to_row) == 1) or (player == 'r' and to_row - from_row == 1) or
			 (player == 'b' and from_row - to_row == 1)) and abs(from_col - to_col) == 1) and not self.jumping:
			return True, None
		if (((token_char.isupper() and abs(from_row - to_row) == 2) or (player == 'r' and to_row - from_row == 2) or
			 (player == 'b' and from_row - to_row == 2)) and abs(from_col - to_col) == 2):
			jump_row = (to_row - from_row) / 2 + from_row
			jump_col = (to_col - from_col) / 2 + from_col
			if self.game_board[int(jump_row)][int(jump_col)].lower() not in [player, '-']:
				return True, [jump_row, jump_col]
		return False, None

	def possible_moves(self, player):
		moves = []
		if self.selected_token == None:
			ind = []
			for i, x in enumerate(self.game_board):
				for j, y in enumerate(x):
					if y.lower() == player:
						ind.append([i, j])
			for i in ind: # todo: fix this inefficiency of checking king moves too
				for p,q in [[1,1],[-1,-1],[1,-1],[-1,1],[2,2],[2,-2],[-2,2],[-2,-2]]:
						if ((i[0]+p) < ROWS) & ((i[0]+p) >= 0):
							if ((i[1]+q) < COLS) & ((i[1]+q) >= 0):
								ivm = self.is_valid_move(player, i, [i[0]+p, i[1]+q])
								if ivm[0] == True: moves.append([i, [i[0]+p, i[1]+q], ivm[1]])
		else:
			i = self.selected_token
			for p,q in [[1,1],[-1,-1],[1,-1],[-1,1],[2,2],[2,-2],[-2,2],[-2,-2]]:
					if ((i[0]+p) < ROWS) & ((i[0]+p) >= 0):
						if ((i[1]+q) < COLS) & ((i[1]+q) >= 0):
							ivm = self.is_valid_move(player, i, [i[0]+p, i[1]+q])
							if ivm[0] == True: moves.append([i, [i[0]+p, i[1]+q], ivm[1]])
		return moves

	def play(self, player, from_loc, to_loc, jump):
		"""
		Move selected token to a particular square, then check to see if the game is over.
		"""
		from_row = from_loc[0]
		from_col = from_loc[1]
		to_row = to_loc[0]
		to_col = to_loc[1]
		token_char = self.game_board[from_row][from_col]
		self.game_board[to_row][to_col] = token_char
		self.game_board[from_row][from_col] = '-'
		if (player == 'r' and to_row == ROWS-1) or (player == 'b' and to_row == 0):
			self.game_board[to_row][to_col] = token_char.upper()
		if jump:
			self.game_board[int(jump[0])][int(jump[1])] = '-'
			self.selected_token = [to_row, to_col]
			self.jumping = True
			self.tokens[player == self.players[0]] -= 1
		else:
			self.selected_token = None
			self.next_turn()
		winner = self.check_winner()
		if winner != None:
			self.status = 'game over'
		return winner

	def next_turn(self):
		self.turn += 1
		pygame.display.set_caption("%s's turn" % self.players[self.turn % 2])

	def check_winner(self):
		"""
		check to see if someone won, or if it is a draw.
		"""
		if self.tokens[0] == 0:
			return self.players[1]
		if self.tokens[1] == 0:
			return self.players[0]
		if self.tokens[0] == 1 & self.tokens[1] == 1:
			return 'draw'
		return None

	def draw(self):
		"""
		Draw the game board and the X's and O's.
		"""
		for i in range(ROWS+1):
			for j in range(COLS+1):
				if (i+j) % 2 == 1: # flip color of board
					pygame.draw.rect(screen, WHITE, (i * WIDTH / ROWS, j * HEIGHT / COLS, WIDTH / ROWS, HEIGHT / COLS))

		for r in range(len(self.game_board)):
			for c in range(len(self.game_board[r])):
				mark = self.game_board[r][c]
				if self.players[0] == mark.lower():
					color = RED
				else:
					color = BLUE
				if self.selected_token:
					if self.selected_token[0] == r and self.selected_token[1] == c:
						color = YELLOW
				if mark != '-':
					x = WIDTH / ROWS * c + WIDTH / ROWS / 2
					y = HEIGHT / COLS * r + HEIGHT / COLS / 2
					pygame.draw.circle(screen, color, (int(x), int(y)), MARK_SIZE)
					if self.game_board[r][c].isupper():
						pygame.draw.circle(screen, BLACK, (int(x), int(y)), int(MARK_SIZE*7/8), width=int(MARK_SIZE/8))

# Helper functions:
def get_clicked_column(mouse_pos):
	x = mouse_pos[0]
	for i in range(1, ROWS):
		if x < i * WIDTH / ROWS:
			return i - 1
	return ROWS-1

def get_clicked_row(mouse_pos):
	y = mouse_pos[1]
	for i in range(1, COLS):
		if y < i * HEIGHT / COLS:
			return i - 1
	return COLS-1

def minimax(game, depth, pl, framerate=None):
	""" args
	game: the game object holding game state
	depth: how many moves ahead to search in the game tree
	pl: index of the player that you want to maximize (0 or 1)
	framerate: if specified, will draw the possible future game states

	returns
	value: maximizing player pieces divided by minimizing player pieces
	best_moves: array of the best moves to make
	"""
	player = game.players[game.turn % 2] # the player whose turn it is currently

	# base case, depth reached
	if (depth == 0) | (game.check_winner() != None):
		your_pieces = game.tokens[pl]
		their_pieces = game.tokens[(pl+1)%2]
		value = your_pieces/their_pieces # metric on how maximizing player is doing
		if framerate != None: # draw game state if framerate specified
			screen.fill(BLACK)
			game.draw()
			pygame.display.flip()
			clock.tick(framerate)
			print(depth, game.players[pl], player, game.tokens, value)
		return value, []

	# maximizing player's turn
	elif player == game.players[pl]:
		value = 0 # starting value lower than the lowest ratio possible, 1/12
		moves = game.possible_moves(player)
		best_move = []
		for move in moves:

			# make a copy of the game to play out the current move in
			new_game = copy.deepcopy(game)
			new_game.play(player, move[0], move[1], move[2])
			minimaxer = minimax(new_game, depth-1, pl, framerate=framerate)

			# update best_move array based on the value this move gives
			tmpval = max(value, minimaxer[0])
			if value < tmpval: # better value than previous best move
				best_move = [move]
				value = tmpval
			elif tmpval == minimaxer[0]: # same value as previous best move
				best_move.append(move)

		print("maximize", depth, game.players[pl], player, game.tokens, value)
		return value, best_move

	# minimizing player's turn
	else:
		value = 13 # starting value higher than the highest ratio possible, 12/1
		moves = game.possible_moves(player)
		best_move = []
		for move in moves:

			# make a copy of the game to play out the current move in
			new_game = copy.deepcopy(game)
			new_game.play(player, move[0], move[1], move[2])
			minimaxer = minimax(new_game, depth-1, pl, framerate=framerate)

			# update best_move array based on the value this move gives
			tmpval = min(value, minimaxer[0])
			if value > tmpval: # better value than previous best move
				best_move = [move]
				value = tmpval
			elif tmpval == minimaxer[0]: # same value as previous best move
				best_move.append(move)

		print("minimize", depth, game.players[pl], player, game.tokens, value)
		return value, best_move

run_minimax = True
if run_minimax == False:
	# start pygame:
	pygame.init()
	size = (WIDTH, HEIGHT)
	screen = pygame.display.set_mode(size)
	game = Game() # start game
	done = False # Loop until the user clicks the close button.
	clock = pygame.time.Clock() # Used to manage how fast the screen updates

	# game loop:
	while not done:

		 # Main event loop
		 for event in pygame.event.get(): # User did something
			 if event.type == pygame.QUIT: # If user clicked close
				 done = True # Flag that we are done so we exit this loop
			 if event.type == pygame.KEYDOWN:
				 entry = str(event.key)
			 if event.type == pygame.MOUSEBUTTONDOWN:
				 mouse_x, mouse_y = pygame.mouse.get_pos()
				 game.evaluate_click(pygame.mouse.get_pos())

		 # Drawing code should go here
		 screen.fill(BLACK) # clear the screen to black
		 game.draw() # draw the game board and marks
		 pygame.display.flip() # update the screen with what we've drawn
		 clock.tick(60) # Limit to 60 frames per second

	pygame.quit() # Close the window and quit.

else:
	done = False
	pygame.init()
	size = (WIDTH, HEIGHT)
	screen = pygame.display.set_mode(size)
	game = Game()
	clock = pygame.time.Clock()
	maximizingPlayerIndex = 0 # which player the computer is playing for
	depth = 4 # How many moves ahead to look
	framerate = 60

	while not done:

		# if it's the computer's turn
		if game.turn % 2 == maximizingPlayerIndex:

			# figure out which moves would be best
			ratio, best_moves = minimax(game, depth, maximizingPlayerIndex, framerate=None)
			print("BEST MOVES:", best_moves)
			print()

			# play one of the best moves
			try:
				game.play(game.players[game.turn % 2], best_moves[0][0], best_moves[0][1], best_moves[0][2])
				screen.fill(BLACK)
				game.draw()
				pygame.display.flip()
				clock.tick(framerate)
			except:
				print("Stalemate :(")
				break

		# if it's the human's turn
		else:
			for event in pygame.event.get(): # User did something
				if event.type == pygame.QUIT: # If user clicked close
					done = True # Flag that we are done so we exit this loop
				if event.type == pygame.KEYDOWN:
					entry = str(event.key)
				if event.type == pygame.MOUSEBUTTONDOWN:
					mouse_x, mouse_y = pygame.mouse.get_pos()
					game.evaluate_click(pygame.mouse.get_pos())
		screen.fill(BLACK) # clear the screen to black
		game.draw() # draw the game board and marks
		pygame.display.flip() # update the screen with what we've drawn
		clock.tick(60) # Limit to 60 frames per second

	pygame.quit() # Close the window and quit.
