import pickle
import pandas as pd

class Driver:

    def __init__(self):
        self.id = 0
        self.name = ''
        self.team = ''
        self.nationality = ''
        self.car_nr = 0

        self.classification_data =  {
            'grid_position': 0,
            'final_position': 0,
            'best_lap_time': 0,
            'points': 0,
            'result_status': 0,
            'total_race_time': 0,
            'laps_driven': 0,
            'tyres_visual': [],
            'tyres_end_laps': []
        }

        self.lap_times = {}
    
    def __str__(self):
        return f'{self.name}\n - {self.team}\n - {self.nationality}\n - {self.car_nr}\n'
    
    @staticmethod
    def export_session(obj, folder_path: str):
        with open(f"{folder_path}/drivers.pkl", 'wb') as file:
            pickle.dump(obj, file)

    def set_driver_info(self, driver_data, config):
        self.name = driver_data['name'] if driver_data['name'] != 'Player' else f"Player{self.id}"
        self.team = config['teams'][str(driver_data['team_id'])]
        self.nationality = config["nationality"][str(driver_data['nationality'])]
        self.car_nr = driver_data['race_number']

    def set_classification_data(self, classification_data):
        self.classification_data['grid_position'] = classification_data['grid_position']
        self.classification_data['final_position'] = classification_data['position']
        self.classification_data['best_lap_time'] = classification_data['best_lap_time_in_ms']
        self.classification_data['points'] = classification_data['points']
        self.classification_data['result_status'] = classification_data['result_status']
        self.classification_data['total_race_time'] = classification_data['total_race_time']
        self.classification_data['laps_driven'] = classification_data['num_laps']
        self.classification_data['tyres_visual'] = classification_data['tyre_stints_visual']
        self.classification_data['tyres_end_laps'] = classification_data['tyre_stints_end_laps']

    def set_lap_times(self, lap_nr, lap_time):
        self.lap_times.update({lap_nr: lap_time})

    def reset_driver(self):
        self.id = 0
        self.name = ''
        self.team = ''
        self.nationality = ''
        self.car_nr = 0

        self.classification_data =  {
            'grid_position': 0,
            'final_position': 0,
            'best_lap_time': 0,
            'points': 0,
            'result_status': 0,
            'total_race_time': 0,
            'laps_driven': 0,
            'tyres_visual': [],
            'tyres_end_laps': []
        }

        self.lap_times = {}

        