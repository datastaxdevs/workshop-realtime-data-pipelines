""" dataStorage.py """

import os
import datetime
from dotenv import load_dotenv
from astrapy.client import create_astra_client


load_dotenv()


from .tableDefinitions import (
    tableDefs,
    knownIdsPerTypeTableName,
    restaurantsByIDTableName,
    restaurantsByIDTimeTableName,
    reviewersByIDTableName,
)

ASTRA_DB_ID = os.environ['ASTRA_DB_ID']
ASTRA_DB_REGION = os.environ['ASTRA_DB_REGION']
ASTRA_DB_APP_TOKEN = os.environ['ASTRA_DB_APP_TOKEN']
ASTRA_DB_KEYSPACE = os.environ['ASTRA_DB_KEYSPACE']

client = create_astra_client(
  astra_database_id=ASTRA_DB_ID,
  astra_database_region=ASTRA_DB_REGION,
  astra_application_token=ASTRA_DB_APP_TOKEN,
)


def initDB():
    # table creation (those are all 'if not exist' creations)
    for td in tableDefs:
        print('Checking "%s" ... ' % td['name'], end='')
        client.schemas.create_table(
            keyspace=ASTRA_DB_KEYSPACE,
            table_definition=td,
        )
        print('done.')


def updateIdSet(idType, ids):
    client.rest.add_row(
        keyspace=ASTRA_DB_KEYSPACE,
        table=knownIdsPerTypeTableName,
        row={
            'id_type': idType,
            'ids': list(ids),
        },
    )


def updateRestaurant(id, name, average, hits, num_outliers):
    client.rest.add_row(
        keyspace=ASTRA_DB_KEYSPACE,
        table=restaurantsByIDTableName,
        row={
            'id': id,
            'name': name,
            'average': average,
            'hits': hits,
            'num_outliers': num_outliers,
        },
    )


def insertRestaurantTime(id, name, average, time=None):
    _rowTime = datetime.datetime.now() if time is None else time
    a=1
    client.rest.add_row(
        keyspace=ASTRA_DB_KEYSPACE,
        table=restaurantsByIDTimeTableName,
        row={
            'id': id,
            'time': _rowTime.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            'name': name,
            'average': average,
        },
    )


def _stringifyMap(map):
    return '{%s}' % (
        ', '.join(
            "'%s': %s" % (k, str(v))
            for k, v in map.items()
        )
    )


def updateReviewer(id, hits, num_outliers, trollings, target_map):
    client.rest.add_row(
        keyspace=ASTRA_DB_KEYSPACE,
        table=reviewersByIDTableName,
        row={
            'id': id,
            'hits': hits,
            'num_outliers': num_outliers,
            'trollings': trollings,
            'target_map': _stringifyMap(target_map),
        },
    )



"""
curl -X 'GET' \
  'https://13484723-4994-4580-9542-4b3278d2ce2c-eu-central-1.apps.astra.datastax.com/api/rest/v1/keyspaces/trollsquad/tables/known_ids_per_type/rows/spiders' \
  -H 'accept: application/json' \
  -H 'X-Cassandra-Token: AstraCS:DYxzfpSzajUalRLcHRXRoIsw:d3195127b81ff687d7aaa37cc2e982dc13c90e03641d1d7894cb78a7b33ace8a' | python -mjson.tool
"""