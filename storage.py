import pymongo


class Storage:
    def __init__(self, parameters):
        self.parameters = parameters

    def save_df(self, df):
        pass

    def find_all(self):
        pass


class MongoDBStorage(Storage):
    def __init__(self, parameters):
        super().__init__(parameters)
        self.mongo_client = pymongo.MongoClient(self.parameters['host_url'])
        self.df_db = self.mongo_client["digital_footprint_db"]
        self.df_collection = self.df_db['digital_footprint']

    def save_df(self, df):
        df_result = self.df_collection.insert_one(df)
        return df_result

    def find_all(self):
        return self.df_collection.find()
