#!/usr/bin/python3
# eric.loeliger@gmail.com

# Change Log
# 8/17/17 - created
# 8/27/17 - Added insertMeterReading
# 12/29/17 - Changed from #!/usr/local/bin/python3.6 to #!/usr/bin/python3
# 12/30/17 - added insertMeterReadings which has all readings in a single row

import pymysql
import logging
import configparser

# load properties from file
config = configparser.ConfigParser()
# THIS HAS TO BE CHANGED ON LINUX !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#config.read('environment_monitor_properties.ini')
config.read('//home/pi/Python_Scripts/environment_monitor/environment_monitor_properties.ini')

# DEBUG switch  0 = Production, 1 = debug
#debugMode = 1
debugMode = int(config['general']['DebugMode'])

# Logger configuration
log_name = config['logger.config']['LogName']
log_path_linux = config['logger.config']['LogPathLinux']

logger = logging.getLogger('environment_monitor_sql.py')
if debugMode == 0:
    ## Linux
    handler = logging.FileHandler('%s%s' % (log_path_linux,  log_name))
else:
    ## Windows
    handler = logging.FileHandler('%s'% log_name)
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

# Database properties
db_host_win = config['database.windows']['host']
db_user_win = config['database.windows']['user']
db_pwd_win = config['database.windows']['password']
db_name_win = config['database.windows']['db']

db_host_linux = config['database.linux']['host']
db_user_linux = config['database.linux']['user']
db_pwd_linux = config['database.linux']['password']
db_name_linux = config['database.linux']['db']


if debugMode == 1:
    logger.info("############################# DEBUG Mode #############################")


## opens the DB connection
def openDBConnection():
    logger.info("***Begin openDBConnection function***")
    global connection
    
    # Connect to the database
    if debugMode == 0:
        ## Linux
        
        connection = pymysql.connect(host='%s' % db_host_linux, port=3306,
                                 user='%s' % db_user_linux,
                                 passwd='%s' % db_pwd_linux,
                                 db='%s' % db_name_linux,
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    else:
        ## Windows
        #global connection
        connection = pymysql.connect(host='%s' % db_host_win,
                                 user='%s' % db_user_win,
                                 passwd='%s' % db_pwd_win,
                                 db='%s' % db_name_win,
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    logger.info("***End openDBConnection function***")    


## Closes the DB connection once all activities are done
def closeDBConnection():
    logger.info("***Begin closeDBConnection function***")
    connection.close()
    logger.info("***End closeDBConnection function***")


# depreciated function - no longer used
def insertMeterReading(insert_dict):
    logger.info("***Begin insertMeterReading function***")
    with connection.cursor() as cursor:
        # Create a new record
        # columns: id (auto), type_code, value, sensor_id, timestamp (auto)
        sql = "INSERT INTO meter_reading (type_code,value,sensor_id,timestamp)  VALUES(%s,%s,%s,NOW())"
        result = cursor.execute(sql, (insert_dict['type_code'],insert_dict['value'],insert_dict['sensor_id']))
        cursor.close()
        logger.debug("Query: %s" % cursor._last_executed)
        logger.debug("Result: %s" % result)

    # connection is not autocommit by default. So you must commit to save
    # your changes.
    connection.commit()
    logger.info("***End insertMeterReading function***")
    return(result)

# current function
def insertMeterReadings(insert_dict):
    logger.info("***Begin insertMeterReading function***")
    with connection.cursor() as cursor:
        # Create a new record
        # columns: id (auto), sensor_id, indoor_temperature, indoor_humidity, timestamp (auto), outdoor_temperature, outdoor_timestamp
        sql = "INSERT INTO meter_reading (sensor_id,indoor_temperature,indoor_humidity,timestamp,outdoor_temperature,outdoor_timestamp)  VALUES(%s,%s,%s,NOW(),%s,%s)"
        result = cursor.execute(sql, (insert_dict['sensor_id'],insert_dict['indoor_temperature'],insert_dict['indoor_humidity'],insert_dict['outdoor_temperature'],insert_dict['outdoor_timestamp']))
        cursor.close()
        logger.debug("Query: %s" % cursor._last_executed)
        logger.debug("Result: %s" % result)

    # connection is not autocommit by default. So you must commit to save
    # your changes.
    connection.commit()
    logger.info("***End insertMeterReading function***")
    return(result)

def selectMeterReadings(select_dict):
    logger.info("***Begin insertMeterReading function***")
    #with connection.cursor() as cursor:
    with connection.cursor(pymysql.cursors.DictCursor) as cursor:
        # columns: id (auto), type_code, value, sensor_id, timestamp (auto)
        sql = "SELECT t.sensor_id,t.type_code,t.value,t.timestamp FROM (SELECT * FROM meter_reading WHERE type_code in (%s) order by id desc limit %s) as t order by t.id" % (select_dict['type_code'],select_dict['limit'])
        logger.debug("Limit: %s" % select_dict['limit'])
        result_number = cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()
        logger.debug("Query: %s" % cursor._last_executed)
        logger.debug("Result: %s" % result)
    logger.info("***End insertMeterReading function***")
    return(result)    
    
