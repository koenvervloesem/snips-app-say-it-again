#!/usr/bin/env python3
"""
This module contains a Snips app that repeats the last message that
your voice assistant has said on the site you are talking to, as well as what
Snips has understood from your last speech message. It can also repeat the
action corresponding to the last intent.
"""

from collections import deque
import importlib

from snipskit.config import AssistantConfig
from snipskit.mqtt.apps import MQTTSnipsApp
from snipskit.mqtt.decorators import topic
from snipskit.mqtt.dialogue import end_session


# MQTT topics
TTS_SAY = "hermes/tts/say"
ASR_TEXT_CAPTURED = "hermes/asr/textCaptured"
INTENT_ALL = "hermes/intent/#"

# Use the assistant's language.
i18n = importlib.import_module('translations.' + AssistantConfig()['language'])


class SayItAgain(MQTTSnipsApp):
    """
    This Snips app repeats the last message that your voice assistant has said
    on the site you are talking to, as well as what Snips has understood
    from your last speech message.
    """

    def initialize(self):
        """Initialize the app."""

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
    def handle_say(self, topic, payload):
        """When Snips says something, save the text."""
        self.last_messages[payload["siteId"]] = payload["text"]

    @topic(ASR_TEXT_CAPTURED)
    def handle_text(self, topic, payload):
        """When Snips captures a text, save it together with its likelihood."""
        # We save the last two texts in a deque because the WhatDidISay intent
        # also generates a captured text and we're not interested in that...
        if payload["siteId"] not in self.last_texts:
            # Create a new deque of length 2.
            self.last_texts[payload["siteId"]] = deque(maxlen=2)

        # Add the text and likelihood at the end of the deque.
        text = payload["text"]
        likelihood = round(payload["likelihood"], 2)
        self.last_texts[payload["siteId"]].append((text, likelihood))

    @topic(INTENT_ALL)
    def handle_intent(self, topic, payload):
        """
        When an intent is triggered (and it is not the RepeatAction intent!),
        save the request.
        """
        # Ignore the RepeatAction intent! We want to perform repeat multiple
        # times. Not ignoring it might create an endless loop!
        if topic != i18n.INTENT_REPEAT_ACTION:
            self.last_intent[payload["siteId"]] = (topic, payload)

    @topic(i18n.INTENT_REPEAT_ACTION)
    def handle_repeat_action(self, topic, payload):
        """Get the last captured intent and repeat."""
        if payload["siteId"] in self.last_intent:
            last_topic, last_payload = self.last_intent[payload["siteId"]]
            last_payload["sessionId"] = payload["sessionId"]
            self.publish(last_topic, last_payload)
        else:
            # If there is no previous message for this siteId,
            # tell the user we're sorry.
            self.publish(*end_session(payload["sessionId"],
                                      i18n.RESULT_INTENT_SORRY))

    @topic(i18n.INTENT_SAY_IT_AGAIN)
    def handle_say_again(self, topic, payload):
        """When the user asks to repeat the last message, do it."""
        if payload["siteId"] in self.last_messages:
            # If we have saved a previous message for this siteId, repeat it.
            last_message = self.last_messages[payload["siteId"]]
            self.publish(*end_session(payload["sessionId"], last_message))
        else:
            # If there is no previous message for this siteId,
            # tell the user we're sorry.
            self.publish(*end_session(payload["sessionId"],
                                      i18n.RESULT_SAY_SORRY))

    @topic(i18n.INTENT_WHAT_DID_I_SAY)
    def handle_what_did_i_say(self, topic, payload):
        """When the user asks to repeat the last captured text, do it."""
        if len(self.last_texts[payload["siteId"]]) == 2:
            # If we have saved two previous texts for this siteId,
            # repeat the first one.
            # The second one is the one that generated the current intent.
            last_text, last_likelihood = self.last_texts[payload["siteId"]][0]
            if last_text:
                self.publish(*end_session(payload["sessionId"],
                                          i18n.RESULT_TEXT.format(last_text,
                                                                  last_likelihood)))
            else:
                # Empty string
                self.publish(*end_session(payload["sessionId"],
                                          i18n.RESULT_TEXT_NOTHING))

        else:
            # If there is no previous text for this siteId,
            # tell the user we're sorry.
            self.publish(*end_session(payload["sessionId"],
                                      i18n.RESULT_TEXT_SORRY))


if __name__ == "__main__":
    SayItAgain()
