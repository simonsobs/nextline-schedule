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
MUTATE_AUTO_MODE_TURN_ON = read_gql(sub / 'AutoModeTurnOn.gql')
MUTATE_AUTO_MODE_TURN_OFF = read_gql(sub / 'AutoModeTurnOff.gql')
MUTATE_QUEUE_PUSH = read_gql(sub / 'QueuePush.gql')

sub = pwd / 'queries'
QUERY_AUTO_MODE = read_gql(sub / 'AutoMode.gql')
QUERY_SCHEDULER = read_gql(sub / 'Scheduler.gql')
QUERY_VERSION = read_gql(sub / 'Version.gql')
QUERY_SCHEDULE_QUEUE_ITEMS = read_gql(sub / 'QueueItems.gql')

sub = pwd / 'subscriptions'
SUBSCRIBE_AUTO_MODE_STATE = read_gql(sub / 'ScheduleAutoModeState.gql')
