from os import PathLike
from pathlib import Path

from graphql import parse, print_ast


def read_gql(path: PathLike | str) -> str:
    '''Load a GraphQL query from a file while checking its syntax.'''

    text = Path(path).read_text()
    parsed = parse(text)
    reformatted = print_ast(parsed)
    return reformatted


pwd = Path(__file__).resolve().parent

sub = pwd / 'mutations'
MUTATE_AUTO_MODE_TURN_ON = read_gql(sub / 'auto_mode' / 'TurnOn.gql')
MUTATE_AUTO_MODE_TURN_OFF = read_gql(sub / 'auto_mode' / 'TurnOff.gql')
MUTATE_AUTO_MODE_CHANGE_MODE = read_gql(sub / 'auto_mode' / 'ChangeMode.gql')
MUTATE_QUEUE_PUSH = read_gql(sub / 'queue' / 'Push.gql')
MUTATE_QUEUE_REMOVE = read_gql(sub / 'queue' / 'Remove.gql')
MUTATE_SCHEDULER_UPDATE = read_gql(sub / 'scheduler' / 'Update.gql')
MUTATE_SCHEDULER_LOAD_SCRIPT = read_gql(sub / 'scheduler' / 'LoadScript.gql')

sub = pwd / 'queries'
QUERY_VERSION = read_gql(sub / 'Version.gql')
QUERY_AUTO_MODE_STATE = read_gql(sub / 'auto_mode' / 'State.gql')
QUERY_AUTO_MODE_MODE = read_gql(sub / 'auto_mode' / 'Mode.gql')
QUERY_QUEUE_ITEMS = read_gql(sub / 'queue' / 'Items.gql')
QUERY_SCHEDULER = read_gql(sub / 'Scheduler.gql')

sub = pwd / 'subscriptions'
SUBSCRIBE_AUTO_MODE_STATE = read_gql(sub / 'ScheduleAutoModeState.gql')
SUBSCRIBE_AUTO_MODE_MODE = read_gql(sub / 'ScheduleAutoModeMode.gql')
SUBSCRIBE_QUEUE_ITEMS = read_gql(sub / 'ScheduleQueueItems.gql')
