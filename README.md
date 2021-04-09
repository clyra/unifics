# Unifi Counter Sensor

This sensor shows the number of devices connected to your unifi APs and also
shows the devices per AP and per ESSID as attributes of the sensor.

![unifi sensor](https://github.com/clyra/homeassistant/blob/master/unifi_sensor.png?raw=true)

## Install

Copy unifics folder to your home-assistant custom_components folder.

TODO: hacs install

## Configure

The sensor can be configured in the UI or using a yaml file:

```yaml
sensor:
   - platform: unifics
     name: <whatever you want> (optional, default: "Unifi Couter Sensor")
     host: <your unifi controller ip or dns name>
     port: <controller port> (optional, default: 8443)
     username: <unifi_controller_username>
     password: <unifi_controller_password>
     site: <your "site" on controller> (optional, default: 'default')
     verify_ssl: <True/False> (optional, default: 'False')
     udm: <True/False> (optional, default: 'False'. If you have a device running UniFiOS such as a Unifi Dream Machine then use 'True' as the API is different.)
```

