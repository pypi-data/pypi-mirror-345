# ********************************************************************
#
#  $Id: helloworld.py 66199 2025-05-05 16:36:19Z seb $
#
#  An example that show how to use a  Yocto-Meteo
#
#  You can find more information on our web site:
#   Yocto-Meteo documentation:
#      https://www.yoctopuce.com/EN/products/yocto-meteo/doc.html
#   Python API Reference:
#      https://www.yoctopuce.com/EN/doc/reference/yoctolib-python-EN.html
#
# *********************************************************************
import sys

from yoctolib.yocto_api import YRefParam, YAPI
from yoctolib.yocto_temperature import YTemperature
from yoctolib.yocto_pressure import YPressure
from yoctolib.yocto_humidity import YHumidity


def die(msg):
    YAPI.FreeAPI()
    sys.exit(msg + ' (check USB cable)')


# the API use local USB devices through VirtualHub
errmsg = YRefParam()
if YAPI.RegisterHub("localhost", errmsg) != YAPI.SUCCESS:
    sys.exit("RegisterHub failed: " + errmsg.value)

# To use a specific device, invoke the script as
#   python helloworld.py [serial_number]
# or
#   python helloworld.py [logical_name]
target = 'any'
if len(sys.argv) > 1:
    target = sys.argv[1]

if target == 'any':
    # retrieve any humidity sensor
    sensor = YHumidity.FirstHumidity()
    if sensor is None:
        die('No module connected')
    target = sensor.get_serialNumber()

# retrieve specified functions
humSensor = YHumidity.FindHumidity(target + '.humidity')
pressSensor = YPressure.FindPressure(target + '.pressure')
tempSensor = YTemperature.FindTemperature(target + '.temperature')
if not tempSensor.isOnline():
    die("Yocto-Meteo '%s' not connected" % target)

print("Use device %s" % humSensor.get_serialNumber())
print("Temp      Pressure Humidity")
while humSensor.isOnline():
    print('%2.1f' % tempSensor.get_currentValue() + "°C   " +
          "%4.0f" % pressSensor.get_currentValue() + "mb  " +
          "%4.0f" % humSensor.get_currentValue() + "% (Ctrl-c to stop)  ")
    YAPI.Sleep(1000)
YAPI.FreeAPI()
