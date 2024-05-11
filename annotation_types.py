from enum import Enum

class AnnotationTypes(Enum):
    KEYWORDS = "keywords"
    TOPICS = "topics"
    NAMED_ENTITIES = "named_entities"
    SUMMARY = "summary"
    EXTRACTED_TEXT = "extracted_text"