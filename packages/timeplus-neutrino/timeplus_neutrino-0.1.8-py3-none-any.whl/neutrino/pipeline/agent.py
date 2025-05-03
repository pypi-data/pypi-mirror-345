import os
import asyncio
import tempfile


from autogen_core import (
    MessageContext,
    RoutedAgent,
    SingleThreadedAgentRuntime,
    TopicId,
    message_handler,
    type_subscription,
    AgentId,
)
from autogen_core.models import ChatCompletionClient, SystemMessage, UserMessage

from autogen_ext.models.cache import ChatCompletionCache, CHAT_CACHE_VALUE_TYPE
from autogen_ext.cache_store.diskcache import DiskCacheStore
from diskcache import Cache

from ..utils.tools import extract_code_blocks_with_type

from ..logging import get_event_logger
from ..message import Message, AgentLogEvent
from ..conf import TimeplusAgentConfig

logger = get_event_logger()
agent_config = TimeplusAgentConfig()

payload_extraction_topic = "PayloadExtractionAgent"
target_schema_inference_topic = "TargetSchemaInferenceAgent"
target_mutable_stream_schema_inference_topic = "TargetMutableStreamSchemaInferenceAgent"
target_stream_table_schema_inference_topic = (
    "TargetStreamTableSchemaInferenceAgent"  # generic agent for all streams/tables
)
mv_extraction_topic = "MVExtractionAgent"


@type_subscription(topic_type=payload_extraction_topic)
class PayloadExtractionAgent(RoutedAgent):
    def __init__(self, model_client: ChatCompletionClient) -> None:
        super().__init__("A agent extract payload.")
        self._system_message = SystemMessage(
            content=(
                """the input data is a debezium CDC data payload, our target is to extract the payload in after or payload:after into a new stream
    the source stream has just one string field with name raw

    here is are sample queries to extrac the after payload based on different types of debezium payload
    case1. when the after payload is in root layer
    select raw:after from source_stream_name where _tp_time > earliest_ts()
    case2. when the after payload is in field of payload
    select raw:payload:after from source_stream_name where _tp_time > earliest_ts()

    return which extract query should be used in markdown code with sql
"""
            )
        )
        self._model_client = model_client
        self._result = None

    @message_handler
    async def extract(self, message: Message, ctx: MessageContext) -> None:
        prompt = f"{message.content}"
        llm_result = await self._model_client.create(
            messages=[
                self._system_message,
                UserMessage(content=prompt, source=self.id.key),
            ],
            cancellation_token=ctx.cancellation_token,
        )
        response = llm_result.content
        log_event = AgentLogEvent(
            agent_description=self._description,
            sender_topic=payload_extraction_topic,
            receiver_topic=target_schema_inference_topic,
            system_message=self._system_message.content,
            user_prompt=prompt,
            response=response,
            model=str(self._model_client.model_info),
        )
        logger.info(log_event)
        self._result = response
        await self.publish_message(
            Message(f"{prompt} {response}"),
            topic_id=TopicId(target_schema_inference_topic, source=self.id.key),
        )
        await self.publish_message(
            Message(f"{prompt} {response}"),
            topic_id=TopicId(
                target_mutable_stream_schema_inference_topic, source=self.id.key
            ),
        )
        await self.publish_message(
            Message(f"{prompt} {response}"),
            topic_id=TopicId(
                target_stream_table_schema_inference_topic, source=self.id.key
            ),
        )


