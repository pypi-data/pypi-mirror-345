# MongoDB CDC Extraction Pipeline

This pipeline extracts data from the Debezium CDC topic `mongodb.lumi_data.unstructured_data` and transforms it into a structured format for analysis in Timeplus.

## 1. Source Stream Definition

```sql
CREATE EXTERNAL STREAM mongodb_lumi_data_unstructured_data_source_stream
(
  `raw` string
)
SETTINGS type = 'kafka',
brokers = 'redpanda:9092',
topic = 'mongodb.lumi_data.unstructured_data'
```

## 2. Target Stream Definition

```sql
CREATE EXTERNAL TABLE mongodb_lumi_data_unstructured_data_target_s3_table
(
  `_id` tuple(`$oid` string),
  `customer_id` uint32,
  `raw_data` tuple(
    `transaction_history` array(
      tuple(
        `date` tuple(`$date` uint64),
        `amount` float64
      )
    ),
    `social_media_activity` tuple(
      `platform` string,
      `activity_score` uint32
    ),
    `miscellaneous` tuple(
      `notes` string,
      `risk_flags` string
    )
  )
)
SETTINGS
    type = 's3',
    access_key_id = 'minioadmin',
    secret_access_key = 'minioadmin',
    region = 'us-east-1',
    bucket = 'timeplus',
    data_format = 'JSONEachRow',
    endpoint = 'http://minio:9000',
    write_to = 'lumi/data.json',
    use_environment_credentials = false;

```

## 3. Extraction Materialized View

```sql
CREATE MATERIALIZED VIEW IF NOT EXISTS mongodb_lumi_data_unstructured_data_view
INTO mongodb_lumi_data_unstructured_data_target_s3_table AS
SELECT
    tuple_cast(
        json_extract_string(raw:payload:after:_id, '$oid')
    ) AS _id,
    json_extract_uint(raw:payload:after, 'customer_id') AS customer_id,
    tuple_cast(
        array_map(
            x -> (
                tuple_cast(
                    tuple_cast(
                        json_extract_uint(x:date, '$date')
                    ) AS date,
                    json_extract_float(x, 'amount') AS amount
                )
            ),
            json_extract_array(raw:payload:after:raw_data, 'transaction_history')
        ) AS transaction_history,
        tuple_cast(
            json_extract_string(raw:payload:after:raw_data:social_media_activity, 'platform') AS platform,
            json_extract_uint(raw:payload:after:raw_data:social_media_activity, 'activity_score') AS activity_score
        ) AS social_media_activity,
        tuple_cast(
            json_extract_string(raw:payload:after:raw_data:miscellaneous, 'notes') AS notes,
            json_extract_string(raw:payload:after:raw_data:miscellaneous, 'risk_flags') AS risk_flags
        ) AS miscellaneous
    ) AS raw_data
FROM mongodb_lumi_data_unstructured_data_source_stream
WHERE _tp_time > earliest_ts();
```