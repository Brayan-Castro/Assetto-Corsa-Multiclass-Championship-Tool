## A Simple tool that simulates WEC Championship for offline play.

As Assetto Corsa doesnt natively support multiclass racing while offline (and i couldnt find a mod that did this) i made this tool.<br>
It's still very primitive but it will be updated, the idea is to have a GUI and support for other championships (such as f1 with teams)<br>
Currently these are it's features.
Technically you could use this on online races (as long as you follow the car naming convention or hardcode them yourself) but i presume there are much better tools for that.

## Features

Ingame Timer app that acurately gets positions when the player force quits from a race
Allows for the creation of custom championships and races based on the wec format, with, technically any car (the cars that i used, mainly from RSS, TRR and ACF, all of the gts had or gt3s or gtm on its id, so it was filtered and separated by class based on that, as i only used gt3s and lmhs, all the cars that dont have gt3 or gtm on its ids will be marked as lmh, other than that, everything goes)
Allows for custom point system based on its class
Losail and Bahrain reward 1.5x points, while La Sarthe rewards 2x
Pole position on a race gives 1 extra point.

## Planned Changes

Visualization of points (as of now, the only way to see the points on a championship is by querying the db).
Add support for manufacturers championships.
Change the starting grid based on class standing (as of now basically every race is divided at the bottom 50 being always gt3s) # Not possible without LUA and i dont want to do that now.
Add GUI or atleast CLI.