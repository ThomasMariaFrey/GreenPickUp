import gymnasium as gym
import numpy as np
import random
# import Helper
try:
    import Helper
except ImportError:
    from RL import Helper

import sys
import os

helper = Helper.HelperMethods(True)

class CompleteEnv(gym.Env):
    # Initializes the environment
    def __init__(self, env_config=None):
        # Set the data
        self.data = env_config["data"]
        self.data_length = len(self.data[0])
        #
        self.distance_weight = self.setupDistanceWeights()
        self.column_weight = self.setupColumnWeight()
        #
        self.dimensions = helper.find_factors(self.data_length)
        # Sets the flag indicating if random steps are requested
        if "random" in env_config:
            self.random = env_config["random"]
        else:
            self.random = False
        # Number of pickup stations used
        if "num_pickup" in env_config:
            self.num_pickup = env_config["num_pickup"]
        else:
            self.num_pickup = 5
        # Location of the pick-up stations
        self.pickup_locations = []
        # State of the RL Algorithm
        self.state = np.zeros(self.data_length)
        # Boolean value signaling when the reinforcement learning algorithm is done
        self.done = False
        # Amount of steps done
        self.max_steps = 5
        # Starting amount of steps
        self.step_count = 0

        action_space = []
        for i in range(self.num_pickup):
            action_space.append(gym.spaces.Discrete(self.data_length))

        action_space = tuple(action_space)

        self.action_space = gym.spaces.Tuple(action_space)
        # The observation space, here a box of height on and the shape of the data length
        self.observation_space = gym.spaces.Box(low=0, high=1, shape=(self.data_length,), dtype=np.float64)

    # Resets the environment to an initial state
    def reset(self, *, seed=None, options=None):
        # Sets the pick-up locations to an empty state
        self.pickup_locations = []
        # Potential states of the reinforcement learning algorihtm
        self.state = np.zeros(self.data_length)
        # Setting the boolean done algorithm back to 0
        self.done = False
        # Setting the done amount of steps back to 0
        self.step_count = 0
        # Returns the given state with the empty pick-up locations list as actions taken
        return self.state, {"actions_taken": self.pickup_locations}

    # Does one step in the algorithm
    def step(self, action):
        # If the requested amount of steps has been done it resets the algorithm
        if self.done:
            return self._reset()

        # Random Agent implementation
        if self.random:
            # Choose a random index of the array
            random_index = random.randint(0, self.data_length - 1)
            # Action to be chosen
            action = random_index

        complete_reward = 0

        for single_action in action:
            self.state[single_action] = 1
            self.pickup_locations.append(single_action)
            complete_reward = complete_reward + self.reward(single_action)

        self.step_count += 1

        # set done to true if the requested amount of pick-up locations has been reached or if the maximum amount of
        # steps has been reached
        self.done = (len(self.pickup_locations) == self.num_pickup) or (self.step_count == self.max_steps)
        
        # Return the reached state, reward, boolean value if done, False and the pick-up locations that have been chosen
        # reward,
        return self.state, complete_reward, self.done, False, {"actions_taken": self.pickup_locations}

    def get_pickup_locations(self):
        return self.pickup_locations

    def reward(self, action):  # single_pickup_location_action):
        # rw = np.zeros(len(action))
        rw = 0
        # for single_pickup_location in action: #-1 because there is an extra id column in the beginning
        for i in range(len(self.data)-1):
            indexes = Helper.HelperMethods.select_indices(action, self.dimensions[0], self.dimensions[1])
            indexes.remove(action)
            rw = rw + self.data[i+1][action] * self.column_weight[i+1]
            for j in range(len(indexes)):
                rw = rw + self.data[i+1][indexes[j]] * self.distance_weight[i+1] * self.column_weight[i+1]
        return rw

    def setupDistanceWeights(self):
        # Initial weight of distances in the reward function
        file_path = '../distanceWeights.txt'

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

    def setupColumnWeight(self):
        # Initial weight of features in the reward function
        file_path = '../featureWeights.txt'

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

    def get_data(self):
        return self.data
