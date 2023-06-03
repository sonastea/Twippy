from datetime import datetime, timedelta
import snscrape.modules.twitter as twit

MAX_NUM_TWEETS = 40


async def get(handle: str):
    tweets = []
    dayagodate = datetime.today() - timedelta(weeks=4)
    dayago = dayagodate.strftime("%Y-%m-%d")

    qry = f"(from:{handle} since:{dayago})"

    for idx, tweet in enumerate(twit.TwitterSearchScraper(qry).get_items()):
        if idx >= MAX_NUM_TWEETS:
            break

        tweets.append({"url": tweet.url, "id": str(tweet.id)})

    # tweets are in descending order by time
    # reverse the list to have the most recent tweet at the end,
    # so the bot could post tweets in ascending time order
    return tweets[::-1]
