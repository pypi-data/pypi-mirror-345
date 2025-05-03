import os

from proton_driver import client

timeplus_host = os.getenv("TIMEPLUS_HOST") or "localhost"
timeplus_user = os.getenv("TIMEPLUS_USER") or "proton"
timeplus_password = os.getenv("TIMEPLUS_PASSWORD") or "timeplus@t+"


class Tools:
    def __init__(self) -> None:
        self.client = client.Client(
            host=timeplus_host,
            port=8463,
            user=timeplus_user,
            password=timeplus_password,
        )

    def list_table(self, *args):
        result = []
        rows = self.client.execute_iter("SHOW STREAMS")
        for row in rows:
            result.append(row[0])
        return result

    def describe_table(self, *args):
        name = args[0]
        result = []
        rows = self.client.execute_iter(f"DESCRIBE {name.strip()}")
        for row in rows:
            col = {}
            col["name"] = row[0]
            col["type"] = row[1]
            result.append(col)
        return result

    def run(self, tool_name, *args):
        result = getattr(self, tool_name)(*args)
        return result

    def list(self):
        return ["list_table", "describe_table"]
