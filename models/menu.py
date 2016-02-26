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
        (T('Search'), False, URL('default', 'search'), []),
        (T('New'), False, None, [
            (T('Object'), False, URL('object', 'new')),
            (T('Collection'), False, URL('collection', 'new'))
            ])
    ]

if "auth" in locals(): auth.wikimenu()

#########################################################################
## GROUP 4                                                            ##
#########################################################################
