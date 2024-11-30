import pickle
import pandas as pd

class Driver:

    def __init__(self):
        self.id = 0
        self.name = ''
        self.team = ''
        self.nationality = ''
        self.car_nr = 0
    
    def __str__(self):
        return f'{self.name}\n - {self.team}\n - {self.nationality}\n - {self.car_nr}\n'
    
    @staticmethod
    def export_session(obj, folder_path: str):
        with open(f"{folder_path}/drivers.pkl", 'wb') as file:
            pickle.dump(obj, file)
        #print(f"Instance saved to {folder_path}/drivers.pkl\n")

    def set_driver_info(self, driver_data, config):
        self.name = driver_data['name'] if driver_data['name'] != 'Player' else f"Player{self.id}"
        self.team = config['teams'][str(driver_data['team_id'])]
        self.nationality = config["nationality"][str(driver_data['nationality'])]
        self.car_nr = driver_data['race_number']

    def set_lap_data(self, lap_data, config):
        lap = lap_data['current_lap_num']
        driver = self.name
        current_lap_time = lap_data['current_lap_time_in_ms']
        lap_distance = lap_data['lap_distance']
        position = lap_data['car_position']
        total_distance = lap_data['total_distance']
        sector = lap_data['sector']
        driver_status = config['driver_status'][str(lap_data['driver_status'])]
        result_status = config['result_status'][str(lap_data['result_status'])]

        row = [lap, driver, current_lap_time, lap_distance, position, total_distance, sector, driver_status, result_status]
        #self.lap_data_df.loc[len(self.lap_data_df)] = row

        return row
    
    def set_car_telemetry_data(self, car_telemetry_data, config):
        driver = self.name
        speed = car_telemetry_data['speed']
        throttle = car_telemetry_data['throttle']
        steer = car_telemetry_data['steer']
        brake = car_telemetry_data['brake']
        clutch = car_telemetry_data['clutch']
        gear = car_telemetry_data['gear']
        engine_rpm = car_telemetry_data['engine_rpm']
        drs = car_telemetry_data['drs']
        #tyres_surface_temperature = car_telemetry_data['tyres_surface_temperature']
        #tyres_inner_temperature = car_telemetry_data['tyres_inner_temperature']

        #row = [driver, speed, throttle, steer, brake, clutch, gear, engine_rpm, drs, tyres_surface_temperature, tyres_inner_temperature]
        row = [driver, speed, throttle, steer, brake, clutch, gear, engine_rpm, drs]

        return row
    

    def reset_driver(self):
        self.id = 0
        self.name = ''
        self.team = ''
        self.nationality = ''
        self.car_nr = 0

        self.lap_data = pd.DataFrame(columns=['Lap',
                                              'Driver',
                                              'Current Lap Time',
                                              'Lap Distance',
                                              'Position',
                                              'Total Distance',
                                              'Sector',
                                              'Driver Status',
                                              'Result Status'])

        