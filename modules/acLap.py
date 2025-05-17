import json
import sys
import sqlite3
from pathlib import Path
import os
from dotenv import load_dotenv
import math
import modules.driver_championship as driver_championship, modules.manu_championship as manu_championship
import re

env_path= Path('config') / '.env'
load_dotenv(dotenv_path=env_path)

def db_manager():
    con = sqlite3.connect('acLap_database.db')            
    return con

# Opens the folder where content manager stores the race result, picks the latest files and returns the opened files as a dict;
def get_raw_race_data():
    folder = Path.home() / "AppData" / "Local" / "AcTools Content Manager" / "Progress" / "Sessions"
    files = list(folder.glob('*'))
    latest_file = max(files, key=lambda f: f.stat().st_mtime)
    with open(latest_file, 'r') as data:
        return json.load(data)
    
def get_timer_race_data():
    json_path = Path.home() / 'Documents' / 'Ac Timer' / 'Results.json'
    with open(json_path, 'r') as n:
        return json.load(n)
    
# This function calculates how many points each race is worth.
def calculate_points(track: str) -> list:
    base_points = [25,18,15,12,10,8,6,4,2,1]

    # This is the point modifier for the longer races.
    if 'lemans' in track:
        base_points = [p * 2 for p in base_points ]
    elif ('losail' in track) or ('bahrain' in track):
        base_points = [int(math.ceil(p * 1.5)) for p in base_points]
    return base_points

# This function updates the points on the database for both the drivers and manufacturers of both categories.
def update_db_points(assigned_team_points, driver_points, poles, isDriver = True):
    # Checks whether the data received by this function should be interpreted as drivers or manufacturers.
    if isDriver:
        database = 'champ_data'
        current_points = driver_championship.get_driver_points()
        current_competitor_list = driver_points
    else:
        database = 'teams_db'
        current_points = manu_championship.get_team_points()
        current_competitor_list = assigned_team_points

    # Sums the current total championship points with the points received from the last race.
    for competitor in current_competitor_list:
        for points in current_points:
            if competitor['name'] == points[0]:
                competitor['points'] += points[1]

    # Updates the database with the points, also which driver got pole and awards him and his team with +1 point.
    for competitor in current_points:
        for name in current_competitor_list:
            # Checks if the current competitor exists in the database (theorically it cant be false)
            if name['name'] in competitor[0]:
                with db_manager() as con:
                    cur = con.cursor()
                    if (name.get('name') in poles) or (name.get('driver') in poles):
                        cur.execute(f"UPDATE {database} SET points = ? WHERE name = ?", (name['points'] + 1, name['name']))
                    else:
                        cur.execute(f"UPDATE {database} SET points = ? WHERE name = ?", (name['points'], name['name']))
    # Calls on itself so i dont need to call it 2 times.
    if isDriver:
        update_db_points(assigned_team_points, driver_points, poles, False)

# really only a 'wrapper' for other functions, gets some basic data required by other functions and calls them on the right order.
def award_points(ordered_position, track, poles, teams):
    points = calculate_points(track)
    driver_points = []
    points_itr = 0

    # Unites the driver names with their points in a list of dicts.
    for category in range(len(ordered_position)):
        for driver in ordered_position[category]:
            if (category == 1) and (driver == ordered_position[category][0]):
                points_itr = 0
            driver_points.append({
                "name": driver,
                "points": points[points_itr]
            })
            points_itr += 1

    assigned_team_points = manu_championship.assign_team_points(ordered_position, teams, points)
    update_db_points(assigned_team_points, driver_points, poles)

def reset_championships():
    with db_manager() as con:
        cur = con.cursor()
        cur.execute('DELETE FROM champ_data')
        cur.execute('DELETE FROM teams_db')
        con.commit()

def first_start():
    race_data = get_timer_race_data()
    car_list = [players['car'] for players in race_data]
    player_list = [players['name'] for players in race_data]
    driver_championship.start_driver_champ(player_list, car_list)
    manu_championship.create_teams_champ(manu_championship.get_teams_data())

# really only a "Wrapper" for other functions, get some basic data and calls the other functions on the right order.
def start_championship():
    # get the results.json from the timer app in assetto corsa main folder (required since races are time based, not position based).
    race_data = get_timer_race_data()
    # gets basic data and stores them in lists, required for other functions
    car_list = [players['car'] for players in race_data]
    player_list = [players['name'] for players in race_data]
    race_result = [(players['name'], players['position']) for players in race_data]
    
    driver_championship.start_driver_champ(player_list, car_list)
    manu_championship.create_teams_champ(manu_championship.get_teams_data())

    # starts both the drivers and the manufacturers championship.
    teams = manu_championship.set_eligible_drivers(race_result)

    ordered_positions = driver_championship.arrange_driver_position(race_result)
    track = race_data[0]['track']
    poles = driver_championship.get_pole(player_list, race_result)
    award_points(ordered_positions, track, poles, teams)

if __name__ == '__main__':
    print('Something Went Wrong')