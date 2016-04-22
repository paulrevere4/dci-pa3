#!/usr/bin/python3
import execnet
OUTPUT_FILE_NAME = "heat-seq.map"

MAX_X = 120
MAX_Y = 120
NUM_ITERATIONS = 1024
NUM_MACHINES = 8

from join import *
import sys

def flush():
  sys.stdout.flush()

# Make state array
HEAT_GRID = [[20.0 for x in range(MAX_X)] for y in range(MAX_Y)]

#@puresignal
def initialize(channel, grid):
  """Set Initial Conditions for State Array"""
  for y in range(30, 89):
    grid[y][0] = 100.0

  channel.send(grid)

#@puresignal
def slave_process(channel, row, below_row, above_row):
  """Main worker process"""
  if below_row == [] or above_row == []:
    # row is on an edge, Edge squares remain in steady state
    channel.send(row)

  else:
    new_row = []

    for i in range(len(row)):
      if i > 0 and i < len(row)-1:
        #check if the cell is inside the edges, average its neighbors
        neighbors = []
        neighbors.append(row[i-1])
        neighbors.append(row[i+1])
        neighbors.append(below_row[i])
        neighbors.append(above_row[i])
        new_val = sum(neighbors)/len(neighbors)
        new_row.append(new_val)
      else:
        #if the cell is on an edge its value stays
        new_row.append(row[i])

    channel.send(new_row)

#@puresignal
def result_printer(grid):
  print("Finished computation")
  f = open(OUTPUT_FILE_NAME, 'w')
  f.write("%d %d\n" % (MAX_X, MAX_Y))
  for y in grid:
    for x in y:
      out_str = "%d"%x
      f.write(out_str.ljust(4, ' '))
    f.write("\n")

def iterate(gws, iteration, max_iterations, grid, max_y_arg, max_x_arg):
  while iteration < max_iterations:
    gw = gws[iteration % NUM_MACHINES]
    print("Started iteration", iteration)
    

    slaves = []
    #Spawn slave processes with old grid state
    for y in range(max_y_arg):
      # print("looping")
      above_row = []
      below_row = []
      row = grid[y]
      if y > 0:
        above_row = grid[y-1]
      if y < max_y_arg-1:
        below_row = grid[y+1]

      slave = gw.remote_exec(slave_process, row=row, below_row=below_row, above_row=below_row)
      slaves.append(slave)

    print("Launched workers. Waiting on results")
    # Update state array
    for i in range(len(slaves)):
      slave = slaves[i]
      new_row = slave.receive()
      grid[i] = new_row

    iteration += 1

  # Check if finished
  print("DONE")
  result_printer(grid)
  # gw.remote_exec(result_printer, grid=HEAT_GRID) #TODO: change to remote_exec
  return grid
  # print ("IAMHERE")

if __name__ == "__main__":
  import time
  gws = []
  for i in range(NUM_MACHINES):
    #gws.append(execnet.makegateway("ssh=localhost"))
    gws.append(execnet.makegateway())
  #TODO: convert pursignal calls to remote_exec calls, return statements become channel.send
  # Spawn/Join on intializer
  #HEAT_GRID = (puresignal(initialize)(HEAT_GRID)).join()
  HEAT_GRID = (gws[0].remote_exec(initialize, grid=HEAT_GRID)).receive()
  print("Initialized heat grid")
  flush()
  # Spawn calculator
  iterate(gws, 0, NUM_ITERATIONS, HEAT_GRID, MAX_Y, MAX_X)
