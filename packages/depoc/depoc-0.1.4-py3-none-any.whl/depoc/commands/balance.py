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
def balance(ctx, date: str, start_date: str, end_date: str) -> None:
    ''' Balance for a specific period. '''
    caption = date
    if start_date and end_date:
        caption = f'{start_date} → {end_date}'
    elif date in ('week', 'month'):
        caption = f"this {date}'s balance"
    elif date == 'today':
        caption = f"today's balance"

    income: float = 0
    expenses: float = 0
    balance: float = 0
    
    service = client.financial_transactions.filter

    if response := _handle_response(
        service,
        date=date,
        start_date=start_date,
        end_date=end_date,
        ):
        for obj in response.results:
            if obj.type == 'credit':
                income += float(obj.amount)
            elif obj.type == 'debit':
                expenses += float(obj.amount)

        balance = round(income + expenses, 2)

        table = Table(
            show_header=True,
            show_footer=True,
            box=None,
            expand=True,
            caption=caption,
            title=f'[bold]R${balance:,.2f}'
            )
        
        table.add_column('', justify='left', no_wrap=True)
        table.add_column('', justify='right', no_wrap=True)
        table.add_row('📈 Income', f'R${income:,.2f}')
        table.add_row('📉 Expenses', f'R${abs(expenses):,.2f}')

        border_style = 'red' if balance < 0 else 'green'

        profile = Panel(
            table,
            title=f'[bold]BALANCE',
            title_align='left',
            border_style=border_style,
        )

        console = Console()
        console.print(profile)