from neurosdk.scanner import Scanner
from neurosdk.cmn_types import *

import concurrent.futures
from time import sleep

from tools.logging import logger

def sensor_found(scanner, sensors):
    for index in range(len(sensors)):
        print('Sensor found: %s' % sensors[index])


def on_sensor_state_changed(sensor, state):
    print('Sensor {0} is {1}'.format(sensor.name, state))


def on_battery_changed(sensor, battery):
    print('Battery: {0}'.format(battery))


def on_signal_data_received(sensor, data):
    print(data)


def on_resist_data_received(sensor, data):
    print(data)


def on_electrodes_state_changed(sensor, data):
    print(data)


def on_envelope_received(sensor, data):
    print(data)


def on_respiration_data_received(sensor, data):
    print(data)

def start_scanner():
    try:
        scanner = Scanner([SensorFamily.SensorLEBrainBitBlack, SensorFamily.SensorLEBrainBit,
                        SensorFamily.SensorLECallibri])

        scanner.sensorsChanged = sensor_found
        scanner.start()
        print("Starting search for 5 sec...")
        sleep(5)
        scanner.stop()

        sensorsInfo = scanner.sensors()

        if not len(sensorsInfo):
            logger.debug("No sensor Found!")

        for i in range(len(sensorsInfo)):
            current_sensor_info = sensorsInfo[i]
            print(sensorsInfo[i])


            def device_connection(sensor_info):
                return scanner.create_sensor(sensor_info)


            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(device_connection, current_sensor_info)
                sensor = future.result()
                print("Device connected")

            sensor.sensorStateChanged = on_sensor_state_changed
            sensor.batteryChanged = on_battery_changed

            sensFamily = sensor.sens_family

            print(sensFamily)
            print(sensor.features)
            print(sensor.commands)
            print(sensor.parameters)
            print(sensor.name)
            print(sensor.state)
            print(sensor.address)
            print(sensor.serial_number)
            print(sensor.batt_power)
            print(sensor.sampling_frequency)
            print(sensor.gain)
            print(sensor.data_offset)
            print(sensor.version)

            if sensor.is_supported_feature(SensorFeature.FeatureSignal):
                sensor.signalDataReceived = on_signal_data_received

            if sensor.is_supported_feature(SensorFeature.FeatureResist):
                sensor.resistDataReceived = on_resist_data_received

            if sensor.is_supported_feature(SensorFeature.FeatureRespiration):
                sensor.respirationDataReceived = on_respiration_data_received

            if sensor.is_supported_feature(SensorFeature.FeatureEnvelope):
                sensor.envelopeDataReceived = on_envelope_received

            if sensor.is_supported_command(SensorCommand.CommandStartSignal):
                sensor.exec_command(SensorCommand.CommandStartSignal)
                print("Start signal")
                sleep(5)
                sensor.exec_command(SensorCommand.CommandStopSignal)
                print("Stop signal")

            if sensor.is_supported_command(SensorCommand.CommandStartResist):
                sensor.exec_command(SensorCommand.CommandStartResist)
                print("Start resist")
                sleep(5)
                sensor.exec_command(SensorCommand.CommandStopResist)
                print("Stop resist")

            if sensor.is_supported_command(SensorCommand.CommandStartEnvelope):
                sensor.exec_command(SensorCommand.CommandStartEnvelope)
                print("Start envelope")
                sleep(5)
                sensor.exec_command(SensorCommand.CommandStopEnvelope)
                print("Stop envelope")

            if sensor.is_supported_command(SensorCommand.CommandStartRespiration):
                sensor.exec_command(SensorCommand.CommandStartRespiration)
                print("Start respiration")
                sleep(5)
                sensor.exec_command(SensorCommand.CommandStopRespiration)
                print("Stop respiration")

            if sensor.is_supported_command(SensorCommand.CommandStartCurrentStimulation):
                sensor.exec_command(SensorCommand.CommandStartCurrentStimulation)
                print("Start CurrentStimulation")
                sleep(5)
                sensor.exec_command(SensorCommand.CommandStopCurrentStimulation)
                print("Stop CurrentStimulation")

            sensor.disconnect()
            print("Disconnect from sensor")
            del sensor

        del scanner
        return ('Remove scanner')
    except Exception as err:
        print("An error occurred!!!!")
        return (err)
