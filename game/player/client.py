from . import management


def connection_checker(called_from, users, p=None, opp=None, rm=None, username=None):
    management.connection_checker(called_from=called_from, users=users, p=p, opp=opp, rm=rm, username=username)


def go_to_next_round(p, rd, rm):
    management.go_to_next_round(p, rd, rm)