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
        (T('Your collections'), False, URL('collections', 'index'), []),
        (T('Search'), False, URL('collections', 'search'), []),
        (T('New'), False, None, [
            (T('Item'), False, URL('item', 'new')),
            (T('Collection'), False, URL('collection', 'new'))
            ])
    ]

if "auth" in locals(): auth.wikimenu()

#########################################################################
## GROUP 4                                                            ##
#########################################################################
