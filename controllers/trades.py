@auth.requires_login()
def index():
    userActiveTrades = db((db.trades.UserProposing == auth.user.id) & (db.trades.UserProposed == db.auth_user.id) & \
                      (db.trades.status == 'active')).select()
    userAcceptedTrades = db((db.trades.UserProposing == auth.user.id) & (db.trades.UserProposed == db.auth_user.id) & \
                      (db.trades.status == 'accepted')).select()
    userrejectedTrades = db((db.trades.UserProposing == auth.user.id) & (db.trades.UserProposed == db.auth_user.id) & \
                      (db.trades.status == 'rejected')).select()

    offeredActiveTrades = db((db.trades.UserProposed == auth.user.id) & (db.trades.UserProposing == db.auth_user.id) & \
                      (db.trades.status == 'active')).select()
    offeredAcceptedTrades = db((db.trades.UserProposed == auth.user.id) & (db.trades.UserProposing == db.auth_user.id) & \
                      (db.trades.status == 'accepted')).select()
    offeredRejectedTrades = db((db.trades.UserProposed == auth.user.id) & (db.trades.UserProposing == db.auth_user.id) & \
                      (db.trades.status == 'rejected')).select()
    return dict(userActiveTrades = userActiveTrades, userAcceptedTrades = userAcceptedTrades, \
                userrejectedTrades = userrejectedTrades, offeredActiveTrades=offeredActiveTrades, \
                offeredAcceptedTrades=offeredAcceptedTrades, offeredRejectedTrades=offeredRejectedTrades)

@auth.requires_login()
def view():
    trade_id = request.args(0) #Get trade id from URL
    objects_in_trade = db(trade_id == db.objects_in_trade.trade_id).select()
    trade = db(trade_id == db.trades.id).select().first() #We need to find who proposed to trade to determine whose objects are whose
    yourObjects = []
    theirObjects = []
    if trade.UserProposing == auth.user.id: #If this is a trade that we proposed
        for object in objects_in_trade:
            if object.offered == True:
                yourObjects += db(object.object_id == db.objects.id).select()
            else:
                theirObjects += db(object.object_id == db.objects.id).select()
    else: #This is a trade that is being proposed to us
        for object in objects_in_trade:
            if object.offered == True:
                theirObjects += db(object.object_id == db.objects.id).select()
            else:
                yourObjects += db(object.object_id == db.objects.id).select()
    if trade.status == 'active':
        form = FORM(DIV(DIV(INPUT(_class = "btn btn-success", _value='Accept Trade', _type="submit"),
                    A('Amend Offer', _href=URL('trades', 'offer', args=trade_id), _class = "btn btn-primary"),
                _class="col-sm-9 col-sm-offset-3"),
                _class="form-group"),
                _class="form-horizontal")

        #If the user accepts the trade, switch object id's of users in trade.
        if form.accepts(request, session):
            #update trade to be accepted
            trade.update_record(status='accepted')
            if trade.UserProposing == auth.user.id: #If this is a trade that we proposed
                for yourObject in yourObjects:
                    yourObject.update_record(user_id=trade.UserProposed) #object user id is now the user we proposed to
                for theirObject in theirObjects:
                    theirObject.update_record(user_id=trade.UserProposing) #their objects are ours
            else:
                for yourObject in yourObjects:
                    yourObject.update_record(user_id=trade.UserProposing) #object user id is now the user proposing
                for theirObject in theirObjects:
                    theirObject.update_record(user_id=trade.UserProposed) #their objects are ours

            session.flash = "Trade Completed! Enjoy your new items!"
            #Progress to offer own items
            redirect(URL('trades', 'index'))
        return dict(trade=trade, yourObjects=yourObjects, theirObjects=theirObjects, form=form)
    else:
        return dict(trade=trade, yourObjects=yourObjects, theirObjects=theirObjects)

