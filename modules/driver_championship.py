import modules.acLap as acLap
import sqlite3
import re

# Gets the latest race result (presumably the first on the championship) and populates the main db with name, car and points (0 atm)
# Also separes each car in their respective category based on their id
def start_driver_champ(player_list: list, car_list: list):
    # Unites both lists and the points into a single tuple so i can use executemany instead of execute.
    nice = list(zip(player_list, car_list, [0] * len(player_list)))
    with acLap.db_manager() as con:
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
def get_driver_points():
    with acLap.db_manager() as con:
        cur = con.cursor()
        cur.execute('SELECT name, points FROM champ_data')
        return cur.fetchall()
    
# Returns the name and the category of the drivers.
def get_driver_category():
    with acLap.db_manager() as con:
        cur = con.cursor()
        cur.execute('SELECT name, category FROM champ_data')
        result = cur.fetchall()
        return result
    
def get_pole(player_list, race_result):
    # Gets raw quali session data (a dict with car_id, time and lap)
    quali_session = acLap.get_raw_race_data()['sessions'][0]['bestLaps']
    # Filters the raw data and gets only the times
    raw_quali_times = [session['time'] for session in quali_session]
    # since the dict is ordered by car_id, it will be in the same order as the player list, so unite them to get a list of ('Player Name', 'Best Quali Time')
    quali_session = list(zip(player_list, raw_quali_times))

    # Gets the list of GT3 and LMH Drivers (honestly, dont know why i used this and not get_category(), but maybe because this returns 2 lists already filtered).
    ordered_list = acLap.driver_championship.arrange_driver_position(race_result)

    # Separates the quali_session list in 2 based on driver category.
    gt3_laps = [time for time in quali_session if time[0] in ordered_list[0]]
    lmh_laps = [time for time in quali_session if time[0] in ordered_list[1]]

    # Sorts each list by their best lap time.
    gt3_laps = sorted(gt3_laps, key=lambda x: x[1])
    lmh_laps = sorted(lmh_laps, key=lambda x: x[1])

    # returns only the first of each
    return gt3_laps[0][0], lmh_laps[0][0]
    
# Gets the value of the race positions, orders them (without separating into categories at first), them separates at their categories and orders them inside their categories.
# Returns both gt3 and lmh lists in a ordered manner (index 0 was the driver with the best position in their category)
def arrange_driver_position(final_positions):
    # Gets a list of the final standings from the .json (CM stores position of the drivers based on a internal list of driver in that event), so if driver n11 finished first, the number 11 would be index 0
    position_list = []
    GT3_list = []
    LMH_list = []
    # The way CM stores the data is why we need to do this, get the list from positions and cross-reference it with a list of the players in the event, if they match, the player name is stored in another list.
    # This loop creates the overall position list not separated by their categories.
    position_list = [name[0] for name in sorted(final_positions, key=lambda x: x[1])]
    # Gets the categories so we can separate the standings list.
    driver_category = get_driver_category()

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

def get_drivers_data():
    with acLap.db_manager() as con:
        cur = con.cursor()
        cur.execute('SELECT name, car, category, points FROM champ_data')
        driver_data = cur.fetchall()
        driver_data = [list(item) for item in driver_data]
        for car_name in driver_data:
            car_name[1] = re.sub('[_]|(rss|gtm|gt3|trr|lmh|lmdh)', ' ', car_name[1]).strip().title()
            car_name[1] = re.sub('(  |  .)', '', car_name[1])
        return driver_data