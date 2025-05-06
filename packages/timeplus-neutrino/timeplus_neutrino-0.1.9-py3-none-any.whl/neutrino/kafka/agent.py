import os
import uuid
from typing import Annotated

from autogen import (
    AssistantAgent,
    UserProxyAgent,
    register_function,
)
from autogen.cache import Cache

from confluent_kafka.admin import AdminClient
from confluent_kafka import Consumer, TopicPartition


config_list = [
    {"model": "gpt-4o", "api_key": os.environ["OPENAI_API_KEY"]},
]

broker = os.environ["KAFKA_BROKER"]


def list_kafka_topics() -> Annotated[list, "The name of tables in the system"]:
    """List topics from a Kafka broker using confluent-kafka."""
    admin_client = AdminClient({"bootstrap.servers": broker})
    metadata = admin_client.list_topics(timeout=5)
    return list(metadata.topics.keys())


def get_topic_details(
    topic: Annotated[str, "the name of the topic"]
) -> Annotated[dict, "the information of the topic"]:
    """Fetch partitions and replication details for a topic."""
    admin_client = AdminClient({"bootstrap.servers": broker})
    metadata = admin_client.list_topics(topic, timeout=5)

    if topic not in metadata.topics:
        return f"Topic '{topic}' not found"

    topic_info = metadata.topics[topic]
    return {p.id: {"replicas": p.replicas} for p in topic_info.partitions.values()}


def get_topic_offsets(
    topic: Annotated[str, "the name of the topic"]
) -> Annotated[dict, "the json object with earliest and latest offset"]:
    """Retrieve earliest and latest offsets for each partition."""
    consumer = Consumer(
        {
            "bootstrap.servers": broker,
            "group.id": "offset_checker",
            "auto.offset.reset": "earliest",
        }
    )

    metadata = consumer.list_topics(topic, timeout=5)
    partitions = [p.id for p in metadata.topics[topic].partitions.values()]

    offsets = {}
    for partition in partitions:
        tp = TopicPartition(topic, partition)
        low, high = consumer.get_watermark_offsets(tp)
        offsets[partition] = {"earliest": low, "latest": high}

    consumer.close()
    return offsets


def get_latest_message(
    topic: Annotated[str, "the name of the topic"]
) -> Annotated[str, "the latest event in string format"]:
    # Generate a unique consumer group ID
    random_group_id = f"consumer-{uuid.uuid4()}"
    conf = {
        "bootstrap.servers": broker,
        "group.id": random_group_id,  # Use a unique group ID to avoid offset tracking
        "auto.offset.reset": "latest",  # Start from the latest message
    }

    consumer = Consumer(conf)

    # Get partition info
    metadata = consumer.list_topics(topic, timeout=5)
    partitions = [p.id for p in metadata.topics[topic].partitions.values()]

    # Find the partition with the latest message
    latest_msg = None

    for partition in partitions:
        # Get the latest offset for the partition
        low, high = consumer.get_watermark_offsets(TopicPartition(topic, partition))
        last_offset = high - 1  # Last available message offset

        if last_offset < 0:
            continue  # No messages in this partition

        # Seek to the last offset
        tp = TopicPartition(topic, partition, last_offset)
        consumer.assign([tp])
        consumer.seek(tp)

        # Poll for the last message
        msg = consumer.poll(timeout=2.0)
        if msg and not msg.error():
            latest_msg = msg.value().decode("utf-8")

    consumer.close()

    return latest_msg


# NOTE: this ReAct prompt is adapted from Langchain's ReAct agent: https://github.com/langchain-ai/langchain/blob/master/libs/langchain/langchain/agents/react/agent.py#L79
ReAct_prompt = """
You are a asistent help explore Apachy Kafka Broker based on input questions.

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


class KafkaExplorerAgent:
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
                "Only use the tools you have been provided with. "
                "When you have determined the Final Answer to the question, "
                "provide it in the format 'Final Answer: [your answer]' and "
                "then end your message with the word TERMINATE. "
                "Do not continue the conversation after providing the Final Answer."
            ),
            llm_config={"config_list": config_list, "cache_seed": None},
        )

        # Register the timeplus tool.
        register_function(
            list_kafka_topics,
            caller=self.assistant,
            executor=self.user_proxy,
            name="list_kafka_topics",
            description="list available kafka topics in the system",
        )

        register_function(
            get_latest_message,
            caller=self.assistant,
            executor=self.user_proxy,
            name="get_latest_message",
            description="return the latest messages from kafka topic",
        )

        register_function(
            get_topic_details,
            caller=self.assistant,
            executor=self.user_proxy,
            name="get_topic_details",
            description="return the detailed information of a kafka topic",
        )

        register_function(
            get_topic_offsets,
            caller=self.assistant,
            executor=self.user_proxy,
            name="get_topic_offsets",
            description="return the latest and earliest offset of a kafka topic",
        )

    def ask(self, question: str):
        with Cache.disk(cache_seed=43) as cache:
            self.user_proxy.initiate_chat(
                self.assistant,
                message=react_prompt_message,
                question=question,
                cache=cache,
            )

        # Get the conversation history
        chat_history = self.user_proxy.chat_messages[self.assistant]
        # Look through all messages for the "Final Answer:" pattern
        for message in reversed(chat_history):  # Start from the most recent
            content = message.get("content", "")
            if "Final Answer:" in content:
                final_answer = content.split("Final Answer:")[1].strip()
                return final_answer

        # If no "Final Answer:" pattern is found
        return "No final answer found in the conversation."
