import os
from openai import OpenAI

from cryptography.fernet import Fernet
from base64 import urlsafe_b64encode, urlsafe_b64decode

from proton_driver import client
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import ModelInfo

timeplus_host = os.getenv("TIMEPLUS_HOST") or "localhost"
timeplus_user = os.getenv("TIMEPLUS_AISERVICE_USER") or "proton"
timeplus_password = os.getenv("TIMEPLUS_AISERVICE_PASSWORD") or "timeplus@t+"

timeplus_aiservice_db = os.getenv("TIMEPLUS_AISERVICE_DB") or "aiservice"

config_stream_name = "agent_config"
secret_stream_name = "secret_store"


class TimeplusAgentConfig:
    def __init__(self) -> None:
        self.secret_manager = SecretManager()
        self.client = client.Client(
            host=timeplus_host,
            user=timeplus_user,
            password=timeplus_password,
            port=8463,
        )
        self._init()

    def _init(self) -> None:
        self._create_aiservice_db()
        self._create_config_stream()

    def get_timeplusd_client(self) -> client.Client:
        return self.client

    def get_aiservice_db(self) -> str:
        return timeplus_aiservice_db

    def _create_aiservice_db(self) -> None:
        try:
            self.client.execute(
                f"CREATE DATABASE IF NOT EXISTS {timeplus_aiservice_db}"
            )
        except Exception as e:
            print(e)

    def _create_config_stream(self) -> None:
        try:
            self.client.execute(
                f"""CREATE MUTABLE STREAM IF NOT EXISTS {timeplus_aiservice_db}.{config_stream_name} (
                agent string,
                base_url string,
                api_key string,
                model string
            )
            PRIMARY KEY (agent)
            """
            )
        except Exception as e:
            print(e)

    def _update_config(self, agent: str, base_url: str, api_key: str, model: str):
        if agent is None or len(agent) == 0:
            print("agent is empty, skip config")
            return

        try:
            self.client.execute(
                f"INSERT INTO {timeplus_aiservice_db}.{config_stream_name} (agent, base_url, api_key, model) VALUES",
                [
                    [
                        agent,
                        base_url,
                        self.secret_manager.encrypt(api_key).decode(),
                        model,
                    ]
                ],
            )
        except Exception as e:
            print(e)

    def _get_config(self, agent: str) -> dict:
        result = {}
        result["base_url"] = os.getenv("OPENAI_BASE_URL") or "https://api.openai.com/v1"
        result["api_key"] = os.getenv("OPENAI_API_KEY")
        result["model"] = "gpt-4o"
        try:
            rows = self.client.execute_iter(
                f"SELECT base_url, api_key, model FROM table({timeplus_aiservice_db}.{config_stream_name}) WHERE agent = '{agent}'"
            )
            for row in rows:
                result["base_url"] = row[0]
                result["api_key"] = self.secret_manager.decrypt(row[1].encode())
                result["model"] = row[2]

            return result

        except Exception as e:
            print(e)

        return result

    def config(self, agent: str, base_url: str, api_key: str, model: str) -> None:
        ok, err = self.validate_openai_config(base_url, api_key, model)
        if not ok:
            raise Exception(f"Invalid OpenAI configuration, error: {err}")

        self._update_config(agent, base_url, api_key, model)

    def get_client(self, agent: str) -> OpenAIChatCompletionClient:
        agent_config = self._get_config(agent)
        model_info = ModelInfo(
            family=agent_config["model"],
            function_calling=False,
            json_output=False,
            vision=False,
        )
        openai_model_client = OpenAIChatCompletionClient(
            model=agent_config["model"],
            base_url=agent_config["base_url"],
            api_key=agent_config["api_key"],
            model_info=model_info,
            temperature=0.0,
        )
        return openai_model_client

    def validate_openai_config(self, base_url, api_key, model):

        """
        Validate OpenAI configuration by making a simple request to the API.

        Args:
        base_url (str): The base URL of the OpenAI API.
        api_key (str): The API key to use for authentication.
        model (str): The name of the model to use for the request.

        Returns:
        tuple: A tuple containing a boolean indicating whether the configuration is valid, and a string containing an error message if the configuration is invalid.
        """
        try:
            # Initialize the client with the provided configuration
            client = OpenAI(base_url=base_url, api_key=api_key)

            # Try to make a simple request
            client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {
                        "role": "user",
                        "content": "Hello, this is a test message to verify API configuration.",
                    },
                ],
                max_tokens=10,
            )

            # If we get here without an exception, the configuration is valid
            print("Success OpenAI configuration is valid!")
            print(f"Model: {model}")
            return True, None

        except Exception as e:
            print("Failed OpenAI configuration validation failed!")
            print(f"Error: {str(e)}")
            return False, str(e)


