import json
import pickle

import matplotlib.font_manager as font_manager
import matplotlib.image as image
import matplotlib.pyplot as plt
import mplcyberpunk as mplcp

from matplotlib.offsetbox import OffsetImage, AnnotationBbox

class RaceAnalyzer:

    def __init__(self, folder_path: str):
        
        self.config = json.load(open('Utility/configurations.json', 'r'))
        self.race_font = font_manager.FontProperties(fname='Utility/RaceFont.ttf')
        self.kanit_font = font_manager.FontProperties(fname='Utility/Kanit-Regular.ttf')

        self.alr_img = image.imread('Utility/ALR_Logo_F1.png')
        self.soft_tyre_img = image.imread('Utility/Soft.png')
        self.medium_tyre_img = image.imread('Utility/Medium.png')
        self.hard_tyre_img = image.imread('Utility/Hard.png')
        self.intermediate_tyre_img = image.imread('Utility/Intermediate.png')
        self.wet_tyre_img = image.imread('Utility/Wet.png')

        self.folder_path = folder_path
        self.drivers = pickle.load(open(f"{folder_path}/drivers.pkl", 'rb'))
        self.session = pickle.load(open(f"{folder_path}/session.pkl", 'rb'))

        self.outliers_included = False

    @staticmethod
    def format_laptime(laptime):
        total_seconds = laptime / 1000
        minutes = int (total_seconds // 60)
        seconds = int(total_seconds % 60)
        milliseconds = int (laptime % 1000)
        
        time_str = f"{minutes}:{seconds:02}.{milliseconds:03}"

        return time_str
    
    def individual_graphs(self):

        for driver_id in self.drivers:
            driver = self.drivers[driver_id]
            driver_name = driver.name
            driver_team = driver.team
    
    def run(self):

        self.individual_graphs()

