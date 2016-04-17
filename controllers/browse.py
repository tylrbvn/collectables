def collection():
    count = db.objects_in_collections.collection_id.count()  #What we are counting, the number of objects in each collection
    #Perform the joint query and get info about owner
    collections = db((db.collections.id==db.objects_in_collections.collection_id) & (db.collections.privacy == 'Public') & (db.collections.user_id == db.auth_user.id)).select(db.collections.name, db.collections.id, db.auth_user.username, count, groupby=db.objects_in_collections.collection_id, orderby=~count)
    return dict(collections = collections)

def have():
    count = db.have_lists.user_id.count()  #What we are counting, the number of objects in have list
    #Perform the joint query and get info about owner
    have_lists = db((db.have_lists.user_id == db.auth_user.id)).select(db.auth_user.id, db.auth_user.username, count, groupby=db.have_lists.user_id, orderby=~count)
    return dict(lists = have_lists)

def want():
    count = db.want_lists.user_id.count()  #What we are counting, the number of objects in want list
    #Perform the joint query and get info about owner
    want_lists = db((db.want_lists.user_id == db.auth_user.id)).select(db.auth_user.id, db.auth_user.username, count, groupby=db.want_lists.user_id, orderby=~count)
    return dict(lists = want_lists)
