"""
This utility file provides classes and functions that are extended  
into Jupyter Notebooks.

@author Preston Mackert
"""

# ---------------------------------------------------------------- #
# libraries
# ---------------------------------------------------------------- #

# system config and core packages
import os
os.environ['HF_HOME'] = os.getcwd() + '/settings/cache/'
import sys
import re
import nltk
import random
# web utilities
from io import StringIO
from bs4 import BeautifulSoup
from urllib.request import urlopen
# bag of words approach
from nltk.sentiment.vader import SentimentIntensityAnalyzer
# neural network approach
from transformers import AutoTokenizer
from transformers import AutoModelForSequenceClassification
from scipy.special import softmax

# ---------------------------------------------------------------- #
# clean html
# ---------------------------------------------------------------- #

def clean_and_tag(url):
    """ 
    params: 
        - url: source web address for debate text
    returns: 
        - a nltk text object with tagged_tokens 
    """
    raw = urlopen(url).read()
    soup = BeautifulSoup(raw, 'html.parser')
    cleaned = BeautifulSoup.get_text(soup)
    # opportunity to clean up source
    tokens = nltk.word_tokenize(cleaned)
    tokens = trim_tokens(tokens)
    tagged_tokens = nltk.pos_tag(tokens)
    return nltk.Text(tagged_tokens)

def trim_tokens(tokens):
    """
    params: 
        - tokens: takes in text tokenized by nltk
    returns: 
        - cleaned token list 
    """
    start = 0
    end = len(tokens)-1
    for i in range(len(tokens)):
        if tokens[i] == 'PARTICIPANTS' and tokens[i+1] == ':':
            start = i
        elif tokens[i] == 'Citation' and tokens[i+1] == ':':
            end = i
            break
    return tokens[start:end]

# ---------------------------------------------------------------- #
# support classes
# ---------------------------------------------------------------- #

class Capturing(list):
    """
    Used as a support class for the get_topics method of the debate text.
    Ref: http://stackoverflow.com/questions/16571150/how-to-capture-stdout-output-from-a-python-function-call
    params: 
        - list
    returns: 
        - cleaned list
    """
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio
        sys.stdout = self._stdout


