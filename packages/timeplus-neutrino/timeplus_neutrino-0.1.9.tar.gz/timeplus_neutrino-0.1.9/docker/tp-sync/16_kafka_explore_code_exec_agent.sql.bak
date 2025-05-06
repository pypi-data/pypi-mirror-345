CREATE OR REPLACE FUNCTION ask_kafka_with_code_executor(question string) RETURNS string LANGUAGE PYTHON AS 
$$
import traceback
import venv
import asyncio
import re
import asyncio

from pathlib import Path
from typing import List

from autogen_core import CancellationToken
from autogen_core import AgentId
from autogen_core.code_executor import CodeBlock, CodeExecutor
from autogen_ext.code_executors.local import LocalCommandLineCodeExecutor
from dataclasses import dataclass
from autogen_core import (
    MessageContext,
    RoutedAgent,
    SingleThreadedAgentRuntime,
    TopicId,
    TypeSubscription,
    message_handler,
    type_subscription,
)
from autogen_core.models import ChatCompletionClient, SystemMessage, UserMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient

work_dir = Path("./coding")
work_dir.mkdir(exist_ok=True)

venv_dir = work_dir / ".venv"
venv_builder = venv.EnvBuilder(with_pip=True)
venv_builder.create(venv_dir)
venv_context = venv_builder.ensure_directories(venv_dir)

local_executor = LocalCommandLineCodeExecutor(work_dir=work_dir, virtual_env_context=venv_context)

async def install_dep(exectuor):
    await exectuor.execute_code_blocks(
        code_blocks=[
            CodeBlock(language="bash", code="pip install confluent-kafka")
        ],
        cancellation_token=CancellationToken(),
    )

asyncio.run(install_dep(local_executor)) 

@dataclass
class Message:
    content: str

code_writer_topic = "CodeWriterAgent"
code_execution_topic = "CodeExecutionAgent"

@type_subscription(topic_type=code_writer_topic)
class CodeWriterAgent(RoutedAgent):
    def __init__(self, model_client: ChatCompletionClient) -> None:
        super().__init__("A code writer agent.")
        self._system_message = SystemMessage(
            content=(
                '''You are a code generator generating workable python code based on confluent-kafka, 
the code will be used to explore apache kafka cluster and brokers,
DONOT generate code other than python, such as install depedency using pip

here are some sample code for your to refer:

1. list topic
from confluent_kafka.admin import AdminClient

def list_topics(broker: str):
    admin_client = AdminClient({'bootstrap.servers': broker})
    metadata = admin_client.list_topics(timeout=5)
    return list(metadata.topics.keys())

# Example usage
print(list_topics("localhost:9092"))

2. Get Topic Details (Partitions, Replicas)
from confluent_kafka.admin import AdminClient
def get_topic_details(broker: str, topic: str):
    admin_client = AdminClient({'bootstrap.servers': broker})
    metadata = admin_client.list_topics(topic, timeout=5)

    if topic not in metadata.topics:
        return f"Topic '{topic}' not found"

    topic_info = metadata.topics[topic]
    return {p.id: {"replicas": p.replicas} for p in topic_info.partitions.values()}

# Example usage
print(get_topic_details("localhost:9092", "your_topic"))

3. Create Topic

from confluent_kafka.admin import NewTopic
from confluent_kafka.admin import AdminClient

def create_topic(broker: str, topic: str, num_partitions: int, replication_factor: int):
    admin_client = AdminClient({'bootstrap.servers': broker})

    new_topic = NewTopic(topic, num_partitions, replication_factor)
    fs = admin_client.create_topics([new_topic])

    for topic, f in fs.items():
        try:
            f.result()  # Wait for topic creation
            print(f"Topic '{topic}' created successfully")
        except Exception as e:
            print(f"Failed to create topic '{topic}': {e}")

# Example usage
create_topic("localhost:9092", "new_topic", 3, 1)

4. Delete Topic

from confluent_kafka.admin import AdminClient
def delete_topic(broker: str, topic: str):
    admin_client = AdminClient({'bootstrap.servers': broker})

    fs = admin_client.delete_topics([topic])

    for topic, f in fs.items():
        try:
            f.result()  # Wait for deletion
            print(f"Topic '{topic}' deleted successfully")
        except Exception as e:
            print(f"Failed to delete topic '{topic}': {e}")

# Example usage
delete_topic("localhost:9092", "old_topic")
                '''
            )
        )
        self._model_client = model_client

    @message_handler
    async def handle_user_description(self, message: Message, ctx: MessageContext) -> None:
        prompt = f"requirement description: {message.content}"
        llm_result = await self._model_client.create(
            messages=[self._system_message, UserMessage(content=prompt, source=self.id.key)],
            cancellation_token=ctx.cancellation_token,
        )
        response = llm_result.content
        assert isinstance(response, str)
        print(f"{'-'*80}\n{self.id.type}:\n{response}")
        
        await self.publish_message(Message(response), topic_id=TopicId(code_execution_topic, source=self.id.key))

def extract_markdown_code_blocks(markdown_text: str) -> List[CodeBlock]:
    pattern = re.compile(r"```(?:\s*([\w\+\-]+))?\n([\s\S]*?)```")
    matches = pattern.findall(markdown_text)
    code_blocks: List[CodeBlock] = []
    for match in matches:
        language = match[0].strip() if match[0] else ""
        code_content = match[1]
        code_blocks.append(CodeBlock(code=code_content, language=language))
    return code_blocks


@type_subscription(topic_type=code_execution_topic)
class CodeExecutionAgent(RoutedAgent):
    def __init__(self, code_executor: CodeExecutor) -> None:
        super().__init__("An executor agent.")
        self._code_executor = code_executor
        self._result = None

    @message_handler
    async def handle_message(self, message: Message, ctx: MessageContext) -> None:
        code_blocks = extract_markdown_code_blocks(message.content)
        if code_blocks:
            result = await self._code_executor.execute_code_blocks(
                code_blocks, cancellation_token=ctx.cancellation_token
            )
            print(f"\n{'-'*80}\nExecutor:\n{result.output}")
            self._result = result.output

model_client = OpenAIChatCompletionClient(
        model="gpt-4o-mini", 
        temperature=0.0
    )

async def run(runtime):
    await CodeWriterAgent.register(
        runtime, type=code_writer_topic, factory=lambda: CodeWriterAgent(model_client=model_client)
    )

    await CodeExecutionAgent.register(
        runtime, type=code_execution_topic, factory=lambda: CodeExecutionAgent(code_executor=local_executor)
    )

    runtime.start()

    await runtime.publish_message(
        Message(content=question),
        topic_id=TopicId(code_writer_topic, source="default"),
    )

    await runtime.stop_when_idle()

    agent_id = AgentId(code_execution_topic, "default")
    agent = await runtime.try_get_underlying_agent_instance(agent_id)
    return agent._result

def ask_kafka_with_code_executor(question):
    runtime = SingleThreadedAgentRuntime()

    results = []
    for (question) in zip(question):
        try:
            result = asyncio.run(run(runtime))
            results.append(result)
        except Exception as e:
            trace = traceback.format_exc()
            results.append(trace)

    return results

$$;