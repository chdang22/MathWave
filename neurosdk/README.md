# Python NeuroSDK 2

Welcome to the Python NeuroSDK 2. The Neurosdk library is designed to work with BrainBit, BrainBitBlack, Callibri and Kolibri devices. The library is intended for python version 3.7 and higher, Windows version 10 and higher.

## Documentation

- [Installing](#installing)
- [Description](#description)
- [Searching device](#searching-device)
- [Connection](#connection)
- [Parameters](#paramaters)
- [Receiving signal](#receiving-signal)
- [Receiving resistance](#receiving-resistance)
- [Electrodes connection](#electrodes-connection)
- [Clean up](#clean_up)

## Installing

```
pip install pyneurosdk2
```

## Description

The package has the following structure:
 - neurosdk - the main package with the implementation of methods
 - sample - is into the neurosdk package, file `sample.py`
 - libs - also into neurosdk package, contain dll library files

The library provides three main modules:

- scanner - to search for devices

```python
from neurosdk.scanner import Scanner
```

- sensor - methods of interaction with the device

```python
from neurosdk.callibri_sensor import CallibriSensor
from neurosdk.brainbit_sensor import BrainBitSensor
from neurosdk.brainbit_black_sensor import BrainBitBlackSensor
```

- types - implementation of all types of the library, you can either connect everything or only those necessary for a specific task

```python
from neurosdk.cmn_types import *
```

## Searching device

The `Scanner` class is used to search for a device. For a correct search, you must specify the list of device types. You can search for one or more device types at the same time. For example, to search for BrainBit and Callibri, you need to create a scanner as follows:

```python
scanner = Scanner([SensorFamily.SensorLEBrainBit, SensorFamily.SensorLECallibri])
```

Search start:

```python
scanner.start()
```

Stop search:

```python
scanner.stop()
```

All found devices can be obtained using the method:

```python
sensors = scanner.sensors()
```

During the search, an `sensorsChanged` callback will be called, which will display a list of found devices. If the device leaves the scanner's field of view for any reason, the device will disappear from the list after 12 seconds.

```python
def sensorFound(scanner, sensors):
   for i in range(len(sensors)):
       print('Sensor %s' % sensors[i])

scanner.sensorsChanged = sensorFound
```

The sensor's list will contain records of the SensorInfo type with fields:

- SensFamily: SensorFamily
- SensModel: int
- Name: str
- Address: str
- SerialNumber: str
- PairingRequired: bool

> Important!
> The serial number of the Callibri and Kolibri does not appear in the SensorInfo recieving during the search. To get this value, you need to connect to the device and request the serial number manually:
>
> ```python
> sn = sensor.serial_number
> ```


## Connection

Next, you can create any device from the list using the method:

```python
sensor = scanner.create_sensor(sensInfo)
```
When created, the device will connect automatically. This is a blocking function, so it is desirable to call it from an separate thread. Upon successful connection, a sensor instance will be returned. If unsuccessful, an exception is thrown. On subsequent connections and disconnections, a callback will be called indicating the state of the device.

To disconnect from the device, use the following method:

```python
sensor.disconnect()
```

To connect to a device created but not connected for any reason, the method:

```python
sensor.connect()
```

It is blocking too.

## Parameters

SDK allows you to get information about the connected device:

```python
print(sensor.sens_family)  # SensorFamily.SensorLEBrainBit
print(sensor.features)  # [<SensorFeature.FeatureSignal: 0>, ...]
print(sensor.commands)  # [<SensorCommand.CommandStartSignal: 0>,...]
print(sensor.parameters)
print(sensor.name)  # BrainBit
print(sensor.state)  # SensorState.StateInRange
print(sensor.address)  # AA:BB:CC:DD:EE:FF
print(sensor.serial_number)  # 123456
print(sensor.batt_power)  # 50
print(sensor.sampling_frequency)  # SensorSamplingFrequency.FrequencyHz250
print(sensor.gain)  # SensorGain.SensorGain6
print(sensor.data_offset)  # SensorDataOffset.DataOffset0
print(sensor.version)  # SensorVersion(FwMajor=50, FwMinor=0, FwPatch=0, HwMajor=1, HwMinor=0, HwPatch=0, ExtMajor=65)
```

>  You can distinguish BrainBit device from Flex by the firmware version number: if the `SensorVersion.FwMajor` is more than 100 - it's Flex, if it's less than BrainBit.

If you need to change any property, you first need to check if it is writable. This can be done by reading the list of device parameters, where each parameter will have an access level:

```
[ParameterInfo(Param=<SensorParameter.ParameterOffset: 8>, ParamAccess=<SensorParamAccess.ParamAccessRead: 0>),  
 ParameterInfo(Param=<SensorParameter.ParameterState: 1>,  ParamAccess=<SensorParamAccess.ParamAccessReadNotify: 2>)
 ...]
```

And also check the support of certain modules:

```python
sensor.is_supported_feature(sensor_future)
sensor.is_supported_command(sensor_command)
sensor.is_supported_parameter(sensor_parameter)
```

## Receiving signal

For any device that supports recieving signal, you can run the following commands for starting:

```python
sensor.exec_command(SensorCommand.CommandStartSignal)
```

Stop:

```python
sensor.exec_command(SensorCommand.CommandStopSignal)
```

### BrainBit, BrainBitBlack, Flex

You can get the signal value using the callback:

```python
def onBrainBitSignalDataReceived(sensor, data):
   print(data)

sensor.brainBitSignalDataReceived = onBrainBitSignalDataReceived
```

After you have finished working with the signal, you can unsubscribe from the callback as follows:

```python
sensor.brainBitSignalDataReceived = None
```

It gives a list of packages. Each package contains:
- PackNum: int
- Marker: int
- O1: float
- O2: float
- T3: float
- T4: float

It is values from 4 channels in volts, a number for each packet and a marker if it was sent and this feature is supported by the device.

### Callibri, Kolibri

You can get the signal value using the callback:

```python
def onCallibriSignalDataReceived(sensor, data):
   print(data)

sensor.callibriSignalDataReceived = onCallibriSignalDataReceived
```

After you have finished working with the signal, you can unsubscribe from the callback as follows:

```python
sensor.callibriSignalDataReceived = None
```

It gives a list of packages. Each package contains:
 - PackNum: int
 - Samples: [float]

It is values in volts and a number for each packet.

## Receiving resistance

Resistance is only supported by BrainBit, BrainBitBlack and Flex. You can also check the availability of these features using the method `sensor.IsSupportedFeature(SensorFeature.FeatureResist)`.

To get resistance values:

```python
def onBrainBitResistDataReceived(sensor, data):
    print(data)


sensor.brainBitResistDataReceived = onBrainBitResistDataReceived

sensor.exec_command(SensorCommand.CommandStartResist)
sensor.exec_command(SensorCommand.CommandStopResist)
```

The callback returns one packet of samples, each packet contains the resistance values in volts:
- O1: float
- O2: float
- T3: float
- T4: float

After you have finished working with the resistance, you can unsubscribe from the callback as follows:

```python
sensor.brainBitResistDataReceived = None
```

> BrainBit cannot be in the resistance and signal readout mode at the same time, so you must first get the resistance values, but only after this signal, or vice versa. For example:
> ```python
> sensor.exec_command(SensorCommand.CommandStartResist)
> sleep(10)
> sensor.exec_command(SensorCommand.CommandStopResist)
> ...
> sensor.exec_command(SensorCommand.CommandStartSignal)
> sleep(10)
> sensor.exec_command(SensorCommand.CommandStopSignal)
> ```

## Electrodes connection

Electrode placement check is available for Callibri and Kolibri devices. This data shows whether the electrodes are attached to the skin.

```python
def onCallibriElectrodeStateChanged(sensor, data):
   print(data)

sensor.callibriElectrodeStateChanged = onCallibriElectrodeStateChanged
```

For unsubscribe from callback:

```python
sensor.callibriElectrodeStateChanged = None
```

Electrodes state can be one of values of enum:
- ElStNormal = 0
- ElStHighResistance = 1
- ElStDetached = 2

To get the state of the electrodes, you need to start a signal from the device.You can receive electrode and signal values at the same time.

## Clean up

After you finish working with the device, you need to clean up the resources used. This happens in the destructor of the scanner and sensor, so if they were not called by the system, you must call them manually.

```python
del sensor
del scanner
```

## License

Copyright (c) Brainbit Inc. All rights reserved.

Licensed under the [MIT license](LICENSE).
