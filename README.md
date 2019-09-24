# rpi-basalt-light
Raspberry PI software to control basalt light

state_topic: "yukon/device/basalt/driveway/rpibasalt1/light/status"


json_attributes_topic: "yukon/device/basalt/attributes"

Template:  {"lightState": <string>, "time": <float>}

Example value:
{"lightState": "NIGHT_LIGHT", "time": 1568429885.4490638}


Set the template in mqtt:

mosquitto_pub -h mqtt -u USERNAME -P PASSWORD -d -t "yukon/device/basalt/attributes" -m '{"lightState": "NIGHT_LIGHT", "time": 1568429885.4490638}' -r