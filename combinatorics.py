from math import *

def V(k: int, n: int):
  return prod(n-i for i in range(k))

def P(n: int):
  return V(n, n) # n!

def K(k: int, n: int):
  return V(k, n) // P(k) # n choose k (integer binomial coefficient)

def factors(N: int):
	primes = [2, 3]
	result = []
	i = 0
	while N > 1:
		if i >= len(primes):
			p = primes[-1] + 2
			while N % p != 0:
				p += 2
			primes.append(p)
		if N % primes[i] == 0:
			N /= primes[i]
			result.append(primes[i])
		else:
			i += 1
	return result
