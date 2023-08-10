import pandas as pd
from datetime import datetime, timedelta, timezone
import csv
from findWhichDay import findDay
from calculateWorkTime import findWorkTimeStore
import sys
import time
from Server import get_store_schedule, get_store_status, get_store_time_zone, db, StoreReport
from Server import app


#  finding if the datetime string has seconds in decimal and then processing it later on in Server.py
def has_decimal_seconds(input_string):
    try:
        # Parse the input string into a datetime object
        input_datetime = datetime.strptime(input_string, "%Y-%m-%d %H:%M:%S.%f %Z")
        
        # Check if microseconds are non-zero (indicating a decimal part)
        return input_datetime.microsecond != 0
    except ValueError:
        # If parsing fails, it means the input string doesn't have microseconds (no decimal)
        return False


def findAllReports():

    report = {}

    wT = findWorkTimeStore()
    # user inputted datetime
    datetime_str = "2023-01-21 11:37:15"

    # Convert the datetime string to a datetime object using strptime()
    current_timestamp = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")

    # Define time intervals
    one_hour_ago = current_timestamp - timedelta(hours=1)
    one_day_ago = current_timestamp - timedelta(days=1)
    one_week_ago = current_timestamp - timedelta(weeks=1)

    dictStoresUpDay = {}
    dictStoreUpHour = {}
    dictStoreUpWeek = {}

    # print(one_week_ago, one_day_ago, one_hour_ago)

    # from the database get all store_status
    store_status_data = get_store_status()
    # print(store_status_data)

    # checking if the logic is right
    # test1: time_stamp = "2023-01-22 06:39:39"
    # test = "2023-01-21 11:33:15"
    # test_t = datetime.strptime(test, "%Y-%m-%d %H:%M:%S")

    # # timestamp_utc_str = test_t.astimezone(timezone.utc)

    # input_string = test_t.strftime("%Y-%m-%d %H:%M:%S %Z")
    # print(input_string)

    cnt = 0
    for x in store_status_data:
        # if cnt > 10:
        #     break
         
        store_id = x['store_id']
        active_status = x['active_status']
        timestamp_utc_str = x['timestamp_utc']
        # print(store_id, active_status, timestamp_utc_str)

        cnt += 1
        
        input_string = timestamp_utc_str.strftime("%Y-%m-%d %H:%M:%S")
        # print(store_id, active_status, timestamp_utc_str, input_string)

        # Parse the input string into a datetime object
        input_datetime = ""
        if has_decimal_seconds(input_string):
            input_datetime = datetime.strptime(input_string, "%Y-%m-%d %H:%M:%S.%f %Z")
        else:
            input_datetime = datetime.strptime(input_string, "%Y-%m-%d %H:%M:%S")

        formatted_utc_string = input_datetime.strftime("%Y-%m-%d %H:%M:%S")
        data1 = datetime.strptime(formatted_utc_string, "%Y-%m-%d %H:%M:%S")

        # ------------------------------------------------------------------------ #
        # //time difference = one_hour_ago, one_week_ago and one_day_ago
        formatted_one_hour = one_day_ago.strftime("%Y-%m-%d %H:%M:%S")
        data2 = datetime.strptime(formatted_one_hour, "%Y-%m-%d %H:%M:%S")

        timeDiff = data1 - data2
        # print(timeDiff.total_seconds())
        # print(timeDiff.total_seconds(), data1, data2)
       
        if timeDiff.total_seconds() > 0 and timeDiff.total_seconds() <= 86400:  # 3600 seconds = 1 hour, 604800 -> 1week, 86400 -> 1day
            if(active_status == "active"):
                pCnt = 0
                if(store_id in dictStoresUpDay):
                    pCnt = dictStoresUpDay[store_id]
                pCnt = pCnt + 1
                dictStoresUpDay[store_id] = pCnt
        
            # print("The time difference is greater than or equal to 1 week.")
        
        # hour wise
        # ------------------------------------------------------------------------ #
        # //time difference = one_hour_ago, one_week_ago and one_day_ago
        formatted_one_hour = one_hour_ago.strftime("%Y-%m-%d %H:%M:%S")
        data2 = datetime.strptime(formatted_one_hour, "%Y-%m-%d %H:%M:%S")

        timeDiff = data1 - data2
        # print(timeDiff.total_seconds())
        # print(timeDiff.total_seconds(), data1, data2)
       
        if timeDiff.total_seconds() > 0 and timeDiff.total_seconds() <= 3600:  # 3600 seconds = 1 hour, 604800 -> 1week, 86400 -> 1day
            # print("here : ",data1, data2, timeDiff.total_seconds())
            if(active_status == "active"):
                pCnt = 0
                if(store_id in dictStoreUpHour):
                    pCnt = dictStoreUpHour[store_id]
                pCnt = pCnt + 1
                dictStoreUpHour[store_id] = pCnt
    
            # print("The time difference is greater than or equal to 1 week.")

        # week wise
        # ------------------------------------------------------------------------ #
        # //time difference = one_hour_ago, one_week_ago and one_day_ago
        # one_hour_ago_n = one_week_ago.astimezone(timezone.utc)
        formatted_one_hour = one_week_ago.strftime("%Y-%m-%d %H:%M:%S")
        data2 = datetime.strptime(formatted_one_hour, "%Y-%m-%d %H:%M:%S")

        timeDiff = data1 - data2
        # print(timeDiff.total_seconds())
        # print(data1, data2)
       
        if timeDiff.total_seconds() > 0 and timeDiff.total_seconds() <= 604800:  # 3600 seconds = 1 hour, 604800 -> 1week, 86400 -> 1day
            # print("here week: ", timeDiff.total_seconds(), data1, data2)
            if(active_status == "active"): 
                pCnt = 0
                if(store_id in dictStoreUpWeek):
                    pCnt = dictStoreUpWeek[store_id]
                pCnt = pCnt + 1
                if(pCnt > 1):
                    print("count is : ", pCnt)
                dictStoreUpWeek[store_id] = pCnt


        

    # print(len(wT))
    # print(len(dictStoresUpDay))

    # ------------------------------------------------------------------------ #
    # day wise calculation
    formatted_datetime = one_day_ago.strftime("%Y-%m-%d %H:%M:%S")

    day_ = findDay(formatted_datetime)

    downTimeNewDay = {}
    upTimeNewDay = {}

    # calculate downtime -> print(wrT, upT)
    for (key, value) in dictStoresUpDay.items():
        upT = value*60
        if key in wT:
            vp = 0
            wrT = wT[key]
            # print(wrT, upT)
            if day_ in wrT:
                vp = int(wrT[day_])
                # //if uptime is greater than downtime
                # if vp < upT:
                #     continue
                upTimeNewDay[key] = upT
                downTimeNewDay[key] = vp - upT

    report['uptime_day_wise'] = upTimeNewDay
    report['downtime_day_wise'] = downTimeNewDay

    # ------------------------------------------------------------------------ #


    # hour wise data calculation
    formatted_datetime = one_hour_ago.strftime("%Y-%m-%d %H:%M:%S")

    day_ = findDay(formatted_datetime)

    # testing logic
    # test = "2023-01-21 11:33:15"
    # test_t = datetime.strptime(test, "%Y-%m-%d %H:%M:%S")

    # formatted_utc_string = test_t.strftime("%Y-%m-%d %H:%M:%S")
    # data1 = datetime.strptime(formatted_utc_string, "%Y-%m-%d %H:%M:%S")


    # # one_hour_ago_n = one_hour_ago.astimezone(timezone.utc)
    # formatted_one_hour = one_hour_ago.strftime("%Y-%m-%d %H:%M:%S")
    # data2 = datetime.strptime(formatted_one_hour, "%Y-%m-%d %H:%M:%S")

    # timeDiff = data2 - data1

    # print(data1, data2, timeDiff.total_seconds())
        

    downTimeNewHour = {}
    upTimeNewHour = {}

    # print(dictStoreUpHour)

    # # # calculate downtime
    cnt = 0
    for (key, value) in dictStoreUpHour.items():
        upT = value*60
        # print(wT, upT)
        if key in wT:
            vp = 0
            wrT = wT[key]
            # print(wrT, upT)
            
            if day_ in wrT:
                vp = int(wrT[day_])
                # print(upT, wrT, day_, store_id)
                # //if uptime is greater than downtime
                # if vp < upT:
                #     continue
                upTimeNewHour[key] = upT
                downTimeNewHour[key] = vp - upT
                
        cnt += 1
                

                # print(wrT, vp, upT)
    
    # print(downTimeNewHour)
    # print(upTimeNewHour)
    report['uptime_hour_wise'] = upTimeNewHour
    report['downtime_hour_wise'] = downTimeNewHour

    # ------------------------------------------------------------------------ #
    # week-wise calculation
        
    downTimeNewWeek = {}
    upTimeNewWeek = {}

    # # calculate downtime
    for (key, value) in dictStoreUpWeek.items():
        upT = value*60
        if key in wT:
            vp = 0
            wrT = wT[key]
            day_arr = [0, 1, 2, 3, 4, 5, 6]
            for day__ in day_arr:
                if day__ in wrT:
                    vp = vp + int(wrT[day__])
            # //if uptime is greater than downtime
            # if vp < upT:
            #     continue
            upTimeNewWeek[key] = upT
            downTimeNewWeek[key] = vp - upT
    
    # print(downTimeNewHour)
    # print(upTimeNewWeek)
    report['uptime_week_wise'] = upTimeNewWeek
    report['downtime_week_wise'] = downTimeNewWeek

    # print(report)

    return report


