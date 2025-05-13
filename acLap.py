import json
import sqlite3
from pathlib import Path
import os
from dotenv import load_dotenv
import math

load_dotenv()

# Opens the folder where content manager stores the race result, picks the latest files and returns the opened files as a dict;
def get_raw_race_data():
    folder = Path(os.getenv('CM_RESULTS_PATH'))
    files = list(folder.glob('*'))
    latest_file = max(files, key=lambda f: f.stat().st_mtime)
    with open(latest_file, 'r') as data:
        return json.load(data)
    
def get_teams_data():
    with open('teams.json', 'r') as n:
        return json.load(n)
    
def create_teams_champ(teams_data):
    with db_manager() as con:
        cur = con.cursor()
        cur.execute('SELECT COUNT(*) FROM teams_db')
        if cur.fetchone()[0] == 0:
            cur.execute('CREATE TABLE IF NOT EXISTS teams_db (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, drivers TEXT NOT NULL, points INT)')
            for teams in teams_data:
                cur.execute('INSERT INTO teams_db (name, drivers, points) VALUES (?, ?, ?)', (teams['name'], str(teams['drivers']), str(0)))

def get_teams():
    with db_manager() as con:
        cur = con.cursor()
        cur.execute('SELECT name, drivers FROM teams_db')
        return cur.fetchall()
    
def set_team_point(race_result):
    teams = get_teams()
    ordered_GT3 = ordernate_position(race_result)[0]
    ordered_LMH = ordernate_position(race_result)[1]

    eligible_for_points_GT3 = []
    eligible_for_points_LMH = []
    for i in range(len(teams)):
        for j in ordered_GT3:
            if j in teams[i][1]:
                eligible_for_points_GT3.append((teams[i][0], j))
                continue
        for j in ordered_LMH:
            if j in teams[i][1]:
                eligible_for_points_LMH.append((teams[i][0], j))
                continue

    return [eligible_for_points_GT3, eligible_for_points_LMH]


def db_manager():
    con = sqlite3.connect('acLap_database.db')            
    return con

"""
Gets the latest race result (presumably the first on the championship) and populates the main db with name, car and points (0 atm)
Also separes each car in their respective category based on their id
"""
def start_champ(player_list: list, car_list: list):
    # Unites both lists and the points into a single tuple so i can use executemany instead of execute.
    nice = list(zip(player_list, car_list, [0] * len(player_list)))
    with db_manager() as con:
        cur = con.cursor()
        cur.execute('SELECT COUNT(*) FROM champ_data')
        if cur.fetchone()[0] == 0:
            cur.execute('CREATE TABLE IF NOT EXISTS champ_data (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, car TEXT NOT NULL, category TEXT, points INTEGER)')
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
        return result
    
"""
Gets the value of the race positions, orders them (without separating into categories at first), them separates at their categories and orders them inside their categories.
Returns both gt3 and lmh lists in a ordered manner (index 0 was the driver with the best position in their category)
"""
def ordernate_position(final_positions):
    # Gets a list of the final standings from the .json (CM stores position of the drivers based on a internal list of driver in that event), so if driver n11 finished first, the number 11 would be index 0
    position_list = []
    GT3_list = []
    LMH_list = []
    """
    The way CM stores the data is why we need to do this, get the list from positions and cross-reference it with a list of the players in the event, if they match, the player name is stored in another list.
    This loop creates the overall position list not separated by their categories.
    """
    position_list = [name[0] for name in sorted(final_positions, key=lambda x: x[1])]
    # Gets the categories so we can separate the standings list.
    driver_category = get_category()

    """
    Loops through the length of position list (as it has all drivers inside), while comparing very name in driver_category with the current name in position list;
    If the names match, it checks which is the category of the driver, and after all iterations, we have 2 ordered lists of positions relative to their current categories.
    """
    for i in range(len(position_list)):
        for j in range(len(position_list)):
            if driver_category[j][0] == position_list[i]:
                if driver_category[j][1] == 'GT3':
                    GT3_list.append(position_list[i])
                else:
                    LMH_list.append(position_list[i])

    return (GT3_list, LMH_list)

# Determines how much points each player should win based on their category and assigns them to the players through a simple loop with switching conditional.
def award_points(ordered_position, track, poles, teams):
    GT3_teams = teams[0]
    LMH_teams = teams[1]

    GT3_position = ordered_position[0]
    LMH_position = ordered_position[1]

    # This 'Aligns' the players with how much points they should win after a race.
    points = [25,18,15,12,10,8,6,4,2,1]

    if 'lemans' in track:
        points = [p * 2 for p in points ]
    elif ('losail' in track) or ('bahrain' in track):
        points = [int(math.ceil(p * 1.5)) for p in points]

    GT3_position = list(zip(GT3_position, points))
    LMH_position = list(zip(LMH_position, points))

    print((GT3_teams))
    print((GT3_position))
    # This is the modifier which determines if it should change the points of the LMH class or the GT3 class.
    mod = 0
    current_points = get_points()
    # This acts as a placeholder and changes its value to one of the 2 standing lists based on the mod value
    cur_list = []
    while mod < 2:
        if mod == 1:
            cur_list = LMH_position
        else:
            cur_list = GT3_position
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

def get_pole(player_list, race_result):
    # Gets raw quali session data (a dict with car_id, time and lap)
    quali_session = get_raw_race_data()['sessions'][0]['bestLaps']
    # Filters the raw data and gets only the times
    raw_quali_times = [session['time'] for session in quali_session]
    # since the dict is ordered by car_id, it will be in the same order as the player list, so unite them to get a list of ('Player Name', 'Best Quali Time')
    quali_session = list(zip(player_list, raw_quali_times))

    # Gets the list of GT3 and LMH Drivers (honestly, dont know why i used this and not get_category(), but maybe because this returns 2 lists already filtered).
    ordered_list = ordernate_position(race_result)

    # Separates the quali_session list in 2 based on driver category.
    gt3_laps = [time for time in quali_session if time[0] in ordered_list[0]]
    lmh_laps = [time for time in quali_session if time[0] in ordered_list[1]]

    # Sorts each list by their best lap time.
    gt3_laps = sorted(gt3_laps, key=lambda x: x[1])
    lmh_laps = sorted(lmh_laps, key=lambda x: x[1])

    # returns only the first of each
    return gt3_laps[0][0], lmh_laps[0][0]

def main():
    """
    get the results.json from the timer app in assetto corsa main folder (required since races are time based, not position based)
    and since when you quit out before a race ends in ac, it doesnt record de position.
    """
    with open(os.getenv('TIMER_RESULTS_PATH'), 'r') as n:
        race_data = json.load(n)
    
    car_list = [players['car'] for players in race_data]
    player_list = [players['name'] for players in race_data]
    race_result = [(players['name'], players['position']) for players in race_data]

    start_champ(player_list, car_list)
    create_teams_champ(get_teams_data())
    teams = set_team_point(race_result)

    ordered_positions = ordernate_position(race_result)
    track = race_data[0]['track']
    poles = get_pole(player_list, race_result)

    award_points(ordered_positions, track, poles, teams)

if __name__ == '__main__':
    main()