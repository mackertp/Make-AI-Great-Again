from __future__ import print_function
try:
    import tweepy
except IOError:
    print('This application requires the tweepy python module.\nInstall with "pip install tweepy"')

"""
Debate analyzer project ("Make AI Great Again")
Twitter tools class
-- methods used to search Twitter and get data on who is receiving tweets

Dylan Telford, Preston Mackert, Alexis Grebenok, Jerry Daigler
10/27/16
"""

candidate_twitters = {"TRUMP": "@realDonaldTrump", "CLINTON": "@HillaryClinton", "CHAFEE": "@LincolnChafee", "WEBB":
                      "@JimWebbUSA", "O'MALLEY": "@MartinOMalley", "SANDERS": "@BernieSanders", "PAUL": "@RandPaul",
                      "CARSON": "@RealBenCarson", "RUBIO": "@marcorubio", "BUSH": "@JebBush", "CRUZ": "@tedcruz",
                      "CHRISTIE": "@GovChristie", "WALKER": "@ScottWalker", "HUCKABEE": "@GovMikeHuckabee", "KASICH":
                      "@JohnKasich", "PENCE": "@mike_pence", "KAINE": "@timkaine"}

CONSUMER_KEY = 'uxXFZ6Vl1Z0euLnYkbuupPsUY'
CONSUMER_SECRET = 'UZXd2H97ekAzbkvUcbk1xu60aE6Ce3JTVU3s5NJh26wBrT9HWI'
ACCESS_TOKEN = '382831461-K0IlfzPWq3zqt9NbxdiHdk89FZ74EHzCTQrCCWxf'
ACCESS_TOKEN_SECRET = 'jAXo0ICCjFgFTU7dPLKS9Vi2tK9mJe84JgLqFHVrekssB'

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

api = tweepy.API(auth)


def candidate_mentions(topic, candidate):
    topic += '@%s-filter:retweets' % candidate_twitters[candidate]
    results = api.search(q=topic, count=200)
    return results


def get_top_five(tweets):
    top_tweets = []
    for tweet in tweets:
        if top_tweets.__len__() < 6:
            top_tweets.append(tweet)
        else:
            for item in top_tweets:
                if tweet.favorite_count > item.favorite_count and tweet not in top_tweets:
                    top_tweets[top_tweets.index(item)] = tweet

    out = "\nhere are the five most popular tweets:\n\n"
    for tweet in top_tweets:
        out += tweet.text
        out += "\n"
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
