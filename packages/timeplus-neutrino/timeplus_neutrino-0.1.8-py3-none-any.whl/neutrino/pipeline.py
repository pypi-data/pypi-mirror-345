"""this module us obsolete"""
import os
from autogen import ConversableAgent


class DataExtractionAgent:

    data_extraction_system_message = "you are a helpful data processing agent, help to extract useful information to unstrcuture data"

    payload_extraction_system_message = """
    the input data is a debezium CDC data payload, our target is to extract the payload in after or payload:after into a new stream
    the source stream has just one string field with name raw

    here is are sample queries to extrac the after payload based on different types of debezium payload
    case1. when the after payload is in root layer
    select raw:after from source_stream_name where _tp_time > earliest_ts()
    case2. when the after payload is in field of payload
    select raw:payload:after from source_stream_name where _tp_time > earliest_ts()

    return which extract query should be used in markdown code with sql

    """

    target_schema_inference_system_message = """please generate DDL based on debezium payload
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

    here is a sample of output DDL:
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

    target_mutable_stream_schema_inference_system_message = """please generate DDL based on debezium payload
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

    mv_extraction_system_message = """please create a materialized view to extraction information from source stream into target stream
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

    In case the payload contains complex composition and hierarchy, you should provide the conversion layer by layer, do not miss any middle layer
    here is a sample that one of the target field is a array of tuple, using array_map function to help
    array_map(
        x -> (
            tuple_cast(
                json_extract_string(x, 'field_name_1') as field_name_1,
                json_extract_float(x, 'field_name_2') as field_name_2
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

    """

    def __init__(self):

        self._llm_config = {
            "config_list": [
                {"model": "gpt-4o", "api_key": os.environ["OPENAI_API_KEY"]}
            ],
            "temperature": 0,
        }

        self.data_extraction_agent = ConversableAgent(
            "data_extraction_agent",
            system_message=self.data_extraction_system_message,
            llm_config=self._llm_config,
            code_execution_config=False,
            max_consecutive_auto_reply=1,
            human_input_mode="NEVER",
        )

        self.payload_extraction_agent = ConversableAgent(
            "payload_extraction_agent",
            system_message=self.payload_extraction_system_message,
            llm_config=self._llm_config,
            code_execution_config=False,
            max_consecutive_auto_reply=1,
            human_input_mode="NEVER",
        )

        self.target_schema_inference_agent = ConversableAgent(
            "target_schema_inference_agent",
            system_message=self.target_schema_inference_system_message,
            llm_config=self._llm_config,
            code_execution_config=False,
            max_consecutive_auto_reply=1,
            human_input_mode="NEVER",
        )

        self.target_mutable_stream_schema_inference_agent = ConversableAgent(
            "target_mutable_stream_schema_inference_agent",
            system_message=self.target_mutable_stream_schema_inference_system_message,
            llm_config=self._llm_config,
            code_execution_config=False,
            max_consecutive_auto_reply=1,
            human_input_mode="NEVER",
        )

        self.mv_extraction_agent = ConversableAgent(
            "mv_extraction_agent",
            system_message=self.mv_extraction_system_message,
            llm_config=self._llm_config,
            code_execution_config=False,
            max_consecutive_auto_reply=1,
            human_input_mode="NEVER",
        )

    def pipeline(self, data, source_stream_name, target_stream_name):
        message = (
            f"based on input data : {data} and source stream name {source_stream_name}"
        )
        self.data_extraction_agent.initiate_chats(
            [
                {
                    "recipient": self.payload_extraction_agent,
                    "message": message,
                    "max_turns": 1,
                    "summary_method": "last_msg",
                },
                {
                    "recipient": self.target_schema_inference_agent,
                    "message": f"based on input data : {data} and target stream name {target_stream_name}",
                    "max_turns": 1,
                    "summary_method": "last_msg",
                },
                {
                    "recipient": self.mv_extraction_agent,
                    "message": "please create materialized view to extrat information from source stream to target stream",
                    "max_turns": 1,
                    "summary_method": "last_msg",
                },
            ]
        )

        return (
            self.payload_extraction_agent.last_message()["content"],
            self.target_schema_inference_agent.last_message()["content"],
            self.mv_extraction_agent.last_message()["content"],
        )

    def pipeline_with_mutable_stream(
        self, data, source_stream_name, target_stream_name, ids
    ):
        message = (
            f"based on input data : {data} and source stream name {source_stream_name}"
        )
        self.data_extraction_agent.initiate_chats(
            [
                {
                    "recipient": self.payload_extraction_agent,
                    "message": message,
                    "max_turns": 1,
                    "summary_method": "last_msg",
                },
                {
                    "recipient": self.target_mutable_stream_schema_inference_agent,
                    "message": f"based on input data : {data} and target stream name {target_stream_name}, , and id fields {','.join(ids)}",
                    "max_turns": 1,
                    "summary_method": "last_msg",
                },
                {
                    "recipient": self.mv_extraction_agent,
                    "message": "please create materialized view to extrat information from source stream to target stream",
                    "max_turns": 1,
                    "summary_method": "last_msg",
                },
            ]
        )

        return (
            self.payload_extraction_agent.last_message()["content"],
            self.target_mutable_stream_schema_inference_agent.last_message()["content"],
            self.mv_extraction_agent.last_message()["content"],
        )
