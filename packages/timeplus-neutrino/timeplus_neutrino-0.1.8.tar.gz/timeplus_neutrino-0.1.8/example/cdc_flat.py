from neutrino.pipeline.agent import DataExtractionAgent
from neutrino.conf import TimeplusAgentConfig

data = """{
		"customer_id": 900,
		"name": "Johnathan Rodriguez",
		"email": "thomasramirez@example.org",
		"phone": "001-845-290-8721x77863",
		"address": "743 Cervantes Causeway Apt. 762\nPort Lauren, NY 12698"
	}"""

source_stream_name = "kafka_cdc_postgres_customers"
target_stream_name = "customers"

#agent_config = TimeplusAgentConfig()
#agent_config.config("default", "http://localhost:11434/v1", "ollama", "codellama:latest")

agent = DataExtractionAgent()

agent1_output, agent2_output = agent.pipeline(data, source_stream_name, target_stream_name)

print(f" target stream : {agent1_output}")
print(f" mv extraction  : {agent2_output}")
