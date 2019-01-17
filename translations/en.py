#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
This module contains the result sentences and intents for the English version
of the Say it again skill.
"""

# Result sentences
RESULT_SAY_SORRY = "Sorry, I don't remember what I said. I must have fallen asleep."
RESULT_TEXT_SORRY = "Sorry, I don't remember what you said. I must have fallen asleep."
RESULT_TEXT = "I heard \"{0}\" with likelihood {1}."
RESULT_TEXT_NOTHING = "Sorry, I didn't hear anything."
RESULT_INTENT_SORRY = "Sorry, I don't know what I should repeat."

# Intents
INTENT_SAY_IT_AGAIN = "hermes/intent/koan:SayItAgain"
INTENT_WHAT_DID_I_SAY = "hermes/intent/koan:WhatDidISay"
INTENT_REPEAT_ACTION = "hermes/intent/koan:RepeatAction"
