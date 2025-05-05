import depoc
import click

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ..utils._response import _handle_response


client = depoc.DepocClient()
console = Console()

def _format_bank(obj, update: bool = False):
    table = Table(
        show_header=False,
        show_footer=True,
        box=None,
        expand=True,
        caption=f'{obj.id}',
        caption_justify='left'
        )
    
    table.add_column('', justify='left', no_wrap=True)
    table.add_column('', justify='right', no_wrap=True)
    balance = float(obj.balance)
    table.add_row(f'', f'[bold]R${balance:,.2f}')

    if update:
        border_style = 'green'
    elif not obj.is_active:
        border_style = 'red'
    else:
        border_style = 'none'

    panel = Panel(
        table,
        title=f'[bold]💰 {obj.name.upper()}',
        title_align='left',
        border_style=border_style,
    )

    console.print(panel)


@click.group(invoke_without_command=True)
@click.pass_context
def bank(ctx) -> None:
    ''' Manage bank accounts '''
    if ctx.invoked_subcommand is None:
        service = client.financial_accounts.all
        total_balance: float = 0
        if response := _handle_response(service):
            results = sorted(
                 response.results,
                 key=lambda result : result.balance,
                 reverse=True,
            )

            for obj in results:
                total_balance += float(obj.balance)
                _format_bank(obj)

            format_total_balance = f'R${total_balance:,.2f}'
            message = f'\n{'💵 Total Balance: ' + format_total_balance}\n'
            click.echo(message)

@bank.command
@click.argument('name')
def create(name: str) -> None:
    ''' Create a new bank account. '''
    data = {'name': name}
    service = client.financial_accounts.create

    if obj := _handle_response(service, data):
        _format_bank(obj)

@bank.command
@click.argument('id')
def get(id: str) -> None:
    ''' Retrieve an specific bank account. '''
    service = client.financial_accounts.get

    if obj := _handle_response(service, resource_id=id):
        _format_bank(obj)

@bank.command
@click.argument('id')
@click.argument('name')
@click.option('-A', '--activate', is_flag=True)
def update(id: str, name: str, activate: bool = False) -> None:
    ''' Update a bank account. '''
    data = {'name': name}

    # I want to reactivate a bank without having to provide a name
    if activate:
        data.update({'is_active': True})

    service = client.financial_accounts.update

    if obj := _handle_response(service, data, id):
        _format_bank(obj, update=True)

@bank.command
@click.argument('id')
def delete(id: str) -> None:
    ''' Delete a bank account. '''
    service = client.financial_accounts.delete

    if _handle_response(service, resource_id=id):
        console.print('✅ Bank account inactivated')
