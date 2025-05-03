CREATE STREAM mongo_cdc
(
  `raw` string
)
ENGINE = ExternalStream
SETTINGS type = 'kafka', brokers = 'redpanda:29092', topic = 'mongodb.lumi_data.unstructured_data', skip_ssl_cert_check = true;

CREATE STREAM postgres_cdc_customers
(
  `raw` string
)
ENGINE = ExternalStream
SETTINGS type = 'kafka', brokers = 'redpanda:29092', topic = 'postgres.public.customers', skip_ssl_cert_check = true;

CREATE STREAM postgres_cdc_credit_history
(
  `raw` string
)
ENGINE = ExternalStream
SETTINGS type = 'kafka', brokers = 'redpanda:29092', topic = 'postgres.public.credit_history ', skip_ssl_cert_check = true;