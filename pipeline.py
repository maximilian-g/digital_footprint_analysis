
class Pipeline:
    def __init__(self, df_extractor, extractor_methods, annotation_techniques, storage, search_service):
        # Instance of Extractor
        self.df_extractor = df_extractor
        """
        Assuming that extractors will be in following format:
        {
            "video":  extract_audio
            "audio":  extract_text_from_audio
            "document": extract_text_from_doc
        }
        """
        self.extractor_methods = extractor_methods
        """
        Assuming that analysis techniques will be in following format:
        {
            "video": [ extract_label_video ]
            "audio": [ extract_label_audio ]
            "text": [ extract_keywords, extract_topic, extract_named_entities ]
        }
        """
        self.annotation_techniques = annotation_techniques
        self.storage = storage
        self.search_service = search_service

    def process_data(self, df_list, save_immediately=False):
        df_list_result = list()
        for df in df_list:
            '''
            Assuming that data is already on local drive and will be in following format:
            {
                "video": "file://data/video_as_audio.mp4"
                "audio": "file://data/video_as_audio.wav"
                "text": "some text"
            }
            '''
            data = self.df_extractor.extract_data(df, self.extractor_methods)
            df_object = df.to_object()
            # Adding extracted data as labels if needed
            # for example in cases with speech recognition, we want to save text as well
            df.add_data_as_label(data, df_object)
            for key in data.keys():
                data_part = data[key]
                if key in self.annotation_techniques:
                    for technique in self.annotation_techniques[key]:
                        technique(data_part, df_object)

            df_object['annotated'] = True
            # saving every annotated DF immediately if save_immediately is True
            if save_immediately:
                self.save_annotated_df([df_object])
            df_list_result.append(df_object)
            # removing temp files from folder after analysis
            self.df_extractor.remove_temp_files()
        return df_list_result

    def save_annotated_df(self, df_list):
        # 2 cases:
        # update of existent (adding labels)
        # insertion of fully new digital footprint
        for df in df_list:
            if '_id' in df:
                query = self.search_service.get_query_find_by_id(id=df['_id'])
                self.storage.update_df_raw(query, df)
            else:
                self.storage.save_df(df)

