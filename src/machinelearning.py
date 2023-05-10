# -*- encoding: utf-8 -*-
'''
Created on 13/10/2013

@author: jmletras
'''

import sentence_database, sentiment_lexicon, re
import nltk

from datetime import datetime
from collections import defaultdict
from nltk.stem.wordnet import WordNetLemmatizer

#from sets import Set
from nltk.corpus import stopwords
from nltk.chunk import ne_chunk
from nltk.tag import pos_tag
from sentiment_lexicon import create_sentimentwordlist, write_dict_to_file, write_list_to_file
from random import shuffle
from nltk.classify.scikitlearn import SklearnClassifier
from sklearn.svm import LinearSVC
from sklearn.linear_model import SGDClassifier
#from nltk.collocations import BigramCollocationFinder
import string, math
from bs4 import BeautifulSoup
import urllib, httplib2
import winsound
import parse_tree


#bigram_measures = nltk.collocations.BigramAssocMeasures()
    
def process_database_sentences():
    print ("Generating features....")
    
    #Delta Calculation
    #global positive_sentences
    #global negative_sentences    
    #positive_sentences = 0
    #negative_sentences = 0
    
    for line in sentences:
        sentence = line[3]
        sentence_class = line[4]
        
        sentence_features = process_single_sentence(sentence)
        
        sentiment_words = entity_afection(sentence_features, line[2])
        
        tokenized_sentence = sentence_features[0]
        uppercase_words = sentence_features[1]
        url = sentence_features[2]
        entities = sentence_features[3]
        #sentiment_words = sentence_features[4]
        tree = sentence_features[5]
        
        #print ("Teste de palavras sentimento " + sentiment_words)
        
        if len(tokenized_sentence) >0:
            tokenized_sentences[line[0]] = tokenized_sentence,  sentence_class, uppercase_words, url, entities, sentiment_words, tree   
        
        
                
        #=======================================================================
        # punctuation = [s for s in string.punctuation]
        # processed_sentence = [x for x in processed_sentence if x not in punctuation]
        # 
        # finder = BigramCollocationFinder.from_words(processed_sentence)
        # scored = finder.score_ngrams(bigram_measures.raw_freq)
        #=======================================================================
        
        #for word in processed_sentence:
        
        #=======================================================================
        # for word, score in scored:
        #     all_words.add(word)
        #     if line[4] == "POSITIVE":
        #         #positive_sentences = positive_sentences + 1
        #         pos_word_frequency.inc(word, 1) 
        #     elif line[4] == "NEGATIVE":
        #     #negative_sentences  = negative_sentences + 1
        #         neg_word_frequency.inc(word, 1)
        #     else:
        #         neu_word_frequency.inc(word, 1)
        #=======================================================================
                
                
    #print all_words    
    
    #write_dict_to_file(pos_word_frequency, "Positive_Bigrams_Frequency")
    #write_dict_to_file(neg_word_frequency, "Negative Bigrams_Frequency")
    #write_dict_to_file(neu_word_frequency, "Neutral_Bigrams_Frequency")   
    #write_list_to_file(list(all_words), "Bigrams_list")   
    #write_list_to_file(scored, "Bigrams_frequency")
    #print "Unigram Features saved to a file..."
    print ("Foram gravadas " + str(len(tokenized_sentences)) + " blocos de texto e " + str(len(all_words)) + " palavras. " ) 
    #return all_words.keys()[:size]
    exit

def process_single_sentence(sentence, show_info=True):
    url = re.findall(r'(https?://\S+)', sentence) #Remove enderecos Web e guarda em variavel
    if len(url) > 0:
        url = url[0]
        sentence = remove_strings(sentence, url)
        #if show_info==True:
        #    print "Url detected: ", str(url)

    user = re.findall(r'(@\S+)', sentence) #Remove referencias a utilizadores no Twitter
    if len(user) > 0:
        sentence = remove_strings(sentence, user)

    sentence = re.sub("[#$%&*\-\"]", "", sentence) #remove caracteres especiais
    sentence = re.sub(r'([a-z])([A-Z])', r'\1 \2', sentence) #Divide Palavras pelas maiusculas
    tokens = re.findall(r"[\w']+|[.,!?;\"]", sentence) #Separar por espacos e por pontuacao
    
    tree = parse_tree.generateParseTree(tokens)
    if show_info==True:
        print (tree)
    entities = parse_tree.extract_entity_names(tree)
    if show_info==True:
        print ("Entidades encontradas: ", str(entities))
    
    sentiment_words = parse_tree.getSentimentWordsFromNodes(tree)
    sentiment_words = [l.lemmatize(s.lower()) for s in sentiment_words if s not in stopwords.words("english")]
    
    new_tokens = []
    for i in tokens:
        i = re.sub("^'+|'+$|'s", "", i)
        if i in slang_dictionary.keys():
            new_tokens.extend([s for s in slang_dictionary[i].split(' ')])
        else:
            new_tokens.append(i)
             
    tokens = new_tokens            
        
    uppercase = re.findall(r"[A-Z]{3,}\B[A-Z]+", sentence)
    
    tokens = [l.lemmatize(s.lower()) for s in tokens if s not in stopwords.words("english") and not s.isdigit()]
    #tokens = [l.lemmatize(s.lower()) for s in tokens if not s.isdigit()]

    #if show_info == True:
    #    print "Processed Sentence:\n", tokens
        
    return tokens, uppercase, url, entities, sentiment_words, tree

