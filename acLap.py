import json
import sqlite3
from pathlib import Path
import os
from dotenv import load_dotenv
import math

load_dotenv()

# Opens the folder where content manager stores the race result, picks the latest files and returns the opened files as a dict;
def get_race_data():
    folder = Path(os.getenv('RESULTS_PATH'))
    files = list(folder.glob('*'))
    latest_file = max(files, key=lambda f: f.stat().st_mtime)
    with open(latest_file, 'r') as data:
        return json.load(data)

# Creates and connects to the main database, returns the connections (so i dont need to write sqlite3... everytime i do something on the db)
def db_manager():
    con = sqlite3.connect('acLap_database.db')            
    return con

# Creates the main championship table (could be together with db_manager)
def create_champ_db():
        with db_manager() as con:
            cur = con.cursor()
            cur.execute('CREATE TABLE IF NOT EXISTS champ_data (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, car TEXT NOT NULL, category TEXT, points INTEGER)')

# Gets the latest race result (presumably the first on the championship) and populates the main db with name, car and points (0 atm)
# Also separes each car in their respective category based on their id (luckilly, every gt3 car i used on the championship has gtm or gt3 in their name, otherwise i would need to hardcode them to the db)
def start_champ(player_list: list, car_list: list):
    # Unites both lists and the points into a single tuple so i can use executemany instead of execute.
    nice = list(zip(player_list, car_list, [0] * len(player_list)))
    with db_manager() as con:
        cur = con.cursor()
        cur.executemany('INSERT INTO champ_data (name, car, points) VALUES (?, ?, ?)', nice)
        for i in range(len(player_list)):
            # Separates the cars into their categories.
            if ('gt3' in car_list[i]) or ('gtm' in car_list[i]):
                cur.execute('UPDATE champ_data SET category = ? WHERE car = ?', ('GT3', car_list[i]))
            else:
                cur.execute('UPDATE champ_data SET category = ? WHERE car = ?', ('LMH', car_list[i]))

# Returns the name and the current points from the driver.
def get_points():
    with db_manager() as con:
        cur = con.cursor()
        cur.execute('SELECT name, points FROM champ_data')
        result = cur.fetchall()
        return result

# Returns the name and the category the drivers are competing.
def get_category():
    with db_manager() as con:
        cur = con.cursor()
        cur.execute('SELECT name, category FROM champ_data')
        result = cur.fetchall()
        # print(len(result))
        return result
    
# Gets the value of the race positions, orders them (without separating into categories at first), them separates at their categories and orders them inside their categories.
# Returns both gt3 and lmh lists in a ordered manner (index 0 was the driver with the best position in their category)
def ordernate_position(player_list, race_data):
    # Gets a list of the final standings from the .json (CM stores position of the drivers based on a internal list of driver in that event), so if driver n11 finished first, the number 11 would be index 0
    race_results = race_data['sessions'][1]['raceResult']
    position_list = []
    GT3_list = []
    LMH_list = []
    # The way CM stores the data is why we need to do this, get the list from positions and cross-reference it with a list of the players in the event, if they match, the player name is stored in another list.
    # This loop creates the overall position list not separated by their categories.
    for un_standings in race_results:
        for positions in player_list:
            if un_standings == player_list.index(positions):
                position_list.append(positions)

    # print(position_list)
    # Gets the categories so we can separate the standings list.
    driver_category = get_category()
    #print(len(driver_category))
    #print(len(position_list))

    # Loops through the length of position list (as it has all drivers inside), while comparing very name in driver_category with the current name in position list;
    # If the names match, it checks which is the category of the driver, and after all iterations, we have 2 ordered lists of positions relative to their current categories.
    for i in range(len(position_list)):
        for j in range(len(position_list)):
            if driver_category[j][0] == position_list[i]:
                if driver_category[j][1] == 'GT3':
                    GT3_list.append(position_list[i])
                else:
                    LMH_list.append(position_list[i])
    return (GT3_list, LMH_list)


# Determines how much points each player should win based on their category and assigns them to the players through a simple loop with switching conditional.
def award_points(GT3_list, LMH_list, track, poles):
    # This 'Aligns' the players with how much points they should win after a race.
    points = [25,18,15,12,10,8,6,4,2,1]
    if 'lemans' in track:
        points = [p * 2 for p in points ]
    if ('losail' in track) or ('bahrain' in track):
        points = [int(math.ceil(p * 1.5)) for p in points]

    GT3_list = list(zip(GT3_list, points))
    LMH_list = list(zip(LMH_list, points))

    # This is the modifier which determines if it should change the points of the LMH class or the GT3 class.
    mod = 0
    current_points = get_points()
    # This acts as a placeholder and changes its value to one of the 2 standing lists based on the mod value
    cur_list = []
    while mod < 2:
        if mod == 1:
            cur_list = LMH_list
        else:
            cur_list = GT3_list
        for i in range(len(current_points)):
            for j in range(len(cur_list)):
                if current_points[i][0] in cur_list[j]:
                    with db_manager() as con:
                        cur = con.cursor()
                        if cur_list[j][0] in poles:
                            cur.execute('UPDATE champ_data SET points = ? WHERE name = ?', (current_points[i][1] + cur_list[j][1] + 1, current_points[i][0]))
                        # Assign the players theirs points based on their current points + their latest standing points
                        else:
                            cur.execute('UPDATE champ_data SET points = ? WHERE name = ?', (current_points[i][1] + cur_list[j][1], current_points[i][0]))
        mod += 1

def get_pole(race_data, player_list):
    bestlaps = race_data['sessions'][0]['bestLaps']
    lap_times = []
    for i in range(len(bestlaps)):
        lap_times.append(bestlaps[i]['time'])

    driver_list = []
    bestlaps = list(zip(player_list, lap_times))
    for i in range(len(bestlaps)):
        driver_list.append(bestlaps[i][0])
    ordered_list = ordernate_position(driver_list, race_data)

    gt3_laps = []
    lmh_laps = []

    for i in range(len(bestlaps)):
        for j in range(len(ordered_list[0])):
            if ordered_list[0][j] == bestlaps[i][0]:
                gt3_laps.append(bestlaps[i])

    for i in range(len(bestlaps)):
        for j in range(len(ordered_list[1])):
            if ordered_list[1][j] == bestlaps[i][0]:
                lmh_laps.append(bestlaps[i])

    gt3_laps = sorted(gt3_laps, key=lambda x: x[1])
    lmh_laps = sorted(lmh_laps, key=lambda x: x[1])

    return gt3_laps[0][0], lmh_laps[0][0]

def main():
    create_champ_db()
    race_data = get_race_data()
    track = race_data['track']
    #print(bestlaps)
    car_list = []
    player_list = []

    # Creates the inital and base lists of players and their cars.
    for players in race_data['players']:
        player_list.append(players['name'])
        car_list.append(players['car'])

    # Checks if the db is empty aka if it is the first time being started.
    with db_manager() as con:
        cur = con.cursor()
        cur.execute('SELECT COUNT(*) FROM champ_data')
        if cur.fetchone()[0] == 0:
            start_champ(player_list, car_list)

    poles = get_pole(race_data, player_list)
    print(poles)
    position_lists = ordernate_position(player_list, race_data)
    award_points(position_lists[0], position_lists[1], track, poles)

if __name__ == '__main__':
    main()