from ray.rllib.algorithms.ppo import PPOConfig

class ConfigFactory():
    def __init__(self, env, data):
        self.env = env
        self.data = data

    def get_standard_ppo_config(self, env_config={}):
        config = PPOConfig()

        # Insert the data into the environment configuration
        if 'data' not in env_config:
            env_config['data'] = self.data
        # Set the environment including the data
        config = config.environment(self.env, env_config=env_config)

        # Using tensorflow 2 as a framework
        config = config.framework(framework="tf2")

        return config
