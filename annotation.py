import spacy
from gensim import corpora, models
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from keybert import KeyBERT
import string


def get_text_from_file(filename):
    with open(filename, encoding="utf-8", mode="r") as f:
        return f.read()


class Annotator:
    def __init__(self):
        self.keyword_model = KeyBERT(model="all-mpnet-base-v2")
        self.nlp = spacy.load("en_core_web_sm")
        self.stop_words = set(stopwords.words('english'))
        self.punctuation = string.punctuation

    """
     Following code gives description of named entity:
      spacy.explain(ent.label_)
    """

    def get_named_entities_from_text(self, text, result_object):
        result = {}
        doc = self.nlp(text)
        # Entity recognition
        for ent in doc.ents:
            if ent.label_ not in result:
                result[ent.label_] = []
            result[ent.label_].append(ent.text)
        result_object['named_entities'] = result

    def get_keywords_from_text(self, text, result_object):
        # getting keywords for each paragraph
        keywords = self.keyword_model.extract_keywords(
            # split by paragraphs
            text.split("\n\n"),
            keyphrase_ngram_range=(1, 3),
            stop_words="english",
            highlight=False,
            top_n=1
        )
        result = set()
        for keyword_list in keywords:
            for keyword_tuple in keyword_list:
                result.add(keyword_tuple[0])
        result_object['keywords'] = list(result)

    def get_topics_from_text(self, text, result_object):
        # preprocessing of the text data
        words = [word for word in word_tokenize(text.lower())
                 if word not in self.stop_words
                 and word not in self.punctuation
                 and word not in "1234567890"]

        # create a dictionary from the text data
        dictionary = corpora.Dictionary([words])

        # create a corpus from the text data
        corpus = dictionary.doc2bow(words)

        # train the Latent Dirichlet Allocation (LDA) model on the corpus
        lda_model = models.LdaModel([corpus], num_topics=5, id2word=dictionary)

        # extract the topics from the model
        topics = []
        for idx, topic in lda_model.show_topics(formatted=False, num_topics=-1):
            topics.append(' '.join([w[0] for w in topic]))

        result_object['topics'] = topics
