@auth.requires_login()
def index():
    """Displays users collection"""
    #Find users pubic boxes
    public = db((db.collections.user_id==auth.user.id) & (db.collections.privacy == 'Public')).select()
    #Find users private boxes
    private = db((db.collections.user_id==auth.user.id) & (db.collections.privacy == 'Private')).select()
    return dict(public_collections = public, private_collections = private)

@auth.requires_login()
def edit():
    #Retrieve collection using ID
    record = db.collections(request.args(0))
    db.collections.id.readable = db.collections.id.writable = False
    db.collections.user_id.readable = db.collections.user_id.writable = False
    #Check if there exists a collection with ID
    if(record):
        #Check user owns that collection
        if ((record.user_id == auth.user.id)):
            form=SQLFORM(db.collections, record)
            if form.accepts(request,session):
                response.flash = 'Collection has been successfully updated.'
            elif form.errors:
                response.flash = 'One or more of the entries is incorrect:'
            return dict(form=form)
    return dict()

@auth.requires_login()
def new():
    db.collections.user_id.readable = db.collections.user_id.writable = False
    form = SQLFORM(db.collections)
    if form.accepts(request.vars, session):
        response.flash = 'New collection successfully created.'
    elif form.errors:
        response.flash = 'One or more of the entries is incorrect:'
    return dict(form = form)

def view():
    collection_id = request.args(0)
    if (session.message):
        response.flash = session.message
        session.message = None
    if collection_id is not None:
        if auth.is_logged_in():
            colls = db((db.collections.id == collection_id) & ((db.collections.privacy == 'Public') | (db.collections.user_id == auth.user.id)) & (db.collections.user_id == db.auth_user.id)).select()
        else:
            colls = db((db.collections.id == collection_id) & (db.collections.privacy == 'Public') & (db.collections.user_id == db.auth_user.id)).select()
        if len(colls)>0:
            objects = db((db.objects_in_collections.collection_id == collection_id) & (db.objects_in_collections.object_id == db.objects.id) & (db.objects.user_id == db.auth_user.id)).select()
            return dict(collections = colls, objects = objects)
    return dict()
