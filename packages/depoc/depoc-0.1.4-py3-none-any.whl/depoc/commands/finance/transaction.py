import depoc
import click
import sys
import time

from typing import Any

from rich.prompt import Prompt
from rich.panel import Panel
from rich.console import Console

from ..utils._response import _handle_response
from ..utils._format import spinner, page_summary, _format_transactions


client = depoc.DepocClient()
console = Console()


@click.group(invoke_without_command=True)
@click.pass_context
@click.option('-l', '--limit', default=50)
@click.option('-p', '--page', default=0)
@click.option('-b', '--bank')
def transaction(ctx, limit: int, page: int, bank: str) -> None:
    ''' Manage financial transactions '''
    if ctx.invoked_subcommand is None:
        service = client.financial_transactions.all

        if response := _handle_response(service, limit=limit, page=page):
            results = response.results

            if bank:
                results = [
                    obj for obj in results if obj.account.name == bank.title()
                ]
                # This page summary data needs to be
                # reviewed to accommodate different cases
                results_count = len(results)
                click.echo((
                    f'\n[Page {1}/{1}] '
                    f'Showing {results_count} results '
                    f'(Total: {results_count})\n'
                ))
            else:
                page_summary(response)

            for obj in results:
                title = f'\n{obj.account.name} {obj.type}'.upper()
                _format_transactions(obj, title)

@transaction.command
@click.option('-c', '--credit', is_flag=True)
@click.option('-d', '--debit', is_flag=True)
@click.option('-t', '--transfer', is_flag=True)
def create(
    credit: bool,
    debit: bool,
    transfer: bool,
) -> None:
    if not any([credit, debit, transfer]):
        message = (
            '🚨 Inform a type of transaction: '
            '-c (credit), -d (debit) or -t (transfer).'
        )
        console.print((
            '🚨 Inform a type of transaction:'
            '\n🏧 [bold][-t][/bold] or [bold][--transfer][/bold]'
            '\n🏧 [bold][-c][/bold] or [bold][--credit][/bold]'
            '\n🏧 [bold][-d][/bold] or [bold][--debit][/bold]'
        ))
        sys.exit(0)

    panel = Panel('[bold]+ ADD NEW TRANSACTION')
    console.print(panel)

    data: dict[str, Any] = {}
    data.update({'amount': Prompt.ask('💰 Amount R$', default=None)})
    console.rule('',style=None, align='left')
    data.update({'account': Prompt.ask('🏦 Account', default=None)})
    console.rule('',style=None, align='left')
    data.update({'send_to': Prompt.ask('🏦 Send to')}) if transfer else None
    console.rule('',style=None, align='left') if transfer else None
    data.update({'description': Prompt.ask('🗒️  Description', default=None)})
    console.rule('',style=None, align='left')
    data.update({'category': Prompt.ask('📂 Category', default=None)})
    console.rule('',style=None, align='left')
    data.update({'contact': Prompt.ask('👤 Contact', default=None)})
    console.rule('',style=None, align='left')

    if credit:
        data.update({'type': 'credit'})
    elif debit:
        data.update({'type': 'debit'})
    elif transfer:
        data.update({'type': 'transfer'})

    service = client.financial_transactions.create

    if obj := _handle_response(service, data):
        title = f'\n{obj.account.name} {obj.type}'.upper()
        _format_transactions(obj, title)

@transaction.command
@click.argument('id')
def get(id: str) -> None:
    ''' Retrieve an specific transaction. '''
    service = client.financial_transactions.get
    if obj := _handle_response(service, resource_id=id):
        title = f'\n{obj.account.name} {obj.type}'.upper()
        _format_transactions(obj, title)

@transaction.command
@click.argument('ids', nargs=-1)
def delete(ids: str) -> None:
    ''' Delete an specific transaction. '''
    service = client.financial_transactions.delete

    while True:
        prompt = click.style('Proceed to deletion? [y/n] ', fg='red')
        confirmation = input(prompt)
        if confirmation == 'n':
            sys.exit(0)
        elif confirmation == 'y':
            break

    if len(ids) > 1:
        spinner()

    for id in ids:
        time.sleep(0.5)
        if _handle_response(service, resource_id=id):
            console.print('✅ Transaction deleted')

@transaction.command
@click.argument('search', required=False)
@click.option('-d', '--date')
@click.option('-s', '--start-date')
@click.option('-e', '--end-date')
@click.option('-b', '--bank')
@click.option('-l', '--limit', default=50)
@click.pass_context
def search(
    ctx,
    search: str,
    date: str,
    start_date: str,
    end_date: str,
    bank: str,
    limit: int,
    ) -> None:
    ''' Filter transactions. '''
    if not any([search, date, start_date, end_date]):
        click.echo(ctx.get_help())
        sys.exit(0)

    service = client.financial_transactions.filter

    if response := _handle_response(
        service,
        search=search,
        date=date,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    ):
        results = response.results
        if bank:
            results = [
                obj for obj in results if obj.account.name == bank.title()
            ]
            # This page summary data needs to be
            # reviewed to accommodate different cases
            results_count = len(results)
            click.echo((
                f'\n[Page {1}/{1}] '
                f'Showing {results_count} results '
                f'(Total: {results_count})\n'
            ))
        else:
            page_summary(response)

        for obj in results:
            title = f'\n{obj.account.name} {obj.type}'.upper()
            _format_transactions(obj, title)
