# -*- encoding: utf-8 -*-
'''
Created on 30 de Mai de 2013

@author: jmletras
'''

import re, os, sqlite3, time, operator
from nltk.corpus import stopwords
from nltk import *
#===============================================================================
# from nltk.tokenize import sent_tokenize, word_tokenize
# from nltk.stem.wordnet import WordNetLemmatizer
# from nltk.chunk import ne_chunk
# from nltk.tag import pos_tag
# from dircache import listdir
#===============================================================================
from numpy.core.defchararray import splitlines
from datetime import datetime
from collections import defaultdict

sentiWord_file = "src/data/SentiWordNet_3.0.0_20130122.txt"
affin_file = "src/data/AFINN/AFINN-111.txt"    
polarity_file = "src/data/dataset/goldstandard_polarity.dat"

def create_sentimentwordlist():
    print ("Generating and joining Sentiment WordList..")
    sentiment_wordlist = {}
    
    try:
        a = open(affin_file)
        try:
            sentiment_wordlist = dict(map(lambda k,v: (k,int(v)), [ line.split('\t') for line in a ])) 
        finally:
            a.close()
    except IOError:
        pass
    
    print ("AFIIN Words: " + str(len(sentiment_wordlist)))
    
    try:
        sw = open(sentiWord_file)
        try:
            lines = sw.read().splitlines() 
        finally:
            sw.close()
    except IOError:
        pass
 
    for line in lines:
        if not line.startswith('#'):
            pos, id, posScore, negScore, SynsetTerms, gloss = line.split('\t')
    
            words = SynsetTerms.split(' ')
            if (posScore != "" and  negScore != ""): #and (posScore != "0" or  negScore != "0"):
                if float(posScore) > float(negScore):
                    if float(posScore) >= 0.625:
                        polarity = 4
                    elif float(posScore) >= 0.50 and float(posScore) < 0.625:
                        polarity = 3
                    elif float(posScore) > 0.20 and float(posScore) < 0.50:
                        polarity = 2
                    elif float(posScore) > 0 and float(posScore) < 0.20:
                        polarity = 1
                    else:
                        polarity = 0                    
                elif float(posScore) < (negScore):
                    if float(negScore) >= 0.65:
                        polarity = -3
                    elif float(negScore) >= 0.50 and float(negScore) < 0.65:
                        polarity = -2
                    elif float(negScore) >= 0.20 and float(negScore) < 0.50:
                        polarity = -1
                    elif float(negScore) > 0 and float(negScore) < 0.20:
                        polarity = 0
                    else:
                        polarity = 0 
                else:
                    polarity = 0
                 
                #===============================================================
                # if len(words) > 1:
                #     for word in words:  
                #         word = (re.sub('[^A-Za-z]+', '', word))
                #         if word not in stopwords.words("english") and word not in sentiment_wordlist:
                #             sentiment_wordlist[word] = polarity
                # else:
                #     word = (re.sub('[^A-Za-z]+', '', SynsetTerms))
                #     if word not in stopwords.words("english") and word not in sentiment_wordlist:
                #         sentiment_wordlist[word] = polarity
                #===============================================================
                for word in words:
                    if word not in sentiment_wordlist:
                        sentiment_wordlist[word] = polarity
    print ("Sentiment Total Words: " + str(len(sentiment_wordlist)))
    return sentiment_wordlist
    
def write_list_to_file(list, file):
    f = open("src/export/"+file+".txt", "w")
    for element in list:
        f.write(str(element)+"\n")
    f.close()
    
def write_dict_to_file(dict, file):
    actual = datetime.now().strftime("%Y%m%d_%H%M%S")
    f = open("src/export/"+file+"_"+actual +".txt", "w")
    for k, v in dict.iteritems():
        f.write(str(k)+"\t"+str(v)+"\n")
    f.close()
    
def extract_entity_names():
    print ("Extracting entity names...")
    entities = []
    for line in sentences:
        chunks = ne_chunk(pos_tag(word_tokenize(line[3])))
        entities.extend([chunk[0][0] for chunk in chunks if hasattr(chunk, 'node')])
    print ("Done: Entity names extracted.")
    write_list_to_file(set(entities), "generated_entities")
    return set(entities)

def extract_hashtags(s):
    return set(re.findall(r'(?i)\#\w+', s))

def remove_hashtags(s, tags):
    new_sentence = s
    for word in s.split(' '):
            if word in tags:
                new_sentence = s.strip(word)
    return new_sentence

def add_final_dot(s):
    if len(s[::-1]) > 1:
            s = s + "."
    return s

