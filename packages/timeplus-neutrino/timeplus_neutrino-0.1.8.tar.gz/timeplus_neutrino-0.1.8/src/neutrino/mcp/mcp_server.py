import logging
import concurrent.futures
import atexit
import json
import os
import time
import re
from typing import Sequence
from confluent_kafka.admin import AdminClient
from confluent_kafka import Consumer

import timeplus_connect
from timeplus_connect.driver.binding import quote_identifier, format_query_value
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from .mcp_env import config
from .prompt_template import TEMPLATE

from neutrino.onboard.agent import DataOnboardingAgent
from neutrino.pipeline.agent import DataExtractionAgent

MCP_SERVER_NAME = "mcp-timeplus"


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(MCP_SERVER_NAME)

QUERY_EXECUTOR = concurrent.futures.ThreadPoolExecutor(max_workers=10)
atexit.register(lambda: QUERY_EXECUTOR.shutdown(wait=True))
SELECT_QUERY_TIMEOUT_SECS = 30


load_dotenv()
load_dotenv(dotenv_path="/timeplus/.env")
logger.info(f"Loading environment variables Timeplus Host {os.getenv('TIMEPLUS_HOST')}")

deps = [
    "timeplus-connect",
    "python-dotenv",
    "uvicorn",
    "confluent-kafka",
    "pip-system-certs",
]

mcp = FastMCP(MCP_SERVER_NAME, dependencies=deps)


@mcp.tool()
def list_databases():

    """List all available databases

    Returns:
        List of database names
    """

    logger.info("Listing all databases")
    client = create_timeplus_client()
    result = client.command("SHOW DATABASES")
    logger.info(f"Found {len(result) if isinstance(result, list) else 1} databases")
    return result


@mcp.tool()
def list_tables(database: str = "default", like: str = None):
    """List available tables/streams in the given database

    Args:
        database: Database name to list tables from (default: "default")
        like: Optional filter pattern to match table names

    Returns:
        List of table information including database, name, comment, and create table query
    """
    logger.info(f"Listing tables in database '{database}'")
    client = create_timeplus_client()

    # Fetch table names
    tables = _fetch_table_names(client, database, like)

    # Fetch table and column comments in batch
    table_comments = _fetch_table_comments(client, database)
    column_comments = _fetch_column_comments(client, database)

    # Process each table
    table_info_list = []
    for table in tables:
        table_info = _get_table_info(
            client, database, table, table_comments, column_comments
        )
        table_info_list.append(table_info)

    logger.info(f"Found {len(table_info_list)} tables")
    return table_info_list


def _fetch_table_names(client, database: str, like: str = None) -> list:
    """Fetch list of table names from the database"""
    query = f"SHOW STREAMS FROM {quote_identifier(database)}"
    if like:
        query += f" LIKE {format_query_value(like)}"

    result = client.command(query)

    # Handle different return types from command
    tables = []
    if isinstance(result, str):
        # Single table result as string
        tables = [t.strip() for t in result.split() if t.strip()]
    elif isinstance(result, Sequence):
        # Multiple table results as sequence
        tables = result

    return tables


def _fetch_table_comments(client, database: str) -> dict:
    """Fetch all table comments in one query"""
    query = f"SELECT name, comment FROM system.tables WHERE database = {format_query_value(database)}"
    result = client.query(query)
    return {row[0]: row[1] for row in result.result_rows}


def _fetch_column_comments(client, database: str) -> dict:
    """Fetch all column comments in one query"""
    query = f"SELECT table, name, comment FROM system.columns WHERE database = {format_query_value(database)}"
    result = client.query(query)

    column_comments = {}
    for row in result.result_rows:
        table, col_name, comment = row
        if table not in column_comments:
            column_comments[table] = {}
        column_comments[table][col_name] = comment

    return column_comments


def _get_table_info(
    client, database: str, table: str, table_comments: dict, column_comments: dict
) -> dict:
    """Get detailed information for a specific table"""
    logger.info(f"Getting schema info for table {database}.{table}")

    # Get create table query
    create_table_query = (
        f"SHOW CREATE STREAM {quote_identifier(database)}.{quote_identifier(table)}"
    )
    create_table_result = client.command(create_table_query)

    # Build table info dictionary
    table_info = {
        "database": database,
        "name": table,
        "comment": table_comments.get(table),
        "create_table_query": create_table_result,
    }

    # Optionally fetch column details if needed
    # table_info["columns"] = _get_column_details(client, database, table, column_comments)

    return table_info


