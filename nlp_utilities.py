from transformers import pipeline
from sentence_transformers import SentenceTransformer
import numpy as np
import traceback
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), "Misc"))
import scraper as scraper
sys.path.append(os.path.join(os.path.dirname(__file__), "Google"))
import google as google



def classifyLabel(sequence, labels):
    try:
        classifier = pipeline("zero-shot-classification",
                        model="facebook/bart-large-mnli")
        return classifier(sequence, labels)
    except TypeError as e:
        #Send an email
        print("An unexpected error has occured clasifying labels \n Sequence:" + sequence + "\nLabels: " + labels)
        traceback.print_exc()
        return {}

def automateAnswer (item, request):
    qa_model = pipeline("question-answering")

    out = google.main(item, request)
    return out
    #     question = google.search_term
    #     context=google.output[google.A]
    #     answer = qa_model(question = question, context = context)
    #     return answer


def extraSentences(item,goal, package):
    manual_input = {}

    def cosine_similarity(sentence_embeddings, ind_a, ind_b):
        s = sentence_embeddings
        return np.dot(s[ind_a], s[ind_b]) / (np.linalg.norm(s[ind_a]) * np.linalg.norm(s[ind_b]))


    def pak_sentence(item,goal, package):

        model = SentenceTransformer('bert-base-nli-mean-tokens')
        desired_sentence = f"what is the {goal} of the {item}?"

        sentences = [desired_sentence]
        
        sentences += package

        sentence_embeddings = model.encode(sentences)

        out = []
        for i in range(1,len(sentences)):
            out.append(cosine_similarity(sentence_embeddings, 0, i))
        return sentences, out

    sentences, out = pak_sentence(item,goal, package)

    # print(sentences[1:len(sentences)], end = "\n")
    # print(out)
    try:
        if max(out) >  1: #some value that is low (0.5)
            return sentences[out.index(max(out))+1]
            # print(f"""The closest People Also Ask question is: {sentences[out.index(max(out))+1]} \nThere is a similarity of {max(out)}""")
        else: 
            return 0
    except:
        return 0