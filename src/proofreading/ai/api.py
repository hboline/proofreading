from pathlib import Path
import json

from openai import OpenAI

from .file import File

class Agent():
    def __init__(self, agent_id: str, style_rules: Path):
        # load paper
        self.paper = File()

        # load style rules
        with open(style_rules, 'r', encoding='utf-8') as f:
            self.STYLE_RULES = json.load(f)
        
        # start agent session
        self.client = OpenAI()
        self.AGENT_ID = agent_id
        self.session = self.client.beta.agents.sessions.create(
            agent_id=self.AGENT_ID,
            environment={"type": "none"},
            input=f"""
                Style Rules: \n\n{self.STYLE_RULES}\n\n
                Paper Text: \n\n{self.paper}
            """,
            stream=False
        )

    def prompt(self, prompt: str):
        self.client.beta.agents.sessions.events.create(
            session_id=self.session.id,
            events=[
                {
                    "type": "agent.session.input.message",
                    "input": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "input_text",
                                    "text": prompt
                                }
                            ]
                        }
                    ]
                }
            ]
        )
