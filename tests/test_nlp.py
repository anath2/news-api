'''
Tests nlp functions
'''

import pytest
import pandas as pd

from news_api import nlp


@pytest.fixture
def news_story(news_data):
        first, *_ = news_data.items()
        title, doc = first
        return {'title': title, 'text': doc}


class TestLsa:

    def test_get_occurence_matrix(self, news_story):
        sentences = nlp.make_sentences(news_story['text'])
        lsa = nlp.LSA(sentences)
        matrix = lsa.get_occurrence_matrix()
        assert isinstance(matrix, pd.DataFrame)

    def test_get_similarity(self, news_story):
        headline = news_story['title']
        story = news_story['text']

        sentences = nlp.make_sentences(story)
        lsa = nlp.LSA(sentences)
        matrix = lsa.get_occurrence_matrix()
        similarity_scores = lsa.get_similarity(headline, matrix)
        assert isinstance(similarity_scores, pd.Series)
        print(similarity_scores)
