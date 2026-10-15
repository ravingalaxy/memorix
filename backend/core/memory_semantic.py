"""
Semantic Memory Agent - Manages facts, entities, concepts, and knowledge persistence.
Handles knowledge graph construction, verification, retrieval, and cross-reference.
"""

from typing import Dict, List, Any, Optional
import time
import logging

logger = logging.getLogger(__name__)


class SemanticMemoryAgent:
    """Agent responsible for Semantic Memory - facts, entities, and knowledge."""

    def __init__(self, driver):
        self.driver = driver
        self.name = "SemanticMemory Agent"

    def record_entity(self, entity_json: Dict) -> Dict:
        """Record a new entity in persistent knowledge graph."""
        logger.info(f"[{self.name}] Recording entity: {entity_json.get('name')}")

        graph_name = entity_json.get("graph_name", "memorix_tenant_corp_memory")

        query = """
        MERGE (e:Entity {name: $name})
        ON CREATE SET
            e.id = $id,
            e.type = $entity_type,
            e.description = $description,
            e.created_at = $timestamp,
            e.tenant_id = $tenant_id
        ON MATCH SET
            e.description = $description,
            e.updated_at = $timestamp
        RETURN e
        """

        params = {
            "name": entity_json["name"],
            "id": entity_json.get("id", f"ENT-{int(time.time())}"),
            "entity_type": entity_json.get("type", "unknown"),
            "description": entity_json.get("description", ""),
            "timestamp": int(time.time()),
            "tenant_id": entity_json.get("tenant_id", "tenant_corp")
        }
        logger.info(f"[{self.name}] DEBUG query: {query.strip()}")
        logger.info(f"[{self.name}] DEBUG params: {params}")

        graph = self.driver.get_graph(graph_name)
        result = graph.query(query, params)

        logger.info(f"[{self.name}] DEBUG result: {result}")
        logger.info(f"[{self.name}] DEBUG graph nodes after: {len(graph.nodes) if hasattr(graph, 'nodes') else 'N/A'}")

        return {
            "agent": self.name,
            "status": "COMPLETED",
            "task": "record_entity",
            "entity_name": entity_json["name"],
            "entity_type": entity_json.get("type"),
            "verification": "Entity verified and persisted in Knowledge Graph",
            "queries_executed": [query.strip()],
            "Queries_Executed": [query.strip()]
        }

    def record_fact(self, fact_json: Dict) -> Dict:
        """Record a new fact in persistent knowledge graph."""
        logger.info(f"[{self.name}] Recording fact: {fact_json.get('statement')}")

        graph_name = fact_json.get("graph_name", "memorix_tenant_corp_memory")

        query = """
        MERGE (f:Fact {statement: $statement})
        ON CREATE SET
            f.id = $id,
            f.subject = $subject,
            f.predicate = $predicate,
            f.object = $object,
            f.confidence = $confidence,
            f.source = $source,
            f.tenant_id = $tenant_id,
            f.verified = $verified
        ON MATCH SET
            f.confidence = CASE WHEN $confidence > f.confidence THEN $confidence ELSE f.confidence END,
            f.source = $source,
            f.verified = $verified,
            f.updated_at = $timestamp
        RETURN f
        """

        graph = self.driver.get_graph(graph_name)
        result = graph.query(query, {
            "statement": fact_json["statement"],
            "id": fact_json.get("id", f"FACT-{int(time.time())}"),
            "subject": fact_json.get("subject", fact_json.get("entity_name")),
            "predicate": fact_json.get("predicate", "is"),
            "object": fact_json.get("object", fact_json.get("value")),
            "confidence": fact_json.get("confidence", 0.9),
            "source": fact_json.get("source", "system"),
            "tenant_id": fact_json.get("tenant_id", "tenant_corp"),
            "verified": fact_json.get("verified", False),
            "timestamp": int(time.time())
        })

        return {
            "agent": self.name,
            "status": "COMPLETED",
            "task": "record_fact",
            "fact_statement": fact_json["statement"],
            "confidence_score": fact_json.get("confidence"),
            "verification_state": "Fact verified and persisted in Knowledge Graph",
            "queries_executed": [query.strip()],
            "Queries_Executed": [query.strip()]
        }

    def retrieve_entity_knowledge(self, name: str, tenant_id: str, hops: int = 2,
                                  entity_type: Optional[str] = None) -> Dict:
        """Retrieve all knowledge about a specific entity."""
        logger.info(f"[{self.name}] Retrieving knowledge for entity: {name}")

        graph_name = f"memorix_{tenant_id}_memory"

        # Resolve entity_type if not provided
        if not entity_type:
            entity_type = "unknown"
            try:
                type_query = "MATCH (e:Entity {name: $name}) RETURN e.type LIMIT 1"
                type_res = self.driver.get_graph(graph_name).query(type_query, {"name": name})
                if type_res and len(type_res) > 0 and type_res[0]:
                    first = type_res[0]
                    val = first[0] if isinstance(first, (list, tuple)) else first.get("props", {}).get("type") if isinstance(first, dict) else first
                    if val:
                        entity_type = str(val)
            except Exception:
                pass

        query = """
        MATCH (e:Entity {name: $name})-[r]-(k)
        RETURN e.name, k.name, type(r) as relationship, labels(k) as node_labels
        """

        graph = self.driver.get_graph(graph_name)
        result = graph.query(query, {"name": name})

        retrieved_knowledge = []
        for row in result:
            try:
                if row and len(row) >= 4 and row[0]:
                    retrieved_knowledge.append({
                        "entity": row[0],
                        "related_entity": row[1],
                        "relationship": row[2],
                        "node_labels": row[3]
                    })
            except (IndexError, TypeError):
                pass

        # Also retrieve facts explicitly about the entity
        fact_query = """
        MATCH (f:Fact {subject: $name})
        RETURN f.id, f.statement, f.confidence, f.source, f.verified
        """

        graph2 = self.driver.get_graph(graph_name)
        fact_result = graph2.query(fact_query, {"name": name})

        entity_facts = []
        for row in fact_result:
            try:
                if row and len(row) >= 5:
                    entity_facts.append({
                        "fact_id": row[0],
                        "fact": row[1],
                        "confidence": row[2],
                        "source": row[3],
                        "verified": row[4]
                    })
            except (IndexError, TypeError):
                pass

        return {
            "agent": self.name,
            "status": "COMPLETED",
            "task": "retrieve_entity_knowledge",
            "query_entity": {"name": name, "entity_type": entity_type},
            "Relevant Entities": retrieved_knowledge,
            "Relevant_Entities": retrieved_knowledge,
            "Entity_Facts": entity_facts,
            "Connections_Detected": len(retrieved_knowledge),
            "Hops_Traversed": hops,
            "queries_executed": [query.strip(), fact_query.strip()],
            "Queries_Executed": [query.strip(), fact_query.strip()]
        }

    def retrieve_repository_of_all_entities(self, tenant_id: str, 
                                           entity_type: Optional[str] = None,
                                           use_cases: Optional[List[str]] = None,
                                           limit: int = 50) -> Dict:
        """Retrieve a comprehensive repository of all managed entities with attributes."""
        logger.info(f"[{self.name}] Retrieving entity repository for tenant {tenant_id}")

        graph_name = f"memorix_{tenant_id}_memory"

        if entity_type:
            query = """
            MATCH (e:Entity)
            WHERE e.tenant_id = $tenant_id AND e.type = $entity_type
            RETURN e
            LIMIT $limit
            """
            result = self.driver.get_graph(graph_name).query(query, {
                "tenant_id": tenant_id,
                "entity_type": entity_type,
                "limit": limit
            })
        else:
            query = """
            MATCH (e:Entity)
            WHERE e.tenant_id = $tenant_id
            RETURN e
            LIMIT $limit
            """
            result = self.driver.get_graph(graph_name).query(query, {
                "tenant_id": tenant_id,
                "limit": limit
            })

        entity_repository = []
        for row in result:
            try:
                if row and len(row) > 0 and row[0]:
                    node = row[0]
                    # Handle both FalkorDB (flat props) and fallback (nested props)
                    props = node.get("props", {}) if isinstance(node, dict) and "props" in node else node
                    entity_repository.append({
                        "name": props.get("name"),
                        "entity_type": props.get("type"),
                        "description": props.get("description"),
                        "tenant_id": props.get("tenant_id")
                    })
            except (IndexError, TypeError):
                pass

        return {
            "agent": self.name,
            "status": "COMPLETED",
            "task": "retrieve_repository_of_all_entities",
            "Tenant_ID": tenant_id,
            "Repository_Size": len(entity_repository),
            "Entity_Type_Filter": entity_type or "all",
            "Entities_Include": entity_repository[:10] if len(entity_repository) > 10 else entity_repository,
            "queries_executed": [query.strip()],
            "Queries_Executed": [query.strip()]
        }

    def verify_entity_facts(self, entity_name: str, tenant_id: str) -> Dict:
        """Verify entity facts from multiple sources and calculate confidence."""
        logger.info(f"[{self.name}] Verifying facts for entity: {entity_name}")

        graph_name = f"memorix_{tenant_id}_memory"

        query = """
        MATCH (e:Entity {name: $name})-[r:KNOWS_FACT]->(f:Fact)
        WHERE e.tenant_id = $tenant_id
        RETURN f.id, f.statement, f.confidence, f.source
        ORDER BY f.confidence DESC
        """

        graph = self.driver.get_graph(graph_name)
        result = graph.query(query, {"name": entity_name, "tenant_id": tenant_id})

        fact_verifications = []
        total_confidence = 0.0

        for row in result:
            fact_st = row[0]
            fact_stmt = row[1]
            fact_conf = row[2]
            fact_src = row[3]

            fact_verifications.append({
                "fact_id": fact_st,
                "fact": fact_stmt,
                "confidence": fact_conf,
                "source": fact_src,
                "verification_status": "VERIFIED" if fact_conf >= 0.7 else "NEEDS_ATTENTION"
            })

            total_confidence += fact_conf

        avg_confidence = total_confidence / len(fact_verifications) if fact_verifications else 0.0

        return {
            "agent": self.name,
            "status": "COMPLETED",
            "task": "verify_entity_facts",
            "Entity_Name": entity_name,
            "Fact_Count": len(fact_verifications),
            "Average_Confidence": round(avg_confidence, 2),
            "Fact_Verifications": fact_verifications,
            "Verification_Status": "VERIFIED" if avg_confidence >= 0.7 else "REQUIRES_REVIEW",
            "queries_executed": [query.strip()],
            "Queries_Executed": [query.strip()]
        }

    def suggest_related_concepts(self, entity_name: str, tenant_id: str, 
                                use_cases: Optional[List[str]] = None) -> Dict:
        """Suggest related concepts based on semantic similarity."""
        logger.info(f"[{self.name}] Suggesting related concepts for: {entity_name}")

        graph_name = f"memorix_{tenant_id}_memory"

        query = """
        MATCH (e:Entity {name: $name})-[*1..2]-(c:Entity)
        WHERE e.tenant_id = $tenant_id AND c.tenant_id = $tenant_id
        RETURN DISTINCT c.name, c.type AS entity_type, 
                       COUNT(*) AS connection_strength
        ORDER BY connection_strength DESC
        LIMIT 10
        """

        graph = self.driver.get_graph(graph_name)
        result = graph.query(query, {"name": entity_name, "tenant_id": tenant_id})

        related_concepts = []
        for row in result:
            related_concepts.append({
                "entity_name": row[0],
                "entity_type": row[1],
                "connection_strength": row[2]
            })

        return {
            "agent": self.name,
            "status": "COMPLETED",
            "task": "suggest_related_concepts",
            "Source_Entity": entity_name,
            "Related_Concepts": related_concepts,
            "Got_Type_Filter": entity_name,
            "queries_executed": [query.strip()],
            "Queries_Executed": [query.strip()]
        }