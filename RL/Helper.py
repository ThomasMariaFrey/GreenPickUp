# Imports
import csv
import datetime
import folium
from IPython.display import IFrame
import json
import numpy as np
import pandas as pd
from ray.rllib.policy.policy import Policy
import os


class HelperMethods:
    """This class is used to enable the preprocessing, training and evaluation of the reinforcement learning algorithm.
    For the preprocessing the methods create_coordinate_list, create_data and merge_data are used.
    For the training the methods: find_factors, reward, set_up_distance_weights and set_up_column_weightss are used.
    For the evaluation the methods: select_indices, create_coordinate_list, action_to_coord, plot_coordinate, 
    initialize_output, create_output and run_policy is used."""
    episode_reward_mean = []
    i = 0
    current_date_time = datetime.datetime.now()
    formatted_date_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    def __init__(self, debug=False):
        self.data = None

        # Get the directory containing your current script:
        # script_dir = os.path.dirname(os.path.abspath(__file__))
        #
        # # Append the relative path to your CSV:
        # csv_path = os.path.join(script_dir, 'dataSets/coordinate_dataset.csv')
        # self.coordinate_list = self.create_coordinate_list(csv_path)

        self.coordinate_list = self.create_coordinate_list("dataSets/coordinate_dataset.csv")
        self.output_name = "rlOutput/" + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + "output.csv"

        if not debug:
            self.trial_datasets = [self.create_data('dataSets/test_dataset_0.csv'),
                                   self.create_data('dataSets/test_dataset_1.csv'),
                                   self.create_data('dataSets/test_dataset_2.csv'),
                                   self.create_data('dataSets/test_dataset_3.csv'),
                                   self.create_data('dataSets/test_dataset_4.csv'),
                                   self.create_data('dataSets/test_dataset_5.csv'),
                                   self.create_data('dataSets/test_dataset_6.csv'),
                                   self.create_data('dataSets/test_dataset_7.csv'),
                                   self.create_data('dataSets/test_dataset_8.csv')]

            self.test_reward_mean = []
            self.dimensions = self.find_factors(len(self.trial_datasets[0][0]))

            self.distance_weight = self.set_up_distance_weights()
            self.column_weight = self.set_up_column_weights()

    def reward(self, action):
        """
        Calculates the reward of a cell that is given by an action. For this the reward of the cell as
        well as the reward of the surrounding cells are considered.
        @param action: The cell of that the rewards are to be calculated.
        @return: The calculated reward for the cell.
        """
        rw = 0
        for i in range(len(self.data)):
            indexes = self.select_indices(action, self.dimensions[0], self.dimensions[1])
            indexes.remove(action)
            rw = rw + self.data[i][action] * self.column_weight[i]
            for j in range(len(indexes)):
                rw = rw + self.data[i][indexes[j]] * self.distance_weight[i] * self.column_weight[i]
        return rw

    def reward(self, action, data):
        """
        Overwrite for the reward function for the case that the data and the dimension is also given.
        Calculates the reward of a cell that is given by an action. For this the reward of the cell aswell as the reward
        of the surrounding cells are considered. Considering more than the directly adjacent cells makes the algorithm
        very slow. Therefor only the adjacend cells are considered.
        @param action: The cell of that the rewards are to be calculated.
        @param data: The data file given from that the reward is calculated.
        @return: The calculated reward for the cell.
        """
        rw = 0
        for i in range(len(data)):
            indexes = self.select_indices(action, self.dimensions[0], self.dimensions[1])
            indexes.remove(action)
            rw = rw + data[i][action] * self.column_weight[i]
            for j in range(len(indexes)):
                rw = rw + data[i][indexes[j]] * self.distance_weight[i] * self.column_weight[i]
        return rw

    def reward(self, action, data, dimensions):
        """
        Overwrite for the reward function for the case that the data and the dimension is also given.
        Calculates the reward of a cell that is given by an action. For this the reward of the cell aswell as the reward
        of the surrounding cells are considered. Considering more than the directly adjacent cells makes the algorithm
        very slow. Therefor only the adjacend cells are considered.
        @param action: The cell of that the rewards are to be calculated.
        @param data: The data file given from that the reward is calculated.
        @param dimensions: A point, representing the dimensions of the dataset.
        @return: The calculated reward for the cell.
        """
        rw = 0
        for i in range(len(data) - 1):
            indexes = self.select_indices(action, dimensions[0], dimensions[1])
            indexes.remove(action)
            rw = rw + data[i][action] * self.column_weight[i]
            for j in range(len(indexes)):
                rw = rw + data[i][indexes[j]] * self.distance_weight[i] * self.column_weight[i]
        return rw

    def action_to_coord(self, actions):
        """
        Given a list of action this method returns the coordinates of the corresponding cell to the action. This is
        done by using the coordinate list.
        @param actions: The list of actions for that the coordinates are to be found.
        @return: The coordinates list for the action list.
        """
        coordinates = [self.coordinate_list[actions]]
        return coordinates

    def create_data(self, given_file_path, merge_data=True):
        """
        This method is used to read in the dataset into respective features. These features are then combined in a
        further step by the merge data function.
        The columns are as follows:
        cell_id,population,traffic,parcel_locker,college,bank,pharmacy,parking,post_office,theatre,cinema,library,atm,
        school,kindergarten,bus_station,hospital,nursing_home,charging_station,university,industrial,commercial,
        residential,social_facility,exhibition_centre,recycling,depot,station,ferry_terminal,cycle_barrier,public,
        apartments,sports_hall,retail,office,archive,town hall,civic,house,cafe,supermarket,community_centre,restaurant,
        stadium,doctors,pub,fast_food, bar,place_of_worship,fuel,religious,studio,music_school,brothel,police,
        biergarten,public_building,bicycle_parking, car_wash,childcare,ice_cream,events_venue
        @param given_file_path: The relative path where the dataset is saved.
        @param merge_data: Merges the feature data if required.
        @return: The features of the data set in a list.
        """
        # Delete the district and the geometry columns before by hand for this code to work!

        file_path = given_file_path
        # # Get the directory containing your current script:
        # script_dir = os.path.dirname(os.path.abspath(__file__))
        #
        # # Append the relative path to your CSV:
        # file_path = os.path.join(script_dir, file_path)
        with open(file_path, 'r') as file:
            reader = csv.reader(file)
            header_row = next(reader)
        data = []
        complete_header = []

        for i in range(38):
            column_data = np.genfromtxt(file_path, delimiter=',', dtype=float, invalid_raise=False)
            column_data = column_data[:, i]
            header = header_row[i]
            column_data = column_data[1:]
            column_data = np.nan_to_num(column_data, nan=0)
            column_data = np.array(column_data.flatten())
            data.append(column_data)
            complete_header.append(header)

        data = np.array(data)

        if merge_data:
            data = self.merge_data(data)
        return data

    def initialize_output(self, data):
        """
        This method is used to further initialize the helper method with the training data set and variables mainly used for documentation
        purposes.
        @return: No returns.
        """
        self.data = data
        self.output_name = "rlOutput/" + self.current_date_time.strftime("%Y%m%d%H%M%S") + "output.csv"
        # file_path = self.output_name
        # # Get the directory containing your current script:
        # script_dir = os.path.dirname(os.path.abspath(__file__))
        #
        # # Append the relative path to your CSV:
        # self.output_name = os.path.join(script_dir, file_path)

        with open(self.output_name, 'w', newline='') as csvfile:
            fieldnames = ['iterations_since_restore', 'num_remote_worker_restarts', 'episode_reward_mean',
                          'num_env_steps_trained_this_iter', 'date', 'timers', 'sampler_results', 'info',
                          'policy_reward_max',
                          'num_faulty_episodes', 'counters', 'num_in_flight_async_reqs', 'perf', 'custom_metrics',
                          'episodes_this_iter', 'episode_media', 'time_this_iter_s', 'warmup_time', 'sampler_perf',
                          'agent_timesteps_total', 'trial_id', 'hostname', 'policy_reward_min', 'training_iteration',
                          'episode_reward_min', 'timestamp', 'num_env_steps_trained', 'node_ip',
                          'num_steps_trained_this_iter',
                          'num_healthy_workers', 'timesteps_total', 'episodes_total', 'episode_len_mean', 'done',
                          'time_total_s', 'policy_reward_mean', 'episode_reward_max', 'num_env_steps_sampled_this_iter',
                          'time_since_restore', 'experiment_id', 'num_agent_steps_sampled', 'config',
                          'num_env_steps_sampled',
                          'num_agent_steps_trained', 'connector_metrics', 'timesteps_since_restore', 'pid',
                          'hist_stats']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

    def create_output(self, result, trainer, extended_logs=True):
        """
        This method is used to create custom logs for the evaluation of the PPO algorithm It also saves policies if so
        required.
        @param result: The result of the PPO algorithm.
        @param trainer: The trainer used for the PPO algorithm.
        @param extended_logs: Saves the current policy and the logs of the model for evaluation.
        @return: No returns
        """
        with open(self.output_name, 'w', newline='') as csvfile:
            fieldnames = ['iterations_since_restore', 'num_remote_worker_restarts', 'episode_reward_mean',
                          'num_env_steps_trained_this_iter', 'date', 'timers', 'sampler_results', 'info',
                          'policy_reward_max',
                          'num_faulty_episodes', 'counters', 'num_in_flight_async_reqs', 'perf', 'custom_metrics',
                          'episodes_this_iter', 'episode_media', 'time_this_iter_s', 'warmup_time', 'sampler_perf',
                          'agent_timesteps_total', 'trial_id', 'hostname', 'policy_reward_min', 'training_iteration',
                          'episode_reward_min', 'timestamp', 'num_env_steps_trained', 'node_ip',
                          'num_steps_trained_this_iter',
                          'num_healthy_workers', 'timesteps_total', 'episodes_total', 'episode_len_mean', 'done',
                          'time_total_s', 'policy_reward_mean', 'episode_reward_max', 'num_env_steps_sampled_this_iter',
                          'time_since_restore', 'experiment_id', 'num_agent_steps_sampled', 'config',
                          'num_env_steps_sampled',
                          'num_agent_steps_trained', 'connector_metrics', 'timesteps_since_restore', 'pid',
                          'hist_stats']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow(result)

        if extended_logs:
            policy_current_date_time = datetime.datetime.now()
            policy_formatted_date_time = policy_current_date_time.strftime("%Y%m%d%H%M%S")
            policy_output_name = "policyStates/" + policy_formatted_date_time + "default_policy"

            default_policy = trainer.get_policy(policy_id="default_policy")
            default_policy.export_checkpoint(policy_output_name)
            my_restored_policy = Policy.from_checkpoint(policy_output_name)

            action = my_restored_policy.compute_single_action(self.data[2])
            coordinates = self.action_to_coord(action[0][2])
            self.plot_coordinate(coordinates)
            results = []

            for j in range(len(self.trial_datasets)):
                results.append(self.run_policy(self.trial_datasets[j], policy_output_name, j))
                action = my_restored_policy.compute_single_action(self.trial_datasets[j][2])
                combined_reward = 0
                for a in action[0]:
                    combined_reward = combined_reward + self.reward(a, self.trial_datasets[j], self.dimensions)
                if len(self.test_reward_mean) < len(self.trial_datasets):
                    distance = len(self.trial_datasets) - len(self.test_reward_mean)
                    for i in range(distance):
                        self.test_reward_mean.append([])
                self.test_reward_mean[j].append(combined_reward)
            self.episode_reward_mean.append(result['episode_reward_mean'])
            combined_list = self.test_reward_mean.append(self.episode_reward_mean)

            with open("reward_list.txt", 'w') as file:
                json.dump(combined_list, file)
            del my_restored_policy

    def run_policy(self, path_to_data, path_to_policy, i):
        """
        This method is able to run a saved policy. It also saves a map of the action chosen by the policy.
        @param path_to_data: The relative spot of the dataset that has been used.
        @param path_to_policy: The relative spot of the policy that is to be used
        @param i: The current iteration that is being considered.
        @return: A two-dimensional variable of the path to data and the trail_gps
        """
        trial_data = path_to_data

        try:
            my_restored_policy = Policy.from_checkpoint(path_to_policy)
        except OSError as e:
            if e.errno == 16:
                print("Error: The device or resource is busy. Please try again later.")
            else:
                print("An OSError occurred with errno:", e.errno)

        action = my_restored_policy.compute_single_action(trial_data[2])
        trial_action = action
        map_name = "trial_csv/dataset" + str(i + 1) + "map.html"
        trial_gps = self.action_to_coord(trial_action[0][2])
        self.plot_coordinate(trial_gps, map_name)

        del my_restored_policy

        return [path_to_data, trial_gps]

    @staticmethod
    def find_factors(x):
        """
        This method finds the two factors of an integer that are as close to each other as possible.
        @param x: The integer for which the factors are to be found.
        @return: The factors calculated for the integer returned as a point.
        """
        min_diff = float('inf')
        result = (x, 1)
        for i in range(2, int(x ** 0.5) + 1):
            if x % i == 0:
                diff = abs(i - x // i)
                if diff < min_diff:
                    min_diff = diff
                    result = (x // i, i)
        return result

    @staticmethod
    def select_indices(x, num_rows, num_cols):
        """
        Given an integer x and the numbers of rows and columns of a matrix this method finds the cell in the matrix
        as well as all cells around it and returns them in an array.
        @param x: The number for that the cell is to be found.
        @param num_rows: The number of given rows.
        @param num_cols: The number of given columns.
        @return: The position of the cell for the given action in a point. The first dimension of the point entails the
        rows whereas the second dimension entails the columns.
        """
        row_range = range(max(0, x // num_cols - 1), min(num_rows, x // num_cols + 2))
        col_range = range(max(0, x % num_cols - 1), min(num_cols, x % num_cols + 2))
        selected_indices = []

        for i in row_range:
            for j in col_range:
                selected_indices.append(i * num_cols + j)

        return selected_indices

    @staticmethod
    def create_coordinate_list(filename):
        """
        This method uses a datafile, here the given dataset-file and extracts a list off coordinates for every entry in
        the data file.
        @param filename: The dataset-file from that the coordinate list is to be extracted from.
        @return: A coordinate list that maps a cell to a coordinate.
        """
        df = pd.read_csv(filename)

        centroid_strings = df['centroid'].tolist()

        points_list = []
        for point_string in centroid_strings:
            point = point_string.strip('POINT ()').split()
            point = (float(point[1]), float(point[0]))
            points_list.append(point)

        return points_list

    @staticmethod
    def set_up_distance_weights():
        """
        Reads in the feature weights from the distanceWeights.txt file. This file contains the feature weights that can
        be used for the algorithms. The real number at the start of each line will be used as the weight for the feature
        that is stated after the number on the same line. Please note that only real numbers in the format x.y and only
        the first number on the line before the comma can be read.
        @return: The list of distance weights for all surrounding cells of the action cell.
        """
        # If necessary replace with the actual path to your distance weight txt file
        file_path = 'distanceWeights.txt'
        # # Get the directory containing your current script:
        # script_dir = os.path.dirname(os.path.abspath(__file__))
        #
        # # Append the relative path to your CSV:
        # file_path = os.path.join(script_dir, file_path)

        with open(file_path, 'r') as file:
            lines = file.readlines()[1:]
            featureWeights = []

            for line in lines:
                weight, feature = line.strip().split(', ')
                featureWeights.append(float(weight))

        return featureWeights

    @staticmethod
    def set_up_column_weights():
        """
        Reads in the feature weights from the featureWeights.txt file. This file contains the feature weights that can
        be used for the algorithms. The real number at the start of each line will be used as the weight for the feature
        that is stated after the number on the same line. Please note that only real numbers in the format x.y and only
        the first number on the line before the comma can be read.
        @return: A list of feature weights of the dataset as set in featureWeights.txt.
        """
        file_path = 'featureWeights.txt'
        # # Get the directory containing your current script:
        # script_dir = os.path.dirname(os.path.abspath(__file__))
        #
        # # Append the relative path to your CSV:
        # file_path = os.path.join(script_dir, file_path)

        with open(file_path, 'r') as file:
            lines = file.readlines()[1:]
            featureWeights = []

            for line in lines:
                weight, feature = line.strip().split(', ')
                featureWeights.append(float(weight))

        return featureWeights

    @staticmethod
    def merge_data(data):
        """
        This method is used to combine the specific featuers requested. The new list is then returned.
        @param data: The data which is to be combined.
        @return: The new dataset that has been combined.
        """
        merged_data = np.zeros((20, data.shape[1]))
        # cell_id: 0
        merged_data[0] = data[0]
        # population: 1
        merged_data[1] = data[37]
        # traffic: 1
        merged_data[2] = data[36]
        # postal: parcel_locker + post_office + depot: 10
        merged_data[3] = data[1] + data[6] + data[21]
        # higher_education: college + university:10
        merged_data[4] = data[2] + data[16]
        # services: bank + pharmacy + atm + retail: 10
        merged_data[5] = data[3] + data[4] + data[10] + data[27]
        # parking:20
        merged_data[6] = data[5]
        # recreational: # theatre + cinema + sports_hall + stadium: + religious: 10
        merged_data[7] = data[7] + data[8] + data[26] + data[32] + data[33]
        # public_buildings: library + public(24) + civic29 + community_centre: 10
        merged_data[8] = data[9] + data[24] + data[29]
        # obstruction: school + kindergarten + construction + cycle_barrier: -100
        merged_data[9] = data[11] + data[12] + data[20] + data[23]
        # transportation: station(22): 10
        merged_data[10] = data[22]
        # healthcare: hospital13 + nursing_home14: 5
        merged_data[11] = data[13] + data[14]
        # charging_station: 10
        merged_data[12] = data[15]
        # industrial: 10
        merged_data[13] = data[17]
        # commercial: 10
        merged_data[14] = data[18]
        # residential + apartments: 10
        merged_data[15] = data[19] + data[25]
        # office: 10
        merged_data[16] = data[28]
        # nature: water + wood + cycle_barrier + :-100
        merged_data[17] = data[34] + data[35]
        # house:5
        merged_data[18] = data[30]
        # supermarket:20
        merged_data[19] = data[31]
        return merged_data

    @staticmethod
    def plot_coordinate(coordinates, output_name=None):
        """
        This method is used plot a list of coordinates on a folium map and saves it. The directory maps must be created
        at file level before using this method.
        Coordinates of the matrix spanning Stuttgart.
        Most North: 48.8663994
        Most South: 48.6920188
        Most East: 9.3160228
        Most West: 9.0386007
        @param coordinates: The list of coordinates as a list of points.
        @param output_name: The output name that is to be used for the saved map.
        @return: Nothing, saves the map under the output_name input or the output_name = "maps/" + formatted_date_time +
        "map.html" default
        """
        # Center of the given edge coordinates of Stuttgart.
        stuttgart_center = [48.6920188 + ((48.8663994 - 48.6920188) / 2), 9.0386007 + ((9.3160228 - 9.0386007) / 2)]
        m = folium.Map(location=stuttgart_center, zoom_start=10)

        for i in range(len(coordinates)):
            text = f"This is action {i + 1}"
            folium.Marker(location=coordinates[i], popup=text).add_to(m)
        # For the normal case where no file directory is provided this is placed in the maps folder with a corresponding
        # date time spot.
        if output_name is None:
            current_date_time = datetime.datetime.now()
            formatted_date_time = current_date_time.strftime("%Y%m%d%H%M%S")
            # You must create a directory "maps" yourself in the directory where this file is placed.
            output_name = "maps/" + formatted_date_time + "map.html"

        m.save(output_name)
        IFrame(src='Legacy/map.html', width=700, height=600)
