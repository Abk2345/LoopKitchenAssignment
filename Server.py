from flask import Flask, request, jsonify
import pytz
import sys
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
import csv

# from calculateWorkTime import business_hour_utc


from findWhichDay import findDay

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://abk45@localhost:5432/LoopKitchenStores'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# database tables
class StoreStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.BigInteger, nullable=False)
    active_status = db.Column(db.String(60), nullable=False)
    timestamp_utc = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, store_id, active_status, timestamp_utc):
       self.store_id = store_id
       self.active_status = active_status
       self.timestamp_utc = timestamp_utc

    def __repr__(self):
        return f"StoreStatus<{self.id}>"
    
    def serialise(self):
        return {'store_id': self.store_id, 'active_status': self.active_status, 'timestamp_utc': self.timestamp_utc}

class StoreSchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.BigInteger, nullable=False)
    day = db.Column(db.Integer, nullable=False)
    start_time_local = db.Column(db.String(100))
    end_time_local = db.Column(db.String(100))

    def __init__(self, store_id, day, start_time_local, end_time_local):
       self.store_id = store_id
       self.day = day
       self.start_time_local = start_time_local
       self.end_time_local = end_time_local

    def __repr__(self):
        return f"StoreSchedule<{self.id}>"
    
    def serialise(self):
        return {'store_id': self.store_id, 'day': self.day, 'start_time_local': self.start_time_local, 'end_time_local': self.end_time_local}

class StoreTimeZone(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    store_id = db.Column(db.BigInteger, nullable=False)
    time_zone = db.Column(db.String(160), nullable=False)

    def __init__(self, store_id, time_zone):
        self.store_id = store_id
        self.time_zone = time_zone

    def __repr__(self):
        return f"StoreTimeZone<{self.id}>"
    
    def serialise(self):
        return {'store_id': self.store_id, 'time_zone': self.time_zone}

class StoreReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.BigInteger, nullable=False)
    upTimeLastHour_min = db.Column(db.Float, nullable=False)
    upTimeLastDay_hour = db.Column(db.Float, nullable=False)
    upTimeLastWeek_hour = db.Column(db.Float, nullable=False) 
    downTimeLastHour_min = db.Column(db.Float, nullable=False)
    downTimeLastDay_hour = db.Column(db.Float, nullable=False)
    downTimeLastWeek_hour = db.Column(db.Float, nullable=False) 

    def __init__(self, store_id, upTimeLastHour_min, upTimeLastDay_hour, upTimeLastWeek_hour, downTimeLastHour_min, downTimeLastDay_hour, downTimeLastWeek_hour):
       self.store_id = store_id
       self.upTimeLastHour_min = upTimeLastHour_min
       self.upTimeLastDay_hour = upTimeLastDay_hour
       self.upTimeLastWeek_hour = upTimeLastWeek_hour
       self.downTimeLastDay_hour = downTimeLastDay_hour
       self.downTimeLastHour_min = downTimeLastHour_min
       self.downTimeLastWeek_hour = downTimeLastWeek_hour

    def __repr__(self):
        return f"StoreStatus<{self.id}>"
    
    def serialise(self):
        return {'store_id': self.store_id, 'upTimeLastHour': self.upTimeLastHour_min,
                'upTimeLastDay': self.upTimeLastDay_hour, 'upTimeLastWeek': self.upTimeLastWeek_hour, 'downTimeLastHour': self.downTimeLastHour_min,
                'downTimeLastDay': self.downTimeLastDay_hour, 'downTimeLastWeek': self.downTimeLastWeek_hour}
 
def has_decimal_seconds(input_string):
    try:
        # Parse the input string into a datetime object
        input_datetime = datetime.strptime(input_string, "%Y-%m-%d %H:%M:%S.%f %Z")
        
        # Check if microseconds are non-zero (indicating a decimal part)
        return input_datetime.microsecond != 0
    except ValueError:
        # If parsing fails, it means the input string doesn't have microseconds (no decimal)
        return False
    
