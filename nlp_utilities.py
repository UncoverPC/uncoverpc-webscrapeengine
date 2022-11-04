from transformers import pipeline
import traceback

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