import datetime
from enum import Enum

from utils import extract_safely
from annotation_types import AnnotationTypes
from time_measurement import measure_time
from datetime import datetime
from auth_methods import AuthMethods

class DigitalFootprintType(Enum):
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"


# list of types of data that can be extracted from digital footprint
class DigitalFootprintDataType(Enum):
    AUDIO = "audio"
    VIDEO = "video"
    TEXT = "text"


def map_to_audio_df(df_object):
    return Audio(id=str(df_object['_id']) if '_id' in df_object else None, link=df_object['link'],
                 created_at=extract_safely(df_object, 'created_at', datetime.now().replace(microsecond=0)),
                 last_labeled_at=extract_safely(df_object, 'last_labeled_at'),
                 auth_data=extract_safely(df_object, 'auth_data'),
                 annotated=extract_safely(df_object, 'annotated'),
                 additional_info=extract_safely(df_object, 'additional_info'),
                 labels=extract_needed_labels(df_object))


def map_to_video_df(df_object):
    return Video(id=str(df_object['_id']) if '_id' in df_object else None, link=df_object['link'],
                 created_at=extract_safely(df_object, 'created_at', datetime.now().replace(microsecond=0)),
                 last_labeled_at=extract_safely(df_object, 'last_labeled_at'),
                 auth_data=extract_safely(df_object, 'auth_data'),
                 annotated=extract_safely(df_object, 'annotated'),
                 additional_info=extract_safely(df_object, 'additional_info'),
                 labels=extract_needed_labels(df_object))


def map_to_document_df(df_object):
    return Document(id=str(df_object['_id']) if '_id' in df_object else None, link=df_object['link'],
                    created_at=extract_safely(df_object, 'created_at', datetime.now().replace(microsecond=0)),
                    last_labeled_at=extract_safely(df_object, 'last_labeled_at'),
                    auth_data=extract_safely(df_object, 'auth_data'),
                    annotated=extract_safely(df_object, 'annotated'),
                    additional_info=extract_safely(df_object, 'additional_info'))

# for video and audio we store transcription text, we need to extract it if we have it
# in order to not recognize speech second time, because it is time-consuming
def extract_needed_labels(df_object):
    current_labels = None
    if AnnotationTypes.EXTRACTED_TEXT.value in df_object:
        current_labels = {
            AnnotationTypes.EXTRACTED_TEXT.value: df_object[AnnotationTypes.EXTRACTED_TEXT.value]
        }
    return current_labels

OBJECT_TO_DF_MAPPER = {
    DigitalFootprintType.AUDIO.value: map_to_audio_df,
    DigitalFootprintType.VIDEO.value: map_to_video_df,
    DigitalFootprintType.DOCUMENT.value: map_to_document_df,
}


def create_df_from_object(df_object):
    if 'type' in df_object and df_object['type'] is not None \
            and df_object['type'] in OBJECT_TO_DF_MAPPER:
        return OBJECT_TO_DF_MAPPER[df_object['type']](df_object)

    print("Unknown type or type of Digital Footprint is not provided")
    return None


class DigitalFootprint:
    def __init__(self, id, link, type, auth_data=None,
                 created_at=datetime.now().replace(microsecond=0),
                 last_labeled_at=None, annotated=False,
                 additional_info=None, labels=None):
        self.id = id
        self.link = link
        self.type = type
        self.created_at = created_at
        self.last_labeled_at = last_labeled_at
        self.auth_data = auth_data
        if self.auth_data is not None:
            self.auth_data['type'] = AuthMethods.from_str(self.auth_data['type'])
        if annotated is None:
            annotated = False
        self.annotated = annotated
        self.additional_info = additional_info
        self.labels = labels

    def to_object(self):
        result = {
            "link": self.link,
            "type": self.type,
            "created_at": self.created_at,
            "annotated": self.annotated
        }
        if self.last_labeled_at is not None:
            result["last_labeled_at"] = self.last_labeled_at
        if self.id is not None:
            result["_id"] = self.id
        # additional information about digital footprint,
        # for example - who produced digital footprint or file name of content
        if self.additional_info is not None:
            result["additional_info"] = {}
            for key in self.additional_info.keys():
                result["additional_info"][key] = self.additional_info[key]
        if self.auth_data is not None:
            result["auth_data"] = {}
            for key in self.auth_data.keys():
                result["auth_data"][key] = self.auth_data[key]
            result["auth_data"]["type"] = self.auth_data["type"].value["name"]
        # assigning labels to the result object if there was any
        if self.labels is not None:
            for key in self.labels.keys():
                result[key] = self.labels[key]
        return result

    def extract_data(self, parameters):
        pass

    # method is designed to add some extracted data parts as a label to a df object
    # as an example - text that is recognized using speech recognition is a label as well
    # this method is always called when digital footprint is being labeled
    def add_data_as_label(self, data_parts, df_object):
        pass


