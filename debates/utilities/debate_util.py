"""
This utility file provides funcitons that are consumed by the 
notebooks to abstract complexity away from the visuals and text.

Introduced Vader, but look to continue training - look at some 
additioal value in plotting and graphing some of the more interesting
findings.

@author Preston Mackert
"""

# ---------------------------------------------------------------- #
# libraries
# ---------------------------------------------------------------- #

import sys
import re
import nltk
import random
from io import StringIO
from bs4 import BeautifulSoup
from urllib.request import urlopen
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# ---------------------------------------------------------------- #
# clean html
# ---------------------------------------------------------------- #

def clean_and_tag(url):
    """ 
    params: url
    return: text object with tagged_tokens 
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
    params: tokens
    return: cleaned token list 
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
    params: list
    return: cleaned list
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
        Instantiate data structures that will be populated by methods. Pre-populates the participants and 
        moderators based on the url. Using an assertion, the nltk.Text object is passed into the parse_text 
        method to populate initial word dictionaries for analysis.
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
        returns a list of topics for the candidates
        """
        txt = nltk.Text(self.word_dict[candidate])
        with Capturing() as collocations:
            txt.collocations()
        all_colls = ""
        for item in collocations:
            all_colls += " " + item
        all_colls = all_colls[1:]
        topics = all_colls.split("; ")

        with open("support_functions/text_files/dontInclude.txt") as fh:
            dont_include = fh.read().splitlines()

        for topic in topics:
            if topic in dont_include:
                topics.remove(topic)

        return topics


    def total_words(self):
        """
        returns the total number of words spoken by the group of candidates
        """
        total = 0
        for part in self.participants:
            total += len(self.word_dict[part])  # sum up word_dict
        return total


    def words_by_candidate(self, candidate, analytics):
        """
        returns a string describing how many words (and what percent of the total)
        a given candidate spoke
        """
        candidate_total = len(self.word_dict[candidate])
        total = self.total_words()
        percent = '%.2f%%' % ((candidate_total / float(total))*100)
        analytics[candidate] = (candidate_total, percent)
        return analytics
        


    def words_by_all_candidates(self):
        """
        returns a multi-line string with as many lines as candidates, where each
        line is the result of a call to words_by_candidates() with a candidate
        """
        analytics = {}
        for part in self.participants:
            analytics = self.words_by_candidate(part, analytics)
        return analytics


    def get_concordance(self, candidate, topic):
        """
        given a candidate's last name and a one-word topic, this returns an nltk.Text
        concordance for that word from the Text object corresponding to that candidate
        """
        my_text = self.text_dict[candidate.upper()]
        return my_text.concordance(topic, width=200, lines=100)

    def get_concordance_list(self, candidate, topic):
        """
        given a candidate's last name and a one-word topic, this returns an nltk.Text
        concordance in list format
        """
        my_text = self.text_dict[candidate.upper()]
        return my_text.concordance_list(topic, width=200, lines=100)


    def get_participants(self):
        """
        returns a list of participants' last names in all caps
        """
        return self.participants


    def get_moderators(self):
        """
        returns a list of moderators' last names in all caps
        """
        return self.moderators


    def get_people(self):
        """
        Iterates over self.text, populating a list of people, using a regular expression to
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
        create the speak, word, and reaction dictionaries using self.candidates and self.moderators.
        Iterate through self.text with a state machine, keeping track of the current
        speaker. Add each word said to the speaker's wd value (list), while incrementing the appropriate
        value (int) in sd every time the speaker changes. Keep track of reactions (in between []) in rd.
        return the three dictionaries in a list
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


    def bayes_classify(self, tweets):
        """
        create a Naive Bayes Classifier, trained on the sampleTweets.txt file which
        contains a 1 or 0 (positive or negative) on each line, along with a tweet.
        Use classifier to figure out percentage of positive tweets sent as argument.
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


    def extract_features(self, tweet):
        """
        defines features for tweets based on what words the tweets contain.
        """
        features = [('hasGood', ('good', 'satisfy', 'well', 'nice')),
                    ('hasGreat', ('great', 'terrific', 'awesome', 'fantastic')),
                    ('hasBad', ('bad', 'boo', 'poor', 'lame')),
                    ('hasTerrible', ('terrible', 'awful', 'shameful', 'despicable')),
                    ('hasLiar', ('lie', 'liar', 'untrustworthy', 'dishonest')),
                    ('hasCriminal', ('criminal', 'crime', 'prison', 'lock')),
                    ('hasCrooked', ('crooked', 'crook', 'corrupt')),
                    ('hasRacist', ('racist', 'race')),
                    ('hasDumb', ('dumb', 'stupid', 'idiot', 'fool', 'retard', 'moron')),
                    ('hasBias', ('bias', 'interest', 'skewed', 'collude', 'collusion')),
                    ('hasPussy', ('pussy', 'grab', 'pussy grabber', 'rape', 'rapist')),
                    ('swears', ('fuck', 'fucking', 'fucker', 'shit', 'ass', 'bitch', 'bastard', 'dick')),
                    ('hasDevil', ('devil', 'demonic', 'satan', 'satanic', 'demon')),
                    ('hasMis', ('mistake', 'misguided', 'mislead', 'misunderstood', 'misunderstands')),
                    ('hasChina', ('china', 'chinese')),
                    ('hasMiddleEast', ('middle', 'syria', 'aleppo', 'saudi', 'arabia', 'iran', 'iraq', 'afghanistan')),
                    ('hasLike', ('like', 'love', 'admire')),
                    ('hasThank', ('thank', 'thanks')),
                    ('hasTrade', ('trade', 'trading', 'deals', 'nafta')),
                    ('hasLol', ('lol', 'haha', 'hahaha', 'hahahaha', 'joke')),
                    ('hasCant', ("can't", "don't", "won't")),
                    ('hasFix', ('fix', 'fixed', 'fixing')),
                    ('hasJobs', ('job', 'jobs')),
                    ('hasWin', ('win', 'winning', 'winner')),
                    ('hasLose', ('lose', 'losing', 'loser'))]
        words = tweet.split()
        tweet_feats = {}
        for feature in features:
            tweet_feats[feature[0]] = False
            for word in words:
                if word.lower() in feature[1]:
                    tweet_feats[feature[0]] = True
        return tweet_feats

    def analyze_topic_sentiment(self, candidate, concordance_list):
        """
        analyzes the sentiment of a given candidate's topic concordance.
        params: candidate name, topic concordance list
        return: analytics dictionary
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

    