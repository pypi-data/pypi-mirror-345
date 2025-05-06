from neutrino.onboard.agent import DataOnboardingAgent

data = """{
		"customer_id": 9,
		"name": "Johnathan Rodriguez",
		"email": "thomasramirez@example.org",
		"phone": "001-845-290-8721x77863",
		"address": "743 Cervantes Causeway Apt. 762\nPort Lauren, NY 12698",
		"ip": "127.0.0.1",
		"time": "2023-01-01 00:00:00",
		"event_time": "2023-01-01 00:00:00",
		"uid": "2a02:aa08:e000:3100::2",
		"uid2":"1f71acbf-59fc-427d-a634-1679b48029a9"
}"""

ddl = """
CREATE STREAM customer
(
  `customer_id` int,
  `name` string,
  `email` string,
  `phone` string,
  `address` string,
  `ip` ipv4,
  `time` datetime,
  `event_time` datetime,
  `uid` ipv6,
  `uid2` uuid
)
TTL to_datetime(event_time) + INTERVAL 1 DAY
SETTINGS mode = 'append', 
    logstore_retention_bytes = '-1', 
    logstore_retention_ms = '86400000', 
    index_granularity = 8192
COMMENT 'customer information'"""


agent = DataOnboardingAgent()

summary_result = agent.summary(data, ddl)

print(f"schema with comments : {summary_result}")
