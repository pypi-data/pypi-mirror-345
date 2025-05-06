-- append only
select schema_inference($${
		"customer_id": 999,
		"name": "Johnathan Rodriguez",
		"email": "thomasramirez@example.org",
		"phone": "001-845-290-8721x77863",
		"address": "743 Cervantes Causeway Apt. 762\nPort Lauren, NY 12698",
		"ip": "127.0.0.1",
		"time": "2023-01-01 00:00:00",
		"event_time": "2023-01-01 00:00:00",
		"uid": "2a02:aa08:e000:3100::2",
		"uid2":"1f71acbf-59fc-427d-a634-1679b48029a9"
}
$$, 'test', 'test stream', 'append_only','')


-- mutable stream
select schema_inference($${
		"customer_id": 999,
		"name": "Johnathan Rodriguez",
		"email": "thomasramirez@example.org",
		"phone": "001-845-290-8721x77863",
		"address": "743 Cervantes Causeway Apt. 762\nPort Lauren, NY 12698",
		"ip": "127.0.0.1",
		"time": "2023-01-01 00:00:00",
		"event_time": "2023-01-01 00:00:00",
		"uid": "2a02:aa08:e000:3100::2",
		"uid2":"1f71acbf-59fc-427d-a634-1679b48029a9"
}
$$, 'test', 'test stream', 'mutable_stream', '')

-- external stream
select schema_inference($${
		"customer_id": 999,
		"name": "Johnathan Rodriguez",
		"email": "thomasramirez@example.org",
		"phone": "001-845-290-8721x77863",
		"address": "743 Cervantes Causeway Apt. 762\nPort Lauren, NY 12698",
		"ip": "127.0.0.1",
		"time": "2023-01-01 00:00:00",
		"event_time": "2023-01-01 00:00:00",
		"uid": "2a02:aa08:e000:3100::2",
		"uid2":"1f71acbf-59fc-427d-a634-1679b48029a9"
}
$$, 'test', 'test stream', 'external',$${
  "type": "kafka",
  "brokers": "redpanda:9092",
  "topic": "customer",
  "security_protocol": "PLAINTEXT",
  "data_format": "JSONEachRow",
  "skip_ssl_cert_check": "false",
  "one_message_per_row": "true"
}
$$)


-- new merged flow

select raw:stream_ddl , raw:mutable_stream_ddl from (
select schema_inference_with_fields_comment($${
		"customer_id": 999,
		"name": "Johnathan Rodriguez",
		"email": "thomasramirez@example.org",
		"phone": "001-845-290-8721x77863",
		"address": "743 Cervantes Causeway Apt. 762\nPort Lauren, NY 12698",
		"ip": "127.0.0.1",
		"time": "2023-01-01 00:00:00",
		"event_time": "2023-01-01 00:00:00",
		"uid": "2a02:aa08:e000:3100::2",
		"uid2":"1f71acbf-59fc-427d-a634-1679b48029a9"
}
$$, 'test', 'test stream', 'stream','') as raw)