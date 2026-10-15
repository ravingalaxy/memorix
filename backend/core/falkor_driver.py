"""
FalkorDB Driver - Production-grade database abstraction for Memorix.
Handles multi-graph isolation, tenant separation, and memory-optimized Cypher execution.
"""

import os
import logging
import threading
import time
import re
from typing import Any, Dict, List, Optional, Union
from falkordb import FalkorDB

logger = logging.getLogger(__name__)


class FalkorDriver:
    """Production-grade FalkorDB driver with multi-graph memory isolation."""

    def __init__(
        self,
        host: str = None,
        port: int = None,
        db_name: str = "memorix",
        use_fallback: bool = True,
    ):
        self.host = host or os.getenv("FALKOR_HOST", "localhost")
        self.port = int(port or os.getenv("FALKOR_PORT", 6379))
        self.password = os.getenv("FALKOR_PASSWORD", None)
        self.username = os.getenv("FALKOR_USERNAME", None)
        self.db_name = db_name
        self.use_fallback = use_fallback
        self._db: Optional[FalkorDB] = None
        self._graphs: Dict[str, Any] = {}
        self._fallback_store: Dict[str, Dict[str, List]] = {} if use_fallback else None
        self._lock = threading.Lock()
        self._query_stats = {"total": 0, "fallback": 0, "real": 0, "errors": 0}
        self._connection_time = 0.0

    @property
    def db(self) -> FalkorDB:
        if self._db is None:
            self._connect()
        return self._db

    def _connect(self):
        start = time.perf_counter()
        try:
            connect_kwargs = {}
            if self.password:
                connect_kwargs["password"] = self.password
            if self.username:
                connect_kwargs["username"] = self.username
            self._db = FalkorDB(host=self.host, port=self.port, **connect_kwargs)
            logger.info(f"Connected to FalkorDB at {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"FalkorDB connection failed: {e}")
            if self.use_fallback:
                logger.warning("Using in-memory fallback store")
                self._db = None
            else:
                raise
        finally:
            self._connection_time = time.perf_counter() - start

    def get_graph(self, name: str):
        """Get or create a graph by name (supports multi-graph isolation)."""
        with self._lock:
            if name not in self._graphs:
                if self._db is not None:
                    try:
                        self._graphs[name] = self._db.select_graph(name)
                    except Exception as e:
                        logger.warning(f"Graph {name} selection failed: {e}, using fallback")
                        self._graphs[name] = _FallbackGraph(name, self._fallback_store)
                else:
                    self._graphs[name] = _FallbackGraph(name, self._fallback_store)
        return self._graphs[name]

    def select_graph(self, name: str):
        return self.get_graph(name)

    def query(self, graph_name: str, cypher: str, params: Optional[Dict] = None):
        self._query_stats["total"] += 1
        if self._db is None:
            self._query_stats["fallback"] += 1
        else:
            self._query_stats["real"] += 1
        
        graph = self.get_graph(graph_name)
        try:
            result = graph.query(cypher, params or {})
            return result
        except Exception as e:
            self._query_stats["errors"] += 1
            logger.error(f"Query error on {graph_name}: {e}")
            raise

    def create_graph(self, name: str):
        """Create a new graph (no-op for FalkorDB, graphs are created on first write)."""
        if name not in self._graphs:
            self.get_graph(name)
        return self._graphs.get(name)

    def get_stats(self) -> Dict:
        return self._query_stats.copy()

    def close(self):
        if self._db is not None:
            try:
                self._db.close()
            except Exception:
                pass
        self._graphs.clear()


class _FallbackGraph:
    """In-memory fallback graph for testing when FalkorDB is unavailable.
    Supports the Cypher subset needed for memory operations.
    """

    def __init__(self, name: str, store: Dict):
        self.name = name
        self.store = store
        self._lock = threading.Lock()
        
        # Initialize storage for this graph
        graph_data = store.setdefault(name, {"nodes": [], "edges": []})
        self.nodes: List[Dict] = graph_data.setdefault("nodes", [])
        self.edges: List[Dict] = graph_data.setdefault("edges", [])
        
        # Track next node ID
        self._next_id = max([n.get("id", 0) for n in self.nodes if isinstance(n.get("id"), int)] + [0]) + 1

    def query(self, cypher: str, params: Optional[Dict] = None) -> List[List]:
        params = params or {}
        cypher = cypher.strip()
        cypher_upper = cypher.upper()

        with self._lock:
            # Detect write operations: CREATE, MERGE, or MATCH with ON CREATE SET/ON MATCH SET
            is_write = (cypher.upper().startswith("CREATE") or 
                       cypher.upper().startswith("MERGE") or
                       "ON CREATE SET" in cypher.upper() or
                       "ON MATCH SET" in cypher.upper())
            
            logger.debug(f"DEBUG Fallback: is_write={is_write}, query starts with: {cypher[:50]!r}")
            
            if is_write:
                return self._handle_write(cypher, params)
            elif cypher.upper().startswith("MATCH"):
                return self._handle_match(cypher, params)
            elif cypher.upper().startswith("CALL"):
                return self._handle_call(cypher, params)
            else:
                return [[]]

    def _handle_write(self, cypher: str, params: Dict) -> List[List]:
        """Handle CREATE, MERGE, and MATCH...ON CREATE SET queries."""
        import re
        
        # Substitute parameters
        working_cypher = cypher
        for key, value in params.items():
            placeholder = "$" + key
            if isinstance(value, str):
                escaped_value = str(value).replace('\\', '\\\\').replace('"', '\\"')
                working_cypher = working_cypher.replace(placeholder, '"' + escaped_value + '"')
            else:
                working_cypher = working_cypher.replace(placeholder, str(value))
        
        logger.debug(f"DEBUG _handle_write: working_cypher = {working_cypher!r}")
        
        # Patterns:
        # 1. MERGE|CREATE (var:Label {props})
        # 2. MATCH (var:Label {props}) ON CREATE SET
        node_pattern = r'(?:MERGE|CREATE)\s*\(?(\w*)\)?\s*:(\w+)\s*\{([^}]+)\}\)?'
        match_pattern = r'MATCH\s*\(?(\w*)\)?\s*:(\w+)\s*\{([^}]+)\}\)?\s*ON\s+CREATE\s+SET'
        
        # Use DOTALL flag to match across newlines
        logger.debug(f"DEBUG node_pattern matches: {re.findall(node_pattern, working_cypher, re.IGNORECASE | re.DOTALL)}")
        logger.debug(f"DEBUG match_pattern matches: {re.findall(match_pattern, working_cypher, re.IGNORECASE | re.DOTALL)}")
        
        nodes_created = []
        
        def process_node(props, label):
            # Also extract from ON CREATE SET
            on_create_match = re.search(r'ON CREATE SET\s+(.+?)(?:\s+RETURN|\s*$)', working_cypher, re.IGNORECASE | re.DOTALL)
            if on_create_match:
                on_create_str = on_create_match.group(1)
                for set_match in re.finditer(r'\w+\.(\w+)\s*=\s*([^,\n]+)', on_create_str):
                    prop_key, prop_val = set_match.groups()
                    props[prop_key.strip()] = prop_val.strip().strip('"\'')
            
            # Also extract from ON MATCH SET
            on_match_match = re.search(r'ON MATCH SET\s+(.+?)(?:\s+RETURN|\s*$)', working_cypher, re.IGNORECASE | re.DOTALL)
            if on_match_match:
                on_match_str = on_match_match.group(1)
                for set_match in re.finditer(r'\w+\.(\w+)\s*=\s*([^,\n]+)', on_match_str):
                    prop_key, prop_val = set_match.groups()
                    if prop_key.strip() not in props:
                        props[prop_key.strip()] = prop_val.strip().strip('"\'')
            
            # Generate node ID
            node_id = props.get("id") or props.get("incr_id") or f"node_{self._next_id}"
            self._next_id += 1
            
            # Check if node exists
            existing = None
            for n in self.nodes:
                if n.get("label") == label:
                    matched_identifying_prop = False
                    match = True
                    for k, v in props.items():
                        if k in ('name', 'id', 'incr_id', 'session_id', 'turn_id', 'statement'):
                            matched_identifying_prop = True
                            if n.get("props", {}).get(k) != v:
                                match = False
                                break
                    if match and matched_identifying_prop:
                        existing = n
                        break
            
            if existing:
                # Only update if we matched on a real identifier
                existing["props"].update(props)
                logger.debug(f"Updated existing node: {label} {props.get('name', node_id)}")
            else:
                node_data = {"id": node_id, "label": label, "props": props}
                self.nodes.append(node_data)
                nodes_created.append(node_data)
                logger.debug(f"Created new node: {label} {props.get('name', node_id)}")
        
        # Pattern 1: MERGE|CREATE
        node_pattern = r'(?:MERGE|CREATE)\s*\(?(\w*)\)?\s*:(\w+)\s*\{([^}]+)\}\)?'
        for match in re.finditer(node_pattern, working_cypher, re.IGNORECASE | re.DOTALL):
            var_name, label, props_str = match.groups()
            props = {}
            for kv_match in re.finditer(r'(\w+)\s*:\s*(?:"([^"]*)"|([^,}]+))', props_str):
                k = kv_match.group(1).strip()
                v = (kv_match.group(2) if kv_match.group(2) is not None else kv_match.group(3)).strip().strip("'")
                props[k] = v
            process_node(props, label)
        
        # Pattern 2: MATCH ... ON CREATE SET
        match_pattern = r'MATCH\s*\(?(\w*)\)?\s*:(\w+)\s*\{([^}]+)\}\)?\s*ON\s+CREATE\s+SET'
        for match in re.finditer(match_pattern, working_cypher, re.IGNORECASE | re.DOTALL):
            var_name, label, props_str = match.groups()
            props = {}
            for kv_match in re.finditer(r'(\w+)\s*:\s*(?:"([^"]*)"|([^,}]+))', props_str):
                k = kv_match.group(1).strip()
                v = (kv_match.group(2) if kv_match.group(2) is not None else kv_match.group(3)).strip().strip("'")
                props[k] = v
            process_node(props, label)
        
        if nodes_created:
            return [[{"id": n["id"], "label": n["label"], "props": n["props"]}] for n in nodes_created]
        return [[]]

    def _handle_match(self, cypher: str, params: Dict) -> List[List]:
        cypher_upper = cypher.upper()
        if "RETURN" not in cypher_upper:
            return [[]]

        # Substitute parameters
        working_cypher = cypher
        for key, value in params.items():
            placeholder = "$" + key
            if isinstance(value, str):
                escaped_value = str(value).replace('\\', '\\\\').replace('"', '\\"')
                working_cypher = working_cypher.replace(placeholder, '"' + escaped_value + '"')
            else:
                working_cypher = working_cypher.replace(placeholder, str(value))

        logger.debug(f"Fallback match query (substituted): {working_cypher}")

        # Extract return variables
        return_vars = []
        return_match = re.search(r'RETURN\s+(.+?)(?:\s+LIMIT|\s+ORDER|\s+WHERE|$)', working_cypher, re.IGNORECASE | re.DOTALL)
        if return_match:
            return_clause = return_match.group(1).strip()
            return_vars = [v.strip().split(' AS ')[0].strip().split('.')[-1] for v in return_clause.split(',')]

        # Determine target labels from MATCH clause
        target_labels = re.findall(r':(\w+)', working_cypher)
        
        # Filter nodes based on query
        filtered_nodes = self._filter_nodes(working_cypher, params, target_labels)
        
        # Build result rows
        if not return_vars:
            return [[n] for n in filtered_nodes]
        
        results = []
        for node in filtered_nodes:
            row = []
            for var in return_vars:
                if var in ('n', 'node', 's', 't', 'e', 'f', 'k'):
                    row.append(node)
                elif '.' in var:
                    parts = var.split('.')
                    if len(parts) == 2 and parts[0] in ('n', 'node', 's', 't', 'e', 'f', 'k'):
                        row.append(node.get('props', {}).get(parts[1]))
                    else:
                        row.append(None)
                else:
                    row.append(node.get('props', {}).get(var))
            results.append(row if len(row) > 1 else [row[0]] if row else [])
        
        return results if results else [[]]

    def _filter_nodes(self, cypher: str, params: Dict, target_labels: List[str]) -> List[Dict]:
        nodes = self.nodes
        
        if target_labels:
            nodes = [n for n in nodes if n.get('label') in target_labels]
        
        # Only filter by params that are actually provided and non-empty
        name = params.get('name')
        if name:
            nodes = [n for n in nodes if n.get('props', {}).get('name') == name]
        
        statement = params.get('statement')
        if statement:
            nodes = [n for n in nodes if n.get('props', {}).get('statement') == statement]
        
        session_id = params.get('session_id')
        if session_id:
            nodes = [n for n in nodes if n.get('props', {}).get('session_id') == session_id or
                     n.get('props', {}).get('incr_id') == session_id]
        
        tenant_id = params.get('tenant_id')
        if tenant_id:
            nodes = [n for n in nodes if n.get('props', {}).get('tenant_id') == tenant_id]
            
        user_id = params.get('user_id')
        if user_id:
            nodes = [n for n in nodes if n.get('props', {}).get('user_id') == user_id]
        
        incident_id = params.get('incident_id')
        if incident_id:
            nodes = [n for n in nodes if n.get('props', {}).get('incr_id') == incident_id or 
                     n.get('props', {}).get('incident_id') == incident_id or
                     n.get('props', {}).get('session_id') == incident_id]
        
        return nodes

    def _handle_call(self, cypher: str, params: Dict) -> List[List]:
        if 'PAGERANK' in cypher.upper():
            return [[{"nodeId": i, "score": 0.5 - i * 0.05, "name": f"Memory-Entity-{i}"} for i in range(5)]]
        elif 'WCC' in cypher.upper() or 'CONNECTED_COMPONENTS' in cypher.upper():
            return [[{"componentId": 0, "memberId": i, "name": f"MemoryCluster-{i}"} for i in range(3)]]
        elif 'DEGREE' in cypher.upper():
            return [[{"nodeId": i, "degree": 3 - i} for i in range(4)]]
        return [[]]

    def run(self, cypher: str, params: Optional[Dict] = None):
        return self.query(cypher, params)

    def create(self, label: str, props: Dict):
        node = {"id": str(len(self.nodes)), "label": label, "props": props}
        self.nodes.append(node)
        return node

    def add_edge(self, from_id: str, to_id: str, rel_type: str, props: Dict = None):
        edge = {"from": from_id, "to": to_id, "type": rel_type, "props": props or {}}
        self.edges.append(edge)
        return edge