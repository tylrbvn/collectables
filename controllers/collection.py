@auth.requires_login()
def index():
    """Displays users collection"""
    #Find users pubic collections
    public = db((db.collections.user_id==auth.user.id) & (db.collections.privacy == 'Public')).select()
    #Find users private collections
    private = db((db.collections.user_id==auth.user.id) & (db.collections.privacy == 'Private')).select()
    return dict(public_collections = public, private_collections = private)

@auth.requires_login()
def add():
    #Retrieve collection record using ID
    record = db.collections(request.args(0))
    #Get list of users objects
    #TODO: Exclude objects that are already in collection
    objects = db(db.objects.user_id == auth.user.id).select()
    #Check if there exists a collection with ID
    if (record):
        #Check user owns that collection
        if (record.user_id == auth.user.id):
            #Form that displays list of object names but returns object ID
            form = FORM(DIV(LABEL('Select an object:', _for='objects', _class="control-label col-sm-3"),
                        DIV(SELECT(_name='objects', *[OPTION(objects[i].name, _value=str(objects[i].id)) for i in range(len(objects))],
                        _class = "form-control select"), _class="col-sm-4"), _class = "form-group"),
                        DIV(DIV(INPUT(_class = "btn btn-primary", _value='Add to collection', _type="submit"),
                        A('Cancel', _href=URL('collection', 'view', args=record.id), _class = "btn btn-default"),
                        _class="col-sm-9 col-sm-offset-3"),
                        _class="form-group"),
                        _class="form-horizontal")
            if form.accepts(request, session):
                #Ensure object not already in collection
                count = db((db.objects_in_collections.collection_id == record.id) & (db.objects_in_collections.object_id == request.vars.objects)).count()
                if (count == 0):
                    db.objects_in_collections.insert(object_id = request.vars.objects,
                    collection_id = record.id)
                    db.commit
                    response.flash = "Object successfully added to collection '" + record.name + "'"
                else:
                    response.flash = "Error: '" + record.name + "' already contains the selected object!"
            elif form.errors:
                response.flash = 'One or more of the entries is incorrect'
            return dict(form = form, collection = record, no_of_objects = len(objects))
    return dict()

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
            form=SQLFORM(db.collections, record, deletable=True)
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
