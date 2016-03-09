@auth.requires_login()
def index():
    trades = db((db.trades.UserProposing == auth.user.id) & (auth.user.id == db.auth_user.id)).select()
    if len(trades)>0:
        return dict(trades = trades)
    else:
        return dict()

@auth.requires_login()
def offer():
    #Retrieve trade record using ID
    trade = db.trades(request.args(0))
    #Check trade exists
    if trade:
        if trade.UserProposing == auth.user.id:
            #Get list of users objects in have list
            objects = db((db.have_lists.user_id == auth.user.id) & (db.have_lists.object_id == db.objects.id)).select()
            form = FORM(DIV(LABEL('Select objects to offer:', _for='objects', _class="control-label col-sm-3"),
                        DIV(SELECT(_name='objects', *[OPTION(objects[i].objects.name, _value=str(objects[i].objects.id)) for i in range(len(objects))],
                        _class = "form-control select"), _class="col-sm-4"), _class = "form-group"),
                        DIV(DIV(INPUT(_class = "btn btn-primary", _value='Add to offer', _type="submit"),
                        A('Cancel', _href=URL('trades', 'view', args=trade.id), _class = "btn btn-default"),
                        _class="col-sm-9 col-sm-offset-3"),
                        _class="form-group"),
                        _class="form-horizontal")
            if form.accepts(request, session):
                #Ensure object not already in collection
                count = db((db.objects_in_trade.trade_id == trade.id) & (db.objects_in_trade.object_id == request.vars.objects)).count()
                if (count == 0):
                    db.objects_in_trade.insert(object_id = request.vars.objects,
                    trade_id = trade.id,
                    offered = True)
                    db.commit
                    response.flash = 'Object successfully added to offer'
                else:
                    response.flash = "Error: You've already offered this object!"
            return dict(form=form, no_of_objects = len(objects))
        else:
            response.flash = 'Error: You can not offer in this trade!'
    else:
        response.flash = 'Error: This trade does not exist!'
    return dict()

@auth.requires_login()
def new():
    users = db(db.auth_user.id != auth.user.id).select()
    #my_objects = db((db.have_lists.user_id == auth.user.id) & (db.have_lists.object_id == db.objects.id)).select()
    #their_objects = db((db.have_lists.user_id == """their ID""") & (db.have_lists.object_id == db.objects.id)).select()

    form = FORM(
                DIV(LABEL('User:', _for='user', _class="control-label col-sm-3"),
                    DIV(SELECT(_name='user', *[OPTION(users[i].username, _value=str(users[i].id)) for i in range(len(users))],
                        _class = "form-control select"), _class="col-sm-4"),
                        _class = "form-group"),
                DIV(DIV(INPUT(_class = "btn btn-primary", _value='Start trade', _type="submit"),
                _class="col-sm-9 col-sm-offset-3"),
                _class="form-group"),
                _class="form-horizontal"
                #TODO: Either use or remove this
                #DIV(LABEL('Objects to offer:', _for='offer', _class="control-label col-sm-3"),
                #    DIV(SELECT(_name='offer', *[OPTION(my_objects[i].objects.name, _value=str(my_objects[i].objects.id)) for i in range(len(my_objects))],
                #        _class = "form-control select"), _class="col-sm-4"),
                #        _class = "form-group"),
                #DIV(LABEL('Objects to request:', _for='request', _class="control-label col-sm-3"),
                #    DIV(SELECT(_name='request', *[OPTION(db((db.have_lists.user_id == request.vars.user) & (db.have_lists.object_id == db.objects.id)).select()[i].objects.name,
                #               _value=str(db((db.have_lists.user_id == request.vars.user) & (db.have_lists.object_id == db.objects.id)).select()[i].objects.id))
                #               for i in range(len(db((db.have_lists.user_id == request.vars.user) & (db.have_lists.object_id == db.objects.id)).select()))],
                #        _class = "form-control select"), _class="col-sm-4"),
                #        _class = "form-group")
                )
    #Insert todays date of creation
    if form.accepts(request, session):
        #Ensure object not already in collection
        trade_id = db.trades.insert(UserProposing = auth.user.id,
        UserProposed = request.vars.user
        )
        db.commit
        response.flash = "Trade created successfully begun"
        #Redirect to view of the trade
        redirect(URL('trades', 'view', args=[trade_id]))
    return dict(form = form)
