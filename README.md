# [NOTICE] This repo is being deprecated

I developed this integration because the official Home Assistant integration did not provide the information I needed, such as the total number of wireless devices per AP or ESSID. However, the [Unifi Network integration](https://www.home-assistant.io/integrations/unifi/) now supports this functionality, so I am deprecating my integration in favor of the official one, which is better supported and more efficiently coded. 

# Unifi Counter Sensor

This sensor shows the number of devices connected to your unifi APs and also
shows the devices per AP and per ESSID as attributes of the sensor.

![unifi sensor](https://github.com/clyra/homeassistant/blob/master/unifi_sensor.png?raw=true)

## Install

To install via the HACS UI on Home Assistant:
1. Visit the HACS Integrations pane
2. Select the three dots in the top right hand corner & select 'Custom repositories'
3. Add https://github.com/clyra/unifics as the Repository and select Integration as the category.
4. 'Unifi Counter Sensor' should now show up as a new integration, click Download.
5. Restart Home Assistant.
6. Configure the integration (as per the next section)

To manually install the integration:
1. Copy the `custom_components/unifics` folder and all of its files to your `config/custom_components` directory in Home Assistant.
2. Restart Home Assistant
3. Configure the integration (as per the next section)

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

