#!/usr/bin/env python
import nltk
import re
"""
AnalysisTools class for Make-AI-Great-Again

methods used to analyze clean debate transcripts

"""


class AnalysisTools:
    def __init__(self, text):
        """Take in a nltk.Text object to run analysis methods on"""
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

    def total_words(self):
        total = 0
        for part in self.participants:
            total += len(self.word_dict[part])
        return total

    def words_by_candidate(self, candidate):
        candidate_total = len(self.word_dict[candidate])
        total = self.total_words()
        percent = '%.2f%%' % ((candidate_total / float(total))*100)
        return '%s spoke %d words (%s of the total words spoken by the candidates)' % (candidate, candidate_total,
                                                                                       percent)

    def words_by_all_candidates(self):
        answer = ''
        for part in self.participants:
            answer += self.words_by_candidate(part) + '\n'
        return answer

    def get_concordance(self, candidate, topic):
        my_text = self.text_dict[candidate]
        return my_text.concordance(topic)

    def get_participants(self):
        return self.participants

    def get_moderators(self):
        return self.moderators

    def get_people(self):
        people = []
        part_string = ''
        mod_string = ''
        speaker_pattern = re.compile(r'^.*[A-Z][A-Z]+$')
        i = 0
        while i < len(self.text):
            if speaker_pattern.match(self.text[i][0]) and self.text[i+1][0] == ':':
                name = self.text[i][0]
                if '.' in name:  # might be causing error where it enters but does not match second expression
                    name_pattern = re.compile(r'^.*\.+([A-Z]+)$')  # weird error with tonkenizer, some are "word.TRUMP"
                    name_match = re.search(name_pattern, name)
                    try:
                        name = name_match.group(1)  # get only name
                    except AttributeError:
                        i += 1
                        continue
                exclude = ['PARTICIPANTS', 'MODERATORS', 'MODERATOR', 'PANELISTS', 'CNN']
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
        return (parts, mods)

    def parse_text(self):
        sd = {}  # speak dictionary
        wd = {}  # word dictionary
        rd = {}  # reaction dictionary
        for mod in self.moderators:
            sd[mod] = 0
            wd[mod] = []
        for part in self.participants:
            sd[part] = 0
            wd[part] = []
        current_speaker = ''
        speaker_pattern = re.compile(r'^.*[A-Z][A-Z]+$')
        for i in range(len(self.text)):
            if speaker_pattern.match(self.text[i][0]) and self.text[i + 1][0] == ':':  # if its a new speaker, change current speaker
                name = self.text[i][0]
                if '.' in name:
                    name_pattern = re.compile(r'^.*\.+([A-Z]+)$')  # weird error with tonkenizer, some are "word.TRUMP"
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