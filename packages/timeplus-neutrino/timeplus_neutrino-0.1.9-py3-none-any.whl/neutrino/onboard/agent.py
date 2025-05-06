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

schema_inference_agent_topic = "SchemaInferenceAgent"
schema_to_table_agent_topic = "SchemaToTableAgent"
field_summary_agent_topic = "FieldSummaryAgent"
analysis_recommendations_agent_topic = "AnalysisRecommendationsAgent"


@type_subscription(topic_type=schema_inference_agent_topic)
class SchemaInferenceAgent(RoutedAgent):
    def __init__(self, model_client: ChatCompletionClient) -> None:
        super().__init__("A schema inference agent.")
        self._system_message = SystemMessage(
            content=(
                """please generate DDL based on input data which is a json object or list of json object seperated by comma
    here are the rules to follow
    * the DDL grammar follows ClickHouse style
    * the Table keyword MUST be replaced with Stream
    * all datatypes MUST be in lowercase, such uint32
    * all keywords MUST be in lowercase, such as nullable
    * all field names MUST keep same as in the json
    * composite types such as array, tuple cannot be nullable
    * should use composite types like array, tuple to represent complex structure in the json
    * from composite types, prefer tuple over map
    * if the data value is null, field type MUST be set as 'unknown'
    * return the result as a markdown sql code
    * Make sure the hierarchy is represented in the DDL match the input data
    * No need return table engine and settings in the DDL
    * DO include TTL and SETTINGS refer to the sample output
    * ALWAYS use _tp_time as the event time column for TTL
    * Put description into the comment

    the DDL grammar is
    CREATE STREAM [IF NOT EXISTS] [db.]<stream_name>
    (
        <col_name1> <col_type_1> [DEFAULT <col_expr_1>] [compression_codec_1],
        <col_name1> <col_type_2> [DEFAULT <col_expr_2>] [compression_codec_2]
    )
    SETTINGS <event_time_column>='<col>', <key1>=<value1>, <key2>=<value2>, ...


    here is a sample of output DDL:
    ```sql
    CREATE STREAM car_live_data
    (
      `cid` string,
      `gas_percent` float64,
      `in_use` bool
    )
    TTL to_datetime(_tp_time) + INTERVAL 1 DAY
    SETTINGS mode = 'append',
        logstore_retention_bytes = '-1',
        logstore_retention_ms = '86400000',
        index_granularity = 8192
    COMMENT ''
    ```

    here is a list of supported datatypes:
    * string
    * int, int32, int8, int64, smallint, bigint, uint16, uint32, uint64
    * float64, float32, double
    * decimal
    * bool
    * ipv4
    * ipv6
    * date
    * datetime
    * datetime64
    * uuid
    * tuple
    * array
    * map
"""
            )
        )
        self._model_client = model_client
        self._result = None

    @message_handler
    async def inference(self, message: Message, ctx: MessageContext) -> None:
        prompt = f"{message.content}, please generate schema"
        llm_result = await self._model_client.create(
            messages=[
                self._system_message,
                UserMessage(content=prompt, source=self.id.key),
            ],
            cancellation_token=ctx.cancellation_token,
        )
        response = llm_result.content
        self._result = response
        log_event = AgentLogEvent(
            agent_description=self._description,
            sender_topic=schema_inference_agent_topic,
            receiver_topic=schema_to_table_agent_topic,
            system_message=self._system_message.content,
            user_prompt=prompt,
            response=response,
            model=str(self._model_client.model_info),
        )
        logger.info(log_event)
        await self.publish_message(
            Message(response),
            topic_id=TopicId(schema_to_table_agent_topic, source=self.id.key),
        )


@type_subscription(topic_type=schema_inference_agent_topic)
class MutableStreamSchemaInferenceAgent(SchemaInferenceAgent):
    def __init__(self, model_client: ChatCompletionClient) -> None:
        super().__init__(model_client)
        self._system_message = SystemMessage(
            content=(
                """please generate DDL based on input data which is a json object or list of json object seperated by comma, and primary keys
    here are the rules to follow
    * the DDL grammar follows ClickHouse style
    * the Table keyword MUST be replaced with Stream
    * all datatypes MUST be in lowercase, such uint32
    * all keywords MUST be in lowercase, such as nullable
    * all field names MUST keep same as in the json
    * composite types such as array, tuple cannot be nullable
    * should use composite types like array, tuple to represent complex structure in the json
    * from composite types, prefer tuple over map
    * if the data value is null, field type MUST be set as 'unknown'
    * return the result as a markdown sql code
    * Make sure the hierarchy is represented in the DDL match the input data
    * No need return table engine and settings in the DDL
    * Put description into the comment
    * Leave the primary key empty or default placeholder, user will input the id later

    the DDL grammar is
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


    here is a sample of output DDL:
    ```sql
    CREATE MUTABLE STREAM car_live_data
    (
      `cid` string,
      `gas_percent` float64,
      `in_use` bool
    )
    PRIMARY KEY (input_comma_separated_primary_keys_here)
    COMMENT ''
    ```

    here is a list of supported datatypes:
    * string
    * int, int32, int8, int64, smallint, bigint, uint16, uint32, uint64
    * float64, float32, double
    * decimal
    * bool
    * ipv4
    * ipv6
    * date
    * datetime
    * datetime64
    * uuid
    * tuple
    * array
    * map
"""
            )
        )


