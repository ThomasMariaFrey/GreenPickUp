import unittest
from Configs.ConfigFactory import ConfigFactory
import numpy as np
from ray.rllib.algorithms.ppo import PPOConfig
from Envs.CompleteEnv import CompleteEnv

class TestConfigFactory(unittest.TestCase):
    def setUp(self):
        data = np.array([10, 30, 70, 20])
        env = CompleteEnv
        self.configFactory = ConfigFactory(env, data)
    def test_get_standard_ppo_config(self):
        ppoConfig = self.configFactory.get_standard_ppo_config()
        assert isinstance(ppoConfig, PPOConfig)

if __name__ == '__main__':
    unittest.main()
