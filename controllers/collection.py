@auth.requires_login()
def index():
    """Displays users collection"""
    #Find users pubic boxes
    public = db((db.collections.user_id==auth.user.id) & (db.collections.privacy == 'Public')).select()
    #Find users private boxes
    private = db((db.collections.user_id==auth.user.id) & (db.collections.privacy == 'Private')).select()
    return dict(public_collections = public, private_collections = private)

@auth.requires_login()
def new():
    db.collections.user_id.readable = db.collections.user_id.writable = False
    form = SQLFORM(db.collections)
    if form.accepts(request.vars, session):
        response.flash = 'New collection successfully created.'
    elif form.errors:
        response.flash = 'One or more of the entries is incorrect:'
    return dict(form = form)
