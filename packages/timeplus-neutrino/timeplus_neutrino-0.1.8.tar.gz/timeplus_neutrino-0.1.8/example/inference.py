from neutrino.onboard.agent import DataOnboardingAgent
from neutrino.utils.tools import extract_code_blocks_with_type
from neutrino.conf import TimeplusAgentConfig

data = """{
		"customer_id": 100,
		"name": "Johnathan Rodriguez",
		"email": "thomasramirez@example.org",
		"phone": "001-845-290-8721x77863",
		"address": "743 Cervantes Causeway Apt. 762\nPort Lauren, NY 12698",
		"ip": "127.0.0.1",
		"time": "2023-01-01 00:00:00",
		"event_time": "2023-01-01 00:00:00",
		"uid": "2a02:aa08:e000:3100::2",
		"uid2":"1f71acbf-59fc-427d-a634-1679b48029a9"
}"""

#agent_config = TimeplusAgentConfig()
#agent_config.config("default", "http://localhost:11434/v1", "ollama", "codellama:latest")

agent = DataOnboardingAgent()

inference_ddl, inference_json = agent.inference(data, "customer")

print(f"schema sql : {inference_ddl}")

json_code = extract_code_blocks_with_type(inference_json)
print(f" schema json : {inference_json}")