@type_subscription(topic_type=target_schema_inference_topic)
class TargetSchemaInferenceAgents(RoutedAgent):
    def __init__(self, model_client: ChatCompletionClient) -> None:
        super().__init__("A agent inference stream schema.")
        self._system_message = SystemMessage(
            content=(
                """please generate DDL based on debezium payload
    case1. when the after payload is in root layer, using json object in the after field as input
    case2. when the after payload is in field of payload,
     using the json string in the after field and only in the after field of payload as input
     No other fields should be considered, such as source, or schema etc

    here are the rules to follow
    * the DDL grammar follows ClickHouse style
    * the Table keyword MUST be replaced with Stream
    * all datatypes MUST be in lowercase, such uint32
    * all keywords MUST be in lowercase, such as nullable
    * all field names MUST keep same as in the json
    * composite types such as array, tuple, map cannot be nullable
    * should use composite types like array, map or tuple to represent complex structure in the json
    * output should be put into markdown of sql
    * bool type is supported
    * available composite types are
        * array
        * tuple
        * map
    * for composite type, using tuple over map, as tulpe is more generic

    here is a sample of output DDL

    ```sql
    CREATE STREAM target_stream
    (
      `cid` string,
      `gas_percent` float64,
      `in_use` bool,
      `latitude` float64,
      `longitude` float64,
      `locked` bool,
      `speed_kmh` float64,
      `time` string,
      `total_km` float64
    )
    ```
"""
            )
        )
        self._model_client = model_client
        self._result = None

    @message_handler
    async def inference(self, message: Message, ctx: MessageContext) -> None:
        prompt = f"{message.content}"
        llm_result = await self._model_client.create(
            messages=[
                self._system_message,
                UserMessage(content=prompt, source=self.id.key),
            ],
            cancellation_token=ctx.cancellation_token,
        )
        response = llm_result.content
        log_event = AgentLogEvent(
            agent_description=self._description,
            sender_topic=target_schema_inference_topic,
            receiver_topic=mv_extraction_topic,
            system_message=self._system_message.content,
            user_prompt=prompt,
            response=response,
            model=str(self._model_client.model_info),
        )
        logger.info(log_event)
        self._result = response
        await self.publish_message(
            Message(f"{prompt} {response}"),
            topic_id=TopicId(mv_extraction_topic, source=self.id.key),
        )


@type_subscription(topic_type=target_mutable_stream_schema_inference_topic)
class TargetMutableStreamSchemaInferenceAgent(RoutedAgent):
    def __init__(self, model_client: ChatCompletionClient) -> None:
        super().__init__("A agent inference mutable stream schema.")
        self._system_message = SystemMessage(
            content=(
                """please generate DDL based on debezium payload
    case1. when the after payload is in root layer, using json object in the after field as input
    case2. when the after payload is in field of payload,
    using the json string in the after field and only in the after field of payload as input
    No other fields should be considered, such as source, or schema etc

    the GRAMMAR is
    CREATE MUTABLE STREAM [IF NOT EXISTS] stream_name (
        <col1> <col_type>,
        <col2> <col_type>,
        <col3> <col_type>,
        <col4> <col_type>
        INDEX <index1> (col3)
        FAMILY <family1> (col3,col4)
    )
    PRIMARY KEY (col1, col2)


    here are the rules to follow
    * the DDL grammar follows ClickHouse style
    * all datatypes MUST be in lowercase, such uint32
    * all keywords MUST be in lowercase, such as nullable
    * all field names MUST keep same as in the json
    * composite types such as array, tuple, map cannot be nullable
    * should use composite types like array, map or tuple to represent complex structure in the json
    * output should be put into markdown of sql
    * bool type is supported
    * available composite types are
        * array
        * tuple
    * for composite type, using tuple over map, as tulpe is more generic

    here is a sample of output DDL:
    ```sql
    CREATE MUTABLE STREAM target_stream
    (
      `cid` string,
      `gas_percent` float64,
      `in_use` bool,
      `latitude` float64,
      `longitude` float64,
    )
    PRIMARY KEY (cid)
    ```
"""
            )
        )
        self._model_client = model_client
        self._result = None

    @message_handler
    async def inference(self, message: Message, ctx: MessageContext) -> None:
        prompt = f"{message.content}"
        llm_result = await self._model_client.create(
            messages=[
                self._system_message,
                UserMessage(content=prompt, source=self.id.key),
            ],
            cancellation_token=ctx.cancellation_token,
        )
        response = llm_result.content
        log_event = AgentLogEvent(
            agent_description=self._description,
            sender_topic=target_mutable_stream_schema_inference_topic,
            receiver_topic=mv_extraction_topic,
            system_message=self._system_message.content,
            user_prompt=prompt,
            response=response,
            model=str(self._model_client.model_info),
        )
        logger.info(log_event)
        self._result = response
        await self.publish_message(
            Message(f"{prompt} {response}"),
            topic_id=TopicId(mv_extraction_topic, source=self.id.key),
        )