# insert data from store status.csv to this
def insert_store_status():
    try:
        # Read the CSV file
        with open('./Data/store_status.csv', 'r') as csvfile:
            csv_data = csv.reader(csvfile)
            header = next(csv_data)  # Skip the header row
            print(header)

            cnt = 0
            for row in csv_data:
                # if(cnt < 1051913):
                #     cnt += 1
                #     continue
                store_id, active_status, timestamp_utc_str = row
                input_string = timestamp_utc_str

                

                # Parse the input string into a datetime object
                input_datetime = ""
                if has_decimal_seconds(input_string):
                    input_datetime = datetime.strptime(input_string, "%Y-%m-%d %H:%M:%S.%f %Z")
                else:
                    input_datetime = datetime.strptime(input_string, "%Y-%m-%d %H:%M:%S %Z")

                    

                

                # Convert the datetime object to UTC
                input_datetime_utc = input_datetime.astimezone(timezone.utc)

                # Format the result as a string without the decimal part
                formatted_utc_string = input_datetime_utc.strftime("%Y-%m-%d %H:%M:%S %Z")
                timestamp_utc = formatted_utc_string


                new_store_status = StoreStatus(store_id=store_id, active_status=active_status, timestamp_utc=timestamp_utc)
                db.session.add(new_store_status)
                db.session.commit()
                # cnt += 1

            
            print("Data from CSV file inserted successfully!")
    except Exception as e:
        print(e, file=sys.stderr)
        return str(e)

def insert_store_schedule():
    try:
        with open('./Data/menu_hours.csv', 'r') as csvfile:
            csv_data = csv.reader(csvfile)
            header = next(csv_data)
            print(header)

            for row in csv_data:
                store_id, day, start_time_local, end_time_local = row

                new_store_schedule = StoreSchedule(store_id=store_id, day=day, start_time_local=start_time_local, end_time_local=end_time_local)
                db.session.add(new_store_schedule)
                db.session.commit()
            print("Store Schedule Inserted")

    except Exception as e:
        print(e, file=sys.stderr)
        return str(e)

def insert_store_time_zone():
    try:
        with open('./Data/time_stamps.csv', 'r') as csvfile:
            csv_data = csv.reader(csvfile)
            header = next(csv_data)
            print(header)

            for row in csv_data:
                store_id, time_zone = row

                new_store_time_zone = StoreTimeZone(store_id=store_id, time_zone=time_zone)
                db.session.add(new_store_time_zone)
                db.session.commit()
            print("Store Timezone Inserted!")
    except Exception as e:
        print(e, file=sys.stderr)
        return str(e)

@app.route('/add_store_status', methods=['POST'])
def post_store_status():
 
    try:
        data = request.get_json()
        store_id = data['store_id']
        active_status = data['active_status']
        timestamp_utc_str = data['timestamp_utc']

        # Validate and convert the timestamp to datetime object
        timestamp_utc = datetime.strptime(timestamp_utc_str, '%Y-%m-%d %H:%M:%S')

        new_store_status = StoreStatus(store_id=store_id, active_status=active_status, timestamp_utc=timestamp_utc)
        db.session.add(new_store_status)
        db.session.commit()
        return "Successfully added Store status! "
    except Exception as e:
        print(e, file=sys.stderr)
        return str(e)
   
@app.route('/get_store_status', methods = ['GET'])
def get_store_status():
    try:
        data = StoreStatus.query.all()
        serialized_data = [entry.serialise() for entry in data]
        return serialized_data
    except Exception as e:
        print(e, file=sys.stderr)
        return (str(e))

@app.route('/get_store_schedule', methods=['GET'])
def get_store_schedule():
    try:
        data = StoreSchedule.query.all()
        serialized_data = [entry.serialise() for entry in data]
        return serialized_data
    except Exception as e:
        print(e, file=sys.stderr)
        return str(e)
    
@app.route('/get_store_timezone', methods = ['GET'])
def get_store_time_zone():
    try:
        data = StoreTimeZone.query.all()
        serialized_data = [entry.serialise() for entry in data]
        return serialized_data
    except Exception as e:
        print(e, file=sys.stderr)
        return (str(e))


if __name__ == "__main__":
    with app.app_context():
        app.run(debug=True)

        # creation of database
    #     db.create_all()
    #     print("Database created!")

    # //calculating the required 
    # business_hour_str = "04:30:05"
    # timezone_str = "America/Chicago"

    # utc_time = business_hour_utc(business_hour_str, timezone_str)


    # print(utc_time)

    # find which day it is in range of 0 to 6
    # find day for "2023-08-07 12:30:00 UTC"
    # datetime_str = "2023-08-11 12:30:00 UTC"
    # findDay(datetime_str)

    # business logic now is
    
