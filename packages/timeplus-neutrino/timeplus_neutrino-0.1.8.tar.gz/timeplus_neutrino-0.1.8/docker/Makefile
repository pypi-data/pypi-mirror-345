
.PHONY: list_topics

list_topics:
	docker exec -it redpanda rpk topic list --brokers=localhost:19092

list_schemas:
	curl http://localhost:8081/subjects

list_connectors:
	curl http://localhost:8083/connectors

register_connectors:
	source ./script/register.sh 

mongo_client:
	docker run -it --rm rtsp/mongosh mongosh mongodb://host.docker.internal:27017

postgres_client:
	docker run -it --rm postgres psql -h host.docker.internal -U debezium -d lumi_credit

install_dep:
	curl -X POST http://localhost:8123/timeplusd/v1/python_packages \
		-u proton:timeplus@t+ \
		-d '{"packages": [{"name": "timeplus-neutrino", "version": "0.1.2"}]}'

uninstall_deps:
	curl -X DELETE http://localhost:8123/timeplusd/v1/python_packages/timeplus-neutrino \
		-u proton:timeplus@t+

list_deps:
	curl http://localhost:8123/timeplusd/v1/python_packages \
		-u proton:timeplus@t+ 

init:
	docker compose exec -it timeplus timeplus sync --username proton --password timeplus@t+ apply ./tp-sync/