def get_sentence_filtering(entities_list):
    print ("Filtering sentences...")
    
    sentence_filtering = {}

    for line in sentences:
        tokens = word_tokenize(line[3]) 
        if len(set(tokens) & set(entities_list)) > 0:
            sentence_filtering[line[0]] = "RELATED"
        else:
            sentence_filtering[line[0]] = "UNRELATED"
    print ("Done: Filtering.")    
    return sentence_filtering

              
def get_sentence_polarity_swn():    
    senti_wordnet = create_sentimentwordlist()()   
    l = WordNetLemmatizer() 
    tweet_polarity={}
    for line in sentences:
        #sentence = emoticon_replace(line)
        
        pos = neg = 0
        tokens = word_tokenize(line[3])

        for word in tokens:
            word_sentiment = senti_wordnet.word_polarity(l.lemmatize(word.lower()))
            
            if word_sentiment:
                pos += float(word_sentiment[0])
                neg += float(word_sentiment[1])
        if pos > neg:
            tweet_polarity[line[0]] = "POSITIVE"
        elif pos < neg:
            tweet_polarity[line[0]] = "NEGATIVE"
        else:
            tweet_polarity[line[0]] = "NEUTRAL"
    return (tweet_polarity)

def get_sentence_polarity_affin(): 
    l = WordNetLemmatizer() 
    afinn = dict(map(lambda k,v: (k,int(v)), [ line.split('\t') for line in open(affin_file) ]))
    tweet_polarity={}
    for line in sentences:
        tokens = word_tokenize(line[3])
        polarity = sum(map(lambda word: afinn.get(l.lemmatize(word.lower()), 0), tokens))
        
        if polarity > 0:
            tweet_polarity[line[0]] = "POSITIVE"
        elif polarity < -2:
            tweet_polarity[line[0]] = "NEGATIVE"
        else:
            tweet_polarity[line[0]] = "NEUTRAL"
    return tweet_polarity

