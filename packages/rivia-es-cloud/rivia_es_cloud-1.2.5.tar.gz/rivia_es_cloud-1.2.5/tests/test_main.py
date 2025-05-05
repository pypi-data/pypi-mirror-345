import os
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone
import uuid

# Mock environment variables and client initialization
with patch.dict(os.environ, {
    'ELASTIC_CLOUD_MODE': 'provisioned',
    'ELASTIC_CLOUD_ID': 'test-cloud-id:base64encodedcloudid',
    'ELASTIC_USER': 'test-user',
    'ELASTIC_PASSWORD': 'test-password'
}), patch('elasticsearch.Elasticsearch') as mock_es_class:
    mock_es = MagicMock()
    mock_es_class.return_value = mock_es
    mock_es.info.return_value = {'version': {'number': '8.0.0'}}
    from rivia_es_cloud.main import (
        _map_object_with_id,
        _map_source_with_id,
        _map_fields,
        must_match_all_fields,
        query,
        query_must,
        query_all,
        upsert,
        get,
        insert,
        update_by_script,
        update,
        get_client
    )

class TestMainFunctions(unittest.TestCase):
    def setUp(self):
        self.mock_es = MagicMock()
        self.patcher = patch('rivia_es_cloud.main.get_client', return_value=self.mock_es)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_map_object_with_id(self):
        response = {
            '_id': '123',
            '_source': {'name': 'test', 'value': 42}
        }
        result = _map_object_with_id(response)
        expected = {'name': 'test', 'value': 42, 'id': '123'}
        self.assertEqual(result, expected)

    def test_map_source_with_id(self):
        response = {
            'hits': {
                'hits': [
                    {'_id': '1', '_source': {'name': 'test1'}},
                    {'_id': '2', '_source': {'name': 'test2'}}
                ],
                'total': {'value': 2}
            },
            'aggregations': {'test': 'agg'}
        }
        result = _map_source_with_id(response)
        expected = {
            'items': [
                {'name': 'test1', 'id': '1'},
                {'name': 'test2', 'id': '2'}
            ],
            'total': 2,
            'aggs': {'test': 'agg'}
        }
        self.assertEqual(result, expected)

    def test_map_fields(self):
        fields = [
            {'name': 'name', 'value': 'customer_name.keyword', 'type': 'match'},
            {'name': 'status', 'type': 'wildcard'},
            {'name': 'age', 'type': 'term'}
        ]
        parameters = {
            'name': 'John',
            'status': 'active',
            'age': 30
        }
        result = _map_fields(fields, parameters)
        expected = [
            {'match': {'customer_name.keyword': 'John'}},
            {'wildcard': {'status': '*active*'}},
            {'term': {'age': 30}}
        ]
        self.assertEqual(result, expected)

    def test_must_match_all_fields(self):
        fields = [
            {'name': 'name', 'value': 'customer_name.keyword', 'type': 'match'},
            {'name': 'status', 'type': 'wildcard'}
        ]
        parameters = {
            'name': 'John',
            'status': 'active'
        }
        result = must_match_all_fields(fields, parameters)
        expected = {
            'bool': {
                'must': [
                    {'match': {'customer_name.keyword': 'John'}},
                    {'wildcard': {'status': '*active*'}}
                ]
            }
        }
        self.assertEqual(result, expected)

    def test_query(self):
        self.mock_es.search.return_value = {
            'hits': {
                'hits': [{'_id': '1', '_source': {'name': 'test'}}],
                'total': {'value': 1}
            }
        }
        result = query('test_index', {'match': {'name': 'test'}})
        self.mock_es.search.assert_called_once()
        self.assertEqual(result['total'], 1)
        self.assertEqual(result['items'][0]['name'], 'test')

    def test_query_must(self):
        fields = [{'name': 'name', 'type': 'match'}]
        parameters = {'name': 'test'}
        self.mock_es.search.return_value = {
            'hits': {
                'hits': [{'_id': '1', '_source': {'name': 'test'}}],
                'total': {'value': 1}
            }
        }
        result = query_must('test_index', fields, parameters)
        self.mock_es.search.assert_called_once()
        self.assertEqual(result['total'], 1)
        self.assertEqual(result['items'][0]['name'], 'test')

    def test_query_all(self):
        self.mock_es.search.return_value = {
            'hits': {
                'hits': [{'_id': '1', '_source': {'name': 'test'}}],
                'total': {'value': 1}
            }
        }
        result = query_all('test_index', 10)
        self.mock_es.search.assert_called_once()
        self.assertEqual(result['total'], 1)
        self.assertEqual(result['items'][0]['name'], 'test')

    def test_upsert(self):
        test_data = {'name': 'test'}
        test_id = '123'
        self.mock_es.index.return_value = {'_id': test_id}
        
        result = upsert('test_index', test_id, test_data)
        
        self.mock_es.index.assert_called_once()
        self.assertIn('id', result)
        self.assertIn('created_at', result)
        self.assertIn('updated_at', result)
        self.assertEqual(result['name'], 'test')

    def test_get(self):
        test_id = '123'
        self.mock_es.get.return_value = {
            '_id': test_id,
            '_source': {'name': 'test'}
        }
        
        result = get('test_index', test_id)
        
        self.mock_es.get.assert_called_once_with(index='test_index', id=test_id)
        self.assertEqual(result['name'], 'test')
        self.assertEqual(result['id'], test_id)

    def test_insert(self):
        test_data = {'name': 'test'}
        self.mock_es.index.return_value = {'_id': '123'}
        
        result = insert('test_index', test_data)
        
        self.mock_es.index.assert_called_once()
        self.assertIn('id', result)
        self.assertIn('created_at', result)
        self.assertIn('updated_at', result)
        self.assertEqual(result['name'], 'test')

    def test_update_by_script(self):
        test_id = '123'
        test_script = {'script': {'source': 'test'}}
        
        update_by_script('test_index', test_id, test_script)
        
        self.mock_es.update.assert_called_once_with(
            index='test_index',
            id=test_id,
            body=test_script
        )

    def test_update(self):
        test_id = '123'
        test_data = {'name': 'new_name', 'age': 30}
        
        update('test_index', test_id, test_data)
        
        self.mock_es.update.assert_called_once()
        call_args = self.mock_es.update.call_args[1]
        self.assertEqual(call_args['index'], 'test_index')
        self.assertEqual(call_args['id'], test_id)
        self.assertIn('script', call_args['body'])

if __name__ == '__main__':
    unittest.main() 