def _get_column_details(
    client, database: str, table: str, column_comments: dict
) -> list:
    """Get detailed information about table columns"""
    schema_query = (
        f"DESCRIBE STREAM {quote_identifier(database)}.{quote_identifier(table)}"
    )
    schema_result = client.query(schema_query)

    columns = []
    column_names = schema_result.column_names

    for row in schema_result.result_rows:
        column_dict = {column_names[i]: row[i] for i in range(len(column_names))}

        # Add comment from pre-fetched comments
        if table in column_comments and column_dict["name"] in column_comments[table]:
            column_dict["comment"] = column_comments[table][column_dict["name"]]
        else:
            column_dict["comment"] = None

        columns.append(column_dict)

    return columns


def execute_query(query: str):
    client = create_timeplus_client()
    try:
        readonly = 1 if config.readonly else 0
        res = client.query(query, settings={"readonly": readonly})
        column_names = res.column_names
        rows = []
        for row in res.result_rows:
            row_dict = {}
            for i, col_name in enumerate(column_names):
                row_dict[col_name] = row[i]
            rows.append(row_dict)
        logger.info(f"Query returned {len(rows)} rows")
        return rows
    except Exception as err:
        logger.error(f"Error executing query: {err}")
        # Return a structured dictionary rather than a string to ensure proper serialization
        # by the MCP protocol. String responses for errors can cause BrokenResourceError.
        return {"error": str(err)}


@mcp.tool()
def run_sql(query: str):
    """
    Execute a SQL query in a separate thread.

    Args:
        query (str): SQL query to execute

    Returns:
        List of dictionaries containing query results.
        If the query fails, returns a dictionary with "status" and "message" keys:
        - "status": "error"
        - "message": error message
    """
    logger.info(f"Executing query: {query}")
    try:
        future = QUERY_EXECUTOR.submit(execute_query, query)
        try:
            result = future.result(timeout=SELECT_QUERY_TIMEOUT_SECS)
            # Check if we received an error structure from execute_query
            if isinstance(result, dict) and "error" in result:
                logger.warning(f"Query failed: {result['error']}")
                # MCP requires structured responses; string error messages can cause
                # serialization issues leading to BrokenResourceError
                return {
                    "status": "error",
                    "message": f"Query failed: {result['error']}",
                }
            return result
        except concurrent.futures.TimeoutError:
            logger.warning(
                f"Query timed out after {SELECT_QUERY_TIMEOUT_SECS} seconds: {query}"
            )
            future.cancel()
            # Return a properly structured response for timeout errors
            return {
                "status": "error",
                "message": f"Query timed out after {SELECT_QUERY_TIMEOUT_SECS} seconds",
            }
    except Exception as e:
        logger.error(f"Unexpected error in run_select_query: {str(e)}")
        # Catch all other exceptions and return them in a structured format
        # to prevent MCP serialization failures
        return {"status": "error", "message": f"Unexpected error: {str(e)}"}


@mcp.prompt()
def generate_sql(requirements: str) -> str:
    """
    Generate a Timeplus SQL query based on natural language requirements.

    This function takes in natural language requirements and returns a prompt
    for the user to generate a Timeplus SQL query that satisfies the requirement.

    Args:
        requirements: The natural language requirement to generate a query for.

    Returns:
        str: A prompt for the user to generate a Timeplus SQL query.
    """
    return f"Please generate Timeplus SQL for the requirement:\n\n{requirements}\n\nMake sure following the guide {TEMPLATE}"


@mcp.tool()
def list_kafka_topics():
    """
    List all topics in the Kafka cluster.

    This function connects to the Kafka cluster using the configuration
    specified in the TIMEPLUS_KAFKA_CONFIG environment variable, retrieves
    all available topics, and returns a list of dictionaries containing
    each topic's name and the number of partitions.

    Returns:
        list: A list of dictionaries, each containing:
            - 'topic' (str): The name of the Kafka topic.
            - 'partitions' (int): The number of partitions for the topic.
    """

    logger.info("Listing all topics in the Kafka cluster")
    admin_client = AdminClient(json.loads(os.environ["TIMEPLUS_KAFKA_CONFIG"]))
    topics = admin_client.list_topics(timeout=10).topics
    topics_array = []
    for topic, detail in topics.items():
        topic_info = {"topic": topic, "partitions": len(detail.partitions)}
        topics_array.append(topic_info)
    return topics_array


