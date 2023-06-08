from utils.neo4j import Neo4j


class TwinLinkCreator:

    @staticmethod
    def create_links(twin_name):
        print(f'Adding links to twin')

        query = f'''
        MERGE (r:Repository {{name: '{twin_name}'}})
        
        WITH r
        MERGE (a:Authors)
        
        WITH r, a
        MERGE (r)-[:HAS_AUTHORS]->(a)
        
        WITH a
        MATCH (s:Author)
        MERGE (a)-[:IS_AUTHOR]->(s)
'''
        result = Neo4j.run_query(query)
        print(result)
