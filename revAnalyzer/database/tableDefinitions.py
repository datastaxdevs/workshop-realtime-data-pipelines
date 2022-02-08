knownIdsPerTypeTableName = 'known_ids_per_type'
restaurantsByIDTableName = 'restaurants_by_id'
restaurantsByIDTimeTableName = 'restaurants_by_id_time'
reviewersByIDTableName = 'reviewers_by_id'

knownIdsPerTypeTable = {
    'name': knownIdsPerTypeTableName,
    'ifNotExists': True,
    'columnDefinitions': [
        {
            'name': 'id_type',
            'typeDefinition': 'text',
            'static': False,
        },
        {
            'name': 'ids',
            'typeDefinition': 'frozen<set<text>>',
            'static': False,
        },
    ],
    'primaryKey': {
        'partitionKey': [
            'id_type',
        ],
    },
}

restaurantsByIDTable = {
    'name': restaurantsByIDTableName,
    'ifNotExists': True,
    'columnDefinitions': [
        {
            'name': 'id',
            'typeDefinition': 'text',
            'static': False,
        },
        {
            'name': 'name',
            'typeDefinition': 'text',
            'static': False,
        },
        {
            'name': 'average',
            'typeDefinition': 'float',
            'static': False,
        },
        {
            'name': 'hits',
            'typeDefinition': 'int',
            'static': False,
        },
        {
            'name': 'num_outliers',
            'typeDefinition': 'int',
            'static': False,
        },
    ],
    'primaryKey': {
        'partitionKey': [
            'id',
        ],
    },
}

restaurantsByIDTimeTable = {
    'name': restaurantsByIDTimeTableName,
    'ifNotExists': True,
    'columnDefinitions': [
        {
            'name': 'id',
            'typeDefinition': 'text',
            'static': False,
        },
        {
            'name': 'time',
            'typeDefinition': 'timestamp',
            'static': False,
        },
        {
            'name': 'name',
            'typeDefinition': 'text',
            'static': False,
        },
        {
            'name': 'average',
            'typeDefinition': 'float',
            'static': False,
        },
    ],
    'primaryKey': {
        'partitionKey': [
            'id',
        ],
        'clusteringKey': [
            'time',
        ],
    },
    'tableOptions': {
        'defaultTimeToLive': 600,
        'clusteringExpression': [
            {
                'column': 'time',
                'order': 'ASC',
            },
        ],
    },
}

reviewersByIDTable = {
    'name': reviewersByIDTableName,
    'ifNotExists': True,
    'columnDefinitions': [
        {
            'name': 'id',
            'typeDefinition': 'text',
            'static': False,
        },
        {
            'name': 'trollings',
            'typeDefinition': 'int',
            'static': False,
        },
        {
            'name': 'hits',
            'typeDefinition': 'int',
            'static': False,
        },
        {
            'name': 'num_outliers',
            'typeDefinition': 'int',
            'static': False,
        },
        {
            'name': 'target_map',
            'typeDefinition': 'frozen<map<text,int>>',
            'static': False,
        },
    ],
    'primaryKey': {
        'partitionKey': [
            'id',
        ],
    },
}

tableDefs = [
    knownIdsPerTypeTable,
    restaurantsByIDTable,
    restaurantsByIDTimeTable,
    reviewersByIDTable,
]
