from neutrino.conf import TimeplusAgentConfig

agent_config = TimeplusAgentConfig()
client = agent_config.get_client("default")

print(client)

config = agent_config._get_config("default")
print(config)