def remove_strings(s, tags):
    new = []
    for word in s.split(' '):
        if word not in tags:
            new.append(word)
        
    return " ".join(new)

def get_sentencefeatures(sentence_tokens, uppercase = "", url = "", entities = "", sentiment_words = "", tree="", key = "", show_info=True):    
    features = {}
    
    if show_info==True:
        print ("Sentence Tokens")
        print (sentence_tokens)
    
    
    
    features["polarity_value"] = 0
    features["polarity_url"] = 0
    features["has_url"] = 0
    features["polarity_qtdpositive"] = 0
    features["polarity_qtdnegative"] = 0
    features["polarity_maxnegative"] = 0
    features["polarity_maxpositive"] = 0
    features["polarity_qtdneutral"] = 0
    features["has_positive"] = 0
    features["has_negative"] = 0
    features["has_negation"] = 0
    features["has_questionmark"] = 0
    features["has_exclamationmark"] = 0
    features["has_uppercase"] = 0
    features["has_posIntensifier"] = 0
    features["has_negIntensifier"] = 0
    features["has_qtdPunctuation"] = 0
    #number_adjectives = 0
    #number_adverbs = 0
    #features["has_aspas"] = 0
    features["perc_positives"] = 0
    features["perc_negatives"] = 0
    features["perc_neutral"] = 0
    features["positive_entropy_value"] = 0
    features["negative_entropy_value"] = 0
    features["neutral_entropy_value"] = 0
 
    features["has_entities"] = 0
    
    if show_info==True:
        print (tree)
    #sentiment_wor)ds = parse_tree.getSentimentWordsFromNodes(tree)
    
    sentiment_words = [l.lemmatize(s.lower()) for s in sentiment_words if s not in stopwords.words("english")]
    
    if show_info==True:
        print ("Sentiment Words: ", str(sentiment_words)  )
    
    #From sentiment words without negation
    #features["polarity_value"] = sum(map(lambda word: polarity_list.get(word, 0), sentiment_words))
    
    #From sentences tokens without negation
    #features["polarity_value"] = sum(map(lambda word: polarity_list.get(word, 0), sentence_tokens))
    
    polarity_values = []
    
    #word_pos = nltk.pos_tag(sentence_tokens)

    #number_adjectives = len([pos[1] for pos in word_pos if pos[1] == "JJ"])
    #number_adverbs = len([pos[1] for pos in word_pos if pos[1] == "RB"])
    if [word for word in sentiment_words if word in negations]:
        features["has_negation"] = 1
    
    
    
    
    
    features["polarity_value"] = sum(calculate_polarity_values(sentiment_words)) #With negations account
    
    if show_info==True:
        print ("Polarity_Value: ", str(features["polarity_value"]))
    
    if features["has_url"]:
        features["has_url"] = 1
    
    #Without taking negations account
    #polarity_values = map(lambda word: polarity_list.get(word, 0), sentence_tokens) 
            
    
    features["polarity_qtdpositive"] = len([i for i in polarity_values if i > 0])
    
    if len(polarity_values) > 1 and max(polarity_values) > 0:
        features["polarity_maxpositive"] = max(polarity_values) #- Testado mas nao aprovado - refeirir no relatorio
    
    if len([i for i in polarity_values if i > 0]) > 0:
        features["has_positive"] = 1
        features["perc_positives"] = len([i for i in polarity_values if i > 0])/float(len(sentence_tokens))
    
    features["polarity_qtdnegative"] = len([i for i in polarity_values if i < 0])
    
    if len(polarity_values) > 1 and min(polarity_values) < -1:
        features["polarity_maxnegative"] = min(polarity_values) #- Testado mas nao aprovado - refeirir no relatorio
    if len([i for i in polarity_values if i <= -2]) > 0:
        features["has_negative"] = 1
        features["perc_negatives"] = len([i for i in polarity_values if i <= -2])/float(len(sentence_tokens))
    
    features["polarity_qtdneutral"] = len(polarity_values) - len([i for i in polarity_values if i > 0]) - len([i for i in polarity_values if i <= -2])  
    features["perc_neutral"] = len([i for i in polarity_values if i == 0])/float(len(sentence_tokens))
        
    question_mark = ["?"]
    features["has_qtdPunctuation"] = len([x for x in sentence_tokens if x in string.punctuation])
    if len([x for x in sentence_tokens if x in question_mark]) > 0:
        features["has_questionmark"] = 1
    
    excl = ["!"] 
    if len([x for x in sentence_tokens if x in excl]) > 0:
        features["has_exclamationmark"] = 1
    
    if uppercase > 0:    
        features["has_uppercase"] = len(uppercase)
    
    
    features["polarity_url"] = polarity_url_list.get(key, 0)
    
    #features["sentence_length"] = len(sentence_tokens) #- Testado mas nao aprovado - referir no relatorio
    
    #features["number_adjectives"] = number_adjectives #- Testado mas nao aprovado - referir no relatorio
    #features["number_adverbs"] = number_adverbs #- Testado mas nao aprovado - referir no relatorio
   
   
    if len([x for x in sentence_tokens if x in positive_intensifiers]) > 0:
        features["has_posIntensifier"] = 1
    if len([x for x in sentence_tokens if x in negative_intensifiers]) > 0:
        features["has_negIntensifier"] = 1
    
    if len(entities) > 0:
        features["has_entities"] = 1
    
    #for word in all_words.keys()[:featuresize]:
    #    features["has(%s)" % word] = (word in sentence_tokens)
    
        
        #=======================================================================
        # c = sentence_tokens.count(word)
        # valuepos = 0
        # valueneg = 0
        # if pos_word_frequency[word] != 0:
        #     valuepos = c * math.log((pos_sentences/pos_word_frequency[word]), 2) 
        # if neg_word_frequency[word] != 0:
        #     valueneg = c * math.log((neg_sentences/neg_word_frequency[word]), 2) 
        # features["deltatfidf(%s)" % word] = c*valuepos - c*valueneg
        #=======================================================================

        
    #===========================================================================
    # features["deltaidf_value"] = 0
    # valuepos = 0
    # valueneg = 0
    # for word in sentence_tokens:
    #     c = sentence_tokens.count(word)
    #     if pos_word_frequency[word] != 0:
    #         valuepos += c * math.log((pos_sentences/pos_word_frequency[word]), 2) 
    #     if neg_word_frequency[word] != 0:
    #         valueneg += c * math.log((neg_sentences/neg_word_frequency[word]), 2)
    # features["deltaidf_value"] = valuepos - valueneg
    #===========================================================================
    
    #####################################################
    #Word Entropy
    
    for word in sentence_tokens:
        if word in entropy:
            if entropy[word] < 0.004:
                if word in pos_word_frequency.keys():
                    #pass
                    features["positive_entropy_value"] += entropy[word]
                elif word in neg_word_frequency.keys():
                    features["negative_entropy_value"] += entropy[word]
                    
                #if str(word) in neu_word_frequency.keys():
                
                else:
                    #pass
                    features["neutral_entropy_value"] += entropy[word]
                
    ######################################################

    if show_info==True:
        print ("Features: \n", features)
        
    return features

