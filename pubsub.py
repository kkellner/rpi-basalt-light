# Handle MQTT publish / subscribe 

import time
import threading
import logging, logging.handlers
import paho.mqtt.client as mqtt
import json

logger = logging.getLogger('pubsub')

class Pubsub:

    mqttBrokerHost = "rpicontroller1.hyperboard.net"
    mqttBrokerPort = 1883
    #sensorQueueName = "yukon/basalt/PubsubA"

    # Node name example: yukon/node/basalt1/status
    queueNamespace = "yukon"
    nodeName = "basalt1"
    queueNodeStatus = queueNamespace + "/node/" + nodeName + "/status"

    # Device name example: yukon/device/basalt/driveway/basalt1/light/status
    locationName = "driveway"
    typeName = "basalt"
    deviceName = "light"
    queueDeviceStatus = queueNamespace + "/device/" + typeName + "/" +locationName + "/" + nodeName + "/" + deviceName + "/status"

    def __init__(self, motion):
        self.motion = motion

        # Connect to MQTT broker
        self.client = mqtt.Client(client_id=Pubsub.nodeName)
        mqttLogger = logging.getLogger('mqtt')
        self.client.enable_logger(mqttLogger)
        self.client.reconnect_delay_set(1, 30)
        self.client.max_queued_messages_set(10)

        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        deathPayload = "DISCONNECTED"
        self.client.will_set(Pubsub.queueNodeStatus, deathPayload, 0, True)

        self.client.connect_async(Pubsub.mqttBrokerHost,Pubsub.mqttBrokerPort,60)

        self.client.loop_start()

    ######################################################################
    # Publish the BIRTH certificates
    ######################################################################
    def publishBirth(self):
        self.publishNodeBirth()
        self.publishDeviceBirth()

    ######################################################################
    # Publish the NODE BIRTH certificate
    ######################################################################
    def publishNodeBirth(self):
        logger.info("Publishing Node Birth")
        payload = "ONLINE"
        self.client.publish(Pubsub.queueNodeStatus, payload, 0, True)

    ######################################################################
    # Publish the DEVICE BIRTH certificate
    ######################################################################
    def publishDeviceBirth(self):
        logger.info("Publishing Device Birth")
        payload = "TBD"
        self.client.publish(Pubsub.queueDeviceStatus, payload, 0, True)

    ######################################################################
    # Publish the NODE offline
    ######################################################################
    def publishNodeOffline(self):
        logger.info("Publishing Node Birth")
        payload = "OFFLINE"
        self.client.publish(Pubsub.queueNodeStatus, payload, 0, True)
        
    def on_connect(self, client, userdata, flags, rc):
        logger.info("Connected with result code "+str(rc))
        self.publishBirth()

    def on_disconnect(self, client, userdata, rc):
        logger.warn("Disconnected with result code "+str(rc))


    def shutdown(self):
        logger.info("Shutdown -- disconnect from MQTT broker")
        self.publishNodeOffline()
        self.client.loop_stop()
        self.client.disconnect()


    def testPub(self):
        data = {
            "lightState": "XYZ",
            "time" : time.time(),
            "otherdata" : "some data"
        }
        self.publishEventObject(Pubsub.queueDeviceStatus, data)


    def publishEventObject(self, eventQueue, eventData):
        data_out=json.dumps(eventData) # encode object to JSON
        return self.publishEventString(eventQueue, data_out)

    def publishEventString(self, eventQueue, eventString):
        logger.info("Publish to queue [%s] data: [%s]", eventQueue, eventString)
        msg_info = self.client.publish(eventQueue, eventString, qos=0)
        #msg_info.wait_for_publish()
        return msg_info


