import click
import itertools
import time

def spinner():

    # initailly clear screen of everything 
    click.clear()

    spinner = itertools.cycle("|/-\\")

    for _ in range(20):  # simulate loading through the spinner cycle of charcters 
        click.echo(click.style(next(spinner), nl=False, fg="blue"))
        time.sleep(0.1)
        click.clear()

