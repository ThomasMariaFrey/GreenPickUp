import ray
from ray.rllib.algorithms.ppo import PPO
import os
from ray.rllib.algorithms.algorithm import Algorithm
from ray.rllib.policy.policy import Policy


# own imports
import Helper
from Configs.ConfigFactory import ConfigFactory
from Envs.CompleteEnv import CompleteEnv

def rl_checkpoint_loader(dataset='dataSets/train_dataset_0.csv'):
    # Suppress the TensorFlow warning
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
    os.environ["CUDA_VISIBLE_DEVICES"] = ""

    helper = Helper.HelperMethods()

    gamma = 0.95
    lr = 0.0001

    helper = Helper.HelperMethods()
    data = helper.create_data(dataset, True)
    ray.init()
    config = ConfigFactory(CompleteEnv, data).get_standard_ppo_config()

    config = config.training(
        gamma=gamma,
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

    #Restoring the algorithm from here.
    while(True):
        path_to_checkpoint = input("Please enter the path to checkpoint of the algorithm.")
        user_input = input("Please enter 1 to restore a algorithm and continue training or enter 2 to restore a policy and compute a single action.")
        if(user_input==1):
            my_new_ppo = Algorithm.from_checkpoint(path_to_checkpoint)
            my_new_ppo.train()
            #Further actions after training to be entered here...
            break
        elif(user_input==2):
            my_restored_policy = Policy.from_checkpoint(path_to_checkpoint)
            datasetPath = input("Please enter the path to the dataset for that the policy is to be performed.")
            data = helper.createData(datasetPath)
            action = my_restored_policy.compute_single_action(data[2])
            print(f"Computed action {action} from given dataset.")
            break
        else:
            print("The wrong input has been entered, please try again.")

if __name__ == '__main__':
    rl_checkpoint_loader()
