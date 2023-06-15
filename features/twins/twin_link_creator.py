from utils.neo4j import Neo4j


class TwinLinkCreator:

    @staticmethod
    def create_links(twin_name):
        print(f'Adding links to twin')

        TwinLinkCreator._add_commits_links()

    @staticmethod
    def _add_commits_links():
        query = f'''
        MATCH (c:Commit)
        
        WITH c
        LIMIT 1
        
        // We only import data of one branch currently, so just add one node based on any commits branch
        MERGE (b:Branch {{name: c.branch}})
        
        WITH b
        MATCH (latest_commit:Commit)
        WHERE NOT(()-[:PARENT]->(latest_commit))
        
        MERGE (b)-[:LATEST_COMMIT]-(latest_commit)
'''
        result = Neo4j.run_query(query)
        print(result)


