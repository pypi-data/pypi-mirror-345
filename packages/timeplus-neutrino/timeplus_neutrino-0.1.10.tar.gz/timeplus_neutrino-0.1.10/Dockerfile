FROM python:3.13.3-slim

ARG VERSION

WORKDIR /timeplus
ADD ./requirements.txt /timeplus
RUN pip3 install -r requirements.txt

COPY ./dist/timeplus_neutrino-${VERSION}.tar.gz /timeplus/timeplus_neutrino-${VERSION}.tar.gz
RUN pip3 install /timeplus/timeplus_neutrino-${VERSION}.tar.gz

# ENTRYPOINT ["python", "-m", "neutrino.mcp.ui_client", "/usr/local/lib/python3.13/site-packages/neutrino/mcp/main.py"]
# ENTRYPOINT ["python", "-m", "neutrino.mcp.cli_client", "/usr/local/lib/python3.13/site-packages/neutrino/mcp/main.py"]

ENTRYPOINT ["python", "-m", "neutrino.mcp.application_server"]

