import os
import uvicorn
import time
import signal
import sys
import multiprocessing

from .api_server import app

# from .ui_client import app
from fastapi_mcp import FastApiMCP


def cleanup():
    print("Cleaning up...")
    # join threads or close resources if needed
    time.sleep(1)


def signal_handler(sig, frame):
    cleanup()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if sys.platform == "darwin":
    multiprocessing.set_start_method("fork", force=True)
else:
    multiprocessing.set_start_method("spawn", force=True)


mcp = FastApiMCP(
    app,
    include_operations=[
        "list_tables",
        "list_databases",
        "run_sql",
        "list_kafka_topics",
        "explore_kafka_topic",
        "infer_stream_schema",
        "infer_kafka_external_stream_schema",
        "generate_debezium_cdc_pipeline_resources_ddl_from_source_stream",
        "generate_debezium_cdc_pipeline_from_sample_data_and_topic",
        "get_s3_settings",
    ],
)
mcp.mount(app)

# Run the server
if __name__ == "__main__":
    import sys

    # Check if server script path is provided as an argument
    if len(sys.argv) > 1:
        os.environ["MCP_SERVER_SCRIPT"] = sys.argv[1]

    uvicorn.run(app, host="0.0.0.0", port=5001)