# add offset and timeout settings
@mcp.tool()
def explore_kafka_topic(topic: str, message_count: int = 1):
    """
    Explore Kafka topic by consuming messages.

    Args:
        topic (str): The name of the topic to explore.
        message_count (int, optional): The number of messages to consume.
            Defaults to 1.

    Returns:
        list: A list of JSON objects representing the consumed messages.
    """
    logger.info(f"Consuming topic {topic}")
    conf = json.loads(os.environ["TIMEPLUS_KAFKA_CONFIG"])
    conf["group.id"] = f"mcp-{time.time()}"
    client = Consumer(conf)
    client.subscribe([topic])
    messages = []
    for i in range(message_count):
        logger.info(f"Consuming message {i + 1}")
        message = client.poll()
        if message is None:
            logger.info("No message received")
            continue
        if message.error():
            logger.error(f"Error consuming message: {message.error()}")
            continue
        else:
            logger.info(f"Received message {i + 1}")
            messages.append(json.loads(message.value()))
    client.close()
    return messages


@mcp.tool()
async def infer_stream(
    sample_data: dict, stream_name: str, stream_description: str, settings: dict
):
    """
    Infer a Timeplus DDL for a given data stream based on sample data.

    Args:
        sample_data (dict): A dictionary representing the sample data to infer the DDL from.
        stream_name (str): The name of the stream for which to generate the DDL.
        stream_description (str): A description of the stream for context in the inference process.
        settings (dict): Additional settings or configurations for the inference process.

    Returns:
        str: The inferred DDL as a string.
    """

    logger.info(
        f"infering stream DDL for sample data {sample_data} with settings {settings}"
    )
    agent = DataOnboardingAgent()
    inference_ddl, inference_json = await agent.async_inference(
        json.dumps(sample_data), stream_name, stream_description
    )
    logger.info(f"schema sql : {inference_ddl}")
    logger.info(f" schema json : {inference_json}")

    return inference_ddl


@mcp.tool()
async def infer_kafka_external_stream(
    sample_data: dict,
    stream_name: str,
    stream_description: str,
    broker: str,
    topic: str,
    raw_format: bool = False,
):
    """
    Infer a Timeplus DDL for a given external kafka stream based on sample data.
    The DDL can be used to create an external stream in Timeplus.

    Args:
        sample_data (dict): A dictionary representing the sample data to infer the DDL from.
        stream_name (str): The name of the stream for which to generate the DDL.
        stream_description (str): A description of the stream for context in the inference process.
        broker (str): The kafka broker URL.
        topic (str): The kafka topic.
        raw_format (bool, optional): Whether to generate a raw format DDL (i.e. single column `raw` of type string). Defaults to False.

    Returns:
        str: The inferred DDL as a string.
    """
    if not raw_format:
        logger.info(
            f"infering kafka external stream DDL for sample data {sample_data} with topic {topic}"
        )
        agent = DataOnboardingAgent()
        settings = {"type": "kafka", "brokers": broker, "topic": topic}
        inference_ddl, inference_json = await agent.async_inference_external_stream(
            json.dumps(sample_data), stream_name, settings, stream_description
        )
        logger.info(f"schema sql : {inference_ddl}")
        logger.info(f" schema json : {inference_json}")
        return inference_ddl
    else:
        logger.info(
            f"infering kafka external stream DDL for sample data {sample_data} with topic {topic} with raw format"
        )
        inference_ddl = f"""CREATE EXTERNAL STREAM {stream_name}
(
  `raw` string
)
SETTINGS type = 'kafka',
brokers = '{broker}',
topic = '{topic}'
COMMENT '{stream_description}'"""
        return inference_ddl


@mcp.tool()
async def generate_debezium_cdc_pipeline_resources_ddl_from_source_stream(
    sample_data: dict,
    source_stream_name: str,
    target_stream_name: str,
):
    """
    Generate pipeline resources DDLs from a sample Debezium CDC data based on source external stream.

    This function creates the necessary DDLs for setting up a pipeline to process
    Debezium CDC data. It generates a target stream DDL and an extraction materialized view DDL.

    Args:
        sample_data (dict): A dictionary representing a sample of the Debezium CDC data payload.
        source_stream_name (str): The name of the source stream associated with the data.
        target_stream_name (str): The name of the target stream for which to generate the DDL.

    Returns:
        dict: A dictionary containing:
            - "target_stream": The inferred target stream DDL as a string.
            - "extraction_mv": The extraction materialized view DDL as a string.
    """
    agent = DataExtractionAgent()
    agent1_output, agent2_output = await agent.async_pipeline(
        sample_data, source_stream_name, target_stream_name
    )

    logger.info(f" target stream : {agent1_output}")
    logger.info(f" mv extraction  : {agent2_output}")
    return {"target_stream": agent1_output, "extraction_mv": agent2_output}


