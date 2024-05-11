from bson.objectid import ObjectId


class MongoDBSearchService:
    def __init__(self, storage):
        self.storage = storage

    def get_named_entities_filters(self, named_entities):
        filters = []
        for entity in named_entities.keys():
            filters.append(
                {
                    "named_entities." + entity: {"$regex": "|".join(named_entities[entity]), "$options": "i"}
                }
            )
        return filters

    def get_additional_info_filters(self, additional_info):
        filters = []
        for info in additional_info.keys():
            filters.append(
                {
                    "additional_info." + info: {"$eq": additional_info[info]}
                }
            )
        return filters

    def aggregate_filters_with_or(self, filters):
        return self.storage.find_by_custom_query({"$or": filters})

    def aggregate_filters_with_and(self, filters):
        return self.storage.find_by_custom_query({"$and": filters})

    def find_by_query(self, query):
        return self.storage.find_by_custom_query(query)

    def get_query_find_before_date(self, date):
        return {"created_at": {"$lt": date}}

    def get_query_find_after_date(self, date):
        return {"created_at": {"$gt": date}}

    def get_query_find_in_period(self, from_date, to_date):
        return {"$and": [
            {"created_at": {"$gt": from_date}},
            {"created_at": {"$lt": to_date}},
        ]}

    def get_query_find_by_id(self, id):
        return {"_id": ObjectId(id)}

    def get_query_find_by_id_values(self, ids):
        object_ids = []
        for id in ids:
            object_ids.append(ObjectId(id))
        return {
            '_id': {
                '$in': object_ids
            }
        }

    def get_query_find_by_type(self, type):
        return {"type": type}

    # searches for any occurrence of at least one topic word in topics list
    def get_query_find_by_topics(self, topics):
        return {"topics": {"$regex": "|".join(topics), "$options": "i"}}

    # searches for any occurrence of at least one keyword in keywords list
    def get_query_find_by_keywords(self, keywords):
        return {"keywords": {"$regex": "|".join(keywords), "$options": "i"}}

    # searches for any occurrence of text inside summary
    def get_query_find_by_text_summary(self, text):
        return {"summary": {"$regex": text, "$options": "i"}}

    # searches for any occurrence of text inside extracted_text
    def get_query_find_by_text_extracted_text(self, text):
        return {"extracted_text": {"$regex": text, "$options": "i"}}
