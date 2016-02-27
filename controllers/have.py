@auth.requires_login()
def add():
    #Get list of users objects
    #TODO: Exclude objects that are already in list
    objects = db(db.objects.user_id == auth.user.id).select()
    #Form that displays list of object names but returns object ID
    form = FORM(DIV(LABEL('Select an object:', _for='objects', _class="control-label col-sm-3"),
                DIV(SELECT(_name='objects', *[OPTION(objects[i].name, _value=str(objects[i].id)) for i in range(len(objects))],
                _class = "form-control select"), _class="col-sm-4"), _class = "form-group"),
                DIV(DIV(INPUT(_class = "btn btn-primary", _value='Add to list', _type="submit"),
                A('Cancel', _href=URL('have', 'view', args=[auth.user.id]), _class = "btn btn-default"),
                _class="col-sm-9 col-sm-offset-3"),
                _class="form-group"),
                _class="form-horizontal")
    if form.accepts(request, session):
        #Ensure object not already in list
        count = db((db.have_lists.user_id == auth.user.id) & (db.have_lists.object_id == request.vars.objects)).count()
        if (count == 0):
            db.have_lists.insert(object_id = request.vars.objects)
            db.commit
            response.flash = "Object successfully added to list!"
        else:
            response.flash = "Error: List already contains the selected object!"
    elif form.errors:
        response.flash = 'One or more of the entries is incorrect'
    return dict(form = form, no_of_objects = len(objects))

@auth.requires_login()
def remove():
    obj = db.objects(request.args(0))
    if (obj):
        if (obj.user_id == auth.user.id):
            #Delete the record
            db((db.have_lists.object_id == obj.id) & (db.have_lists.user_id == auth.user.id)).delete()
            #TODO: This is not currently visible due to immediate redirect
            response.flash = "'" + obj.name + "' successfully removed from list'"
            redirect(URL('have', 'view', args=[auth.user.id]))
        else:
            response.flash = "You don't have permission to remove this"
    else:
        response.flash = "Invalid object selected"
    return dict()

def view():
    user = db.auth_user(request.args(0))
    if (user):
        #Get list of objects in users have list
        objects = db((db.have_lists.user_id == user.id) & (db.have_lists.object_id == db.objects.id)).select()
        if auth.is_logged_in():
            if (user.id == auth.user.id):
                #User logged in viewing their own list
                return dict(objects = objects, user = user, removal = True)
        #User viewing another user's list or user not logged in viewing a list
        return dict(objects = objects, user = user)
    else:
        response.flash = "Invalid user"
        return dict()
