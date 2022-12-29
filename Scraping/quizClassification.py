from transformers import pipeline
import bing as bing
import nlp_utilities as utils
qa_model = pipeline("question-answering", model = "deepset/minilm-uncased-squad2")


def processProduct(productInfo, questions, quiz_questions):
    classifiedItem = productInfo
    doneProp = {}
    incProp = []

    for item in questions:
        temp = qa_model(question = item, context = " ".join(productInfo['Properties']))
        if (temp['score']>0.4): #May require fine-tuning
            doneProp[item] = temp['answer']
        else:
            incProp.append(item)

    for item in incProp:
        temp = bing.getData(f"{item.replace('?',' ')} {classifiedItem['Name']}")

        print(temp)

        if temp['Definite Answer'] != "":
            doneProp[item] = temp['Definite Answer']
        
        elif temp['Highlighted Answer'] != "":
            doneProp[item] = temp['Highlighted Answer']
        elif temp['General Answer'] != "":
            # We use the general answer as a context to see if we can get anything out of it
            pass
        else:
            # Last resort
            question = utils.extraSentences(classifiedItem["Name"], item, temp['People also ask'])
            if question == 0:
                # There is no good "people also ask"
                answer = input(f" {(item.replace('?', ''))} for the {productInfo['Name']}: ")
                doneProp[item] = answer

            else:
                # There is a suitable "people also ask" section TODO
                pass
        
        classifiedItem["QuizResponses"] = doneProp
        
    for qNum in range(len(questions)):
        label = utils.classifyLabel(classifiedItem["QuizResponses"][questions[qNum]], quiz_questions[qNum]['answers'])
        classifiedItem["QuizResponses"][questions[qNum]] = label['labels'][0]
    return classifiedItem


