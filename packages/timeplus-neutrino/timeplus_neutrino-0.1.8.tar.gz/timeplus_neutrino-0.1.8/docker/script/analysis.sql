SELECT
  _tp_time, raw:payload:after:customer_id as customer_id, raw:payload:after:raw_data as raw_data
FROM
  mongo_cdc
WHERE
  _tp_time > earliest_ts();

SELECT
  _tp_time, raw:after:customer_id as customer_id, raw:after:bank_name as bank_name, raw:after:credit_score as credit_score, raw:after:outstanding_debt as outstanding_debt
FROM
  postgres_cdc_credit_history
WHERE
  _tp_time > earliest_ts();

SELECT
  _tp_time, raw:after:customer_id as customer_id,raw:after:name as name,raw:after:email as email,raw:after:phone as phone, raw:after:address as address 
FROM
  postgres_cdc_customers
WHERE
  _tp_time > earliest_ts();


WITH credit_history AS
  (
    SELECT
      _tp_time, raw:after:customer_id AS customer_id, raw:after:bank_name AS bank_name, raw:after:credit_score AS credit_score, raw:after:outstanding_debt AS outstanding_debt
    FROM
      postgres_cdc_credit_history
    WHERE
      _tp_time > earliest_ts()
  ), customer AS
  (
    SELECT
      _tp_time, raw:after:customer_id AS customer_id, raw:after:name AS name, raw:after:email AS email, raw:after:phone AS phone, raw:after:address AS address
    FROM
      postgres_cdc_customers
    WHERE
      _tp_time > earliest_ts()
  ), unstructure AS
  (
    SELECT
      _tp_time, raw:payload:after:customer_id AS customer_id, raw:payload:after:raw_data AS raw_data
    FROM
      mongo_cdc
    WHERE
      _tp_time > earliest_ts()
  )
SELECT
  unstructure.customer_id as customer_id, unstructure.raw_data as transactions, 
  customer.name, customer.email, customer.phone, customer.address, 
  credit_history.bank_name, credit_history.credit_score, credit_history.outstanding_debt
FROM
  unstructure
INNER JOIN customer ON unstructure.customer_id = customer.customer_id AND date_diff_within(1m, unstructure._tp_time, customer._tp_time)
INNER JOIN credit_history ON unstructure.customer_id = credit_history.customer_id AND date_diff_within(1m, unstructure._tp_time, credit_history._tp_time)






