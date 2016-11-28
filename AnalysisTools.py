import nltk
import re
from cStringIO import StringIO
import sys

"""
Debate analyzer project ("Make AI Great Again")
AnalysisTools class
-- methods used to analyze clean debate transcripts

Dylan Telford, Preston Mackert, Alexis Grebenok, Jerry Daigler
10/26/16
"""


class Capturing(list):
    """
    Taken from Stack Overflow user kindall. Used because collocations in nltk have an output that results in a None,
    this allows us to save the collocations to get topics.

    Link to code: http://stackoverflow.com/questions/16571150/how-to-capture-stdout-output-from-a-python-function-call
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
    """ Take in a nltk.Text object and run analysis methods on it """
    def __init__(self, text):
        """
        Set up data structures for use by methods. Call to the get_people method to set up
        the lists of participants and moderators. Call to the parse_text method to set up  and
        populate the speak, word, and reaction dictionaries. Use participants and word_dict to
        set up text_dict to use for concordances
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

        with open("dontInclude.txt") as fh:
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

    def words_by_candidate(self, candidate):
        """
        returns a string describing how many words (and what percent of the total)
        a given candidate spoke
        """
        candidate_total = len(self.word_dict[candidate])
        total = self.total_words()
        percent = '%.2f%%' % ((candidate_total / float(total))*100)
        return '%s spoke %d words (%s of the total words spoken by the candidates)' % (candidate, candidate_total,
                                                                                       percent)

    def words_by_all_candidates(self):
        """
        returns a multi-line string with as many lines as candidates, where each
        line is the result of a call to words_by_candidates() with a candidate
        """
        answer = ''
        for part in self.participants:
            answer += self.words_by_candidate(part) + '\n'
        return answer

    def get_concordance(self, candidate, topic):
        """
        given a candidate's last name and a one-word topic, this returns an nltk.Text
        concordance for that word from the Text object corresponding to that candidate
        """
        my_text = self.text_dict[candidate.upper()]
        return my_text.concordance(topic, width=200, lines=100)

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

    def make_concordance(self, candidate, topic):
        """
        iterate over self.text, searching for the word or a list of words in onder.
        if found, backtrack until you find the start of the sentence, record index,
        look ahead until you find period, join into a string and save in list.
        *** NOT WORKING RIGHT NOW, JUST USING NLTK.TEXT.CONCORDANCE() ***
        """
        my_text = self.text_dict[candidate]
        print my_text
        results = []
        topic_list = topic.split()
        multi_word = True
        if len(topic_list) == 1:
            multi_word = False
        for i in range(len(my_text)):
            if my_text[i].lower() == topic_list[0].lower():
                match = True
                if multi_word:
                    j = 1
                    while j < len(topic_list):
                        if my_text[i+j].lower() != topic_list[j].lower():
                            match = False
                if not match:
                    continue
                start = i
                end = i+1
                while my_text[start] != '.':
                    start -= 1
                while my_text[end] != '.':
                    end += 1
                start += 1
                end += 1
                sent_list = my_text[start:end]
                """
                tuple_list = my_text[start:end]
                sent_list = []
                for tup in tuple_list:
                    sent_list.append(tup[0])
                """
                sent = ' '.join(sent_list)
                results.append(sent)
        answer = ''
        for result in results:
            answer += '%s\n' % result
        return answer

    def get_people(self):
        """
        iterates over self.text, populating a list of people, using a regular expression to
        pick out words in all caps followed by a colon. Account for exceptions that should not be
        included (like CNN, PARTICIPANTS, etc.). Then, extract the sentences introducing the
        participants and moderators, and compare the list of people to these to compile and return
        two separate lists for participants and moderators
        """
        people = []
        part_string = ''
        mod_string = ''
        speaker_pattern = re.compile(r'^.*[A-Z][A-Z]+$')
        i = 0
        while i < len(self.text):
            if speaker_pattern.match(self.text[i][0]) and self.text[i+1][0] == ':':
                name = self.text[i][0]
                if '.' in name:
                    name_pattern = re.compile(r'^.*\.+([A-Z]+)$')  # weird error with tokenizer, some are "word.TRUMP"
                    name_match = re.search(name_pattern, name)
                    try:
                        name = name_match.group(1)  # get only name
                    except AttributeError:
                        i += 1  # necessary for one of the debates, some weird error in the tagger...
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
        parts = []
        mods = []
        for person in people:
            name = person.lower()
            if name in part_string.split():
                parts.append(name.upper())
            elif name in mod_string.split():
                mods.append(name.upper())
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
