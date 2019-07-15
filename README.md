# kicad-panelizer
A simple script to create a v-scored panel of a KiCad board.

To use:
1. Ensure you have KiCad 5.1.2+ installed
2. Clone script to an appropriate location
3. Configure options
    1. Open script with text editor and change board input/output paths to the paths of the input/output board files. Note that the output path will replace any existing board file at the output path.
    2. Change NUM_X and NUM_Y to the number of copies of the board in the x (horizontal) and y (vertical) direction.
    3. (optional) set v-score parameters to what you wish.
    4. Save script
4. Open a terminal and `cd` to the directory of the script
5. Run it with python 3: `python3 panelizer.py`

Please submit feature requests and bug reports via GitHub Issues.
