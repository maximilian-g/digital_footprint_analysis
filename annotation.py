import spacy
import re
from gensim import corpora, models
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from keybert import KeyBERT
from transformers import BartTokenizer, BartForConditionalGeneration
import string
from annotation_types import AnnotationTypes
from datetime import datetime
from time_measurement import measure_time


def get_text_from_file(filename):
    with open(filename, encoding="utf-8", mode="r") as f:
        return f.read()


def get_paragraphs_with_min_len(text, desired_min_paragraph_len):
    text = re.sub(r' +', ' ', text)
    text = re.sub(r' uh ', ' ', text)
    possible_paragraphs = text.split("\n\n")
    if len(possible_paragraphs) < 6:
        new_possible_paragraphs = []
        for paragraph in possible_paragraphs:
            new_possible_paragraphs.extend(paragraph.split("\n"))
        possible_paragraphs = new_possible_paragraphs

    result_paragraphs = []
    temp_paragraphs = []
    for paragraph in possible_paragraphs:
        if desired_min_paragraph_len > len(paragraph) > 0:
            temp_paragraphs.append(paragraph)
        elif len(paragraph) > 0:
            result_paragraphs.append(paragraph)

    current_paragraph = ""
    for temp_paragraph in temp_paragraphs:
        if len(current_paragraph) >= desired_min_paragraph_len:
            result_paragraphs.append(current_paragraph)
            current_paragraph = ""
        else:
            current_paragraph = current_paragraph + " " + temp_paragraph

    if len(current_paragraph) != 0:
        result_paragraphs.append(current_paragraph)

    return result_paragraphs


class Annotator:
    def __init__(self):
        self.keyword_model = KeyBERT(model="paraphrase-multilingual-MiniLM-L12-v2")
        self.summary_tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-cnn')
        self.summary_model = BartForConditionalGeneration.from_pretrained('facebook/bart-large-cnn')
        self.nlp = spacy.load("en_core_web_lg")
        self.stop_words = set(stopwords.words('english'))
        self.punctuation = string.punctuation

        # constants
        self.PARAGRAPH_MIN_LEN = 300
        self.MAX_SUMMARY_INPUT_LENGTH = 4096
        self.ALLOWED_NER_LABELS = ["DATE", "EVENT", "FAC", "GPE", "LANGUAGE", "LAW", "LOC",
                                   "NORP", "ORG", "PERSON", "PRODUCT", "WORK_OF_ART"]

    """
     Following code gives description of named entity:
      spacy.explain(ent.label_)
    """

    def get_named_entities_from_text(self, text, result_object):
        start = datetime.now()
        result = {}
        doc = self.nlp(text)
        # Entity recognition
        for ent in doc.ents:
            if ent.label_ in self.ALLOWED_NER_LABELS:
                if ent.label_ not in result:
                    result[ent.label_] = set()
                temp_text = ent.text
                temp_text = re.sub(r'\n+', ' ', temp_text)
                temp_text = re.sub(r' +', ' ', temp_text)
                result[ent.label_].add(temp_text)
        for key in result:
            result[key] = list(result[key])
        measure_time(start, f"Named Entity Recognition for {result_object['link']}")
        result_object[AnnotationTypes.NAMED_ENTITIES.value] = result

    def get_keywords_from_text(self, text, result_object):
        start = datetime.now()

        # getting keywords for each paragraph
        # split by paragraphs
        possible_paragraphs = get_paragraphs_with_min_len(text, self.PARAGRAPH_MIN_LEN)

        total_paragraphs_len = 0
        for paragraph in possible_paragraphs:
            total_paragraphs_len = total_paragraphs_len + len(paragraph)

        # there might be texts not divided by paragraphs,
        # in that case we still need to get reasonable quantity of keywords,
        # depending on the length of the text, 2000 is approximate length of a paragraph
        top_n = max(3, total_paragraphs_len // 2000) if len(possible_paragraphs) == 1 else 1

        keywords = self.keyword_model.extract_keywords(
            possible_paragraphs,
            keyphrase_ngram_range=(1, 3),
            stop_words="english",
            highlight=False,
            top_n=top_n
        )
        result = set()
        for keyword_list in keywords:
            if isinstance(keyword_list, list):
                for keyword_tuple in keyword_list:
                    result.add(keyword_tuple[0])
            else:
                # in case of single paragraph, keyword_list becomes a tuple, not a list
                result.add(keyword_list[0])
        measure_time(start, f"Keywords extraction for {result_object['link']}")
        result_object[AnnotationTypes.KEYWORDS.value] = list(result)

    def get_topics_from_text(self, text, result_object):
        start = datetime.now()
        # in order to show more topics for large sized texts
        num_topics = max(3, len(text) // 2000)

        # preprocessing of the text data
        words = [word for word in word_tokenize(re.sub(r"('s)|( uh )|(»)|(«)|(’)", '', text).strip().lower())
                 if word not in self.stop_words
                 and word not in self.punctuation
                 and word not in "1234567890"]

        # create a dictionary from the text data
        dictionary = corpora.Dictionary([words])

        # create a corpus from the text data
        corpus = dictionary.doc2bow(words)

        # train the Latent Dirichlet Allocation (LDA) model on the corpus
        lda_model = models.LdaModel([corpus], num_topics=num_topics, id2word=dictionary)

        # extract the topics from the model
        topics = set()
        lda_topics = lda_model.show_topics(formatted=False, num_topics=num_topics, num_words=3)
        for idx, topic in lda_topics:
            topics.add(' '.join([w[0] for w in topic]))
        measure_time(start, f"Topic generation for {result_object['link']}")
        result_object[AnnotationTypes.TOPICS.value] = list(topics)

    def get_summary_from_text(self, text, result_object):
        start = datetime.now()
        text = re.sub(r'»+', '', text)
        text = re.sub(r'«+', '', text)
        text = re.sub(r'’+', '', text)
        text = re.sub(r' +', ' ', text)
        text = re.sub(r'\n+', ' ', text).strip()

        texts_to_summarize = []
        if len(text) <= self.MAX_SUMMARY_INPUT_LENGTH:
            texts_to_summarize.append(text)
        else:
            for i in range(0, len(text), self.MAX_SUMMARY_INPUT_LENGTH):
                texts_to_summarize.append(text[i:min(i + self.MAX_SUMMARY_INPUT_LENGTH, len(text) - 1)].strip())

        result = ""
        for current_text in texts_to_summarize:
            inputs = self.summary_tokenizer.encode(current_text,
                                                   return_tensors="pt",
                                                   max_length=1024,
                                                   truncation=True)
            summary_ids = self.summary_model.generate(inputs,
                                                      max_length=250,
                                                      min_length=50,
                                                      length_penalty=2.0,
                                                      num_beams=4,
                                                      early_stopping=True)
            summary = self.summary_tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            if len(result) > 0:
                result = result + " "
            result = result + summary
        measure_time(start, f"Summary generation for {result_object['link']}")
        result_object[AnnotationTypes.SUMMARY.value] = result

