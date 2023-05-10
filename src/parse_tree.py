# -*- encoding: utf-8 -*-
'''
Created on 30 de Mai de 2013

@author: jmletras
'''
import nltk, re

from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tag import pos_tag
import os, sqlite3
from guess_language import guess_language
#import machinelearning


#===============================================================================
# lista =["1", "2", "3"]
# def split_on_caps(str, show=False, key="", teste=False):   
#     str = re.sub("[#$%&*\-]", "", str)
#     str = re.sub(r'([a-z])([A-Z])', r'\1 \2', str)
#     if show==True:
#         print re.findall(r"[\w']+|[.,!?;\"]", str)
#     else:
#         print "Não mostrar"
#     if teste==True:
#         print "Lista:\n", lista
#===============================================================================

def emoticon_replace(sentence):
    happy = set((":)",":-)","=)",":}",":^)",":=)",";)","(:",";-)"))
    sad = set((":(",":-(","=(",":'("))
    for emoticon in happy:
        sentence = sentence.replace(emoticon, "happy")
    for emoticon in sad:
        sentence = sentence.replace(emoticon, "sad")

    return sentence

def get_sentencespolarity(polarity_file):
    polarity = {}
    try:
        f = open(polarity_file)
        
        try:
            lines = f.read().splitlines()
        finally:
            f.close()
        for line in lines:
            line_polarity = line.split("\t")
            line_polarity = [s[1:-1] for s in line_polarity] #retirar as aspas das palavras
            polarity[line_polarity[1]] = line_polarity[2]
    except IOError:
            pass
    return polarity

def get_sentencesfiltering(filtering_file):
    filtering = {}
    try:
        f = open(filtering_file)
        
        try:
            lines = f.read().splitlines()
        finally:
            f.close()
        for line in lines:
            line_polarity = line.split("\t")
            line_polarity = [s[1:-1] for s in line_polarity] #retirar as aspas das palavras
            filtering[line_polarity[1]] = line_polarity[2]
    except IOError:
            pass
    return filtering

def store_sentences_db(c, directory):        
    #c.execute("DROP TABLE full_dataset")
    c.execute("CREATE TABLE if not exists full_dataset (tweet_id, author, entity_id, text, polarity, filtering)")
    i=0
    
    for filess in os.listdir(directory):    
        try:
            f = open(directory+filess)
            try:
                lines = f.read().splitlines()[1:]
                print (f)
            finally:
                f.close()
        except IOError:
                pass
        for line in lines:
            sentences = line.split("\t")
            sentences = [s[1:-1] for s in sentences]
                        
            if guess_language(u""+sentences[3]+"") == "en":
                
                check_message = c.execute("SELECT COUNT(*) FROM full_dataset WHERE text = ?", (sentences[3],))
              
                if check_message.fetchone()[0]==0:
                    sentences[3] = emoticon_replace(sentences[3])
                    if sentences[0] in sentences_polarities:
                        sentences.append(sentences_polarities[sentences[0]])
                    else:
                        sentences.append("")
                    if sentences[0] in sentences_polarities:
                        sentences.append(sentences_filtering[sentences[0]])
                    else : 
                        sentences.append("")
                    c.execute("INSERT INTO full_dataset (tweet_id, author, entity_id, text, polarity, filtering) VALUES (?, ?, ?, ?, ?, ?)", (sentences))
                    i+=1
                    print (sentences)
    
    print (str(i)+ " sentences were added to the database")

def create_filtering_dataset():
    conn = sqlite3.connect('full_dataset.db')
    conn.text_factory = str
    c = conn.cursor()    
    
    
    store_sentences_db(c, filtering_tweets_directory, sentences_polarities, sentences_filtering)
    
    conn.commit()
    
def extract_entity_names(t):
    entity_names = []
    if hasattr(t, 'node') and t.node:
        if t.node == ('NE'):
            if len(t.node) > 1:
                entity_names.append(' '.join(child[0] for child in t))
            #for child in t:
            #    entity_names.append(child[0])
        #=======================================================================
        # if t.node == ('NP'):
        #     for child in t:
        #         if child[1] == "NNP":
        #             entity_names.append(child[0])
        #=======================================================================
        else:
            for child in t:
                entity_names.extend(extract_entity_names(child))
    return entity_names