@type_subscription(topic_type=schema_inference_agent_topic)
class ExternalStreamSchemaInferenceAgent(SchemaInferenceAgent):
    def __init__(self, model_client: ChatCompletionClient) -> None:
        super().__init__(model_client)
        self._system_message = SystemMessage(
            content=(
                """please generate DDL based on input data which is a json object or list of json object seperated by comma, and related properties
    here are the rules to follow
    * the DDL grammar follows ClickHouse style
    * the Table keyword MUST be replaced with Stream
    * all datatypes MUST be in lowercase, such uint32
    * all keywords MUST be in lowercase, such as nullable
    * all field names MUST keep same as in the json
    * composite types such as array, tuple cannot be nullable
    * should use composite types like array, tuple to represent complex structure in the json
    * from composite types, prefer tuple over map
    * if the data value is null, field type MUST be set as 'unknown'
    * return the result as a markdown sql code
    * Make sure the hierarchy is represented in the DDL match the input data
    * No need return table engine and settings in the DDL
    * Put description into the comment

    the DDL grammar is
    CREATE EXTERNAL STREAM [IF NOT EXISTS] stream_name (<col_name1> <col_type>)
    SETTINGS type='kafka',
            brokers='ip:9092',
            topic='..',
            security_protocol='..',
            username='..',
            password='..',
            sasl_mechanism='..',
            data_format='..',
            kafka_schema_registry_url='..',
            kafka_schema_registry_credentials='..',
            ssl_ca_cert_file='..',
            ss_ca_pem='..',
            skip_ssl_cert_check=..,
            config_file='..'


    here is a sample of output DDL:
    ```sql
    CREATE EXTERNAL STREAM car_live_data
    (
      `cid` string,
      `gas_percent` float64,
      `in_use` bool
    )
    SETTINGS type = 'kafka',
        brokers = 'redpanda:9092',
        topic = 'csv_topic',
        security_protocol = 'PLAINTEXT',
        data_format = 'RawBLOB',
        skip_ssl_cert_check = 'false',
        one_message_per_row = 'true'
    COMMENT ''
    ```

    here is a list of supported datatypes:
    * string
    * int, int32, int8, int64, smallint, bigint, uint16, uint32, uint64
    * float64, float32, double
    * decimal
    * bool
    * ipv4
    * ipv6
    * date
    * datetime
    * datetime64
    * uuid
    * tuple
    * array
    * map
"""
            )
        )


@type_subscription(topic_type=schema_to_table_agent_topic)
class SchemaToTableAgent(RoutedAgent):
    def __init__(self, model_client: ChatCompletionClient) -> None:
        super().__init__("A agent turn schema to column table.")
        self._system_message = SystemMessage(
            content=(
                """based on generated DDL, please convert it into a json object
    Rules:
    * for type string, it MUST be a single line for string

    for example, if the input DDL is:
    CREATE STREAM car_live_data
    (
      `cid` string,
      `gas_percent` float64,
      `in_use` bool,
      `composite` tuple(
          'x' int
          ),
    )

    the output of the json description of the DDL should be:
    ```json

    [
        {
            "name" : "cid", "type" : "string"
        },
        {
            "name" : "gas_percent", "type" : "float64"
        },
        {
            "name" : "in_use", "type" : "bool"
        },
        {
            "name" : "composite", "type" : "tuple('x' int)"
        }
    ]
    ```
"""
            )
        )
        self._model_client = model_client
        self._result = None

    @message_handler
    async def convert(self, message: Message, ctx: MessageContext) -> None:
        prompt = f"{message.content}, please convert to table"
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
            sender_topic=schema_to_table_agent_topic,
            receiver_topic="",
            system_message=self._system_message.content,
            user_prompt=prompt,
            response=response,
            model=str(self._model_client.model_info),
        )
        logger.info(log_event)
        self._result = response


