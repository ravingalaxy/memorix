"""
Seed Data Generator for Memorix scenarios.
Provides rich memory scenarios demonstrating Episodic, Semantic, and Procedural memory.
"""

from typing import Dict, List, Any
import time


class SeedData:
    """Provides seed scenarios for testing and judging Memorix Track 2."""

    @staticmethod
    def get_multi_session_scenario() -> Dict[str, Any]:
        """Scenario 1: Multi-session Agent Coordination with Episodic Memory"""
        now = int(time.time())
        return {
            "scenario_id": "MULTI-SESSION-01",
            "title": "Customer Support Agent Coordination (Multi-Session)",
            "description": "Multiple intelligent agents collaborating across three separate sessions on building a memory system for personalized customer service.",
            "session_1": {
                "session_id": "SES-001",
                "agents": ["CustomerBot", "KnowledgeBase", "MemoryAgent"],
                "turns": [
                    {
                        "id": "T1-001",
                        "tenant_id": "tenant_corp",
                        "user_id": "user_alice",
                        "agent_name": "CustomerBot",
                        "content": "Hello, I need help with my order #WS-12345. Can you check if it's been delivered?",
                        "timestamp": now - 86400,
                        "intent": "inquiry",
                        "summary": "Customer inquiries about order delivery status",
                    },
                    {
                        "id": "T1-002",
                        "tenant_id": "tenant_corp",
                        "user_id": "user_alice",
                        "agent_name": "KnowledgeBase",
                        "content": "Checking inventory and order tracking system... Order #WS-12345 status: In Transit. Expected delivery: October 17, 2026.",
                        "timestamp": now - 86300,
                        "intent": "information retrieval",
                        "summary": "Knowledge retrieved from external systems",
                    },
                    {
                        "id": "T1-003",
                        "tenant_id": "tenant_corp",
                        "user_id": "user_alice",
                        "agent_name": "MemoryAgent",
                        "content": "Storing customer profile: Alice Robertson. Last interaction: Sep 28. Known preferences: Prefers email communication. Order History: 47 previous orders.",
                        "timestamp": now - 86200,
                        "intent": "data persistence",
                        "summary": "Customer profile and preferences persisted",
                    },
                ],
                "shared_state": {
                    "session_summary": "CustomerBot: Initial inquiry handoff to KnowledgeBase | MemoryAgent: Alice Robertson profile persisted",
                    "embedding_generated": True,
                    "entities_mentioned": ["Alice Robertson", "Order #WS-12345"],
                },
            },
            "session_2": {
                "session_id": "SES-002",
                "agents": ["KnowledgeBase", "SupportAnalytics", "BudgetChecker"],
                "turns": [
                    {
                        "id": "T2-001",
                        "tenant_id": "tenant_corp",
                        "user_id": "user_bob",
                        "agent_name": "KnowledgeBase",
                        "content": "Bob Johnson, I see you have 3 pending orders. Would you like me to prioritize order #WS-67890 which is already at the warehouse?",
                        "timestamp": now - 43200,
                        "intent": "personalized recommendation",
                        "summary": "Follow-up on previous incomplete interaction",
                    },
                    {
                        "id": "T2-002",
                        "tenant_id": "tenant_corp",
                        "user_id": "user_bob",
                        "agent_name": "SupportAnalytics",
                        "content": "Bob has a 93% satisfaction score. Recent complaints: No issues. Loyal customer category: Gold Tier. Recommendation: Offer priority upgrade.",
                        "timestamp": now - 43100,
                        "intent": "customer analytics",
                        "summary": "Customer behavior analytics retrieved",
                    },
                    {
                        "id": "T2-003",
                        "tenant_id": "tenant_corp",
                        "user_id": "user_bob",
                        "agent_name": "BudgetChecker",
                        "content": "Confirming your Gold Tier budget: 3 priority tiers unspent in your account. Priority upgrade cost: $15/month.",
                        "timestamp": now - 43000,
                        "intent": "financial check",
                        "summary": "Budget verification complete",
                    },
                ],
                "shared_state": {
                    "session_summary": "KnowledgeBase: Bob Johnson profile recalled | SupportAnalytics: Gold tier highlighting | BudgetChecker: Budget approved",
                    "historical_context": "Correlated with SES-001 (Alice Robertson incident)",
                    "new_knowledge_extracted": True,
                },
            },
            "session_3": {
                "session_id": "SES-003",
                "agents": ["MemoryAgent", "Enforcer", "TicketProxy"],
                "turns": [
                    {
                        "id": "T3-001",
                        "tenant_id": "tenant_corp",
                        "user_id": "user_carol",
                        "agent_name": "MemoryAgent",
                        "content": "Carol White, I've detected a 7-day loyalty pattern. Awaiting your custom quote for yesterday's group order (#WS-99999).",
                        "timestamp": now - 200,
                        "intent": "anticipatory service",
                        "summary": "Preemptive customer service based on identified patterns",
                    },
                    {
                        "id": "T3-002",
                        "tenant_id": "tenant_corp",
                        "user_id": "user_carol",
                        "agent_name": "Enforcer",
                        "content": "Order #WS-99999 - Group size: 8 people, all new customers. Agreement: 20% discount applied if booking today.",
                        "timestamp": now - 100,
                        "intent": "policy enforcement",
                        "summary": "Custom pricing policy applied",
                    },
                    {
                        "id": "T3-003",
                        "tenant_id": "tenant_corp",
                        "user_id": "user_carol",
                        "agent_name": "TicketProxy",
                        "content": "Booking confirmed. Order #WS-99999 attached to Account #AC-45678. Next steps: Confirm deposit by Oct 18.",
                        "timestamp": now - 50,
                        "intent": "transaction completion",
                        "summary": "Booking transaction finalized",
                    },
                ],
                "shared_state": {
                    "session_summary": "MemoryAgent: Pattern detection enabled | Enforcer: Custom pricing applied | TicketProxy: Transaction completed successfully",
                    "learning_committed": True,
                    "cross_session_correlation": "SES-001 & SES-002 identified 'Gold Tier' pattern",
                },
            },
            "nodes": [
                {
                    "id": "SES-001", 
                    "label": "Session", 
                    "props": {
                        "session_id": "SES-001",
                        "tenant_id": "tenant_corp",
                        "started_at": now - 86400,
                        "ended_at": now - 86000,
                        "status": "closed",
                        "turn_count": 3,
                        "participating_agents": ["CustomerBot", "KnowledgeBase", "MemoryAgent"]
                    }
                },
                {
                    "id": "T1-001",
                    "label": "ConversationTurn",
                    "props": {
                        "session_id": "SES-001",
                        "turn_number": 1,
                        "speaker": "CustomerBot",
                        "speaker_type": "agent",
                        "content": "Hello, I need help with my order #WS-12345. Can you check if it's been delivered?",
                        "timestamp": now - 86400,
                        "importance": "high"
                    }
                },
                {
                    "id": "T1-003",
                    "label": "ConversationTurn",
                    "props": {
                        "session_id": "SES-001",
                        "turn_number": 3,
                        "speaker": "MemoryAgent",
                        "speaker_type": "agent",
                        "content": "Storing customer profile: Alice Robertson. Last interaction: Sep 28. Known preferences: Prefers email communication. Order History: 47 previous orders.",
                        "timestamp": now - 86200,
                        "importance": "high"
                    }
                },
                {
                    "id": "SES-002",
                    "label": "Session",
                    "props": {
                        "session_id": "SES-002",
                        "tenant_id": "tenant_corp",
                        "started_at": now - 43200,
                        "ended_at": now - 42000,
                        "status": "closed",
                        "turn_count": 3,
                        "participating_agents": ["KnowledgeBase", "SupportAnalytics", "BudgetChecker"]
                    }
                },
                {
                    "id": "T2-001",
                    "label": "ConversationTurn",
                    "props": {
                        "session_id": "SES-002",
                        "turn_number": 1,
                        "speaker": "KnowledgeBase",
                        "speaker_type": "agent",
                        "content": "Bob Johnson, I see you have 3 pending orders. Would you like me to prioritize order #WS-67890 which is already at the warehouse?",
                        "timestamp": now - 43200,
                        "importance": "medium"
                    }
                },
                {
                    "id": "T2-002",
                    "label": "ConversationTurn",
                    "props": {
                        "session_id": "SES-002",
                        "turn_number": 2,
                        "speaker": "SupportAnalytics",
                        "speaker_type": "agent",
                        "content": "Bob has a 93% satisfaction score. Recent complaints: No issues. Loyal customer category: Gold Tier. Recommendation: Offer priority upgrade.",
                        "timestamp": now - 43100,
                        "importance": "medium"
                    }
                },
                {
                    "id": "SES-003",
                    "label": "Session",
                    "props": {
                        "session_id": "SES-003",
                        "tenant_id": "tenant_corp",
                        "started_at": now - 300,
                        "ended_at": now,
                        "status": "open",
                        "turn_count": 3,
                        "participating_agents": ["MemoryAgent", "Enforcer", "TicketProxy"]
                    }
                },
                {
                    "id": "T3-001",
                    "label": "ConversationTurn",
                    "props": {
                        "session_id": "SES-003",
                        "turn_number": 1,
                        "speaker": "MemoryAgent",
                        "speaker_type": "agent",
                        "content": "Carol White, I've detected a 7-day loyalty pattern. Awaiting your custom quote for yesterday's group order (#WS-99999).",
                        "timestamp": now - 200,
                        "importance": "high"
                    }
                },
                {
                    "id": "T3-003",
                    "label": "ConversationTurn",
                    "props": {
                        "session_id": "SES-003",
                        "turn_number": 3,
                        "speaker": "TicketProxy",
                        "speaker_type": "agent",
                        "content": "Booking confirmed. Order #WS-99999 attached to Account #AC-45678. Next steps: Confirm deposit by Oct 18.",
                        "timestamp": now - 50,
                        "importance": "high"
                    }
                },
                {
                    "id": "ENT-ALICE",
                    "label": "Entity",
                    "props": {
                        "name": "Alice Robertson",
                        "type": "customer",
                        "description": "Frequent customer prefers email communication",
                        "tenant_id": "tenant_corp",
                        "created_at": now - 86400 * 30
                    }
                },
                {
                    "id": "ENT-BOB",
                    "label": "Entity",
                    "props": {
                        "name": "Bob Johnson",
                        "type": "customer",
                        "description": "Gold Tier customer with 93% satisfaction rate",
                        "tenant_id": "tenant_corp",
                        "created_at": now - 86400 * 365
                    }
                },
                {
                    "id": "ENT-CAROL",
                    "label": "Entity",
                    "props": {
                        "name": "Carol White",
                        "type": "customer",
                        "description": "7-day loyalty pattern detected",
                        "tenant_id": "tenant_corp",
                        "created_at": now - 86400 * 7
                    }
                },
                {
                    "id": "SKILL-GOLD-TIER",
                    "label": "Skill",
                    "props": {
                        "name": "Gold Tier Customization",
                        "description": "Apply premium services to Gold Tier customers",
                        "procedure": [
                            {"step": 1, "action": "Identify Gold Tier customer from profile"},
                            {"step": 2, "action": "Check budget availability"},
                            {"step": 3, "action": "Apply priority upgrade logic"}
                        ],
                        "category": "customer-service",
                        "difficulty": 3,
                        "tenant_id": "tenant_corp",
                        "learned_by": "SupportAnalytics",
                        "created_at": now
                    }
                },
            ],
            "edges": [
                {"from": "SES-001", "to": "T1-001", "type": "CONTAINS_TURN", "props": {"order": 1}},
                {"from": "SES-001", "to": "T1-003", "type": "CONTAINS_TURN", "props": {"order": 3}},
                {"from": "T1-003", "to": "ENT-ALICE", "type": "KNOWS_FACT", "props": {"fact": "Alice's preference: email"}},
                {"from": "SES-002", "to": "T2-001", "type": "CONTAINS_TURN", "props": {"order": 1}},
                {"from": "SES-002", "to": "T2-002", "type": "CONTAINS_TURN", "props": {"order": 2}},
                {"from": "T2-002", "to": "ENT-BOB", "type": "KNOWS_FACT", "props": {"fact": "Bob is Gold Tier"}},
                {"from": "T2-002", "to": "SKILL-GOLD-TIER", "type": "HAS_PROCEDURAL", "props": {"training_source": "archived"}},
                {"from": "SES-003", "to": "T3-001", "type": "CONTAINS_TURN", "props": {"order": 1}},
                {"from": "SES-003", "to": "T3-003", "type": "CONTAINS_TURN", "props": {"order": 3}},
                {"from": "T3-001", "to": "ENT-CAROL", "type": "KNOWS_FACT", "props": {"fact": "Carol detected 7-day pattern"}},
                {"from": "ENT-BOB", "to": "SES-002", "type": "PARTICIPATES_IN", "props": {}},
                {"from": "ENT-CAROL", "to": "SES-003", "type": "PARTICIPATES_IN", "props": {}},
                {"from": "SES-001", "to": "SES-002", "type": "FOLLOWS", "props": {"session_gap_seconds": 43200}},
                {"from": "SES-002", "to": "SES-003", "type": "FOLLOWS", "props": {"session_gap_seconds": 43200}},
            ],
        }

    @staticmethod
    def get_procedural_learning_scenario() -> Dict[str, Any]:
        """Scenario 2: Procedural Memory Learning & Improvement"""
        now = int(time.time())
        return {
            "scenario_id": "PROCEDURAL-01",
            "title": "Adaptive Workflow Learning System",
            "description": "Agents learning and improving workflows through performance feedback, demonstrating procedural memory evolution.",
            "nodes": [
                {
                    "id": "WFL-ORDER-PROCESS",
                    "label": "Workflow",
                    "props": {
                        "id": "WFL-ORDER-PROCESS",
                        "name": "Customer Order Processing",
                        "description": "Complete end-to-end order lifecycle management",
                        "steps": [
                            "Customer inquiry",
                            "Inventory check",
                            "Price quotation",
                            "Order confirmation",
                            "Payment processing",
                            "Shipment tracking",
                            "Delivery confirmation",
                            "Feedback collection",
                        ],
                        "agents_involved": ["CustomerBot", "InventoryAgent", "PriceAgent", "PaymentAgent", "ShippingAgent"],
                        "success_criteria": "Order completion within 48 hours",
                        "tenant_id": "tenant_corp",
                        "version": 1,
                        "created_at": now - 86400 * 30
                    }
                },
                {
                    "id": "SKILL-ORDER-AUTOMATION",
                    "label": "Skill",
                    "props": {
                        "id": "SKILL-ORDER-AUTOMATION",
                        "name": "Standard Order Processing",
                        "description": "Process individual small orders successfully 95% of the time",
                        "procedure": [
                            {"step": 1, "action": "Parse customer order specs", "duration_ms": 500},
                            {"step": 2, "action": "Check inventory availability", "duration_ms": 800},
                            {"step": 3, "action": "Generate price quote", "duration_ms": 600},
                            {"step": 4, "action": "Schedule fulfillment", "duration_ms": 400},
                            {"step": 5, "action": "Confirm with customer", "duration_ms": 300},
                        ],
                        "category": "order-processing",
                        "difficulty": 2,
                        "success_rate": 0.95,
                        "execution_count": 1507,
                        "avg_duration_ms": 2600,
                        "tenant_id": "tenant_corp",
                        "learned_by": "CustomerBot",
                        "created_at": now - 86400 * 30,
                        "version": 1,
                        "improvements": []
                    }
                },
                {
                    "id": "SKILL-COMPLEX-ORDER",
                    "label": "Skill",
                    "props": {
                        "id": "SKILL-COMPLEX-ORDER",
                        "name": "Complex Multi-Part Order Handler",
                        "description": "Handle orders with 5+ items or cross-tier shipping requirements",
                        "procedure": [
                            {"step": 1, "action": "Validate complex requirements", "duration_ms": 1200},
                            {"step": 2, "action": "Find all compatible items", "duration_ms": 1500},
                            {"step": 3, "action": "Calculate combined discount", "duration_ms": 400},
                            {"step": 4, "action": "Coordinate with shipping partners", "duration_ms": 2000},
                            {"step": 5, "action": "Generate comprehensive quote", "duration_ms": 800},
                            {"step": 6, "action": "Complex approval workflow", "duration_ms": 1500},
                        ],
                        "category": "order-processing",
                        "difficulty": 5,
                        "success_rate": 0.88,
                        "execution_count": 234,
                        "avg_duration_ms": 7400,
                        "tenant_id": "tenant_corp",
                        "learned_by": "CustomerBot",
                        "created_at": now - 86400 * 60,
                        "version": 2,
                        "improvements": []
                    }
                },
                {
                    "id": "KEY-LEARNING-01",
                    "label": "Fact",
                    "props": {
                        "id": "KEY-LEARNING-01",
                        "statement": "Discount thresholds for complex orders improved by 25% after February enhancement",
                        "subject": "Discount pricing",
                        "predicate": "improved",
                        "object": "25%",
                        "source": "historical_analysis",
                        "tenant_id": "tenant_corp",
                        "created_at": now - 86400 * 14,
                    }
                },
                {
                    "id": "METRIC-100-SUCCESS",
                    "label": "Fact",
                    "props": {
                        "id": "METRIC-100-SUCCESS",
                        "statement": "SKILL-ORDER-AUTOMATION reached 100 successful executions milestone",
                        "subject": "ORDER-AUTOMATION skill",
                        "predicate": "achieved milestone",
                        "object": "100 executions",
                        "source": "performance_tracking",
                        "tenant_id": "tenant_corp",
                        "created_at": now - 86400 * 10,
                    }
                },
                {
                    "id": "TWEAK-LEARNED-01",
                    "label": "Fact",
                    "props": {
                        "id": "TWEAK-LEARNED-01",
                        "statement": "Inventory check time reduced by 40% when using cached item metadata",
                        "subject": "inventory agent system",
                        "predicate": "optimized",
                        "object": "40% faster",
                        "source": "trace_analytics",
                        "tenant_id": "tenant_corp",
                        "created_at": now - 86400 * 5,
                    }
                },
            ],
            "edges": [
                {"from": "WFL-ORDER-PROCESS", "to": "SKILL-ORDER-AUTOMATION", "type": "HAS_PROCEDURAL", "props": {"deployed_version": 1}},
                {"from": "WFL-ORDER-PROCESS", "to": "SKILL-COMPLEX-ORDER", "type": "HAS_PROCEDURAL", "props": {"deployed_version": 2}},
                {"from": "SKILL-ORDER-AUTOMATION", "to": "SKILL-COMPLEX-ORDER", "type": "IMPROVES", "props": {"enhancement_type": "feature_flag"}},
                {"from": "SKILL-ORDER-AUTOMATION", "to": "KEY-LEARNING-01", "type": "LEARNED_FROM", "props": {}},
                {"from": "SKILL-ORDER-AUTOMATION", "to": "METRIC-100-SUCCESS", "type": "LEARNED_FROM", "props": {}},
                {"from": "SKILL-ORDER-AUTOMATION", "to": "TWEAK-LEARNED-01", "type": "LEARNED_FROM", "props": {}},
                {"from": "TWEAK-LEARNED-01", "to": "SKILL-ORDER-AUTOMATION", "type": "IMPROVES", "props": {"result": "baseline_optimization"}},
                {"from": "TWEAK-LEARNED-01", "to": "SKILL-COMPLEX-ORDER", "type": "IMPROVES", "props": {"result": "optimization_common"}},
            ],
        }

    @staticmethod
    def get_all_scenarios() -> List[Dict[str, Any]]:
        return [
            SeedData.get_multi_session_scenario(),
            SeedData.get_procedural_learning_scenario()
        ]

    @staticmethod
    def load_into_graph(driver, scenario: Dict[str, Any], tenant_id: str = "tenant_corp") -> Dict[str, int]:
        """Load scenario nodes and edges into FalkorDB or fallback graph."""
        graph_name = f"memorix_{tenant_id}_memory"
        graph = driver.get_graph(graph_name)
        
        nodes_loaded = 0
        edges_loaded = 0
        
        nodes = scenario.get("nodes", [])
        edges = scenario.get("edges", [])
        
        if hasattr(graph, "nodes") and hasattr(graph, "edges"):
            # In-memory fallback graph
            for node in nodes:
                n_id = str(node.get("id"))
                label = node.get("label", "Entity")
                props = dict(node.get("props", {}))
                props["id"] = n_id
                if tenant_id and "tenant_id" not in props:
                    props["tenant_id"] = tenant_id
                
                # Check if exists
                existing = None
                for existing_node in graph.nodes:
                    if existing_node.get("id") == n_id or existing_node.get("props", {}).get("id") == n_id:
                        existing = existing_node
                        break
                if existing:
                    existing["props"].update(props)
                else:
                    graph.nodes.append({"id": n_id, "label": label, "props": props})
                nodes_loaded += 1
                
            for edge in edges:
                graph.add_edge(
                    from_id=str(edge.get("from")),
                    to_id=str(edge.get("to")),
                    rel_type=edge.get("type", "RELATES_TO"),
                    props=dict(edge.get("props", {}))
                )
                edges_loaded += 1
        else:
            # Real FalkorDB graph via Cypher
            for node in nodes:
                n_id = str(node.get("id"))
                label = node.get("label", "Entity")
                props = dict(node.get("props", {}))
                props["id"] = n_id
                if tenant_id and "tenant_id" not in props:
                    props["tenant_id"] = tenant_id
                
                # Format properties for Cypher
                set_clauses = [f"n.{k} = ${k}" for k in props.keys()]
                set_str = ", ".join(set_clauses)
                query = f"MERGE (n:{label} {{id: $id}}) SET {set_str} RETURN n"
                try:
                    graph.query(query, props)
                    nodes_loaded += 1
                except Exception:
                    pass
                    
            for edge in edges:
                from_id = str(edge.get("from"))
                to_id = str(edge.get("to"))
                rel_type = edge.get("type", "RELATES_TO")
                props = dict(edge.get("props", {}))
                
                query = f"""
                MATCH (a {{id: $from_id}}), (b {{id: $to_id}})
                MERGE (a)-[r:{rel_type}]->(b)
                SET r += $props
                RETURN r
                """
                try:
                    graph.query(query, {"from_id": from_id, "to_id": to_id, "props": props})
                    edges_loaded += 1
                except Exception:
                    pass
                    
        return {"nodes_loaded": nodes_loaded, "edges_loaded": edges_loaded}