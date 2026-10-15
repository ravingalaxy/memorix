"""
Episodic Memory Agent - Maintains persistent conversation history and session records.
Handles temporal information across agent sessions with timeline tracking and cross-session recall.
"""

from typing import Dict, List, Any, Optional
import time
import logging

logger = logging.getLogger(__name__)


class EpisodicMemoryAgent:
    """Agent responsible for Episodic Memory - recording sessions and conversation turns."""

    def __init__(self, driver):
        self.driver = driver
        self.name = "EpisodicMemory Agent"

    def record_session_start(self, session_id: str, tenant_id: str, user_id: str, agents: List[str]) -> Dict:
        """Record the beginning of a new session with participating agents."""
        logger.info(f"[{self.name}] Recording session start: {session_id} for tenant {tenant_id}")

        now = int(time.time())
        graph_name = f"memorix_{tenant_id}_memory"

        query = """
        MERGE (s:Session {session_id: $session_id})
        ON CREATE SET
            s.tenant_id = $tenant_id,
            s.user_id = $user_id,
            s.started_at = $timestamp,
            s.status = 'active',
            s.participating_agents = $agents,
            s.turn_count = 0
        SET s.last_active = $timestamp
        RETURN s
        """

        graph = self.driver.get_graph(graph_name)
        result = graph.query(query, {
            "session_id": session_id,
            "tenant_id": tenant_id,
            "user_id": user_id,
            "timestamp": now,
            "agents": agents
        })

        return {
            "agent": self.name,
            "status": "COMPLETED",
            "session_id": session_id,
            "graph_name": graph_name,
            "aggregate_features": False,
            "finding_accuracy": 1.0,
            "saved_session_info": "Session metadata initialized in FalkorDB",
            "queries_executed": [query.strip()]
        }

    def record_conversation_turn(self, turn_id: str, session_id: str, tenant_id: str, speaker: str, 
                                 content: str, timestamp: int, intent: Optional[str] = None,
                                 entities_mentioned: Optional[List[str]] = None, 
                                 response_to: Optional[str] = None) -> Dict:
        """Record a single conversation turn or turn sequence."""
        logger.info(f"[{self.name}] Recording turn: {turn_id} in session {session_id}")

        # Need to get current turn count
        turn_count = self.get_current_turn_count(tenant_id, session_id)

        # Get session start time for calculation
        session_info = self.get_session_info(tenant_id, session_id)

        graph_name = f"memorix_{tenant_id}_memory"

        query = """
        MATCH (s:Session {session_id: $session_id})
        MERGE (t:ConversationTurn {turn_id: $turn_id})
        ON CREATE SET
            t.turn_number = $turn_number,
            t.speaker = $speaker,
            t.content = $content,
            t.timestamp = $timestamp,
            t.intent = $intent,
            t.entities_mentioned = $entities,
            t.response_to = $response_to,
            t.extracted_embeddings = $embedding
        MERGE (s)-[:CONTAINS_TURN]->(t)
        SET
            s.turn_count = $new_turn_count,
            s.last_active = $timestamp,
            t.importance = $importance
        RETURN t
        """

        graph = self.driver.get_graph(graph_name)

        # Calculate importance based on turn number and content length
        importance = 0.5 + (len(content) * 0.001) + (0.1 if (intent or response_to) else 0)

        # Simplified embedding (in production would be from QA vector model)
        embedding = f"embedding-{turn_id}_{int(time.time())}"

        try:
            graph.query(query, {
                "turn_id": turn_id,
                "session_id": session_id,
                "turn_number": turn_count,
                "speaker": speaker,
                "content": content,
                "timestamp": timestamp,
                "intent": intent or "general",
                "entities": entities_mentioned or [],
                "response_to": response_to,
                "embedding": embedding,
                "new_turn_count": turn_count + 1,
                "importance": min(importance, 1.0)
            })

            return {
                "agent": self.name,
                "status": "COMPLETED",
                "task": "record_conversation_turn",
                "turn_id": turn_id,
                "session_id": session_id,
                "agent_handoff": "MemoryAgent → Orchestrator",
                "aggregate_features": False,
                "finding_accuracy": 1.0,
                "saved_memory": "Full conversation turn stored in Graph Memory",
                "memory_path": f"Session({session_id}) -> Turn({turn_id}) -> Episodic Memory",
                "queries_executed": [query.strip()]
            }
        except Exception as e:
            logger.error(f"[{self.name}] Error recording turn: {e}")
            return {
                "agent": self.name,
                "status": "FAILED",
                "task": "record_conversation_turn",
                "error": str(e)
            }

    def record_session_end(self, session_id: str, tenant_id: str, status: str = "closed", 
                           summary: Optional[str] = None) -> Dict:
        """Record the end of a session and generate summary."""
        logger.info(f"[{self.name}] Recording session end: {session_id}")

        now = int(time.time())
        graph_name = f"memorix_{tenant_id}_memory"

        query = """
        MATCH (s:Session {session_id: $session_id})
        SET
            s.status = $status,
            s.ended_at = $timestamp,
            s.summary = $summary
        RETURN s
        """

        graph = self.driver.get_graph(graph_name)
        graph.query(query, {
            "session_id": session_id,
            "status": status,
            "timestamp": now,
            "summary": summary or f"Session {session_id} completed with status {status}"
        })

        return {
            "agent": self.name,
            "status": "COMPLETED",
            "task": "record_session_end",
            "session_id": session_id,
            "session_status": status,
            "session_summary": summary,
            "queries_executed": [query.strip()]
        }

    def retrieve_session_history(self, session_id: str, tenant_id: str, hops: int = 2) -> Dict:
        """Retrieve the full session history with turn-by-turn timeline."""
        logger.info(f"[{self.name}] Retrieving history for session {session_id}")

        graph_name = f"memorix_{tenant_id}_memory"

        # Query session start and turns, following timeline
        query = """
        MATCH (s:Session {session_id: $session_id})
        OPTIONAL MATCH (s)-[:CONTAINS_TURN]->(t:ConversationTurn)
        RETURN s, t
        ORDER BY t.timestamp ASC
        """

        graph = self.driver.get_graph(graph_name)
        result = graph.query(query, {"session_id": session_id})

        session_info = None
        turns = []
        for row in result:
            # Handle empty results from fallback driver
            if not row or len(row) == 0:
                continue
            try:
                if session_info is None and row[0]:
                    node = row[0]
                    props = node.get('props', {}) if isinstance(node, dict) and 'props' in node else node if isinstance(node, dict) else {}
                    session_info = {
                        "session_id": props.get("session_id", session_id),
                        "tenant_id": props.get("tenant_id", tenant_id),
                        "user_id": props.get("user_id"),
                        "started_at": props.get("started_at"),
                        "ended_at": props.get("ended_at"),
                        "status": props.get("status"),
                        "turn_count": props.get("turn_count", 0),
                        "participating_agents": props.get("participating_agents", [])
                    }
            except (IndexError, TypeError):
                pass
            try:
                if len(row) > 1 and row[1]:
                    node = row[1]
                    props = node.get('props', {}) if isinstance(node, dict) and 'props' in node else node if isinstance(node, dict) else {}
                    turn_id = props.get("turn_id")
                    if turn_id and not any(t.get("turn_id") == turn_id for t in turns):
                        turns.append({
                            "turn_id": turn_id,
                            "turn_number": props.get("turn_number"),
                            "speaker": props.get("speaker"),
                            "content": props.get("content"),
                            "timestamp": props.get("timestamp"),
                            "intent": props.get("intent"),
                            "entities_mentioned": props.get("entities_mentioned", [])
                        })
            except (IndexError, TypeError):
                pass

        if session_info is None:
            session_info = self.get_session_info(tenant_id, session_id)

        return {
            "agent": self.name,
            "status": "COMPLETED",
            "task": "retrieve_session_history",
            "session_id": session_id,
            "session": session_info,
            "turns": turns,
            "session_data": turns,
            "turn_count": len(turns),
            "queries_executed": [query.strip()]
        }

    def recall_across_sessions(self, tenant_id: str, user_id: Optional[str] = None, 
                              agents: Optional[List[str]] = None, 
                              hops: int = 3, time_window_hours: Optional[int] = None) -> Dict:
        """Recall information across multiple sessions based on user, agents, and time window."""
        logger.info(f"[{self.name}] Cross-session recall for tenant {tenant_id}")

        graph_name = f"memorix_{tenant_id}_memory"

        query = """
        MATCH (s:Session)
        WHERE s.tenant_id = $tenant_id
        OPTIONAL MATCH (s)-[:CONTAINS_TURN]->(t:ConversationTurn)
        WHERE
            ($user_id IS NULL OR t.speaker = $user_id OR s.user_id = $user_id)
            AND ($agents IS NULL OR any(a IN s.participating_agents WHERE a IN $agents))
            AND ($time_window IS NULL OR t.timestamp >= timestamp() - $time_window)
        RETURN DISTINCT s.session_id, s.started_at, s.summary, 
                       collect(DISTINCT t.content) AS all_contents
        ORDER BY s.started_at DESC
        """

        time_window = time_window_hours * 3600 if time_window_hours else None

        graph = self.driver.get_graph(graph_name)
        result = graph.query(query, {
            "tenant_id": tenant_id,
            "user_id": user_id,
            "agents": agents or [],
            "time_window": time_window
        })

        recalled_sessions = []
        for row in result:
            if row and len(row) >= 4:
                recalled_sessions.append({
                    "session_id": row[0],
                    "started_at": row[1],
                    "summary": row[2],
                    "turns": row[3]
                })

        return {
            "agent": self.name,
            "status": "COMPLETED",
            "task": "recall_across_sessions",
            "tenant_id": tenant_id,
            "Recall_depth_hops": hops,
            "Recall_results": recalled_sessions,
            "Recall_session_count": len(recalled_sessions),
            "Recall_time_window_hrs": time_window_hours,
            "queries_executed": [query.strip()]
        }

    def get_current_turn_count(self, tenant_id: str, session_id: str) -> int:
        """Get the current turn count for a session."""
        graph_name = f"memorix_{tenant_id}_memory"
        query = """
        MATCH (s:Session {session_id: $session_id})
        RETURN s.turn_count
        """
        graph = self.driver.get_graph(graph_name)
        result = graph.query(query, {"session_id": session_id})
        
        try:
            if result and len(result) > 0:
                first_row = result[0]
                if isinstance(first_row, (list, tuple)) and len(first_row) > 0:
                    count = first_row[0]
                    return int(count) if count else 0
                elif not isinstance(first_row, (list, tuple)):
                    return int(first_row) if first_row else 0
        except (IndexError, TypeError, ValueError):
            pass
        return 0

    def get_session_info(self, tenant_id: str, session_id: str) -> Dict:
        """Get session metadata."""
        graph_name = f"memorix_{tenant_id}_memory"
        query = """
        MATCH (s:Session {session_id: $session_id})
        RETURN s
        """
        graph = self.driver.get_graph(graph_name)
        result = graph.query(query, {"session_id": session_id})
        
        try:
            if result and len(result) > 0:
                first_row = result[0]
                if isinstance(first_row, (list, tuple)) and len(first_row) > 0:
                    node = first_row[0]
                    if isinstance(node, dict):
                        props = node.get('props', {})
                        return {
                            "session_id": props.get("session_id"),
                            "started_at": props.get("started_at"),
                            "user_id": props.get("user_id"),
                        }
        except (IndexError, TypeError):
            pass
        return {}