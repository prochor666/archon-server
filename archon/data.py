from bson.objectid import ObjectId
from archon import app
import pymongo.collection

def ex(finder: dict = {}) -> list:
    try:
        _ = proxy(finder)
        return list(
            _['data_source'].find(_['filter'], _['exclude']).sort(_['sort'][0], _['sort'][1]).collation({ 'locale': "en", 'caseLevel': True })
        )

    except Exception as e:
        return f"Database server error {str(e)}"


def one(finder: dict = {}) -> dict:
    try:
        _ = proxy(finder)
        return _['data_source'].find_one(_['filter'], _['exclude'])

    except Exception as e:
        return f"Database server error {str(e)}"


def collect_one(document: dict) -> dict:
    if '_id' in document:
        document['_id'] = str(document['_id'])
        document['id'] = document['_id']
    if 'creator' in document:
        document['creator'] = str(document['creator'])
    if 'updater' in document:
        document['updater'] = str(document['updater'])
    if 'owner' in document:
        document['owner'] = str(document['owner'])
    if 'user_id' in document:
        document['user_id'] = str(document['user_id'])

    return document


def collect(find_result: list) -> list:
    result = []
    for document in find_result:
        result.append(collect_one(document))
    return result


def proxy(finder: dict) -> dict:
    _collection = finder.get('collection')
    data_source = []
    _filter = finder.get('filter', None)
    _exclude = finder.get('exclude', None)
    _sort = finder.get('sort', ['Id', 1])
    
    if type(_collection) is str:
        data_source = app.db[_collection]

        if type(data_source) is pymongo.collection.Collection:
            _from_str = {
                'asc': 1,
                'desc': -1
            }

            if _sort is None or type(_sort) is not list:
                _sort = ['Id', 1]

            if type(_filter) is dict and 'id' in _filter:
                _filter['_id'] = ObjectId(_filter.pop('id'))

            if type(_sort) is list and len(_sort) == 2:
                if type(_sort[1]) is str and _sort[1].lower() in _from_str.keys():
                    _sort[1] = _from_str[_sort[1]]

    return {
        'data_source': data_source,
        'filter': _filter,
        'exclude': _exclude,
        'sort': _sort,
    }
