# -*- coding: utf-8 -GPK*-

{
    'name': 'PMS VVTI',
    'version': '1.0',
    "author": 'Yali Technologies',
    "website": 'http://www.yalitechnologies.com/',
    'category': 'Project Management System',
    'sequence': 15,
    'summary': 'Project Management System',
    'description': 'Project Management System',
    'depends': ['base', 'mail'],
    'data': [
        'data/project.xml',
        'menu/main_menu.xml',
        'security/project.xml',
        'security/ir.model.access.csv',
        'views/project/notes.xml',
        'views/project/procedure.xml',
        'views/project/task.xml',
        'views/project/ram.xml',
        'menu/project_menu.xml',

    ],
    'demo': [

    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