@type_subscription(topic_type=target_stream_table_schema_inference_topic)
class TargetStreamAndTableSchemaInferenceAgent(RoutedAgent):
    def __init__(self, model_client: ChatCompletionClient) -> None:
        super().__init__("A agent inference stream and table schema DDL.")
        self._system_message = SystemMessage(
            content=(
                """please generate Timeplus stream or table creationDDL based on data payload
    case1. when the after payload is in root layer, using json object in the after field as input
    case2. when the after payload is in field of payload,
     using the json string in the after field and only in the after field of payload as input
     No other fields should be considered, such as source, or schema etc
     
    here are the grammar for different types of streams/tables
    * append-only stream
    CREATE STREAM [IF NOT EXISTS] [db.]<stream_name>
    (
        <col_name1> <col_type_1> [DEFAULT <col_expr_1>] [compression_codec_1],
        <col_name1> <col_type_2> [DEFAULT <col_expr_2>] [compression_codec_2]
    )
    SETTINGS <event_time_column>='<col>', <key1>=<value1>, <key2>=<value2>, ...
    
    * mutable stream
    CREATE MUTABLE STREAM [IF NOT EXISTS] stream_name (
        <col1> <col_type> [DEFAULT|ALIAS expr1],
        <col2> <col_type> [DEFAULT|ALIAS expr2],
        <col3> <col_type> [DEFAULT|ALIAS expr3],
        <col4> <col_type> [DEFAULT|ALIAS expr4],
        INDEX <index1> (column_list) [UNIQUE] [STORING (stored_column_list)],
        FAMILY <family1> (col3,col4)
        )
    PRIMARY KEY (col1, col2)
    SETTINGS
        logstore_retention_bytes=..,
        logstore_retention_ms=..,
        shards=..,
        replication_factor=..
        
    * ClickHouse/MySQL external table
    CREATE EXTERNAL TABLE name
    SETTINGS type='clickhouse|mysql',
            address='..',
            user='..',
            password='..',
            database='..',
            secure=true|false,
            table='..';
            
    * s3 external table
    CREATE EXTERNAL TABLE [IF NOT EXISTS] name
    (<col_name1> <col_type1>, <col_name2> <col_type2>, ...)
    PARTITION BY .. -- optional
    SETTINGS
        type='s3', -- required
        use_environment_credentials=true|false, -- optional, default false
        access_key_id='..', -- optional
        secret_access_key='..', -- optional
        region='..', -- required
        bucket='..', -- required
        read_from='..', -- optional
        write_to='..', -- optional
        data_format='..', -- optional
        ...
        
    * kafka external stream
    CREATE EXTERNAL STREAM [IF NOT EXISTS] stream_name (<col_name1> <col_type>)
    SETTINGS type='kafka',
            brokers='ip:9092',
            topic='..',
            security_protocol='..',
            username='..',
            password='..',
            sasl_mechanism='..',
            data_format='..',
            format_schema='..',
            one_message_per_row=..,
            kafka_schema_registry_url='..',
            kafka_schema_registry_credentials='..',
            ssl_ca_cert_file='..',
            ss_ca_pem='..',
            skip_ssl_cert_check=..,
            properties='..',
            config_file='..'


    here are the rules to follow
    * the DDL grammar follows ClickHouse style
    * all datatypes MUST be in lowercase, such uint32
    * all keywords MUST be in lowercase, such as nullable
    * all field names MUST keep same as in the json
    * composite types such as array, tuple, map cannot be nullable
    * should use composite types like array, map or tuple to represent complex structure in the json
    * output should be put into markdown of sql
    * bool type is supported
    * available composite types are
        * array
        * tuple
    * for composite type, using tuple over map, as tulpe is more generic
    
    here are samples of the output DDL
    
    append-only stream:
    ```sql
    CREATE STREAM target_stream
    (
      `cid` string,
      `gas_percent` float64,
      `in_use` bool,
      `latitude` float64,
      `longitude` float64,
      `locked` bool,
      `speed_kmh` float64,
      `time` string,
      `total_km` float64
    )
    ```
    
    mutable stream:
    ```sql
    CREATE MUTABLE STREAM target_stream
    (
      `cid` string,
      `gas_percent` float64,
      `in_use` bool,
      `latitude` float64,
      `longitude` float64,
    )
    PRIMARY KEY (cid)
    ```
"""
            )
        )
        self._model_client = model_client
        self._result = None

    @message_handler
    async def inference(self, message: Message, ctx: MessageContext) -> None:
        prompt = f"{message.content}"
        llm_result = await self._model_client.create(
            messages=[
                self._system_message,
                UserMessage(content=prompt, source=self.id.key),
            ],
            cancellation_token=ctx.cancellation_token,
        )
        response = llm_result.content
        log_event = AgentLogEvent(
            agent_description=self._description,
            sender_topic=target_mutable_stream_schema_inference_topic,
            receiver_topic=mv_extraction_topic,
            system_message=self._system_message.content,
            user_prompt=prompt,
            response=response,
            model=str(self._model_client.model_info),
        )
        logger.info(log_event)
        self._result = response
        await self.publish_message(
            Message(f"{prompt} {response}"),
            topic_id=TopicId(mv_extraction_topic, source=self.id.key),
        )


