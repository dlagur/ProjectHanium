# -*- coding: utf-8 -*-
"""ExtractiveSummarization.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/github/dlagur/ProjectHanium/blob/main/ExtractiveSummarization.ipynb
"""

!pip install jpype1
!pip install konlpy

from konlpy.tag import Kkma
from konlpy.tag import Twitter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import normalize
import numpy as np

kkma = Kkma() # text를 문장단위로 나눈다

def text2sentences(text):
    sentences = kkma.sentences(text)
    for idx in range(0, len(sentences)):
        if len(sentences[idx]) <= 10:
            sentences[idx-1] += (' ' + sentences[idx])
            sentences[idx] = ''
    return sentences

import pandas as pd

text = pd.read_csv('/content/IT_0.csv')

text

sentences = text2sentences(text['answer'][0])

sentences[0]

twitter = Twitter()

# 불용어 제거

stopwords = ['글자수', '000', '또한', '저는', '있습니다', '그리고', '이러한', '거나', '자수', '통해', '이후', '당시', '대한', '때문 ']

def get_nouns(sentences):
    nouns = []
    for sentence in sentences:
        if sentence is not '':
            nouns.append(' '.join([noun for noun in twitter.nouns(str(sentence)) if noun not in stopwords and len(noun) > 1]))
    return nouns

nouns = get_nouns(sentences)

nouns

nouns

"""## TF-IDF 모델 생성 및 그래프 생성"""

tfidf = TfidfVectorizer()
cnt_vec = CountVectorizer()
graph_sentence = []

def build_sent_graph(sentence):
    tfidf_mat = tfidf.fit_transform(sentence).toarray()
    graph_sentence = np.dot(tfidf_mat, tfidf_mat.T)
    return graph_sentence

sent_graph = build_sent_graph(nouns) # 요약할 문장 단위에 대한 sentence graph 생성

def build_words_graph(sentence):
    cnt_vec_mat = normalize(cnt_vec.fit_transform(sentence).toarray().astype(float), axis =0)
    vocab = cnt_vec.vocabulary_
    return np.dot(cnt_vec_mat.T, cnt_vec_mat), {vocab[word] : word for word in vocab}

words_graph, idx2word = build_words_graph(nouns)

words_graph

idx2word

"""### 순서

1.   위에서 구한 가중치 그래프 이용 TextRank 알고리즘에 넣어 점수 매기기
2.   순위가 높은 순서대로 정렬
3.   요약할 문장의 개수만큼 출력


"""

def get_ranks(graph, d=0.85): # d = damping factor
    A = graph
    matrix_size = A.shape[0]
    for id in range(matrix_size):
        A[id, id] = 0 # diagonal 부분을 0으로
        link_sum = np.sum(A[:,id]) # A[;, id] = A[:][id]
        if link_sum != 0:
            A[:, id] /= link_sum
        A[:, id] *= -d
        A[id, id] = 1
        
    B = (1-d) * np.ones((matrix_size, 1))
    ranks = np.linalg.solve(A, B) # 연립방정식 Ax = b
    return {idx : r[0] for idx, r in enumerate(ranks)}

# sent_rank_idx = get_ranks(sent_graph) # sent_graph = sentence 가중치 그래프
word_rank_idx = get_ranks(words_graph)

# sorted_sent_rank_idx = sorted(sent_rank_idx, key=lambda k: sent_rank_idx[k], reverse=True)
sorted_word_rank_idx = sorted(word_rank_idx, key=lambda k : word_rank_idx[k], reverse=True)

# 요약할 문장의 수를 입력하면 그 문장의 개수만큼 요약

def summarize(sent_num=5): # 기본 5개의 문장으로 텍스트를 요약
    summary = []
    index = []
    for idx in sorted_sent_rank_idx[:sent_num]:
        index.append(idx)
    
    index.sort()

    for idx in index:
        summary.append(sentences[idx])

    for text in summary:
        print(text)
        print('\n')

text['answer'][0]

def keywords(word_num=10):

    keywords = []
    index = []
    for idx in sorted_word_rank_idx[:word_num]:
        index.append(idx)

    # index.sort()
    for idx in index:
        keywords.append(idx2word[idx])

    print(keywords)

keywords()