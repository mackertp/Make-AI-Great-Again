import tweepy

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

results = api.search(q="Trump")
for result in results:
    print(result.text)


def candidate_search(topic, candidate):
    results = api.search(q=topic)
