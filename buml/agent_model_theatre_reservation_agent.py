###############
# AGENT MODEL #
###############
import datetime
from besser.BUML.metamodel.state_machine.state_machine import Body, Condition, ConfigProperty, CustomCodeAction
from besser.BUML.metamodel.state_machine.agent import Agent, AgentReply, LLMReply, RAGReply, DBReply, LLMOpenAI, LLMHuggingFace, LLMHuggingFaceAPI, LLMReplicate, RAGVectorStore, RAGTextSplitter, Tool, Skill, Workspace, ReasoningState, ReceiveTextEvent, ReceiveFileEvent, ReceiveJSONEvent, ReceiveMessageEvent, WildcardEvent, DummyEvent
from besser.BUML.metamodel.structural import Metadata
import operator

agent = Agent('Theatre_reservation_agent')

agent.add_property(ConfigProperty('websocket_platform', 'websocket.host', '0.0.0.0'))
agent.add_property(ConfigProperty('websocket_platform', 'websocket.port', 8765))
agent.add_property(ConfigProperty('websocket_platform', 'streamlit.host', '0.0.0.0'))
agent.add_property(ConfigProperty('websocket_platform', 'streamlit.port', 5000))
agent.add_property(ConfigProperty('nlp', 'nlp.language', 'en'))
agent.add_property(ConfigProperty('nlp', 'nlp.region', 'US'))
agent.add_property(ConfigProperty('nlp', 'nlp.timezone', 'Europe/Madrid'))
agent.add_property(ConfigProperty('nlp', 'nlp.pre_processing', True))
agent.add_property(ConfigProperty('nlp', 'nlp.intent_threshold', 0.4))
agent.add_property(ConfigProperty('nlp', 'nlp.openai.api_key', 'YOUR-API-KEY'))
agent.add_property(ConfigProperty('nlp', 'nlp.hf.api_key', 'YOUR-API-KEY'))
agent.add_property(ConfigProperty('nlp', 'nlp.replicate.api_key', 'YOUR-API-KEY'))

# INTENTS
profile_standard = agent.new_intent('profile_standard', [
    'STANDARD',
],
description="Standard profile")
profile_access = agent.new_intent('profile_access', [
    'ACCESS',
],
description="Accessibility profile")
start_booking = agent.new_intent('start_booking', [
    'BOOK',
],
description="Start booking")
ask_faq = agent.new_intent('ask_faq', [
    'FAQ',
    'prices?',
],
description="FAQ question")
cancel_booking = agent.new_intent('cancel_booking', [
    'CANCEL',
],
description="Cancel draft")
pick_hamlet = agent.new_intent('pick_hamlet', [
    'Hamlet',
],
description="Pick show")
seats_2 = agent.new_intent('seats_2', [
    '2',
    'two seats',
],
description="Two seats")
zone_front = agent.new_intent('zone_front', [
    'FRONT',
],
description="Front zone")

default_llm = None

# STATES
initial_state = agent.new_state('initial_state', initial=True)
profile_pick = agent.new_state('profile_pick')
hub = agent.new_state('hub')
show_select = agent.new_state('show_select')
seat_count = agent.new_state('seat_count')
zone_pick = agent.new_state('zone_pick')
confirm_do = agent.new_state('confirm_do')
faq_llm = agent.new_state('faq_llm')
cancel_reset = agent.new_state('cancel_reset')

# initial_state state
initial_state.go_to(profile_pick)

# profile_pick state
profile_pick_body = Body('profile_pick_body')
profile_pick_body.add_action(AgentReply('Welcome — pick STANDARD or ACCESS'))

profile_pick.set_body(profile_pick_body)
profile_pick.when_intent_matched(profile_standard).go_to(hub)

profile_pick.when_intent_matched(profile_access).go_to(hub)

# hub state
hub_body = Body('hub_body')
hub_body.add_action(AgentReply('BOOK | FAQ | CANCEL'))
hub_body.add_action(AgentReply('Shows menu'))

hub.set_body(hub_body)
hub.when_intent_matched(start_booking).go_to(show_select)

hub.when_intent_matched(ask_faq).go_to(faq_llm)

hub.when_intent_matched(cancel_booking).go_to(cancel_reset)

# show_select state
show_select_body = Body('show_select_body')
show_select_body.add_action(AgentReply('Pick Hamlet / Jazz / Comedy'))

show_select.set_body(show_select_body)
show_select.when_intent_matched(pick_hamlet).go_to(seat_count)

# seat_count state
seat_count_body = Body('seat_count_body')
seat_count_body.add_action(AgentReply('Seats 1–4'))

seat_count.set_body(seat_count_body)
seat_count.when_intent_matched(seats_2).go_to(zone_pick)

# zone_pick state
zone_pick_body = Body('zone_pick_body')
zone_pick_body.add_action(AgentReply('FRONT or REAR'))

zone_pick.set_body(zone_pick_body)
zone_pick.when_intent_matched(zone_front).go_to(confirm_do)

# confirm_do state
confirm_do_body = Body('confirm_do_body')
confirm_do_body.add_action(AgentReply('Book + confirmation code'))

confirm_do.set_body(confirm_do_body)
confirm_do.go_to(hub)

# faq_llm state
faq_llm_body = Body('faq_llm_body')
faq_llm_body.add_action(AgentReply('LLM FAQ (profile-aware tone)'))

faq_llm.set_body(faq_llm_body)
faq_llm.go_to(hub)

# cancel_reset state
cancel_reset_body = Body('cancel_reset_body')
cancel_reset_body.add_action(AgentReply('Clear draft → hub'))

cancel_reset.set_body(cancel_reset_body)
cancel_reset.go_to(hub)

