## Description

Strideutils contains common patterns for cosmos api requests, monitoring, and other integrations for gsheets, slack, and twilio.

## Setup

In a virtual environment of your choice install strideutils.

```
pip install strideutils
```

with poetry

```
poetry add strideutils
```

This package is frequently updated, so keep that in mind while developing.

## Configuration

Strideutils requires three different environment variables that can be added to `~/.zshrc` or `~/.bashrc`

```
export STRIDEUTILS_CONFIG_PATH=
export STRIDEUTILS_ENV_PATH=
```

Examples of these files are included under strideutils/config_examples.
Stride Labs employees can find config.yaml in launchpad and .env.local in lastpass. We recommend you place .env.local in your launchpad repo.

Any configuration or secrets that aren't consumed don't need to be set. However if one is accessed but unset, an error will be thrown for easier debugging.

Once strideutils is installed and configured, each module you need should be imported individually. This isolates the different secrets that are expected and consumed.

Some common imports:

```python
from strideutils.stride_config import config
config.get_chain(name='osmosis')

from strideutils import stride_requests
stride_requests.request('https://google.com')

from strideutils.stride_alerts import raise_alert
```

## Slack Connector

TODO

## Sheets Connector

TODO

## Redis Connector

TODO

## Telegram Connector

The Telegram connector provides a simple interface for sending messages and files to Telegram chats. It uses the python-telegram-bot library internally but provides a synchronous interface for ease of use.

### Setup

1. Install the required dependency:
   ```
   pip install python-telegram-bot>=22.0
   ```

2. Set the `TELEGRAM_BOT_TOKEN` environment variable with your Telegram bot token (can be obtained from BotFather on Telegram)

### Usage Examples

```python
# Send a simple message
from strideutils import telegram_connector

# Simple message
telegram_connector.send_message("123456789", "Hello Berachain validators!")

# Thread messages
telegram_connector.send_message(
    "123456789", 
    [
        "Stride delegation update:", 
        "We've delegated 1000 BGT to your validator node.",
        "Transaction hash: 0x1234..."
    ]
)

# Send a file with caption
telegram_connector.send_file(
    "123456789",
    "/path/to/a/file/eg/delegation_report.pdf",
    caption="March delegation report"
)
```

The connector follows the singleton pattern used elsewhere in strideutils, and automatically handles the conversion between async and sync interfaces.

## Developing Strideutils

To access the strideutils repo locally rather than using the pip version (for actively making changes to strideutils and a dependency), add the path to strideutils to the beginning of PYTHONPATH

```python
import sys
sys.path = ['/path/to/strideutils/'] + sys.path
```

Alternatively, you can install strideutils through local mode. However, please be warned that this will make your local Python environment _always_ use your local strideutils. This might lead to unexpected behavior if you local changes.

To install in local mode, run the following:

```python
pip3 install -e /Users/username/Documents/strideutils
```

Confirm the location of where it's being imported from by printing the module.
After making changes to strideutils, reload it before testing your application.

```python
from importlib import reload
reload(strideutils)
```