def calculate_positive_word_frequency():
    print ("Calculating Positive word frequency")
    try:
        a = open("src/export/Positive Words Frequency_20131116_174131.txt")
        try:
            pos_word_frequency = dict(map(lambda k_v: (k_v[0],float(k_v[1].rstrip())), [ line.split('\t') for line in a ])) 
        finally:
            a.close()
    except IOError as e:
        print ("I/O error({0}): {1}".format(e.errno, e.strerror))
        pass
    
    print ("Positive Words: ", str(len(pos_word_frequency)))
    return pos_word_frequency

def calculate_negative_word_frequency(): 
    print ("Calculating Negative word frequency" )
    try:
        a = open("src/export/Negative Words Frequency_20131116_174132.txt")
        try:
            neg_word_frequency = dict(map(lambda k_v: (k_v[0],float(k_v[1].rstrip())), [ line.split('\t') for line in a ])) 
        finally:
            a.close()
    except IOError as e:
        print ("I/O error({0}): {1}".format(e.errno, e.strerror))
        pass
    print ("Negative Words: ", str(len(neg_word_frequency)))
    return neg_word_frequency

def calculate_neutral_word_frequency():
    print ("Calculating Neutral word frequency" )
    try:
        a = open("src/export/Neutral Words Frequency_20131116_174132.txt")
        try:
            neu_word_frequency = dict(map(lambda k_v: (k_v[0],float(k_v[1].rstrip())), [ line.split('\t') for line in a ])) 
        finally:
            a.close()
    except IOError as e:
        print ("I/O error({0}): {1}".format(e.errno, e.strerror))
        pass
    print ("Neutral Words: ", str(len(neu_word_frequency)))
    return neu_word_frequency

