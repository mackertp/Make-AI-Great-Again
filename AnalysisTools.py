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
                if '.' in name:
                    name_pattern = re.compile(r'^.*\.+([A-Z]+)$')  # weird error with tonkenizer, some are "word.TRUMP"
                    name_match = re.search(name_pattern, name)
                    try:
                        name = name_match.group(1)  # get only name
                    except AttributeError:
                        i += 1
                        continue
                exclude = ['PARTICIPANTS', 'MODERATORS', 'MODERATOR', 'PANELISTS']
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