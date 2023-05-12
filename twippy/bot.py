import discord
import scraper

from discord import Client
from discord.ext import tasks
from log import setup_logger, get_logger

setup_logger()

log = get_logger("Twippy")

BOT_ID = 1105600725129633884

handles = {
    "pogzilla1": 1105589209684783135,
    "ot9trans": 1104549831998967909,
}


class Bot(Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.offset = {}

    async def setup_hook(self) -> None:
        """Default async initialisation method for discord.py."""
        self.retrieve_tweets.start()

    async def on_ready(self):
        log.info(f"Logged in as {self.user}")

    @tasks.loop(seconds=60)
    async def retrieve_tweets(self):
        for handle, channel_id in handles.items():
            log.info(f"<retrieve_tweets>  {handle},{channel_id}")
            global tweet_id
            channel = self.get_channel(channel_id)

            """find last message from twippy in this channel"""
            message = await discord.utils.get(channel.history(), author__id=BOT_ID)

            """
            Generic tweet url: https://twitter.com/{handle}/status/{tweet_id}
            Extract tweet id from [5] index existing message
            Otherwise set previous tweets length to 0
            """
            if message is not None:
                tweet_id = message.content.split("/")[5]
            else:
                self.offset[handle] = 0
                continue

            """
            Fetch latest tweets from this handle and find if it exists in that list
            Exists: Set previous list length including last message to use as offset for later
            Else: Set previous list to starting point of 0 as key, offset dict
            """
            tweets = await scraper.get(handle)
            tweet = next(
                (tweet for tweet in tweets if tweet.id == tweet_id), None)

            if tweet is not None:
                index = tweets.index(tweet)
                self.offset[handle] = 0 if index == - \
                    1 else len(tweets[: index + 1])
            else:
                self.offset[handle] = 0

        for handle, channel_id in handles.items():
            channel = self.get_channel(channel_id)
            tweets = await scraper.get(handle)

            """
            Retrieve starting index by using length of previous list as an offset.
            Starting index = length of new tweets - offset
            Update offset[handle] to newly tweets length
            """
            offset = len(tweets) - self.offset[handle]
            start_index = len(tweets) - offset
            for tweet in tweets[start_index:]:
                msg = "https://twitter.com/{}/status/{}".format(
                    handle, tweet.id)
                await channel.send(msg)

    @retrieve_tweets.before_loop
    async def before_retrieval_of_tweets(self):
        await self.wait_until_ready()