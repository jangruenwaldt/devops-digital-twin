FROM neo4j:latest

ENV NEO4J_apoc_export_file_enabled=true \
    NEO4J_apoc_import_file_enabled=true \
    NEO4J_apoc_import_file_use__neo4j__config=true \
    NEO4J_PLUGINS='["apoc"]' \
    NEO4J_dbms_security_procedures_unrestricted=apoc.*

RUN apt-get -y update; apt-get -y install curl

RUN mkdir -p plugins \
    && curl -L -o plugins/apoc-5.9.0-extended.jar https://github.com/neo4j-contrib/neo4j-apoc-procedures/releases/download/5.9.0/apoc-5.9.0-extended.jar