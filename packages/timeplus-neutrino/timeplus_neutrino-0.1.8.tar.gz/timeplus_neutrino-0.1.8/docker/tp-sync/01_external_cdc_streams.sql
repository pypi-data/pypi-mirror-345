-- all cdc stream with debezium payload should use raw format
-- there is no full type mapping supported for now 
CREATE EXTERNAL STREAM IF NOT EXISTS kafka_cdc_mongo_unstructure
(
  `raw` string
)
SETTINGS type = 'kafka', 
    brokers = 'redpanda:9092', 
    topic = 'mongodb.lumi_data.unstructured_data', 
    security_protocol = 'PLAINTEXT', 
    data_format = 'RawBLOB', 
    skip_ssl_cert_check = 'false', 
    one_message_per_row = 'true'
COMMENT '';

CREATE EXTERNAL STREAM IF NOT EXISTS kafka_cdc_postgres_credit_history
(
  `raw` string
)
SETTINGS type = 'kafka', 
    brokers = 'redpanda:9092', 
    topic = 'postgres.public.credit_history', 
    security_protocol = 'PLAINTEXT', 
    data_format = 'RawBLOB', 
    skip_ssl_cert_check = 'false', 
    one_message_per_row = 'true'
COMMENT '';

CREATE EXTERNAL STREAM IF NOT EXISTS kafka_cdc_postgres_customers
(
  `raw` string
)
SETTINGS type = 'kafka', 
    brokers = 'redpanda:9092', 
    topic = 'postgres.public.customers', 
    security_protocol = 'PLAINTEXT', 
    data_format = 'RawBLOB', 
    skip_ssl_cert_check = 'false', 
    one_message_per_row = 'true'
COMMENT ''