def sentence_polarity(sentence_tokens):
    sentence_polarity = []
    negations = ["no", "not", "neither", "none", "no one" , "nobody" , "nothing", "nowhere" , "never", \
                 "don't","does not", "doesn't", "nor", "cannot" , "won't", "isn't"]
    number_negations = 0

    for word in sentence_tokens:   
        if str(word) in negations:
            number_negations += 1
            #features["has_negation"] = 1
            print ("negation")
            
                
        else:
            word_polarity = polarity_list.get(word, 0)
            if number_negations > 0:
                if word_polarity > 2:
                        
                    #i = int(word_polarity / 2)-1
                    sentence_polarity.append(word_polarity - 2)
                    #print int(word_polarity / 2), i
                    number_negations = 0
                elif word_polarity < -2:
                        
                    #i = int(word_polarity / 2)+1
                    sentence_polarity.append(word_polarity + 2)
                    number_negations = 0
                else: 
                    sentence_polarity.append(-1 * word_polarity)
                    #number_negations = 0
            else:
                sentence_polarity.append(word_polarity)    
    return sentence_polarity

def getTreeNodes(tree):
    nodes = []
    if hasattr(tree, 'node') and tree.node:
        if tree.node == ('S') or tree.node == ('NP'):
            for child in tree:
                if hasattr(child, 'node') and child.node:
                    if child.node == ('NP'):
                        
                    #nodes.extend(getTreeNodes(child))
                        nodes.append(child)
        #else:
            #nodes.append(tree.node)
    return nodes

def returnNodeChilds(tree):
    childs = []
    if hasattr(tree, 'node') and tree.node:
        for child in tree:
            childs.extend(child)
    return childs

def get_words_from_nodes(tree):
    words = []
    if hasattr(tree, 'node') and tree.node:
        if tree.node != "S":
            for child in tree:
                if hasattr(child, 'node') and child.node:
                    words.extend(get_words_from_nodes(child))
                else:
                    words.append((tree.node, child[0]))
        else:
            for child in tree:
                words.extend(get_words_from_nodes(child))
    
    return words

def getSentimentWordsFromNodes(tree):
    sentimentLeafs = []
    if hasattr(tree, 'node') and tree.node:
        if tree.node == ('VP') or tree.node == ('ADJ'):
            for child in tree:
                if hasattr(child, 'node') and child.node:
                    sentimentLeafs.extend(getSentimentWordsFromNodes(child))
                else:
                    sentimentLeafs.append(child[0])
        else:
            for child in tree:
                sentimentLeafs.extend(getSentimentWordsFromNodes(child))
    
    return sentimentLeafs

def getSentimentIndexFromNodes(tree, i=0):
    sentimentLeafs = []
   
    if hasattr(tree, 'node') and tree.node:
        
        if tree.node == ('VP') or tree.node == ('ADJ'):
            for child in tree:
                
                sentimentLeafs.append(i)
                i += 1
        else:
            for child in tree:
                
                i += 1
                sentimentLeafs.extend(getSentimentIndexFromNodes(child , i))
        
    
    return sentimentLeafs

