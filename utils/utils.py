import inspect
import datetime
import pytz
import click


def fname():
    return inspect.stack()[1][3]


def log(msg, f, path, level=1):

    stamp = "{}".format(datetime.datetime.now().strftime("[%d/%m/%y %H:%M:%S]"))

    # Colour codes for different error levels
    colors = ["cyan", "green", "yellow", "red"]

    # Labels for different log levels
    log_levels = ["[Debug]", "[Info]", "[Warning]", "[Error]"]

    click.echo('{}{} "{}:{}" {}'.format(stamp, click.style(log_levels[level], fg=colors[level]), path, f, msg))


def get_time_in_france():
    naive_dt = datetime.datetime(2013, 9, 3, 16, 0)
    dt = pytz.timezone("Europe/Paris").localize(naive_dt, is_dst=None)
    now = dt.now()
    now += datetime.timedelta(hours=1)
    now = datetime.datetime(
        year=now.year,
        day=now.day,
        hour=now.hour,
        minute=now.minute,
        month=now.month
    )

    return now.strftime("%I:%M %p")


