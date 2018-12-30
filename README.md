# environment_monitor

This script gathers local temperature & humidity sensor data, as well as outdoor temperatures from the NOAA CO-OPS APIs, stores in a local MySQL DB, and sends to an Adafruit IO dashboard.

## Getting Started

This app consists of 4 main components:
   1. main python script
   2. SQL interraction python script
   3. ini properties file
   4. MySQL database
   5. callAPI module (re-usable)
   
This script was designed to be run in Production on a Linux machine (Raspberry Pi for me), although it can also be run on Windows.

### Prerequisites

Non-standard Python Modules Required:
- requests (for making API calls)
- pymysql (for MySQL DB interraction, optional)
- AdafruitIO (sudo pip3 install adafruit-io)

MySQL database installed (optional)

.ini Properties file




## Known Issues

None