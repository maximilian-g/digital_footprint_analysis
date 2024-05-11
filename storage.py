import pymongo


class Storage:
    def __init__(self, parameters):
        self.parameters = parameters

    def save_df(self, df):
        pass

    def find_all(self):
        pass

    def find_by_custom_query(self, custom_query):
        pass


class MongoDBStorage(Storage):
    def __init__(self, parameters):
        super().__init__(parameters)
        self.mongo_client = pymongo.MongoClient(self.parameters['host_url'])
        self.df_db = self.mongo_client["digital_footprint_db"]
        if 'collection' in parameters:
            self.df_collection = self.df_db[parameters['collection']]
        else:
            self.df_collection = self.df_db["digital_footprint"]

    def save_df(self, df):
        df_result = self.df_collection.insert_one(df)
        return df_result

    # creates expression, works with df as is
    def update_df_raw(self, id_filter, df):
        set_expr = {}
        for key in df:
            # id should not be in the expression, it is immutable
            if key != '_id':
                set_expr[key] = df[key]
        expression = {"$set": set_expr}
        return self.update_df(id_filter, expression)

    # to get id_filter - see service.py get_query_find_by_id
    def update_df(self, id_filter, expression):
        df_result = self.df_collection.update_one(id_filter, expression)
        return df_result

    def find_all(self):
        return self.df_collection.find()

    def find_by_custom_query(self, custom_query):
        return self.df_collection.find(custom_query)

    def delete_by_id(self, id_filter):
        df_result = self.df_collection.delete_one(id_filter)
        return df_result

    def find_not_annotated(self):
        return self.df_collection.find(
            {
                "$or": [
                    {"annotated": False},
                    {"annotated": {"$exists": False}}
                ]
            }
        )
