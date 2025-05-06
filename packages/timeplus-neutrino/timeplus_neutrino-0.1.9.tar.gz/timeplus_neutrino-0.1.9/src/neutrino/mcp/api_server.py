import traceback
from fastapi import FastAPI
from fastapi import HTTPException, status
from typing import Optional, Dict, Any


from .mcp_server import (
    list_tables,
    list_databases,
    run_sql,
    list_kafka_topics,
    explore_kafka_topic,
    infer_stream,
    infer_kafka_external_stream,
    generate_debezium_cdc_pipeline_resources_ddl_from_source_stream,
    generate_debezium_cdc_pipeline_from_sample_data_and_topic,
    get_s3_settings,
)

app = FastAPI()


# Expose as a GET endpoint
@app.get("/tables", operation_id="list_tables")
async def get_tables(database: str = "default", like: Optional[str] = None):
    """
    List all tables in the given database, filtered by the given like pattern if provided.

    Args:
        database: The name of the database to list tables from (default: "default")
        like: An optional filter pattern to match table names

    Returns:
        A list of table information, including database, name, comment, and create table query
    """
    return list_tables(database, like)


@app.get("/databases", operation_id="list_databases")
async def get_databases():
    """
    List all available databases

    Returns:
        A list of database names
    """

    return list_databases()


@app.post("/run_sql", operation_id="run_sql")
async def execute_query(query: str):
    """
    Execute the given SQL query.

    Args:
        query: The SQL query to execute

    Returns:
        A list of row dictionaries, or an error message if the query failed
    """
    return run_sql(query)


@app.get("/kafka_topics", operation_id="list_kafka_topics")
async def get_kafka_topics():
    """
    List all available kafka topics

    Returns:
        A list of kafka topic names
    """
    return list_kafka_topics()


@app.post("/kafka_topic_explore", operation_id="explore_kafka_topic")
async def explore_kafka(topic: str, message_count: int = 1):
    """
    Explore Kafka topic by consuming messages.

    Args:
        topic (str): The name of the topic to explore.
        message_count (int, optional): The number of messages to consume.
            Defaults to 1.

    Returns:
        list: A list of JSON objects representing the consumed messages.
    """
    return explore_kafka_topic(topic, message_count)


@app.post("/infer_stream_schema", operation_id="infer_stream_schema")
async def infer_stream_schema(
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
    return await infer_stream(sample_data, stream_name, stream_description, settings)


@app.post(
    "/infer_kafka_external_stream_schema",
    operation_id="infer_kafka_external_stream_schema",
)
async def infer_kafka_external_stream_schema(
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
    return await infer_kafka_external_stream(
        sample_data, stream_name, stream_description, broker, topic, raw_format
    )


@app.post(
    "/generate_debezium_cdc_pipeline_resources_ddl_from_source_stream",
    operation_id="generate_debezium_cdc_pipeline_resources_ddl_from_source_stream",
)
async def generate_debezium_cdc_pipeline_resources_ddl_from_source_stream_op(
    sample_data: dict,
    source_stream_name: str,
    target_stream_name: str,
):
    """
    Generate the DDL for the debezium cdc pipeline resources based on sample data.

    Args:
        sample_data (dict): A dictionary representing a sample of the Debezium CDC data payload.
        source_stream_name (str): The name of the source stream associated with the data.
        target_stream_name (str): The name of the target stream for which to generate the DDL.

    Returns:
        dict: A dictionary containing:
            - "target_stream": The inferred target stream DDL as a string.
            - "extraction_mv": The extraction materialized view DDL as a string.
    """
    return await generate_debezium_cdc_pipeline_resources_ddl_from_source_stream(
        sample_data, source_stream_name, target_stream_name
    )


@app.post(
    "/generate_debezium_cdc_pipeline_from_sample_data_and_topic",
    operation_id="generate_debezium_cdc_pipeline_from_sample_data_and_topic",
    response_model=Dict[str, Any],
)
async def generate_debezium_cdc_pipeline_from_sample_data_and_topic_op(
    sample_data: dict,
    topic: str,
    broker: str,
    settings: dict,
):
    """
    Generate the DDL for the debezium cdc pipeline resources based on sample data from a kafka topic.

    Args:
        sample_data (dict): A dictionary representing the sample data to infer the DDL from.
        broker (str): The kafka broker URL.
        topic (str): The kafka topic.
        settings (dict): Additional settings or configurations for the inference process.
        - "type": The type of the stream (e.g., "append only stream", "mutable stream", "mysql external table", "s3 exteral table", "kafka external stream").

    Returns:
        dict: A dictionary containing:
        - "source_stream": The external source stream DDL as a string.
        - "target_stream": The inferred target stream DDL as a string.
        - "extraction_mv": The inferred extraction materialized view DDL as a string.
    """
    try:
        # Input validation
        if not sample_data:
            raise ValueError("Sample data cannot be empty")

        if not topic:
            raise ValueError("Topic cannot be empty")

        if not broker:
            raise ValueError("Broker cannot be empty")

        if not settings or not isinstance(settings, dict):
            raise ValueError("Settings must be provided as a dictionary")

        # Check if the required 'type' setting is present
        if "type" not in settings:
            raise ValueError("Settings must include a 'type' field")

        # Call the function to generate the pipeline
        result = await generate_debezium_cdc_pipeline_from_sample_data_and_topic(
            sample_data, topic, broker, settings
        )

        return result

    except Exception as e:
        # Log the full exception for debugging
        trace = traceback.format_exc()
        print(f"Error generating Debezium CDC pipeline: {trace}")

        # Return a proper error response
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate pipeline: {str(e)}",
            headers={"X-Error": "Internal processing error"},
        )


@app.get("/s3_settings", operation_id="get_s3_settings")
async def get_s3_settings_op():
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
    return get_s3_settings()
