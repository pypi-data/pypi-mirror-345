from neutrino.kafka.agent import KafkaExplorerAgent

agent = KafkaExplorerAgent()
result = agent.ask('how many topics are there? and what are the names of these topics?')
print(f'the answer is {result}')