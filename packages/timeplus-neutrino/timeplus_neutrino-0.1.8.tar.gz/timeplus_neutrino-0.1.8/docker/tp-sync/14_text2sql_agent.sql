CREATE OR REPLACE FUNCTION text2sql(question string) RETURNS string LANGUAGE PYTHON AS 
$$
import traceback
from neutrino.timeplus.text2sql import Text2SQLAgent
from neutrino.utils.tools import extract_code_blocks_with_type


def text2sql(question):
    results = []
    for (question) in zip(question):
        try:
            agent = Text2SQLAgent()
            sql_result = agent.ask(question)
            code_sql_result = extract_code_blocks_with_type(sql_result)
            results.append(str(code_sql_result[0][1]))
        except Exception as e:
            trace = traceback.format_exc()
            results.append(trace)

    return results

$$;