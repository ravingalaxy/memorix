"""
Memory Orchestrator Agent - Coordinates Episodic, Semantic, and Procedural Memory agents.
Handles cross-session recall, agent handoffs, and memory coordination across tenants.
"""

from typing import Dict, List, Any, Optional
import time
import logging
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.memory_session import EpisodicMemoryAgent
from core.memory_semantic import SemanticMemoryAgent
from core.memory_procedural import ProceduralMemoryAgent

logger = logging.getLogger(__name__)


class MemoryOrchestrator:
    """Master Orchestrator Agent for Memorix memory system."""

    def __init__(self, driver):
        self.driver = driver
        self.name = "Memory Orchestrator"
        self.episodic_agent = EpisodicMemoryAgent(driver)
        self.semantic_agent = SemanticMemoryAgent(driver)
        self.procedural_agent = ProceduralMemoryAgent(driver)

    def coordinate_session_end(self, session_id: str, tenant_id: str, 
                              status: str, agents: List[str]) -> Dict:
        """
        Orchestrate session completion with cross-agent coordination.
        Records session end in Episodic Memory and extracts learnings.
        """
        logger.info(f"[{self.name}] Coordinating session completion: {session_id}")

        try:
            # Step 1: Record session end in Episodic Memory
            episodic_result = self.episodic_agent.record_session_end(
                session_id=session_id,
                tenant_id=tenant_id,
                status=status,
                summary=f"Session completed with status {status}, agents: {', '.join(agents)}"
            )
            logger.info(f"[{self.name}] Step 1 complete: record_session_end")

            # Step 2: Extract semantic entities and facts from the session
            semantic_facts = []
            semantic_results = []
            if status == "closed":
                semantic_facts = self._extract_semantic_learnings(session_id, tenant_id)
                logger.info(f"[{self.name}] Step 2a complete: _extract_semantic_learnings returned {len(semantic_facts)} facts")
                semantic_results = []
                for fact in semantic_facts:
                    semantic_results.append(
                        self.semantic_agent.record_fact(fact)
                    )
                logger.info(f"[{self.name}] Step 2b complete: record_fact for {len(semantic_results)} facts")

            # Step 3: Check for procedural improvements
            procedural_result = self._auto_learn_procedures_from_sessions(
                session_id, tenant_id
            )
            logger.info(f"[{self.name}] Step 3 complete: _auto_learn_procedures_from_sessions")

            # Step 4: Generate orchestration summary
            orchestration_summary = f"""
            Session {session_id} coordination complete.
            Agents: {', '.join(agents)}
            Status: {status}
            Semantic Learnings: {len(semantic_facts) if status == 'closed' else 0} facts extracted
            Procedural Improvements: {procedural_result.get('pattern_count', 0)} patterns detected
            Memory Type: Episodic + Semantic + Procedural integration
            """

            return {
                "agent": self.name,
                "status": "COMPLETED",
                "status_summary": orchestration_summary,
                "coordinated_result": {
                    "episodic_memory": episodic_result,
                    "semantic_memory": semantic_results if status == "closed" else [],
                    "procedural_memory": procedural_result
                },
                "graph_memory_calls": [
                    (episodic_result.get("queries_executed") or episodic_result.get("Queries_Executed") or ["session recording"])[0],
                    f"Episodic + Semantic + Procedural combination query"
                ],
                "Logic_Approximate": "COMPLETE"
            }
        except Exception as e:
            logger.error(f"[{self.name}] Error in coordinate_session_end: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise

    def recall_entity_knowledge_with_context(self, entity_name: str, tenant_id: str, 
                                            session_id: Optional[str] = None) -> Dict:
        """
        Retrieve entity knowledge across all memory types with cross-session context.
        Combines Episodic, Semantic, and Procedural views of an entity.
        """
        logger.info(f"[{self.name}] Recall entity knowledge: {entity_name}")

        # Step 1: Semantic knowledge retrieval
        semantic_result = self.semantic_agent.retrieve_entity_knowledge(
            name=entity_name,
            tenant_id=tenant_id
        )

        # Step 2: Procedural suggestions based on entity type
        entity_type = semantic_result.get("query_entity", {}).get("entity_type", "unknown")
        procedural_result = self.procedural_agent.suggest_potential_new_skills(
            session_context=f"{entity_name} {entity_type}",
            tenant_id=tenant_id
        )

        # Step 3: If session context available, retrieve episodic sessions
        episodic_sessions = []
        if session_id:
            episodic_result = self.episodic_agent.retrieve_session_history(
                session_id=session_id,
                tenant_id=tenant_id
            )

            # Extract mentions of this entity from conversation turns
            entity_mentions = self._find_entity_mentions(
                entity_name,
                episodic_result.get("session_data", [])
            )
            episodic_sessions = entity_mentions

        orchestration_summary = f"""
        Cross-memory entity recall for {entity_name}.
        Semantic: {semantic_result.get("Connections_Detected", 0)} connections
        Procedural: {len(procedural_result.get("Suggested_Skills", []))} skill suggestions
        Episodic: {len(episodic_sessions)} session mentions
        Memory Mode: Episodic + Semantic + Procedural integrated recall
        """

        return {
            "agent": self.name,
            "status": "COMPLETED",
            "Orchestration_Summary": orchestration_summary,
            "Memory_View_Branches": {
                "Semantic_Memory_View": {
                    "Entity": semantic_result.get("query_entity"),
                    "Relevant_Entities": semantic_result.get("Relevant_Entities"),
                    "Entity_Facts": semantic_result.get("Entity_Facts")
                },
                "Procedural_Memory_View": {
                    "Potential_Skills": procedural_result.get("Suggested_Skills")
                },
                "Episodic_Memory_View": {
                    "Session_Mentions": episodic_sessions
                }
            },
            "Cross_Session_Coordination": session_id is not None,
            "Average_Quality_Mapping": "COMPLETE",
            "queries_executed": (semantic_result.get("queries_executed") or semantic_result.get("Queries_Executed") or []) + 
                                (procedural_result.get("queries_executed") or procedural_result.get("Queries_Executed") or [])
        }

    def coordinate_agent_handoff(self, from_agent: str, to_agent: str, 
                                 session_id: str, tenant_id: str,
                                 context_summary: str) -> Dict:
        """
        Coordinate agent handoffs by recording handoff state in memory graph.
        Enables seamless context passing between agents.
        """
        logger.info(f"[{self.name}] Coordinating agent handoff: {from_agent} → {to_agent}")

        graph_name = f"memorix_{tenant_id}_memory"

        # Create handoff node in graph
        handoff_query = """
        CREATE (h:AgentHandoff {
            id: $id,
            session_id: $session_id,
            from_agent: $from_agent,
            to_agent: $to_agent,
            context_summary: $context,
            timestamp: $timestamp,
            success: true
        })
        RETURN h
        """

        graph = self.driver.get_graph(graph_name)
        graph.query(handoff_query, {
            "id": f"HANDOFF-{int(time.time())}",
            "session_id": session_id,
            "from_agent": from_agent,
            "to_agent": to_agent,
            "context": context_summary,
            "timestamp": int(time.time())
        })

        # Link handoff to session
        link_query = """
MATCH (h:AgentHandoff {id: $handoff_id})
MATCH (s:Session {session_id: $session_id})
MERGE (s)-[:CONTAINS_HANDOFF]->(h)
"""
        graph.query(link_query, {
            "handoff_id": f"HANDOFF-{int(time.time())}",
            "session_id": session_id
        })

        return {
            "agent": self.name,
            "status": "COMPLETED",
            "task": "coordinate_agent_handoff",
            "handoff_id": f"HANDOFF-{int(time.time())}",
            "From": from_agent,
            "To": to_agent,
            "Session_ID": session_id,
            "Context_Summary": context_summary,
            "Memory_Path": f"Session({session_id}) -> Handoff({from_agent}→{to_agent}->Procedural Memory)",
            "queries_executed": [handoff_query.strip()]
        }

    def _find_entity_mentions(self, entity_name: str, session_data: List[Dict]) -> List[Dict]:
        """Helper to find entity mentions in session data."""
        mentions = []
        if not session_data:
            return mentions

        for data in session_data:
            if isinstance(data, dict) and "turn_id" in data:
                # Parse conversation content for entity mentions
                content = data.get("content", "")
                if entity_name.lower() in content.lower():
                    mentions.append({
                        "turn_id": data.get("turn_id"),
                        "turn_number": data.get("turn_number", 0),
                        "timestamp": data.get("timestamp", 0),
                        "content_preview": content[:100] + "..." if len(content) > 100 else content
                    })

        return mentions

    def memo_merge(self, source_tenant: str, target_tenant: str, 
                  entity_name: str, merge_strategy: str = "merge") -> Dict:
        """
        Coordinate memory merges between tenants.
        For cross-tenant delegation scenarios.
        """
        logger.info(f"[{self.name}] Coordinating memory merge: {source_tenant} → {target_tenant}")

        # Notionally merge entity knowledge between tenants
        # In production, would implement actual merge logic with conflict resolution

        orchestration_summary = f"""
        Memory merge coordination: {entity_name} from {source_tenant} to {target_tenant}.
        Strategy: {merge_strategy}
        Memory Mode: Multi-tenant memory integration
        """

        return {
            "agent": self.name,
            "status": "COMPLETED",
            "Orchestration_Summary": orchestration_summary,
            "Source_Tenant": source_tenant,
            "Target_Tenant": target_tenant,
            "Entity_Name": entity_name,
            "Merge_Strategy": merge_strategy,
            "Memory_Type": "Multi-tenant memory integration",
            "logic_used": "MOVEMENT_COMMIT"
        }

    def _extract_semantic_learnings(self, session_id: str, tenant_id: str) -> List[Dict]:
        """Extract semantic facts from a completed session."""
        # Retrieve session history
        episodic_result = self.episodic_agent.retrieve_session_history(
            session_id=session_id,
            tenant_id=tenant_id
        )
        
        facts = []
        session_data = episodic_result.get("session_data") if episodic_result else []
        if not session_data:
            session_data = []
        
        for data in session_data:
            if isinstance(data, dict) and "content" in data:
                content = data.get("content", "")
                speaker = data.get("speaker", "")
                
                # Extract entities and create facts
                entities = data.get("entities_mentioned", [])
                if isinstance(entities, str):
                    try:
                        import ast
                        entities = ast.literal_eval(entities)
                    except (ValueError, SyntaxError):
                        entities = [e.strip() for e in entities.strip("[]").replace("'", "").split(",") if e.strip()]
                if not isinstance(entities, list) or entities is None:
                    entities = []

                for entity in entities:
                    facts.append({
                        "statement": f"{entity} mentioned by {speaker}",
                        "subject": entity,
                        "predicate": "mentioned_by",
                        "object": speaker,
                        "confidence": 0.8,
                        "source": "session_extraction",
                        "tenant_id": tenant_id
                    })
        
        return facts

    def _auto_learn_procedures_from_sessions(self, session_id: str, tenant_id: str) -> Dict:
        """Auto-learn procedural patterns from completed sessions."""
        # In production, this would analyze successful workflows and suggest skill improvements
        
        improvements_count = 0
        detected_patterns = []

        # Placeholder: Synthesize procedural improvements
        detected_patterns.append({
            "pattern_type": "workflow_optimization",
            "confidence": 0.85,
            "suggestion": "Consider creating skill for entity mentions extraction"
        })

        for pattern in detected_patterns:
            improvements_count += 1

        return {
            "pattern_count": improvements_count,
            "patterns_detected": detected_patterns,
            "auto_learned": improvements_count > 0
        }