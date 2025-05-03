
import json
from neutrino.onboard import DataOnboardingAgent
from neutrino.utils.tools import extract_code_blocks_with_type

data_file_path = './data/coinbase_preview_data.json'
with open(data_file_path, 'r') as file:
    data = json.load(file)
    
columns_file_path = './data/coinbase_column_data.json'
with open(columns_file_path, 'r') as file:
    column_data = json.load(file)
    
agent = DataOnboardingAgent()    
# inference_rsult = agent.inference(data, 'coinbase')
# print(f"inference result is : {inference_rsult}")

# summary_result = agent.summary(data, column_data)
# print(f"summary result is : {summary_result}")

sql_result = agent.recommendations(data, column_data, 'coinbase')
extracted_sql_result = extract_code_blocks_with_type(sql_result)
print(f"analysis result is : {extracted_sql_result[0][1]}")



