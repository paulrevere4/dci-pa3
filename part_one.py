#!/usr/bin/python3

OUTPUT_FILE_NAME = "heat-seq.map"

MAX_X = 122
MAX_Y = 122
NUM_ITERATIONS = 1024

from join import *
import sys

def flush():
  sys.stdout.flush()

# Make state array
HEAT_GRID = [[20.0 for x in range(MAX_X)] for y in range(MAX_Y)]

def initialize(grid):
  """Set Initial Conditions for State Array"""
  for y in range(30, 92):
    grid[y][0] = 100.0
  return grid

def array_sum(array):
  """Do floating point summation of array"""
  out_sum = 0.0
  for elem in array:
    out_sum += float(elem)
  return out_sum

def slave_process(row, below_row, above_row):
  """Main worker process"""
  new_row = []

  assert(len(row) == MAX_X)

  for x in range(len(row)):
    if x > 0 and x < len(row)-1:
      #check if the cell is inside the edges, average its neighbors
      neighbors = []
      neighbors.append(row[x-1]) # Left
      neighbors.append(row[x+1]) # Right
      neighbors.append(below_row[x]) # Bottom
      neighbors.append(above_row[x]) # Top
      a_s = array_sum(neighbors)
      assert(len(neighbors) == 4)
      new_val = a_s / 4.0
      new_row.append(new_val)
    else:
      #if the cell is on an edge its value stays
      new_row.append(row[x])

  return new_row

def result_printer(grid):
  print("Finished computation")
  f = open(OUTPUT_FILE_NAME, 'w')
  f.write("%d %d\n" % (MAX_X, MAX_Y))
  for x in range(MAX_X):
    for y in range(MAX_Y):
      f.write("%.6f\n" % grid[x][y])

def iterate(iteration, grid):
  print("Started iteration", iteration)
  # Check if finished
  if iteration == NUM_ITERATIONS:
    print("DONE")
    puresignal(result_printer)(grid)
    return grid

  slaves = []

  #Spawn slave processes with old grid state
  for y in range(1, MAX_Y - 1):
    row = grid[y]
    above_row = grid[y-1]
    below_row = grid[y+1]

    slave = puresignal(slave_process)(row, below_row, above_row)
    slaves.append(slave)
  print("Launched workers. Waiting on results")
  assert(len(slaves) == MAX_Y - 2 ) # Skip top and bottom rows
  # Update state array
  for i in range(len(slaves)):
    slave = slaves[i]
    new_row = slave.join()
    grid[i+1] = new_row
  # Spawn next iteration
  print("Finished iteration ", iteration)
  iterator = puresignal(iterate)(iteration + 1, grid)
  return iterator.join()

if __name__ == "__main__":
  import time
  # Spawn/Join on intializer
  HEAT_GRID = (puresignal(initialize)(HEAT_GRID)).join()
  print("Initialized heat grid")
  flush()
  # Spawn calculator
  iterator = puresignal(iterate)(0, HEAT_GRID)
