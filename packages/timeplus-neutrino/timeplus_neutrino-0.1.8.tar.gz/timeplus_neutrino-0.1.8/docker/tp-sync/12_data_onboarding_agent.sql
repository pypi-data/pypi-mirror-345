CREATE OR REPLACE FUNCTION schema_inference(data string, name string, description string, type string, properties string) RETURNS string LANGUAGE PYTHON AS 
$$
import traceback
import json
from neutrino.onboard.agent import DataOnboardingAgent


def schema_inference(data, name, description, type, properties):
    results = []
    for (data, name, description, type, properties) in zip(data, name, description, type, properties):
        try:
            agent = DataOnboardingAgent()
            result = {}
            if type == "append_only":
                inference_ddl, inference_json = agent.inference(data, name, description)
                result["ddl"] = inference_ddl
                result["json"] = inference_json
            elif type == "mutable_stream":
                inference_ddl, inference_json = agent.inference_mutable_stream(data, name, description)
                result["ddl"] = inference_ddl
                result["json"] = inference_json
            elif type == "external":
                inference_ddl, inference_json = agent.inference_external_stream(data, name, properties, description)
                result["ddl"] = inference_ddl
                result["json"] = inference_json
            
            results.append(json.dumps(result))
            
        except Exception as e:
            trace = traceback.format_exc()
            results.append(trace)

    return results

$$;

CREATE OR REPLACE FUNCTION schema_inference_with_fields_comment(data string, name string, description string, type string, properties string) RETURNS string LANGUAGE PYTHON AS 
$$
import traceback
import json
from neutrino.onboard.agent import DataOnboardingAgent


def schema_inference_with_fields_comment(data, name, description, type, properties):
    results = []
    for (data, name, description, type, properties) in zip(data, name, description, type, properties):
        try:
            
            result = {}
            if type == "stream":
                agent_stream = DataOnboardingAgent()
                agent_mutable_stream = DataOnboardingAgent()
                stream_inference_ddl, stream_inference_json = agent_stream.inference(data, name, description)
               
                mutable_stream_inference_ddl, mutable_stream_inference_json = agent_mutable_stream.inference_mutable_stream(data, name, description)

                summary_agent = DataOnboardingAgent()
                summary_result = summary_agent.summary(data, stream_inference_ddl)

                mutable_summary_agent = DataOnboardingAgent()
                mutable_summary_result = mutable_summary_agent.summary(data, mutable_stream_inference_ddl)

                result["stream_ddl"] = summary_result
                result["mutable_stream_ddl"] = mutable_summary_result

            elif type == "externalstream":
                agent_stream = DataOnboardingAgent()
                inference_ddl, inference_json = agent_stream.inference_external_stream(data, name, properties, description)
                
                summary_agent = DataOnboardingAgent()
                summary_result = summary_agent.summary(data, inference_ddl)
                result["external_stream_ddl"] = summary_result
            
            results.append(json.dumps(result))
            
        except Exception as e:
            trace = traceback.format_exc()
            results.append(trace)

    return results

$$;


CREATE OR REPLACE FUNCTION field_summary(data string, ddl string) RETURNS string LANGUAGE PYTHON AS 
$$
import traceback
from neutrino.onboard.agent import DataOnboardingAgent


def field_summary(data, ddl):
    results = []
    for (data, ddl) in zip(data, ddl):
        try:
            agent = DataOnboardingAgent()
            summary_result = agent.summary(data, ddl)
            results.append(summary_result)
        except Exception as e:
            trace = traceback.format_exc()
            results.append(trace)

    return results

$$;

CREATE OR REPLACE FUNCTION analysis_recommendation(data string, ddl string) RETURNS string LANGUAGE PYTHON AS 
$$
import traceback
from neutrino.onboard.agent import DataOnboardingAgent


def analysis_recommendation(data, ddl):
    results = []
    for (data, ddl) in zip(data, ddl):
        try:
            agent = DataOnboardingAgent()
            recommendation_result = agent.recommendations(data, ddl)
            results.append(recommendation_result)
        except Exception as e:
            trace = traceback.format_exc()
            results.append(trace)

    return results

$$;