# -*- coding: utf-8 -*-

{
    'name': 'aki Real Estate',
    'version' : '0.1',
    'category': 'akiERP/Estate',
    'summary':'Phần mềm quản lý buôn bán BĐS',
    'description': "",
    'website':'www.akierp.com',
    'depends':[
        'base'
    ],
    'data':[
        'security/ir.model.access.csv',
        'views/estate_property_view.xml',
        'views/estate_property_offer_view.xml',
        'views/estate_property_type_view.xml',
        'views/estate_property_tag_view.xml',
        'views/res_user_view.xml',
        'menus/estate_menus.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False

}