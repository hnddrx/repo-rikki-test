{
    'name': 'Cost Center',
    'version': '1.0',
    'summary': 'This module is for managing Cost Center',
    'description': 'A module to list and manage Cost Center',
    'category': 'Human Resource',
    'author': 'Wren',
    'depends': [
        'base', 
        'web', 
        'hr',
        'base_setup',
        'resource',
        'web',
        'mail', 
        'advanced_employee_manager',
        'custom_approval_flow',
        ],
    'data': [
        'security/ir.model.access.csv',
        'views/cost_center.xml',
        'data/cost_center.xml',
        
    ], 
    """ "assets":{
        "web.assets_backend":[
            'certificate_of_employment/static/src/js/counter/owl_component.js'
        ] 
    },  """
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3'
}