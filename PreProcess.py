# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import re
import config


def changeFace(ans):
    
    val = re.sub("Face Amount: ",' ',ans)
    
    val = re.sub(",",' ',val)
    val = str(re.sub(" ",'',val))
    index = (val.find('$'))
    if(index!=-1):
        val = val[1:]
        
    #val = int(val)
    return (val)



def changeWt(ans):
    
    val = re.sub("#",'lb',ans)
    
    val = re.sub("lbs",'lb',val)
    val = str(re.sub(" ",'',val))
    if(re.search('KG|Kg|kg',val, re.I | re.U)):
        x = re.findall(r'\d+',ans)
        val = str(int(int(x[0])*2.2)) + 'lb'
    #val = int(val)
    return (val)

def preprocess_main():
	print("\nPre processing starting .. ")
	df = pd.read_csv(config.regex_processed_csv, encoding='UTF-8')
	df = df.iloc[1:]
	df = df.drop(columns=['Year_of_birth'])

	df['Weight'] = df['Weight'].apply(changeWt)
	print("Weight updation completed.. ")
	df['Face Amount'] = df['Face Amount'].apply(changeFace)
	print("Face amount updation completed ... ")	

	df.to_csv(config.preprocessed_csv,index=False, encoding = "utf-8")
	print("Pre processing completed ...")

preprocess_main()
