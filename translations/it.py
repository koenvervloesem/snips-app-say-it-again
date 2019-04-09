"""
This module contains the result sentences and intents for the Italian version
of the Say it again app.
"""

# Result sentences
RESULT_SAY_SORRY = "Scusa, non mi ricordo cosa ho detto. Devo essermi addormentato."
RESULT_TEXT_SORRY = "Scusa, non mi ricordo cosa hai detto. Devo essermi addormentato."
RESULT_TEXT = "Ho sentito \"{0}\" con probabilità {1}."
RESULT_TEXT_NOTHING = "Scusa, non ho sentito nulla."
RESULT_INTENT_SORRY = "Scusa, non ricordo la mia ultima azione. Devo essermi addormentato."

# Intents
INTENT_SAY_IT_AGAIN = "hermes/intent/boggiano:Ripetilo"
INTENT_WHAT_DID_I_SAY = "hermes/intent/boggiano:CosaHoDetto"
INTENT_REPEAT_ACTION = "hermes/intent/boggiano:RipetiAzione"
