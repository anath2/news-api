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
    _SVD_RANK = 3

    def __init__(self, doclist: List, svd_rank: int = 3, vocab: Optional[List] = None):
        self._nlp = spacy.load(_SPACY_LANG_PACK)
        self._doclist = doclist
        self._vocabulary = vocab if vocab is not None else self._calculate_vocab()
        self._svd_rank = svd_rank

    def get_occurrence_matrix(self) -> pd.DataFrame:
        '''
        RETURNS:
            An occurrence matrix of the form :

            d1  d2  d3 ...
            -------------------------------
        t1
        t2
        t3
        ...

        Creates an occurence matrix using a list of documents and a vocabulary
        An occurrence matrix consists of rows representing terms in the vocabulary and
        columns indicating documents. Entries of the matrix represent the frequency of
        terms in the corresponding documents
        '''
        matrix = pd.DataFrame()

        for d in self._doclist:
            embedding = self._get_embedding(d)
            matrix = matrix.append(embedding)

        return matrix.transpose()

    def get_related_keywords(self, doc: str, occurence_matrix: pd.DataFrame) -> List:
        '''
        Get top keywords related to the document to compared with the rest of the
        corpus
        '''
        similarity_scores = self.get_similarity(doc, occurence_matrix)
        rounded = similarity_scores.apply(lambda x: round(x, 2))
        top = rounded[rounded > 0]
        docs = top.index
        return [t.text for t in self._nlp(' '.join(docs)) if t.pos_ in self._POS]

    def get_similarity(self, doc: str, occurence_matrix: pd.DataFrame) -> pd.Series:
        '''
        ARGS:
            doc: The doc to be compared
            occurrence_matrix: The document to be compared against

        RETURNS:
            A series with similairity scores

        Calculculates similarity between a document and an occurence matrix
        and returns a list of similarity scores for each document
        '''
        U, s, Vt = self._calculate_svd(occurence_matrix)
        V = Vt.transpose()
        S = np.zeros((len(s), len(s),))
        np.fill_diagonal(S, s)

        U_red = U[:, :self._svd_rank]
        S_red = S[:self._svd_rank, :self._svd_rank]
        V_red = V[: , :self._svd_rank]
        Vt_red = V_red.transpose()

        embedding = self._get_embedding(doc)
        embedding_red = np.dot(np.dot(embedding, U_red), np.linalg.inv(S_red))   # Q^t . U . S^-1

        scores = []
        for row in V_red:
            cosine = np.dot(embedding_red, row) / np.linalg.norm(embedding_red) * np.linalg.norm(row)
            scores.append(cosine)

        return pd.Series(scores, index=occurence_matrix.columns, name='Similairity')  # Since order of documents is preserved




    def _calculate_svd(self, matrix):
        array = matrix.to_numpy(dtype='int32')
        U, S, Vt = np.linalg.svd(array, full_matrices=False)
        return U, S, Vt

    def _calculate_vocab(self):
        docstr = ' '.join(self._doclist)
        doc = self._nlp(docstr)
        vocab = [token.text for token in doc if token.pos_ in self._POS]
        return vocab

    def _get_embedding(self, doc: str) -> pd.Series:
        tokens = [t.text for t in self._nlp(doc)]
        return pd.Series({v: tokens.count(v) for v in self._vocabulary}, name=doc)
