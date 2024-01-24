# -*- coding: utf-8 -*-
"""
Created on Jan 21 2023
@author: JIANG Yuxin
"""

from pdtb2 import CorpusReader
import argparse
import os
import sys


top_senses = set(['Temporal', 'Comparison', 'Contingency', 'Expansion'])
selected_second_senses = set([
    'Temporal.Asynchronous',
    'Temporal.Synchronous',
    'Contingency.Cause',
    'Contingency.Cause+Belief',
    'Contingency.Condition',
    'Contingency.Purpose',
    'Comparison.Contrast',
    'Comparison.Concession',
    'Expansion.Conjunction',
    'Expansion.Equivalence',
    'Expansion.Instantiation',
    'Expansion.Level-of-detail',
    'Expansion.Manner',
    'Expansion.Substitution',
])


def preprocess(splitting):
    train_sec = []
    dev_sec = []
    test_sec = []
    # following Ji, for 4-way and 11-way
    if splitting == 1:
        train_sec = ['2.0', '3.0', '4.0', '5.0', '6.0', '7.0', '8.0', '9.0', '10.0', '11.0',
                     '12.0', '13.0', '14.0', '15.0', '16.0', '17.0', '18.0', '19.0', '20.0']
        dev_sec = ['0.0', '1.0']
        test_sec = ['21.0', '22.0']

    # following Lin, for 4-way and 11-way
    elif splitting == 2:
        train_sec = [
            '2.0', '3.0', '4.0', '5.0', '6.0', '7.0', '8.0', '9.0', '10.0', '11.0',
            '12.0', '13.0', '14.0', '15.0', '16.0', '17.0', '18.0', '19.0', '20.0', '21.0',
        ]
        dev_sec = ['22.0']
        test_sec = ['23.0']

    # instances in 'selected_second_senses'
    arg1_train = []
    arg2_train = []
    sense1_train = []    # top, second, connective
    sense2_train = []    # None, None, None

    arg1_dev = []
    arg2_dev = []
    sense1_dev = []
    sense2_dev = []

    arg1_test = []
    arg2_test = []
    sense1_test = []
    sense2_test = []

    os.chdir(sys.path[0])
    for corpus in CorpusReader('./raw/complete.tsv').iter_data():
        if corpus.Relation != 'Implicit':
            continue
        #Make sure to have same CSV fields. e.g ConnHeadSemClass1, Section, Conn2SemClass1
        #
        #My CSV file fields:
        #
        #Relation, Conn1, ConnHeadSemClass1, Conn2, SemClass1, Arg1, Arg2,	Section	

        
        sense_split = corpus.ConnHeadSemClass1.split('.')
        sense_l2 = '.'.join(sense_split[0:2])
        if sense_l2 in selected_second_senses:
            arg1 = corpus.Arg1
            arg2 = corpus.Arg2
            if str(corpus.Section) in train_sec:
                arg1_train.append(arg1)
                arg2_train.append(arg2)
                sense1_train.append([sense_split[0], sense_l2, corpus.Conn1])
                sense2_train.append([None, None, None])
            elif str(corpus.Section) in dev_sec:
                arg1_dev.append(arg1)
                arg2_dev.append(arg2)

                sense1_dev.append([sense_split[0], sense_l2, corpus.Conn1])
            elif str(corpus.Section) in test_sec:
                arg1_test.append(arg1)
                arg2_test.append(arg2)
                sense1_test.append([sense_split[0], sense_l2, corpus.Conn1])

            else:
                continue
            #Make sure to have same CSV fields. e.g ConnHeadSemClass1, Section, Conn2SemClass1
            if str(corpus.Conn2) != '':
                sense_split = corpus.Conn2SemClass1.split('.')
                sense_l2 = '.'.join(sense_split[0:2])
                if sense_l2 in selected_second_senses:
                    if str(corpus.Section) in train_sec:
                        arg1_train.append(arg1)
                        arg2_train.append(arg2)
                        sense1_train.append(
                            [sense_split[0], sense_l2, corpus.Conn2])
                        sense2_train.append([None, None, None])
                    elif str(corpus.Section) in dev_sec:
                        sense2_dev.append(
                            [sense_split[0], sense_l2, corpus.Conn2])
                    elif str(corpus.Section) in test_sec:
                        sense2_test.append(
                            [sense_split[0], sense_l2, corpus.Conn2])
            else:
                if str(corpus.Section) in dev_sec:
                    sense2_dev.append([None, None, None])
                elif str(corpus.Section) in test_sec:
                    sense2_test.append([None, None, None])

    assert len(arg1_train) == len(arg2_train) == len(
        sense1_train) == len(sense2_train)
    assert len(arg1_dev) == len(arg2_dev) == len(sense1_dev) == len(sense2_dev)
    assert len(arg1_test) == len(arg2_test) == len(
        sense1_test) == len(sense2_test)
    print('train size:', len(arg1_train))
    print('dev size:', len(arg1_dev))
    print('test size:', len(arg1_test))

    if splitting == 1:
        pre = './PDTB3/Ji//data//'
    elif splitting == 2:
        pre = './PDTB3/Lin//data//'

    with open(pre + 'train.txt', 'w') as f:
        for arg1, arg2, sense1, sense2 in zip(arg1_train, arg2_train, sense1_train, sense2_train):
            print('{} ||| {} ||| {} ||| {}'.format(
                sense1, sense2, ' '.join(arg1.split()), ' '.join(arg2.split())), file=f)
    with open(pre + 'dev.txt', 'w') as f:
        for arg1, arg2, sense1, sense2 in zip(arg1_dev, arg2_dev, sense1_dev, sense2_dev):
            print('{} ||| {} ||| {} ||| {}'.format(
                sense1, sense2, ' '.join(arg1.split()), ' '.join(arg2.split())), file=f)
    with open(pre + 'test.txt', 'w') as f:
        for arg1, arg2, sense1, sense2 in zip(arg1_test, arg2_test, sense1_test, sense2_test):
            print('{} ||| {} ||| {} ||| {}'.format(
                sense1, sense2, ' '.join(arg1.split()), ' '.join(arg2.split())), file=f)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', dest='func',
                        choices=['pre', 'test'], type=str, default='pre')
    # 1 for 'Ji', 2 for 'Lin'
    parser.add_argument('-s', dest='splitting',
                        choices=[1, 2], type=int, default='1')
    A = parser.parse_args()
    preprocess(A.splitting)
