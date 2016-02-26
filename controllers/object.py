@auth.requires_login()
def new():
    db.objects.user_id.readable = db.objects.user_id.writable = False
    form = SQLFORM(db.objects)
    if form.accepts(request.vars, session):
        response.flash = 'New object successfully created.'
    elif form.errors:
        response.flash = 'One or more of the entries is incorrect:'
    return dict(form = form)
