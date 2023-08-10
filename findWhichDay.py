from datetime import datetime

# finding which day any datetime belongs to
def findDay(utc_datetime_str):
    # Parse the UTC datetime string into a datetime object
    utc_datetime = datetime.strptime(utc_datetime_str, "%Y-%m-%d %H:%M:%S")

    # Get the day of the week (0: Monday, 1: Tuesday, ..., 6: Sunday)
    day_of_week = utc_datetime.weekday()

    print("Day of the week:", day_of_week)

    return day_of_week
