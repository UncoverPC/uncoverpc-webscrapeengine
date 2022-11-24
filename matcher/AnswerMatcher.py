from transformers import pipeline

labelClassificationModelName = "zero-shot-classification"
labelClassificationModelType = "facebook/bart-large-mnli"


def getPrediction(sequence, labels):
    model = pipeline(labelClassificationModelName,
                     labelClassificationModelType)
    return model(sequence, labels)

# Get specific question


# Get sequences from Google
sequence_to_classify = "up to 10 hours"

# Get labels from MongoDB
candidate_labels = ['3-5 hours', '5-8 hours', '8-12 hours', '12 hours +']

print(getPrediction(sequence_to_classify, candidate_labels))