def calculate_polarity_values(sentiment_words):
    
    polarity_values = []
    number_negations = 0
    
    for word in sentiment_words:    #Verbs, adjectives and negations taken in account for sentiment words
        
        if word in negations:
            number_negations += 1                            
                
        else:
            word_polarity = polarity_list.get(word, 0)
            if number_negations > 0:
                if word_polarity > 2:
                        
                    #i = int(word_polarity / 2)-1
                    polarity_values.append(word_polarity - 2)
                    #print int(word_polarity / 2), i
                    number_negations = 0
                elif word_polarity < -2:
                        
                    #i = int(word_polarity / 2)+1
                    polarity_values.append(word_polarity + 2)
                    number_negations = 0
                elif word_polarity >= -2 and word_polarity <= 2: 
                    polarity_values.append(-1 * word_polarity)
                    number_negations = 0
            else:
                polarity_values.append(word_polarity)
                #number_negations = 0
    return polarity_values

def get_sentence_polarity(key):
    print (key)
    return sentences[key][4]

def get_class(value):
    
    if value > 0:
        return "POSITIVE"
    elif value < -1:
        return "NEGATIVE"
    else:
        return "NEUTRAL"
    

def calculate_entropy():
    print ("Calculating frequency of words entropy")
    
    pos_word_frequency = calculate_positive_word_frequency()
    neg_word_frequency = calculate_negative_word_frequency()
    neu_word_frequency = calculate_neutral_word_frequency()
    
    for word in all_words:
        ent = 0.0
    
        pos = pos_word_frequency.get(word, 0)
        neg = neg_word_frequency.get(word, 0)
        neu = neu_word_frequency.get(word, 0)
        
        #len(pos_word_frequency)
        
        if pos > 0:
            ent += float(pos)/sum(pos_word_frequency.values()) * math.log(float(pos)/sum(pos_word_frequency.values()), 2)
        if neg > 0:
            ent += float(neg)/sum(neg_word_frequency.values()) * math.log(float(neg)/sum(neg_word_frequency.values()), 2)
        if neu > 0:
            ent += float(neu)/sum(neu_word_frequency.values()) * math.log(float(neu)/sum(neu_word_frequency.values()), 2)
        ent = -ent
        entropy[word] = ent
    
    #write_dict_to_file(entropy, "Bigrams_entropy")
        
def get_featuresets():
    
    sentence_polarity = []
    #i = 1
    for key, value in tokenized_sentences.items():
        tokens = value[0]
        sentence_class = value[1]
        uppercase = value[2]
        url = value[3]
        entities = value[4]
        sentiment_words = value[5]
        tree = value[6]
        
        sentence_polarity.append([get_sentencefeatures(tokens, uppercase, url, entities, sentiment_words, tree, key ), sentence_class])
        #print i
        #i = i+1  
    
    #write_list_to_file(sentence_polarity, "FeaturesSets_List_Bigram+Polarity")  
    #print "FeatureSets Saved to List"
    print ("Sentences Features Generated.") 
    return sentence_polarity  

def get_sentence_url_polarities(): 
    print ("Retrieving URL polarities from file...") 
    try:
        a = open("export/URL_Polarities_20131109_134032.txt")
        try:
            polarity_url_dict = dict(map(lambda k_v: (k_v[0],int(k_v[1])), [ line.split('\t') for line in a ])) 
        finally:
            a.close()
    except IOError:
        print ("Ocorreu um erro ao ler o ficheiro: export/URL_Polarities_20131109_134032.txt" ), 
        pass
    print ("Polarity URL list retrieved.")
    return polarity_url_dict

def get_slang_dictionary():
    print ("Retrieving internet slang from file...") 
    try:
        a = open("src/data/internetslang.txt")
        try:
            internet_slang_dict = dict(map(lambda k_v: (l.lemmatize(k_v[0].lower()),k_v[1].rstrip()), [ line.split('\t') for line in a ])) 
        finally:
            a.close()
    except IOError:
        print ("Ocorreu um erro ao ler o ficheiro: data/internetslang.txt") , 
        pass
    print ("Internet Slang list retrieved.")
    return internet_slang_dict

def save_polarity_url_to_file():
    print ("Saving polarity URL to file")
    sentences_url_polarity = {}
    i = 0
    for line in sentences:
        print (str(i))
        url_list = []
        url_list = re.findall(r'(https?://\S+)', line[3]) #Remove enderecos Web
        if len(url_list) > 0:
            if url_list[0] != "":
                url = urllib.quote(url_list[0], safe=":/")
                try:
                    soup = BeautifulSoup(urllib.urlopen(url))
                    if soup.title:
                        if soup.title.string:
                            print (soup.title.string)
                            url_tokens = re.findall(r"[\w']+|[#-.,!?;\"]",soup.title.string)
                            tokens = [l.lemmatize(s.lower()) for s in url_tokens if s not in stopwords.words("english") and not s.isdigit()]
                            sentences_url_polarity[line[0]] = sum(map(lambda word: polarity_list.get(word, 0), tokens))
                except urllib.HTTPError as e: 
                    #print "Error:", e
                    pass
    
                except httplib2.BadStatusLine as e:
                    #print "Error:", e
                    pass
                except urllib.URLError as e: 
                    #print "Error:", e
                    pass
                except urllib.socket.error as e:
                    #print "Error:", e
                    pass
        i += 1
    #write_dict_to_file(sentences_url_polarity, "URL_Polarities")
        
    print ("Done" )
    
   