@auth.requires_login()
def offer():
    #Retrieve trade record using ID
    trade = db.trades(request.args(0))
    #Check trade exists
    if trade:
        if trade.UserProposing == auth.user.id:
            #Get list of users objects in have list
            #TODO: Remove objects already being offered
            objects = db((db.have_lists.user_id == auth.user.id) & (db.have_lists.object_id == db.objects.id)).select()
            form = FORM(DIV(LABEL('Select object to offer:', _for='objects', _class="control-label col-sm-3"),
                        DIV(SELECT(_name='objects', *[OPTION(objects[i].objects.name, _value=str(objects[i].objects.id)) for i in range(len(objects))],
                        _class = "form-control select"), _class="col-sm-4"), _class = "form-group"),
                        DIV(DIV(INPUT(_class = "btn btn-default", _value='Add to offer', _type="submit"),
                        A('Next step', _href=URL('trades', 'ask', args=trade.id), _class = "btn btn-primary"),
                        _class="col-sm-9 col-sm-offset-3"),
                        _class="form-group"),
                        _class="form-horizontal")
            if form.accepts(request, session):
                #Ensure object not already in trade
                count = db((db.objects_in_trade.trade_id == trade.id) & (db.objects_in_trade.object_id == request.vars.objects)).count()
                if (count == 0):
                    db.objects_in_trade.insert(object_id = request.vars.objects,
                    trade_id = trade.id,
                    offered = True)
                    db.commit
                    response.flash = 'Object successfully added to offer'
                else:
                    response.flash = "Error: You've already offered this object!"
            objects_offered = db((db.objects_in_trade.trade_id == trade.id) & (db.objects_in_trade.offered == True) & (db.objects_in_trade.object_id == db.objects.id) & (db.objects.user_id == db.auth_user.id)).select()
            return dict(form=form, no_of_objects = len(objects), objects_offered = objects_offered, control = 'offer')
        else:
            response.flash = 'Error: You can not offer in this trade!'
    else:
        response.flash = 'Error: This trade does not exist!'
    return dict()

@auth.requires_login()
def ask():
    #Retrieve trade record using ID
    trade = db.trades(request.args(0))
    #Check trade exists
    if trade:
        if trade.UserProposing == auth.user.id:
            #Get list of objects in other user's have list
            objects = db((db.have_lists.user_id == trade.UserProposed) & (db.have_lists.object_id == db.objects.id)).select()
            form = FORM(DIV(LABEL('Select object to request:', _for='objects', _class="control-label col-sm-3"),
                        DIV(SELECT(_name='objects', *[OPTION(objects[i].objects.name, _value=str(objects[i].objects.id)) for i in range(len(objects))],
                        _class = "form-control select"), _class="col-sm-4"), _class = "form-group"),
                        DIV(DIV(INPUT(_class = "btn btn-default", _value='Add to request', _type="submit"),
                        A('Initiate trade', _href=URL('trades', 'view', args=trade.id), _class = "btn btn-primary"),
                        _class="col-sm-9 col-sm-offset-3"),
                        _class="form-group"),
                        _class="form-horizontal")
            if form.accepts(request, session):
                #Ensure object not already in trade
                count = db((db.objects_in_trade.trade_id == trade.id) & (db.objects_in_trade.object_id == request.vars.objects)).count()
                if (count == 0):
                    db.objects_in_trade.insert(object_id = request.vars.objects,
                    trade_id = trade.id,
                    asked = True)
                    db.commit
                    response.flash = 'Object successfully added to request'
                else:
                    response.flash = "Error: You've already requested this object!"
            objects_requested = db((db.objects_in_trade.trade_id == trade.id) & (db.objects_in_trade.asked == True) & (db.objects_in_trade.object_id == db.objects.id) & (db.objects.user_id == db.auth_user.id)).select()
            return dict(form=form, no_of_objects = len(objects), objects_requested = objects_requested, control = 'ask')
        else:
            response.flash = 'Error: You can not request in this trade!'
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
                DIV(DIV(INPUT(_class = "btn btn-primary", _value='Next step', _type="submit"),
                A('Cancel', _href=URL('default', 'index'), _class = "btn btn-danger"),
                _class="col-sm-9 col-sm-offset-3"),
                _class="form-group"),
                _class="form-horizontal")
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
    #Insert todays date of creation
    if form.accepts(request, session):
        #Ensure object not already in collection
        trade_id = db.trades.insert(UserProposing = auth.user.id,
        UserProposed = request.vars.user
        )
        db.commit
        session.flash = "Trade successfully created, now offer some objects!"
        #Progress to offer own items
        redirect(URL('trades', 'offer', args=[trade_id]))
    return dict(form = form)
