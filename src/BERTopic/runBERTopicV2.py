import os
import argparse
from bertopic import BERTopic
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
from umap import UMAP 
from hdbscan import HDBSCAN
import pandas as pd

os.environ["TOKENIZERS_PARALLELISM"] = "false"

stopWords = stopwords.words('english') 
for word in stopwords.words('german'):
    stopWords.append(word)
for word in stopwords.words('russian'):
    stopWords.append(word)
#ukrstopWords = ['а', 'аби', 'абиде', 'абиким', 'абикого', 'абиколи', 'абикому', 'абикуди', 'абихто', 'абичий', 'абичийого', 'абичийому', 'абичим', 'абичию', 'абичия', 'абичиє', 'абичиєму', 'абичиєю', 'абичиєї', 'абичиї', 'абичиїй', 'абичиїм', 'абичиїми', 'абичиїх', 'абичого', 'абичому', 'абищо', 'абияка', 'абияке', 'абиякий']
with open("data/stopwords/stopwords_ua.txt") as file:
    ukrstopWords = [line.rstrip() for line in file]
for stopwords in ukrstopWords:
    stopWords.append(stopwords)

vectorizer_model = CountVectorizer(ngram_range=(1, 2), stop_words=stopWords)

def validate_file(f):
    if not os.path.exists(f):
        raise argparse.ArgumentTypeError("{0} does not exist".format(f))
    return f

class BERTopicAnalysis:
    def __init__(self, input_file, output_folder, k_cluster, do_inference):
        self.input_file = input_file
        self.output_folder = output_folder
        self.k_cluster = k_cluster
        self.do_inference = do_inference

    def read_data(self):
        self.df = pd.read_csv(self.input_file)
        self.df.dropna(subset=['messageSender', 'messageText'],inplace=True)
        self.df.drop_duplicates(subset=['messageText', 'messageSender', 'chat'], keep='first',inplace=True)
        self.df = self.df[self.df['messageText'].map(type) == str]
        self.df["messageText"] = self.df['messageText'].str.split().str.join(' ')
        lines = self.df[(self.df['messageText'].str.len() >= 100) & (self.df['messageText'].str.len() <= 2500)].messageText.values
        self.text_to_analyse_list = [line.rstrip() for line in lines]

    def read_model(self):
        print("loading model")
        self.model=BERTopic.load(f"{self.output_folder}/BERTopicmodel")



    def k_cluster_type(self):
        if self.k_cluster.isnumeric():
            self.k_cluster = int(self.k_cluster)

    def fit_BERTopic(self):
        umap_model = UMAP(n_neighbors=25, n_components=10, metric='cosine', low_memory=False, random_state=42)
        hdbscan_model = HDBSCAN(min_cluster_size=10, metric='euclidean', prediction_data=True)
        self.model = BERTopic(verbose=True,
                              language="multilingual",
                              nr_topics=self.k_cluster, 
                              vectorizer_model=vectorizer_model,
                            #   min_topic_size=self.min_topic_size,
                              umap_model=umap_model,
                              hdbscan_model=hdbscan_model,
                            #   calculate_probabilities=True
                              )#, nr_topics=int(self.k_cluster))
        topics, probs = self.model.fit_transform(self.text_to_analyse_list)

    def save_results(self):
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
        fig = self.model.visualize_topics()
        fig.write_html(f"{self.output_folder}/bert_topic_model_distance_model.html")
        fig = self.model.visualize_hierarchy()
        fig.write_html(f"{self.output_folder}/bert_topic_model_hierarchical_clustering.html")
        fig = self.model.visualize_barchart(top_n_topics=30)
        fig.write_html(f"{self.output_folder}/bert_topic_model_word_scores.html")
        fig = self.model.visualize_heatmap()
        fig.write_html(f"{self.output_folder}/bert_topic_model_word_heatmap.html")
        self.model.save(f"{self.output_folder}/BERTopicmodel")
    
    def write_multi_sheet_excel(self):
        writer = pd.ExcelWriter(f"{self.output_folder}/representative_docs.xlsx", engine='xlsxwriter')
        for i in self.model.get_representative_docs().keys():
            df = pd.DataFrame(self.model.get_representative_docs()[i], columns=['message'])
            df.to_excel(writer, sheet_name=self.model.get_topic_info()[self.model.get_topic_info()['Topic']==i]['Name'].values[0][:31])
        writer.save()
        self.model.get_topic_info().to_csv(f"{self.output_folder}/topic_info.csv")

    def inference(self):
        pred, prob = self.model.transform(self.df['messageText'].values)
        self.df['cluster'] = pred
        # self.df = pd.merge(self.df,pd.DataFrame(probs, columns=['prob_0', 'prob_1', 'prob_2', 'prob_3', 'prob_4', 'prob_5', 'prob_6', 'prob_7', 'prob_8', 'prob_9']), left_index=True, right_index=True)
        self.df.to_csv(f"{self.output_folder}/df.csv", index=False)

    def run_all(self):
        self.read_data()
        if os.path.exists(f"{self.output_folder}/BERTopicmodel"):
            self.read_model()
        else:
            self.k_cluster_type()
            self.fit_BERTopic()
            self.save_results()
            self.write_multi_sheet_excel()
        if self.do_inference:
            self.inference()

def main():
    parser = argparse.ArgumentParser()
    # sample use python src/
    parser.add_argument('-i', '--input_file', help="Specify the input file", type=validate_file, required=True) #TODO change to argparse.FileType('r')
    parser.add_argument('-o', '--output_folder', help="Specify folder for results", required=True)
    parser.add_argument('-k', '--k_cluster', help="number of topic cluster", required=False, default="auto")
    parser.add_argument('-di', '--do_inference', help="does inference on data", action='store_true')
    # parser.add_argument('-cp', '--calculate_probs', help="does inference on data", action='store_true')
    args = parser.parse_args()
    BERTopic_Analysis = BERTopicAnalysis(args.input_file,
                                         args.output_folder,
                                         args.k_cluster,
                                         args.do_inference
                                         )
    BERTopic_Analysis.run_all()

if __name__ == '__main__':
    main()