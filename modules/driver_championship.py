import modules.acLap as acLap
import sqlite3
import re

def start_driver_champ():
    car_list = [players['car'] for players in acLap.get_timer_race_data()]
    player_list = [players['name'] for players in acLap.get_timer_race_data()]
    nice = list(zip(player_list, car_list, [0] * len(player_list)))
    with acLap.db_manager() as con:
        cur = con.cursor()
        try:
            cur.execute('SELECT COUNT(*) FROM champ_data')
        except sqlite3.OperationalError:
            cur.execute('CREATE TABLE IF NOT EXISTS champ_data (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, car TEXT NOT NULL, category TEXT, points INTEGER)')
        else:
            if cur.fetchone()[0] == 0:
                cur.executemany('INSERT INTO champ_data (name, car, points) VALUES (?, ?, ?)', nice)
                for i in range(len(player_list)):
                    if ('gt3' in car_list[i]) or ('gtm' in car_list[i]):
                        cur.execute('UPDATE champ_data SET category = ? WHERE car = ?', ('GT3', car_list[i]))
                    else:
                        cur.execute('UPDATE champ_data SET category = ? WHERE car = ?', ('LMH', car_list[i]))

def get_driver_points():
    with acLap.db_manager() as con:
        cur = con.cursor()
        cur.execute('SELECT name, points FROM champ_data')
        return cur.fetchall()
    
def get_driver_class():
    with acLap.db_manager() as con:
        cur = con.cursor()
        cur.execute('SELECT name, category FROM champ_data')
        result = cur.fetchall()
        return result
    
# Function that returns a tuple with the pole of both GT3 and LMH.
def get_pole(race_result):
    player_list = [players['name'] for players in acLap.get_timer_race_data()]
    # Gets the raw qualification times from Content Manager
    raw_quali_times = [session['time'] for session in acLap.get_raw_race_data()['sessions'][0]['bestLaps']]

    # 'Unites' the raw quali times with their respective driver.
    quali_session = list(zip(player_list, raw_quali_times))

    # List used to separate drivers between class.
    lap_times = [[],[]]

    # List of drivers separated by class.
    ordered_list = arrange_driver_position(race_result)

    # Iterates through both classes.
    for category in range(len(ordered_list)):
        # Iterates through every driver present in ordered_list
        for driver in ordered_list[category]:
            # Iterates through every driver in quali_session
            for name in quali_session:
                # If the names of the driver in ordered_list match the driver in quali_session
                if driver[0] == name[0]:
                    # It appends the driver and time to the new lap time list in it's respective category, 0 is GT3 and 1 is LMH.
                    lap_times[category].append(name)
        # Sorts the drivers in each class by their lap time.
        lap_times[category] = sorted(lap_times[category], key=lambda x: x[1])

    # returns just the fastest of each class because.
    return lap_times[0][0], lap_times[1][0]
    
# Function that does a bunch of random things and somehow is the heart and soul of the code.
def arrange_driver_position(final_positions):
    # List of points (duh, but depending on the race their value change).
    points = acLap.calculate_points()

    # Will be used later to separate both classes.
    ordered_list = [[],[]]

    # List with the final standing on each driver (not separated by class).
    position_list = [name[0] for name in sorted(final_positions, key=lambda x: x[1])]

    # List of each driver and their class.
    driver_class = get_driver_class()

    # Iterates through all drivers in position list.
    for name in position_list:
        #  Iterates through all drivers in driver_class
        for driver in driver_class:
            # If their name match
            if driver[0] == name:
                # Check what is the driver class.
                if driver[1] == 'GT3':
                    # And appends it to the correct list.
                    ordered_list[0].append(name)
                else:
                    ordered_list[1].append(name)

    # Unites every driver with how much points they should get.
    ordered_list = [list(zip(category, points)) for category in ordered_list]

    return ordered_list

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