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

        self.session_ended = False

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

                #if ('event_string_code' in self.packet or 'classification_data' in self.packet) and not self.session_ended:
                if 'classification_data' in self.packet and not self.session_ended:
                    
                    if 'classification_data' in self.packet:
                        data = self.packet['classification_data']

                        for idx, driver_data in enumerate(data):
                            driver = self._drivers[idx]
                            driver.set_classification_data(driver_data)

                        string_code = 'SEND'
                    else:
                        string_code = ''.join([chr(i) for i in self.packet['event_string_code']])

                    if string_code == 'SEND':
                        print('Session ended')
                        self._session.export_session(self._session, self._session.folder)
                        self._drivers[0].export_session(self._drivers, self._session.folder)

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

                if 'lap_history_data' in self.packet:
                    data = self.packet['lap_history_data']
                    driver_id = self.packet['car_idx']

                    for lap_nr, lap in enumerate(data):
                        driver = self._drivers[driver_id]
                        driver.set_lap_times(lap_nr+1, lap['lap_time_in_ms'])


                

        except KeyboardInterrupt:
            print('Stopping listener')
            

if __name__ == '__main__':
    client = Telemetry()
    client._start()
    print('Listener stopped')
    