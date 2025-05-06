import os


def get_timeplus_env_config():
    """
    Extract Timeplus-specific environment variables from the current environment
    and return them as a dictionary.

    Returns:
        dict: A dictionary containing Timeplus environment variables as strings
    """
    # Define the environment variables we want to extract
    timeplus_vars = [
        "TIMEPLUS_HOST",
        "TIMEPLUS_USER",
        "TIMEPLUS_PASSWORD",
        "TIMEPLUS_READ_ONLY",
        "TIMEPLUS_KAFKA_CONFIG",
    ]

    # Create a dictionary with the environment variables
    config = {}
    for var in timeplus_vars:
        value = os.environ.get(var)
        if value is not None:
            config[var] = value

    return config
