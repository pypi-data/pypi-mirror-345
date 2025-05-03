CREATE EXTERNAL TABLE IF NOT EXISTS my_s3_stream (
    id string,
    value float
)
SETTINGS
    type = 's3',
    access_key_id = 'minioadmin',
    secret_access_key = 'minioadmin',
    region = 'us-east-1',
    bucket = 'timeplus',
    data_format = 'JSONEachRow',
    endpoint = 'http://minio:9000',
    write_to = 'example/data.json',
    use_environment_credentials = false;

INSERT INTO my_s3_stream (id, value) VALUES
('sensor-a', 12.5),
('sensor-b', 18.9),
('sensor-c', 5.3),
('sensor-a', 13.1),
('sensor-b', 19.0);

CREATE EXTERNAL TABLE IF NOT EXISTS read_my_s3_json (
    id string,
    value float
)
SETTINGS
    type = 's3',
    access_key_id = 'minioadmin',
    secret_access_key = 'minioadmin',
    region = 'us-east-1',
    bucket = 'timeplus',
    data_format = 'JSONEachRow',
    endpoint = 'http://minio:9000',
    read_from = 'example/data.*.json',
    use_environment_credentials = false;

SELECT * FROM read_my_s3_json;