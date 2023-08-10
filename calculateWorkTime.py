from datetime import datetime
import pytz
import csv
from Server import get_store_schedule, get_store_status, get_store_time_zone
from Server import app

# using business hour and timezone to find utc time
def business_hour_utc(business_hour, timezone_str):
    # Parse business hour string into a datetime object
    business_hour_datetime = datetime.strptime(business_hour, "%H:%M:%S")

    # Get the timezone object for the given timezone_str
    timezone = pytz.timezone(timezone_str)

    # Combine the business hour datetime with the timezone
    business_hour_with_tz = timezone.localize(business_hour_datetime)

    # Convert the business hour to UTC
    business_hour_utc = business_hour_with_tz.astimezone(pytz.UTC)

    business_hour_utc = business_hour_utc.strftime("%Y-%m-%d %H:%M:%S %Z")
    
    dt = datetime.strptime(business_hour_utc, "%Y-%m-%d %H:%M:%S %Z")

    # Extract time components (hours, minutes, seconds)
    hours = dt.hour
    minutes = dt.minute
    seconds = dt.second

    # Format the time as a string
    time_string = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return time_string

# calculating work time for a particular restaurant on a particular day
def business_hour_difference(start_time, end_time):
    # Parse business hour strings into datetime objects
    start_datetime = datetime.strptime(start_time, "%H:%M:%S")
    end_datetime = datetime.strptime(end_time, "%H:%M:%S")

    # Calculate the time difference
    time_difference = end_datetime - start_datetime

    # Extract the total seconds
    total_seconds = time_difference.total_seconds()

    return total_seconds/60

# storing work time for each restaurant on each of days
def findWorkTimeStore():
    # traverse all the store data
    storeWorkTime = {}

    # using get api from the database
    menu_hours_data = get_store_schedule()

    cnt = 0
    for x in menu_hours_data:
        # if cnt > 10:
        #     break
         
        store_id = x['store_id']
        day = x['day'] 
        start_time_local = x['start_time_local'] 
        end_time_local = x['end_time_local']

        tempArray = {}
        if store_id in storeWorkTime:
            tempArray = storeWorkTime[store_id]
        tempArray[day] = business_hour_difference(start_time_local, end_time_local)
        storeWorkTime[store_id] = tempArray

       
        # print(store_id, day, start_time_local, end_time_local)
        cnt = cnt + 1

    return storeWorkTime

    # find the difference
    # store in a object like {"store1": {0: 3, 1: 2, 2: 3}}


if __name__ == "__main__":
    with app.app_context():
        findWorkTimeStore()
    # Example usage
    # business_hour_str = "04:30:05"
    # timezone_str = "America/New_York"

    # utc_time = business_hour_utc(business_hour_str, timezone_str)


    # print(utc_time)
    # print("Business hour in UTC:", utc_time)
