@auth.requires_login()
def edit():
    #Retrieve object using ID
    record = db.objects(request.args(0))
    db.objects.id.readable = db.objects.id.writable = False
    db.objects.user_id.readable = db.objects.user_id.writable = False
    #Check if there exists an object with ID
    if(record):
        #Check user owns that object
        if ((record.user_id == auth.user.id)):
            form=SQLFORM(db.objects, record, deletable=True)
            if form.accepts(request,session):
                response.flash = 'Object has been successfully updated.'
            elif form.errors:
                response.flash = 'One or more of the entries is incorrect:'
            return dict(form=form)
    return dict()

@auth.requires_login()
def new():
    db.objects.user_id.readable = db.objects.user_id.writable = False
    form = SQLFORM(db.objects)
    if form.accepts(request.vars, session):
        response.flash = 'New object successfully created.'
    elif form.errors:
        response.flash = 'One or more of the entries is incorrect:'
    return dict(form = form)

def view():
    object_id = request.args(0)
    if object_id is not None:
        #If own object
        if auth.is_logged_in():
            objects = db((db.objects.id == object_id) & (db.objects.user_id == auth.user.id) & (db.objects.user_id == db.auth_user.id)).select()
            if len(objects)>0:
                return dict(objects = objects)
        #If an object from another user's public collection
        public = db((db.objects_in_collections.object_id == object_id) & (db.objects_in_collections.collection_id == db.collections.id) & (db.collections.privacy == 'Public')).select()
        if len(public)>0:
            objects = db((db.objects.id == object_id) & (db.objects.user_id == db.auth_user.id)).select()
            return dict(objects = objects)
    return dict()