def sentiment_assigning(tree, entities, sentiment_words):
    #tokens, uppercase, url, entities, sentiment_words, tree
    #print "Árvore:"
    #print tree
    sentiment = []
    #sentiment = {}
    #print "Entities: ", str(len(sentiment))
    #print sentiment
    #print "Sentiment: ", str(sentiment_count)
    #print sentence[3]
    #entities = sentence[3]
    #tree = sentence[5]
    #sentiment_words = sentence[4]
    #print sentiment
    if hasattr(tree, 'node') and tree.node:
        #if tree.node == ('NP'):
            #for child in tree:      
                #if hasattr(child, 'node') and child.node:
        if tree.node == ('NE'):
            sentiment.append("[Entity]")
            #print "Entity Found "
            #sentiment.append(len(sentiment)+1)
            #entity = ""
            #for child in tree:
                #entity += child[0]
            #    print "Entity", str(child[0])
            #    sentiment.extend(sentiment_assigning(child, entities, sentiment_words))
                        #sentiment.update((sentiment_assigning(child, entities, sentiment_words, entities_count, sentiment_count)))          
                        
        
        elif tree.node == ('VP') or tree.node == ('ADJ'):
            #print "Tree ADJ VP"
            
            for child in tree:
                #if len(sentiment) > 0:
                sentiment.append(child[0])
                
                #===============================================================
                # if hasattr(child, 'node') and child.node:
                #     sentiment.update((sentiment_assigning(child, entities, sentiment_words, entities_count, sentiment_count)))
                # else:
                #     print "VPADJ child:", child[0]
                #     if entities_count > 0:
                #          
                #         if entities_count in sentiment:
                #             sentiment_list = sentiment[entities_count]
                #             sentiment_list.append(child[0])
                #             sentiment[entities_count] = sentiment_list
                #         else:
                #             sentiment[entities_count] = [child[0]]
                #          
                #     sentiment_count += 1
                #     print "Sentiment:", sentiment_count
                # sentiment.update((sentiment_assigning(child, entities, sentiment_words, entities_count, sentiment_count)))
                #===============================================================
        #=======================================================================
        # elif tree.node == ('PNT'):
        #     for child in tree:
        #         print "PNT:", child
        #         if child[1] == ".":
        #             if entities_count == len(entities) and sentiment_count == len(sentiment_count):
        #                 for i in range(0, len(sentiment_words)):
        #                     sentiment[i] = sentimentLeafs
        #              
        #             elif entities_count < len(entities):
        #                  
        #                 if sentiment_count < len(sentiment_count):
        #                     for i in range(len(sentiment), entities_count):
        #                         sentiment[i] = sentimentLeafs
        #                         sentiment_count = 0
        #                         sentimentLeafs = []
        #                      
        #                 elif sentiment_count == len(sentiment_words):
        #                     for i in range(len(sentiment), entities_count):
        #                         sentiment[i] = sentimentLeafs
        #                     for i in range(len(sentiment[i]), len(entities)):
        #                         sentiment[i] = []  
        #         sentiment.update((sentiment_assigning(child, entities_count, sentiment_count)))      
        #=======================================================================
        elif tree.node == ('PNT'):
            sentiment.append("[PNT]")
        else:
            for child in tree: 
                #print "Próxima árvore: ", child[0]   
                sentiment.extend(sentiment_assigning(child, entities, sentiment_words))
    
    return sentiment  

def get_dictionary_sentiment(list):
    
    dictionary = {}
    sentiment_words = []
    entities = 0
    pun = 0
     
    
    for item in list:
        if item != "[PNT]":
            if item == "[Entity]":
                entities += 1
                
                pun = 0
                num_ent = len(dictionary)
                
                dictionary[num_ent+1] = sentiment_words
            else:
                #if entities in dictionary and len(dictionary[entities]) < 1 and pun == 0:
                if entities != 0 and pun == 0:
                                       
                    for x in range(len(dictionary), len(dictionary)-entities, -1): 
                        dictionary[x].append(item)
                else:
                    sentiment_words.append(item)
            
        else:
            
            if entities != 0:
                pun = 1
                entities = 0
                #===============================================================
                # if len(dictionary) == 0:
                #     for x in range(1, entities+1):
                #         dictionary[x] = sentiment_words
                # else:
                #     print dictionary[entities]
                #     print sentiment_words
                #     dictionary[entities] = sentiment_words
                #===============================================================
            if list.count("[Entity]") > 1:   
                sentiment_words = []
    return dictionary
                    
    
def get_data():
    sentences = []
    conn = sqlite3.connect('src/full_dataset.db')
    conn.text_factory = str
    c = conn.cursor()
    c.execute("SELECT * FROM full_dataset")   
    for row in c.fetchall():
        sentences.append(row) 
    conn.close()
    return sentences

def generateParseTree(sentence_tokens):
    
    #sentence_tokens = word_tokenize(sentence_tokens)
    #print tokens
    
    #print "Polarity"
    #print sentence_polarity(sentence_tokens)
    
    pos = pos_tag(sentence_tokens)
    #print "Pos"
    #-print pos
    
    chunked_sentences = nltk.ne_chunk(pos, binary=True)
    
    grammar = """ 
              PNT: {<.|,>?}              
              CONJP: {<PNT>?<CC>+}
              ADJ: {<RB.*>*<DT>*<JJ.*>}              
              NP: {<DT|PRP\$|PP\$>*<NNP.*|NE>+} # Chunk nouns
              VP: {<RB.*>*<DT>*<VB.*>+<JJ.*|RBR>*} # Chunk verbs        
              """
    #print grammar            
    cp2 = nltk.RegexpParser(grammar)
    parseTree = cp2.parse(chunked_sentences)
    #parseTree.draw()
    #print get_words_from_nodes(parseTree)
    #print getSentimentIndexFromNodes(parseTree)
    #print getTreeNodes(parseTree)
    #print extract_entity_names(parseTree)
    
    #print parseTree
    return parseTree
    
    

    #parseTree.draw()
