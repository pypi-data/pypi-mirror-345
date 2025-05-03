#!/bin/bash

set -e

# Register MongoDB Connector
curl -X POST http://localhost:8083/connectors \
-H "Content-Type: application/json" \
-d '{
  "name": "mongodb-connector",
  "config": {
    "connector.class": "io.debezium.connector.mongodb.MongoDbConnector",
    "tasks.max": "1",
    "mongodb.connection.string": "mongodb://mongo:27017/?replicaSet=rs0",
    "mongodb.name": "dbserver1",
    "database.include.list": "lumi_data",
    "collection.include.list": "lumi_data.unstructured_data",
    "topic.prefix": "mongodb",
    "mongodb.change.stream.full.document": "updateLookup",
    "database.history.kafka.bootstrap.servers": "kafka:9092",
    "database.history.kafka.topic": "schema-changes.lumi_data"
  }
}'

# Register PostgreSQL Connector
curl -X POST "http://localhost:8083/connectors" \
-H "Content-Type: application/json" \
-d '{
  "name": "inventory-connector",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "database.hostname": "postgres",
    "database.port": "5432",
    "database.user": "debezium",
    "database.password": "dbz",
    "database.dbname": "lumi_credit",
    "database.server.name": "lumi_credit_server",
    "slot.name": "debezium_slot",
    "plugin.name": "pgoutput",
    "publication.autocreate.mode": "filtered",
    "table.include.list": "public.credit_history,public.customers",
    "topic.prefix": "postgres",
    "key.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter.schemas.enable": "false"
  }
}'
