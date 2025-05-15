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

## Changelog v0.5
Code modularization;<br>
Separated award_points() into smaller, more concise functions;<br>
Started adding type annotations to functions;<br>
Added comments;<br>
Changed the project folder structure.

## Planned Changes

Visualization of points (as of now, the only way to see the points on a championship is by querying the db);<br>
Add GUI;<br>
Add a function to get and show the winners after the last race;<br>
Clean the code some more.

## About teams.json

Driver names need to match the driver names inside the game, the, team names can be anything you want.