#!/usr/bin/python3
import execnet
OUTPUT_FILE_NAME = "heat-seq.map"

MAX_X = 122
MAX_Y = 122
#NUM_ITERATIONS = 1024
NUM_ITERATIONS = 1

from join import *
import sys

def flush():
  sys.stdout.flush()

# Make state array
HEAT_GRID = [[20.0 for x in range(MAX_X)] for y in range(MAX_Y)]

#@puresignal
def initialize(channel, grid):
  """Set Initial Conditions for State Array"""
  for y in range(30, 92):
    grid[y][0] = 100.0

  channel.send(grid)

#@puresignal
def slave_process(channel, old_grid, x, y):
  """Main worker process"""
  if x == 0 or y == 0 or x == MAX_X - 1 or y == MAX_Y - 1:
    # Edge squares remain in steady state
    return (x,y, old_grid[y][x])

  # Get neighbor values
  neighbors = [
                old_grid[y-1][x-1], # Top left
                old_grid[y-1][x], # Up one
                old_grid[y][x-1], # Left one
                old_grid[y][x] #Own old value
              ]

  y_height_okay = False
  if (y+1) < len(old_grid):
    y_height_okay = True
    neighbors.append(old_grid[y+1][x]) # Down one
  if ((x+1) < len(old_grid[y])):
    neighbors.append(old_grid[y][x+1]) # Right one
    if y_height_okay:
      neighbors.append(old_grid[y+1][x+1]) # Bottom Right
      neighbors.append(old_grid[y+1][x-1]) # Bottom left
      neighbors.append(old_grid[y-1][x+1]) # Top Right

  # Calculate avg of neighbors and self
  new_val = sum(neighbors)/len(neighbors)

  # Report assigned coordinates and new value
  return (x,y, new_val)

#@puresignal
def result_printer(grid):
  print("Finished computation")
  f = open(OUTPUT_FILE_NAME, 'w')
  f.write("%d %d\n" % (MAX_X, MAX_Y))
  for y in grid:
    for x in y:
      f.write("%d\n" % (x))

def iterate(gw, iteration, grid):
  print("Started iteration", iteration)
  # Check if finished
  if iteration == NUM_ITERATIONS:
    print("DONE")
    puresignal(result_printer)(grid) #TODO: change to remote_exec
    return grid

  slaves = []
  #Spawn slave processes with old grid state
  for y in range(MAX_Y):
    for x in range(MAX_X):
      slave = puresignal(slave_process)(grid, x, y) #TODO: Change this to remote_exec
      slaves.append(slave)
  print("Launched workers. Waiting on results")
  # Update state array
  for i in range(len(slaves)):
    slave = slaves[i]
    (x,y, val) = slave.join() #TODO: CHange this to receive
    grid[y][x] = val

  # Run next iteration
  iterate(iteration + 1, grid)

if __name__ == "__main__":
  import time
  gw = execnet.makegateway()
  #TODO: convert pursignal calls to remote_exec calls, return statements become channel.send
  # Spawn/Join on intializer
  #HEAT_GRID = (puresignal(initialize)(HEAT_GRID)).join()
  HEAT_GRID = (gw.remote_exec(initialize, grid=HEAT_GRID)).receive()
  print("Initialized heat grid")
  flush()
  # Spawn calculator
  iterate(gw, 0, HEAT_GRID)