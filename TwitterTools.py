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

candidate_twitters = {"TRUMP": "@realDonaldTrump", "CLINTON": "@HillaryClinton"}

CONSUMER_KEY = 'uxXFZ6Vl1Z0euLnYkbuupPsUY'
CONSUMER_SECRET = 'UZXd2H97ekAzbkvUcbk1xu60aE6Ce3JTVU3s5NJh26wBrT9HWI'
ACCESS_TOKEN = '382831461-K0IlfzPWq3zqt9NbxdiHdk89FZ74EHzCTQrCCWxf'
ACCESS_TOKEN_SECRET = 'jAXo0ICCjFgFTU7dPLKS9Vi2tK9mJe84JgLqFHVrekssB'

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

api = tweepy.API(auth)


def candidate_mentions(topic, candidate):
    topic += '@%s' % candidate_twitters[candidate]
    results = api.search(q=topic)
    return results


def candidate_account(topic, candidate):
    topic = 'from:%s' % candidate_twitters[candidate][1:]
    print(topic)
    results = api.search(q=topic)
    return results


def opponent_mentions(topic, candidate):
    topic += '@%s' % candidate
    results = api.search(q=topic)
    return results


def opponent_account(topic, candidate):
    topic += 'from:%s' % candidate_twitters[candidate][1:]
    results = api.search(q=topic)
    return results
