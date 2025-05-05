import depoc
import click
import sys
import time

from typing import Any

from rich.console import Console
from rich.console import group
from rich.panel import Panel
from rich.table import Table

from ..utils._response import _handle_response
from ..utils._format import spinner, _format_category


client = depoc.DepocClient()
console = Console()


@group()
def get_tables(tables: list):
    for table in tables:
        yield table


@click.group(invoke_without_command=True)
@click.pass_context
@click.option('-l', '--limit', default=50)
@click.option('-p', '--page', default=0)
def category(ctx, limit: int, page: int) -> None:
    ''' Manage financial categories '''
    if ctx.invoked_subcommand is None:
        service = client.financial_categories.all

        if response := _handle_response(service, limit=limit, page=page):
            # I want to include the is_active
            # attr into the categories dict
            categories: dict[str, dict] = {}
            for obj in response.results:
                if not obj.parent:
                    categories.update({obj.name: {'id': obj.id}})

            for obj in response.results:
                if obj.parent:
                    parent = obj.parent
                    while parent:
                        if parent.name not in categories.keys():
                            child = categories[parent.parent.name][parent.name]
                            if child:
                                child.update({
                                    'id': parent.id,
                                    obj.name: {'id': obj.id}
                                })
                        elif obj.parent.name in categories.keys():
                            categories[parent.name].update({
                                obj.name: {'id': obj.id}
                            })
                        parent = parent.parent

            for k, v in categories.items():
                table = Table(
                    show_header=True,
                    show_footer=True,
                    box=None,
                    expand=True,
                    )
                
                table.add_column('', justify='left', no_wrap=True)
                table.add_column('', justify='right', no_wrap=True)

                tables = [table]

                for name, value in v.items():
                    if isinstance(value, dict):
                        if len(value) > 1:
                            sub = Table(
                                show_header=True,
                                show_footer=True,
                                box=None,
                                expand=True,
                            )

                            sub.add_column(name, justify='left', no_wrap=True)
                            sub.add_column(value['id'], justify='right', no_wrap=True)

                            for a, b in value.items():
                                if a != 'id':
                                    sub.add_row(
                                        f'[bright_black]{a}',
                                        f'[bright_black]{b['id']}'
                                    )
                            tables.append(sub)
                        else:
                            table.add_row(name, value['id'])

                group = get_tables(tables)

                profile = Panel(
                    group,
                    title=f'[bold]{k.upper()}',
                    title_align='left',
                    subtitle=v['id'],
                    subtitle_align='left',
                )

                console.print(profile)

@category.command
@click.argument('name')
@click.option('-p', '--parent', help='Inform the Parent Caregory if any.')
def create(name: str, parent: str) -> None:
    ''' Create a new category. '''
    data: dict[str, Any] = {'name': name}
    data.update({'parent': parent}) if parent else None

    service = client.financial_categories.create
    if obj := _handle_response(service, data):
        _format_category(obj, highlight=True)


@category.command
@click.argument('id')
def get(id: str) -> None:
    ''' Retrieve an specific category '''
    service = client.financial_categories.get
    if obj := _handle_response(service, resource_id=id):
        _format_category(obj)

@category.command
@click.argument('id')
@click.option('--name', help='Inform the new name for the Category.')
@click.option('--parent', help='Inform the Parent Caregory if any.')
@click.option('--activate', is_flag=True, help='Activate category.')
def update(id: str, name: str, parent: str, activate: bool) -> None:
    ''' Update a category '''
    data: dict[str, Any] = {}
    data.update({'name': name}) if name else None
    data.update({'parent': parent}) if parent else None
    data.update({'is_active': True}) if activate else None

    service = client.financial_categories.update

    if obj := _handle_response(service, data, id):
        _format_category(obj, highlight=True)

@category.command
@click.argument('ids', nargs=-1)
def delete(ids: str) -> None:
    ''' Delete a category '''
    service = client.financial_categories.delete

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
            console.print('✅ Category inactivated')
