import os
from typing import Annotated

from autogen import (
    AssistantAgent,
    UserProxyAgent,
    register_function,
)
from autogen.cache import Cache

from .tools import Tools

tool = Tools()

config_list = [
    {"model": "gpt-4o", "api_key": os.environ["OPENAI_API_KEY"]},
]


def list_table() -> Annotated[str, "The name of tables in the system"]:
    return str(tool.list_table())


def describe_table(
    name: Annotated[str, "The name of the table"]
) -> Annotated[str, "schema definition of the table"]:
    return str(tool.describe_table(name))


# NOTE: this ReAct prompt is adapted from Langchain's ReAct agent: https://github.com/langchain-ai/langchain/blob/master/libs/langchain/langchain/agents/react/agent.py#L79
ReAct_prompt = """
You are a asistent help generating SQL based on input questions.
Please stop when you have the SQL, no need to execute the SQL
To generate SQL, here are rules:
* the grammar follows ClickHouse style
* all datatypes MUST be in lowercase, such uint32
* all keywords MUST be in lowercase, such as nullable
* for normal query, add table() function to the table name, for example select count(*) from table(table_name)
* for real time query, where continously return new result to the user, append a time range, for example
  select count(*) from table_name where _tp_time > now() -1h
  which will return the number of event received in the past 1 hour

You have access to tools provided.
Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take
Action Input: the input to the action
Observation: the result of the action
... (this process can repeat multiple times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!
Question: {input}
"""

# Define the ReAct prompt message. Assuming a "question" field is present in the context


def react_prompt_message(sender, recipient, context):
    return ReAct_prompt.format(input=context["question"])


class Text2SQLAgent:
    def __init__(self):
        self.user_proxy = UserProxyAgent(
            name="User",
            is_termination_msg=lambda x: x.get("content", "")
            and x.get("content", "").rstrip().endswith("TERMINATE"),
            human_input_mode="NEVER",
            max_consecutive_auto_reply=10,
        )

        self.assistant = AssistantAgent(
            name="Assistant",
            system_message=(
                "Only use the tools you have been provided with."
                "You are a SQL generator. Your task is to generate SQL queries and nothing else. "
                "Do NOT execute SQL or ask for execution. Once the SQL is generated, respond with TERMINATE."
            ),
            llm_config={"config_list": config_list, "cache_seed": None},
        )

        # Register the timeplus tool.
        register_function(
            list_table,
            caller=self.assistant,
            executor=self.user_proxy,
            name="list_table",
            description="list available tables in the system",
        )

        register_function(
            describe_table,
            caller=self.assistant,
            executor=self.user_proxy,
            name="describe_table",
            description="return the schema of the table",
        )

    def ask(self, question: str):
        with Cache.disk(cache_seed=43) as cache:
            self.user_proxy.initiate_chat(
                self.assistant,
                message=react_prompt_message,
                question=question,
                cache=cache,
            )

            # print(f" the final answer is { self.user_proxy.last_message()['content'] } ")
            return self.user_proxy.last_message()["content"]
