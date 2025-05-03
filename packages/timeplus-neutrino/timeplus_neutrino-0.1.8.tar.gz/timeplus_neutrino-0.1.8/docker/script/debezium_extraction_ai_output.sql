
-- postgres customer table

CREATE STREAM customers
(
  `customer_id` uint32,
  `name` string,
  `email` string,
  `phone` string,
  `address` string
);

CREATE MATERIALIZED VIEW IF NOT EXISTS customers_view
INTO customers AS
SELECT
    json_extract_uint(raw:after, 'customer_id') AS customer_id,
    json_extract_string(raw:after, 'name') AS name,
    json_extract_string(raw:after, 'email') AS email,
    json_extract_string(raw:after, 'phone') AS phone,
    json_extract_string(raw:after, 'address') AS address
FROM kafka_cdc_postgres_customers
WHERE _tp_time > earliest_ts();

-- postgres credit history table

CREATE STREAM credit_history
(
  `history_id` uint32,
  `customer_id` uint32,
  `bank_name` string,
  `credit_score` uint32,
  `outstanding_debt` float64,
  `last_updated` uint32
);

CREATE MATERIALIZED VIEW IF NOT EXISTS credit_history_view
INTO credit_history AS
SELECT
    json_extract_uint(raw:after, 'history_id') AS history_id,
    json_extract_uint(raw:after, 'customer_id') AS customer_id,
    json_extract_string(raw:after, 'bank_name') AS bank_name,
    json_extract_uint(raw:after, 'credit_score') AS credit_score,
    json_extract_float(raw:after, 'outstanding_debt') AS outstanding_debt,
    json_extract_uint(raw:after, 'last_updated') AS last_updated
FROM kafka_cdc_postgres_credit_history
WHERE _tp_time > earliest_ts();


-- mongo unstructure data

CREATE STREAM customer_unstructure
(
  `_id` tuple(`$oid` string),
  `customer_id` uint32,
  `raw_data` tuple(
    `transaction_history` array(
      tuple(
        `date` tuple(`$date` int64),
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
);

-- following extract is wrong with transaction_history.date, which need prompt to fix
create materialized view if not exists extracted_customer_unstructure_view
into customer_unstructure as
select
    tuple_cast(
        json_extract_string(raw:payload:after:_id, '$oid')
    ) as _id,
    json_extract_uint(raw:payload:after, 'customer_id') as customer_id,
    tuple_cast(
        array_map(
            x -> (
                tuple_cast(
                    json_extract_int(x:date, '$date') as date,
                    json_extract_float(x, 'amount') as amount
                )
            ),
            json_extract_array(raw:payload:after:raw_data, 'transaction_history')
        ) as transaction_history,
        tuple_cast(
            json_extract_string(raw:payload:after:raw_data:social_media_activity, 'platform') as platform,
            json_extract_uint(raw:payload:after:raw_data:social_media_activity, 'activity_score') as activity_score
        ) as social_media_activity,
        tuple_cast(
            json_extract_string(raw:payload:after:raw_data:miscellaneous, 'notes') as notes,
            json_extract_string(raw:payload:after:raw_data:miscellaneous, 'risk_flags') as risk_flags
        ) as miscellaneous
    ) as raw_data
from kafka_cdc_mongo_unstructure
where _tp_time > earliest_ts();


-- this is fixed extraction
create materialized view if not exists extracted_customer_unstructure_view
into customer_unstructure as
select
    tuple_cast(
        json_extract_string(raw:payload:after:_id, '$oid')
    ) as _id,
    json_extract_uint(raw:payload:after, 'customer_id') as customer_id,
    tuple_cast(
        array_map(
            x -> (
                tuple_cast(
                    tuple_cast(json_extract_int(x:date, '$date') as date) as date,
                    json_extract_float(x, 'amount') as amount
                )
            ),
            json_extract_array(raw:payload:after:raw_data, 'transaction_history')
        ) as transaction_history,
        tuple_cast(
            json_extract_string(raw:payload:after:raw_data:social_media_activity, 'platform') as platform,
            json_extract_uint(raw:payload:after:raw_data:social_media_activity, 'activity_score') as activity_score
        ) as social_media_activity,
        tuple_cast(
            json_extract_string(raw:payload:after:raw_data:miscellaneous, 'notes') as notes,
            json_extract_string(raw:payload:after:raw_data:miscellaneous, 'risk_flags') as risk_flags
        ) as miscellaneous
    ) as raw_data
from kafka_cdc_mongo_unstructure
where _tp_time > earliest_ts();





