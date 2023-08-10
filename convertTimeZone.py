import pytz
from datetime import datetime


def convert_to_utc(local_time_str, timezone_str):
    # Get the timezone object
    timezone = pytz.timezone(timezone_str)

    # Convert the local time string to a datetime object with the specified timezone
    local_time = datetime.strptime(local_time_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone)

    # Convert to UTC
    utc_time = local_time.astimezone(pytz.utc)

    return utc_time.strftime('%Y-%m-%d %H:%M:%S')


if(__name__ == "__main__"):
    local_time_str = '2023-08-04 15:30:00'
    timezone_str = 'America/New_York'

    utc_time_str = convert_to_utc(local_time_str, timezone_str)
    print("UTC Time:", utc_time_str)