def delete_all_entries():
    try:
        # Delete all entries from the table
        num_deleted = db.session.query(StoreReport).delete()
        db.session.commit()
        return "All entries deleted successfully."
    except Exception as e:
        db.session.rollback()
        return f"Error: {str(e)}"          
 
def prepare_report():

    delete_all_entries()

    report__ = findAllReports()

    upTimeLastHour = report__['uptime_hour_wise']
    downTimeLastHour = report__['downtime_hour_wise']
    upTimeLastDay = report__['uptime_day_wise']
    downTimeLastDay = report__['downtime_day_wise']
    upTimeLastWeek = report__['uptime_week_wise']
    downTimeLastWeek = report__['downtime_week_wise']

    time_zones = get_store_time_zone()

    cnt = 0

    map_ = {}
    for x in time_zones:
        # if cnt > 100:
        #     break
        store_id = x['store_id']
        report_obj = {}
        if store_id in map_:
            continue
        else:
            map_[store_id] = "yes"
            if store_id in upTimeLastHour:
                report_obj['upTimeLastHour'] =  int(upTimeLastHour[store_id])
                report_obj['downTimeLastHour'] = int(downTimeLastHour[store_id])
            else:
                report_obj['upTimeLastHour'] = -999
                report_obj['downTimeLastHour'] = -999

            if store_id in upTimeLastDay:
                report_obj['upTimeLastDay'] = int(upTimeLastDay[store_id])//60
                report_obj['downTimeLastDay'] = int(downTimeLastDay[store_id])//60
            else:
                report_obj['upTimeLastDay'] = -999
                report_obj['downTimeLastDay'] = -999

            if store_id in upTimeLastWeek:
                report_obj['upTimeLastWeek'] = int(upTimeLastWeek[store_id])//60
                report_obj['downTimeLastWeek'] = int(downTimeLastWeek[store_id])//60
            else:
                report_obj['upTimeLastWeek'] = -999
                report_obj['downTimeLastWeek'] = -999

            new_store_time_zone = StoreReport(store_id, report_obj['upTimeLastHour'], report_obj['upTimeLastDay'], report_obj['upTimeLastWeek'],
                                                report_obj['downTimeLastHour'], report_obj['downTimeLastDay'], report_obj['downTimeLastWeek'])
            
        # print(store_id, report_obj['upTimeLastHour'], report_obj['upTimeLastDay'], report_obj['upTimeLastWeek'],
        #         report_obj['downTimeLastHour'], report_obj['downTimeLastDay'], report_obj['downTimeLastWeek'])
            db.session.add(new_store_time_zone)
            db.session.commit()
        cnt = cnt + 1
        

    print("Data insertion Complete!")
    return "Success"

# to check if make report api is alreading running
is_trigger_report_running = False
@app.route('/trigger_report', methods = ['GET'])
def trigger_report():
    try:
        print("Trigger report api is running !")
        global is_trigger_report_running
        start_time = time.time()    
        is_trigger_report_running = True
        prepare_report()
        end_time = time.time()
        time_diff = end_time - start_time
        print("Time taken for report generation and saving (in min) is: ", time_diff/60)
        time.sleep(5)
        is_trigger_report_running = False
        print("Success in running trigger report api!")
        return "Success"
    except Exception as e:
        print(e, file=sys.stderr)
        return (str(e))


@app.route('/get_report/<int:id>', methods = ['GET'])
def get_report(id):
    try:
        global is_trigger_report_running
        if not is_trigger_report_running:
            report_ = StoreReport.query.filter(StoreReport.store_id==int(id)).all()
            return [a.serialise() for a in report_]
        else:
            return "Report making is in progress"
   
    except Exception as e:
        print(e, file=sys.stderr)
        return (str(e))



if __name__ == "__main__":
    with app.app_context():
        # findAllReports() 
        # prepare_report()
        app.run(debug=True)
    
    

