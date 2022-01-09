
from flask import Flask,  request, render_template
from transformers import TFBertForTokenClassification
from transformers import BertTokenizerFast
from transformers import pipeline
from flask import jsonify
import json
import pandas as pd
import xml.etree.ElementTree as ET
import os
import random
import re


app = Flask(__name__)
df = pd.read_json("./data/randomdata.json")


def randomize(column):
    rand_number = random.randrange(2000)
    value = ""
    value = df[column][rand_number]
    return value

def find_sex(sentence):

    c_f = ""
    sex = "F"
    pattern = re.compile(r"[A-Z]{6}\d{2}[A-Z]\d{2}[A-Z]\d{3}[A-Z]")  
    ris = pattern.search(sentence)
    
    if ris:
        c_f = str(ris.group())

        if int(c_f[9])> 3:
           sex= "F"
        else:
           sex = "M" 
    else:
        sentence_list = sentence.split()

        if  "M" in  sentence_list:
            sex= "M"
        else:
            sex = "F"  

    return sex, c_f      

def split_address(address):
    indirizzo_i = ""
    ind_n_ = ""
    for s in address:
        if s.isdigit():
            ind_n_= s
        else:
            indirizzo_i+= s + " "  

    return indirizzo_i, ind_n_             
    

@app.route("/")
def home():

    return render_template("index.html")


@app.route("/predict",methods=['GET', 'POST'])
def predict():
    
    data = request.files["file"]

    tokenizer = BertTokenizerFast.from_pretrained('dbmdz/bert-base-italian-cased')
    model = TFBertForTokenClassification.from_pretrained('./models/italian_bert')
    nlp = pipeline('ner', model=model, tokenizer=tokenizer,aggregation_strategy="first")
    
    if data.filename.lower().endswith(('.json')):

        data.save(os.path.join("./data/update_data/", data.filename))

        with open(os.path.join("./data/update_data/", data.filename)) as json_file:

           d_json = json.load(json_file)

           for row in d_json:
               sentence = ""

               for key,value in row.items():
                   sentence += str(value) + " "

               sex,cf= find_sex(sentence)

               result = nlp(sentence)

               indirizzo_B = ""
               indirizzo_I = ""
               cognome = ""
               nome = ""
               
               for token in result:
      
                  if token["entity_group"] == "LABEL_1":
                     indirizzo_B = token["word"]
                    
                  if token["entity_group"] == "LABEL_4":
                     indirizzo_I = token["word"]
                 
                  if token["entity_group"] == "LABEL_3":
                     cognome =token["word"] 

                  if token["entity_group"] == "LABEL_2":
                     nome = token["word"]        

               count_columns = 0
               
               indirizzo_I, ind_N = split_address(indirizzo_I.split())
               
               random_ind = randomize("indirizzo").split()
               ind_b_random = random_ind[0]
               
               ind_i_random, ind_n_random = split_address(random_ind[1:])
                     
               ind_column_pos = 0

               for key,value in row.items():
                  count_columns += 1
     
                  if cf == str(row[key]):
                    row[key]= "ABCXYZ00A99Z123X"

                  if len(cognome)>1 and cognome in str(row[key]) :
                
                    row[key] = str(row[key]).replace(cognome, randomize("cognome"))
                  
                  if len(nome)>1 and nome in str(row[key]) :
              
                    if sex=="M":
                        row[key] = str(row[key]).replace(nome,randomize("man_name"))
                    else:
                        row[key] = str(row[key]).replace(nome,randomize("femal_name"))


                  if len(indirizzo_B)>1 and indirizzo_B in str(row[key]):
                 
                    row[key] = str(row[key]).replace(indirizzo_B,ind_b_random)
                    ind_column_pos = count_columns
           

                  if len(indirizzo_I)> 1 and indirizzo_I in str(row[key]):
                   
                    row[key] = str(row[key]).replace(indirizzo_I,ind_i_random)
                      
                    if len(ind_N)> 1 and ind_N in str(row[key]):
            
                        row[key] = str(row[key]).replace(ind_N,ind_n_random)
                      
             
                  if len(ind_N)==2 and count_columns-ind_column_pos==2 and ind_N in str(row[key]):
                     
                    row[key] = str(row[key]).replace(ind_N,ind_n_random)

           with open('output.json', 'w') as f:
              json.dump(d_json, f  , indent=0)            


    elif data.filename.lower().endswith(('.xml')):  
      
        data.save(os.path.join("./data/update_data/", data.filename))
    
        tree = ET.parse(os.path.join("./data/update_data/", data.filename))
        root = tree.getroot()
 
        for i, child in enumerate(root):
            sentence = ""

            for subchild in child:
                sentence += str(subchild.text) + " "

            sex,cf= find_sex(sentence)
            
            result = nlp(sentence)

            indirizzo_B = ""
            indirizzo_I = ""
            cognome = ""
            nome = ""

            for token in result:
      
               if token["entity_group"] == "LABEL_1":
                     indirizzo_B = token["word"]
      
               if token["entity_group"] == "LABEL_4":
                     indirizzo_I = token["word"]
             
               if token["entity_group"] == "LABEL_3":
                     cognome =token["word"] 

               if token["entity_group"] == "LABEL_2":
                     nome = token["word"]     

            count_columns =0
            
            indirizzo_I, ind_N = split_address(indirizzo_I.split())

            random_ind = randomize("indirizzo").split()
            ind_b_random = random_ind[0]
            ind_i_random, ind_n_random = split_address(random_ind[1:])
                                   
            ind_column_pos = 0
               
            for subchild in child:
                count_columns += 1

                if cf == str(subchild.text):
                    subchild.text= "ABCXYZ00A99Z123X"

                if len(cognome)>1 and cognome in str(subchild.text) :
          
                    subchild.text = str(subchild.text).replace(cognome, randomize("cognome"))
              
                if len(nome)>1 and nome in str(subchild.text) :
                  
                    if sex=="M":
                        subchild.text = str(subchild.text).replace(nome,randomize("man_name"))
                    else:
                        subchild.text = str(subchild.text).replace(nome,randomize("femal_name"))
                    
                    
                if len(indirizzo_B)>1 and indirizzo_B in str(subchild.text):
                    
                      subchild.text = str(subchild.text).replace(indirizzo_B,ind_b_random)
                      ind_column_pos = count_columns
                   
                if len(indirizzo_I)> 1 and indirizzo_I in str(subchild.text):
                     
                      subchild.text = str(subchild.text).replace(indirizzo_I,ind_i_random)
                      
                      if len(ind_N)> 1 and ind_N in str(subchild.text):
                     
                        subchild.text = str(subchild.text).replace(ind_N,ind_n_random)       
                     
                if len(ind_N)==2 and count_columns-ind_column_pos==2 and ind_N in str(subchild.text):
                      
                      subchild.text = str(subchild.text).replace(ind_N,ind_n_random)
                 

        tree.write("./output.xml")            
                       

    return render_template("predict.html")






