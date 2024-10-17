import click
import fileMgmt


@click.command()
@click.option('--data_gen', is_flag=True, help='Generate a new data set.')
@click.option('--data', is_flag=True, help='View existing data sets.')
@click.option('--train', is_flag=True, help='Train a rl agent.')
@click.option('--checkpoint', is_flag=True, help='Load a checkpoint.')
@click.option('--weights', is_flag=True, help='Manage the weights of the rl environment.')
@click.option('--pbt', is_flag=True, help='Perform Population-Based Training')
def hello(data_gen, data, train, checkpoint, weights, pbt):
    import sys
    from pathlib import Path

    if data_gen:
        click.echo("Please define the parameters for the traffic simulation")
        k_drive = click.prompt('k_drive', type=int, default=5)
        k_bike = click.prompt('k_bike', type=int, default=5)
        k_walk = click.prompt('k_walk', type=int, default=5)
        target_csv = click.prompt('Please enter the name of the csv that the data will be exported to',
                                  type=str, default='data_rl.csv')

        sys.path.append(str(Path('DataProcessing').resolve()))
        from DataProcessing import main as data_processing_main

        data_processing_main = data_processing_main.Main(k_drive, k_bike, k_walk)
        success_message = data_processing_main.run(target_csv)
        click.echo(success_message)
        return

    if data:
        fileMgmt.show_available_datasets()
        return

    if weights:
        import os
        import webbrowser

        file_path = os.path.abspath("RL/featureWeights.txt")
        # Open the file in the application that opens a txt file per default on the users machine.
        webbrowser.open('file://' + file_path)

    if pbt:
        dataset = fileMgmt.select_available_dataset()
        sys.path.append(str(Path('RL').resolve()))
        from RL import PBT
        PBT.perform_pbt(dataset="dataSets/"+dataset)
        return

    if train:

        dataset = fileMgmt.select_available_dataset()
        sys.path.append(str(Path('RL').resolve()))
        from RL import MainPPO
        from RL.Envs.CompleteEnv import CompleteEnv
        MainPPO.main_ppo(rl_env=CompleteEnv, dataset="dataSets/"+dataset)
        return

    if checkpoint:
        dataset = fileMgmt.select_available_dataset()
        sys.path.append(str(Path('RL').resolve()))
        from RL import RLCheckpointLoader
        RLCheckpointLoader.rl_checkpoint_loader(dataset="dataSets/"+dataset)
        return

    click.echo("Try 'python greenpickup.py --help' for help.")


if __name__ == '__main__':
    hello()
