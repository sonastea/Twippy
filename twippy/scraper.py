from tweety.bot import Twitter, UserTweets

app = Twitter()


async def get(handle: str) -> UserTweets:
    all_tweets = app.get_tweets(handle, replies=False)
    # tweets are in descending order by time, 0 index is the most recent
    # we reverse the list to have the most recent tweet at the end,
    # so the bot could tweets in ascending time postted
    return all_tweets[::-1]
