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

from snipskit.apps import MQTTSnipsApp
from snipskit.app_decorators import topic
from snipskit.config import AssistantConfig


# MQTT topics
TTS_SAY = "hermes/tts/say"
ASR_TEXT_CAPTURED = "hermes/asr/textCaptured"
DM_END_SESSION = "hermes/dialogueManager/endSession"
INTENT_ALL = "hermes/intent/#"

# Use the assistant's language.
i18n = importlib.import_module('translations.' + AssistantConfig()['language'])


class SayItAgain(MQTTSnipsApp):
    """
    This skill repeats the last message that your voice assistant has said
    on the site you are talking to, as well as what Snips has understood
    from your last speech message.
    """

    def initialize(self):
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

    @topic(TTS_SAY)
    def handle_say(self, client, userdata, msg):
        """When Snips says something, save the text."""
        payload = json.loads(msg.payload.decode('utf-8'))
        self.last_messages[payload["siteId"]] = payload["text"]

    @topic(ASR_TEXT_CAPTURED)
    def handle_text(self, client, userdata, msg):
        """When Snips captures a text, save it together with its likelihood."""
        # We save the last two texts in a deque because the WhatDidISay intent
        # also generates a captured text and we're not interested in that...
        payload = json.loads(msg.payload.decode('utf-8'))
        if payload["siteId"] not in self.last_texts:
            # Create a new deque of length 2.
            self.last_texts[payload["siteId"]] = deque(maxlen=2)

        # Add the text and likelihood at the end of the deque.
        text = payload["text"]
        likelihood = round(payload["likelihood"], 2)
        self.last_texts[payload["siteId"]].append((text, likelihood))

    @topic(INTENT_ALL)
    def handle_intent(self, client, userdata, msg):
        """
        When an intent is triggered (and it is not the RepeatAction intent!),
        save the request.
        """
        # Ignore the RepeatAction intent! We want to perform repeat multiple
        # times. Not ignoring it might create an endless loop!
        if msg.topic != i18n.INTENT_REPEAT_ACTION:
            payload = json.loads(msg.payload.decode('utf-8'))
            self.last_intent[payload["siteId"]] = msg

    @topic(i18n.INTENT_REPEAT_ACTION)
    def handle_repeat_action(self, client, userdata, msg):
        """Get the last captured intent and repeat."""
        payload = json.loads(msg.payload.decode('utf-8'))
        if payload["siteId"] in self.last_intent:
            last_msg = self.last_intent[payload["siteId"]]
            last_payload = json.loads(last_msg.payload.decode('utf-8'))
            last_payload["sessionId"] = payload["sessionId"]
            client.publish(last_msg.topic, json.dumps(last_payload))
        else:
            # If there is no previous message for this siteId,
            # tell the user we're sorry.
            client.publish(DM_END_SESSION,
                           json.dumps({'text': i18n.RESULT_INTENT_SORRY,
                                       'sessionId': payload["sessionId"]})
                           )

    @topic(i18n.INTENT_SAY_IT_AGAIN)
    def handle_say_again(self, client, userdata, msg):
        """When the user asks to repeat the last message, do it."""
        payload = json.loads(msg.payload.decode('utf-8'))
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
                           json.dumps({'text': i18n.RESULT_SAY_SORRY,
                                       'sessionId': payload["sessionId"]})
                           )

    @topic(i18n.INTENT_WHAT_DID_I_SAY)
    def handle_what_did_i_say(self, client, userdata, msg):
        """When the user asks to repeat the last captured text, do it."""
        payload = json.loads(msg.payload.decode('utf-8'))
        if len(self.last_texts[payload["siteId"]]) == 2:
            # If we have saved two previous texts for this siteId,
            # repeat the first one.
            # The second one is the one that generated the current intent.
            last_text, last_likelihood = self.last_texts[payload["siteId"]][0]
            if last_text:
                client.publish(DM_END_SESSION,
                               json.dumps({'text': i18n.RESULT_TEXT.format(last_text,
                                                                           last_likelihood),
                                           'sessionId': payload["sessionId"]})
                               )
            else:
                # Empty string
                client.publish(DM_END_SESSION,
                               json.dumps({'text': i18n.RESULT_TEXT_NOTHING,
                                           'sessionId': payload["sessionId"]})
                               )

        else:
            # If there is no previous text for this siteId,
            # tell the user we're sorry.
            client.publish(DM_END_SESSION,
                           json.dumps({'text': i18n.RESULT_TEXT_SORRY,
                                       'sessionId': payload["sessionId"]})
                           )


if __name__ == "__main__":
    SayItAgain()
