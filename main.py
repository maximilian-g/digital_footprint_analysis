import extractor
import annotation
from digital_footprint import Document, Video
from extractor import Extractor
from pipeline import Pipeline
from storage import MongoDBStorage

if __name__ == "__main__":
    # Configuration
    base_folder = "some_folder"

    df_extractor = Extractor(base_folder)

    extraction_methods = {
        "document": extractor.extract_text_from_document,
        "video": extractor.extract_audio_from_video,
        "audio": extractor.extract_text_from_audio
    }

    annotator = annotation.Annotator()

    annotation_methods = {
        "text": [
            annotator.get_named_entities_from_text,
            annotator.get_keywords_from_text,
            annotator.get_topics_from_text,
        ]
    }

    storage = MongoDBStorage(parameters={
        "host_url": "some_host"
    })

    # Initializing pipeline with given configuration
    my_pipeline = Pipeline(df_extractor,
                           extraction_methods,
                           annotation_methods,
                           storage)

    df_list = [
        Document(None, "some_link", "document")
    ]

    annotated_df = my_pipeline.process_data(df_list)
    my_pipeline.save_annotated_df(annotated_df)