class AnalysisTools:
    def __init__(self, text):
        """
        Instantiates data structures for a custom class. Pre-populates the participants and 
        moderators based an assumed debate url. 
        params:
            - text: a nltk.Text object
        returns:
            - prepopulated participant list
            - text data structures for support functions
        """
        assert isinstance(text, nltk.Text)
        self.text = text
        self.participants, self.moderators = self.get_people()
        dicts = self.parse_text()
        self.speak_dict = dicts[0]
        self.word_dict = dicts[1]
        self.reaction_dict = dicts[2]
        self.text_dict = {}
        for part in self.participants:
            self.text_dict[part] = nltk.Text(self.word_dict[part])

    def candidate_topics(self, candidate):
        """
        params:
            - candidate: a string indicating the candidate you want to analyze
        returns:
            - a list of topics for the specified candidate
        """
        txt = nltk.Text(self.word_dict[candidate])
        with Capturing() as collocations:
            txt.collocations()
        all_colls = ""
        for item in collocations:
            all_colls += " " + item
        all_colls = all_colls[1:]
        topics = all_colls.split("; ")
        with open("settings/text_files/dontInclude.txt") as fh:
            dont_include = fh.read().splitlines()
        for topic in topics:
            if topic in dont_include:
                topics.remove(topic)
        return topics

    def total_words(self):
        """
        returns:
            - the total number of words spoken by each candidate
        """
        total = 0
        for part in self.participants:
            total += len(self.word_dict[part])  # sum up word_dict
        return total

    def words_by_candidate(self, candidate, analytics):
        """
        params:
            - candidate: a string indicating the selected candidate
            - analytics: a dictionary that stores analytics for candidates (key = candidate string)
        returns:
            - an updated analytics dictionary with the selected candidate's statistics
        """
        candidate_total = len(self.word_dict[candidate])
        total = self.total_words()
        percent = '%.2f%%' % ((candidate_total / float(total))*100)
        analytics[candidate] = (candidate_total, percent)
        return analytics

    def words_by_all_candidates(self):
        """
        returns: 
            - a dictionary of candidate analytics
        """
        analytics = {}
        for part in self.participants:
            analytics = self.words_by_candidate(part, analytics)
        return analytics

    def get_concordance(self, candidate, topic):
        """
        params: 
            - candidate: a string indicating the selected candidate
            - topic: a string to search for within a candidate's section of text
        returns: 
            - an nltk.Text concordance for the topic string from the selected candidate
        """
        my_text = self.text_dict[candidate.upper()]
        return my_text.concordance(topic, width=200, lines=100)

    def get_concordance_list(self, candidate, topic):
        """
        params:
            - candidate: a string indicating the selected candidate
            - topic: a string to search for within a candidate's section of text
        returns:
            - an nltk.Text concordance in python's built-in list format
        """
        my_text = self.text_dict[candidate.upper()]
        return my_text.concordance_list(topic, width=200, lines=100)

    def get_participants(self):
        """
        returns:
            - a list of participants' last names in all caps
        """
        return self.participants

    def get_moderators(self):
        """
        returns:
            - a list of moderators' last names in all caps
        """
        return self.moderators

    def get_people(self):
        """
        A support funciton that iterates over self.text, populating a list of people, using a regular expression to
        pick out words in all caps followed by a colon. Account for exceptions that should not be
        included (like CNN, PARTICIPANTS, etc.). Extract the sentences introducing the
        participants and moderators, and compare the list of people to these to compile and return
        two separate lists for participants and moderators.
        """
        people = []
        part_string = ''
        mod_string = ''
        speaker_pattern = re.compile(r'^.*[A-Z][A-Z]+$')
        # populate the people list
        i = 0
        while i < len(self.text):
            if speaker_pattern.match(self.text[i][0]) and self.text[i+1][0] == ':':
                name = self.text[i][0]
                if '.' in name:
                    # weird error with tokenizer, some are "word.TRUMP"
                    name_pattern = re.compile(r'^.*\.+([A-Z]+)$')
                    name_match = re.search(name_pattern, name)
                    try:
                        # get only name
                        name = name_match.group(1)  
                    except AttributeError:
                        # necessary for one of the debates, some weird error in the tagger...
                        i += 1  
                        continue
                exclude = ['PARTICIPANTS', 'MODERATORS', 'MODERATOR', 'PANELISTS', 'CNN', 'ClINTON']
                if name not in people and name not in exclude:
                    people.append(name)
            if self.text[i][0] == 'PARTICIPANTS':
                i += 2
                while not (speaker_pattern.match(self.text[i][0]) and self.text[i+1][0] == ':'):
                    part_string += self.text[i][0].lower() + ' '
                    i += 1
            if self.text[i][0] in ['MODERATOR', 'MODERATORS']:
                i += 2
                while not (speaker_pattern.match(self.text[i][0]) and self.text[i+1][0] == ':'):
                    mod_string += self.text[i][0].lower() + ' '
                    i += 1
            i += 1
        # find the participants and moderators
        parts = []
        mods = []
        for person in people:
            name = person.lower()
            if name in part_string.split():
                parts.append(name.upper())
            elif name in mod_string.split():
                mods.append(name.upper())
        # return both participants and moderators
        return parts, mods

    def parse_text(self):
        """
        A support function that creates the speak, word, and reaction dictionaries using self.candidates and self.moderators.
        Iterates through self.text keeping track of the current speaker. Adds each word said to the speaker's "wd" value (list), while
        incrementing the appropriate value (int) in "sd" every time the speaker changes. Keep track of reactions (in between []) in "rd".
        returns 
            - sd, wd, rd: dictionaries to support key analytics functions
        """
        sd = {}  # speak dictionary maps speaker (string) to # of times speaking (int)
        wd = {}  # word dictionary maps speaker (string) to list of words said ([strings])
        rd = {}  # reaction dictionary maps reaction (string) to occurrences (int)
        for mod in self.moderators:
            sd[mod] = 0
            wd[mod] = []
        for part in self.participants:
            sd[part] = 0
            wd[part] = []
        current_speaker = ''
        speaker_pattern = re.compile(r'^.*[A-Z][A-Z]+$')
        for i in range(len(self.text)):
            if speaker_pattern.match(self.text[i][0]) and self.text[i + 1][0] == ':':  # all caps followed by colon
                name = self.text[i][0]
                if '.' in name:  # weird error with tonkenizer, some are "word.TRUMP"
                    name_pattern = re.compile(r'^.*\.+([A-Z]+)$')
                    name_match = re.search(name_pattern, name)
                    try:
                        current_speaker = name_match.group(1)  # get only name
                    except AttributeError:
                        continue
                else:
                    current_speaker = name
                # Increment speaker's value in speak dictionary
                if current_speaker in sd:
                    sd[current_speaker] += 1
            elif self.text[i][0] == '[':  # elif its a reaction
                i += 1
                reaction = self.text[i][0]
                i += 1
                while self.text[i][0] != ']':  # find multi-word reactions
                    reaction += ' ' + self.text[i][0]
                    i += 1
                # Add to reaction dictionary
                if reaction in rd:
                    rd[reaction] += 1
                else:
                    rd[reaction] = 1
            else:  # else its a word, assign to speaker if not punctuation
                word_pattern = re.compile(r'^[A-Za-z]+-*[A-Za-z]*')
                word = self.text[i][0]
                if word_pattern.match(word):
                    # Add word to speaker's value (list) in word dictionary
                    if current_speaker in wd:
                        wd[current_speaker].append(word)
        return [sd, wd, rd]

    def analyze_topic_sentiment(self, candidate, concordance_list):
        """
        Analyzes the sentiment of a given candidate's topic concordance list using a "bag of words" 
        approach with nltk's built-in vader sentiment.
        params: 
            - candidate name
            - topic 
            - concordance_list
        returns: 
            - a dictionary of scored sentiments
        """
        # instantiate vader and the return analytics dict
        sia = SentimentIntensityAnalyzer()
        analytics = {}
        # clean the concordance list items into a python list with relevant data
        analysis = []
        for segment in concordance_list:
            analysis.append(list(segment)[0] + list(segment)[2])
        # score the entire comment with vader
        for comment in analysis:
            comment = ' '.join(word for word in comment)
            analytics[comment] = {}
            sentiment_dict = sia.polarity_scores(comment)
            analytics[comment]['overall_sentiment_dict'] = sentiment_dict
            analytics[comment]['negative'] = sentiment_dict['neg']*100
            analytics[comment]['neural'] = sentiment_dict['neu']*100
            analytics[comment]['positive'] = sentiment_dict['pos']*100
            # decide sentiment as positive, negative and neutral
            if sentiment_dict['compound'] >= 0.05 :
                analytics[comment]['overall'] = 'Positive'
            elif sentiment_dict['compound'] <= - 0.05 :
                analytics[comment]['overall'] = 'Negative'
            else :
                analytics[comment]['overall'] = 'Neutral'
        return analytics

    def score_sentiments(self, concordance_list):
        """
        Function that scores sentiment using a neural network approach. Hugging Face
        transformers is utilized with pytorch.
        params:
            - concordance_list: a python list generated from get_concordance_list
        returns: 
            - a dictionary of scored sentiments for a given list of comments
        """
        MODEL = f'cardiffnlp/twitter-roberta-base-sentiment'
        tokenizer = AutoTokenizer.from_pretrained(MODEL)
        model = AutoModelForSequenceClassification.from_pretrained(MODEL)
        sentiments = {'Negative': 0, 'Neutral': 0, 'Positive': 0}
        avg_sent = {'Negative': 0, 'Neutral': 0, 'Positive': 0}
        sorted_comments = {'Negative': [], 'Neutral': [], 'Positive': []}
        # clean the concordance list items into a python list with relevant data
        analysis = []
        for segment in concordance_list:
            analysis.append(list(segment)[0] + list(segment)[2])
        for comment in analysis:
            comment = ' '.join(word for word in comment)
            encoded_text = tokenizer(comment, return_tensors='pt')
            output = model(**encoded_text, output_hidden_states=True)
            scores = output[0][0].detach().numpy()
            scores = softmax(scores)
            sentiment = {
                'Negative': scores[0],
                'Neutral': scores[1],
                'Positive': scores[2]
            }
            avg_sent['Negative'] += sentiment['Negative']
            avg_sent['Neutral'] += sentiment['Neutral']
            avg_sent['Positive'] += sentiment['Positive']
            if sentiment['Positive'] - sentiment['Negative'] > 0:
                sentiments['Positive'] += 1
                sorted_comments['Positive'].append(comment)
            elif sentiment['Positive'] - sentiment['Negative'] < 0:
                sentiments['Negative'] += 1
                sorted_comments['Negative'].append(comment)
            else:
                sentiments['Neutral'] += 1
                sorted_comments['Neutral'].append(comment)
        avg_sent['Negative'] = (avg_sent['Negative'] / len(analysis)).item()
        avg_sent['Neutral'] = (avg_sent['Neutral'] / len(analysis)).item()
        avg_sent['Positive'] = (avg_sent['Positive'] / len(analysis)).item()
        return (avg_sent, sentiments, sorted_comments)
        

