import ray
from ray.rllib.algorithms.ppo import PPO
import os

# own imports
import Helper
from Configs.ConfigFactory import ConfigFactory
# from Envs.CompleteEnv import CompleteEnv

def main_ppo(rl_env, dataset='dataSets/train_dataset_0.csv'):
    # Suppress the TensorFlow warning
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
    os.environ["CUDA_VISIBLE_DEVICES"] = ""

    helper = Helper.HelperMethods()
    data = helper.create_data(dataset, True)
    data_length = len(data[0])
    dimensions = helper.find_factors(data_length)

    ray.init()
    config = ConfigFactory(rl_env, data).get_standard_ppo_config()

    config = config.training(
        gamma=0.95,
        lr=0.0001,
        clip_param=0.2,
        lambda_=0.95,
        num_sgd_iter=20,
        sgd_minibatch_size=1024,
        train_batch_size=5000,
        vf_clip_param=5
    )

    config = config.resources(
        num_cpus_per_worker=4
    )
    trainer = PPO(config=config)

    i = 0
    helper.initialize_output(data)

    while True:
        result = trainer.train()
        print("Iteration: " + str(i))
        i = i + 1
        if i % 30 == 0:
            helper.create_output(result, trainer)
            path_to_checkpoint = trainer.save()
            print(
                "An Algorithm checkpoint has been created inside directory: "
                f"'{path_to_checkpoint}'."
            )


if __name__ == '__main__':
    from Envs.CompleteEnv import CompleteEnv
    main_ppo(rl_env=CompleteEnv)

    