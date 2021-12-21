
from flask import Flask,  request, render_template
from transformers import TFBertForTokenClassification
from transformers import BertTokenizerFast
from transformers import pipeline
from flask import jsonify
import json
import pandas as pd
import xml.etree.ElementTree as ET
import os


app = Flask(__name__)
dizionario = {"tot val":0,"cognome":0,"nome":0,"indirizzo":0}
@app.route("/")
def home():

    return render_template("index.html")

@app.route("/prova",methods=['GET', 'POST'])
def prova():
    data = request.files["file"]
    
  
    tokenizer = BertTokenizerFast.from_pretrained('dbmdz/bert-base-italian-cased')
   
    model = TFBertForTokenClassification.from_pretrained('./models/italian_bert')
    nlp = pipeline('ner', model=model, tokenizer=tokenizer,aggregation_strategy="first")
    
    if data.filename.lower().endswith(('.json')):
        data.save(os.path.join("./update_data/", data.filename))
        with open(os.path.join("./update_data/", data.filename)) as json_file:
           d_json = json.load(json_file)
           for p in d_json:
               dizionario["tot val"] += 1
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
                    
                     p[k] = "cognome nuovo"
                  if cognome in str(v) :
                    dizionario["cognome"] += 1
                    p[k] = str(v).replace(cognome, "cognome nuovo")

                  if nome in str(v) :
                    dizionario["nome"] += 1
                    p[k] = str(v).replace(nome, "nome nuovo")

                  if indirizzo in str(v) :
                    dizionario["indirizzo"] += 1
                    p[k] = str(v).replace(indirizzo, "indirizzo nuovo")    

           with open('output.json', 'w') as f:
              json.dump(d_json, f  )       
       # print(df)
       # print(os.path.join("./update_data/", data.filename))
      
        #data.save(os.path.join("./update_data/", data.filename))

        #with open(os.path.join("./update_data/", data.filename), 'w') as outfile:
         #  json.dump(data, outfile)

       # data.save(os.path.join("./update_data/", data.filename))
      



    elif data.filename.lower().endswith(('.xml')):  
        print(os.path.join("./update_data/", data.filename))
        data.save(os.path.join("./update_data/", data.filename))
        #xml_data = open(os.path.join("./update_data/", data.filename), 'r').read()
        tree = ET.parse(os.path.join("./update_data/", data.filename))
        root = tree.getroot()
 
        #root = ET.XML(xml_data)  # Parse XML

        d = []
        cols = []

        for i, child in enumerate(root):
            
            d.append([subchild.text for subchild in child])
            cols.append(child.tag)
            dizionario["tot val"] += 1
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
                    dizionario["cognome"] += 1
                    subchild.text = str(subchild.text).replace(cognome, "cognome nuovo")

                if nome in str(subchild.text) :
                    dizionario["nome"] += 1
                    subchild.text = str(subchild.text).replace(nome, "nome nuovo")

                if indirizzo in str(subchild.text) :
                    dizionario["indirizzo"] += 1
                    subchild.text = str(subchild.text).replace(indirizzo, "indirizzo nuovo")    



        tree.write("./output.xml")            
                       



            

        df = pd.DataFrame(d)    
       



    
    print(data.filename)
    
    #return str(file)
    return str(dizionario)

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




