"""
BESSER agent entry point (same name as editor export).

The Web Modeling Editor generates a skeleton agent; this project ships the
full implementation in theatre_bot.py (reservation store, LLM FAQ, all intents).

Run:
  python Theatre_reservation_agent.py
  # or: python theatre_bot.py
"""
from theatre_bot import agent

if __name__ == "__main__":
    agent.run()
