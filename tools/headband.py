from neurosdk.scanner import Scanner
from neurosdk.cmn_types import *
from time import sleep
from tools.logging import logger
from flask_json import json_response

import concurrent.futures
import traceback

def sensor_found(scanner, sensors):
    for index in range(len(sensors)):
        logger.debug("Sensor found: %s" % sensors[index])

def on_sensor_state_changed(sensor, state):
    logger.debug("Sensor {0} is {1}".format(sensor.name, state))

def on_battery_changed(sensor, battery):
    logger.debug("Batter: {0}".format(battery))

def on_signal_data_received(sensor, data):
    logger.debug(data)

class headband:
    def __init__():
        scanner = None
        sensors_info = None
        sensor = None
        ERROR_MSG = "Ooops.. Didn't work!"

    def scanner_search() -> list:
        global scanner
        global sensors_info
        try:
            scanner = Scanner([SensorFamily.SensorLEBrainBit])
            scanner.sensorsChanged = sensor_found
            scanner.start()
            logger.debug("Start searching for 5 seconds...")
            sleep(5)
            scanner.stop()
            sensors_info = scanner.sensors()

            if not len(sensors_info):
                logger.error("No sensors found!!")
                logger.error("Please try 1) turn on headband, 2) put on headband, \
                            and 3) stay in the bluetooth range (within 2 meters)")
                return None
            
        except Exception as err:
            ex_data = str(Exception) + '\n'
            ex_data = ex_data + str(err) + '\n'
            ex_data = ex_data + traceback.format_exc()
            logger.error(ex_data)
            return None
        return sensors_info

    def sensor_connect():
        global sensor
        if sensors_info is None:
            logger.error("No sensors to connect!")
            logger.error("Please press scanner_search button \
                        to search for sensors first")
            # TODO: what to return

        current_sensor_info = sensors_info[0]
        logger.debug(current_sensor_info)

        def device_connection(sensor_info):
            return scanner.create_sensor(sensor_info)
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(device_connection, current_sensor_info)
            sensor = future.result()
            tutorial = open("Tutorial_Page.html").read().format(ConStatus='Connected')
            logger.debug("Device connected")

        sensor.sensorStateChanged = on_sensor_state_changed
        sensor.batteryChanged = on_battery_changed

    def start_signal():
        if sensor.is_supported_feature(SensorFeature.FeatureSignal):
            sensor.signalDataReceived = on_signal_data_received

        if sensor.is_supported_command(SensorCommand.CommandStartSignal):
            sensor.exec_command(SensorCommand.CommandStartSignal)
            logger.debug("Start signal")
            sleep(5)
            # TODO: when to stop receiving signal
            # sensor.exec_command(SensorCommand.CommandStopSignal)
            # logger.debug("Stop signal")
        else:
            logger.error("Something wrong with headband connection!")
            logger.error("Please reconnect headband")

    def stop_signal():
        sensor.exec_command(SensorCommand.CommandStopSignal)
        logger.debug("Stop signal")

    def sensor_disconnect():
        global scanner
        global sensor
        sensor.disconnect()
        logger.debug("Disconnect from sensor")
        del sensor
        logger.debug("Removed scanner")
        del scanner
    
