import sqlite3
import acLap
import json
import modules.driver_championship as driver_championship
from pathlib import Path

# gets the raw data from the teams.json file
def get_teams_data():
    project_root = Path(__file__).resolve().parent.parent
    teams_path = project_root / 'config' / 'teams.json'
    with open(teams_path, 'r') as n:
        return json.load(n)
    
# uses the data from the teams.json file to create and populate the teams database
def create_teams_champ(teams_data):
    with acLap.db_manager() as con:
        cur = con.cursor()
        cur.execute('SELECT COUNT(*) FROM teams_db')
        if cur.fetchone()[0] == 0:
            cur.execute('CREATE TABLE IF NOT EXISTS teams_db (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, drivers TEXT NOT NULL, points INT)')
            for teams in teams_data:
                cur.execute('INSERT INTO teams_db (name, drivers, points) VALUES (?, ?, ?)', (teams['name'], str(teams['drivers']), str(0)))

def get_teams() -> tuple:
    with acLap.db_manager() as con:
        cur = con.cursor()
        cur.execute('SELECT name, drivers FROM teams_db')
        return cur.fetchall()
    
def get_team_points() -> tuple:
    with acLap.db_manager() as con:
        cur = con.cursor()
        cur.execute('SELECT name, points FROM teams_db')
        return cur.fetchall()
    
# Gets a list of teams and its drivers and uses ordernate_position() to check which driver from the team finished first.
# As per WEC rules, teams only get rewarded points for the driver on the better position.
def set_eligible_drivers(race_result):
    teams = get_teams()
    ordered_driver_lists = driver_championship.arrange_driver_position(race_result)

    eligible_drivers = [[],[]]

    # Populates the 2 driver lists with tuples based on the driver with the best position on each team.
    for category in range(len(ordered_driver_lists)):
        for team in teams:
            for driver in ordered_driver_lists[category]:
                if driver in team[1]:
                    eligible_drivers[category].append([team[0], driver])
                    continue
    
    return eligible_drivers

# This function creates a list of dicts with the keys 'team', 'driver' and 'points', based on the eligible driver for points on a team;
# And how many points he scored on a the last race;
def assign_team_points(ordered_position, teams, points: list) -> list:
    team_driver_points = []
    point_itr = 0
    # ordered_position is a list of lists where [0] is a list of GT3 drivers and [1] is a list of LMH drivers.
    for category in range(len(ordered_position)):
        # Loops through all the drivers in the category.
        for driver in ordered_position[category]:
            # Loops through all the teams in their respective category.
            for team in teams[category]:
                # If a driver on the list of eligible drivers is on a team, it appends to the dict all the necessary info.
                if driver == team[1]:
                    team_driver_points.append({
                        "name": team[0],
                        "driver": driver,
                        "points": points[point_itr]
                    })
            # This iterator is exclusive to the points list because in WEC teams/drivers get awarded points based on their class standing not overall standing;
            if point_itr >= len(teams[category]):
                point_itr = 0
            else:
                point_itr += 1
    return team_driver_points