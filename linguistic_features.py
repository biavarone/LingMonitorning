# -*- coding: utf-8  -*-
# !/usr/bin/python

import re
from utils import ratio, dict_counter


class Features:
    lexical_words_list = ['ADJ', 'ADV', 'NOUN', 'PROPN', 'VERB']
    mood_re = re.compile('Mood=[A-Za-z]+')
    tense_re = re.compile('Tense=[A-Za-z]+')
    person_re = re.compile('Person=[1-3]+')
    number_re = re.compile('Number=[A-Za-z]+')
    verbform_re = re.compile('VerbForm=[A-Za-z]+')
    gender_re = re.compile('Gender=[A-Za-z]+')
    chunks_len = 100  # TODO chunks_len 100 e 200

    def __init__(self):
        self.n_char = 0  # number of characters per document (or sentence)
        self.n_tok = 0  # tokens per document (or sentence)
        self.n_tok_no_punct = 0  # tokens per document without punctuation
        self.in_dict = 0  # tokens in dictionary (only italian for now)
        self.n_FO = 0  # (only IT for now) numero parole fondamentali per documento
        self.n_AU = 0  # (only IT for now) numero parole alto uso per documento
        self.n_AD = 0  # (only IT for now) numero parole alta disponibilità per documento
        self.in_dict_types = 0  # types in dictionary (only IT for now)
        self.n_FO_types = 0  # (only IT for now) TIPI lessico fondamentale
        self.n_AU_types = 0  # (only IT for now) TIPI lessico alto uso
        self.n_AD_types = 0  # (only IT for now) TIPI lessico alta disponibilità
        self.lexical_words = 0  # parole piene (lexical words) ##!! attenzione, prima self.full_words
        self.n_verb = 0
        self.n_verbal_root = 0
        self.n_root = 0
        self.n_links = 0
        self.total_links_len = 0
        self.max_links_len = 0
        self.n_subordinate_proposition = 0
        self.n_subordinate_chain = 0
        self.total_subordinate_chain_len = 0
        self.n_subordinate_pre = 0
        self.n_subordinate_post = 0
        self.total_verb_edges = 0
        self.n_subj_pre = 0
        self.n_subj_post = 0
        self.n_obj_pre = 0
        self.n_obj_post = 0
        self.n_prepositional_chain = 0
        self.total_prepositional_chain_len = 0

        self.max_sentence_trees_depth = []
        self.prep_chains = []
        self.subordinate_chains = []
        self.ttrs_form = []
        self.ttrs_lemma = []

        self.types_form = []
        self.types_lemma = []
        self.types_form_chunk = []  # For documents
        self.types_lemma_chunk = []
        self.upos_total = {}
        self.xpos_total = {}
        self.dep_total = {}
        self.verbs_mood_total = {}
        self.verbs_tense_total = {}
        self.verbs_num_pers_total = {}
        self.verb_edges_total = {}

    @staticmethod
    def is_punct(token):
        """
            Return True if the passed token is a punctuation mark.

            :param token: (Token) the token to be inspected
            :return: (bool) True if the token is a punctuation mark
        """
        return token.upos == 'PUNCT'

    @staticmethod
    # Language dependent --> italiano
    # TODO e per altre lingue?
    def is_prepositional_syntagm(token):
        have_case_child = False
        for child in token.children:
            if child.dep == 'case':
                have_case_child = True
                break
        return have_case_child and token.dep == 'nmod'

    @staticmethod
    def is_subordinate_proposition(token):
        """

        :param token: (Token) the token to be inspected
        :return: (bool) True if the token ???
        """
        is_subordinate = False
        if token.dep in ['acl:relcl', 'advcl', 'ccomp', 'xcomp']:
            is_subordinate = True
        elif token.upos == 'VERB' and token.dep not in ['cop', 'conj', 'root']:
            is_subordinate = True
        elif token.upos in ['ADJ', 'NOUN', 'PRON'] and token.dep not in ['cop', 'conj', 'root']:
            for child in token.children:
                if child.dep == 'cop':
                    is_subordinate = True
                    break
        return is_subordinate

    @staticmethod
    def get_chain_lengths(token, is_function):
        lengths = [1]
        sub_lengths = []
        for child in token.children:
            if is_function(child):
                sub_lengths += [i + 1 for i in Features.get_chain_lengths(child, is_function)]
        if len(sub_lengths) > 0:
            lengths = sub_lengths
        return lengths

    def count_chars_and_tokens(self, token):
        # Conto caratteri per token, conto num token
        if not self.is_punct(token):
            self.n_char += len(token.form)
            self.n_tok_no_punct += 1
        self.n_tok += 1

    def count_pos_and_dep(self, token):
        # Crea un dizionario con --> key: uPOS value: quante volte quella POS appare nel documento
        dict_counter(self.upos_total, token.upos)
        # Crea un dizionario con key: tipo di dipendenza value: quante volte quella dipendenza appare nel documento
        # dep --> relazione di dipendenza che la parola ha con la sua testa
        dict_counter(self.dep_total, token.dep)
        # Crea un dizionario con --> key: xPOS, value: quante volte quella POS appare nel documento
        dict_counter(self.xpos_total, token.xpos)

    def count_lexical_words(self, token):
        if token.upos in self.lexical_words_list:
            self.lexical_words += 1

    def forms_and_lemmas(self, token):
        if token.form not in self.types_form_chunk and not self.is_punct(token):
            self.types_form_chunk.append(token.form)
        if token.lemma not in self.types_lemma_chunk and not self.is_punct(token):
            self.types_lemma_chunk.append(token.lemma)

        if self.n_tok_no_punct == self.chunks_len:
            self.ttrs_form.append(ratio(len(self.types_form_chunk), float(self.n_tok_no_punct)))
            self.ttrs_lemma.append(ratio(len(self.types_lemma_chunk), float(self.n_tok_no_punct)))

        if not self.is_punct(token) and token.lemma not in self.types_lemma:
            self.types_lemma.append(token.lemma)
        if not self.is_punct(token) and token.form not in self.types_form:
            self.types_form.append(token.form)

    def lexicon_in_dictionary(self, token, dictionary):
        # Lessico nel dizionario di DeMauro
        if token.lemma in dictionary and not self.is_punct(token):
            self.in_dict += 1
            if dictionary[token.lemma] == 'AU':
                self.n_AU += 1
            elif dictionary[token.lemma] == 'AD':
                self.n_AD += 1
            elif dictionary[token.lemma] == 'FO':
                self.n_FO += 1
            if token.lemma not in self.types_lemma:
                self.in_dict_types += 1
                if dictionary[token.lemma] == 'AU':
                    self.n_AU_types += 1
                elif dictionary[token.lemma] == 'AD':
                    self.n_AD_types += 1
                elif dictionary[token.lemma] == 'FO':
                    self.n_FO_types += 1
        elif token.form in dictionary and not self.is_punct(token):
            self.in_dict += 1
            if dictionary[token.form] == 'AU':
                self.n_AU += 1
            elif dictionary[token.form] == 'AD':
                self.n_AD += 1
            elif dictionary[token.form] == 'FO':
                self.n_FO += 1
            if token.form not in self.types_lemma:
                self.in_dict_types += 1
                if dictionary[token.form] == 'AU':
                    self.n_AU_types += 1
                elif dictionary[token.form] == 'AD':
                    self.n_AD_types += 1
                elif dictionary[token.form] == 'FO':
                    self.n_FO_types += 1

    def verbal_features(self, token):
        if token.upos == 'VERB':
            self.n_verb += 1

            # TODO n_verb_edges --> mai più usata oltre ste 3 righe. CHE FAMO???????
            # TODO controllare che non aggiunga punteggiatura al numero di archi
            n_verb_edges = len(token.children)  # Trova tutti i dipendenti del verbo (archi entranti nella testa del verbo)

            # TODO problema: token.children contiene children della root, che in alcune treebank non è associata al verbo
            dict_counter(self.verb_edges_total, n_verb_edges)  # Quanti verbi nella frase con un tot di archi

            self.total_verb_edges += n_verb_edges  # Numero totale archi in una frase/documento


            # TODO aggiungere gender e verbform
            try:
                dict_counter(self.verbs_mood_total,
                             self.mood_re.findall(token.mfeats)[0][5:])
            except IndexError:
                pass
            try:
                dict_counter(self.verbs_tense_total, self.tense_re.findall(token.mfeats)[0][6:])
            except IndexError:
                pass
            try:
                pers = self.person_re.findall(token.mfeats)[0][7:]
            except IndexError:
                pers = ''
            try:
                num = self.number_re.findall(token.mfeats)[0][7:]
            except IndexError:
                num = ''
            dict_counter(self.verbs_num_pers_total, num + '+' + pers)

            if token.dep == 'root':
                self.n_verbal_root += 1

    def count_roots(self, token):
        if token.dep == 'root':
            self.n_root += 1  # ROOT per doc/sentence

    def count_links(self, token):
        if token.head != 0 and not self.is_punct(token):
            self.n_links += 1  # Number of tokens linked to the root (?)
            link_len = abs(token.head - token.id)  # Link length (distance of the token from the head)
            self.total_links_len += link_len  # Needed to compute average link length

            if link_len > self.max_links_len:
                self.max_links_len = link_len  # Longest link per document

    def count_subjects(self, token):
        # Count pre-verbal and post-verbal subjects
        if 'subj' in token.dep:
            # Token.head contiene l'id dell'elemento da cui dipende il soggetto
            if token.id < token.head:
                self.n_subj_pre += 1
            else:
                self.n_subj_post += 1

    def count_objects(self, token):
        # Count pre-verbal and post-verbal objects
        if 'obj' in token.dep:
            if token.id < token.head:
                self.n_obj_pre += 1
            else:
                self.n_obj_post += 1

    def count_prepositional_chain_and_syntagms(self, token, sentence):
        # TODO ?
        if token.dep == 'nmod':
            if self.is_prepositional_syntagm(token):
                if not self.is_prepositional_syntagm(sentence.tokens[token.head - 1]):
                    chains_lenghts = self.get_chain_lengths(token, self.is_prepositional_syntagm)
                    self.prep_chains += chains_lenghts
                    self.n_prepositional_chain += len(chains_lenghts)
                    self.total_prepositional_chain_len += sum(chains_lenghts)

    def count_subordinate_propositions(self, token, sentence):
        if self.is_subordinate_proposition(token):
            self.n_subordinate_proposition += 1
            if token.id > sentence.root.id:  # TODO solito problema, non è detto che la root sia il verbo
                self.n_subordinate_post += 1
            else:
                self.n_subordinate_pre += 1
            if not self.is_subordinate_proposition(sentence.tokens[token.head - 1]):
                # TODO magari controlla che qui funzioni tutto, prima o poi
                chains_lenghts = self.get_chain_lengths(token, self.is_subordinate_proposition)
                self.subordinate_chains += chains_lenghts
                self.n_subordinate_chain += len(chains_lenghts)
                self.total_subordinate_chain_len += sum(chains_lenghts)