def generate_afinn_polarity_list():
    print ("Generating AFINN Polarity Word List")
    try:
        a = open("src/data/AFINN/AFINN-111.txt")
        try:
            polarity_list = dict(map(lambda k_v: (k_v[0], int(k_v[1])), [ line.split('\t') for line in a ])) 
        finally:
            a.close()
    except IOError:
        print ("Ocorreu um erro ao ler o ficheiro " )
        pass
    print ("Polarity List: AFINN. Words: ", str(len(polarity_list)))
    return polarity_list

def generate_afinn_swn_polarity_list():
    print ("Generating AFINN Polarity Word List")
    try:
        a = open("src/export/sentiment_wordlist_20131018_215835.txt")
        try:
            polarity_list = dict(map(lambda k_v: (k_v[0], int(k_v[1])), [ line.split(':') for line in a ])) 
        finally:
            a.close()
    except IOError:
        print ("Ocorreu um erro ao ler o ficheiro " )
        pass
    print ("Polarity List: AFINN+SentiWordNet. Words: ", str(len(polarity_list)))
    return polarity_list
    
def save_arff_file(featuresets, name):    
    f = open("export/featuresets_"+name+".arff", "w")
    f.write("@RELATION reputation\n\n")
    
    
    
    features_list = [k for k in featuresets[0][0]]
    for feature in features_list:
        f.write("@ATTRIBUTE "+str(feature)+" REAL\n")
    f.write("@ATTRIBUTE class {\"POSITIVE\", \"NEGATIVE\", \"NEUTRAL\"}\n\n")
    f.write("@DATA\n")
    for k in featuresets:
        string = ', '.join(str(value) for value in k[0].values())
        string += ", " + str(k[1])+"\n"
        f.write(string)
    f.close()          
    return "Arff File Generated"

def generate_report_calculated_polarities(right, wrong, polarities_calculated):
    print ("----Polaridade----")
    print ("Polaridade real - Positivos: " ,polarities_calculated.count("POSITIVE"), " Negativos: " ,polarities_calculated.count("NEGATIVE"), \
        "Neutros: " ,polarities_calculated.count("NEUTRAL"))
    
    print ("Polaridade calculada - Correctos:", right.count("POSITIVE"), right.count("NEGATIVE"), right.count("NEUTRAL")," - Errados:", \
        wrong.count("POSITIVE"), wrong.count("NEGATIVE"), wrong.count("NEUTRAL"))
        
    print ("------------Acertos-----------------")
    print ("Correctos: ", len(right), " - Errados:", len(wrong))
    print ("Taxa de Acerto: {0:.3f}".format(len(right)/float(len(polarities_calculated))))
    
    print ( "------------Precisão-----------------")
    print ("Positivos: {0:.3f}".format(right.count("POSITIVE")/float(right.count("POSITIVE")+wrong.count("POSITIVE"))))
    print ("Negativos: {0:.3f}".format(right.count("NEGATIVE")/float(right.count("NEGATIVE")+wrong.count("NEGATIVE"))))
    print ("Neutros: {0:.3f}".format(right.count("NEUTRAL")/float(right.count("NEUTRAL")+wrong.count("NEUTRAL"))))

    print ("------------Cobertura-----------------")
    print ("Positivos: {0:.3f}".format(right.count("POSITIVE")/float(polarities_calculated.count("POSITIVE"))))
    print ("Negativos: {0:.3f}".format(right.count("NEGATIVE")/float(polarities_calculated.count("NEGATIVE"))))
    print ("Neutros: {0:.3f}".format(right.count("NEUTRAL")/float(polarities_calculated.count("NEUTRAL"))))
    
    print ("------------Medida-F-----------------")
    print ("Positivos: {0:.3f}".format(2*((right.count("POSITIVE")/float(right.count("POSITIVE")+wrong.count("POSITIVE"))*right.count("POSITIVE")/float(polarities_calculated.count("POSITIVE")))/  \
                                         (right.count("POSITIVE")/float(right.count("POSITIVE")+wrong.count("POSITIVE"))+right.count("POSITIVE")/float(polarities_calculated.count("POSITIVE"))))))
    print ("Negativos: {0:.3f}".format(2*((right.count("NEGATIVE")/float(right.count("NEGATIVE")+wrong.count("NEGATIVE"))*right.count("NEGATIVE")/float(polarities_calculated.count("NEGATIVE")))/  \
                                         (right.count("NEGATIVE")/float(right.count("NEGATIVE")+wrong.count("NEGATIVE"))+right.count("NEGATIVE")/float(polarities_calculated.count("NEGATIVE"))))))
    print ("Neutros: {0:.3f}".format(2*((right.count("NEUTRAL")/float(right.count("NEUTRAL")+wrong.count("NEUTRAL"))*right.count("NEUTRAL")/float(polarities_calculated.count("NEUTRAL")))/  \
                                         (right.count("NEUTRAL")/float(right.count("NEUTRAL")+wrong.count("NEUTRAL"))+right.count("NEUTRAL")/float(polarities_calculated.count("NEUTRAL"))))) )           

