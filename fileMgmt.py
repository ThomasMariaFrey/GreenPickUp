import click

def show_available_datasets():
    import os
    click.echo("Available datasets:")
    click.echo("__________________________________________")
    available_datasets = os.listdir("./RL/dataSets")
    for available_dataset in available_datasets:
        click.echo(available_dataset)
    click.echo("__________________________________________")
    return available_datasets


def select_available_dataset():
    available_datasets = show_available_datasets()
    selected_dataset_path = click.prompt('Select a dataset', type=str, default='test_dataset_0.csv')
    while selected_dataset_path not in available_datasets:
        selected_dataset_path = click.prompt("Not a valid dataset. Try again:", type=str)
    return selected_dataset_path


def show_available_checkpoints():
    import os
    click.echo("Available checkpoints:")
    click.echo("__________________________________________")
    available_datasets = os.listdir("./RL/policyStates")
    for available_dataset in available_datasets:
        click.echo(available_dataset)
    click.echo("__________________________________________")
    return available_datasets


def select_available_checkpoint():
    available_datasets = show_available_checkpoints()
    selected_dataset_path = click.prompt('Select a checkpoint', type=str)
    while selected_dataset_path not in available_datasets:
        selected_dataset_path = click.prompt("Not a valid checkpoint. Try again:", type=str)
    return selected_dataset_path
