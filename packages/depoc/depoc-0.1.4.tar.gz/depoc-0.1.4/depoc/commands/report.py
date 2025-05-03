import depoc
import click

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .utils._response import _handle_response


client = depoc.DepocClient()


@click.command
@click.option('-d', '--date', default='week')
@click.option('-s', '--start-date')
@click.option('-e', '--end-date')
@click.pass_context
def report(ctx, date: str, start_date: str, end_date: str) -> None:
    ''' Financial report for a specific period. '''
    caption = date
    if start_date and end_date:
        caption = f'{start_date} → {end_date}'
    elif date in ('week', 'month'):
        caption = f"this {date}'s report"
    elif date == 'today':
        caption = f"today's report"

    current_balance: float = 0
    total_receivable: float = 0
    total_payable: float = 0
    
    banks = client.financial_accounts.all
    receivables = client.receivables.filter
    payables = client.payables.filter

    if banks_response := _handle_response(banks):
        for obj in banks_response.results:
            current_balance += float(obj.balance)

    if receivables_response := _handle_response(
        receivables,
        date=date,
        start_date=start_date,
        end_date=end_date,
    ):  
        for obj in receivables_response.results:
            total_receivable += float(obj.outstanding_balance)

    if payables_response := _handle_response(
        payables,
        date=date,
        start_date=start_date,
        end_date=end_date,
    ):
        for obj in payables_response.results:
            total_payable += float(obj.outstanding_balance)

        total_balance = round(
            current_balance + total_receivable - total_payable, 2
        )

        table = Table(
            show_header=True,
            show_footer=True,
            box=None,
            expand=True,
            caption=caption,
            title=f'[bold]R${total_balance:,.2f}'
            )
        
        table.add_column('', justify='left', no_wrap=True)
        table.add_column('', justify='right', no_wrap=True)
        table.add_row('💰 Balance', f'R${current_balance:,.2f}')
        table.add_row('📈 Receivables', f'R${total_receivable:,.2f}')
        table.add_row('📉 Payables', f'R${abs(total_payable):,.2f}')

        border_style = 'red' if total_balance < 0 else 'green'

        profile = Panel(
            table,
            title=f'[bold]REPORT',
            title_align='left',
            border_style=border_style,
        )

        console = Console()
        console.print(profile)