def entity_afection(sentence, entitylist):
    sentiment_words = []
    sentiment_dictionary = parse_tree.get_dictionary_sentiment(parse_tree.sentiment_assigning(sentence[5], sentence[3], sentence[4]))
        
    print ("Entidades reais (Anotadas):", str(entity_detection[entitylist]))
        
    if len(sentence[3]) > 0:
        print ("Entidades detectadas pelo sistema: ", sentence[3])
        print ("Entidades e sentimentos atribuidos:")
        entity_detected = ""
        sentiment_index = 0
        for x in range(0, len(sentence[3])):
            sentiment_words = [l.lemmatize(word.lower()) for word in sentiment_dictionary[x+1]]
            print (sentence[3][x], " - ", sentiment_words, " - Valor pol.:", sum(calculate_polarity_values(sentiment_words)))
                
                
            for word in sentence[3][x].split():
                if word in entity_detection[entitylist].split() or word.lower() in entity_detection[entitylist].split():
                    #entity_detected.append("\""+sentence[3][x]++++"\"")
                    entity_detected = sentence[3][x]
                    sentiment_index = x+1
                        
                    #print "Sentimento: ", sum(calculate_polarity_values(sentiment_words))
        if entity_detected:
            print ("Entidade considerada igual:", entity_detected)
        if sentiment_index != 0:
            sentiment_words = [l.lemmatize(word.lower()) for word in sentiment_dictionary[sentiment_index]]
            print ("Palavras sentimento atribuidas a entidade real:", sentiment_words, " - Valor pol.:", sum(calculate_polarity_values(sentiment_words)))
        else:
            sentiment_words = sentence[4]
            print ("Palavras sentimento atribuidas:", sentence[4], " - Valor pol.:", sum(calculate_polarity_values(sentence[4])))
            
    else:
        print ("Nao foi encontrada qualquer referencia a uma entidade.")
        sentiment_words = sentence[4]
        print ("Palavras sentimento atribuidas pelo sistema:", sentence[4], " - Valor pol.:", sum(calculate_polarity_values(sentence[4])))
    return sentiment_words

def calculate_processing_time():
    print ("Generating sentences to calculate the processing time...") 
    sentences_list = []
    try:
        a = open("data/50_sentences.txt")
        try:
            sentences_list = a.read().splitlines()         
        finally:
            a.close()
    except IOError:
        print ("Ocorreu um erro ao ler o ficheiro") , 
        pass
    print ("Foram lidas ", str(len(sentences_list)), "mensagens.")
    
    time_start = datetime.now()
    for sentence in sentences_list:
        print ("\nFrase:", sentence)
        sentence = process_single_sentence(sentence, True)

        print ("Entidades, sentimentos e pontuacao:")
        print (parse_tree.sentiment_assigning(sentence[5], sentence[3], sentence[4]))        
        
        sentiment_dictionary = parse_tree.get_dictionary_sentiment(parse_tree.sentiment_assigning(sentence[5], sentence[3], sentence[4]))
        
        
        if len(sentence[3]) > 0:
            
            if len(sentence[3]) == 1:
                print ("Uma entidade encontrada")    
            else:
                print ("Varias entidades encontradas")
            for x in range(0, len(sentence[3])):
                sentiment_words = [l.lemmatize(word.lower()) for word in sentiment_dictionary[x+1]]
                print (sentence[3][x], " - ", sentiment_words, sum(calculate_polarity_values(sentiment_words)))
        else:
            print ("Nao foi encontrada qualquer referencia a uma entidade.")
        #print parse_tree.getTreeNodes(sentence[5])
            #print classifier.classify(get_sentencefeatures(sentence[0], sentence[1], sentence[2], sentence[3], sentence[4], sentence[5], show_info=True))
    
    print ("Tempo total para ", str(len(sentences_list)), "mensagens:", str(datetime.now() - time_start))
    print ("Tempo medio: ", str((datetime.now() - time_start)/len(sentences_list)))


