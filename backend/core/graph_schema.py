"""
Memory Graph Schema Definitions for Memorix (Track 2: Agent Memory & Coordination).
Defines Episodic, Semantic, Procedural memory nodes and their relationships.
"""

from typing import Dict, List, Any
from enum import Enum


class MemoryType(Enum):
    EPISODIC = "EPISODIC"      # Specific events, conversations, sessions
    SEMANTIC = "SEMANTIC"      # Facts, concepts, knowledge
    PROCEDURAL = "PROCEDURAL"  # Skills, workflows, procedures


class GraphSchema:
    """Schema definitions for the Memorix multi-agent memory system."""

    # ==================== NODE LABELS ====================
    
    # Memory Nodes
    EPISODIC_MEMORY = "EpisodicMemory"
    SEMANTIC_MEMORY = "SemanticMemory"
    PROCEDURAL_MEMORY = "ProceduralMemory"
    
    # Agent & Session Nodes
    AGENT = "Agent"
    SESSION = "Session"
    CONVERSATION_TURN = "ConversationTurn"
    TASK = "Task"
    
    # Knowledge Nodes
    ENTITY = "Entity"
    CONCEPT = "Concept"
    FACT = "Fact"
    SKILL = "Skill"
    WORKFLOW = "Workflow"
    TOOL = "Tool"
    
    # Coordination Nodes
    AGENT_HANDOFF = "AgentHandoff"
    SHARED_STATE = "SharedState"
    COORDINATION_EVENT = "CoordinationEvent"
    
    # Tenant/User Isolation
    TENANT = "Tenant"
    USER = "User"
    
    # ==================== RELATIONSHIP TYPES ====================
    
    # Memory Hierarchy
    HAS_EPISODIC = "HAS_EPISODIC"
    HAS_SEMANTIC = "HAS_SEMANTIC"
    HAS_PROCEDURAL = "HAS_PROCEDURAL"
    
    # Temporal Links (Episodic)
    OCCURRED_DURING = "OCCURRED_DURING"
    PRECEDES = "PRECEDES"
    FOLLOWS = "FOLLOWS"
    PART_OF_SESSION = "PART_OF_SESSION"
    
    # Semantic Links
    KNOWS_FACT = "KNOWS_FACT"
    RELATES_TO = "RELATES_TO"
    IS_A = "IS_A"
    HAS_PROPERTY = "HAS_PROPERTY"
    INSTANCE_OF = "INSTANCE_OF"
    SIMILAR_TO = "SIMILAR_TO"
    
    # Procedural Links
    HAS_STEP = "HAS_STEP"
    EXECUTES = "EXECUTES"
    LEARNED_FROM = "LEARNED_FROM"
    IMPROVES = "IMPROVES"
    REQUIRES_TOOL = "REQUIRES_TOOL"
    REQUIRES_SKILL = "REQUIRES_SKILL"
    
    # Agent Coordination
    HANDOFF_TO = "HANDOFF_TO"
    SHARES_STATE_WITH = "SHARES_STATE_WITH"
    COORDINATES_WITH = "COORDINATES_WITH"
    DELEGATES_TO = "DELEGATES_TO"
    RECEIVES_FROM = "RECEIVES_FROM"
    
    # Session & Conversation
    PARTICIPATES_IN = "PARTICIPATES_IN"
    INITIATED = "INITIATED"
    RESPONDED_TO = "RESPONDED_TO"
    CONTAINS_TURN = "CONTAINS_TURN"
    
    # Tenant/User Isolation
    BELONGS_TO_TENANT = "BELONGS_TO_TENANT"
    BELONGS_TO_USER = "BELONGS_TO_USER"
    OWNS_MEMORY = "OWNS_MEMORY"
    ACCESSES = "ACCESSES"
    
    # Task & Workflow
    ASSIGNED_TO = "ASSIGNED_TO"
    COMPLETED_BY = "COMPLETED_BY"
    DEPENDS_ON = "DEPENDS_ON"
    TRIGGERS = "TRIGGERS"

    @staticmethod
    def get_all_labels() -> List[str]:
        return [
            GraphSchema.EPISODIC_MEMORY,
            GraphSchema.SEMANTIC_MEMORY,
            GraphSchema.PROCEDURAL_MEMORY,
            GraphSchema.AGENT,
            GraphSchema.SESSION,
            GraphSchema.CONVERSATION_TURN,
            GraphSchema.TASK,
            GraphSchema.ENTITY,
            GraphSchema.CONCEPT,
            GraphSchema.FACT,
            GraphSchema.SKILL,
            GraphSchema.WORKFLOW,
            GraphSchema.TOOL,
            GraphSchema.AGENT_HANDOFF,
            GraphSchema.SHARED_STATE,
            GraphSchema.COORDINATION_EVENT,
            GraphSchema.TENANT,
            GraphSchema.USER,
        ]

    @staticmethod
    def get_all_relationships() -> List[str]:
        return [
            GraphSchema.HAS_EPISODIC,
            GraphSchema.HAS_SEMANTIC,
            GraphSchema.HAS_PROCEDURAL,
            GraphSchema.OCCURRED_DURING,
            GraphSchema.PRECEDES,
            GraphSchema.FOLLOWS,
            GraphSchema.PART_OF_SESSION,
            GraphSchema.KNOWS_FACT,
            GraphSchema.RELATES_TO,
            GraphSchema.IS_A,
            GraphSchema.HAS_PROPERTY,
            GraphSchema.INSTANCE_OF,
            GraphSchema.SIMILAR_TO,
            GraphSchema.HAS_STEP,
            GraphSchema.EXECUTES,
            GraphSchema.LEARNED_FROM,
            GraphSchema.IMPROVES,
            GraphSchema.REQUIRES_TOOL,
            GraphSchema.REQUIRES_SKILL,
            GraphSchema.HANDOFF_TO,
            GraphSchema.SHARES_STATE_WITH,
            GraphSchema.COORDINATES_WITH,
            GraphSchema.DELEGATES_TO,
            GraphSchema.RECEIVES_FROM,
            GraphSchema.PARTICIPATES_IN,
            GraphSchema.INITIATED,
            GraphSchema.RESPONDED_TO,
            GraphSchema.CONTAINS_TURN,
            GraphSchema.BELONGS_TO_TENANT,
            GraphSchema.BELONGS_TO_USER,
            GraphSchema.OWNS_MEMORY,
            GraphSchema.ACCESSES,
            GraphSchema.ASSIGNED_TO,
            GraphSchema.COMPLETED_BY,
            GraphSchema.DEPENDS_ON,
            GraphSchema.TRIGGERS,
        ]

    @staticmethod
    def get_node_properties() -> Dict[str, Dict[str, str]]:
        return {
            GraphSchema.EPISODIC_MEMORY: {
                "id": "string",
                "session_id": "string",
                "turn_id": "string",
                "tenant_id": "string",
                "user_id": "string",
                "agent_name": "string",
                "content": "string",
                "summary": "string",
                "embedding": "vector",
                "timestamp": "timestamp",
                "duration_ms": "integer",
                "tokens": "integer",
                "importance": "float",
                "memory_type": "string",
            },
            GraphSchema.SEMANTIC_MEMORY: {
                "id": "string",
                "tenant_id": "string",
                "entity_name": "string",
                "entity_type": "string",
                "fact": "string",
                "confidence": "float",
                "source": "string",
                "source_agent": "string",
                "verified": "boolean",
                "access_count": "integer",
                "last_accessed": "timestamp",
                "created_at": "timestamp",
                "updated_at": "timestamp",
            },
            GraphSchema.PROCEDURAL_MEMORY: {
                "id": "string",
                "tenant_id": "string",
                "skill_name": "string",
                "description": "string",
                "steps": "json",
                "tools_required": "json",
                "success_rate": "float",
                "execution_count": "integer",
                "avg_duration_ms": "integer",
                "last_executed": "timestamp",
                "created_by_agent": "string",
                "version": "integer",
            },
            GraphSchema.AGENT: {
                "id": "string",
                "name": "string",
                "type": "string",
                "capabilities": "json",
                "memory_access": "json",
                "status": "string",
                "tenant_id": "string",
                "created_at": "timestamp",
                "last_active": "timestamp",
            },
            GraphSchema.SESSION: {
                "id": "string",
                "tenant_id": "string",
                "user_id": "string",
                "started_at": "timestamp",
                "ended_at": "timestamp",
                "status": "string",
                "turn_count": "integer",
                "participating_agents": "json",
                "summary": "string",
            },
            GraphSchema.CONVERSATION_TURN: {
                "id": "string",
                "session_id": "string",
                "turn_number": "integer",
                "speaker": "string",
                "speaker_type": "string",
                "content": "string",
                "intent": "string",
                "entities_mentioned": "json",
                "timestamp": "timestamp",
                "response_to": "string",
            },
            GraphSchema.TASK: {
                "id": "string",
                "session_id": "string",
                "tenant_id": "string",
                "assigned_agent": "string",
                "description": "string",
                "status": "string",
                "priority": "integer",
                "input_data": "json",
                "output_data": "json",
                "created_at": "timestamp",
                "completed_at": "timestamp",
                "depends_on_task": "string",
            },
            GraphSchema.ENTITY: {
                "id": "string",
                "name": "string",
                "type": "string",
                "description": "string",
                "tenant_id": "string",
                "created_at": "timestamp",
            },
            GraphSchema.CONCEPT: {
                "id": "string",
                "name": "string",
                "definition": "string",
                "domain": "string",
                "tenant_id": "string",
                "created_at": "timestamp",
            },
            GraphSchema.FACT: {
                "id": "string",
                "statement": "string",
                "subject": "string",
                "predicate": "string",
                "object": "string",
                "confidence": "float",
                "source": "string",
                "tenant_id": "string",
                "verified": "boolean",
                "created_at": "timestamp",
            },
            GraphSchema.SKILL: {
                "id": "string",
                "name": "string",
                "description": "string",
                "procedure": "json",
                "category": "string",
                "difficulty": "integer",
                "tenant_id": "string",
                "learned_by": "string",
                "created_at": "timestamp",
            },
            GraphSchema.WORKFLOW: {
                "id": "string",
                "name": "string",
                "description": "string",
                "steps": "json",
                "agents_involved": "json",
                "success_criteria": "string",
                "tenant_id": "string",
                "version": "integer",
                "created_at": "timestamp",
            },
            GraphSchema.TOOL: {
                "id": "string",
                "name": "string",
                "description": "string",
                "function_signature": "json",
                "category": "string",
                "tenant_id": "string",
                "available_to": "json",
            },
            GraphSchema.AGENT_HANDOFF: {
                "id": "string",
                "session_id": "string",
                "from_agent": "string",
                "to_agent": "string",
                "context_summary": "string",
                "state_snapshot": "json",
                "reason": "string",
                "timestamp": "timestamp",
                "success": "boolean",
            },
            GraphSchema.SHARED_STATE: {
                "id": "string",
                "session_id": "string",
                "key": "string",
                "value": "json",
                "version": "integer",
                "updated_by": "string",
                "updated_at": "timestamp",
                "accessible_by": "json",
            },
            GraphSchema.COORDINATION_EVENT: {
                "id": "string",
                "session_id": "string",
                "event_type": "string",
                "participants": "json",
                "payload": "json",
                "timestamp": "timestamp",
            },
            GraphSchema.TENANT: {
                "id": "string",
                "name": "string",
                "description": "string",
                "created_at": "timestamp",
                "settings": "json",
            },
            GraphSchema.USER: {
                "id": "string",
                "email": "string",
                "name": "string",
                "tenant_id": "string",
                "role": "string",
                "preferences": "json",
                "created_at": "timestamp",
                "last_active": "timestamp",
            },
        }

    @staticmethod
    def get_memory_graph_name(tenant_id: str, memory_type: str) -> str:
        """Generate graph name for tenant-isolated memory storage."""
        return f"memorix_{tenant_id}_{memory_type.lower()}"

    @staticmethod
    def get_main_graph_name(tenant_id: str) -> str:
        """Generate main coordination graph name for tenant."""
        return f"memorix_{tenant_id}_main"