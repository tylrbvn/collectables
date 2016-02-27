@auth.requires_login()
def remove():
    obj = db.objects(request.args(0))
    if (obj):
        #Delete the record
        db((db.want_lists.object_id == obj.id) & (db.want_lists.user_id == auth.user.id)).delete()
        #TODO: This is not currently visible due to immediate redirect
        response.flash = "'" + obj.name + "' successfully removed from list'"
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
