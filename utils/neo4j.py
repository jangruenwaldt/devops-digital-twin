import time

from py2neo import Graph

from utils.config import Config


class Neo4j:

    @staticmethod
    def run_query(query):
        return Neo4j.get_graph().run(query)

    @staticmethod
    def wait_for_connection(retries=8, delay=8):
        for i in range(retries):
            try:
                connection = Graph(Config.get_db_address(), auth=(Config.get_db_user(), Config.get_db_pw()))
                connection.run('match (n) return n limit 1')
                return connection
            except Exception:
                print(f"Neo4j is not available, retrying in {delay}s")
                time.sleep(delay)

        raise Exception("Could not connect to Neo4j")

    @staticmethod
    def get_graph():
        return Neo4j.wait_for_connection()

    @staticmethod
    def wipe_database():
        Neo4j.get_graph().run('''
        CALL apoc.periodic.iterate(
          "MATCH (n) RETURN n",
          "DETACH DELETE n",
          {batchSize: 1000, parallel: false}
        )
        ''')

    @staticmethod
    def count_nodes():
        result = Neo4j.get_graph().run(f"MATCH (n) RETURN COUNT(n) AS count")
        return result.evaluate()