@type_subscription(topic_type=mv_extraction_topic)
class MVExtractionAgent(RoutedAgent):
    def __init__(self, model_client: ChatCompletionClient) -> None:
        super().__init__("A agent inference mutable stream schema.")
        self._system_message = SystemMessage(
            content=(
                """please create a materialized view to extraction information from source stream into target stream
    the source stream has just one string field with name raw
    here are the rules to following
    * the grammar follows ClickHouse style
    * all function name follows snake case, such as json_extract_array
    * all keywords MUST be in lowercase, such as nullable
    * using tuple for hierarchy case which is generic
    * please CHECK the structure of the source payload, make sure the extraction map the structure excatly
      especially when there is tuple of tuple, make sure each layer of tuple clearly casted using tuple_cast


    here is the grammar of materialized view
    CREATE MATERIALIZED VIEW [IF NOT EXISTS] <view_name>
    INTO <target_stream> AS <SELECT ...>

    NOTE, to extrat json with hierarchy,
    this one is WRONG : json_extract_uint(raw, 'after.customer_id') AS customer_id
    extract target field does not support hierarchy
    SHOULD BE : json_extract_uint(raw:after, 'customer_id') AS customer_id,

    this one is WRONG : tuple_cast(json_extract_string(raw:payload:after, '_id.$oid')) AS _id,
    SHOULD BE : tuple_cast(json_extract_string(raw:payload:after:_id, '$oid')) AS _id,

    to construct or convert tuple type , call tuple_cast, for example:
    tuple_cast(a, b) AS tuple_field,
    there is no tuple() function, NEVER call tuple() function

    For each tuple type, SHOULD use tuple_cast to extract it from original json.

    In case the payload contains complex composition and hierarchy, you should provide the conversion layer by layer, do not miss any middle layer
    here is a sample that one of the target field is a array of tuple, using array_map function to help
    array_map(
        x -> (
            tuple_cast(
                json_extract_string(x, 'field_name') as field_name,
            )
        ),
        json_extract_array(after:raw_data, 'field_name_3')
    ) as field

    please only use following available json extraction functions if required:
    * json_extract_int
    * json_extract_uint
    * json_extract_float
    * json_extract_bool
    * json_extract_string
    * json_extract_array
    ```
"""
            )
        )
        self._model_client = model_client
        self._result = None

    @message_handler
    async def extract(self, message: Message, ctx: MessageContext) -> None:
        prompt = f"please create materialized view to extrat information from source stream to target stream, {message}"
        llm_result = await self._model_client.create(
            messages=[
                self._system_message,
                UserMessage(content=prompt, source=self.id.key),
            ],
            cancellation_token=ctx.cancellation_token,
        )
        response = llm_result.content
        log_event = AgentLogEvent(
            agent_description=self._description,
            sender_topic=mv_extraction_topic,
            receiver_topic="",
            system_message=self._system_message.content,
            user_prompt=prompt,
            response=response,
            model=str(self._model_client.model_info),
        )
        logger.info(log_event)
        self._result = response


