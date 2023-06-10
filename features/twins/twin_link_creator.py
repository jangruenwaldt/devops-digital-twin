from utils.neo4j import Neo4j


class TwinLinkCreator:

    @staticmethod
    def create_links(twin_name):
        print(f'Adding links to twin')

        TwinLinkCreator._add_authors_links(twin_name)
        TwinLinkCreator._add_commits_links()
        TwinLinkCreator._add_deployment_links()
        TwinLinkCreator._add_automation_links()
        TwinLinkCreator.add_project_management_links()

    @staticmethod
    def _add_authors_links(twin_name):
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
        
        WITH b
        MERGE (all:Branches)
        
        WITH b, all
        MERGE (all)-[:IS_BRANCH]-(b)
        
        WITH all
        MATCH (r:Repository)
        MERGE (r)-[:HAS_BRANCHES]-(all)
'''
        result = Neo4j.run_query(query)
        print(result)

    @staticmethod
    def _add_automation_links():
        query = f'''
        MERGE (all:Automations)
        
        WITH all
        MATCH (r:Repository)
        
        MERGE (r)-[:HAS_AUTOMATIONS]-(all)
        
        WITH all
        MATCH (a:Automation)
        
        MERGE (all)-[:IS_AUTOMATION]->(a)
    '''
        result = Neo4j.run_query(query)
        print(result)

    @staticmethod
    def _add_deployment_links():
        query = f'''
        MERGE (all_dts:DeploymentTargets)
        
        WITH all_dts
        MATCH (r:Repository)
        
        MERGE (r)-[:HAS_DEPLOYMENT_TARGETS]-(all_dts)
        
        WITH all_dts
        // TODO: Let user name it?
        MERGE (dt:DeploymentTarget {{name: 'unknown'}})
        
        WITH all_dts, dt
        MERGE (all_dts)-[:IS_DEPLOYMENT_TARGET]-(dt)
        
        WITH dt
        
        MATCH (latest_deploy:Deployment)
        WHERE NOT(()-[:SUCCEEDS]->(latest_deploy))
        
        MERGE (dt)-[:LATEST_DEPLOY]-(latest_deploy)
'''
        result = Neo4j.run_query(query)
        print(result)

    @staticmethod
    def add_project_management_links():
        query = f'''
        MERGE (all:ProjectManagement)
        
        WITH all
        MATCH (r:Repository)
        
        MERGE (r)-[:HAS_PROJECT_MANAGEMENT]-(all)
'''
        result = Neo4j.run_query(query)
        print(result)

        query2 = f'''
        CALL apoc.periodic.iterate(
        "
        MATCH (i:Issue) RETURN i
        ",
        "
        MATCH (all:ProjectManagement)
        MERGE (all)-[:IS_ISSUE]->(i)
        ", 
        {{batchSize:1000, iterateList:true, parallel:false}})
'''
        result2 = Neo4j.run_query(query2)
        print(result2)


