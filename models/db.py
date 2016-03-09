# Connect database and store in the global variable collections
db = DAL('sqlite://collections.db')

# -*- coding: utf-8 -*-

from gluon.tools import Auth, Service, PluginManager

auth = Auth(db)
service = Service()
plugins = PluginManager()

## custom user table
db.define_table(
    auth.settings.table_user_name,
    Field('username', length=128, default=''),
    Field('password', 'password', length=512,  # required
          readable=False, label='Password'),
    Field('registration_key', length=512,  # required
          writable=False, readable=False, default=''),
    Field('reset_password_key', length=512,  # required
          writable=False, readable=False, default=''),
    Field('registration_id', length=512,  # required
          writable=False, readable=False, default=''))

## validators
custom_auth_table = db[auth.settings.table_user_name]  # get the custom_auth_table
custom_auth_table.username.requires = [
    IS_NOT_EMPTY(error_message=auth.messages.is_empty),
    IS_NOT_IN_DB(db, custom_auth_table.username)]

auth.settings.table_user = custom_auth_table  # tell auth to use custom_auth_table

## create all tables needed by auth
auth.define_tables(username=True)

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True
auth.settings.actions_disabled = ['retrieve_username', 'request_reset_password']

## login after registration and redirect to home page
# auth.settings.login_after_registration = True
# auth.settings.login_next = URL('default', 'boxes.html')

object_types = ['Advertising and brand',
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

# Objects Table: stores details on each object
db.define_table('objects',
                Field('name', requires=IS_NOT_EMPTY()),
                Field('user_id', db.auth_user, default=auth.user_id),   # adds logged in user by default,
                Field('type', requires=IS_IN_SET(object_types, error_message="Please select an object type", multiple=True), default = object_types[0]), #Can only currently be one type
                #Field('description', requires=IS_NOT_EMPTY(), widget=SQLFORM.widgets.text.widget), (Not in spec specifically, may wish to reinclude)
                Field('story', widget=SQLFORM.widgets.text.widget), #Optional as not all objects have a story
                Field('value', requires=[IS_EMPTY_OR(IS_DECIMAL_IN_RANGE(0,1e100)), #Optional as not all objects have a known value
                                        IS_EMPTY_OR(IS_EXPR('(len(str(value).split(".")) != 2) | ((len(str(value).split(".")) == 2) and (len(str(value).split(".")[1]) == 2))', error_message='Must be in valid currency format e.g. (£)1 or (£)1.00 (2 decimal places)'))])
                )


# Collections Table: stores details about the Collections
db.define_table('collections',
                Field('name', requires=IS_NOT_EMPTY()),
                Field('user_id', db.auth_user, default=auth.user_id),   # adds logged in user by default
                Field('privacy',
                      requires=IS_IN_SET(['Public', 'Private'], error_message="Please select privacy setting"), default = 'Public'))

# Objects in Collections Table: stores relation between objects and the collections they are in
db.define_table('objects_in_collections',
                Field('object_id', db.objects),
                Field('collection_id', db.collections))

# Have List: stores specific users have list
db.define_table('have_lists',
                Field('user_id', db.auth_user, default=auth.user_id,    # adds logged in user by default
                      writable=False, readable=False),
                Field('object_id', db.objects))

# Want List: stores specific users have list
db.define_table('want_lists',
                Field('user_id', db.auth_user, default=auth.user_id,    # adds logged in user by default
                      writable=False, readable=False),
                Field('object_id', db.objects))

import datetime
# Trades Table: stores details about Trades
db.define_table('trades',
                Field('UserProposing', db.auth_user), # User proposing trade (really couldn't think of better name)
                Field('UserProposed', db.auth_user), # User being proposed to
                Field('date', default=datetime.date.today()),   # adds current date by default
                Field('accepted', type='boolean', default=False),   # true if trade accepted
                Field('rejected', type='boolean', default=False))   # true if trade rejected

# Objects in Trade Table: stores relation between objects and the trades they are in
db.define_table('objects_in_trade',
                Field('object_id', db.objects),
                Field('trade_id', db.trades),
                Field('offered', type='boolean'),   # true if object is being offered by proposer
                Field('asked', type='boolean'))     # true if object is being asked by proposer
