import yaml
import logging
import logging.config


log_config_yaml = """
version: 1
disable_existing_loggers: false
formatters:
  simple:
    format: '%(levelname)s: %(message)s'
handlers:
  stdout:
    class: logging.StreamHandler
    formatter: simple
    stream: ext://sys.stdout
loggers:
  root:
    level: DEBUG
    handlers:
    - stdout
"""

logger = logging.getLogger("aimo")
logging.config.dictConfig(yaml.safe_load(log_config_yaml))