def calculate_rules_processing():
    print ("Getting the entities list..")
    
    entity_detection = {}
    try:
        f = open("data/dataset/replab2013_entities.tsv")
        
        try:
            lines = f.read().splitlines()
        finally:
            f.close()
        for line in lines:
            line_polarity = line.split("\t")
            line_polarity = [s[1:-1] for s in line_polarity] #retirar as aspas das palavras
            
            entity = line_polarity[1].replace("\"", "") #.split()
            entity = entity.strip()
            
            entity_detection[line_polarity[0]] = entity
    except IOError:
            pass
    
    print (entity_detection)
    
    print ("Calculating Rules based sentiment")
    
    #Comparar polaridades
    #equal = 0
    right = []
    wrong = []
    polarities_calculated = []
    
    for sentence_list in sentences:
        print ("\nFrase:", sentence_list)
        sentence = process_single_sentence(sentence_list[3], False)
        
        #tokens, uppercase, url, entities, sentiment_words, tree
    
        #id, user, file, msg, class
        sentiment_dictionary = parse_tree.get_dictionary_sentiment(parse_tree.sentiment_assigning(sentence[5], sentence[3], sentence[4]))
        
        
        print ("Entidades reais (Anotadas):", str(entity_detection[sentence_list[2]]))
        
        if len(sentence[3]) > 0:
            print ("Entidades detectadas pelo sistema: ", sentence[3])
            print ("Entidades e sentimentos atribuidos:")
            entity_detected = ""
            sentiment_index = 0
            for x in range(0, len(sentence[3])):
                sentiment_words = [l.lemmatize(word.lower()) for word in sentiment_dictionary[x+1]]
                print (sentence[3][x], " - ", sentiment_words, " - Valor pol.:", sum(calculate_polarity_values(sentiment_words)))
                
                
                for word in sentence[3][x].split():
                    if word in entity_detection[sentence_list[2]].split() or word.lower() in entity_detection[sentence_list[2]].split():
                        #entity_detected.append("\""+sentence[3][x]++++"\"")
                        entity_detected = sentence[3][x]
                        sentiment_index = x+1
                        
                        #print "Sentimento: ", sum(calculate_polarity_values(sentiment_words))
            if entity_detected:
                print ("Entidade considerada igual:", entity_detected)
            if sentiment_index != 0:
                sentiment_words = [l.lemmatize(word.lower()) for word in sentiment_dictionary[sentiment_index]]
                print ("Palavras sentimento atribuidas a entidade real:", sentiment_words, " - Valor pol.:", sum(calculate_polarity_values(sentiment_words)))
            else:
                sentiment_words = sentence[4]
                print ("Palavras sentimento atribuidas:", sentence[4], " - Valor pol.:", sum(calculate_polarity_values(sentence[4])))
            
        else:
            print ("Nao foi encontrada qualquer referencia a uma entidade.")
            sentiment_words = sentence[4]
            print ("Palavras sentimento atribuidas pelo sistema:", sentence[4], " - Valor pol.:", sum(calculate_polarity_values(sentence[4])))
        
        print ("Classe calculada: ", get_class(sum(calculate_polarity_values(sentiment_words))), " Classe real:" ,sentence_list[4])
        
        if get_class(sum(calculate_polarity_values(sentiment_words))) == sentence_list[4]:
            print ("Certo")
            right.append(get_class(sum(calculate_polarity_values(sentiment_words))))
            polarities_calculated.append(sentence_list[4])
        else:
            print ("Errado")
            wrong.append(get_class(sum(calculate_polarity_values(sentiment_words))))
            polarities_calculated.append(sentence_list[4])
    generate_report_calculated_polarities(right, wrong, polarities_calculated)
        
