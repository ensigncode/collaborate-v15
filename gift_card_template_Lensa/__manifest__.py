# -*- coding: utf-8 -*-

{
    'name': 'Gift Card Template',
    'version': '15.0.1.0.10',
    'category': 'Gift',
    'sequence': 216,
    'description': """
       Gift Card
    """,
    'depends': ['pos_gift_card'],
    'data': [
        'views/template.xml',
        'views/pos_config.xml',
    ],
    'external_dependencies': {
        'python': ['translate']
    },
    'installable': True,
    'license': 'OEEL-1',
}
