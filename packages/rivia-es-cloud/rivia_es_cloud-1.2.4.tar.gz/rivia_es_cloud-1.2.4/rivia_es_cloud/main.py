import os
import uuid
from datetime import datetime, timezone
from elasticsearch import Elasticsearch

mode = os.environ.get('ELASTIC_CLOUD_MODE', 'provisioned')

if mode == 'serverless':
    client = Elasticsearch(
        os.environ.get('ELASTIC_HOST'),
        api_key=os.environ.get('ELASTIC_API_KEY')
    )
else:
    client = Elasticsearch(
        cloud_id=os.environ.get('ELASTIC_CLOUD_ID'),
        basic_auth=(os.environ.get("ELASTIC_USER"), os.environ.get("ELASTIC_PASSWORD"))
    )

print("Connected to the elastic cloud service", client.info())

def _map_object_with_id(response):
    return {**response['_source'], 'id': response['_id']}

def _map_source_with_id(response):
    items = [ _map_object_with_id(hit) for hit in response['hits']['hits'] ]
    return {'items': items, 'total': response['hits']['total']['value'], 'aggs': response.get('aggregations', {})}

def _map_fields(fields, parameters):
    """
    Converte os campos e os parâmetros em uma lista de cláusulas de consulta para o Elasticsearch.
    
    :param fields: Lista de campos a serem mapeados. 
        Exemplo: [{'name': 'name', 'value': 'customer_name.keyword', 'type': 'match'}]
    :param parameters: Dicionário de parâmetros de busca. 
        Exemplo: {'name': 'Vitor', 'status': 'active'}
    :return: Lista de cláusulas de consulta (match, wildcard ou term) para o Elasticsearch.
    """
    return [
        {
            field.get('type', 'match'):
                {field.get('value', field['name']): 
                    f"*{value}*" if field.get('type') == 'wildcard' else value}
        }
        for field in fields
            if (value := parameters.get(field['name']))
    ]

def get_client():
    """
    Retorna a instância do client do Elasticsearch.
    """
    return client

def must_match_all_fields(fields, parameters):
    """
    Monta a cláusula bool "must" para o Elasticsearch usando os campos e os parâmetros fornecidos.
    
    :param fields: Lista de campos a serem mapeados. 
                Exemplo: [{'name': 'name', 'value': 'customer_name.keyword', 'type': 'match'}]
    :param parameters: Dicionário de parâmetros de busca.
    :return: Cláusula bool "must" com a lista de condições de match, wildcard e term.
    """
    must_clauses = _map_fields(fields, parameters)
    return {'bool': {'must': must_clauses}} if must_clauses else {'match_all': {}}

def query(index, match, sort=None, limit=100, offset=0, pretty=True):
    """
    Realiza a consulta no Elasticsearch.
    
    :param index: Índice do Elasticsearch.
    :param match: Dicionário de parâmetros de busca. Conforme o retorno da função must_match_all_fields.
    :return: Resultado da consulta.
    """
    es = get_client()
    items = es.search(index=index, query=match, size=limit, from_=offset, sort=sort)
    return _map_source_with_id(items) if pretty else items

def query_must(index, fields, parameters, sort=None, limit=100, offset=0, pretty=True):
    """
    Realiza a consulta no Elasticsearch.
    
    :param index: Índice do Elasticsearch.
    :param fields: Lista de campos a serem mapeados. 
                Exemplo: [{'name': 'name', 'value': 'customer_name.keyword', 'type': 'match'}]
    :param parameters: Dicionário de parâmetros de busca.
    :return: Resultado da consulta.
    """
    match = must_match_all_fields(fields, parameters)
    return query(index, match, sort, limit, offset, pretty)

def query_all(index, limit, sort=None, offset=0, pretty=True):
    """
    Retorna todos os documentos de um índice do Elasticsearch.
    
    :param index: Índice do Elasticsearch.
    :param limit: Limite de documentos a serem retornados.
    :return: Resultado da consulta.
    """
    return query(index, {'match_all': {}}, sort, limit, offset, pretty)

def upsert(index, id, data):
    """
    Insere ou atualiza um documento no Elasticsearch.
    
    :param index: Índice do Elasticsearch.
    :param id: Identificador do documento.
    :param data: Dados do documento.
    """
    now = datetime.now(timezone.utc).isoformat()
    data['id'] = id
    data['updated_at'] = now

    if 'created_at' not in data:
        data['created_at'] = now
    
    es = get_client()
    es.index(index=index, id=id, body=data)
    return data

def get(index, id):
    """
    Retorna um documento do Elasticsearch.
    
    :param index: Índice do Elasticsearch.
    :param id: Identificador do documento.
    :return: Documento encontrado.
    """
    es = get_client()
    found = es.get(index=index, id=id)
    return _map_object_with_id(found)

def insert(index, data):
    """
    Insere um documento no Elasticsearch.
    
    :param index: Índice do Elasticsearch.
    :param data: Dados do documento.
    """
    id = str(uuid.uuid4())
    return upsert(index, id, data)

def update_by_script(index, id, script):
    """
    Atualiza um documento no Elasticsearch.
    
    :param index: Índice do Elasticsearch.
    :param id: Identificador do documento.
    :param script: Script de atualização.
    """
    es = get_client()
    es.update(index=index, id=id, body=script)

def update(index, id, data):
    """
    Atualiza um documento no Elasticsearch.
    
    :param index: Índice do Elasticsearch.
    :param id: Identificador do documento.
    :param data: Dados do documento que serão atualizados.
    """
    script = {
        'script': {
            'source': '; '.join([f"ctx._source.{key} = params.{key}" for key in data.keys()]),
            'lang': 'painless',
            'params': data
        }
    }
    update_by_script(index, id, script)