from py2neo import Graph

from utils.config import Config


class Neo4j:
    @staticmethod
    def get_graph():
        return Graph(Config.get_db_address(), auth=(Config.get_db_user(), Config.get_db_pw()))

    @staticmethod
    def wipe_database():
        Neo4j.get_graph().delete_all()

    @staticmethod
    def remove_releases():
        cypher_query = 'MATCH (n:Deployment) DETACH DELETE n'
        Neo4j.get_graph().run(cypher_query)

    @staticmethod
    def remove_issues_and_labels():
        Neo4j.get_graph().run('MATCH (n:Issue) DETACH DELETE n')
        Neo4j.get_graph().run('MATCH (n:IssueLabel) DETACH DELETE n')

    @staticmethod
    def count_nodes():
        result = Neo4j.get_graph().run(f"MATCH (n) RETURN COUNT(n) AS count")
        return result.evaluate()
