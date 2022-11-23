# pip install pymongo python-decouple
from pymongo import MongoClient
import json
from decouple import config

### setup
MONGO_USER = config('USER')
MONGO_PASS = config('PASS')

CONNECTION_STRING = f'mongodb+srv://{MONGO_USER}:{MONGO_PASS}@cluster0.fgvaysh.mongodb.net/?retryWrites=true&w=majority'

client = MongoClient(CONNECTION_STRING)

db = client['uncoverpc']
laptopCollection = db['laptops']
userCollection = db['users']
quizCollection = db['quizzes']
quiz = db['quiz']

# Test Quiz
async def getQuiz():
	out = []
	collection = quiz.find()[0]['questions']
	for item in collection:
		out.append(item['question'])
	return out


#for item in test:
 #   print(item, end = "\n")

# get all data from quizzes collection
allQuizzes = []
for quiz in quizCollection.find():
	allQuizzes.append(quiz)
print(allQuizzes)

# post new products

# products: data from a json file of products
# collection: one of the above collectsion from 'setup'
# formatting: a function to format data in 'products'
# returns Ids of inserted products
def postNewProducts(products, collection, formatting):
	productIds = []
	for product in formatting(products):
		productIds.append(collection.insert_one(product).inserted_id)
	return productIds

def laptopFormatting(laptops):
	formattedLaptops = []
	for laptop in laptops:
		formatted = {
			"name": laptop,
			"specs": laptops[laptop]
		}
		formattedLaptops.append(formatted)
	return formattedLaptops

# testing
with open('./laptops.json', 'r') as f:
  data = json.load(f)

ids = postNewProducts(data, laptopCollection, laptopFormatting)
print(ids)
f.close()

# close mongodb client
client.close()