def remove_strings(s, tags):
    new = []
    for word in s.split(' '):
        if word not in tags:
            new.append(word)
        
    return " ".join(new)

def calculate_filtering(): 
    filtering_list = {}
    for line in sentences:
        sentence = line[3]
        print (sentence)
        url = re.findall(r'(https?://\S+)', sentence)
        if len(url) > 0:
            url = url[0]
            sentence = remove_strings(sentence, url)
            
        entities = extract_entity_names(chunk(sentence))
        
        if len(entities) > 0:
            filtering_list[line[0]] = "RELATED"
            print (entities)
            print ("Encontrado")
        else:
            filtering_list[line[0]] = "UNRELATED"
            print ("Nao encontrado") 
    return filtering_list
        
def compare_filtering(calculated_filtering):
    
    print ("Comparing filtering...")
    true_filtering = {}
    equal = 0
    different = 0
    
    right = []
    wrong = []
    filtering_calculated = []

    try:
        f = open(filtering_file)
        
        try:
            lines = f.read().splitlines()
        finally:
            f.close()
        for line in lines:
            real_filtering = line.split("\t")
            real_filtering = [s[1:-1] for s in real_filtering]
            true_filtering[real_filtering[1]] = real_filtering[2]
    except IOError:
            pass
        
    for k,v in calculated_filtering.iteritems():
        if k in true_filtering:
            if v == true_filtering[k]:
                equal += 1
                right.append(v)
                filtering_calculated.append(true_filtering[k])
            else:
                    
                different += 1
                wrong.append(v)
                filtering_calculated.append(true_filtering[k])
            
    print ("----Filtragem----")
    print ("Filtragem real - Relacionados: " ,filtering_calculated.count("RELATED"), " N Relacionados: " ,filtering_calculated.count("UNRELATED"))
    
    print ("Filtragem calculada - Correctos:", right.count("RELATED"), right.count("UNRELATED")," - Errados:", \
        wrong.count("RELATED"), wrong.count("UNRELATED"))
        
    print ("------------Acertos-----------------")
    print ("Correctos: ", equal, " - Errados:", different)
    print ("Taxa de Acerto: {0:.3f}".format(equal/float(len(calculated_filtering))))
    
    print ("------------Precisão-----------------")
    print ("Relacionados: {0:.3f}".format(right.count("RELATED")/float(right.count("RELATED")+wrong.count("RELATED"))))
    print ("N Relacionados: {0:.3f}".format(right.count("UNRELATED")/float(right.count("UNRELATED")+wrong.count("UNRELATED"))))

    print ("------------Cobertura-----------------")
    print ("Relacionados: {0:.3f}".format(right.count("RELATED")/float(filtering_calculated.count("RELATED"))))
    print ("N Relacionados: {0:.3f}".format(right.count("UNRELATED")/float(filtering_calculated.count("UNRELATED"))))
    
    print ("------------Medida-F-----------------")
    print ("Relacionados: {0:.3f}".format(2*((right.count("RELATED")/float(right.count("RELATED")+wrong.count("RELATED"))*right.count("RELATED")/float(filtering_calculated.count("RELATED")))/  \
                                         (right.count("RELATED")/float(right.count("RELATED")+wrong.count("RELATED"))+right.count("RELATED")/float(filtering_calculated.count("RELATED"))))))
    print ("N Relacionados: {0:.3f}".format(2*((right.count("UNRELATED")/float(right.count("UNRELATED")+wrong.count("UNRELATED"))*right.count("UNRELATED")/float(filtering_calculated.count("UNRELATED")))/  \
                                         (right.count("UNRELATED")/float(right.count("UNRELATED")+wrong.count("UNRELATED"))+right.count("UNRELATED")/float(filtering_calculated.count("UNRELATED"))))))


l = WordNetLemmatizer() 
#filtering_tweets_directory = "data/dataset/training/"
polarity_file = "src/data/dataset/goldstandard_polarity.dat"
filtering_file = "src/data/dataset/goldstandard_filtering.dat"
#sentences_polarities = get_sentencespolarity(polarity_file)
#sentences_filtering = get_sentencesfiltering(filtering_file)
sentences = get_data()
