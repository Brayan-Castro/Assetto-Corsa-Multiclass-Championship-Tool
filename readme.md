## A Simple tool that simulates WEC Championship for offline play.
As Assetto Corsa doesnt natively support multiclass racing while offline (and i couldnt find a mod that did this) i made this tool.<br>
It's still very primitive but it will be updated, the idea is to have a GUI and support for other championships (such as f1 with teams)<br>
Currently these are it's features.<br>
Technically you could use this on online races (as long as you follow the car naming convention or hardcode them yourself) but i presume there are much better tools for that.

## Features
Ingame Timer app that acurately gets positions when the player force quits from a race (will be added to this repo later);<br>
Allows for the creation of custom championships and races based on the wec format, with, technically any GT3 and LMH car;<br>
Added support for manufacturers championships (just added but probably working)
Allows for custom point system based on its class;<br>
Losail and Bahrain reward 1.5x points, while La Sarthe rewards 2x;<br>
Pole position on a race gives 1 extra point.<br>

## Changelog v0.6
Code modularization;<br>
Separated award_points() into smaller, more concise functions;<br>
Started adding type annotations to functions;<br>
Added comments;<br>
added a simplistic (but working) GUI :)<br>
Changed the project folder structure (again).

## Planned Changes
show winners after the race;<br>
make the GUI less shit;<br>
Clean the code some more (still needed, there is A LOT of redudancy, specially with functions, there are 3 get_team_{something} functions, and as of the creation of acLapGUI, the acLap file is mainly a wrapper? for other things);<br>
Next step is adjust how to app finds the necessary config files and compile everything to a standalone .exe;

## About teams.json
Driver names need to match the driver names inside the game, team names can be anything you want.