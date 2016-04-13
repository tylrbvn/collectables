@auth.requires_login()
def index():
    userActiveTrades = db((db.trades.UserProposing == auth.user.id) & (db.trades.UserProposed == db.auth_user.id) & \
                      (db.trades.status == 'active')).select()
    userAcceptedTrades = db((db.trades.UserProposing == auth.user.id) & (db.trades.UserProposed == db.auth_user.id) & \
                      (db.trades.status == 'accepted')).select()
    userRejectedTrades = db((db.trades.UserProposing == auth.user.id) & (db.trades.UserProposed == db.auth_user.id) & \
                      (db.trades.status == 'rejected')).select()
    userDraftTrades = db((db.trades.UserProposing == auth.user.id) & (db.trades.UserProposed == db.auth_user.id) & \
                      (db.trades.status == 'draft')).select()

    offeredActiveTrades = db((db.trades.UserProposed == auth.user.id) & (db.trades.UserProposing == db.auth_user.id) & \
                      (db.trades.status == 'active')).select()
    offeredAcceptedTrades = db((db.trades.UserProposed == auth.user.id) & (db.trades.UserProposing == db.auth_user.id) & \
                      (db.trades.status == 'accepted')).select()
    offeredRejectedTrades = db((db.trades.UserProposed == auth.user.id) & (db.trades.UserProposing == db.auth_user.id) & \
                      (db.trades.status == 'rejected')).select()
    return dict(userActiveTrades = userActiveTrades, userAcceptedTrades = userAcceptedTrades, \
                userrejectedTrades = userRejectedTrades, userDraftTrades = userDraftTrades, offeredActiveTrades=offeredActiveTrades, \
                offeredAcceptedTrades=offeredAcceptedTrades, offeredRejectedTrades=offeredRejectedTrades)

@auth.requires_login()
def view():
    trade = db.trades(request.args(0))
    if trade:
        if trade.UserProposing == auth.user.id or trade.UserProposed == auth.user.id:
            yourObjects = db((trade.id == db.objects_in_trade.trade_id) & (db.objects_in_trade.object_id == db.objects.id) & (db.objects.user_id == auth.user.id) & (db.objects.user_id == db.auth_user.id)).select()
            theirObjects = db((trade.id == db.objects_in_trade.trade_id) & (db.objects_in_trade.object_id == db.objects.id) & (db.objects.user_id != auth.user.id) & (db.objects.user_id == db.auth_user.id)).select()
            if trade.UserProposed==auth.user_id:
                partner = db.auth_user(trade.UserProposing)
            else:
                partner = db.auth_user(trade.UserProposed)
            if (trade.status == 'active') and (trade.awaiting == 'proposed' and auth.user.id == trade.UserProposed) or (trade.awaiting == 'proposing' and auth.user.id == trade.UserProposing):
                form = FORM(INPUT(_class = "btn btn-success", _value='Accept offer', _type="submit"),
                            A('Counter offer', _href=URL('trades', 'offer', args=trade.id), _class = "btn btn-primary"),
                            A('Reject offer', _href=URL('trades', 'reject', args=trade.id), _class = "btn btn-danger"),
                        _class="form-horizontal")

                #If the user accepts the trade, switch object id's of users in trade.
                if form.accepts(request, session):
                    #update trade to be accepted
                    trade.update_record(status='accepted')
                    if trade.UserProposing == auth.user.id: #If this is a trade that we proposed
                        for yourObject in yourObjects:
                            db.objects.insert(name = yourObject.objects.name,
                            type = yourObject.objects.type,
                            story = yourObject.objects.story,
                            value = yourObject.objects.value,
                            user_id = trade.UserProposed)
                            yourObject.objects.delete_record()
                        for theirObject in theirObjects:
                            db.objects.insert(name = theirObject.objects.name,
                            type = theirObject.objects.type,
                            story = theirObject.objects.story,
                            value = theirObject.objects.value,
                            user_id = trade.UserProposing)
                            theirObject.objects.delete_record()
                        db.commit()
                    else:
                        for yourObject in yourObjects:
                            db.objects.insert(name = yourObject.objects.name,
                            type = yourObject.objects.type,
                            story = yourObject.objects.story,
                            value = yourObject.objects.value,
                            user_id = trade.UserProposing)
                            yourObject.objects.delete_record()
                        for theirObject in theirObjects:
                            db.objects.insert(name = theirObject.objects.name,
                            type = theirObject.objects.type,
                            story = theirObject.objects.story,
                            value = theirObject.objects.value,
                            user_id = trade.UserProposed)
                            theirObject.objects.delete_record()
                        db.commit()
                    session.flash = "Trade successfully accepted, your objects have been exchanged!"
                    #Progress to offer own items
                    redirect(URL('trades', 'index'))
                return dict(trade=trade, yourObjects=yourObjects, theirObjects=theirObjects, partner = partner, form=form,  control='trade')
            else:
                return dict(trade=trade, yourObjects=yourObjects, theirObjects=theirObjects, partner = partner, control='trade')
        else:
            #If the user
            session.flash = "You don't have permission to view this trade - check that you haven't logged out"
            redirect(URL('trades', 'index'))
    else:
        session.flash = "Oops! This trade doesn't exist on our system. Sorry about that!"
        redirect(URL('trades', 'index'))
    # display trade items
    # provide + button functionality
    # will have to refresh page every 'press'

