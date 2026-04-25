import json
from sqlalchemy import text
from sqlalchemy.orm import Session

def execute_cypher(db: Session, query: str, params: dict = None):
    """
    Executes a Cypher query on the 'indus_production' graph via Apache AGE.
    """
    # Wrap parameters in agtype format if needed, but for simple queries we can just use string formatting
    # or let AGE handle it. AGE uses a specific syntax: SELECT * FROM cypher('graph_name', $$ query $$, [params])
    
    # Ensure search_path includes ag_catalog
    db.execute(text("SET search_path = ag_catalog, \"$user\", public;"))
    
    # Prepare the Cypher call
    # Note: Apache AGE uses $$ as a delimiter for the Cypher string.
    # If params are provided, we should ideally use the parameterized version of the cypher function.
    
    if params:
        # Convert params to a JSON string that AGE can interpret as agtype
        param_json = json.dumps(params)
        full_query = text(f"SELECT * FROM cypher('indus_production', $$ {query} $$, :params) as (result agtype);")
        return db.execute(full_query, {"params": param_json}).all()
    else:
        full_query = text(f"SELECT * FROM cypher('indus_production', $$ {query} $$) as (result agtype);")
        return db.execute(full_query).all()

def sync_machine_to_graph(db: Session, machine_id: str, name: str, properties: dict = None):
    """Creates or updates a Machine node in the graph."""
    props = {"id": str(machine_id), "name": name}
    if properties:
        props.update(properties)
    
    query = """
    MERGE (m:Machine {id: $id})
    SET m.name = $name
    """
    # Add extra properties to SET clause if needed
    execute_cypher(db, query, props)

def delete_machine_from_graph(db: Session, machine_id: str):
    """Removes a Machine node and its relationships from the graph."""
    query = "MATCH (m:Machine {id: $id}) DETACH DELETE m"
    execute_cypher(db, query, {"id": str(machine_id)})

def sync_connection_to_graph(db: Session, source_id: str, target_id: str, weight: float = 1.0):
    """Creates a directed relationship between two machines."""
    query = """
    MATCH (a:Machine {id: $source_id}), (b:Machine {id: $target_id})
    MERGE (a)-[r:CONNECTION]->(b)
    SET r.weight = $weight
    """
    execute_cypher(db, query, {
        "source_id": str(source_id),
        "target_id": str(target_id),
        "weight": weight
    })

def delete_connection_from_graph(db: Session, source_id: str, target_id: str):
    """Removes a connection relationship between two machines."""
    query = """
    MATCH (a:Machine {id: $source_id})-[r:CONNECTION]->(b:Machine {id: $target_id})
    DELETE r
    """
    execute_cypher(db, query, {
        "source_id": str(source_id),
        "target_id": str(target_id)
    })
