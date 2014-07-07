#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Use POIs from different schemes and unify them in only one information services scheme.
"""


import argparse
import copy
import logging
import os
import sys

import pymongo


app_name = os.path.splitext(os.path.basename(__file__))[0]
ignored_schemas_name = []
log = logging.getLogger(app_name)


def add_field_to_poi(poi, field_id, value, metadata):
    poi_copy = copy.deepcopy(poi)
    if field_id not in poi_copy:
        poi_copy[field_id] = [value]
        poi_copy['metadata'][field_id] = [metadata]
    else:
        poi_copy[field_id].append(value)
        poi_copy['metadata'][field_id].append(metadata)
    poi_copy['metadata']['positions'].append(field_id)
    return poi_copy


def add_field_to_schema(schema, field_id, metadata, old_schema):
    schema_copy = copy.deepcopy(schema)
    if metadata['label'] in [field['label'] for field in schema['fields']]:
        return schema
    for field in old_schema['fields']:
        if field['id'] == field_id and field['label'] == metadata.get('label').split(' - ')[1]:
            field_copy = copy.deepcopy(field)
            field_copy['label'] = metadata['label']
            schema_copy['fields'].append(field_copy)
            break
    return schema_copy


def field_metadata(poi, field_id, label_dict_pairs, default = None, schema = None):
    poi_label_index = label_index(poi, field_id, label_dict_pairs)
    if poi_label_index is None:
        return None
    return dict([
        (
            key,
            u'{} - {}'.format(schema['title'], value) if key == 'label' else value,
            )
        for key, value in poi['metadata'][field_id][poi_label_index].iteritems()
        ])


def field_value(poi, field_id, label_dict_pairs, default = None):
    if field_id == 'territories':
        poi_label_index = label_index(poi, field_id, label_dict_pairs)
        return default if poi_label_index is None else map(
            lambda item: (item['kind'], item['code']),
            filter(
                None,
                poi[field_id][poi_label_index],
                ),
            )
    poi_label_index = label_index(poi, field_id, label_dict_pairs)
    return default if poi_label_index is None else poi[field_id][poi_label_index]


def get_schemas_information(db):
    merging_fields_by_schema_name = {}
    for schema_name in db.schemas.distinct('name'):
        if schema_name in ignored_schemas_name:
            continue
        for field in db.schemas.find_one({'name': schema_name})['fields']:
            merging_fields_by_schema_name.setdefault(schema_name, []).append((field['id'], [('label', field['label'])]))

    return merging_fields_by_schema_name


def label_index(poi, field_id, label_dict_pairs):
    for _label_index, _label_dict in enumerate(poi['metadata'].get(field_id, [])):
        if all(map(lambda item: _label_dict[item[0]] == item[1], label_dict_pairs)):
            return _label_index
    return None


def main():
    parser = argparse.ArgumentParser(description = __doc__)
    parser.add_argument('csv_filename', nargs = '?', help = 'CSV File name.')
    parser.add_argument('-d', '--database_name', default = 'souk_passim', help = 'Name of database used')
    parser.add_argument('-v', '--verbose', action = 'store_true', help = 'Increase output verbosity')

    args = parser.parse_args()
    logging.basicConfig(level = logging.DEBUG if args.verbose else logging.WARNING, stream = sys.stdout)
    db = pymongo.Connection()[args.database_name]

    information_services_by_id = dict([
        (item['_id'], item)
        for item in db.pois.find({'metadata.deleted': {'$exists': False}, 'metadata.schema-name': 'ServiceInfo'})
        ])
    information_service_schema = db.schemas.find_one({'name': 'ServiceInfo'})
    schema_by_schema_name = dict([(schema['name'], schema) for schema in db.schemas.find()])
    selected_pois_id = set()  # ID of POIs which will be removed after processed

    merging_fields_by_schema_name = get_schemas_information(db)
    poi_count = db.pois.find({
            'metadata.deleted': {'$exists': False},
            'metadata.schema-name': {'$ne': 'ServiceInfo'},
            }).count()
    for index, poi in enumerate(db.pois.find({
            'metadata.deleted': {'$exists': False},
            'metadata.schema-name': {'$ne': 'ServiceInfo'},
            })):
        print u'Poi {} : {} / {} being processed'.format(poi['_id'], index + 1, poi_count)
        information_service_id = field_value(poi, 'link', [('label', u'Service d\'information')])
        if information_service_id is None:
            continue

        schema_name = poi['metadata']['schema-name']
        guichet_information_number = len(
            filter(
                lambda i: i['label'] == u"Guichet d'information - Intitul\xe9",
                information_services_by_id[information_service_id]['metadata']['name'],
                )
            )
        if schema_name == 'GuichetInformation' and guichet_information_number > 0:
            continue
        for field_id, metadata in merging_fields_by_schema_name.get(schema_name, []):
            field_metadata_dict = field_metadata(
                poi,
                field_id,
                metadata,
                schema = schema_by_schema_name[schema_name],
                )
            value = field_value(poi, field_id, metadata)
            if field_metadata_dict is None or value is None or \
                    label_index(poi, field_id, field_metadata_dict.items()) is not None:
                continue
            information_service_schema = add_field_to_schema(
                information_service_schema,
                field_id,
                field_metadata_dict,
                schema_by_schema_name[schema_name]
                )
            information_services_by_id[information_service_id] = add_field_to_poi(
                information_services_by_id[information_service_id],
                field_id,
                value,
                field_metadata_dict,
                )
            if schema_name in information_service_schema['children']:
                information_service_schema['children'].remove(schema_name)
            selected_pois_id.add(poi['_id'])

    db.schemas.save(information_service_schema)
    for poi in information_services_by_id.itervalues():
        db.pois.save(poi)
    for poi_id in selected_pois_id:
        db.pois.remove({'_id': poi_id})

    return 0


if __name__ == "__main__":
    sys.exit(main())
