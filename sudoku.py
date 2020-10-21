from random import choice, sample
from time import sleep

class InvalidCollapse(Exception):
	pass

def print_sudoku(sudoku: list):
	for r in range(9):
		for c in range(9):
			x = sudoku[9*r + c]
			print(list(x)[0] if len(x) == 1 else ('{}' if len(x) == 0 else x), end=' ')
		print()
	print()


def solve(sudoku: list):
	while True:
		i = min_entropy(sudoku)
		if len(sudoku[i]) == 0:
			raise InvalidCollapse()
		elif len(sudoku[i]) == 1:
			return sudoku
		else:
			for x in sample(sudoku[i], len(sudoku[i])): # todo: sample a distribution
				new_sudoku = [{x for x in item} for item in sudoku]
				collapse(new_sudoku, i, x)
				propagate(new_sudoku, [i])
				try:
					return solve(new_sudoku)
				except InvalidCollapse:
					pass
			raise InvalidCollapse()

def check(sudoku: list):
	new_sudoku = [{x for x in item} for item in sudoku]
	propagate(new_sudoku, [*range(9*9)])
	return new_sudoku

def min_entropy(sudoku: list): # todo: implement actual entropy
	return min(range(9*9), key=lambda i: len(sudoku[i]) if len(sudoku[i]) != 1 else 20)

def collapse(sudoku: list, i: int, x: int):
	sudoku[i] = {x}

def propagate(sudoku: list, stack: list):
	while stack:
		i = stack.pop()
		x = sudoku[i]
		if len(x) == 0:
			continue
		elif len(x) == 1:
			x0 = list(x)[0]
			for j in entangled(i):
				if x0 in sudoku[j]:
					sudoku[j].discard(x0)
					stack.append(j)

def entangled(i: int):
	row, col = divmod(i, 9)
	block_row = 3 * (row // 3)
	block_col = 3 * (col // 3)
	result = {9*row + c for c in range(9)}
	result |= {9*r + col for r in range(9)}
	result |= {9*(block_row + r) + (block_col + c) for c in range(3) for r in range(3)}
	result -= {i}
	return result
	


if __name__ == '__main__':
	import re

	# setup initial conditions
	with open('sudoku.txt', 'r') as f:
		sudoku = [{int(x) % 9} if x.isnumeric() else {i for i in range(9)} for x in re.findall(r'\S', f.read())]
	sudoku = check(sudoku)
	print_sudoku(sudoku)

	# solve
	solved = solve(sudoku)
	print_sudoku(solved)

