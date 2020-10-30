import click

@click.command('tst-command1')
def exec_test_commnad1():
    """test command."""
    click.echo('Test Command1.')

@click.command('tst-command2')
def exec_test_commnad2():
    """test command."""
    click.echo('Test Command2.')

@click.command('tst-command3')
def exec_test_commnad3():
    """test command."""
    click.echo('Test Command3.')
