from neutrino.onboard.agent import DataOnboardingAgent

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

ddl = """
CREATE STREAM customer
(
  `_id` tuple(`$oid` string),
  `customer_id` int,
  `raw_data` tuple(
    `transaction_history` array(
      tuple(
        `date` tuple(`$date` int64),
        `amount` float64
      )
    ),
    `social_media_activity` tuple(
      `platform` string,
      `activity_score` int
    ),
    `miscellaneous` tuple(
      `notes` string,
      `risk_flags` string
    )
  )
)
TTL to_datetime(_tp_time) + INTERVAL 1 DAY
SETTINGS mode = 'append',
    logstore_retention_bytes = '-1',
    logstore_retention_ms = '86400000',
    index_granularity = 8192
COMMENT ''"""


agent = DataOnboardingAgent()

summary_result = agent.summary(data, ddl)

print(f"schema with comments : {summary_result}")
