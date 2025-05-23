import json
import sqlite3
from pathlib import Path
from dotenv import load_dotenv
import math
import modules.driver_championship as driver_championship, modules.manu_championship as manu_championship

env_path= Path('config') / '.env'
load_dotenv(dotenv_path=env_path)

def db_manager():
    con = sqlite3.connect('acLap_database.db')            
    return con

def get_raw_race_data():
    folder = Path.home() / "AppData" / "Local" / "AcTools Content Manager" / "Progress" / "Sessions"
    files = list(folder.glob('*'))
    latest_file = max(files, key=lambda f: f.stat().st_mtime)
    with open(latest_file, 'r') as data:
        return json.load(data)
    
def calculate_points() -> list:
    track = get_raw_race_data()['track']

    # Look, i now this is dumb, but it works ok.
    base_points = [25,18,15,12,10,8,6,4,2,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

    if 'lemans' in track:
        base_points = [p * 2 for p in base_points ]
    elif ('losail' in track) or ('bahrain' in track):
        base_points = [int(math.ceil(p * 1.5)) for p in base_points]
    return base_points

def update_db_points(ordered_teams, ordered_drivers, poles, isDriver = True):
    # Creates a nice and tidy list of driver names and how many points they should earn.
    driver_points = []
    for category in ordered_drivers:
        for driver in category:
            driver_points.append({
                "name": driver[0],
                "points": driver[1]
            })

    # Decides how this function should interpret the received data.
    if isDriver:
        database = 'champ_data'
        current_points = driver_championship.get_driver_points()
        current_competitor_list = driver_points
    else:
        database = 'teams_db'
        current_points = manu_championship.get_team_points()
        current_competitor_list = ordered_teams

    # Sums the current total championship points with the points received from the last race.
    for competitor in current_competitor_list:
        for points in current_points:
            if competitor['name'] == points[0]:
                competitor['points'] += points[1]

    # Updates the database with the correct points, also checks if the driver was pole and gives him +1 point.
    for competitor in current_points:
        for name in current_competitor_list:
            if name['name'] in competitor[0]:
                with db_manager() as con:
                    cur = con.cursor()
                    if (name.get('name') in poles) or (name.get('driver') in poles):
                        cur.execute(f"UPDATE {database} SET points = ? WHERE name = ?", (name['points'] + 1, name['name']))
                    else:
                        cur.execute(f"UPDATE {database} SET points = ? WHERE name = ?", (name['points'], name['name']))

    # Calls on itself
    if isDriver:
        update_db_points(ordered_teams, driver_points, poles, False)

def reset_championships():
    with db_manager() as con:
        cur = con.cursor()
        cur.execute('DELETE FROM champ_data')
        cur.execute('DELETE FROM teams_db')
        con.commit()

def first_start():
    driver_championship.start_driver_champ()
    manu_championship.create_teams_champ(manu_championship.get_teams_data())

# really only a "Wrapper" for other functions, get some basic data and calls the other functions on the right order.
def start_championship():
    driver_list = [driver['name'] for driver in get_raw_race_data()['players']]
    pos_list = [time for time in get_raw_race_data()['sessions'][1]['raceResult']]


    race_result = []
    for position in pos_list:
        for driver in driver_list:
            if position == driver_list.index(driver):
                race_result.append((driver, pos_list.index(position)))

    # starts both the drivers and the manufacturers championship.
    driver_championship.start_driver_champ()
    manu_championship.create_teams_champ(manu_championship.get_teams_data())
    
    ordered_drivers = driver_championship.arrange_driver_position(race_result)
    poles = driver_championship.get_pole(race_result)
    ordered_teams = manu_championship.set_eligible_drivers(race_result)

    update_db_points(ordered_teams, ordered_drivers, poles)

if __name__ == '__main__':
    print('Something Went Wrong')