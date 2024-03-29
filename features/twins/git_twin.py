from utils.neo4j import Neo4j


class GitTwin:

    @staticmethod
    def construct_from_json(path):
        print(f'Constructing GitTwin from {path}')
        query = f'''
CALL apoc.periodic.iterate(
"
    CALL apoc.load.json('file://{path}') YIELD value RETURN value as commit_data
",
"
    MERGE (commit:Commit {{hash: commit_data.hash}})
    SET
    commit.message = commit_data.message,
    commit.date = commit_data.date,
    commit.branch = commit_data.branch,
    commit.url = commit_data.url
    
    FOREACH (parentHash IN commit_data.parents |
      MERGE (parent:Commit {{hash: parentHash}})
      MERGE (commit)-[:PARENT]->(parent)
    )
    
    WITH commit, commit_data
    MERGE (author:Author {{id: commit_data.author}})
    MERGE (author)-[r:COMMITTED]->(commit)
    SET
    r.date = commit_data.date

    RETURN 1
",
{{batchSize: 1000, parallel: false}})
YIELD batch
'''
        result = Neo4j.run_query(query)
        print(result)
