# Rivia ES Cloud

Wrapper para o cliente Elasticsearch Cloud com construtor de consultas e melhorias.

## Requisitos

- Python >= 3.8
- Elasticsearch >= 9.0.1

## Instalação

Para instalar as dependências, execute:

```sh
pip install rivia-es-cloud
```

## Configuração

Defina as seguintes variáveis de ambiente para configurar a conexão com o Elasticsearch Cloud:

- `ELASTIC_CLOUD_ID`
- `ELASTIC_USER`
- `ELASTIC_PASSWORD`

Para clusters do Elastic Cloud em formato serverless, defina as seguintes variáveis de ambiente


- `ELASTIC_CLOUD_MODE` = serverless
- `ELASTIC_HOST`
- `ELASTIC_API_KEY`

## Uso

### Funções Disponíveis

#### `get_client()`

Retorna a instância do cliente do Elasticsearch.

#### `must_match_all_fields(fields, parameters)`

Monta a cláusula bool "must" para o Elasticsearch usando os campos e os parâmetros fornecidos.

- `fields`: Lista de campos a serem mapeados. Exemplo: `[{'name': 'profile_text', 'value': 'profile_text', 'type': 'match'},{'name': 'hair_color', 'value': 'hair_color.keyword', 'type': 'term'},{'name': 'age_range', 'value': 'age', 'type': 'range'}]`
- `parameters`: Dicionário de parâmetros de busca. Exemplo: `{'profile_text': 'Travel','hair_color': 'Brown','age_range': {'gte': 28, 'lte': 35}}`

#### `query(index, match, sort=None, limit=100, offset=0, pretty=True)`

Realiza a consulta no Elasticsearch.

- `index`: Índice do Elasticsearch.
- `match`: Dicionário de parâmetros de busca. Conforme o retorno da função must_match_all_fields.
- `sort`: Parâmetros de ordenação (opcional).
- `limit`: Limite de documentos a serem retornados (opcional).
- `offset`: Offset para a consulta (opcional).
- `pretty`: Formatar o resultado (opcional).

#### `query_must(index, fields, parameters, sort=None, limit=100, offset=0, pretty=True)`

Realiza a consulta no Elasticsearch.

- `index`: Índice do Elasticsearch.
- `fields`: Lista de campos a serem mapeados. Exemplo: `[{'name': 'profile_text', 'value': 'profile_text', 'type': 'match'},{'name': 'hair_color', 'value': 'hair_color.keyword', 'type': 'term'},{'name': 'age_range', 'value': 'age', 'type': 'range'}]`
- `parameters`: Dicionário de parâmetros de busca. Exemplo: `{'profile_text': 'Travel','hair_color': 'Brown','age_range': {'gte': 28, 'lte': 35}}`
- `sort`: Parâmetros de ordenação (opcional).
- `limit`: Limite de documentos a serem retornados (opcional).
- `offset`: Offset para a consulta (opcional).
- `pretty`: Formatar o resultado (opcional).

#### `query_all(index, limit, sort=None, offset=0, pretty=True)`

Retorna todos os documentos de um índice do Elasticsearch.

- `index`: Índice do Elasticsearch.
- `limit`: Limite de documentos a serem retornados.
- `sort`: Parâmetros de ordenação (opcional).
- `offset`: Offset para a consulta (opcional).
- `pretty`: Formatar o resultado (opcional).

#### `upsert(index, id, data)`

Insere ou atualiza um documento no Elasticsearch.

- `index`: Índice do Elasticsearch.
- `id`: Identificador do documento.
- `data`: Dados do documento.

#### `get(index, id)`

Retorna um documento do Elasticsearch.

- `index`: Índice do Elasticsearch.
- `id`: Identificador do documento.

## Exemplo de Uso

```python
import os
import rivia-es-cloud as es

# Defina as variáveis de ambiente
os.environ['ELASTIC_CLOUD_ID'] = 'your_cloud_id'
os.environ['ELASTIC_USER'] = 'your_user'
os.environ['ELASTIC_PASSWORD'] = 'your_password'

# Realiza uma consulta
fields = [{'name': 'name', 'value': 'customer_name.keyword', 'type': 'match'}]
parameters = {'name': 'Vitor'}
match = es.must_match_all_fields(fields, parameters)
result = es.query('your_index', match)
print(result)

# Realiza uma consulta
fields = [{'name': 'name', 'value': 'customer_name.keyword', 'type': 'match'}]
parameters = {'name': 'Vitor'}
result = es.query_must('your_index', fields, parameters)
print(result)

# Retorna todos os primeiros 10 documentos
result = es.query_all('your_index', limit=10)
print(result)

# Insere um documento
data = {'name': 'Vitor', 'status': 'active'}
document = es.insert('your_index', data)
print(document)

# Insere ou atualiza um documento
data = {'name': 'Vitor', 'status': 'active'}
document = es.upsert('your_index', 'document_id', data)
print(document)

# Retorna um documento
document = es.get('your_index', 'document_id')
print(document)
```
