import os
from neutrino.conf import TimeplusAgentConfig

agent_config = TimeplusAgentConfig()

## a valid local ollama config
agent_config.config("default", "http://localhost:11434/v1", "ollama", "codellama:latest")

## a valid openai config
agent_config.config("default", "https://api.openai.com/v1", os.environ["OPENAI_API_KEY"], "gpt-4o-mini")

## invalid local ollama config - no such model
try:
    agent_config.config("default", "http://localhost:11434/v1", "ollama", "abc")
except Exception as e:
    print(e)
    
## invalid local ollama config - wrong url
try:
    agent_config.config("default", "http://localhost:11434/v2", "ollama", "abc")
except Exception as e:
    print(e)