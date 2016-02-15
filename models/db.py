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

## login after registration and redirect to home page
# auth.settings.login_after_registration = True
# auth.settings.login_next = URL('default', 'boxes.html')


# Objects Table: stores details on each object
db.define_table('objects',
                Field('name', requires=IS_NOT_EMPTY()),
                Field('type', requires=IS_NOT_EMPTY()),
                Field('description', requires=IS_NOT_EMPTY(), widget=SQLFORM.widgets.text.widget),
                Field('story', requires=IS_NOT_EMPTY(), widget=SQLFORM.widgets.text.widget),
                Field('value', requires=IS_NOT_EMPTY()))


# Collections Table: stores details about the Collections
db.define_table('collections',
                Field('name', requires=IS_NOT_EMPTY()),
                Field('user_id', db.auth_user, default=auth.user_id),   # adds logged in user by default
                Field('privacy_settings',
                      requires=IS_IN_SET(['Public', 'Private'], error_message="Please select setting")))

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