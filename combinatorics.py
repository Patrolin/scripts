from math import *

def V(k, n):
  return prod(n-i for i in range(k))

def P(n):
  return V(n, n) # n!

def K(k, n):
  return V(k, n) // P(k) # n choose k (integer binomial coefficient)
