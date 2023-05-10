# -*- encoding: utf-8 -*-
'''
Created on 10/10/2013

@author: jmletras
'''
import os, sqlite3
from datetime import datetime
from guess_language import guess_language

    
    
def emoticon_replace(sentence):
    happy = set((":)",":-)","=)",":}",":^)",":=)",";)","(:",";-)"))
    sad = set((":(",":-(","=(",":'("))
    for emoticon in happy:
        sentence = sentence.replace(emoticon, "happy")
    for emoticon in sad:
        sentence = sentence.replace(emoticon, "sad")

    return sentence

def get_sentencespolarity():
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


def store_sentences_db(directory):        
    #c.execute("DROP TABLE dataset_test")
    c.execute("CREATE TABLE if not exists dataset_test (tweet_id, author, entity_id, text, polarity)")
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
            if sentences[3] and (sentences[0] in sentences_polarities):            
                if guess_language(u""+sentences[3]+"") == "en":
                    
                    check_message = c.execute("SELECT COUNT(*) FROM dataset_test WHERE text = ?", (sentences[3],))
                  
                    if check_message.fetchone()[0]==0:
                        sentences[3] = emoticon_replace(sentences[3])
                        sentences.append(sentences_polarities[sentences[0]])
                        c.execute("INSERT INTO dataset_test (tweet_id, author, entity_id, text, polarity) VALUES (?, ?, ?, ?, ?)", (sentences))
                        i+=1
    conn.commit()
    print (str(i)+ " sentences were added to the database")
    
def get_data(data):
    print ("Accessing sentences from database: ", str(data+".db"))
    sentences = []
    conn = sqlite3.connect("src/"+data+".db")
    conn.text_factory = str
    c = conn.cursor()
    c.execute("SELECT * FROM "+ data)   
    for row in c.fetchall():
        sentences.append(row) 
    conn.close()
    return sentences

def get_dataCountByPolarity(polarity):
    conn = sqlite3.connect('src/dataset_train.db')
    conn.text_factory = str
    ci = conn.cursor()
    ci.execute('SELECT COUNT(*) FROM dataset where polarity LIKE "'+polarity+'"')    
    return ci.fetchone()[0]
        
if __name__ == '__main__':
    conn = sqlite3.connect('src/dataset_test.db')
    conn.text_factory = str
    c = conn.cursor()
    
    tweets_directory_training = "src/data/dataset/training/"
    tweets_directory_test = "src/data/dataset/test/"
    polarity_file = "src/data/dataset/test_goldstandard_polarity.dat"
    
    start = datetime.now()
    sentences_polarities = get_sentencespolarity()
    store_sentences_db(tweets_directory_test)
    print ("Positivas", get_dataCountByPolarity("POSITIVE"))
    print ("Negativas", get_dataCountByPolarity("NEGATIVE"))
    print ("Neutro", get_dataCountByPolarity("NEUTRAL"))
    
    print (int(get_dataCountByPolarity("POSITIVE"))+int(get_dataCountByPolarity("NEGATIVE"))+int(get_dataCountByPolarity("NEUTRAL")))
    #print len(get_positive_data())
    conn.close()
    