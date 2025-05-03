from base64 import b64decode, b64encode
from bson import ObjectId

def doc_id_to_b64(doc: dict|list[dict]):
        result = {} if type(doc) is list else { **doc }
        if type(doc) is list:
            results = [ doc_id_to_b64(document) for document in doc ]
            return results

        if "_id" in doc:
            if type(doc["_id"]) is ObjectId:
                result["_id"] = b64encode(doc["_id"].binary).decode()
            elif type(doc["_id"]) is str:
                result["_id"] = b64encode(bytes(doc["_id"], "utf-8")).decode()

        return result
    
def doc_b64_to_obj_id(doc: dict|list[dict]):
    result = { **doc }
    if type(doc) is list:
        results = [ doc_b64_to_obj_id(document) for document in doc ]
        return results
        
    if "_id" in doc:
        if type(doc["_id"]) is str:
            result["_id"] = ObjectId(b64decode(bytes(doc["_id"], "utf-8")))

    return result