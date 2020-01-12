'''
NLP library
'''

from collections import OrderedDict
from typing import List, Optional

import spacy
import numpy as np
import pandas as pd


_SPACY_LANG_PACK = 'en_core_web_sm'


def make_sentences(document: str) -> List:
    '''
    Returns a list of sentences for a given document
    '''
    nlp = spacy.load(_SPACY_LANG_PACK)
    return [s.text for s in nlp(document).sents]


class LSA:
    '''
    Latent semantic analysis
    '''

    _POS = ['PROPN', 'NOUN']

    def __init__(self, doclist: List, vocab: Optional[List] = None):
        self._nlp = spacy.load(_SPACY_LANG_PACK)
        self._doclist = doclist
        self._vocabulary = vocab if vocab is not None else self._calculate_vocab()

    def get_occurrence_matrix(self) -> pd.DataFrame:
        '''
        Creates an occurence matrix using a list of documents and a vocabulary
        '''
        matrix = pd.DataFrame()

        for d in self._doclist:
            embedding = self._get_embedding(d)
            matrix = matrix.append(embedding)

        return matrix.transpose()

    def get_similarity(self, doc, occurence_matrix) -> List:
        '''
        ARGS:
            doc: The doc to be compared
            occurrence_matrix: The document to be compared against
        RETURNS:
            List: Similarity score for each document

        Calculculates similarity between a document and an occurence matrix
        and returns a list of similarity scores for each document
        '''
        embedding = self._get_embedding(doc)
        return embedding.dot(occurence_matrix.transpose())  # Since columns represent the embeddings

    def _calculate_vocab(self):
        docstr = ' '.join(self._doclist)
        doc = self._nlp(docstr)
        vocab = [token.text for token in doc if token.pos_ in self._POS]
        return vocab

    def _get_embedding(self, doc: str) -> pd.Series:
        tokens = [t.text for t in self._nlp(doc)]
        return pd.Series({v: tokens.count(v) for v in self._vocabulary}, name=doc)
