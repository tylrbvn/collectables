@auth.requires_login()
def custom():
    db.objects.user_id.readable = db.objects.user_id.writable = False
    form = SQLFORM(db.objects, buttons = [TAG.button('Add to want list', _class = "btn-primary", _type="submit"), A("Cancel", _class = "btn btn-default", _href=URL('want', 'view', args=[auth.user.id]))])
    form.vars.user_id = None
    if form.accepts(request, session):
        db.want_lists.insert(object_id = form.vars.id,
        user_id = auth.user.id)
        db.commit
        response.flash = "New custom object '" + request.vars.name + "' successfully added to want list"
    elif form.errors:
        response.flash = 'One or more of the entries is incorrect:'
    return dict(form = form)

@auth.requires_login()
def remove():
    obj = db.objects(request.args(0))
    if (obj):
        if not obj.user_id:
            #Check how many want list custom object is in
            count = db(db.want_lists.object_id == obj.id).count()
            #If only in this want list, delete the custom objects
            if count == 1:
                db(db.objects.id == obj.id).delete()
        else:
            #Delete the record
            db((db.want_lists.object_id == obj.id) & (db.want_lists.user_id == auth.user.id)).delete()
        session.flash = "'" + obj.name + "' successfully removed from list'"
        redirect(URL('want', 'view', args=[auth.user.id]))
    else:
        response.flash = "Invalid object selected"
    return dict()

def view():
    user = db.auth_user(request.args(0))
    if (user):
        #Get list of objects in users want list
        objects = db((db.want_lists.user_id == user.id) & (db.want_lists.object_id == db.objects.id)).select()
        if auth.is_logged_in():
            if (user.id == auth.user.id):
                #User logged in viewing their own list
                return dict(objects = objects, user = user, removal = True)
        #User viewing another user's list or user not logged in viewing a list
        return dict(objects = objects, user = user)
    else:
        response.flash = "Invalid user"
        return dict()