class DataExtractionAgent:
    def __init__(self):
        # cache_dir = os.path.join(os.getcwd(), ".neutrino_cache")
        cache_dir = os.path.join(tempfile.gettempdir(), ".neutrino_cache")
        os.makedirs(cache_dir, exist_ok=True)  # Ensure the directory exists
        openai_model_client = agent_config.get_client("default")
        cache_store = DiskCacheStore[CHAT_CACHE_VALUE_TYPE](Cache(cache_dir))
        self.client = ChatCompletionCache(openai_model_client, cache_store)
        self.runtime = SingleThreadedAgentRuntime()

    async def _pipeline(self, data, source_stream_name, target_stream_name):
        await PayloadExtractionAgent.register(
            self.runtime,
            type=payload_extraction_topic,
            factory=lambda: PayloadExtractionAgent(model_client=self.client),
        )

        await TargetSchemaInferenceAgents.register(
            self.runtime,
            type=target_schema_inference_topic,
            factory=lambda: TargetSchemaInferenceAgents(model_client=self.client),
        )

        await MVExtractionAgent.register(
            self.runtime,
            type=mv_extraction_topic,
            factory=lambda: MVExtractionAgent(model_client=self.client),
        )

        message = f"based on input data : {data} and source stream name {source_stream_name} and target stream name {target_stream_name}"
        self.runtime.start()

        await self.runtime.publish_message(
            Message(content=message),
            topic_id=TopicId(payload_extraction_topic, source="default"),
        )

        await self.runtime.stop_when_idle()

        target_schema_inference_agent_id = AgentId(
            target_schema_inference_topic, "default"
        )
        target_schema_inference_agent = (
            await self.runtime.try_get_underlying_agent_instance(
                target_schema_inference_agent_id
            )
        )

        mv_extraction_agent_id = AgentId(mv_extraction_topic, "default")
        mv_extraction_agent = await self.runtime.try_get_underlying_agent_instance(
            mv_extraction_agent_id
        )

        schema_inference_result = extract_code_blocks_with_type(
            target_schema_inference_agent._result
        )
        mv_extraction_result = extract_code_blocks_with_type(
            mv_extraction_agent._result
        )

        # TODO: handle failed to extract case
        return (
            schema_inference_result[-1][1],
            mv_extraction_result[-1][1],
        )

    def pipeline(self, data, source_stream_name, target_stream_name):
        return asyncio.run(self._pipeline(data, source_stream_name, target_stream_name))

    async def async_pipeline(self, data, source_stream_name, target_stream_name):
        return await self._pipeline(data, source_stream_name, target_stream_name)

    async def _pipeline_with_mutable_stream(
        self, data, source_stream_name, target_stream_name, ids
    ):
        await PayloadExtractionAgent.register(
            self.runtime,
            type=payload_extraction_topic,
            factory=lambda: PayloadExtractionAgent(model_client=self.client),
        )

        await TargetMutableStreamSchemaInferenceAgent.register(
            self.runtime,
            type=target_mutable_stream_schema_inference_topic,
            factory=lambda: TargetMutableStreamSchemaInferenceAgent(
                model_client=self.client
            ),
        )

        await MVExtractionAgent.register(
            self.runtime,
            type=mv_extraction_topic,
            factory=lambda: MVExtractionAgent(model_client=self.client),
        )

        message = f"based on input data : {data} and target stream name {target_stream_name}, and id fields {','.join(ids)}"
        self.runtime.start()

        await self.runtime.publish_message(
            Message(content=message),
            topic_id=TopicId(payload_extraction_topic, source="default"),
        )

        await self.runtime.stop_when_idle()

        target_schema_inference_agent_id = AgentId(
            target_mutable_stream_schema_inference_topic, "default"
        )
        target_schema_inference_agent = (
            await self.runtime.try_get_underlying_agent_instance(
                target_schema_inference_agent_id
            )
        )

        mv_extraction_agent_id = AgentId(mv_extraction_topic, "default")
        mv_extraction_agent = await self.runtime.try_get_underlying_agent_instance(
            mv_extraction_agent_id
        )

        schema_inference_result = extract_code_blocks_with_type(
            target_schema_inference_agent._result
        )
        mv_extraction_result = extract_code_blocks_with_type(
            mv_extraction_agent._result
        )

        # TODO: handle failed to extract case
        return (
            schema_inference_result[-1][1],
            mv_extraction_result[-1][1],
        )

    def pipeline_with_mutable_stream(
        self, data, source_stream_name, target_stream_name, ids
    ):
        return asyncio.run(
            self._pipeline_with_mutable_stream(
                data, source_stream_name, target_stream_name, ids
            )
        )

    async def _generic_pipeline(
        self, data, source_stream_name, target_stream_name, properties
    ):
        await PayloadExtractionAgent.register(
            self.runtime,
            type=payload_extraction_topic,
            factory=lambda: PayloadExtractionAgent(model_client=self.client),
        )

        await TargetStreamAndTableSchemaInferenceAgent.register(
            self.runtime,
            type=target_stream_table_schema_inference_topic,
            factory=lambda: TargetStreamAndTableSchemaInferenceAgent(
                model_client=self.client
            ),
        )

        await MVExtractionAgent.register(
            self.runtime,
            type=mv_extraction_topic,
            factory=lambda: MVExtractionAgent(model_client=self.client),
        )

        message = f"based on input data : {data} and source stream name {source_stream_name} , target stream name {target_stream_name}, and properties {properties}"
        self.runtime.start()

        await self.runtime.publish_message(
            Message(content=message),
            topic_id=TopicId(payload_extraction_topic, source="default"),
        )

        await self.runtime.stop_when_idle()

        target_schema_inference_agent_id = AgentId(
            target_stream_table_schema_inference_topic, "default"
        )
        target_schema_inference_agent = (
            await self.runtime.try_get_underlying_agent_instance(
                target_schema_inference_agent_id
            )
        )

        mv_extraction_agent_id = AgentId(mv_extraction_topic, "default")
        mv_extraction_agent = await self.runtime.try_get_underlying_agent_instance(
            mv_extraction_agent_id
        )

        schema_inference_result = extract_code_blocks_with_type(
            target_schema_inference_agent._result
        )
        mv_extraction_result = extract_code_blocks_with_type(
            mv_extraction_agent._result
        )

        # TODO: handle failed to extract case
        return (
            schema_inference_result[-1][1],
            mv_extraction_result[-1][1],
        )

    def generic_pipeline(
        self, data, source_stream_name, target_stream_name, properties
    ):
        return asyncio.run(
            self._generic_pipeline(
                data, source_stream_name, target_stream_name, properties
            )
        )

    async def async_generic_pipeline(
        self, data, source_stream_name, target_stream_name, properties
    ):
        return await self._generic_pipeline(
            data, source_stream_name, target_stream_name, properties
        )