class TwitterTools:
    """
    # TODO: Review API config and utiliization in a notebook for 2028.
    """
    def __init__(self, auth, api):
        """
        encapsulate use of the tweepy API.
        """
        # ---------------------------------------------------------------- #
        # rest api config
        # ---------------------------------------------------------------- #
        
        # TODO: create updated .env file and configure in notebook
        # auth = tweepy.OAuthHandler(config.CONSUMER_KEY, config.CONSUMER_SECRET)
        # auth.set_access_token(config.ACCESS_TOKEN, config.ACCESS_TOKEN_SECRET)
        # self.api = tweepy.API(auth)
        self.candidate_twitters = {
            "TRUMP": "@realDonaldTrump", 
            "BIDEN": "@JoeBiden", 
            "HARRIS": "@KamalaHarris"
        }

    def extract_features(self, tweet):
        """
        # features = this list is proprietary 🕵🏻 🔐 []
        words = tweet.split()
        tweet_feats = {}
        for feature in features:
            tweet_feats[feature[0]] = False
            for word in words:
                if word.lower() in feature[1]:
                    tweet_feats[feature[0]] = True
        return tweet_feats
        """
        return tweet
        
    def candidate_mentions(self, topic, candidate):
        topic += '@%s-filter:retweets' % candidate_twitters[candidate]
        # tweepy deprecated the ability to search all tweets since we made this project
        results = api.search_recent_tweets(q=topic, count=200)
        return results

    def get_top_five(self, tweets):
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
    
    def get_hashtags(self, tweets):
        hashtags = []
        for tweet in tweets:
            for word in tweet.text.split(" "):
                try:
                    if word[0] == "#" and word not in hashtags:
                        hashtags.append(word)
                except IndexError:
                    continue
        return hashtags
        
    def bayes_classify(self, tweets):
        """
        Function that explores the use of a "naive bayes" classifier algorithm. Set up to 
        be trained on the sampleTweets.txt file. This file contains a 1 or 0 (positive or negative) 
        on each line, along with a tweet. Use the classifier to figure out a percentage of positive 
        tweets.
        """
        with open('support_functions/text_files/sampleTweets.txt', 'r') as fh:
            text = fh.readlines()
        sents = []
        for line in text:
            lines = line.split('   ')
            sents.append((lines[1], lines[0]))
        random.shuffle(sents)
        test_sents = sents[80:]
        train_sents = sents[:80]
        test_set = [(self.extract_features(t), s) for (t, s) in test_sents]
        train_set = [(self.extract_features(t), s) for (t, s) in train_sents]
        classifier = nltk.NaiveBayesClassifier.train(train_set)
        print("NBC Accuracy: " + str(nltk.classify.accuracy(classifier, test_set)))
        tweet_set = [self.extract_features(t) for t in tweets]
        sentiments = classifier.classify_many(tweet_set)
        positive = 0
        for sent in sentiments:
            if sent == '1':
                positive += 1
        try:
            percent = (positive/float(len(sentiments)))*100
        except ZeroDivisionError:
            percent = 0
        print("We estimate that %.2f percent of tweets are positive toward this issue." % percent)