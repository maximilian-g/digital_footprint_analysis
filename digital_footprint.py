import datetime


class DigitalFootprint:
    def __init__(self, id, link, type, created_at=datetime.datetime.now().replace(microsecond=0).isoformat()):
        self.id = id
        self.link = link
        self.type = type
        self.created_at = created_at

    def to_object(self):
        result = {
            "link": self.link,
            "type": self.type,
            "created_at": self.created_at
        }
        if self.id is not None:
            result["_id"] = self.id
        return result

    def extract_data(self, parameters):
        pass


class Video(DigitalFootprint):
    def __init__(self, id, link, type):
        super().__init__(id, link, type)
        self.id = id
        self.link = link
        self.type = type

    def extract_data(self, parameters):
        # getting extractors from parameters and extracting data from initial file
        initial_file = parameters['initial_file_path']
        extractors = parameters['extractors']
        ''' 
        Passing initial_file 2 times, because first arg is initial path to file,
        second argument is target path to new file with ".wav" extension
        '''
        audio_path = extractors['video'](initial_file, initial_file)
        print("Extracting text from audio")
        text = extractors['audio'](audio_path)
        print("Finished extracting text from audio")
        return {
            "video": initial_file,
            "audio": audio_path,
            "text": text
        }


class Audio(DigitalFootprint):
    def __init__(self, id, link, type):
        super().__init__(id, link, type)
        self.id = id
        self.link = link
        self.type = type

    def extract_data(self, parameters):
        # getting extractors from parameters and extracting data from initial file
        initial_file = parameters['initial_file_path']
        extractors = parameters['extractors']
        text = extractors['audio'](initial_file)
        return {
            "text": text
        }


class Document(DigitalFootprint):
    def __init__(self, id, link, type):
        super().__init__(id, link, type)
        self.id = id
        self.link = link
        self.type = type

    def extract_data(self, parameters):
        # getting extractors from parameters and extracting data from initial file
        initial_file = parameters['initial_file_path']
        extractors = parameters['extractors']
        text = extractors['document'](initial_file)
        return {
            "text": text
        }
