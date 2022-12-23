"""
Debate analyzer project ("Make AI Great Again")
Twitter tools class
-- methods used to search Twitter and get data on who is receiving tweets

Dylan Telford, Preston Mackert, Alexis Grebenok, Jerry Daigler
10/27/16
"""

# ------------------------------------------- #
# imports
# ------------------------------------------- #

import config
import tweepy

# ------------------------------------------- #
# configuration
# ------------------------------------------- #

candidate_twitters = {
    "TRUMP": "@realDonaldTrump", "CLINTON": "@HillaryClinton", "CHAFEE": "@LincolnChafee", 
    "WEBB":"@JimWebbUSA", "O'MALLEY": "@MartinOMalley", "SANDERS": "@BernieSanders", "PAUL": "@RandPaul",
    "CARSON": "@RealBenCarson", "RUBIO": "@marcorubio", "BUSH": "@JebBush", "CRUZ": "@tedcruz",
    "CHRISTIE": "@GovChristie", "WALKER": "@ScottWalker", "HUCKABEE": "@GovMikeHuckabee", "KASICH":
    "@JohnKasich", "PENCE": "@mike_pence", "KAINE": "@timkaine"
}

auth = tweepy.OAuthHandler(config.CONSUMER_KEY, config.CONSUMER_SECRET)
auth.set_access_token(config.ACCESS_TOKEN, config.ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)


# ------------------------------------------- #
# support functions
# ------------------------------------------- #

def candidate_mentions(topic, candidate):
    topic += '@%s-filter:retweets' % candidate_twitters[candidate]
    # tweepy deprecated the ability to search all tweets since we made this project
    results = api.search_recent_tweets(q=topic, count=200)
    return results


def get_top_five(tweets):
    top_tweets = []
    for tweet in tweets:
        if top_tweets.__len__() < 5:
            top_tweets.append(tweet)
        else:
            for item in top_tweets:
                if tweet.favorite_count > item.favorite_count and tweet not in top_tweets:
                    top_tweets[top_tweets.index(item)] = tweet

    out = "\nhere are the five most popular tweets:\n\n"
    tweet_num = 1
    for tweet in top_tweets:
        out += "%d) " % tweet_num
        out += tweet.text
        out += "\n"
        tweet_num += 1
    if len(tweets) == 0:
        out += "Welp, looks like nobody cared about this :(\n"

    return out


def get_hashtags(tweets):
    hashtags = []
    for tweet in tweets:
        for word in tweet.text.split(" "):
            try:
                if word[0] == "#" and word not in hashtags:
                    hashtags.append(word)
            except IndexError:
                continue

    return hashtags
