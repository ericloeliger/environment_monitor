#!/usr/bin/python3


# Change Log
# 8/17/17 - created
# 8/27/17 - Added removal of \r chars from sensor response, added saving to DB
# 12/29/17 - Changed from #!/usr/local/bin/python3.6 to #!/usr/bin/python3
# 12/30/17 - Changed to storing all meter readings in a single row, improved exception logging
# 12/31/17 - Added sending to adafruit IO

# To Do
# Add NOAA temp data



import logging
import configparser
from Adafruit_IO import *
from call_api import callApi
import environment_monitor_sql as sql

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

logger = logging.getLogger('environment_monitor.py')
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



if debugMode == 1:
    logger.info("############################# DEBUG Mode #############################")

# functions go here

# ######### Main Program ############



# program goes here
try:
    logger.info("########## Begin environment_monitor.py ##########")
    logger.info("Opening DB connection")
    sql.openDBConnection()
    # call API to get environment vaues
    
    # callApi(method, url, authType, authorization, accept, body, expectJSON):
    url = config['sensor.config']['Sensor1URL']
    sensor_id = config['sensor.config']['Sensor1ID']
    (response,response_code) = callApi('GET', url, None, None, None,"", 0)
    logger.debug("Raw binary response: %s" % response.encode('utf-8'))
    response = response.replace('\r', '')
    list_data = response.split(",")
    sensor_type = list_data[0]
    temperature = list_data[1]
    humidity = list_data[2]
    logger.debug("Parameter 1 =%s" % sensor_type)
    logger.debug("Parameter 2 =%s" % temperature)
    logger.debug("Parameter 3 =%s" % humidity)


    # call NOAA API to get outside temp
    noaa_base_url = config['noaa.api.config']['BaseURL']
    noaa_station_id = config['noaa.api.config']['StationID']
    noaa_date = config['noaa.api.config']['Date']
    noaa_units = config['noaa.api.config']['Units']
    noaa_timezone = config['noaa.api.config']['TimeZone']
    noaa_format = config['noaa.api.config']['Format']
    noaa_application = config['noaa.api.config']['Application']
    noaa_product = "air_temperature"
    logger.debug("Product: %s" % noaa_product)

    # build NOAA API URL
    noaa_url = ("%sstation=%s&product=%s&date=%s&units=%s&time_zone=%s&format=%s&application=%s" % (noaa_base_url, noaa_station_id, noaa_product, noaa_date, noaa_units, noaa_timezone, noaa_format, noaa_application))
    logger.debug("Full NOAA API URL: %s" % noaa_url)
    logger.info("Calling NOAA API")
    (response,response_code) = callApi('GET', noaa_url, None, None, None,"", 1)

    if response_code == 200:
        for x in response['data']:
            outdoor_temperature = float(x['v'])
            logger.info("Outdoor temperature: %s" % outdoor_temperature)
            outdoor_timestamp = x['t']
            logger.info("NOAA Time: %s" % outdoor_timestamp)
    else:
        logger.info("NOAA URL returned error - storing outdoor_temperature as NULL")
        outdoor_temperature = None
        outdoor_timestamp = None

    # save values in DB
    # insertMeterReading - columns: id (auto), type_code, value, sensor_id, timestamp (auto)
    # insertMeterReadings - columns: id (auto), sensor_id, indoor_temperature, indoor_humidity, outdoor_temperature, timestamp (auto)
    insert_dict = {}

    # depreciated 12/30/17
##    if temperature != None:
##        insert_dict['type_code'] = 1
##        insert_dict['value'] = temperature
##        insert_dict['sensor_id'] = sensor_id
##        result = sql.insertMeterReading(insert_dict)
##        logger.info("Insert temperature result: %s" % result)
##
##    if humidity != None:
##        insert_dict['type_code'] = 2
##        insert_dict['value'] = humidity
##        insert_dict['sensor_id'] = sensor_id
##        result = sql.insertMeterReading(insert_dict)
##        logger.info("Insert humidity result: %s" % result)

    insert_dict['sensor_id'] = sensor_id
    insert_dict['indoor_temperature'] = temperature
    insert_dict['indoor_humidity'] = humidity
    insert_dict['outdoor_temperature'] = outdoor_temperature
    insert_dict['outdoor_timestamp'] = outdoor_timestamp
    result = sql.insertMeterReadings(insert_dict)
    logger.info("Insert meter readings result: %s" % result)


    # sending to adafruit IO feed
    aio = Client(config['adafruit.io']['ClientKey'])

    # define feed dictionary
    feedDictionary = {}
    feedDictionary['indoorTemperature'] = {}
    feedDictionary['indoorHumidity'] = {}
    feedDictionary['outdoorTemperature'] = {}
    feedDictionary['indoorTemperature']['feedID'] = config['adafruit.io']['IndoorTemperatureFeedID1']
    feedDictionary['indoorHumidity']['feedID'] = config['adafruit.io']['IndoorHumidityFeedID1']
    feedDictionary['outdoorTemperature']['feedID'] = config['adafruit.io']['OutdoorTemperatureFeedID1']

    # add test data to feed dictionary
    feedDictionary['indoorTemperature']['value'] = temperature
    feedDictionary['indoorHumidity']['value'] = humidity
    feedDictionary['outdoorTemperature']['value'] = outdoor_temperature

    logger.debug("Adafruit feed dictionary: %s" % feedDictionary)

    for x in feedDictionary:
        logger.info("Sending %s value %s to Adafruit feed %s" % (x,feedDictionary[x]['value'],feedDictionary[x]['feedID'] ))
        aio.send(feedDictionary[x]['feedID'],feedDictionary[x]['value'])
        logger.info("%s sent successfully" % x)



except Exception as e:
    logger.exception("Exception occured: %s" % e)

finally:
    logger.info("Closing DB connection")
    sql.closeDBConnection()
    logger.info("########## End environment_monitor.py ##########")
