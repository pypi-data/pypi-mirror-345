from neutrino.onboard.agent import DataOnboardingAgent
from neutrino.utils.tools import extract_code_blocks_with_type

data = """{
	"_id": {
		"$oid": "67bc078e18939cdcb051732a"
	},
	"customer_id": 49,
	"raw_data": {
		"transaction_history": [
			{
				"date": {
					"$date": 1738368000000
				},
				"amount": 391.05
			},
			{
				"date": {
					"$date": 1738540800000
				},
				"amount": 923.33
			},
			{
				"date": {
					"$date": 1738972800000
				},
				"amount": 541.95
			},
			{
				"date": {
					"$date": 1736208000000
				},
				"amount": 116.17
			},
			{
				"date": {
					"$date": 1736899200000
				},
				"amount": 399.86
			},
			{
				"date": {
					"$date": 1739577600000
				},
				"amount": 625.11
			},
			{
				"date": {
					"$date": 1738195200000
				},
				"amount": 668.96
			},
			{
				"date": {
					"$date": 1736294400000
				},
				"amount": 472.46
			},
			{
				"date": {
					"$date": 1737072000000
				},
				"amount": 17.49
			}
		],
		"social_media_activity": {
			"platform": "Twitter",
			"activity_score": 34
		},
		"miscellaneous": {
			"notes": "Policy wish success begin candidate raise state.",
			"risk_flags": "Medium"
		}
	}
}"""


agent = DataOnboardingAgent()

inference_ddl, inference_json = agent.inference(data, "customer")

print(f"schema sql : {inference_ddl}")
print(f"schema json : {inference_json}")


