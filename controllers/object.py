@auth.requires_login()
def index():
    #Select all user's objects in alphabetical order by name
    objects = db((db.objects.user_id == auth.user.id) & (auth.user.id == db.auth_user.id)).select(orderby = db.objects.name)
    if len(objects)>0:
        return dict(objects = objects, control = 'object')
    else:
        return dict(control = 'object')

@auth.requires_login()
def add():
    #Retrieve object record using ID
    record = db.objects(request.args(0))
    #Get list of user's collections
    #TODO: Exclude collections that object is already in
    collections = db(db.collections.user_id == auth.user.id).select()
    #Check if there exists an object with ID
    if (record):
        #Check user owns that object
        if (record.user_id == auth.user.id):
            #Form that displays list of collection names but returns collection ID
            form = FORM(DIV(LABEL('Select a collection:', _for='collections', _class="control-label col-sm-3"),
                        DIV(SELECT(_id='collections',_name='collections', *[OPTION(collections[i].name, _value=str(collections[i].id)) for i in range(len(collections))],
                        _class = "form-control select"), _class="col-sm-4"), _class = "form-group"),
                        DIV(DIV(INPUT(_class = "btn btn-primary", _value='Add to collection', _type="submit"),
                        A('Cancel', _href=URL('object', 'view', args=record.id), _class = "btn btn-default"),
                        _class="col-sm-9 col-sm-offset-3"),
                        _class="form-group"),
                        _class="form-horizontal")

            if form.accepts(request, session):
                #Ensure object not already in collection
                count = db((db.objects_in_collections.collection_id == request.vars.collections) & (db.objects_in_collections.object_id == record.id)).count()
                if (count == 0):
                    db.objects_in_collections.insert(object_id = record.id,
                    collection_id = request.vars.collections)
                    db.commit
                    response.flash = "'" + record.name + "' successfully added to collection"
                else:
                    response.flash = "Error: Selected collection already contains '" + record.name + "'"
            elif form.errors:
                response.flash = 'One or more of the entries is incorrect:'
            return dict(form = form, object = record, no_of_collections = len(collections))
    return dict()

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
def have():
    #Retrieve object record using ID
    record = db.objects(request.args(0))
    #Check if there exists an object with ID
    if (record):
        #Check user owns that object
        if (record.user_id == auth.user.id):
            #Ensure object not already in list
            count = db((db.have_lists.object_id == record.id) & (db.have_lists.user_id == auth.user.id)).count()
            if (count == 0):
                db.have_lists.insert(object_id = record.id)
                db.commit
                session.flash = "'" + record.name + "' successfully added to have list"
            else:
                session.flash = "Error: '" + record.name + "' already in have list"
        else:
            session.flash = "Error: You don't have permission to add that"
            redirect(URL('have', 'view', args=[auth.user.id]))
    else:
        session.flash = "Error: Object does not exist"
        redirect(URL('have', 'view', args=[auth.user.id]))
    redirect(URL('object', 'view', args=[record.id]))
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
    object = db.objects(request.args(0))
    if (object):
        owner = db.auth_user(object.user_id)
        if (owner):
            #If own object
            if auth.is_logged_in():
                if (object.user_id == auth.user.id):
                    return dict(object = object, owner = owner)
            #If an object from another user's public collection
            public = db((db.objects_in_collections.object_id == object.id) & (db.objects_in_collections.collection_id == db.collections.id) & (db.collections.privacy == 'Public')).select()
            #If an object from another user's have list
            have_object = db(db.have_lists.object_id == db.objects.id).select()
            if len(public)>0 or len(have_object)>0:
                return dict(object = object, owner = owner)
        else:
            #It is a custom object which are public by default
            return dict(object = object)
    return dict()

@auth.requires_login()
def want():
    #Retrieve object record using ID
    record = db.objects(request.args(0))
    #Check if there exists an object with ID
    if (record):
        #Check to ensure that the object in another user's have list
        count = db(db.have_lists.object_id == record.id).count()
        if count > 0:
            #Ensure object not already in own want list
            count = db((db.want_lists.object_id == record.id) & (db.want_lists.user_id == auth.user.id)).count()
            if (count == 0):
                db.want_lists.insert(object_id = record.id)
                db.commit
                session.flash = "'" + record.name + "' successfully added to want list"
            else:
                session.flash = "Error: '" + record.name + "' already in want list"
            redirect(URL('object', 'view', args=[record.id]))
        else:
            session.flash = "Error: You do not have permission to add this item to want list"
    else:
        session.flash = "Error: Object does not exist"
    redirect(URL('want','view', args=[auth.user.id]))
    return dict()
