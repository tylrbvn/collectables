# -*- coding: utf-8 -*-

#########################################################################
## MENU BAR
#########################################################################

response.title = "Collectables"
response.logo = A(B(response.title),
                  _class="navbar-brand",_href=URL('default', 'index'),
                  _id="web2py-logo")

response.meta.author = 'Group 4'
response.meta.description = "A collector's favourite tool."

if auth.is_logged_in():
    response.menu = [
        (T('Your collections'), False, URL('collection', 'index'), []),
        (T('Your objects'), False, URL('object', 'index'), []),
        (T('Your lists'), False, None, [
            (T('Have list'), False, URL('have', 'view', args=[auth.user.id])),
            (T('Want list'), False, URL('want', 'view', args=[auth.user.id]))
            ]),
        (T('Your trades'), False, URL('trades', 'index'), []),
        (T('New'), False, None, [
            (T('Object'), False, URL('object', 'new')),
            (T('Collection'), False, URL('collection', 'new')),
            (T('Trade'), False, URL('trades', 'new'))
            ]),
        (T('Browse'), False, None, [
            (T('Public collections'), False, URL('browse', 'collection')),
            (T('Have lists'), False, URL('browse', 'have')),
            (T('Want lists'), False, URL('browse', 'want'))
            ]),
        (T('Search'), False, URL('collection', 'search'), [])
    ]
else:
    response.menu = [
        (T('Browse'), False, None, [
            (T('Public collections'), False, URL('browse', 'collection')),
            (T('Have lists'), False, URL('browse', 'have')),
            (T('Want lists'), False, URL('browse', 'want'))
            ])
    ]
if "auth" in locals(): auth.wikimenu()

#########################################################################
## GROUP 4                                                            ##
#########################################################################
