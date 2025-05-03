CREATE OR REPLACE FUNCTION ask_kafka(question string) RETURNS string LANGUAGE PYTHON AS 
$$
import traceback
from neutrino.kafka.agent import KafkaExplorerAgent


def ask_kafka(question):
    results = []
    for (question) in zip(question):
        try:
            agent = KafkaExplorerAgent()
            result = agent.ask(question)
            clean_output = result.removesuffix(" TERMINATE")
            results.append(clean_output)
        except Exception as e:
            trace = traceback.format_exc()
            results.append(trace)

    return results

$$;