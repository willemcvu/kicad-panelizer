import os
import sys
from argparse import ArgumentParser
from pathlib import Path
import pcbnew
from pcbnew import *
"""
A simple script to create a v-scored panel of a KiCad board.
Author: Willem Hillier
This script is very much in-progress, and so here's an extensive TODO list:
    - Put report in panel file in a text field
    - Put logo/text block on panel border
    - Put fuducials on border
    - Auto-calculate distance from line to text center ("V-SCORE") based on text size
    - Is there a way to pull back copper layers to the pullback distances so if the user presses "b" on the panel, it doesn't get wrecked (by copper getting too close to V-scores)
    - (maybe) Make a "DRC" that checks if copper is too close to V-score lines
"""

# set up command-line arguments parser
parser = ArgumentParser(description="A script to panelize KiCad files.")
parser.add_argument(dest="sourceBoardFile", help='Path to the *.kicad_pcb file to be panelized')
args = parser.parse_args()
sourceBoardFile = args.sourceBoardFile

#Check that input board is a *.kicad_pcb file
sourceFileExtension = os.path.splitext(sourceBoardFile)[1]
if not(sourceFileExtension == '.kicad_pcb'):
    print(sourceBoardFile + " is not a *.kicad_pcb file. Quitting.")
    quit()

# Output file name is format {inputFile}_panelized.kicad_pcb
panelOutputFile = os.path.splitext(sourceBoardFile)[0] + "_panelized.kicad_pcb"

# To scale KiCad's nm to mm
# All dimension parameters used by this script are mm unless otherwise noted
SCALE = 1000000

# number of copies of source board on panel in X and Y directions
NUM_X = 4
NUM_Y = 4

# edge rail dimensions
HORIZONTAL_EDGE_RAIL_WIDTH = 0
VERTICAL_EDGE_RAIL_WIDTH = 10

#v-scoring parameters
V_SCORE_LAYER = "Eco1.User"
V_SCORE_LINE_LENGTH_BEYOND_BOARD = 20
V_SCORE_TEXT_CENTER_TO_LINE_LENGTH = 10
V_SCORE_TEXT = "V-SCORE"
V_SCORE_TEXT_SIZE = 2
V_SCORE_TEXT_THICKNESS = 0.1

#Creates a list that can be used to lookup layer numbers by their name
def get_layertable():
    layertable = {}

    numlayers = pcbnew.PCB_LAYER_ID_COUNT
    for i in range(numlayers):
        layertable[board.GetLayerName(i)] = i
#        print("{} {}".format(i, board.GetLayerName(i)))
    return layertable

