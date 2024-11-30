import os
import pickle
import json
import openpyxl
import pandas as pd

from datetime import datetime
from fastparquet import write
from f1_23_telemetry.listener import TelemetryListener
from openpyxl.utils.cell import get_column_letter, column_index_from_string

from Classes.Driver import Driver
from Classes.Session import Session



class Telemetry:

    def __init__(self):
        self._is_listening = True

        self._drivers: dict[int, Driver]  = {}
        self._session: Session = Session()

        self._config = self._load_config()
        self._listener = self._get_listener()

        self._lap_data_counter = 0
        self._telemetry_data_counter = 0

        self._telemetry_read = True
        self.session_ended = False

        self.lap_data = pd.DataFrame(columns=['Lap',
                                              'Driver',
                                              'Current Lap Time',
                                              'Lap Distance',
                                              'Position',
                                              'Total Distance',
                                              'Sector',
                                              'Driver Status',
                                              'Result Status'])
        
        self.car_data = pd.DataFrame(columns=['Driver',
                                              'Speed',
                                              'Throttle',
                                              'Steer',
                                              'Brake',
                                              'Clutch',
                                              'Gear',
                                              'Engine RPM',
                                              'DRS',
                                              #'tyre surface temp',
                                              #'tyre inner temp'
                                              ])

    def _load_config(self):
        with open('Utility/configurations.json', 'r') as f:
            return json.load(f)
        
    def _get_listener(self):
        try:
            print('Starting listener on localhost:20777')
            return TelemetryListener()
        except OSError as exception:
            print(f'Unable to setup connection: {exception.args[1]}')
            print('Failed to open connector, stopping.')
            exit(127)

    def _start(self):

        try:
            while self._is_listening:

                self.packet = self._listener.get().to_dict()

                if not self._session.finished and 'session_type' in self.packet:
                    self._session.set_session_info(self.packet, self._config)
                    self.session_ended = False

                if ('event_string_code' in self.packet or 'classification_data' in self.packet) and not self.session_ended:
                    
                    if 'classification_data' in self.packet:
                        string_code = 'SEND'
                    else:
                        string_code = ''.join([chr(i) for i in self.packet['event_string_code']])

                    if string_code == 'SEND':
                        print('Session ended')
                        self._session.export_session(self._session, self._session.folder)
                        self._drivers[0].export_session(self._drivers, self._session.folder)

                        with open(f"{self._session.folder}/lap_data.pkl", 'wb') as file:
                            pickle.dump(self.lap_data, file)

                        with open(f"{self._session.folder}/car_data.pkl", 'wb') as file:
                            pickle.dump(self.car_data, file)

                        for idx, driver in self._drivers.items():
                            driver.reset_driver()
                        
                        if self._session.session_type == "Race":
                            self._is_listening = False
                        else:
                            self._session.reset_session()

                        self.session_ended = True

                if 'participants' in self.packet:
                    data = self.packet['participants']

                    for idx, driver_data in enumerate(data):
                        driver = Driver()
                        driver.id = idx
                        driver.set_driver_info(driver_data, self._config)
                        self._drivers[idx] = driver

                if 'lap_data' in self.packet:
                    lap_telem_data = self.packet['lap_data']
                    rows = [[self._drivers[idx].name, lap_data['current_lap_num'], lap_data['current_lap_time_in_ms'], 
                             lap_data['lap_distance'], lap_data['car_position'],lap_data['total_distance'], lap_data['sector'], 
                             self._config['driver_status'][str(lap_data['driver_status'])], 
                             self._config['result_status'][str(lap_data['result_status'])]]
                             for idx, lap_data in enumerate(lap_telem_data)]
                    
                    df_new_data = pd.DataFrame(rows, columns=['Driver', 'Lap', 'Current Lap Time', 'Lap Distance', 'Position', 'Total Distance', 'Sector', 'Driver Status', 'Result Status'])
                    self.lap_data = pd.concat([self.lap_data, df_new_data], ignore_index=True)

                    # if self._lap_data_counter > self._telemetry_data_counter:
                    #     self._telemetry_read = False

                    # elif self._lap_data_counter < self._telemetry_data_counter:
                    #    self.lap_data.loc[len(self.lap_data)] = [None] * len(self.lap_data.columns)
                    #    self._lap_data_counter += 1
                       
                    # for idx, lap_data in enumerate(data):
                    #     row = self._drivers[idx].set_lap_data(lap_data, self._config)
                    #     #self.lap_data.loc[self._lap_data_counter] = row
                    #     self.lap_data.loc[len(self.lap_data)] = row
                    
                    self._lap_data_counter += 1
                    #print(f"Lap data - {self._lap_data_counter}")

                if 'car_telemetry_data' in self.packet:
                    car_telem_data = self.packet['car_telemetry_data']
                    rows = [[self._drivers[idx].name, data['speed'], data['throttle'], data['steer'], data['brake'], data['clutch'], data['gear'], data['engine_rpm'], data['drs']]
                        for idx, data in enumerate(car_telem_data)
                    ]

                    df_new_data = pd.DataFrame(rows, columns=["Driver", "Speed", "Throttle", "Steer", "Brake", "Clutch", "Gear", "Engine_rpm", "DRS"])
                    self.car_data = pd.concat([self.car_data, df_new_data], ignore_index=True)


                    # # if not self._telemetry_read:
                    # #     self.car_data.loc[len(self.car_data)] = [None] * len(self.car_data.columns)
                    # #     self._telemetry_data_counter += 1
                    # #     self._telemetry_read = True

                    # for idx, car_telemetry_data in enumerate(car_telem_data):
                        
                    #     driver = self.name
                    #     speed = car_telemetry_data['speed']
                    #     throttle = car_telemetry_data['throttle']
                    #     steer = car_telemetry_data['steer']
                    #     brake = car_telemetry_data['brake']
                    #     clutch = car_telemetry_data['clutch']
                    #     gear = car_telemetry_data['gear']
                    #     engine_rpm = car_telemetry_data['engine_rpm']
                    #     drs = car_telemetry_data['drs']
                    #     row = [driver, speed, throttle, steer, brake, clutch, gear, engine_rpm, drs]
                    #     self.car_data.loc[len(self.car_data)] = row

                        #row = self._drivers[idx].set_car_telemetry_data(car_telemetry_data, self._config)
                        #self.car_data.loc[len(self.car_data)] = row

                    self._telemetry_data_counter += 1
                    #print(f"Telemetry data - {self._telemetry_data_counter}")
                        

                
                
        except KeyboardInterrupt:
            print('Stopping listener')
            

if __name__ == '__main__':
    client = Telemetry()
    client._start()
    print('Listener stopped')
    print(f"Lap data - {client._lap_data_counter}")
    print(f"Car Telemetry data - {client._telemetry_data_counter}\n")
    