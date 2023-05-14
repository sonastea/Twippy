import asyncio
import json
import scraper

from discord import Client
from discord.ext import tasks
from log import setup_logger, get_logger

setup_logger()

log = get_logger("Twippy")

BOT_ID = 1105600725129633884

handles = {}


class Bot(Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.offset = {}

    async def setup_hook(self) -> None:
        """Default async initialisation method for discord.py."""
        self.retrieve_saved_handles.start()

    async def on_ready(self):
        log.info(f"Logged in as {self.user}")

    async def on_disconnect(self):
        log.info(f"Disconnected as {self.user}")
        self.dump_handles_data()

    async def dump_handles_data(self):
        with open("handles.json", "w") as file:
            json.dump(handles, file)

    async def on_message(self, message):
        if message.author == self.user:
            return

        log.info(f"{message.author.name} {message.content}")

        if message.content.startswith(".add"):
            handle = message.content.split(" ")[1]
            channel_id = message.channel.id

            handles[handle] = channel_id
            await message.add_reaction("✅")
            await self.dump_handles_data()

        if message.content.startswith(".remove"):
            handle = message.content.split(" ")[1]

            handles.pop(handle)
            await message.add_reaction("✅")
            await self.dump_handles_data()

    async def get_last_messages(self, channel_id: int) -> None:
        log.info(f"<get_last_messages> {channel_id}")

        """find last message from twippy in this channel"""
        channel = self.get_channel(channel_id)
        messages = [
            message
            async for message in channel.history(limit=200)
            if message.author.id == BOT_ID
        ]

        """
        Generic tweet url: https://twitter.com/{handle}/status/{tweet_id}
        Extract tweet id from [5] index existing message
        Otherwise set previous tweets length to 0
        """
        tweet_ids = {}
        for message in reversed(messages):
            tweet_ids[message.content.split(
                "/")[3]] = message.content.split("/")[5]

        for handle in handles.keys():
            if handle not in tweet_ids.keys():
                """
                we need to send the recent 40 tweets when tracking a new handle or
                the bot will never send newer tweets since we use the last
                discord message matching the handle and tweet id
                """
                try:
                    self.offset[handle]
                except KeyError:
                    self.offset[handle] = 0
            else:
                """
                Fetch latest tweets from this handle and find if it exists in that list
                Exists: Set previous list length including last message to use as offset for later
                Else: Set previous list to starting point of 0 as key, offset dict
                """
                tweets = await scraper.get(handle)
                tweet = next(
                    (tweet for tweet in tweets if tweet.id ==
                     tweet_ids[handle]), None
                )

                if tweet is not None:
                    index = tweets.index(tweet)
                    self.offset[handle] = 0 if index == -1 | 0 else index + 1
                else:
                    self.offset[handle] = 0

    async def send_new_messages(self, handle: str, channel_id: int) -> None:
        log.info(f"<send_new_messages> {handle},{channel_id}")

        channel = self.get_channel(channel_id)
        tweets = await scraper.get(handle)

        """
        Retrieve starting index by using length of previous list as an offset.
        Starting index = length of new tweets - offset
        Update offset[handle] to newly tweets length
        """
        offset = (
            self.offset[handle] if self.offset[handle] < len(
                tweets) else len(tweets)
        )
        for tweet in tweets[offset:]:
            msg = "https://twitter.com/{}/status/{}".format(handle, tweet.id)
            await channel.send(msg)

    @tasks.loop(count=1)
    async def retrieve_saved_handles(self):
        log.info(f"<retrieve_saved_handles>")

        file = open("handles.json")
        saved_handles = json.load(file)
        for handle, channel_id in saved_handles.items():
            handles[handle] = channel_id
        file.close()

        self.retrieve_tweets.start()

    @tasks.loop(seconds=60)
    async def retrieve_tweets(self):
        log.info(f"<retrieve_tweets> __Starting__")

        get_last_jobs = []
        send_new_jobs = []

        for channel_id in set(handles.values()):
            get_last_jobs.append(self.get_last_messages(channel_id))
        await asyncio.gather(*get_last_jobs)

        for handle, channel_id in handles.items():
            send_new_jobs.append(self.send_new_messages(handle, channel_id))
        await asyncio.gather(*send_new_jobs)

        log.info(f"<retrieve_tweets> __Finishing__")

    @retrieve_saved_handles.before_loop
    async def before_retrieved_saved_handles(self):
        await self.wait_until_ready()

    @retrieve_tweets.before_loop
    async def before_retrieve_tweets(self):
        await self.wait_until_ready()
