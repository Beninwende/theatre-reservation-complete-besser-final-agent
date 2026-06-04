# You may need to add your working directory to the Python path. To do so, uncomment the following lines of code
# import sys
# sys.path.append("/Path/to/directory/besser-agentic-framework") # Replace with your directory path

import json
import logging
import operator

from baf.core.agent import Agent
from baf.library.transition.events.base_events import *
from baf.nlp.llm.llm_huggingface import LLMHuggingFace
from baf.nlp.llm.llm_huggingface_api import LLMHuggingFaceAPI
from baf.nlp.llm.llm_openai_api import LLMOpenAI
from baf.nlp.llm.llm_replicate_api import LLMReplicate
from baf.core.session import Session
from baf.nlp.intent_classifier.intent_classifier_configuration import LLMIntentClassifierConfiguration, SimpleIntentClassifierConfiguration
from baf.nlp.speech2text.openai_speech2text import OpenAISpeech2Text
from baf.nlp.text2speech.openai_text2speech import OpenAIText2Speech

# Configure the logging module
logging.basicConfig(level=logging.INFO, format='{levelname} - {asctime}: {message}', style='{')


# Create the bot
agent = Agent('Theatre_reservation_agent')
# Load bot properties stored in a dedicated file
agent.load_properties('config.yaml')

# Define the platform your chatbot will use





platform = agent.use_websocket_platform(use_ui=True)



ic_config = SimpleIntentClassifierConfiguration(
    framework='pytorch',
    num_epochs=50,
    embedding_dim=128,
    hidden_dim=128,
    input_max_num_tokens=15,
    discard_oov_sentences=True,
    check_exact_prediction_match=True,
    activation_last_layer='sigmoid',
    lr=0.001
)

agent.set_default_ic_config(ic_config)

# No LLM configured; consumers referencing default_llm will fail loudly at runtime
default_llm = None






##############################
# INTENTS
##############################
profile_standard = agent.new_intent('profile_standard', [
    'STANDARD',
    ],
    description='Standard profile'
)
profile_access = agent.new_intent('profile_access', [
    'ACCESS',
    ],
    description='Accessibility profile'
)
start_booking = agent.new_intent('start_booking', [
    'BOOK',
    ],
    description='Start booking'
)
ask_faq = agent.new_intent('ask_faq', [
    'FAQ',
    'prices?',
    ],
    description='FAQ question'
)
cancel_booking = agent.new_intent('cancel_booking', [
    'CANCEL',
    ],
    description='Cancel draft'
)
pick_hamlet = agent.new_intent('pick_hamlet', [
    'Hamlet',
    ],
    description='Pick show'
)
seats_2 = agent.new_intent('seats_2', [
    '2',
    'two seats',
    ],
    description='Two seats'
)
zone_front = agent.new_intent('zone_front', [
    'FRONT',
    ],
    description='Front zone'
)



##############################
# CUSTOM CONDITIONS
##############################


##############################
# STATES
##############################


initial_state = agent.new_state('initial_state', initial=True)
profile_pick = agent.new_state('profile_pick')
hub = agent.new_state('hub')
show_select = agent.new_state('show_select')
seat_count = agent.new_state('seat_count')
zone_pick = agent.new_state('zone_pick')
confirm_do = agent.new_state('confirm_do')
faq_llm = agent.new_state('faq_llm')
cancel_reset = agent.new_state('cancel_reset')



# initial_state
initial_state.go_to(profile_pick)
# profile_pick
def profile_pick_body(session: Session):
    reply_text = 'Welcome — pick STANDARD or ACCESS'
    session.reply(reply_text)
profile_pick.set_body(profile_pick_body)
profile_pick.when_intent_matched(profile_standard).go_to(hub)
profile_pick.when_intent_matched(profile_access).go_to(hub)
# hub
def hub_body(session: Session):
    reply_text = 'BOOK | FAQ | CANCEL'
    session.reply(reply_text)
    reply_text = 'Shows menu'
    session.reply(reply_text)
hub.set_body(hub_body)
hub.when_intent_matched(start_booking).go_to(show_select)
hub.when_intent_matched(ask_faq).go_to(faq_llm)
hub.when_intent_matched(cancel_booking).go_to(cancel_reset)
# show_select
def show_select_body(session: Session):
    reply_text = 'Pick Hamlet / Jazz / Comedy'
    session.reply(reply_text)
show_select.set_body(show_select_body)
show_select.when_intent_matched(pick_hamlet).go_to(seat_count)
# seat_count
def seat_count_body(session: Session):
    reply_text = 'Seats 1–4'
    session.reply(reply_text)
seat_count.set_body(seat_count_body)
seat_count.when_intent_matched(seats_2).go_to(zone_pick)
# zone_pick
def zone_pick_body(session: Session):
    reply_text = 'FRONT or REAR'
    session.reply(reply_text)
zone_pick.set_body(zone_pick_body)
zone_pick.when_intent_matched(zone_front).go_to(confirm_do)
# confirm_do
def confirm_do_body(session: Session):
    reply_text = 'Book + confirmation code'
    session.reply(reply_text)
confirm_do.set_body(confirm_do_body)
confirm_do.go_to(hub)
# faq_llm
def faq_llm_body(session: Session):
    reply_text = 'LLM FAQ (profile-aware tone)'
    session.reply(reply_text)
faq_llm.set_body(faq_llm_body)
faq_llm.go_to(hub)
# cancel_reset
def cancel_reset_body(session: Session):
    reply_text = 'Clear draft → hub'
    session.reply(reply_text)
cancel_reset.set_body(cancel_reset_body)
cancel_reset.go_to(hub)




# RUN APPLICATION

if __name__ == '__main__':
    agent.run()