@type_subscription(topic_type=field_summary_agent_topic)
class FieldSummaryAgent(RoutedAgent):
    def __init__(self, model_client: ChatCompletionClient) -> None:
        super().__init__("A agent provide field summary of a stream/table.")
        self._system_message = SystemMessage(
            content=(
                """please update DDL to add field comment for each column, based on the input sample data and schema,
    here is a sample of the output:
    ```sql
    CREATE STREAM customer
    (
        `customer_id` int COMMENT 'unique customer id',
        `name` string COMMENT 'customer name',
        `email` string COMMENT 'customer email',
        `info` tuple(`name` string, `email` string) COMMENT 'customer information'
    )
    ```

    NOTE, the comment SHOULD only apply to the first level for composite type, i.e. `tuple('name' string, 'email' string)`
    NO comment SHOULD be added for child columnes of tuple, map, array
"""
            )
        )
        self._model_client = model_client
        self._result = None

    @message_handler
    async def summary(self, message: Message, ctx: MessageContext) -> None:
        prompt = f"{message.content}, please generate field summary"
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
            sender_topic=field_summary_agent_topic,
            receiver_topic="",
            system_message=self._system_message.content,
            user_prompt=prompt,
            response=response,
            model=str(self._model_client.model_info),
        )
        logger.info(log_event)
        self._result = response


@type_subscription(topic_type=analysis_recommendations_agent_topic)
class AnalysisRecommendationsAgent(RoutedAgent):
    def __init__(self, model_client: ChatCompletionClient) -> None:
        super().__init__(
            "A agent provide analysis recommendations base on schema and sample data."
        )

        self._system_message = SystemMessage(
            content=(
                """please generate 10 analysis SQL based on input sample data and DDL
    output into a json object which is an array
    note, you need escape newlines if the output contains multiple lines string

    The generate SQL should follow these rules
    * the SQL follows the ClickHouse grammar
    * all function name MUST be in lower cases, following snake cases, for example : array_sum
    * no CROSS JOIN is supported
    * Only quote the column name with ` if the column name contains -, space or start with number

    As timeplus is a streaming processing platform, there are three different types of query regarding how to scan the data
    please use one of these three patterns to each generate SQL

    1 temperal window based analysis tumble window with 5 second window size
    following query return analysis result in a continously streaming query for every 5 second window
    select window_start, window_end, count(*) as count, max(c1) as max_c1
    from tumble(my_stream, 5s) group by window_start, window_end

    2 global aggregration which Global aggregation will start the aggregation for all incoming events since the query is submitted, and never ends.
    select count(*) as count, id as id
    from my_stream group by id

    3 historical aggreation, using table function, the query will just run traditional SQL that scan all historical data and return after query end
    select count(*) as count, id as id
    from table(my_stream) group by id


    #########
    here is a sample output:
    [
      {
        "sql": "select eventVersion, sum(videoSourceBandwidthBytesPerEvent + videoFecBandwidthBytesPerEvent + audioSourceBandwidthBytesPerEvent + audioFecBandwidthBytesPerEvent) as total_bandwidth_bytes from xray_stream group by eventVersion",
        "description": "Calculate the total bandwidth used per event version by summing up video, audio, and FEC bandwidths.",
        "name" : "Bandwidth Utilization Analysis"
      }
    ]"""
            )
        )
        self._model_client = model_client
        self._result = None

    @message_handler
    async def summary(self, message: Message, ctx: MessageContext) -> None:
        prompt = f"{message.content}, please generate field summary"
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
            sender_topic=analysis_recommendations_agent_topic,
            receiver_topic="",
            system_message=self._system_message.content,
            user_prompt=prompt,
            response=response,
            model=str(self._model_client.model_info),
        )
        logger.info(log_event)
        self._result = response


