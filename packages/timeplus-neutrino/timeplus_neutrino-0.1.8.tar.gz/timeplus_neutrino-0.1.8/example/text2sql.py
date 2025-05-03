from neutrino.timeplus.text2sql import Text2SQLAgent
from neutrino.utils.tools import extract_code_blocks_with_type

question = "how may customers are there?"
agent = Text2SQLAgent()

# TODO: in some case, the answer lies in the second last message
sql_result = agent.ask(question)

print(sql_result)