class Video(DigitalFootprint):
    def __init__(self, link, id=None, type=DigitalFootprintType.VIDEO.value,
                 auth_data=None, created_at=datetime.now().replace(microsecond=0),
                 last_labeled_at=None, annotated=False, additional_info=None, labels=None):
        super().__init__(id, link, type, auth_data=auth_data, created_at=created_at, last_labeled_at=last_labeled_at,
                         annotated=annotated, additional_info=additional_info, labels=labels)
        self.id = id
        self.link = link
        self.type = type

    def extract_data(self, parameters):
        # getting extractors from parameters and extracting data from initial file
        initial_file = parameters['initial_file_path']
        extractors = parameters['extractors']
        start = datetime.now()
        ''' 
        Passing initial_file 2 times, because first arg is initial path to file,
        second argument is target path to new file with ".wav" extension
        '''
        audio_path = extractors[self.type](initial_file, initial_file)
        measure_time(start, f"Audio extraction for video - {initial_file}")

        if self.labels is not None and \
                AnnotationTypes.EXTRACTED_TEXT.value in self.labels:
            text = self.labels[AnnotationTypes.EXTRACTED_TEXT.value]
        else:
            start = datetime.now()
            text = extractors[DigitalFootprintType.AUDIO.value](audio_path)
            measure_time(start, f"Text extraction for video - {initial_file}")
        return {
            DigitalFootprintDataType.VIDEO.value: initial_file,
            DigitalFootprintDataType.AUDIO.value: audio_path,
            DigitalFootprintDataType.TEXT.value: text
        }

    def add_data_as_label(self, data_parts, df_object):
        super().add_data_as_label(data_parts, df_object)
        if DigitalFootprintDataType.TEXT.value in data_parts:
            df_object[AnnotationTypes.EXTRACTED_TEXT.value] = data_parts[DigitalFootprintDataType.TEXT.value]


class Audio(DigitalFootprint):
    def __init__(self, link, id=None, type=DigitalFootprintType.AUDIO.value,
                 auth_data=None, created_at=datetime.now().replace(microsecond=0),
                 last_labeled_at=None, annotated=False, additional_info=None, labels=None):
        super().__init__(id, link, type, auth_data=auth_data, created_at=created_at, last_labeled_at=last_labeled_at,
                         annotated=annotated, additional_info=additional_info, labels=labels)
        self.id = id
        self.link = link
        self.type = type

    def extract_data(self, parameters):
        # getting extractors from parameters and extracting data from initial file
        initial_file = parameters['initial_file_path']
        extractors = parameters['extractors']
        if self.labels is not None and \
                AnnotationTypes.EXTRACTED_TEXT.value in self.labels:
            text = self.labels[AnnotationTypes.EXTRACTED_TEXT.value]
        else:
            start = datetime.now()
            text = extractors[self.type](initial_file)
            measure_time(start, f"Text extraction for audio - {initial_file}")
        return {
            DigitalFootprintDataType.TEXT.value: text
        }

    def add_data_as_label(self, data_parts, df_object):
        super().add_data_as_label(data_parts, df_object)
        if DigitalFootprintDataType.TEXT.value in data_parts:
            df_object[AnnotationTypes.EXTRACTED_TEXT.value] = data_parts[DigitalFootprintDataType.TEXT.value]


class Document(DigitalFootprint):
    def __init__(self, link, id=None, type=DigitalFootprintType.DOCUMENT.value,
                 auth_data=None, created_at=datetime.now().replace(microsecond=0),
                 last_labeled_at=None, annotated=False, additional_info=None, labels=None):
        super().__init__(id, link, type, auth_data=auth_data, created_at=created_at, last_labeled_at=last_labeled_at,
                         annotated=annotated, additional_info=additional_info, labels=labels)
        self.id = id
        self.link = link
        self.type = type

    def extract_data(self, parameters):
        # getting extractors from parameters and extracting data from initial file
        initial_file = parameters['initial_file_path']
        extractors = parameters['extractors']
        start = datetime.now()
        text = extractors[self.type](initial_file)
        measure_time(start, f"Text extraction for document - {initial_file}")
        return {
            DigitalFootprintDataType.TEXT.value: text
        }
