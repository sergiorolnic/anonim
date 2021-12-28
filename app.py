
from flask import Flask,  request, render_template
from transformers import TFBertForTokenClassification
from transformers import BertTokenizerFast
from transformers import pipeline
from flask import jsonify
import json
import pandas as pd
import xml.etree.ElementTree as ET
import os
import time
import random

app = Flask(__name__)
df = pd.read_json("./data/randomData.json")


def randomize(column):
    rand_number = random.randrange(2000)
    
    value = ""
    
    
    value = df[column][rand_number]
    return value
        




@app.route("/")
def home():

    return render_template("index.html")

@app.route("/prova",methods=['GET', 'POST'])
def prova():
    
    data = request.files["file"]
    list_durata = []
  
    tokenizer = BertTokenizerFast.from_pretrained('dbmdz/bert-base-italian-cased')
   
    model = TFBertForTokenClassification.from_pretrained('./models/italian_bert')
    nlp = pipeline('ner', model=model, tokenizer=tokenizer,aggregation_strategy="first")
    
    if data.filename.lower().endswith(('.json')):
        data.save(os.path.join("./update_data/", data.filename))
        with open(os.path.join("./update_data/", data.filename)) as json_file:
           d_json = json.load(json_file)
           tick = time.time()
           righe=0
           for p in d_json:
               start= time.time()
               righe += 1
            
               sentence = ""
               for k,v in p.items():
                   sentence += str(v) + " "
                   print(v)
               ris = nlp(sentence)
               indirizzo = ""
               cognome = ""
               nome = ""
               true_name = ""
               for t in ris:
      
                  if t["entity_group"] == "LABEL_1":
                     indirizzo = t["word"]
                  if t["entity_group"] == "LABEL_4":
                     indirizzo += " " + t["word"]
        
                  if t["entity_group"] == "LABEL_3":
                     cognome =t["word"]
                     true_name = t["word"]
                  if t["entity_group"] == "LABEL_2":
                     nome = t["word"]        
                
               for k,v in p.items():
               
                  if str(v) == cognome:
                    
                     #p[k] = "cognome nuovo"
                     p[k] = randomize("cognome")
                  if cognome in str(v) :
                  
                    p[k] = str(v).replace(cognome, randomize("cognome"))

                  if nome in str(v) :
                  
                    p[k] = str(v).replace(nome,randomize("man_name"))

                  if indirizzo in str(v) :
                  
                    p[k] = str(v).replace(indirizzo, randomize("indirizzo"))   
               stop = time.time()
               list_durata.append(stop-start)


           with open('output.json', 'w') as f:
              json.dump(d_json, f  )            



    elif data.filename.lower().endswith(('.xml')):  
        print(os.path.join("./update_data/", data.filename))
        data.save(os.path.join("./update_data/", data.filename))
        #xml_data = open(os.path.join("./update_data/", data.filename), 'r').read()
        tree = ET.parse(os.path.join("./update_data/", data.filename))
        root = tree.getroot()
 
        #root = ET.XML(xml_data)  # Parse XML

        d = []
        cols = []
        tick = time.time()
        righe=0
        for i, child in enumerate(root):
            start= time.time()
            d.append([subchild.text for subchild in child])
            cols.append(child.tag)
            righe += 1
            sentence = ""
            for subchild in child:
                sentence += str(subchild.text) + " "

            ris = nlp(sentence)
            indirizzo = ""
            cognome = ""
            nome = ""
            true_name = ""
            for t in ris:
      
               if t["entity_group"] == "LABEL_1":
                   indirizzo = t["word"]
               if t["entity_group"] == "LABEL_4":
                   indirizzo += " " + t["word"]
        
               if t["entity_group"] == "LABEL_3":
                  cognome =t["word"]
                  true_name = t["word"]
               if t["entity_group"] == "LABEL_2":
                  nome = t["word"]    
            for subchild in child:
              
                if cognome in str(subchild.text) :
                   
                    subchild.text = str(subchild.text).replace(cognome, "cognome nuovo")

                if nome in str(subchild.text) :
              
                    subchild.text = str(subchild.text).replace(nome, "nome nuovo")

                if indirizzo in str(subchild.text) :
                 
                    subchild.text = str(subchild.text).replace(indirizzo, "indirizzo nuovo")    

            stop = time.time()
            list_durata.append(stop-start)        



        tree.write("./output.xml")            
                       



            

        df = pd.DataFrame(d)    
       



    
    print(data.filename)
    list_def = []
    for x in list_durata:
        list_def.append(x-(sum(list_durata)/righe))
    
    varianza = sum(list_def)/righe
    duration = time.time()-tick
    dizi = {"righe":righe, "duration":duration, "media": duration/righe, "varianza":varianza}
    #return str(file)
    return str(dizi)

from flask import jsonify
@app.route("/predict")
def predict():
    
    tokenizer = BertTokenizerFast.from_pretrained('bert-base-uncased')
 
    model = TFBertForTokenClassification.from_pretrained('./models/accurate_model')
    
    nlp = pipeline('ner', model=model, tokenizer=tokenizer,aggregation_strategy="first")
    
    output = nlp("5 10 SERGIU ROLNIC M 8031935 BIANZE BTAZEI35C08A847I VC MONCALIERI TO ITA STRADA GENOVA 58 10024 24032017 10003 13101963 3101963 12112021 05:49:25 CENS2011")
   
    response = "Insolvente" if str(output) else "Non insolvente"
    return render_template("predict.html", resp=response, data=output)
    #return render_template("predict.html", resp="e vaiiii")
    #return str(output)
    #return str(output)