class DataOnboardingAgent:
    def __init__(self):
        # cache_dir = os.path.join(os.getcwd(), ".neutrino_cache")
        cache_dir = os.path.join(tempfile.gettempdir(), ".neutrino_cache")
        os.makedirs(cache_dir, exist_ok=True)  # Ensure the directory exists
        openai_model_client = agent_config.get_client("default")
        cache_store = DiskCacheStore[CHAT_CACHE_VALUE_TYPE](Cache(cache_dir))
        self.client = ChatCompletionCache(openai_model_client, cache_store)
        self.runtime = SingleThreadedAgentRuntime()

    async def _inference(self, message, stream_type="append"):
        inferenceAgentClass = (
            SchemaInferenceAgent  # TODO: switch to different agent here
        )

        if stream_type == "mutable":
            inferenceAgentClass = MutableStreamSchemaInferenceAgent
        elif stream_type == "external":
            inferenceAgentClass = ExternalStreamSchemaInferenceAgent

        await inferenceAgentClass.register(
            self.runtime,
            type=schema_inference_agent_topic,
            factory=lambda: inferenceAgentClass(model_client=self.client),
        )

        await SchemaToTableAgent.register(
            self.runtime,
            type=schema_to_table_agent_topic,
            factory=lambda: SchemaToTableAgent(model_client=self.client),
        )

        self.runtime.start()

        await self.runtime.publish_message(
            Message(content=message),
            topic_id=TopicId(schema_inference_agent_topic, source="default"),
        )

        await self.runtime.stop_when_idle()
        inference_agent_id = AgentId(schema_inference_agent_topic, "default")
        inference_agent = await self.runtime.try_get_underlying_agent_instance(
            inference_agent_id
        )

        table_agent_id = AgentId(schema_to_table_agent_topic, "default")
        table_agent = await self.runtime.try_get_underlying_agent_instance(
            table_agent_id
        )

        inference_result = extract_code_blocks_with_type(inference_agent._result)
        table_result = extract_code_blocks_with_type(table_agent._result)

        # TODO: handle failed to extract case
        return inference_result[0][1], table_result[0][1]

    def inference(self, data, stream_name, description=""):
        message = f"based on input data : {data}, and stream name : {stream_name}, and description : {description}"
        return asyncio.run(self._inference(message))

    def inference_mutable_stream(self, data, stream_name, description=""):
        message = f"based on input data : {data}, and stream name : {stream_name}, and description : {description}"
        return asyncio.run(self._inference(message, stream_type="mutable"))

    def inference_external_stream(self, data, stream_name, properties, description=""):
        message = f"based on input data : {data}, and stream name : {stream_name}, and properties : {properties} , and description : {description}"
        return asyncio.run(self._inference(message, stream_type="external"))

    async def async_inference(self, data, stream_name, description=""):
        message = f"based on input data : {data}, and stream name : {stream_name}, and description : {description}"
        return await self._inference(message)

    async def aysnc_inference_mutable_stream(self, data, stream_name, description=""):
        message = f"based on input data : {data}, and stream name : {stream_name}, and description : {description}"
        return await self._inference(message, stream_type="mutable")

    async def async_inference_external_stream(
        self, data, stream_name, properties, description=""
    ):
        message = f"based on input data : {data}, and stream name : {stream_name}, and properties : {properties} , and description : {description}"
        return await self._inference(message, stream_type="external")

    async def _summary(self, data, columns):
        await FieldSummaryAgent.register(
            self.runtime,
            type=field_summary_agent_topic,
            factory=lambda: FieldSummaryAgent(model_client=self.client),
        )

        message = f"based on input data : {data}, and ddl : {columns}"
        self.runtime.start()

        await self.runtime.publish_message(
            Message(content=message),
            topic_id=TopicId(field_summary_agent_topic, source="default"),
        )

        await self.runtime.stop_when_idle()
        agent_id = AgentId(field_summary_agent_topic, "default")
        agent = await self.runtime.try_get_underlying_agent_instance(agent_id)

        result = extract_code_blocks_with_type(agent._result)

        # TODO: handle failed to extract case
        return result[0][1]

    def summary(self, data, ddl):
        return asyncio.run(self._summary(data, ddl))

    async def _recommendations(self, data, ddl):
        await AnalysisRecommendationsAgent.register(
            self.runtime,
            type=analysis_recommendations_agent_topic,
            factory=lambda: AnalysisRecommendationsAgent(model_client=self.client),
        )

        message = f"based on input data : {data}, and ddl : {ddl} "
        self.runtime.start()

        await self.runtime.publish_message(
            Message(content=message),
            topic_id=TopicId(analysis_recommendations_agent_topic, source="default"),
        )

        await self.runtime.stop_when_idle()
        agent_id = AgentId(analysis_recommendations_agent_topic, "default")
        agent = await self.runtime.try_get_underlying_agent_instance(agent_id)

        result = extract_code_blocks_with_type(agent._result)

        # TODO: handle failed to extract case
        return result[0][1]

    def recommendations(self, data, ddl):
        return asyncio.run(self._recommendations(data, ddl))
