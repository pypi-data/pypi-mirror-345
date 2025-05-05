import click
import pyfiglet
from talemai.helper.creditionals import read_db_config, write_db_config
from talemai.helper.store_vectors import store_vectors
import asyncio

@click.command()

def main():
    ascii_art = pyfiglet.figlet_format("Talem AI CLI")
    click.echo(click.style(ascii_art, fg="blue"))

    db_config = read_db_config()

    if (db_config == None):
        new_api_endpoint = click.prompt('Enter new AstraDB URL')
        new_token = click.prompt('Enter new AstraDB Token')

        write_db_config(new_api_endpoint, new_token)
        click.echo(click.style("AstraDB configurations updated successfully.", fg="green"))
    
    else:
        click.echo(click.style("Already have configuration, using them...", fg="yellow"))

    # continue on w/ the program (store_vector re-reads the db config anyways)
    collection_name = click.prompt("Enter collection name to update")
    namespace = click.prompt("Enter namespace to update")
    pdf_url = click.prompt("Enter PDF url")
    click.echo(click.style("Using stored AstraDB URL", fg="yellow"))
    
    # run the logic for astradb to store info given as vectors 
    # asyncio runs in as async which is required for successful execution within astradb internals

    asyncio.run(store_vectors(pdf_url,collection_name,namespace))
