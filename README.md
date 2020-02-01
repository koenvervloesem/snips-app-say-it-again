# Say it again app for Snips 

[![Build status](https://api.travis-ci.com/koenvervloesem/snips-app-say-it-again.svg?branch=master)](https://travis-ci.com/koenvervloesem/snips-app-say-it-again) [![Maintainability](https://api.codeclimate.com/v1/badges/85a21cdc831d667ec532/maintainability)](https://codeclimate.com/github/koenvervloesem/snips-app-say-it-again/maintainability) [![Code quality](https://api.codacy.com/project/badge/Grade/336aac5c6a324dde9767e75a254f34af)](https://www.codacy.com/app/koenvervloesem/snips-app-say-it-again) [![Python versions](https://img.shields.io/badge/python-3.5|3.6|3.7-blue.svg)](https://www.python.org) [![GitHub license](https://img.shields.io/github/license/koenvervloesem/snips-app-say-it-again.svg)](https://github.com/koenvervloesem/snips-app-say-it-again/blob/master/LICENSE) [![Languages](https://img.shields.io/badge/i18n-en|de|fr|it-brown.svg)](https://github.com/koenvervloesem/snips-app-say-it-again/tree/master/translations) [![Snips App Store](https://img.shields.io/badge/snips-app-blue.svg)](https://console.snips.ai/store/en/skill_YoV709qZP3n)

**Important information: Following the acquisition of Snips by Sonos, the Snips Console is not available anymore after January 31, 2020. As such, we have exported all data of the English and German version of this app from the Snips Console and made these available in the directory [console](https://github.com/koenvervloesem/snips-app-say-it-again/tree/master/console) with the same MIT license as the rest of this project. This project has been archived. If you're searching for an alternative to Snips, I believe that [Rhasspy](https://rhasspy.readthedocs.io/) is currently the best choice for an offline open source voice assistant.**

With this [Snips](https://snips.ai/) app, you can ask your voice assistant to repeat its last message, the last text it captured from your speech or the last action it has performed.

The app is multi-room aware: it repeats the last message it has said or heard or the last action it has performed on the site you are talking to.

## Installation

The easiest way to install this app is by adding the corresponding Snips app to your assistant in the [Snips Console](https://console.snips.ai):

*   English: [Say it again](https://console.snips.ai/store/en/skill_YoV709qZP3n)
*   French: [Say It Again ( Répète )](https://console.snips.ai/store/fr/skill_WrK0rWr9Xrp)
*   German: [Wie bitte?](https://console.snips.ai/store/de/skill_Qw5BPznz1lv)
*   Italian: [Ripeti](https://console.snips.ai/store/it/skill_zmzla0BkBbQ)

## Usage

This app recognizes the following intents:

*   SayItAgain - The user asks to repeat the last message. The app responds by repeating the most recent message it uttered.
*   WhatDidISay - The user asks to repeat the last text Snips has captured. The app responds by repeating the most recent text it captured from the user's speech.
*   RepeatAction - The user asks to repeat the last action Snips has performed. The app responds by repeating the most recent intent it captured, which executes its corresponding action again.

## Copyright

This app is provided by [Koen Vervloesem](mailto:koen@vervloesem.eu) as open source software. See LICENSE for more information.
