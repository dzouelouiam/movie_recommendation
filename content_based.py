import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt 
from sklearn.feature_extraction.text import TfidfVectorizer 
from sklearn.metrics.pairwise import linear_kernel 
from ast import literal_eval 
from sklearn.feature_extraction.text import CountVectorizer 
from sklearn.metrics.pairwise import cosine_similarity
import csv

def recommendation ():
    dfl = pd.read_csv("/Users/dzouelouiam/Desktop/myproject/base/data/tmdb_5000_movies.csv")
    dfl.head(10)
