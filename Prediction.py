# -*- coding: utf-8 -*-

# File imports

import pandas as pd
import numpy as np
import config
from nltk.corpus import stopwords, wordnet as wn
from nltk.tokenize import wordpunct_tokenize, sent_tokenize
from nltk import pos_tag
from nltk.stem.wordnet import WordNetLemmatizer
import re
import pickle
from MailCleaner import mail_cleaner_main
from RegexProcessing import regex_processing_main
from PreProcess import preprocess_main
import logging

logging.basicConfig(filename=config.log_file, level=logging.WARNING)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Removes all punctuations which acts as noise
def rem_punt(doc):
    ans = re.sub('"|\\n|\(|\)|\.|[$!--+@#:]', ' ', doc)
    ans = re.sub(' +', ' ', ans)
    ans = ans.lower()
    return ans


# Stop words removal using tokenization
def tokenize(document):
    lemmy = []
    stop_word = set(stopwords.words('english'))
    for sent in sent_tokenize(document):
        for token, tag in pos_tag(wordpunct_tokenize(sent)):
            # logger.debug(token,tag)
            if token in stop_word:
                 continue
            lemma = lemmatize(token, tag)
            lemmy.append(lemma)
    return lemmy

# Lemmatization for tokens simplification


def lemmatize(token, tag):
    tag = {
          'N': wn.NOUN,
          'V': wn.VERB,
          'R': wn.ADV,
          'J': wn.ADJ
    }.get(tag[0], wn.NOUN)
    lemmatizer = WordNetLemmatizer()
    return lemmatizer.lemmatize(token, tag)


def PredictionModule(doc):
	loaded_model = pickle.load(open('SavedModels/'+ config.raw_data_type + 'SVM.sav', 'rb'))

	pd = loaded_model.predict([doc])
	return (pd)


def prediction_main(file):
	logger.info('>> Start Mail cleaning')
	mail_cleaner_main(file)
	
	logger.info('>> Start Regex Processing')
	regex_processing_main(file)

	logger.info('>> Start PreProcess')
	preprocess_main(file)

	df = pd.read_csv(config.preprocessed_csv, encoding='UTF-8')
	df['Contents'] = df[df.columns[0:12]].apply(
	    lambda x: ','.join(x.dropna().astype(str)), axis=1)
	logger.debug(f"Contents= {[i for i in df['Contents']]}")

	logger.info('>> Start tokenize and remove punctuations')
	df['Lemmitize'] = df['Contents'].apply(rem_punt).apply(tokenize)
	logger.debug(f"Features= {[i for i in df['Lemmitize']]}")

	df.to_csv(config.enlp_processed_csv, index=False, encoding="utf-8")
	# change when merged with email raw data
	df = pd.read_csv(config.enlp_processed_csv)

	logger.info('>> Start Prediction')
	df['result'] = df['Lemmitize'].apply(PredictionModule)
	logger.debug(f"Offer= {df['result']}")

	of = pd.read_csv(config.eraw_data_csv, encoding = 'utf-8')
	of['Offer_noise_free'] = df['result']
	

	df.to_csv(config.enlp_processed_csv,index=False, encoding = "utf-8")
	of.to_csv(config.eraw_data_csv,index=False, encoding = "utf-8")

# prediction_main(config.eraw_data_csv)
	



