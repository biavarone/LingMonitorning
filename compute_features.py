# -*- coding: utf-8  -*-
# !/usr/bin/python

import operator
from utils import ratio, get_from_dict, dict_distribution
from linguistic_features import Features


def max_depth(token):
    """
    NP-complete problem! Be careful
    Args:
        token:

    Returns:

    """
    if len(token.children) == 0:
        return 0
    else:
        maximum = 0
        for child in token.children:
            depth = max_depth(child)
            if depth > maximum:
                maximum = depth
        return maximum + 1


def compute_features(sentence, dictionary):
    """
    Compute the features defined in the Class Features()

    :param sentence: ([[Sentence]]) list of documents
    :param dictionary: //
    :return: None
    """
    features_values = {
        # 'n_sentences': len(sentences),
        'n_sentences': 1,  # because we're working with 1 sentence at a time # TODO fix in case of use with docs
        'n_tokens': 0
    }

    features = Features()

    # Compute linguistic features for each sentence
    # TODO fix in case of use with docs
    # for sentence in sentences:
    features_values['n_tokens'] += len(sentence.tokens)

    features.max_sentence_threes_depth.append(max_depth(sentence.root))

    for token in sentence.tokens:  # Features for each token in the sentence
        if dictionary:
            features.lexicon_in_dictionary(token, dictionary)  # Lessico nel dizionario di demauro
        features.forms_and_lemmas(token)  # Features about forms and lemmas
        features.count_chars_and_tokens(token)  # Count character per token and number of tokens
        features.count_pos_and_dep(token)  # Count uPOS, xPOS, dep
        features.count_lexical_words(token)  # Count lexical words (PAROLE PIENE)
        features.verbal_features(token)  # Verbal features
        features.count_roots(token)
        features.count_links(token)  # Checking number of roots and links per file
        features.count_subjects(token)  # Count preverbal and postverbal subjects
        features.count_objects(token)  # Count preverbal and postverbal objects
        features.count_prepositional_chain_and_syntagms(token, sentence)  # Count prepositional chains and prepositional syntagms
        features.count_subordinate_propositions(token, sentence)  # Count subordinate propositions, pre and post verbal subordinates, subordinate chains

    # Compute type/token ratio on forms and lemmas
    if len(features.ttrs_form) > 0:
        # TODO MA STA COSA A CHE SERVE?
        features_values['ttr_form'] = ['chunk_' + str((i + 1) * features.chunks_len) + ':' + str(ttr) for i, ttr in
                                       enumerate(features.ttrs_form)]  # TODO Perché chunks_len?
        features_values['ttr_lemma'] = ['chunk_' + str((i + 1) * features.chunks_len) + ':' + str(ttr) for i, ttr in
                                        enumerate(features.ttrs_lemma)]
    else:
        features_values['ttr_form'] = ratio(len(features.types_form_chunk), float(features.n_tok))
        # print(features_values['ttr_form'])
        features_values['ttr_lemma'] = ratio(len(features.types_lemma_chunk), float(features.n_tok))
        # print(features_values['ttr_lemma'])

    # For documents only # TODO Fix this?
    features_values['tokens_per_sent'] = ratio(features_values['n_tokens'], float(features_values['n_sentences']))

    features_values['char_per_tok'] = ratio(features.n_char, float(features.n_tok_no_punct))  # mean chars per token

    if dictionary:
        features_values['in_dict'] = ratio(features.in_dict, float(features.n_tok_no_punct))
        features_values['in_dict_types'] = ratio(features.in_dict_types, float(len(features.types_lemma)))
        features_values['in_FO'] = ratio(features.n_FO, float(features.n_tok_no_punct))
        features_values['in_AD'] = ratio(features.n_AD, float(features.n_tok_no_punct))
        features_values['in_AU'] = ratio(features.n_AU, float(features.n_tok_no_punct))
        features_values['in_FO_types'] = ratio(features.n_FO_types, float(len(features.types_lemma)))
        features_values['in_AD_types'] = ratio(features.n_AD_types, float(len(features.types_lemma)))
        features_values['in_AU_types'] = ratio(features.n_AU_types, float(len(features.types_lemma)))

    features_values['upos_dist'] = dict_distribution(features.upos_freq, 'upos_dist')  # Coarse-grained
    features_values['xpos_dist'] = dict_distribution(features.xpos_freq, 'xpos_dist')  # Fine-grained
    features_values['lexical_density'] = ratio(features.lexical_words, features.n_tok_no_punct)
    features_values['verbs_mood_dist'] = dict_distribution(features.verbs_mood_freq, 'verbs_mood_dist')
    features_values['verbs_tense_dist'] = dict_distribution(features.verbs_tense_freq, 'verbs_tense_dist')
    features_values['verbs_num_pers_dist'] = dict_distribution(features.verbs_num_pers_freq, 'verbs_num_pers_dist')
    # TODO aggiungere VerbForm e Gender


    # syntactic features
    features_values['verbal_head_total'] = get_from_dict(features.upos_freq, 'VERB')
    features_values['verbal_head_per_sent'] = ratio(get_from_dict(features.upos_freq, 'VERB'), features_values['n_sentences'])  # For documents
    features_values['verbal_root_total'] = features.n_verbal_root
    features_values['verbal_root_perc'] = ratio(features.n_verbal_root, features.n_root)  # For documents
    features_values['avg_token_per_clause'] = ratio(features.n_tok, features.n_verb)
    # features_values['verb_childs'] = features.n_verb_childs
    # features_values['avg_verb_childs'] = ratio(features.n_verb_childs, features.n_verb)
    features_values['avg_links_len'] = ratio(features.total_links_len, features.n_links)
    features_values['max_links_len'] = features.max_links_len  # TODO aggiungere link medio massimo per documento
    features_values['avg_max_depth'] = ratio(sum(features.max_sentence_threes_depth), len(features.max_sentence_threes_depth))  # Documents
    features_values['dep_dist'] = dict_distribution(features.dep_freq, 'dep_dist')
    features_values['dep_freq'] = [('dep_freq_' + x, y) for x, y in
                                   sorted(features.dep_freq.items(), key=operator.itemgetter(1), reverse=True)]
    features_values['subj_pre'] = ratio(features.n_subj_pre, features.n_subj_pre + features.n_subj_post)
    features_values['subj_post'] = ratio(features.n_subj_post, features.n_subj_pre + features.n_subj_post)
    features_values['obj_pre'] = ratio(features.n_obj_pre, features.n_obj_pre + features.n_obj_post)
    features_values['obj_post'] = ratio(features.n_obj_post, features.n_obj_pre + features.n_obj_post)
    features_values['prepositional_chains_total'] = features.n_prepositional_chain
    features_values['avg_prepositional_chain_len'] = ratio(features.total_prepositional_chain_len, features.n_prepositional_chain)

    features_values['prepositional_chain_freq'] = sorted(
        {'prep_freq_' + str(i): features.prep_chains.count(i) for i in set(features.prep_chains)}.items(),
        key=operator.itemgetter(1), reverse=True)
    features_values['prepositional_chain_distribution'] = sorted(
        {'prep_dist_' + str(i): features.prep_chains.count(i) / float(features.n_prepositional_chain) for i in set(features.prep_chains)}.items(),
        key=operator.itemgetter(1), reverse=True)
    features_values['subordinate_chains_freq'] = sorted(
        {'subordinate_freq_' + str(i): features.subordinate_chains.count(i) for i in set(features.subordinate_chains)}.items(),
        key=operator.itemgetter(1), reverse=True)
    features_values['subordinate_chains_distribution'] = sorted(
        {'subordinate_dist_' + str(i): features.subordinate_chains.count(i) / float(features.n_subordinate_chain) for i in
         set(features.subordinate_chains)}.items(), key=operator.itemgetter(1), reverse=True)

    features_values['total_subordinate_proposition'] = features.n_subordinate_proposition
    features_values['total_subordinate_chain'] = features.n_subordinate_chain
    # features_values['total_subordinate_chain_len'] = features.total_subordinate_chain_len
    features_values['avg_subordinate_chain_len'] = ratio(features.total_subordinate_chain_len, features.n_subordinate_chain)
    features_values['principal_proposition_dist'] = ratio(features.n_verb - features.n_subordinate_proposition, features.n_verb)
    features_values['subordinate_proposition_dist'] = ratio(features.n_subordinate_proposition, features.n_verb)
    features_values['subordinate_pre'] = ratio(features.n_subordinate_pre, features.n_subordinate_proposition)
    features_values['subordinate_post'] = ratio(features.n_subordinate_post, features.n_subordinate_proposition)
    features_values['verb_edges_dist'] = [('verb_edges_dist_' + str(k), v) for k, v in dict_distribution(features.verb_edges_freq, '')]  # Arità totale
    # Non ha senso tenerla, meglio usare solo la distribuzione
    # features_values['verb_edges_freq'] = [('verb_edges_freq_' + str(k), v) for k, v in sorted(features.verb_edges_freq.items(),
    #                                                          key=operator.itemgetter(1), reverse=True)]
    features_values['avg_verb_edges'] = ratio(features.total_verb_edges, features.n_verb)  # Arità media

    return features_values