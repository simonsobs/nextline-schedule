from pathlib import Path

pwd = Path(__file__).resolve().parent

sub = pwd / 'mutations'
MUTATE_AUTO_MODE_TURN_ON = (sub / 'AutoModeTurnOn.gql').read_text()
MUTATE_AUTO_MODE_TURN_OFF = (sub / 'AutoModeTurnOff.gql').read_text()


sub = pwd / 'queries'
QUERY_AUTO_MODE = (sub / 'AutoMode.gql').read_text()
QUERY_SCHEDULER = (sub / 'Scheduler.gql').read_text()

sub = pwd / 'subscriptions'
SUBSCRIBE_AUTO_MODE_STATE = (sub / 'ScheduleAutoModeState.gql').read_text()
