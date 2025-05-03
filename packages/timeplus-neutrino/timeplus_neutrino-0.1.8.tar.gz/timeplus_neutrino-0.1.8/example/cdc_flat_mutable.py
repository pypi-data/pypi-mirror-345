from neutrino.pipeline.agent import DataExtractionAgent
from neutrino.utils.tools import extract_code_blocks_with_type

data = """{
		"customer_id": 100,
		"name": "Johnathan Rodriguez",
		"email": "thomasramirez@example.org",
		"phone": "001-845-290-8721x77863",
		"address": "743 Cervantes Causeway Apt. 762\nPort Lauren, NY 12698"
	}"""

source_stream_name = "kafka_cdc_postgres_customers"
target_stream_name = "customers"

agent = DataExtractionAgent()

agent1_output, agent2_output = agent.pipeline_with_mutable_stream(data, source_stream_name, target_stream_name, ["customer_id"])

print(f" target stream : {agent1_output}")

print(f" mv extraction  : {agent2_output}")