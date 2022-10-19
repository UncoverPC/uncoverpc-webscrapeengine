from sentence_transformers import SentenceTransformer
import numpy as np

import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), "Google"))
import google as google

def cosine_similarity(sentence_embeddings, ind_a, ind_b):
    s = sentence_embeddings
    return np.dot(s[ind_a], s[ind_b]) / (np.linalg.norm(s[ind_a]) * np.linalg.norm(s[ind_b]))


def pak_sentence():

    model = SentenceTransformer('bert-base-nli-mean-tokens')
    desired_sentence = google.search_term

    sentences = [desired_sentence]

    sentences += google.output[google.PAK]
    sentence_embeddings = model.encode(sentences)

    out = []
    for i in range(1,len(sentences)):
        out.append(cosine_similarity(sentence_embeddings, 0, i))
    return sentences, out
    

if (google.output[google.HA] == '' and google.output[google.A] == ''):
    # try:
    sentences, out = pak_sentence()

    print(sentences[1:len(sentences)], end = "\n")
    print(out)
    if max(out) > 0.3: #some value that is low
        print(f"""The closest People Also Ask question is: {sentences[out.index(max(out))+1]} \nThere is a similarity of {max(out)}""")
    else: 
        print("Did not find optimal sentence.")
    
    # except:
    #     print("Error has occured") 