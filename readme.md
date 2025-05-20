## Assetto Corsa Multi-Class Championship Tool (MCT).
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

## Changelog v1.0 (yay)
Refactured a bunch of code;<br>
Fixed bugs involved with the handling and usage of the teams_config.json (basically, now names dont need to be removed from the file if they aren't in the game also);<br>
Fixed how the drivers are showed in the manufacturers championship table in the GUI (as the team_config file could have more drivers per team than in-game, it would show non existant drivers)<br>
Changed how the drivers name are showed in the manufacturers championship (before: ['Habsburg', 'Schumacher'] after: Habsburg, Schumacher)<br>
Fixed inconsistency with the point system (it was EXTREMELY incorrect and inconsistent, specially with the manufacturers, now everything should be right);<br>
Added an Icon.

## Planned Changes
show winners after the race;<br>
make the GUI less shit;<br>

## About teams.json
As of now, you just need to change the file if you want to change the team a driver represent or if you want to add a name, in-game names still need to be in the file (otherwise they wont appear), put you dont need to keep 1:1 (so if of the 36 dafault drivers you only want to race with 26, you will only need to add yourself to the file, no need to remove anything)