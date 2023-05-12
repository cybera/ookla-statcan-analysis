import sys
sys.path.append("..")
from sklearn.preprocessing import StandardScaler,LabelEncoder
from sklearn.cluster import KMeans,DBSCAN
import matplotlib
import matplotlib.pyplot as plt 
from src.datasets.loading import statcan, ookla
import numpy as np
import scipy
import pandas as pd
#import seaborn as sns
label_encoder=LabelEncoder()
scaler = StandardScaler()

def preparedata(calc,cat,target,df):
    '''
    This function returns the dataframe that transform selected columns of original dataframe. Standardize the numerical variables and encode categorical variable 
    '''
    X=df.loc[:,(calc+target+cat)].copy()
    for c in cat:
        X[c]=label_encoder.fit_transform(X[c])
        X[c]=X[c].astype(int)
    X.loc[:,calc+target] = scaler.fit_transform(X.loc[:,calc+target])
    return X

    
    
    

def best_k(k,df_X,init_pt='k-means++',max_iter=500,n_init=10,random_seed=42):
    '''
    This function is intended to return the best k for k means .
    '''
    max_k = k
    distortions = [] 
    for i in range(1, max_k+1):
        if len(df_X) >= i:
            model = KMeans(n_clusters=i, init=init_pt, max_iter=max_iter, n_init=n_init, random_state=random_seed)
            model.fit(df_X)
            distortions.append(model.inertia_)## best k: the lowest derivative
    k = range(1,max_k+1)[np.argmin(distortions)]
    return k
    
    
    
    
def AddCluster(k,df,init_pt='k-means++',max_iter=500,n_init=10,random_seed=42):
    model = KMeans(n_clusters=k, init='k-means++', max_iter=500, n_init=10, random_state=42)
    df.loc[:,"cluster"] = model.fit_predict(df)
    return df

# def DrawCluster2D(X,k):
#     fig, ax = plt.subplots()
#     sns.scatterplot(x="lat", y="long", data=X, 
#                     palette=sns.color_palette("bright",k),
#                     hue='cluster', size="centroids", size_order=[1,0],
#                     legend="brief", ax=ax).set_title('Clustering (k='+str(k)+')')
#     th_centroids = model.cluster_centers_
#     ax.scatter(th_centroids[:,0], th_centroids[:,1], s=50, c='black', marker="x")
#     return ax




    