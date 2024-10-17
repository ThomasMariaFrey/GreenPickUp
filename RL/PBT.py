import random

import ray
from ray import air, tune
from ray.tune.schedulers import PopulationBasedTraining

from Envs.CompleteEnv import CompleteEnv
import Helper


def perform_pbt(dataset='dataSets/test_dataset_8.csv'):

    helper = Helper.HelperMethods()
    # data, distance_weight, column_weight = helper.createData(True)
    data = helper.create_data(dataset, True)
    data_length = len(data[0])
    dimensions = helper.find_factors(data_length)

    env_config = {
        "data": data
    }

    if True:#__name__ == "__main__":
        print("started pbt")
        # import argparse
        #
        # parser = argparse.ArgumentParser()
        # parser.add_argument(
        #     "--smoke-test", action="store_true", help="Finish quickly for testing"
        # )
        # args, _ = parser.parse_known_args()

        # Postprocess the perturbed config to ensure it's still valid
        def explore(config):
            # ensure we collect enough timesteps to do sgd
            if config["train_batch_size"] < config["sgd_minibatch_size"] * 2:
                config["train_batch_size"] = config["sgd_minibatch_size"] * 2
            # ensure we run at least one sgd iter
            if config["num_sgd_iter"] < 1:
                config["num_sgd_iter"] = 1
            return config

        hyperparam_mutations = {
            "lambda": lambda: random.uniform(0.9, 1.0),
            "clip_param": lambda: random.uniform(0.01, 0.5),
            "lr": [1e-3, 5e-4, 1e-4, 5e-5, 1e-5],
            "num_sgd_iter": lambda: random.randint(1, 30),
            "sgd_minibatch_size": lambda: random.randint(128, 16384),
            "train_batch_size": lambda: random.randint(2000, 160000),
        }

        pbt = PopulationBasedTraining(
            time_attr="time_total_s",
            perturbation_interval=120,
            resample_probability=0.25,
            # Specifies the mutations of these hyperparams
            hyperparam_mutations=hyperparam_mutations,
            # custom_explore_fn=explore,
        )

        # Stop when we've either reached 100 training iterations or reward=300
        # stopping_criteria = {"training_iteration": 100, "episode_reward_mean": 30000}
        stopping_criteria = {"training_iteration": 100, "episode_reward_mean": 200000}

        tuner = tune.Tuner(
            "PPO",
            # "DQN",
            tune_config=tune.TuneConfig(
                metric="episode_reward_mean",
                mode="max",
                scheduler=pbt,
                num_samples=4  # 1 if args.smoke_test else 4,
            ),
            param_space={
                "env": CompleteEnv,
                "env_config": env_config,
                "kl_coeff": 1.0,
                "num_workers": 4,
                "num_cpus_per_worker": 4,
                'framework': 'tf2',
                'log_level': 'INFO',
                "num_cpus": 1,  # number of CPUs to use per trial
                "num_gpus": 1,  # number of GPUs to use per trial
                "model": {"free_log_std": True},
                # These params are tuned from a fixed starting value.
                "lambda": 0.95,
                "clip_param": 0.2,
                "lr": 1e-4,
                # These params start off randomly drawn from a set.
                "num_sgd_iter": tune.choice([10, 20, 30]),
                "sgd_minibatch_size": tune.choice([128, 512, 2048]),
                "train_batch_size": tune.choice([10000, 20000, 40000]),
            },
            run_config=air.RunConfig(stop=stopping_criteria, local_dir="./ray_results2", name="test_experiment1"),
        )
        results = tuner.fit()
        import pprint

        best_result = results.get_best_result()

        print("Best performing trial's final set of hyperparameters:\n")
        pprint.pprint(
            {k: v for k, v in best_result.config.items() if k in hyperparam_mutations}
        )

        print("\nBest performing trial's final reported metrics:\n")

        metrics_to_print = [
            "episode_reward_mean",
            "episode_reward_max",
            "episode_reward_min",
            "episode_len_mean",
        ]
        pprint.pprint({k: v for k, v in best_result.metrics.items() if k in metrics_to_print})


if __name__ == '__main__':
    perform_pbt()