class SecretManager:
    def __init__(self):
        """
        Initialize the SecretManager that uses Timeplus mutable stream to store encryption keys.

        Args:
            client: The Timeplus client instance
            db_name: The database name where the stream will be created
            stream_name: The name of the mutable stream to store encryption keys
        """
        self.client = client.Client(
            host=timeplus_host,
            user=timeplus_user,
            password=timeplus_password,
            port=8463,
        )
        self.db_name = timeplus_aiservice_db
        self.stream_name = secret_stream_name
        self._create_key_stream()
        self.key = self._get_or_create_key()

    def _create_key_stream(self):
        """Create the mutable stream for storing encryption keys if it doesn't exist"""
        try:
            self.client.execute(
                f"""CREATE MUTABLE STREAM IF NOT EXISTS {self.db_name}.{self.stream_name} (
                key_id string,
                encryption_key string
                )
                PRIMARY KEY (key_id)
                """
            )
        except Exception as e:
            print(f"Error creating encryption key stream: {e}")

    def _get_or_create_key(self) -> bytes:
        """
        Retrieve the encryption key from the Timeplus stream or create a new one if it doesn't exist.
        Exits with fatal error if Timeplus access fails.

        Returns:
            bytes: The encryption key

        Raises:
            SystemExit: If there's an error accessing the Timeplus stream
        """
        key_id = "primary"  # Using a static key_id for simplicity

        try:
            # Try to retrieve the existing key
            rows = self.client.execute_iter(
                f"SELECT encryption_key FROM table({self.db_name}.{self.stream_name}) WHERE key_id = '{key_id}'"
            )

            # Check if we got a result
            for row in rows:
                if row and row[0]:
                    return urlsafe_b64decode(row[0])

            # If we get here, no key was found, so create a new one
            encryption_key = Fernet.generate_key()

            # Store the key in the mutable stream
            self.client.execute(
                f"INSERT INTO {self.db_name}.{self.stream_name} (key_id, encryption_key) VALUES",
                [
                    [
                        key_id,
                        urlsafe_b64encode(
                            encryption_key
                        ).decode(),  # Store as base64 string
                    ]
                ],
            )
            print("New encryption key generated and saved to Timeplus.")
            return encryption_key

        except Exception as e:
            error_msg = (
                f"FATAL ERROR: Failed to access Timeplus stream for encryption key: {e}"
            )
            print(error_msg)
            import sys

            sys.exit(1)  # Exit with error code 1

    def encrypt(self, input: str) -> bytes:
        """
        Encrypt a string input

        Args:
            input: The string to encrypt

        Returns:
            bytes: The encrypted data
        """
        cipher = Fernet(self.key)
        encrypted_input = cipher.encrypt(input.encode())
        return encrypted_input

    def decrypt(self, input: bytes) -> str:
        """
        Decrypt encrypted data

        Args:
            input: The encrypted data

        Returns:
            str: The decrypted string
        """
        cipher = Fernet(self.key)
        decrypted_input = cipher.decrypt(input).decode()
        return decrypted_input
