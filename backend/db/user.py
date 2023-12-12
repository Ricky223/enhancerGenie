from db.connect import client

user_collection = client["Users"]


# returns true if operation is successful
def insert_fp_to_user_history(username: str, fp: str) -> bool:
    user = user_collection.find_one({"username": username})
    if not user:
        return False

    if "history" in user:
        if user["history"] is None:
            newvalues = {"$set": {"history": [fp]}}
        else:
            for hash in user["history"]:
                if hash == fp:
                    return True

            user["history"].append(fp)
            newvalues = {"$set": {"history": user["history"]}}
    else:
        newvalues = {"$set": {"history": [fp]}}

    filter = {'username': username}

    user_collection.update_one(filter, newvalues)
    return True


def get_user_history(username: str):
    user = user_collection.find_one({"username": username})
    if not user:
        return []

    if "history" not in user:
        return []

    if user["history"] == None:
        return []

    return user["history"]

def delete_history_item(username: str, fp: str):
  user_collection.update_one({"username": username}, {
    "$pull": {"history": fp}
  })
