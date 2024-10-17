import copy
import unittest
from Envs.CompleteEnv import CompleteEnv
import numpy.testing
import Helper

class TestEnv(unittest.TestCase):
    def setUp(self):
        helper = Helper.HelperMethods(True)
        data = helper.create_data('dataSets/train_dataset_0.csv', True)
        env_config = {
            "data": data
        }
        self.env = CompleteEnv(env_config)

    def test_reset(self):
        env_before = copy.deepcopy(self.env)
        self.env.step([0, 1, 2, 3, 4])
        self.env.reset()
        env_after = copy.deepcopy(self.env)

        self.assertEqual(env_before.pickup_locations, env_after.pickup_locations)
        numpy.testing.assert_array_equal(env_before.state, env_after.state)
        self.assertEqual(env_before.step_count, env_after.step_count)

    def test_step(self):
        pickup_locations_before = self.env.get_pickup_locations().copy()
        self.env.step([0, 1, 2, 3, 4])
        pickup_locations_after = self.env.get_pickup_locations().copy()

        self.assertNotEqual(pickup_locations_before, pickup_locations_after)

    def test_get_pickup_locations(self):
        self.assertEqual(self.env.get_pickup_locations(), self.env.pickup_locations)
        self.env.step([0, 1, 2, 3, 4])
        self.assertEqual(self.env.get_pickup_locations(), self.env.pickup_locations)

    def test_reward(self):
        # TODO
        pass

if __name__ == '__main__':
    unittest.main()