@auth.requires_login()
def offer():
    #Retrieve trade record using ID
    trade = db.trades(request.args(0))
    #Check trade exists
    if trade:
        if trade.status == 'active' or trade.status == 'draft':
            #Get list of users objects in have list
            #TODO: Remove objects already being offered
            objects = db((db.have_lists.user_id == auth.user.id) & (db.have_lists.object_id == db.objects.id)).select()
            form = FORM(DIV(LABEL('Select object to offer:', _for='objects', _class="control-label col-sm-3"),
                        DIV(SELECT(_name='objects', *[OPTION(objects[i].objects.name, _value=str(objects[i].objects.id)) for i in range(len(objects))],
                        _class = "form-control select"), _class="col-sm-4"), _class = "form-group"),
                        DIV(DIV(INPUT(_class = "btn btn-default", _value='Add to offer', _type="submit"),
                        A('Done', _href=URL('trades', 'view', args=trade.id), _class = "btn btn-primary"),
                        _class="col-sm-9 col-sm-offset-3"),
                        _class="form-group"),
                        _class="form-horizontal")
            if trade.awaiting == 'proposing' and auth.user.id == trade.UserProposing:
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
                return dict(form=form, no_of_objects = len(objects), objects_offered = objects_offered, trade_id = trade.id, control = 'offer')
            elif trade.awaiting == 'proposed' and auth.user.id == trade.UserProposed:
                if form.accepts(request, session):
                    #Ensure object not already in trade
                    count = db((db.objects_in_trade.trade_id == trade.id) & (db.objects_in_trade.object_id == request.vars.objects)).count()
                    if (count == 0):
                        db.objects_in_trade.insert(object_id = request.vars.objects,
                        trade_id = trade.id,
                        asked = True)
                        db.commit
                        response.flash = 'Object successfully added to offer'
                    else:
                        response.flash = "Error: You've already offered this object!"
                objects_offered = db((db.objects_in_trade.trade_id == trade.id) & (db.objects_in_trade.asked == True) & (db.objects_in_trade.object_id == db.objects.id) & (db.objects.user_id == db.auth_user.id)).select()
                return dict(form=form, no_of_objects = len(objects), objects_offered = objects_offered, trade_id = trade.id, control = 'offer')
        else:
            response.flash = 'Error: This trade is inactive!'
    else:
        response.flash = 'Error: This trade does not exist!'
    return dict()