if __name__ == '__main__':
    start = datetime.now()
    l = WordNetLemmatizer() 
    
    #all_words = nltk.FreqDist()
    
    all_words = {}
    entropy = {}
    #bigram_entropy = {}
    #pos_word_frequency = nltk.FreqDist()
    #neg_word_frequency = nltk.FreqDist()
    #neu_word_frequency = nltk.FreqDist()

    polarity_url_list = {}
    polarity_list = {}
    #positive_sentences = 0
    #negative_sentences = 0
    #featuresize = 300
    
    negations = ["no", "not", "neither", "none", "no one" , "nobody" , "nothing", "nowhere" , "never", \
                 "don't","does not", "doesn't", "nor", "cannot" , "won't", "isn't"]
    positive_intensifiers = ["very", "completely", "much", "more", "extremely", "amazingly", "insanely"]
    negative_intensifiers = ["less", "almost", "quite", "bit", "fairly", "slightly"]
       
    
    #Old example. AFINN + SentiWordnet    
    #===========================================================================
    # try:
    #     a = open("export/sentiment_wordlist_20131018_215835.txt")
    #     try:
    #         polarity_list = dict(map(lambda (k,v): (k,int(v)), [ line.split(':') for line in a ])) 
    #     finally:
    #         a.close()
    # except IOError:
    #     pass
    #===========================================================================
    
    
    polarity_list = generate_afinn_polarity_list() #Sentiment WordList AFINN
    #polarity_list = generate_afinn_swn_polarity_list() #Sentiment WordList AFINN + SWN
    slang_dictionary = get_slang_dictionary()
    
    #Process Database Sentences    
    
    #######################################
    #Entropy
    #calculate_entropy()
    #########################################
    
    try:
        a = open("src/export/entropy_half_training.txt")
        try:
            entropy = dict(map(lambda k_v: (k_v[0],float(k_v[1].rstrip())), [ line.split('\t') for line in a ])) 
        finally:
            a.close()
    except IOError as e:
        print ("I/O error({0}): {1}".format(e.errno, e.strerror))
        pass
    
    pos_word_frequency = calculate_positive_word_frequency()
    neg_word_frequency = calculate_negative_word_frequency()
    neu_word_frequency = calculate_neutral_word_frequency()
    
    print ("Getting the entities list..")
    
    entity_detection = {}
    try:
        f = open("src/data/dataset/replab2013_entities.tsv")
        
        try:
            lines = f.read().splitlines()
        finally:
            f.close()
        for line in lines:
            line_polarity = line.split("\t")
            line_polarity = [s[1:-1] for s in line_polarity] #retirar as aspas das palavras
            
            entity = line_polarity[1].replace("\"", "") #.split()
            entity = entity.strip()
            
            entity_detection[line_polarity[0]] = entity
    except IOError:
            pass
    
    print (entity_detection)
    
    
    tokenized_sentences = {}
    sentences = sentence_database.get_data("dataset")    
    shuffle(sentences)
    print ("Existem " + str(len(sentences)) + " mensagens na BD para treino.")
    
    process_database_sentences() 
    
    print ("Generating Feature Sets.... for training" )
    featuresets = get_featuresets()
    
    print ("Generating training and test set")
    #train_set, test_set = featuresets[11000:], featuresets[:11000]
    train_set = featuresets
    
    print ("Teste")
    
    sentences = sentence_database.get_data("dataset_test")    
    shuffle(sentences)
    print ("Existem " + str(len(sentences)) + " mensagens na BD para teste.")
    
    tokenized_sentences = {}
    process_database_sentences() 
    
    print ("Generating Feature Sets.... for training" )
    featuresets = get_featuresets()
    
    print ("Generating training and test set")
    #train_set, test_set = featuresets[11000:], featuresets[:11000]
    test_set = featuresets
    print ("train_set", len(train_set))
    print ("test_set", len(test_set))
    
    print ("Classifying...")
    classifier = nltk.NaiveBayesClassifier.train(train_set)
    #classifier = nltk.DecisionTreeClassifier.train(train_set)
    #classifier = SklearnClassifier(LinearSVC()).train(train_set)
    #classifier = SklearnClassifier(SGDClassifier()).train(train_set)
    
    refsets = defaultdict(set)
    testsets = defaultdict(set)
  
    for i, (feats, label) in enumerate(test_set):
            refsets[label].add(i)
            observed = classifier.classify(feats)
            testsets[observed].add(i)
              
    #print "Quantidade de features: " + str(featuresize)
    print ('accuracy:', nltk.classify.util.accuracy(classifier, test_set))
    print ('pos precision:', nltk.metrics.precision(refsets['POSITIVE'], testsets['POSITIVE']))
    print ('pos recall:', nltk.metrics.recall(refsets['POSITIVE'], testsets['POSITIVE']))
    print ('neg precision:', nltk.metrics.precision(refsets['NEGATIVE'], testsets['NEGATIVE']))
    print ('neg recall:', nltk.metrics.recall(refsets['NEGATIVE'], testsets['NEGATIVE']))
    print ('neu precision:', nltk.metrics.precision(refsets['NEUTRAL'], testsets['NEUTRAL']))
    print ('neu recall:', nltk.metrics.recall(refsets['NEUTRAL'], testsets['NEUTRAL']))
    
    #classifier.show_most_informative_features(100)
    
    print ("Generating ARFF file...")
    save_arff_file(featuresets, "25_features_VB-ADJ-ADV_Sentiment_Preparacao_Teste")
   
    
    
    #calculate_processing_time()
    #calculate_rules_processing()
    
    print (datetime.now() - start)
    winsound.PlaySound('beep-7.wav', winsound.SND_FILENAME)
    #===========================================================================
    # while True:
    #     user_input = raw_input('\nPlease enter your sentence:\n')
    #     if user_input == "exit":
    #         print "Program terminated."
    #         break
    #     sentence = process_single_sentence(user_input, True)
    #===========================================================================
        #print classifier.classify(get_sentencefeatures(sentence[0], sentence[1], sentence[2], sentence[3], sentence[4], show_info=True))
        
        