def get_sentence_polarity_affin_sw(): 
    l = WordNetLemmatizer() 
    sentiment_wordlist = create_sentimentwordlist()
    
    print ("Total polarities AFINN+SWN: ", len(sentiment_wordlist))
    tweet_polarity={}    
    
    #f = open("export/generated_polarity_values.txt", "w")
    
    print ("Generating sentence polarities...")
    for line in sentences:
        sentence = line[3]

        #hashtags = extract_hashtags(sentence)
        #sentence = remove_hashtags(sentence, hashtags)
        #sentence = add_final_dot(sentence)
                       
        polarity = 0
        tokens = word_tokenize(sentence)
        
        polarity_list = []
        number_negations = 0
        positive = 1
        negative = 1
        
        #entities = get_entity(tokens)         
        #tokens = [x for x in tokens if x not in entities] 
        
        #Negations
        
        #=======================================================================
        # for word in tokens:
        #     word = l.lemmatize(word.lower())
        #     word_polarity = sentiment_wordlist.get(word, 0)
        #     if word in negations:
        #         number_negations += 1
        #                  
        #     if number_negations > 0:                    
        #         if word_polarity != 0:
        #             polarity_list.append(-1 * word_polarity)
        #             number_negations = 0
        #         else:
        #             polarity_list.append(word_polarity)
        #     else:
        #         polarity_list.append(word_polarity)
        #=======================================================================

        #Negations but not totally inverted
        
        for word in tokens:
            word = l.lemmatize(word.lower())
            word_polarity = sentiment_wordlist.get(word, 0)
            if word in negations:
                number_negations += 1
                          
                if number_negations > 0:                    
                    if word_polarity > 2:
                        i = int(word_polarity / 2)-1
                        polarity_list.append(i)
                        number_negations = 0
                    elif word_polarity < -2:
                        i = int(word_polarity / 2)+1
                        polarity_list.append(i)
                        number_negations = 0
                    else:
                        polarity_list.append(-1 * word_polarity)
                else:
                    polarity_list.append(word_polarity)
                     
            else:
                polarity_list.append(word_polarity)
        
        
        #Positive & Negative Intensifiers
        #=======================================================================
        # for word in tokens:
        #     word = l.lemmatize(word.lower())
        #     if word in positive_intensifiers:
        #         positive += 1
        #         negative = 0
        #     elif word in negative_intensifiers:
        #         negative += 1
        #         positive = 0
        #     else:
        #         word_polarity = sentiment_wordlist.get(word, 0)
        #         if positive > 0:
        #             if word_polarity != 0:
        #                 positive = 0
        #                 polarity_list.append(1.3* word_polarity)
        #             else:
        #                 positive = 0
        #                 polarity_list.append(word_polarity)
        #         elif negative > 0:
        #             if word_polarity != 0:
        #                 negative = 0
        #                 polarity_list.append(-1.3* word_polarity)
        #             else:
        #                 negative = 0
        #                 polarity_list.append(word_polarity)
        #         else:
        #             polarity_list.append(word_polarity)
        #=======================================================================
                
        polarity = sum(polarity_list)
        
        #Conjunto de caracteristicas para Weka
        #tweet_polarity[line[0]] = polarity, max(polarity_list),min(polarity_list)        
        
        #Somar polaridade através do dicionário de sentimentos AFINN (quando não se utilizam calculos de negações ou intensificadores)
        #polarity = sum(map(lambda word: sentiment_wordlist.get(l.lemmatize(word.lower()), 0), tokens))
        
        
        #f.write(str(line[0])+" "+str(line[3])+" "+str(polarity)+"\n")
    
        
        if int(polarity) > 0:
            tweet_polarity[line[0]] = "POSITIVE"
        elif int(polarity) < -2:
            tweet_polarity[line[0]] = "NEGATIVE"
        else:            
            tweet_polarity[line[0]] = "NEUTRAL"
    
    #f.close()
    
    print ("Done: Sentence polarities.")
    #Juntar AFINN ao SentiWordNet mantendo as caracteristicas de polaridade do SWN              
    #===========================================================================
    # print "Adicionando polaridade de AFINN"
    # for k,v in afinn.iteritems():
    #     if k not in senti_wordnet.sentiwordnet():
    #         if v > 2:
    #             senti_wordnet.add_word(v, (1, 0))
    #         elif v > 0 and v <= 2:
    #             senti_wordnet.add_word(v, (0.5, 0))
    #         elif v > -1 and v <= 0:
    #             senti_wordnet.add_word(v, (0.0, 0.0))
    #         elif v >= -3 and v <= -1:
    #             senti_wordnet.add_word(v, (0.0, 0.5))
    #         elif v == -4:
    #             senti_wordnet.add_word(v, (0, 1))
    #             
    #             
    # print "SentiWordNet + AFINN lexicon: " , len(senti_wordnet.sentiwordnet())
    # tweet_polarity={}
    # for line in sentences:
    #     pos = neg = 0
    #     tokens = nltk.word_tokenize(line[3])
    #     for word in tokens:
    #         word_sentiment = senti_wordnet.word_polarity(word.lower())
    #         if word_sentiment:
    #             pos += float(word_sentiment[0])
    #             neg += float(word_sentiment[1])
    #     if pos > neg:
    #         tweet_polarity[line[0]] = "POSITIVE"
    #     elif pos < neg:
    #         tweet_polarity[line[0]] = "NEGATIVE"
    #     else:
    #         tweet_polarity[line[0]] = "NEUTRAL"
    #===========================================================================
    return tweet_polarity
        
        
