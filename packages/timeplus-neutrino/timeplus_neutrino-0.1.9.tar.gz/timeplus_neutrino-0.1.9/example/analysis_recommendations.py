from neutrino.onboard.agent import DataOnboardingAgent
from neutrino.utils.tools import extract_code_blocks_with_type

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

ddl = """CREATE STREAM customer
(
  `customer_id` int COMMENT 'unique customer id',
  `name` string COMMENT 'customer name',
  `email` string COMMENT 'customer email address',
  `phone` string COMMENT 'customer phone number',
  `address` string COMMENT 'customer physical address',
  `ip` ipv4 COMMENT 'customer IPv4 address',
  `time` datetime COMMENT 'record creation time',
  `event_time` datetime COMMENT 'event occurrence time',
  `uid` ipv6 COMMENT 'customer IPv6 address',
  `uid2` uuid COMMENT 'unique identifier for the customer event'
)
TTL to_datetime(event_time) + INTERVAL 1 DAY
SETTINGS mode = 'append', 
    logstore_retention_bytes = '-1', 
    logstore_retention_ms = '86400000', 
    index_granularity = 8192
COMMENT 'customer information'
"""


agent = DataOnboardingAgent()

recommendation_result = agent.recommendations(data, ddl)
print(f"recommendations : {recommendation_result}")
