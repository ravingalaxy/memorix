"""
Memorix API Endpoint Verification Script
Tests all endpoints against the running server.
"""
import requests
import json
import sys

BASE = "http://localhost:8000"
results = []

def test(name, method, url, json_data=None, expect=200):
    try:
        if method == "GET":
            r = requests.get(url, timeout=10)
        else:
            r = requests.post(url, json=json_data, timeout=10)
        ok = r.status_code == expect
        status = "PASS" if ok else "FAIL"
        results.append((name, status, r.status_code))
        body_preview = r.text[:120] if not ok else ""
        if not ok:
            print(f"  FAIL {name}: got {r.status_code}, expected {expect}")
            print(f"       Body: {body_preview}")
        else:
            print(f"  PASS {name}: {r.status_code}")
    except Exception as e:
        results.append((name, "ERROR", str(e)))
        print(f"  ERROR {name}: {e}")

print("=" * 60)
print("MEMORIX API VERIFICATION")
print("=" * 60)

# 1. Health
test("Health Check", "GET", f"{BASE}/api/health")

# 2. Dashboard
test("Dashboard (GET /)", "GET", f"{BASE}/")

# 3. Scenarios
test("List Scenarios", "GET", f"{BASE}/api/scenarios")

# 4. Seed Scenario
test("Seed MULTI-SESSION-01", "POST", f"{BASE}/api/seed/MULTI-SESSION-01")

# 5. Seed Procedural
test("Seed PROCEDURAL-01", "POST", f"{BASE}/api/seed/PROCEDURAL-01")

# 6. Start Session
test("Start Session", "POST", f"{BASE}/api/session/start", {
    "session_id": "TEST-001", "user_id": "user_test",
    "tenant_id": "tenant_corp", "agents": ["CustomerBot", "KnowledgeBase"]
})

# 7. Record Turn
test("Record Turn", "POST", f"{BASE}/api/conversation/turn", {
    "turn_id": "T-TEST-001", "session_id": "TEST-001",
    "tenant_id": "tenant_corp", "user_id": "user_test",
    "speaker": "CustomerBot", "content": "Hello, I need help with my order",
    "intent": "inquiry", "entities_mentioned": "Order-123", "summary": "Test turn"
})

# 8. Add Entity
test("Add Entity", "POST", f"{BASE}/api/entity", {
    "name": "Alice Robertson", "type": "customer",
    "entity_type": "customer", "description": "Gold tier customer",
    "tenant_id": "tenant_corp"
})

# 9. List Entities
test("List Entities", "GET", f"{BASE}/api/entities?tenant_id=tenant_corp")

# 10. Add Fact
test("Add Fact", "POST", f"{BASE}/api/fact", {
    "statement": "Alice is a Gold Tier customer",
    "subject": "Alice", "predicate": "is", "object": "Gold Tier",
    "confidence": 0.95, "source": "test", "tenant_id": "tenant_corp"
})

# 11. Get Entity Knowledge
test("Get Entity Knowledge", "GET", f"{BASE}/api/entities/Alice%20Robertson?tenant_id=tenant_corp")

# 12. Add Skill
test("Add Skill", "POST", f"{BASE}/api/skill", {
    "name": "Order Processing", "description": "Process customer orders",
    "procedure": [{"step": 1, "action": "Parse order"}],
    "category": "order-processing", "difficulty": 2,
    "tenant_id": "tenant_corp", "learned_by": "CustomerBot"
})

# 13. Get Skill
test("Get Skill", "GET", f"{BASE}/api/skills/gold-tier-customization?tenant_id=tenant_corp")

# 14. Suggest Skills
test("Suggest Skills", "POST", f"{BASE}/api/skills/suggest", {
    "session_context": "customer support order processing",
    "tenant_id": "tenant_corp"
})

# 15. Agent Handoff
test("Agent Handoff", "POST", f"{BASE}/api/coordination/handoff", {
    "from_agent": "CustomerBot", "to_agent": "KnowledgeBase",
    "session_id": "TEST-001", "tenant_id": "tenant_corp",
    "context_summary": "Customer needs order status lookup"
})

# 16. Get Session History
test("Get Session History", "GET", f"{BASE}/api/sessions/TEST-001?tenant_id=tenant_corp")

# 17. End Session
test("End Session", "POST", f"{BASE}/api/session/end", {
    "session_id": "TEST-001", "tenant_id": "tenant_corp", "status": "closed"
})

# 18. Graph Data
test("Graph Data", "GET", f"{BASE}/api/graph/tenant_corp")

# Summary
print("\n" + "=" * 60)
passed = sum(1 for _, s, _ in results if s == "PASS")
failed = sum(1 for _, s, _ in results if s != "PASS")
print(f"RESULTS: {passed}/{len(results)} passed, {failed} failed")
if failed > 0:
    print("\nFailed tests:")
    for name, status, code in results:
        if status != "PASS":
            print(f"  - {name}: {status} ({code})")
print("=" * 60)
sys.exit(0 if failed == 0 else 1)
