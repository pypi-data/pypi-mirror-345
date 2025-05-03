from neutrino.pipeline.agent import DataExtractionAgent
from neutrino.conf import TimeplusAgentConfig

data = """{
		"customer_id": 9000,
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

settings = {
	"type" :'s3',
    "access_key_id" : 'minioadmin',
    "secret_access_key" : 'minioadmin',
    "region" : 'us-east-1',
    "bucket" : 'timeplus',
   "data_format" : 'JSONEachRow',
    "endpoint" : 'http://minio:9000',
    "write_to" : 'lumi/data.json',
    "use_environment_credentials" : False
}
agent1_output, agent2_output = agent.generic_pipeline(data, source_stream_name, target_stream_name, settings)

print(f" target stream : {agent1_output}")
print(f" mv extraction  : {agent2_output}")
