#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
This module contains a Snips skill that repeats the last message that
your voice assistant has said on the site you are talking to.
"""

import paho.mqtt.client as mqtt
import json

# Result sentence
RESULT_SORRY = "Sorry, I don't remember what I said. I must have fallen asleep."

# MQTT topics
TTS_SAY = "hermes/tts/say"
DM_END_SESSION = "hermes/dialogueManager/endSession"
INTENT_SAY_IT_AGAIN = "hermes/intent/koan:SayItAgain"

# If this skill is supposed to run on the satellite,
# please get this mqtt connection info from <config.ini>
# Hint: MQTT server is always running on the master device
MQTT_HOST = 'localhost'
MQTT_PORT = 1883


class SayItAgain(object):
    """
    This skill repeats the last message that your voice assistant has said
    on the site you are talking to.
    """

    def __init__(self):
        """Initialize the skill."""

        # Create an empty dictionary that will hold the last message
        # of each siteId.
        self.last_messages = {}

        self.client = mqtt.Client()
        self.client.on_connect = self.subscribe_topics
        self.client.on_message = self.handle_message

        self.client.connect(MQTT_HOST, MQTT_PORT, 60)
        self.client.loop_forever()

    def subscribe_topics(self, client, userdata, flags, rc):
        """Subscribe to the MQTT topics we're interested in."""
        client.subscribe(TTS_SAY)
        client.subscribe(INTENT_SAY_IT_AGAIN)

    def handle_message(self, client, userdata, msg):
        """Handle the messages we have subscribed to."""

        if msg.topic == TTS_SAY:
            self.handle_say(client, userdata, msg)
        elif msg.topic == INTENT_SAY_IT_AGAIN:
            self.handle_say_again(client, userdata, msg)

    def handle_say(self, client, userdata, msg):
        """When Snips says something, save the text."""
        payload = json.loads(msg.payload)
        self.last_messages[payload["siteId"]] = payload["text"]

    def handle_say_again(self, client, userdata, msg):
        """When the user asks to repeat the last message, do it."""
        payload = json.loads(msg.payload)
        if payload["siteId"] in self.last_messages:
            # If we have saved a previous message for this siteId, repeat it.
            last_message = self.last_messages[payload["siteId"]]
            client.publish(DM_END_SESSION,
                           json.dumps({'text': last_message,
                                       'sessionId': payload["sessionId"]})
                           )
        else:
            # If there is no previous message for this siteId,
            # tell the user we're sorry.
            client.publish(DM_END_SESSION,
                           json.dumps({'text': RESULT_SORRY,
                                       'sessionId': payload["sessionId"]})
                           )


if __name__ == "__main__":
    SayItAgain()
