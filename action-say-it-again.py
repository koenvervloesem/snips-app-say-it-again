#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
This module contains a Snips skill that repeats the last message that
your voice assistant has said on the site you are talking to, as well as what
Snips has understood from your last speech message.
"""

from collections import deque

import paho.mqtt.client as mqtt
import json

# Result sentence
RESULT_SAY_SORRY = "Sorry, I don't remember what I said. I must have fallen asleep."
RESULT_TEXT_SORRY = "Sorry, I don't remember what you said. I must have fallen asleep."
RESULT_TEXT = "I heard \"{}\" with likelihood {}."

# MQTT topics
TTS_SAY = "hermes/tts/say"
ASR_TEXT_CAPTURED = "hermes/asr/textCaptured"
DM_END_SESSION = "hermes/dialogueManager/endSession"
INTENT_SAY_IT_AGAIN = "hermes/intent/koan:SayItAgain"
INTENT_WHAT_DID_I_SAY = "hermes/intent/koan:WhatDidISay"

# If this skill is supposed to run on the satellite,
# please get this mqtt connection info from <config.ini>
# Hint: MQTT server is always running on the master device
MQTT_HOST = 'localhost'
MQTT_PORT = 1883


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

        # Create an empty dictionary that will hold the two last captured texts
        # and their likelihoods of each siteId.
        self.last_texts = {}

        self.client = mqtt.Client()
        self.client.on_connect = self.subscribe_topics

        self.client.connect(MQTT_HOST, MQTT_PORT, 60)
        self.client.loop_forever()

    def subscribe_topics(self, client, userdata, flags, rc):
        """Subscribe to the MQTT topics we're interested in."""
        client.subscribe([(TTS_SAY, 0),
                          (ASR_TEXT_CAPTURED, 0),
                          (INTENT_SAY_IT_AGAIN, 0),
                          (INTENT_WHAT_DID_I_SAY, 0)])

        client.message_callback_add(TTS_SAY,
                                    self.handle_say)
        client.message_callback_add(ASR_TEXT_CAPTURED,
                                    self.handle_text)
        client.message_callback_add(INTENT_SAY_IT_AGAIN,
                                    self.handle_say_again)
        client.message_callback_add(INTENT_WHAT_DID_I_SAY,
                                    self.handle_what_did_i_say)

    def handle_say(self, client, userdata, msg):
        """When Snips says something, save the text."""
        payload = json.loads(msg.payload)
        self.last_messages[payload["siteId"]] = payload["text"]

    def handle_text(self, client, userdata, msg):
        """When Snips captures a text, save it together with is likelihood."""
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
                           json.dumps({'text': RESULT_SAY_SORRY,
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
            client.publish(DM_END_SESSION,
                           json.dumps({'text': RESULT_TEXT.format(last_text,
                                                                  last_likelihood),
                                       'sessionId': payload["sessionId"]})
                           )
        else:
            # If there is no previous text for this siteId,
            # tell the user we're sorry.
            client.publish(DM_END_SESSION,
                           json.dumps({'text': RESULT_TEXT_SORRY,
                                       'sessionId': payload["sessionId"]})
                           )


if __name__ == "__main__":
    SayItAgain()
