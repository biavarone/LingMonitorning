# -*- coding: utf-8  -*-
# !/usr/bin/python

import codecs
import sys
from hashlib import md5
from utils import vectorize
from senttok import Sentence, Token
from compute_features import compute_features


def read_file(input_file):
    """
    Reads the input file and build a data structure containing a list of documents (or sentences?)

    :param input_file: (string) path to input file
    :return: ([[Sentence]]) list of documents in file
    """
    # sentences = []
    sentences = {}
    sentence = []
    # identifiers = []

    with codecs.open(input_file, 'r', 'utf-8') as f:
        for line in f:
            if line == '\n' and sentence:
                mysent = Sentence(sentence)  # Create an object Sentence
                # Create identifier
                m = md5()
                identifier = ''
                for token in sentence:
                    identifier += token.form + ' '
                m.update(identifier.encode('utf-8')[:-1])
                sentences[m.hexdigest()] = mysent
                sentence = []
            elif line == '\n':  # Skip blank lines
                pass
            elif line.startswith('#'):
                pass

            # If a line of text is found, divide it in tokens and create a Token() object
            # Note: text is TAB-separated
            else:
                line = line.strip().split('\t')
                if '-' in line[0]:
                    pass
                else:
                    sentence.append(Token(line))

        if sentence:
            mysent = Sentence(sentence)
            m = md5()
            identifier = ""
            for token in sentence:
                identifier += token.form + " "
            m.update(identifier.encode('utf-8'))
            sentences[m.hexdigest()] = mysent

    return sentences


def read_dictionary(dict_file):
    """
    Reads the dictionary file and builds a dict

    :param dict_file: (string) path to dictionary file
    :return: (dict) dictionary
    """
    dictionary = {}
    with codecs.open(dict_file, 'r', 'utf-8') as f:
        for line in f:
            line = line.strip().split('\t')
            dictionary[line[0]] = line[1].strip()
    return dictionary


def read_and_compute(input_file, *fund_dictionary):

    sentences = read_file(input_file)  # Reads input file in CoNLL-U format

    if fund_dictionary:
        # Import file of 'Dizionario Fondamentale (De Mauro)' (only for Italian for now)
        dictionary = read_dictionary(fund_dictionary[0])
    else:
        dictionary = None

    sent_features = {}

    for sent_id, sentence in sentences.items():
        # Compute linguistic features and store them in a dictionary {Key: sentence_id, Value: sentence_features}
        # The function takes in input the sentences of every document and the Dizionario Fondamentale, if present
        features = compute_features(sentence, dictionary)
        sent_features[sent_id] = features
    vectorize(sent_features)


if __name__ == '__main__':
    # TODO handle input as documents and as sentences
    # try:
    #     read_and_compute(sys.argv[1], sys.argv[2])
    # except IndexError:
    #     read_and_compute(sys.argv[1])
    read_and_compute('01.parsed', 'DizionarioFondamentale')