@mcp.tool()
async def generate_debezium_cdc_pipeline_from_sample_data_and_topic(
    sample_data: dict,
    topic: str,
    broker: str,
    settings: dict,
):
    """
    Generate pipeline resources DDLs from a sample Debezium CDC data and kafka topic.

    This function creates the necessary DDLs for setting up a pipeline to process
    Debezium CDC data. It generates an external source stream DDL, a target stream
    DDL, and an extraction materialized view DDL.

    Args:
        sample_data (dict): A dictionary representing a sample of the Debezium CDC data payload.
        topic (str): The Kafka topic name associated with the data.
        broker (str): The Kafka broker URL.
        settings (dict): Additional settings or configurations for the inference process.
        - "type": The type of the stream (e.g., "append only stream", "mutable stream", "mysql external table", "s3 exteral table", "kafka external stream").


    Returns:
        dict: A dictionary containing:
            - "source_stream": The external source stream DDL as a string.
            - "target_stream": The inferred target stream DDL as a string.
            - "extraction_mv": The inferred extraction materialized view DDL as a string.
    """

    source_stream_name = f"{sanitize_table_name(topic)}_source_stream"
    target_stream_name = f"{sanitize_table_name(topic)}_target_stream"
    source_external_stream_ddl = f"""CREATE EXTERNAL STREAM {source_stream_name}
(
  `raw` string
)
SETTINGS type = 'kafka',
brokers = '{broker}',
topic = '{topic}'
"""
    agent = DataExtractionAgent()
    agent1_output, agent2_output = await agent.async_generic_pipeline(
        sample_data, source_stream_name, target_stream_name, settings
    )
    return {
        "source_stream": source_external_stream_ddl,
        "target_stream": agent1_output,
        "extraction_mv": agent2_output,
    }


@mcp.tool()
def get_s3_settings():
    """
    Retrieve S3 settings for data storage and access.

    Returns:
        dict: A dictionary containing S3 configuration settings including:
            - "type": The type of storage, set to 's3'.
            - "access_key_id": The access key ID for S3 authentication.
            - "secret_access_key": The secret access key for S3 authentication.
            - "region": The region where the S3 bucket is located.
            - "bucket": The name of the S3 bucket.
            - "data_format": The format of the data stored in S3.
            - "endpoint": The endpoint URL for accessing the S3 service.
            - "write_to": The path within the bucket where data is written.
            - "use_environment_credentials": A flag indicating whether to use environment credentials.
            - "s3_min_upload_file_size": The minimum file size for uploading to S3 in bytes.
    """

    # TODO: add support for environment variables or configuration file or Timeplus config streams
    return {
        "type": "s3",
        "access_key_id": "minioadmin",
        "secret_access_key": "minioadmin",
        "region": "us-east-1",
        "bucket": "timeplus",
        "data_format": "JSONEachRow",
        "endpoint": "http://minio:9000",
        "write_to": "data/data.json",
        "use_environment_credentials": False,
        "s3_min_upload_file_size": 1024 * 256,  # 256KB
    }


def create_timeplus_client():
    client_config = config.get_client_config()
    logger.info(
        f"Creating Timeplus client connection to {client_config['host']}:{client_config['port']} "
        f"as {client_config['username']} "
        f"(secure={client_config['secure']}, verify={client_config['verify']}, "
        f"connect_timeout={client_config['connect_timeout']}s, "
        f"send_receive_timeout={client_config['send_receive_timeout']}s)"
    )

    try:
        client = timeplus_connect.get_client(**client_config)
        # Test the connection
        version = client.server_version
        logger.info(f"Successfully connected to Timeplus server version {version}")
        return client
    except Exception as e:
        logger.error(f"Failed to connect to Timeplus: {str(e)}")
        raise


def sanitize_table_name(name: str) -> str:
    # Replace any character that is not a-z, A-Z, 0-9, or _ with _
    sanitized = re.sub(r"[^a-zA-Z0-9_]", "_", name)
    # Optionally, remove leading digits or underscores to match ClickHouse rules better
    sanitized = re.sub(r"^[^a-zA-Z]+", "", sanitized)
    return sanitized
