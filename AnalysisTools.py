#!/usr/bin/env python
"""
AnalysisTools class for Make-AI-Great-Again

methods used to analyze clean debate transcripts

"""

import nltk

class AnalysisTools:
    def __init__(self, text):
        """Take in a nltk.Text object to run analysis methods on"""
        assert isinstance(text, nltk.Text)
        self.text = text