import os
import json
import numpy
import Utility
import seaborn as sns
import fastf1.plotting
import matplotlib.pyplot as plt



class Driver:

    def __init__(self, name: str):
        self.name = name
        self.team = "No Team"
        self.country = "Unknown"
        
        self.lap_times = []

        self.compound_dict = {16: "Soft", 17: "Medium", 18: "Hard",7: "Inter",8: "Wet"}
        
        self.finishing_position = 0
        self.starting_position = 0
        self.best_lap_time = 0
        self.points = 0
        self.result_status = "Unknown"
        self.laps_driven = 0
        self.tyre_stints_visual = []
        self.tyre_stints_end_laps = []


    def set_race_data(self, data: dict):
        
        self.lap_times = data['lap_times']

        self.team = data['team']
        self.country = data['country']
        self.finishing_position = data['final_position']
        self.starting_position = data['grid_position']
        self.best_lap_time = data['best_lap_time']
        self.points = data['points']
        self.result_status = data['result_status']
        self.laps_driven = data.get('laps_driven', 0)
        self.tyre_stints_visual = [self.compound_dict.get(tyre) for tyre in data.get('tyre_stints_visual', []) if tyre != 0]
        self.tyre_stints_end_laps = [laps for laps in data.get('tyre_stints_end_laps', []) if laps != 0]
        self.tyre_stints_end_laps[-1] = self.laps_driven
        self.tyre_stints = [self.tyre_stints_end_laps[0]] + [(self.tyre_stints_end_laps[i] - self.tyre_stints_end_laps[i - 1]) for i in range(1, len(self.tyre_stints_end_laps))]

    def get_lap_times(self):
        return list({key: value for key, value in self.lap_times.items() if value != 0}.values())
        
    def get_mean_lap_time(self):
        return numpy.mean(self.get_lap_times())

    def get_tyre_stints(self):
        tyres_used = []
        for idx, tyre in enumerate(self.tyre_stints_visual):
            tyres_used.extend([tyre] * self.tyre_stints[idx])

        return tyres_used

    def remove_slow_laps(self, laps):
        
        for out_laps in self.tyre_stints_end_laps[:-1]:

            try:
                laps.remove(self.get_lap_times()[out_laps])
                laps.remove(self.get_lap_times()[out_laps + 1])
            except:
                laps.remove(self.get_tyre_stints()[out_laps])
                laps.remove(self.get_tyre_stints()[out_laps + 1])

        return laps[1:]



