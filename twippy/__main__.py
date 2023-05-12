import discord
import os
import sys

from bot import Bot
from log import get_logger

log = get_logger("Twippy")


if "TOKEN" not in os.environ:
    message = "TOKEN is not set as an environment variable"
    log.fatal(message)
    sys.exit(message)


if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.message_content = True

    client = Bot(intents=intents)

    client.run(os.environ["TOKEN"])
