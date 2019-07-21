# kicad-panelizer
A simple script to create a v-scored panel of a KiCad board.

To use:
1. Ensure you have KiCad 5.1.2+ installed
2. Clone script to an appropriate location
3. Configure options
    1. Change NUM_X and NUM_Y to the number of copies of the board in the x (horizontal) and y (vertical) direction.
    2. (optional) set v-score parameters to what you wish.
    3. Save script
4. Open a terminal and `cd` to the directory of the script
5. Run it with python 3: `python3 panelizer.py /path/to/source_board.kicad_pcb`
6. Panelized output will be saved to the same directory as the source board, with the name `{sourceboardname}_panelized.kicad_pcb`

Please submit feature requests and bug reports via GitHub Issues.
