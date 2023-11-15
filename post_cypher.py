import requests
import json
import base64


def QueryCypher(url, login, query):
    headers = {
        'content-type': 'application/json',
        'authorization': "Basic " + base64.b64encode(login.encode()).decode()}

    # cypher_query = {
    #     "statements": [
    #         {"statement": query,
    #          "resultDataContents": ["graph", "row"]
    #          }]
    # }

    # result = requests.post(url, data=json.dumps(cypher_query), headers=headers).json()
    result = requests.get(url + query).json()
    return result


if __name__ == '__main__':
    url = "http://910.mivc.top:20000/base_services/neo4j?query="
    login = "neo4j:123456"

    query = "MATCH (a:person) RETURN a, a.primaryName limit 3"
    # query = "MATCH p0=(a0:person)-[r0]-(b0:movie),p1=(a1:person)-[r1]-(b0:movie)" + \
    #     "WHERE b0.douban_movie_id<>'nan' AND type(r0)=~'act.*' AND a1.Chinese_name='陈凯歌' AND type(r1)=~'direct.*'" + \
    #         "RETURN DISTINCT p0,p1,id(a0),id(b0)"

    print(url + query)

    result = QueryCypher(url, login, query)
    print(result)

    # with open('./test.json', 'a') as f:
    #     json_dump = json.dumps(result, indent=4, ensure_ascii=False)
    #     f.write(json_dump)