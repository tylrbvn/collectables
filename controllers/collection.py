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

@auth.requires_login()
def search():
    object_types = ['',
                    'Advertising and brand',
                    'Architectural',
                    'Art',
                    'Books, magazines and paper',
                    'Clothing, fabric and textiles',
                    'Coins, currency and stamps',
                    'Film and television',
                    'Glass and pottery',
                    'Household items',
                    'Memorabilia',
                    'Music',
                    'Nature and animals',
                    'Sports',
                    'Technology',
                    'Themed',
                    'Toys and Games']

    form = FORM(DIV(LABEL('Name:', _for='name', _class="control-label col-sm-3"),
                DIV(INPUT(_class = "form-control string", _name='name', _type="text"), _class="col-sm-3"),
                _class="form-group"),
                DIV(LABEL('Type:', _for='type', _class="control-label col-sm-3"),
                            DIV(SELECT(_name='type', *[OPTION(type) for type in object_types],
                            _class = "form-control select"), _class="col-sm-4"), _class = "form-group"),
                DIV(LABEL('Value:', _for='value', _class="control-label col-sm-3"),
                DIV(INPUT(_class = "form-control string", _name='value', _type="double"), _class="col-sm-3"),
                _class="form-group"),
                DIV(LABEL('Owned by:', _for='owner', _class="control-label col-sm-3"),
                DIV(INPUT(_class = "form-control string", _name='owner', _type="text"), _class="col-sm-3"),
                _class="form-group"),
                DIV(DIV(INPUT(_class = "btn btn-primary", _value='Search', _type="submit"),
                _class="col-sm-9 col-sm-offset-3"),
                _class="form-group"),
                _class="form-horizontal")

    if form.accepts(request, session):
        search_term = ""
        if (len(request.vars.name) > 0):
            name_term = "%" + request.vars.name + "%"
            search_term = (db.objects.name.like(name_term))
        if (len(request.vars.type) > 0):
            type_term = "%" + request.vars.type + "%"
            if (search_term):
                search_term = search_term & (db.objects.type.like(type_term))
            else:
                search_term = (db.objects.type.like(type_term))
        if (len(request.vars.value) > 0):
            value_term = "%" + request.vars.value + "%"
            if (search_term):
                search_term = search_term & (db.objects.value.like(value_term))
            else:
                search_term = (db.objects.value.like(value_term))
        if (len(request.vars.owner) > 0):
            #Look up user ID given username
            user = db.auth_user(username = request.vars.owner)
            #If user exists with username
            if (user):
                owner_term = "%" + str(user.id) + "%"
                if (search_term):
                    search_term = search_term & (db.objects.user_id.like(owner_term))
                else:
                    search_term = (db.objects.user_id.like(owner_term))
        #Allow for a blank search to return all objects
        constraint = (((db.objects_in_collections.collection_id == db.collections.id) & (db.collections.privacy == 'Public') &
                                (db.objects_in_collections.object_id == db.objects.id)) | (db.objects.user_id == auth.user.id)) & (db.objects.user_id == db.auth_user.id)
        if (search_term):
            search_term =  search_term & constraint
        else:
            search_term = constraint
        #Get results in alphabetical order by title
        results = db(search_term).select(orderby=db.objects.name)
        #Filter out duplicate results caused by objects being in public collections
        #Not able to get select query do this due to complexity in use of distinct
        distinct = dict()
        for i in range(len(results)):
            if results[i].objects.id not in distinct:
                distinct[results[i].objects.id] = i
        #Output success indicated by number of distinct result(s)
        output = "Search complete: " + str(len(distinct)) + " result"
        if(len(distinct) != 1): output += "s"
        response.flash = output
    else:
        if form.errors:
            response.flash = 'One or more of the entries is incorrect'
        results = dict()
        distinct = dict()
    return dict(form = form, results = results, distinct = distinct)

@auth.requires_login()
def remove():
    collection = db.collections(request.args(0))
    obj = db.objects(request.args(1))
    if (collection and obj):
        if ((collection.user_id == auth.user.id) & (obj.user_id == auth.user.id)):
            #Delete the link
            db((db.objects_in_collections.object_id == obj.id) & (db.objects_in_collections.collection_id == collection.id)).delete()
            #TODO: This is not currently visible due to immediate redirect
            response.flash = "'" + obj.name + "' successfully removed from collection '" + collection.name + "'"
            redirect(URL('collection', 'view', args=[collection.id]))
        else:
            response.flash = "You don't have permission to remove this"
    else:
        response.flash = "Invalid colleciton or object selected"
    return dict()

def view():
    collection_id = request.args(0)
    if collection_id is not None:
        if auth.is_logged_in():
            colls = db((db.collections.id == collection_id) & ((db.collections.privacy == 'Public') | (db.collections.user_id == auth.user.id)) & (db.collections.user_id == db.auth_user.id)).select()
        else:
            colls = db((db.collections.id == collection_id) & (db.collections.privacy == 'Public') & (db.collections.user_id == db.auth_user.id)).select()
        if len(colls)>0:
            objects = db((db.objects_in_collections.collection_id == collection_id) & (db.objects_in_collections.object_id == db.objects.id) & (db.objects.user_id == db.auth_user.id)).select()
            return dict(collections = colls, objects = objects, removal = True)
    return dict()
