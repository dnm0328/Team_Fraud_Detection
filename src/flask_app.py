from flask import Flask, request, render_template
import pickle
import json
from pymongo import MongoClient


#from somewhere import predict.py
app = Flask(__name__)



review_idx_list = []
low  = 0
med = 0
high = 0

try:
    client = MongoClient('localhost', 27017)
    print('Connected Successfully!')
except:
    print('Could not connect to MongoDB')
db = client['fraud_predictions']
entries = db['entries']

'''
low_num = entries.count_documents(entries.find({'fraud_pred':{'$lt': 0.3}}))
low += low_num


med_num = entries.count_documents(entries.find({'fraud_pred':{'$gt': 0.3, '$lt': 0.6}}))
med += med_num


high_num = entries.count_documents(entries.find({'fraud_pred':{'$gt': 0.6}}))
high += high_num
# review_idx_list.append(the json ID or IDX )
'''

low_num = entries.count_documents({'fraud_pred': {'$lt': 0.2}})
low += low_num

med_num = entries.count_documents({'fraud_pred': {'$gt': 0.2, '$lt': 0.5}})
med += med_num

high_num = entries.count_documents({'fraud_pred': {'$gt': 0.5}})
high += high_num

# highest_prob = entries.find({}, {'fraud_pred': {'$gt': 0.6}})
lst = entries.find({'fraud_pred':{'$gt':.2}})
for x in lst:
    val = x['fraud_pred']
    a = round(val, 3)
    d = (a, x['_id'])
    review_idx_list.append(d)
review_idx_list.sort(reverse=True)
    
    
@app.route('/', methods=['GET'])


def home():
    return ''' <p> Welcome, friend, view your
                   <a href="/dashboard">dashboard</a> and an
                   <a href="/form_example">example form</a> </p> '''

@app.route('/dashboard', methods=['GET', 'POST'])

def dashboard_template_test():


    return render_template('template.html', my_string="File ID list needing further review!", review_idx_list=review_idx_list, high=high,
                           medium=med,low=low)


@app.route('/score', methods=['POST'])
def get_new_file_probs():
    #read in new jsons:
    score = 4

    return ''' outputScore: {}  '''.format(score)

@app.route('/form_example', methods=['GET'])
def form_display():
    return ''' <form action="/string_reverse" method="POST">
                <input type="text" name="some_string" />
                <input type="submit" />
               </form>
             '''

@app.route('/string_reverse', methods=['POST'])
def reverse_string():

    text = str(request.form['some_string'])
    reversed_string = text[-1::-1]
    return ''' output: {}  '''.format(reversed_string)



if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080, debug=True)

  # Establish the Mongo Client Instance