#Used to create progress bar, from here: https://gist.github.com/vladignatyev/06860ec2040cb497f0f3
def progress(count, total, suffix=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s %s\r' % (bar, percents, '%', suffix))
    sys.stdout.flush()  # As suggested by Rom Ruben


#load source board
board = LoadBoard(sourceBoardFile)
print('Loaded board\n')

# set up layer table
layertable = get_layertable()

#get dimensions of board
boardWidth = board.GetBoardEdgesBoundingBox().GetWidth()
boardHeight = board.GetBoardEdgesBoundingBox().GetHeight()


# Now it's time to make an array of tracks, drawings, modules (footprints), and zones.
# array of tracks
tracks = board.GetTracks()

#get total number of tracks for progress bar
n = 0
for track in tracks:
    n += 1

i = 0
newTracks = []
for sourceTrack in tracks:                          # Iterate through each track to be copied
    for x in range(0,NUM_X):                        # Iterate through x direction
        for y in range(0, NUM_Y):                   # Iterate through y direction
            i += 1
            if((x!=0)or(y!=0)):                     # Don't duplicate source object to location
                newTrack = sourceTrack.Duplicate()
                newTrack.Move(wxPoint(x*boardWidth, y*boardWidth)) # Move to correct location
                newTracks.append(newTrack)          # Add to temporary list of tracks
                progress(i ,n*NUM_X*NUM_Y,'Positioning tracks')                    # Progress bar

print("\n")

i=0
for track in newTracks:  # add new tracks to board
    tracks.Append(track)
    i += 1
    progress(i, len(newTracks), 'Adding tracks to panel' )
    

# array of drawing objects
drawings = board.GetDrawings()

n = 0
for drawing in drawings:
    n += 1

newDrawings = []

i = 0
for drawing in drawings:                          # Iterate through each object to be copied
    for x in range(0,NUM_X):                    # Iterate through x direction
        for y in range(0, NUM_Y):               # Iterate through y direction
            i += 1
            if((x!=0)or(y!=0)):                     # Don't duplicate source object to location
                newDrawing = drawing.Duplicate()
                newDrawing.Move(wxPoint(x*boardWidth, y*boardWidth)) # Move to correct location
                newDrawings.append(newDrawing)              # Add to temporary list of objects
                progress(i ,n*NUM_X*NUM_Y,'Positioning drawings')                    # Progress bar

print("\n")

i=0
for drawing in newDrawings:  # add new objects to board
    board.Add(drawing)
    i += 1
    progress(i ,len(newDrawings),'Adding drawings to panel')                    # Progress bar


print("\n")

# array of modules
modules = board.GetModules()

n = 0
for module in modules:
    n += 1

newModules = []

i = 0

for sourceModule in modules:                                        # Iterate through each object to be copied
    for x in range(0,NUM_X):                                    # Iterate through x direction
        for y in range(0, NUM_Y):                               # Iterate through y direction
            i += 1
            if((x!=0)or(y!=0)):                                     # Don't duplicate source object to location
                newModule = pcbnew.MODULE(sourceModule)
                newModule.SetPosition(wxPoint(x*boardWidth + sourceModule.GetPosition().x, y*boardWidth + sourceModule.GetPosition().y)) # Move to correct location
                newModules.append(newModule)                        # Add to temporary list of objects
                progress(i ,n*NUM_X*NUM_Y,'Positioning modules')                    # Progress bar

print("\n")

i = 0
for module in newModules:  # add new objects to board
    board.Add(module)
    i += 1
    progress(i, len(newModules), 'Adding modules to panel')

print("\n")

# array of zones
modules = board.GetModules()                  #used to extract nets for zones...
newZones = []

#total for progress bar
n = 0
for a in range(0, board.GetAreaCount()):
    for x in range(0, NUM_X):
        for y in range(0, NUM_Y):
            n += 1


i = 0

for a in range(0,board.GetAreaCount()):       # Iterate through each object to be copied
    sourceZone = board.GetArea(a)                     
    for x in range(0,NUM_X):                    # Iterate through x direction
        for y in range(0, NUM_Y):               # Iterate through y direction
            i += 1
            progress(i, n, 'Determining nets of zones')
            if((x!=0)or(y!=0)):                     # Don't duplicate source object to location
                newZone = sourceZone.Duplicate()
                newZone.SetNet(sourceZone.GetNet())
                newZone.Move(wxPoint(x*boardWidth, y*boardWidth)) # Move to correct location

                # simulate pullback distance

                newZones.append(newZone)              # Add to temporary list of objects

print("\n")

i = 0
for zone in newZones:  # add new objects to board
    board.Add(zone)
    i += 1
    progress(i, len(newZones), 'Adding new zones to board')

print("\n")

# Get dimensions and center coordinate of entire array (without siderails to be added shortly)
arrayWidth = board.GetBoardEdgesBoundingBox().GetWidth()
arrayHeight = board.GetBoardEdgesBoundingBox().GetHeight()
arrayCenter = board.GetBoardEdgesBoundingBox().GetCenter()

# Erase all existing edgeCuts objects (individual board outlines)
drawings = board.GetDrawings()
for drawing in drawings:                          # Iterate through each object to be copied
    if(drawing.IsOnLayer(layertable["Edge.Cuts"])):
        drawing.DeleteStructure()

print("Existing Edge.Cuts lines deleted.")

# Create actual Edge.Cuts perimeter
edge = pcbnew.DRAWSEGMENT(board)
board.Add(edge)
edge.SetStart(pcbnew.wxPoint(arrayCenter.x - arrayWidth/2 - HORIZONTAL_EDGE_RAIL_WIDTH*SCALE, arrayCenter.y - arrayHeight/2 - VERTICAL_EDGE_RAIL_WIDTH*SCALE))
edge.SetEnd( pcbnew.wxPoint(arrayCenter.x + arrayWidth/2 + HORIZONTAL_EDGE_RAIL_WIDTH*SCALE, arrayCenter.y - arrayHeight/2 - VERTICAL_EDGE_RAIL_WIDTH*SCALE))
edge.SetLayer(layertable["Edge.Cuts"])

edge = pcbnew.DRAWSEGMENT(board)
board.Add(edge)
edge.SetStart(pcbnew.wxPoint(arrayCenter.x + arrayWidth/2 + HORIZONTAL_EDGE_RAIL_WIDTH*SCALE, arrayCenter.y - arrayHeight/2 - VERTICAL_EDGE_RAIL_WIDTH*SCALE))
edge.SetEnd( pcbnew.wxPoint(arrayCenter.x + arrayWidth/2 + HORIZONTAL_EDGE_RAIL_WIDTH*SCALE, arrayCenter.y + arrayHeight/2 + VERTICAL_EDGE_RAIL_WIDTH*SCALE))
edge.SetLayer(layertable["Edge.Cuts"])

edge = pcbnew.DRAWSEGMENT(board)
board.Add(edge)
edge.SetStart( pcbnew.wxPoint(arrayCenter.x + arrayWidth/2 + HORIZONTAL_EDGE_RAIL_WIDTH*SCALE, arrayCenter.y + arrayHeight/2 + VERTICAL_EDGE_RAIL_WIDTH*SCALE))
edge.SetEnd( pcbnew.wxPoint(arrayCenter.x - arrayWidth/2 - HORIZONTAL_EDGE_RAIL_WIDTH*SCALE, arrayCenter.y + arrayHeight/2 + VERTICAL_EDGE_RAIL_WIDTH*SCALE))
edge.SetLayer(layertable["Edge.Cuts"])

edge = pcbnew.DRAWSEGMENT(board)
board.Add(edge)
edge.SetStart( pcbnew.wxPoint(arrayCenter.x - arrayWidth/2 - HORIZONTAL_EDGE_RAIL_WIDTH*SCALE, arrayCenter.y + arrayHeight/2 + VERTICAL_EDGE_RAIL_WIDTH*SCALE))
edge.SetEnd( pcbnew.wxPoint(arrayCenter.x - arrayWidth/2 - HORIZONTAL_EDGE_RAIL_WIDTH*SCALE, arrayCenter.y - arrayHeight/2 - VERTICAL_EDGE_RAIL_WIDTH*SCALE))
edge.SetLayer(layertable["Edge.Cuts"])

print("New Edge.Cuts created.")

# re-calculate board dimensions with new edge cuts
panelWidth = board.GetBoardEdgesBoundingBox().GetWidth()
panelHeight = board.GetBoardEdgesBoundingBox().GetHeight()
panelCenter = arrayCenter #should be the same as arrayCenter

# V-scoring lines

# absolute edges of v-scoring
vscore_top = panelCenter.y - panelHeight/2 - V_SCORE_LINE_LENGTH_BEYOND_BOARD*SCALE
vscore_bottom = panelCenter.y + panelHeight/2 + V_SCORE_LINE_LENGTH_BEYOND_BOARD*SCALE
vscore_right = panelCenter.x + panelWidth/2 + V_SCORE_LINE_LENGTH_BEYOND_BOARD*SCALE
vscore_left = panelCenter.x - panelWidth/2 - V_SCORE_LINE_LENGTH_BEYOND_BOARD*SCALE

v_scores = []
# vertical v-scores
for x in range(1,NUM_X):
    x_loc = panelCenter.x - panelWidth/2 + HORIZONTAL_EDGE_RAIL_WIDTH*SCALE + boardWidth*x
    v_score_line = pcbnew.DRAWSEGMENT(board)
    v_scores.append(v_score_line)
    v_score_line.SetStart(pcbnew.wxPoint(x_loc, vscore_top))
    v_score_line.SetEnd(pcbnew.wxPoint(x_loc, vscore_bottom))
    v_score_line.SetLayer(layertable[V_SCORE_LAYER])
    
    v_score_text = pcbnew.TEXTE_PCB(board)
    v_score_text.SetText(V_SCORE_TEXT)
    v_score_text.SetPosition(wxPoint(x_loc, vscore_top - V_SCORE_TEXT_CENTER_TO_LINE_LENGTH*SCALE))
    v_score_text.SetTextSize(pcbnew.wxSize(SCALE*V_SCORE_TEXT_SIZE,SCALE*V_SCORE_TEXT_SIZE))
    #v_score_text.SetThickness(SCALE*1)
    v_score_text.SetLayer(layertable[V_SCORE_LAYER])
    v_score_text.SetTextAngle(900)
    board.Add(v_score_text)

print("Vertical v-scores created.")
    
# horizontal v-scores
for y in range(0,NUM_Y+1):
    y_loc = panelCenter.y - panelHeight/2 + VERTICAL_EDGE_RAIL_WIDTH*SCALE + boardWidth*y
    v_score_line = pcbnew.DRAWSEGMENT(board)
    v_scores.append(v_score_line)
    v_score_line.SetStart(pcbnew.wxPoint(vscore_left, y_loc))
    v_score_line.SetEnd(pcbnew.wxPoint(vscore_right, y_loc))
    v_score_line.SetLayer(layertable[V_SCORE_LAYER])
    
    v_score_text = pcbnew.TEXTE_PCB(board)
    v_score_text.SetText(V_SCORE_TEXT)
    v_score_text.SetPosition(wxPoint(vscore_left - V_SCORE_TEXT_CENTER_TO_LINE_LENGTH*SCALE, y_loc))
    v_score_text.SetTextSize(pcbnew.wxSize(SCALE*V_SCORE_TEXT_SIZE,SCALE*V_SCORE_TEXT_SIZE))
    #v_score_text.SetThickness(SCALE*1)
    v_score_text.SetLayer(layertable[V_SCORE_LAYER])
    v_score_text.SetTextAngle(0)
    board.Add(v_score_text)

print("Horizontal v-scores created.")

# In order to make sure copper is pulled-back from the v-score, we can move the v-scores to the edge.cuts layer, re-fill zones, then move them back. 
# Also, lock all the zones to ensure they can't get refilled and therefore messed up.

# move vscores to edge.cuts layer
for vscore in v_scores:
    vscore.SetLayer(layertable["Edge.Cuts"])
    board.Add(vscore)

# refill zones
#pcbnew.ZONE_FILLER(board).Fill(board.Zones())

# move back to correct layer
for vscore in v_scores:
    vscore.SetLayer(layertable[V_SCORE_LAYER])

# Save output
board.Save(panelOutputFile)
print("Board output saved to " + panelOutputFile)

# Print report
print("\nREPORT:")
print("Board dimensions: " + str(boardWidth/SCALE) + "x" + str(boardHeight/SCALE) + "mm")
print("Panel dimensions: " + str(panelWidth/SCALE) + "x" + str(panelHeight/SCALE) + "mm")
