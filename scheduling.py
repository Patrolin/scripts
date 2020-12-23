def lateness(data, s=0):
  res = []
  for t, d in data:
    res.append(max(0, s+t - d))
    s += t
  return res

def maximum_lateness(data):
  return max(lateness(data))

def total_lateness(data):
  return sum(lateness(data))


data = [
  (2, 0),
  (2, 8),
  (2, 9),
  (3, 9),
  (3, 12),
  (5, 5),
  (5, 9),
  (5, 12),
  (8, 7),
  (10, 3),
]

def minimize_maximum_lateness(data, s=0): # O(n) - earliest deadline first
  #res = min(data, key=lambda x: x[1])
  res = min(data, key=lambda x: (x[1], x[0]))
  return res

def minimize_total_lateness(data, s=0): # O(n^2) - P=NP?
  i = 0; v = 10000000
  for j in range(len(data)):
    x = data[j]
    w = 0
    for k in range(len(data)):
      y = data[k]
      w += max(0, s+y[0] - y[1] + (x[0] if k != j else 0))
    if w < v:
      i = j
      v = w
  res = data[i]
  return res

def schedule(f, data):
  copy = [(t, d) for (t, d) in data]
  res = []
  s = 0
  while copy:
    x = f(copy, s)
    res.append(x)
    copy.remove(x)
    s += x[0]
  return res

print(M:= schedule(minimize_maximum_lateness, data))
print(T:= schedule(minimize_total_lateness, data))
print()

print(maximum_lateness(M))
print(maximum_lateness(T))
print(maximum_lateness(data))
print()

print(total_lateness(M))
print(total_lateness(T))
print(total_lateness(data))

