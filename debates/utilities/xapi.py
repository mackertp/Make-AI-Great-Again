"""
Need to update the old twitter connection with a new API into 
X.com... it's cool, but just don't undertstand why it had to 
literally kill the twitter bird, loved that guy.

@author Preston Mackert
"""

# ---------------------------------------------------------------- #
# libraries
# ---------------------------------------------------------------- #

import config
# last updated in 2023, might still be okay?
import tweepy # https://pypi.org/project/tweepy/

# ---------------------------------------------------------------- #
# rest api config
# ---------------------------------------------------------------- #

candidate_twitters = {
    "TRUMP": "@realDonaldTrump", "BIDEN": "@JoeBiden"
}

# need to create a new .env file
auth = tweepy.OAuthHandler(config.CONSUMER_KEY, config.CONSUMER_SECRET)
auth.set_access_token(config.ACCESS_TOKEN, config.ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)


# ---------------------------------------------------------------- #
# functional api programming - opportunities to abstract
# ---------------------------------------------------------------- #

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
