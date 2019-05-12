import time
import numpy as np
import paho.mqtt.client as mqtt

client = mqtt.Client()
client.connect("localhost", 1883, 60)
while True:
    print("send")
    client.publish("testing", np.random.normal(0))
    time.sleep(0.5)
