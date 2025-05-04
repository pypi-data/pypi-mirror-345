
import io
import base64
import polars as pl
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import scipy.cluster.hierarchy as hr
from sklearn.cluster import AgglomerativeClustering
import matplotlib.pyplot as plt
import altair as alt



class ClusterAnalyzer:

    df: pl.DataFrame
    distanceMatrix: None

    def __init__(self, data: list[dict]|pl.DataFrame):
        self.df = data if isinstance(data, pl.DataFrame) else pl.DataFrame(data)

    def createDistanceMatrix(self):
        return hr.linkage(self.df, method='ward', metric='euclidean', optimal_ordering=False)
    
    def normalize(self, min_value: int, max_value: int):
        scaler = MinMaxScaler(feature_range=(min_value, max_value))
        ndf = scaler.fit_transform(self.df)
        ndf = pl.DataFrame(ndf, column=self.df.columns)
        self.df = ndf

    def getDendrogramHeight(self):
        mdf = pl.DataFrame(self.distanceMatrix)
        height = round(mdf.iloc[:, 2].max())
        return height
    
    def getDendrogramCenterHeight(self):
        return round(self.getDendrogramHeight() / 2)
    
    def guessNrOfClustersByCenter(self):
        center_height = self.getDendrogramCenterHeight()
        nr_of_leaves = self.distanceMatrix.shape[0] + 1
        merge_heights = self.distanceMatrix[:, 2]
        nr_of_clusters = nr_of_leaves - np.digitize(center_height, merge_heights)
        return nr_of_clusters
    
    def createDendrogram(self, title='Dendrogram'):
        fig = plt.figure(figsize=(10, 7))
        plt.title(title)
        center_height = self.getDendrogramCenterHeight()
        n_clusters = self.guessNrOfClustersByCenter()
        plt.annotate(
            text='Clusters: ' + str(n_clusters),
            xy=(0.97, 0.97),
            xycoords='axes fraction',
            va='top', ha='right',
            bbox={'boxstyle': 'round', 'fc': 'w'}
        )
        hr.dendrogram(self.distanceMatrix)
        plt.axhline(y=center_height, color='r', linestyle='-')
        return fig
    
    def exportDendrogramAsBase64Str(self, dendrogram_fig):
        plt.figure(dendrogram_fig)
        iobytes = io.BytesIO()
        plt.savefig(iobytes, format='png', transparent=True)
        iobytes.seek(0)
        b64jpg = str(base64.b64encode(iobytes.read()))[2:-1]
        return b64jpg
    
    def createClusterCol(self, n_clusters: int|None = None):
        n_clusters = n_clusters if n_clusters else self.guessNrOfClustersByCenter()
        model = AgglomerativeClustering(n_clusters=n_clusters, affinity='euclidean', linkeage='ward')
        model.fit(self.df)
        return np.add(model.labels_, 1)
    
    def createClusterCol2(self, n_clusters: int|None=None):
        return hr.fcluster(self.distanceMatrix, n_clusters, criterion='maxclust')
    
    def createClusterCol3(self):
        # k means here
        ...
    
    def analyze(self, n_clusters: int|None = None):
        clust_col = self.createClusterCol(n_clusters)
        return # create cluster column at the end of the df