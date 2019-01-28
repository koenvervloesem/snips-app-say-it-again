#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module contains a Snips skill that repeats the last message that
your voice assistant has said on the site you are talking to, as well as what
Snips has understood from your last speech message. It can also repeat the
action corresponding to the last intent.
"""

from collections import deque
import importlib
import json

import paho.mqtt.client as mqtt
import toml

# MQTT topics
TTS_SAY = "hermes/tts/say"
ASR_TEXT_CAPTURED = "hermes/asr/textCaptured"
DM_END_SESSION = "hermes/dialogueManager/endSession"
INTENT_MQTT = "hermes/intent/#"


class SayItAgain(object):
    """
    This skill repeats the last message that your voice assistant has said
    on the site you are talking to, as well as what Snips has understood
    from your last speech message.
    """

    def __init__(self):
        """Initialize the skill."""

        # Create an empty dictionary that will hold the last message
        # of each siteId.
        self.last_messages = {}

        # Create an empty dictionary that will hold the last two captured texts
        # and their likelihoods of each siteId.
        self.last_texts = {}

        # Create an empty dictionary that will hold the last triggered intent
        # of each siteId.
        self.last_intent = {}

        # Use the assistant's language.
        with open("/usr/share/snips/assistant/assistant.json") as json_file:
            language = json.load(json_file)["language"]

        self.i18n = importlib.import_module("translations." + language)

        # Get the MQTT host and port from /etc/snips.toml.
        try:
            mqtt_host_port = toml.load('/etc/snips.toml')['snips-common']['mqtt']
            mqtt_host, mqtt_port = mqtt_host_port.split(':')
            mqtt_port = int(mqtt_port)
        except (KeyError, ValueError):
            # If the mqtt key doesn't exist or doesn't have the correct format,
            # use the default values.
            mqtt_host = 'localhost'
            mqtt_port = 1883

        self.client = mqtt.Client()
        self.client.on_connect = self.subscribe_topics

        self.client.connect(mqtt_host, mqtt_port, 60)
        self.client.loop_forever()

    def subscribe_topics(self, client, userdata, flags, rc):
        """Subscribe to the MQTT topics we're interested in."""
        client.subscribe([(TTS_SAY, 0),
                          (ASR_TEXT_CAPTURED, 0),
                          (INTENT_MQTT, 0)])  # This captures all intents.

        client.message_callback_add(TTS_SAY,
                                    self.handle_say)
        client.message_callback_add(ASR_TEXT_CAPTURED,
                                    self.handle_text)
        client.message_callback_add(INTENT_MQTT,
                                    self.handle_intent)
        client.message_callback_add(self.i18n.INTENT_SAY_IT_AGAIN,
                                    self.handle_say_again)
        client.message_callback_add(self.i18n.INTENT_WHAT_DID_I_SAY,
                                    self.handle_what_did_i_say)
        client.message_callback_add(self.i18n.INTENT_REPEAT_ACTION,
                                    self.handle_repeat_action)

    def handle_say(self, client, userdata, msg):
        """When Snips says something, save the text."""
        payload = json.loads(msg.payload)
        self.last_messages[payload["siteId"]] = payload["text"]

    def handle_text(self, client, userdata, msg):
        """When Snips captures a text, save it together with its likelihood."""
        # We save the last two texts in a deque because the WhatDidISay intent
        # also generates a captured text and we're not interested in that...
        payload = json.loads(msg.payload)
        if payload["siteId"] not in self.last_texts:
            # Create a new deque of length 2.
            self.last_texts[payload["siteId"]] = deque(maxlen=2)

        # Add the text and likelihood at the end of the deque.
        text = payload["text"]
        likelihood = round(payload["likelihood"], 2)
        self.last_texts[payload["siteId"]].append((text, likelihood))

    def handle_intent(self, client, userdata, msg):
        """
        When an intent is triggered (and it is not the RepeatAction intent!),
        save the request.
        """
        # Ignore the RepeatAction intent! We want to perform repeat multiple
        # times. Not ignoring it might create an endless loop!
        if msg.topic != self.i18n.INTENT_REPEAT_ACTION:
            payload = json.loads(msg.payload)
            self.last_intent[payload["siteId"]] = msg

    def handle_repeat_action(self, client, userdata, msg):
        """Get the last captured intent and repeat."""
        payload = json.loads(msg.payload)
        if payload["siteId"] in self.last_intent:
            last_msg = self.last_intent[payload["siteId"]]
            last_payload = json.loads(last_msg.payload)
            last_payload["sessionId"] = payload["sessionId"]
            client.publish(last_msg.topic, json.dumps(last_payload))
        else:
            # If there is no previous message for this siteId,
            # tell the user we're sorry.
            client.publish(DM_END_SESSION,
                           json.dumps({'text': self.i18n.RESULT_INTENT_SORRY,
                                       'sessionId': payload["sessionId"]})
                           )

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
                           json.dumps({'text': self.i18n.RESULT_SAY_SORRY,
                                       'sessionId': payload["sessionId"]})
                           )

    def handle_what_did_i_say(self, client, userdata, msg):
        """When the user asks to repeat the last captured text, do it."""
        payload = json.loads(msg.payload)
        if len(self.last_texts[payload["siteId"]]) == 2:
            # If we have saved two previous texts for this siteId,
            # repeat the first one.
            # The second one is the one that generated the current intent.
            last_text, last_likelihood = self.last_texts[payload["siteId"]][0]
            if last_text:
                client.publish(DM_END_SESSION,
                               json.dumps({'text': self.i18n.RESULT_TEXT.format(last_text,
                                                                                last_likelihood),
                                           'sessionId': payload["sessionId"]})
                               )
            else:
                # Empty string
                client.publish(DM_END_SESSION,
                               json.dumps({'text': self.i18n.RESULT_TEXT_NOTHING,
                                           'sessionId': payload["sessionId"]})
                               )

        else:
            # If there is no previous text for this siteId,
            # tell the user we're sorry.
            client.publish(DM_END_SESSION,
                           json.dumps({'text': self.i18n.RESULT_TEXT_SORRY,
                                       'sessionId': payload["sessionId"]})
                           )


if __name__ == "__main__":
    SayItAgain()
