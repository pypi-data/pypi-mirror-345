"""this module us obsolete"""

import os
from autogen import ConversableAgent


class DataOnboardingAgent:
    data_onboarding_system_message = "you are a helpful data processing agent"

    schema_inference_system_message = """please generate DDL based on input data which is a json object or list of json object seperated by comma
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


    here is a sample of output DDL:
    ```sql
    CREATE STREAM car_live_data
    (
      `cid` string,
      `gas_percent` float64,
      `in_use` bool
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

    schema_to_table_system_message = """based on generated DDL, please convert it into a json objec
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

    field_summary_system_message = """ please generate a report to explain each fields of the schema,
    turn the hierachy into flatten when generating this report for each field,
    use '.' to connect the parents and children names
    output the result into a json object
    here is a sample of the output:
    [
        {
            "name": "eventversion",
            "type": "uint32",
            "description": "The version of the current event."
        },
        {
            "name": "open_24h",
            "type": "string",
            "description": "The price of the asset at the beginning of the last 24-hour period."
        }
    ]
    """

    analysis_recommendations_system_message = """ please propose what kind an analysis we can do based on input data and schema
    output into a json object which is an array
    """

    analysis_sql_generation_system_message = """ please generate 10 analysis SQL based on input schema and analysis recommendations
    output into a json object which is an array
    note, you need escape newlines if the output contains multiple lines string

    The generate SQL should follow these rules
    * the SQL follows the ClickHouse grammar
    * all method name MUST be in lower cases, following snake cases, for example : array_sum
    * no CROSS JOIN is supported

    As timeplus is a streaming processing platform, there are three different types of query regarding how to scan the data
    please randomly select one of these three patterns to generate SQL

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
    ]

    """

    def __init__(self):
        self._llm_config = {
            "config_list": [
                {"model": "gpt-4o-mini", "api_key": os.environ["OPENAI_API_KEY"]}
            ],
            "temperature": 0,
        }

        """
        self._llm_config = {
            "config_list": [
                {
                    "model": "gemma2:9b",
                    "base_url": "http://localhost:11434/v1",
                    "api_key": "ollama",
                }
            ]}
        """

        self.data_onboarding_agent = ConversableAgent(
            "data_onboarding_agent",
            system_message=self.data_onboarding_system_message,
            llm_config=self._llm_config,
            code_execution_config=False,
            max_consecutive_auto_reply=1,
            human_input_mode="NEVER",
        )

        self.schema_inference_agent = ConversableAgent(
            "schema_inference_agent",
            system_message=self.schema_inference_system_message,
            llm_config=self._llm_config,
            code_execution_config=False,
            max_consecutive_auto_reply=1,
            human_input_mode="NEVER",
        )

        self.schema_to_table_agent = ConversableAgent(
            "schema_to_table_agent",
            system_message=self.schema_to_table_system_message,
            llm_config=self._llm_config,
            code_execution_config=False,
            max_consecutive_auto_reply=1,
            human_input_mode="NEVER",
        )

        self.field_summary_agent = ConversableAgent(
            "field_summary_agent",
            system_message=self.field_summary_system_message,
            llm_config=self._llm_config,
            code_execution_config=False,
            max_consecutive_auto_reply=1,
            human_input_mode="NEVER",
        )

        self.analysis_recommendations_agent = ConversableAgent(
            "analysis_recommendations_agent",
            system_message=self.analysis_recommendations_system_message,
            llm_config=self._llm_config,
            code_execution_config=False,
            max_consecutive_auto_reply=1,
            human_input_mode="NEVER",
        )

        self.analysis_sql_generation_agent = ConversableAgent(
            "analysis_sql_generation_agent",
            system_message=self.analysis_sql_generation_system_message,
            llm_config=self._llm_config,
            code_execution_config=False,
            max_consecutive_auto_reply=1,
            human_input_mode="NEVER",
        )

    def process(self):
        message = (
            f"based on input data : {self.data}, and stream name : {self.stream_name}"
        )
        self.data_onboarding_agent.initiate_chats(
            [
                {
                    "recipient": self.schema_inference_agent,
                    "message": message,
                    "max_turns": 1,
                    "summary_method": "last_msg",
                },
                {
                    "recipient": self.field_summary_agent,
                    "message": "based on input DDL, add field summary",
                    "max_turns": 1,
                    "summary_method": "last_msg",
                },
                {
                    "recipient": self.analysis_recommendations_agent,
                    "message": f"based on input data : {self.data}, and field summary",
                    "max_turns": 1,
                    "summary_method": "last_msg",
                },
                {
                    "recipient": self.analysis_sql_generation_agent,
                    "message": "based on input schema and recommandations, generate analysis SQL, those metric seems like some video network package quality related data.",
                    "max_turns": 1,
                    "summary_method": "last_msg",
                },
            ]
        )

    def inference(self, data, stream_name):
        message = f"based on input data : {data}, and stream name : {stream_name}"
        self.data_onboarding_agent.initiate_chats(
            [
                {
                    "recipient": self.schema_inference_agent,
                    "message": message,
                    "max_turns": 1,
                    "summary_method": "last_msg",
                },
                {
                    "recipient": self.schema_to_table_agent,
                    "message": "please generate json expression for the schema",
                    "max_turns": 1,
                    "summary_method": "last_msg",
                },
            ]
        )

        return (
            self.schema_inference_agent.last_message()["content"],
            self.schema_to_table_agent.last_message()["content"],
        )

    def summary(self, data, columns):
        message = f"based on input data : {data}, and columns : {columns}"
        self.data_onboarding_agent.initiate_chats(
            [
                {
                    "recipient": self.field_summary_agent,
                    "message": message,
                    "max_turns": 1,
                    "summary_method": "last_msg",
                }
            ]
        )

        return self.field_summary_agent.last_message()["content"]

    def recommendations(self, data, columns, stream_name):
        message = f"based on input data : {data}, and columns : {columns} and stream name : {stream_name}"
        self.data_onboarding_agent.initiate_chats(
            [
                {
                    "recipient": self.analysis_sql_generation_agent,
                    "message": message,
                    "max_turns": 1,
                    "summary_method": "last_msg",
                }
            ]
        )

        return self.analysis_sql_generation_agent.last_message()["content"]
