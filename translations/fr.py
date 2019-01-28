#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module contains the result sentences and intents for the French version
of the Say it again skill.
"""

# Result sentences
RESULT_SAY_SORRY = "Désolé, je ne me souviens pas de ce que j'ai dit. Je dois m'être endormi."
RESULT_TEXT_SORRY = "Désolé, je ne me souviens pas de ce que vous avez dit. Je dois m'être endormi."
RESULT_TEXT = "J'ai entendu: \"{0}\" avec une probabilité de {1}."
RESULT_TEXT_NOTHING = "Désolé, je n'ai rien entendu."
RESULT_INTENT_SORRY = "Désolé, je ne me souviens pas de la dernière action. Je dois m'être endormi"

# Intents
INTENT_SAY_IT_AGAIN = "hermes/intent/Tealque:SayItAgain"
INTENT_WHAT_DID_I_SAY = "hermes/intent/Tealque:WhatDidISay"
INTENT_REPEAT_ACTION = "hermes/intent/Tealque:RepeatAction"
