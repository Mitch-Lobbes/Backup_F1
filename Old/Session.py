from datetime import datetime
import pickle
import os

class Session:

    def __init__(self):
        self.n_laps = 0
        self.track = ''
        self.session_type = ''
        self.fastest_lap = 0
        self.track_length = 0
        self.n_drivers = 0
        self.map_segments = []
        self.finished = False

    def __str__(self):
        return f'{self.track}\n- {self.session_type}\n- {self.n_laps} laps\n- {self.track_length}m\n'

    def export_session(self, obj, folder_path: str):
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        with open(f"{folder_path}/session.pkl", 'wb') as file:
            pickle.dump(obj, file)

    def set_session_info(self, packet, config):
        self.session_type = config['session_types'][str(packet['session_type'])]
        self.track = config['tracks'][str(packet['track_id'])]
        self.n_laps = packet['total_laps']
        self.track_length = packet['track_length']

        self.folder = f"Results/{self.session_type}/{self.track} {datetime.now().strftime('%d-%m-%Y (%Hh%M)')}"

        self.finished = True

    def reset_session(self):
        self.n_laps = 0
        self.track = ''
        self.session_type = ''
        self.fastest_lap = 0
        self.track_length = 0
        self.n_drivers = 0
        self.map_segments = []
        self.finished = False

        #print('Session reset\n')
