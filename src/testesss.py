'''
Created on 15 de Jan de 2014

@author: boss
'''
def calculate_processing_time():
    print "Generating sentences to calculate the processing time..." 
    sentences_list = []
    try:
        a = open("data/50_sentences.txt")
        try:
            sentences_list = a.read().splitlines()
            #sentences_list = lines.split("\t")
            #sentences_list = [ line.split('\t') for line in a ]
        finally:
            a.close()
    except IOError:
        print "Ocorreu um erro ao ler o ficheiro" , 
        pass
    print "Foram lidas ", str(len(sentences_list)), "mensagens."
    
    print sentences_list
    #print lines
    
    #for sentence in sentences_list:
    #    print sentence
    
        #sentence = process_single_sentence(sentence, True)
        #print classifier.classify(get_sentencefeatures(sentence[0], sentence[1], sentence[2], sentence[3], sentence[4], show_info=True))
    
    
if __name__ == '__main__':
    calculate_processing_time()