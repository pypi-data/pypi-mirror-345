import logging


class UsersLogs:
    HUD_ENABLE_NOT_SET = (
        logging.ERROR,
        "Did not load as HUD_ENABLE is undefined. \
Please set HUD_ENABLE=true to run Hud. For more information visit https://docs.hud.io/docs/py-sdk-ie.",
    )
    HUD_ENABLE_INVALID = (
        logging.ERROR,
        "Did not load as HUD_ENABLE is set to a non-true value. \
Please set HUD_ENABLE=true to run Hud. For more information visit https://docs.hud.io/docs/py-sdk-ie.",
    )
    HUD_SERVICE_NOT_SET = (
        logging.ERROR,
        "Can't load Hud, HUD_SERVICE was not set. \
Please set service name using the env var HUD_SERVICE. For more information visit https://docs.hud.io/docs/py-sdk-ie. E0001",
    )
    HUD_SERVICE_INVALID = (
        logging.ERROR,
        "Can't load Hud, HUD_SERVICE value has invalid service name. \
Please set service name using the env var HUD_SERVICE. For more information visit https://docs.hud.io/docs/py-sdk-ie. E0002",
    )
    HUD_KEY_NOT_SET = (
        logging.ERROR,
        "Can't load Hud, HUD_KEY was not set. \
Please set API key using the env var HUD_KEY. For more information visit https://docs.hud.io/docs/py-sdk-ie. E0003",
    )
    HUD_KEY_INVALID = (
        logging.ERROR,
        "Can't load Hud, HUD_KEY value has invalid API key. \
Please set a valid key in env var HUD_KEY. For more information visit https://docs.hud.io/docs/py-sdk-ie. E0004",
    )
    HUD_TAGS_INVALID_TYPE = (
        logging.WARN,
        "HUD_TAGS should be of type Dict[str, str], Hud will run without tags. \
Please set valid tags in env var HUD_TAGS. For more information visit https://docs.hud.io/docs/py-sdk-ie. E0005",
    )
    HUD_TAGS_WITH_DOTS = (
        logging.WARN,
        "HUD_TAGS keys can't contain dots, they have been replaced with underscores. For more information visit https://docs.hud.io/docs/py-sdk-ie. E0006",
    )
    HUD_TAGS_INVALID_JSON = (
        logging.WARN,
        "HUD_TAGS is not a valid json, defaulting to empty tags. \
Please set valid textual tags in env var HUD_TAGS. For more information visit https://docs.hud.io/docs/py-sdk-ie. E0007",
    )
    HUD_INITIALIZED_SUCCESSFULLY = (
        logging.INFO,
        "Initialized successfully",
    )
    HUD_RUN_EXPORTER_FAILED = (
        logging.ERROR,
        "SDK has initiated a graceful shutdown. Your application remains unaffected. E0008",
    )
    HUD_FAILED_TO_CONNECT_TO_MANAGER = (
        logging.ERROR,
        "SDK has initiated a graceful shutdown. Your application remains unaffected. E0009",
    )
    HUD_EXCEPTION_IN_WORKER = (
        logging.ERROR,
        "SDK has initiated a graceful shutdown. Your application remains unaffected. E0010",
    )
    HUD_EXPORTER_STARTUP_TIMEOUT = (
        logging.ERROR,
        "SDK has initiated a graceful shutdown. Your application remains unaffected. E0011",
    )

    HUD_PYTHON_EXECUTABLE_NOT_FOUND = (
        logging.ERROR,
        "Can't load Hud, Python executable was not found. Please set HUD_PYTHON_BINARY_PATH with the python executable path. For more information visit https://docs.hud.io/docs/py-sdk-ie. E0012",
    )
    HUD_FAILED_TO_COMMUNICATE_WITH_MANAGER = (
        logging.ERROR,
        "SDK has initiated a graceful shutdown. Your application remains unaffected. E0013",
    )
    HUD_NO_MANAGER = (
        logging.ERROR,
        "SDK has initiated a graceful shutdown. Your application remains unaffected. E0014",
    )
    HUD_FAILED_TO_REGISTER_PROCESSES = (
        logging.ERROR,
        "SDK has initiated a graceful shutdown. Your application remains unaffected. E0015",
    )
    HUD_FAILED_TO_OPEN_SHARED_MEMORIES = (
        logging.ERROR,
        "SDK has initiated a graceful shutdown. Your application remains unaffected. E0016",
    )
    HUD_FAILED_TO_REGISTER_TASKS = (
        logging.ERROR,
        "SDK has initiated a graceful shutdown. Your application remains unaffected. E0017",
    )
    HUD_THROTTLED = (
        logging.WARN,
        "SDK initialized successfully in idle mode.",
    )
    HUD_FIRST_METRICS_COLLECTED = (
        logging.INFO,
        "First metrics collected successfully",
    )
    HUD_STANDBY_ARGS_INVALID = (
        logging.ERROR,
        "Can't load Hud, standby mode arguments were partially provided. Please set both standby_callback and standby_check_interval arguments to enable standby mode. E0019",
    )
    HUD_STANDBY_MINIMUM_INTERVAL = (
        logging.WARN,
        "standby_check_interval is less than the minimum required interval. Defaulting to minimum interval.",
    )
    HUD_STANDBY_MODE = (
        logging.INFO,
        "Entering standby mode. Metrics will not be collected until re-enabled.",
    )
    HUD_STANDBY_CALLBACK_UNEXPECTED_BEHAVIOR = (
        logging.WARN,
        "Can't load Hud, provided standby callback behaves unexpectedly. The expected callback is a synchronous function that returns a boolean. E0020",
    )
    HUD_STANDBY_CALLBACK_EXCEPTION_INFO = (
        logging.ERROR,
        "During the execution of the standby callback, an exception occurred:",
    )
    HUD_ENTRYPOINT_COMMAND_NOT_PROVIDED = (
        logging.ERROR,
        "Please provide a valid command to run.",
    )
    HUD_ENTRYPOINT_COMMAND_NOT_FOUND = (
        logging.ERROR,
        "Command executable not found.",
    )