class RaceAnalyzer:

    def __init__(self, race_data_directory: str):
        self.directory = race_data_directory
        self.data = json.load(open(f"{race_data_directory}/data.json", 'r'))
        self.config = self.load_config()

        self.session_info = self.data['session_info']
        self.driver_info = self.data['driver_info']

        self.track = self.session_info['track']
        self.drivers = {}

        self.sort_by = 'finishing_position'

        self.start()

    def load_config(self):
        with open('configurations.json', 'r') as f:
            return json.load(f)

    def start(self):
        self.parse_drivers()
        self.race_result = self.get_race_result()

        # drivers_chosen = ["NORRIS", "LECLERC", "VERSTAPPEN"]
        drivers_chosen = []

        self.visual_boxplot(drivers_chosen=drivers_chosen)
        self.visual_violinplot(drivers_chosen=drivers_chosen)

        drivers_folder = f"{self.directory}/Drivers"

        if not os.path.exists(drivers_folder):
            os.makedirs(drivers_folder)

        for driver, driver_info in self.race_result:
            if drivers_chosen == [] or driver in drivers_chosen:
                self.individual_graph(driver_info=driver_info, location=drivers_folder)

        #self.multiple_graph(drivers_chosen=drivers_chosen, location=drivers_folder)

    def parse_drivers(self):
        for driver_id, driver_data in self.driver_info.items():
            if 'name' in driver_data and driver_data['laps_driven'] != 0:
                driver = Driver(name=driver_data['name'])
                driver.set_race_data(data=driver_data)
                self.drivers[driver_data['name']] = driver

    def get_race_result(self):
        return sorted(self.drivers.items(), key=lambda item: getattr(item[1], self.sort_by))

    def visual_boxplot(self, outliers_included: bool = False, drivers_chosen: list = []):
        fig, ax = plt.subplots(figsize=(28,10))
        lap_times, tyres, drivers, means = [], [], [], []

        for driver, driver_info in self.race_result:

            if drivers_chosen == [] or driver in drivers_chosen:
                print(driver)
                driver_lap_times = driver_info.get_lap_times() if outliers_included else driver_info.remove_slow_laps(driver_info.get_lap_times())
                driver_tyre_compounds = driver_info.get_tyre_stints() if outliers_included else driver_info.remove_slow_laps(driver_info.get_tyre_stints())
                driver_means = Utility.format_laptime(round(numpy.mean(driver_lap_times)))

                lap_times.append(driver_lap_times)
                tyres.append(driver_tyre_compounds)
                drivers.append(driver)
                means.append(driver_means)

        bp = ax.boxplot(lap_times, vert=True, showmeans=True, meanline=True, labels=drivers, showfliers=False, patch_artist=True,
                        flierprops={'marker': 'o', "markerfacecolor": "white"},
                        medianprops={'color': 'white', 'linewidth': 0},
                        meanprops={'color': 'white'},
                        whiskerprops={'color': 'white', 'linewidth': 2},
                        capprops={'color': 'white', 'linewidth': 2}
                        )
        
        ax.set_title(f"Grand Prix: {self.track}\nSorted By {self.sort_by}", fontdict={"color": "white", "fontsize": 20})
        ax.set_xlabel("Drivers", fontdict={"color": "white", "fontsize": 20})
        ax.set_ylabel("Laptime", fontdict={"color": "white", "fontsize": 20})

        ax.set_facecolor("#212121")
        fig.set_facecolor("#111111")

        ax.tick_params(axis='x', labelsize=14, colors='White', rotation=45)
        ax.tick_params(axis='y', labelsize=14, colors='White')

        ax.spines['bottom'].set_color('white')
        ax.spines['top'].set_color('White') 
        ax.spines['right'].set_color('White')
        ax.spines['left'].set_color('White')
        
        for idx, box in enumerate(bp['boxes']):
            box.set(facecolor="white", edgecolor="black", linewidth=2)
            box.set(facecolor = self.config['team_color'][self.race_result[idx][1].team])

        old_labels = [ticks.get_text() for ticks in ax.get_yticklabels(which="major")]
        new_labels = [Utility.format_laptime(int(old_label)) for old_label in old_labels]
        old_labels = [int(old_label) for old_label in old_labels]

        ax.set_yticks(old_labels, new_labels)

        ax.grid(which='major', color='grey', linewidth=0.8)

        plt.savefig(f"{self.directory}/boxplot.png", dpi=300)
        plt.close()

    def visual_violinplot(self, outliers_included: bool = False, drivers_chosen: list = []):
        fig, ax = plt.subplots(figsize=(28,10))
        lap_times, tyres, drivers, means = [], [], [], []

        flat_drivers = []

        for driver, driver_info in self.race_result:

            if drivers_chosen == [] or driver in drivers_chosen:

                driver_lap_times = driver_info.get_lap_times() if outliers_included else driver_info.remove_slow_laps(driver_info.get_lap_times())
                driver_tyre_compounds = driver_info.get_tyre_stints() if outliers_included else driver_info.remove_slow_laps(driver_info.get_tyre_stints())
                driver_means = Utility.format_laptime(round(numpy.mean(driver_lap_times)))

                lap_times.append(driver_lap_times)
                tyres.append(driver_tyre_compounds)
                drivers.append(driver)
                means.append(driver_means)

                flat_drivers.extend([driver] * len(driver_lap_times))

        flat_lap_times = [time for driver_lap_times in lap_times for time in driver_lap_times]
        flat_tyre_compounds = [tyre for driver_tyres in tyres for tyre in driver_tyres]

        sns.violinplot(y=flat_lap_times,x=flat_drivers, inner=None, scale='width', palette=[self.config['team_color'][self.drivers[driver].team] for driver in drivers])
        sns.swarmplot(y=flat_lap_times,x=flat_drivers, hue=flat_tyre_compounds, palette={'Soft': 'red', 'Medium': 'yellow', 'Hard': 'grey'}, hue_order=["Soft", "Medium", "Hard"], linewidth=0, size=5)

        ax.set_title(f"Grand Prix: {self.track}\nSorted By {self.sort_by}", fontdict={"color": "white", "fontsize": 20})
        ax.set_xlabel("Drivers", fontdict={"color": "white", "fontsize": 20})
        ax.set_ylabel("Laptime", fontdict={"color": "white", "fontsize": 20})

        ax.set_facecolor("#212121")
        fig.set_facecolor("#111111")

        ax.tick_params(axis='x', labelsize=14, colors='White', rotation=45)
        ax.tick_params(axis='y', labelsize=14, colors='White')

        ax.spines['bottom'].set_color('white')
        ax.spines['top'].set_color('White') 
        ax.spines['right'].set_color('White')
        ax.spines['left'].set_color('White')

        old_labels = [ticks.get_text() for ticks in ax.get_yticklabels(which="major")]
        new_labels = [Utility.format_laptime(int(old_label)) for old_label in old_labels]
        old_labels = [int(old_label) for old_label in old_labels]

        ax.set_yticks(old_labels, new_labels)

        sns.despine(left=True, bottom=True)
        ax.grid(which='major', color='grey', linewidth=0.2)

        plt.tight_layout()

        plt.legend(title='Tyre Compounds', title_fontsize='12', fontsize='16', loc='upper right')

        plt.savefig(f"{self.directory}/Violin.png")
        plt.close()

    def individual_graph(self, driver_info: Driver, location: str):
        fig, ax = plt.subplots(figsize=(28, 10))

        ax.plot(driver_info.get_lap_times(), color=self.config['team_color'][driver_info.team], label=driver_info.name, linewidth=3.5, markeredgewidth=2, markeredgecolor='white')

        for idx, lap in enumerate(driver_info.get_lap_times()):
            
            if driver_info.get_tyre_stints()[idx] == "Soft":
                soft_point = ax.scatter(idx, lap, color='red', s=100, zorder=10, label='Soft')
            elif driver_info.get_tyre_stints()[idx] == "Medium":
                medium_point = ax.scatter(idx, lap, color='yellow', s=100, zorder=10, label='Medium')
            elif driver_info.get_tyre_stints()[idx] == "Hard":
                hard_point = ax.scatter(idx, lap, color='grey', s=100, zorder=10, label='Hard')

        ax.set_title(f"Grand Prix: {self.track}\n Laptimes {driver_info.name}", fontdict={"color": "white", "fontsize": 20})
        ax.set_xlabel("Drivers", fontdict={"color": "white", "fontsize": 20})
        ax.set_ylabel("Laptime", fontdict={"color": "white", "fontsize": 20})

        ax.set_facecolor("#212121")
        fig.set_facecolor("#111111")

        ax.tick_params(axis='x', labelsize=14, colors='White')
        ax.tick_params(axis='y', labelsize=14, colors='White')

        ax.spines['bottom'].set_color('white')
        ax.spines['top'].set_color('White') 
        ax.spines['right'].set_color('White')
        ax.spines['left'].set_color('White')

        old_labels = [ticks.get_text() for ticks in ax.get_yticklabels(which="major")]
        new_labels = [Utility.format_laptime(int(old_label)) for old_label in old_labels]
        old_labels = [int(old_label) for old_label in old_labels]

        ax.set_yticks(old_labels, new_labels)
        ax.set_xticks(range(len(driver_info.get_lap_times())))
        
        ax.grid(which='major', color='grey', linewidth=0.1)

        try:
            ax.legend(title='Tyre Compounds', loc='upper right', title_fontsize=12, fontsize='16', handles=[soft_point, medium_point, hard_point])
        except:
            try:
                ax.legend(title='Tyre Compounds', loc='upper right', title_fontsize=12,fontsize='16', handles=[soft_point, medium_point])
            except:
                try:
                    ax.legend(title='Tyre Compounds', loc='upper right', title_fontsize=12,fontsize='16', handles=[soft_point, hard_point])
                except:
                    try:
                        ax.legend(title='Tyre Compounds', loc='upper right', title_fontsize=12,fontsize='16', handles=[medium_point, hard_point])
                    except:
                        try:
                            ax.legend(title='Tyre Compounds', loc='upper right', title_fontsize=12,fontsize='16', handles=[soft_point])
                        except:
                            try:
                                ax.legend(title='Tyre Compounds', loc='upper right', title_fontsize=12,fontsize='16', handles=[medium_point])
                            except:
                                try:
                                    ax.legend(title='Tyre Compounds', loc='upper right', title_fontsize=12,fontsize='16', handles=[hard_point])
                                except:
                                    pass


        plt.savefig(f"{location}/{driver_info.name}.png", dpi=300)
        plt.close()

    def multiple_graph(self, drivers_chosen: list, location: str):
        fig, ax = plt.subplots(figsize=(28, 10))

        for driver in drivers_chosen:
            driver_info = self.drivers[driver]
            ax.plot(driver_info.get_lap_times(), color=self.config['team_color'][driver_info.team], label=driver_info.name, linewidth=3.5, markeredgewidth=2, markeredgecolor='white')
            
            for idx, lap in enumerate(driver_info.get_lap_times()):
                if driver_info.get_tyre_stints()[idx] == "Soft":
                    soft_point = ax.scatter(idx, lap, color='red', s=100, zorder=10, label='Soft')
                elif driver_info.get_tyre_stints()[idx] == "Medium":
                    medium_point = ax.scatter(idx, lap, color='yellow', s=100, zorder=10, label='Medium')
                elif driver_info.get_tyre_stints()[idx] == "Hard":
                    hard_point = ax.scatter(idx, lap, color='grey', s=100, zorder=10, label='Hard')

        title = " VS ".join(drivers_chosen)
        ax.set_title(f"Grand Prix: {self.track}\n{title}", fontdict={"color": "white", "fontsize": 20})
        ax.set_xlabel("Drivers", fontdict={"color": "white", "fontsize": 20})
        ax.set_ylabel("Laptime", fontdict={"color": "white", "fontsize": 20})

        ax.set_facecolor("#212121")
        fig.set_facecolor("#111111")

        ax.tick_params(axis='x', labelsize=14, colors='White', rotation=45)
        ax.tick_params(axis='y', labelsize=14, colors='White')

        ax.spines['bottom'].set_color('white')
        ax.spines['top'].set_color('White') 
        ax.spines['right'].set_color('White')
        ax.spines['left'].set_color('White')

        old_labels = [ticks.get_text() for ticks in ax.get_yticklabels(which="major")]
        new_labels = [Utility.format_laptime(int(old_label)) for old_label in old_labels]
        old_labels = [int(old_label) for old_label in old_labels]

        ax.set_yticks(old_labels, new_labels)
        ax.set_xticks(range(len(driver_info.get_lap_times())))

        ax.grid(which='major', color='grey', linewidth=0.1)

        try:
            ax.legend(title='Tyre Compounds', loc='upper right', title_fontsize=12, fontsize='16', handles=[soft_point, medium_point, hard_point])
        except:
            try:
                ax.legend(title='Tyre Compounds', loc='upper right', title_fontsize=12,fontsize='16', handles=[soft_point, medium_point])
            except:
                try:
                    ax.legend(title='Tyre Compounds', loc='upper right', title_fontsize=12,fontsize='16', handles=[soft_point, hard_point])
                except:
                    try:
                        ax.legend(title='Tyre Compounds', loc='upper right', title_fontsize=12,fontsize='16', handles=[medium_point, hard_point])
                    except:
                        try:
                            ax.legend(title='Tyre Compounds', loc='upper right', title_fontsize=12,fontsize='16', handles=[soft_point])
                        except:
                            try:
                                ax.legend(title='Tyre Compounds', loc='upper right', title_fontsize=12,fontsize='16', handles=[medium_point])
                            except:
                                try:
                                    ax.legend(title='Tyre Compounds', loc='upper right', title_fontsize=12,fontsize='16', handles=[hard_point])
                                except:
                                    pass

        
        plt.savefig(f"{location}/{title} Graph.png", dpi=300)
        plt.close()

        
race_data_directory = r"Results/Race/Brazil 22-09-2024 (22h08)"
client = RaceAnalyzer(race_data_directory=race_data_directory)