#===============================================================================
# def compare_filtering(sentence_filtering):
#     print "Comparing filtering..."
#     original_entities = {}
#     right = []
#     wrong = []
#     
#     try:
#         f = open(filtering_file)        
#         try:
#             lines = f.read().splitlines()
#         finally:
#             f.close()
#         for line in lines:
#             sentences = line.split("\t")
#             sentences = [s[1:-1] for s in sentences]
#             original_entities[sentences[1]] = sentences[2]
#     except IOError:
#             pass
#         
#     for k,v in sentence_filtering.iteritems():
#         if v == original_entities[k]:
#             right.append(v)
#         else:
#             wrong.append(v)
#             
#     print "------Entidades------"        
#     print "Correctos: ", len(right), " - Errados:", len(wrong)
#     print "{0:.3f}".format(len(right)/float(len(right)+len(wrong)))
#     print right.count("RELATED"), wrong.count("RELATED"), right.count("UNRELATED"), wrong.count("UNRELATED")
#     
#     print "------------Precisão-----------------"
#     print "Relacionado: {0:.3f}".format(right.count("RELATED")/float(right.count("RELATED")+wrong.count("RELATED")))
#     print "Nao relacionado: {0:.3f}".format(right.count("UNRELATED")/float(right.count("UNRELATED")+wrong.count("UNRELATED")))
#     
#     print "------------Cobertura-----------------"
#     print "Relacionado: {0:.3f}".format(right.count("RELATED")/float(sum(x == "RELATED" for x in original_entities.values())))
#     print "Nao relacionado: {0:.3f}".format(right.count("UNRELATED")/float(sum(x == "UNRELATED" for x in original_entities.values())))
#     
#     print "------------Medida-F-----------------"
#     print "Relacionado: {0:.3f}".format(2*((right.count("RELATED")/float(right.count("RELATED")+wrong.count("RELATED"))*right.count("RELATED")/float(sum(x == "RELATED" for x in original_entities.values())))/  \
#                                          (right.count("RELATED")/float(right.count("RELATED")+wrong.count("RELATED"))+right.count("RELATED")/float(sum(x == "RELATED" for x in original_entities.values())))))
#     print "Nao relacionado: {0:.3f}".format(2*((right.count("UNRELATED")/float(right.count("UNRELATED")+wrong.count("UNRELATED"))*right.count("UNRELATED")/float(sum(x == "UNRELATED" for x in original_entities.values())))/  \
#                                          (right.count("UNRELATED")/float(right.count("UNRELATED")+wrong.count("UNRELATED"))+right.count("UNRELATED")/float(sum(x == "UNRELATED" for x in original_entities.values())))))
#     
#===============================================================================
def compare_polarities():
    
    print ("Comparing polarities...")
    true_polarity = {}
    equal = 0
    different = 0
    
    right = []
    wrong = []
    polarities_calculated = []

    try:
        f = open(polarity_file)
        
        try:
            lines = f.read().splitlines()
        finally:
            f.close()
        for line in lines:
            real_polarity = line.split("\t")
            real_polarity = [s[1:-1] for s in real_polarity]
            true_polarity[real_polarity[1]] = real_polarity[2]
    except IOError:
            pass
        
    for k,v in calculated_polarities.iteritems():
        if k in true_polarity:
            if v == true_polarity[k]:
                equal += 1
                right.append(v)
                polarities_calculated.append(true_polarity[k])
            else:
                    
                different += 1
                wrong.append(v)
                polarities_calculated.append(true_polarity[k])
            
    print ("----Polaridade----")
    print ("Polaridade real - Positivos: " ,polarities_calculated.count("POSITIVE"), " Negativos: " ,polarities_calculated.count("NEGATIVE"), \
        "Neutros: " ,polarities_calculated.count("NEUTRAL"))
    
    print ("Polaridade calculada - Correctos:", right.count("POSITIVE"), right.count("NEGATIVE"), right.count("NEUTRAL")," - Errados:", \
        wrong.count("POSITIVE"), wrong.count("NEGATIVE"), wrong.count("NEUTRAL"))
        
    print ("------------Acertos-----------------")
    print ("Correctos: ", equal, " - Errados:", different)
    print ("Taxa de Acerto: {0:.3f}".format(equal/float(len(calculated_polarities))))
    
    print ("------------Precisão-----------------")
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
                                         (right.count("NEUTRAL")/float(right.count("NEUTRAL")+wrong.count("NEUTRAL"))+right.count("NEUTRAL")/float(polarities_calculated.count("NEUTRAL"))))))               
                                      
             
if __name__ == '__main__':
    #nltk.download()
    
    conn = sqlite3.connect('src/dataset.db')
    conn.text_factory = str
    c = conn.cursor()
    
    negations = ["no", "not", "neither", "none", "no one" , "nobody" , "nothing", "nowhere" , "never", \
                 "don't","does not", "doesn't", "nor", "n't"]
    positive_intensifiers = ["very", "completely", "much", "more", "extremely", "amazingly", "insanely"]
    negative_intensifiers = ["less", "almost", "quite", "bit", "fairly", "slightly"]
    
    
    #filtering_file = "data/REPLAB2013_BASELINE_FILTERING.tsv"

    
    
    start = datetime.now()
    
    sentences = []
    c.execute("SELECT * FROM dataset")
    for row in c.fetchall():
            sentences.append(row)
    #print len(sentences)        
    #Extract Bigrams
    #bigrams_list = extract_top_bigrams(50)
   
    #Calculate Filtering
    #entity_names = extract_entity_names()
    #sentence_filter_entity = get_sentence_filtering(entity_names)
    #print compare_filtering(sentence_filter_entity)
    
    #Calculate Polarities     
    #calculated_polarities = get_sentence_polarity_swn() #Calcular polaridade com sentiWordNet
    #calculated_polarities = get_sentence_polarity_affin()    #Calcular polaridade com AFINN
    calculated_polarities = get_sentence_polarity_affin_sw()
      
    #print writeArffFile()
    compare_polarities()
    
    
    conn.close()
    
    end = datetime.now()
    time = end - start
    print (time)