def collection():
    #Get the 8 largest public collections
    count = db.objects_in_collections.collection_id.count()  #What we are counting, the number of objects in each collection
    #Perform the joint query and get info about owner
    collections = db((db.collections.id==db.objects_in_collections.collection_id) & (db.collections.privacy == 'Public') & (db.collections.user_id == db.auth_user.id)).select(db.collections.name, db.collections.id, db.auth_user.username, count, groupby=db.objects_in_collections.collection_id, orderby=~count, limitby=(0,8))
    return dict(collections = collections)

def have():
    return dict()

def want():
    return dict()
