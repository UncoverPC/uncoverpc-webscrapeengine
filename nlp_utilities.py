from transformers import pipeline
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


def tempAdd():
    manual_input = {}

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
    
    def no_sentence():
        for item in google.goal:
            manual_input[item] = input(f"Please enter the updated value for {item}: ")

        print(manual_input)

    if (google.output[google.HA] == '' and google.output[google.A] == ''):
        #try:
        sentences, out = pak_sentence()

        print(sentences[1:len(sentences)], end = "\n")
        print(out)
        if max(out) >  1: #some value that is low
            print(f"""The closest People Also Ask question is: {sentences[out.index(max(out))+1]} \nThere is a similarity of {max(out)}""")
        else: 
            print("Did not find optimal sentence.")
            no_sentence()
        # except:
        #     print("Error has occured") 

    else:
        no_sentence()
    