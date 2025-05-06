CREATE OR REPLACE FUNCTION debezium_payload_extraction(data string, source_stream string, target_stream string) RETURNS string LANGUAGE PYTHON AS 
$$
import traceback
import json
from neutrino.pipeline.agent import DataExtractionAgent


def debezium_payload_extraction(data, source_stream, target_stream):
    results = []
    for (data, source_stream, target_stream) in zip(data, source_stream, target_stream):
        try:
            agent = DataExtractionAgent()
            target_stream_ddl, extraction_mv_ddl = agent.pipeline(data, source_stream, target_stream)

            result = {
                "target_stream_ddl" : target_stream_ddl,
                "extraction_mv_ddl" : extraction_mv_ddl 
            }
            results.append(json.dumps(result))
        except Exception as e:
            trace = traceback.format_exc()
            results.append(trace)

    return results

$$;