@auth.requires_login()
def ask():
    #Retrieve trade record using ID
    trade = db.trades(request.args(0))
    #Check trade exists
    if trade:
        if trade.status == 'active' or trade.status == 'draft':
            #Get list of objects in other user's have list
            if trade.awaiting == 'proposing' and auth.user.id == trade.UserProposing:
                objects = db((db.have_lists.user_id == trade.UserProposed) & (db.have_lists.object_id == db.objects.id)).select()
                form = FORM(DIV(LABEL('Select object to request:', _for='objects', _class="control-label col-sm-3"),
                            DIV(SELECT(_name='objects', *[OPTION(objects[i].objects.name, _value=str(objects[i].objects.id)) for i in range(len(objects))],
                            _class = "form-control select"), _class="col-sm-4"), _class = "form-group"),
                            DIV(DIV(INPUT(_class = "btn btn-default", _value='Add to request', _type="submit"),
                            A('Done', _href=URL('trades', 'view', args=trade.id), _class = "btn btn-primary"),
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
                return dict(form=form, no_of_objects = len(objects), objects_requested = objects_requested, trade_id = trade.id, control = 'ask')
            elif trade.awaiting == 'proposed' and auth.user.id == trade.UserProposed:
                objects = db((db.have_lists.user_id == trade.UserProposing) & (db.have_lists.object_id == db.objects.id)).select()
                form = FORM(DIV(LABEL('Select object to request:', _for='objects', _class="control-label col-sm-3"),
                            DIV(SELECT(_name='objects', *[OPTION(objects[i].objects.name, _value=str(objects[i].objects.id)) for i in range(len(objects))],
                            _class = "form-control select"), _class="col-sm-4"), _class = "form-group"),
                            DIV(DIV(INPUT(_class = "btn btn-default", _value='Add to request', _type="submit"),
                            A('Done', _href=URL('trades', 'view', args=trade.id), _class = "btn btn-primary"),
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
                        response.flash = 'Object successfully added to request'
                    else:
                        response.flash = "Error: You've already requested this object!"
                objects_requested = db((db.objects_in_trade.trade_id == trade.id) & (db.objects_in_trade.offered == True) & (db.objects_in_trade.object_id == db.objects.id) & (db.objects.user_id == db.auth_user.id)).select()
                return dict(form=form, no_of_objects = len(objects), objects_requested = objects_requested, trade_id = trade.id, control = 'ask')
        else:
            response.flash = 'Error: You can not request in this trade!'
    else:
        response.flash = 'Error: This trade does not exist!'
    return dict()

@auth.requires_login()
def update():

    return dict()
@auth.requires_login()
def reject():
    #Retrieve trade record using ID
    trade = db.trades(request.args(0))
    #Check trade exists
    if trade:
        if trade.status == 'active':
            if (trade.awaiting == 'proposing' and auth.user.id == trade.UserProposing) or (trade.awaiting == 'proposed' and auth.user.id == trade.UserProposed):
                trade.update_record(status='rejected')
                session.flash = "Trade rejected!"
                redirect(URL('trades', 'index'))
    else:
        session.flash = 'Error: You do not have permission to do this'
    redirect(URL('trades', 'index'))
    return dict()

@auth.requires_login()
def remove():
    trade = db.trades(request.args(1))
    obj = db.objects(request.args(0))
    if (trade and obj):
        if (trade.awaiting == 'proposing' and auth.user.id == trade.UserProposing) or (trade.awaiting == 'proposed' and auth.user.id == trade.UserProposed):
            #Delete the link
            db((db.objects_in_trade.object_id == obj.id) & (db.objects_in_trade.trade_id == trade.id)).delete()
            session.flash = "'" + obj.name + "' successfully removed"
            redirect(URL('trades', 'view', args=[trade.id]))
        else:
            session.flash = "Error: You don't have permission to remove this"
            redirect(URL('trades', 'view', args=[trade.id]))
    else:
        session.flash = "Error: Invalid trade or object selected"
        redirect(URL('trades', 'index'))
    return dict()

@auth.requires_login()
def new():
    # source selects target
    # source redirected to view() and shown empty trade
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
    #     #Ensure object not already in
    #     trade_id = db.trades.insert(UserProposing = auth.user.id,
    #     UserProposed = request.vars.user
    #     )
    #     db.commit
    #     session.flash = "You are now making a trade, offer some objects!"
    #     #Progress to offer own items
        redirect(URL('trades', 'view', args=[trade_id]))
    return dict(form = form)