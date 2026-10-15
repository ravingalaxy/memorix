#!/usr/bin/env python3
"""Comprehensive test script for Memorix application."""

import subprocess
import time
import sys
import os

def start_server():
    """Start the Memorix server in the background."""
    print("Starting Memorix server...")
    proc = subprocess.Popen(
        [sys.executable, 'main.py'],
        cwd='F:\\hackathon\\Track 2  Memorix',
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )
    time.sleep(3)
    return proc

def stop_server(proc):
    """Stop the server process."""
    print("Stopping server...")
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()

def test_endpoints():
    """Test all API endpoints."""
    import requests
    base = 'http://localhost:8000/api'
    
    print("\n=== MEMORIX SYSTEM VERIFICATION ===\n")
    
    results = []
    
    # 1. Health
    try:
        r = requests.get(f'{base}/health', timeout=5)
        s = r.json().get('status', 'unknown')
        print('1. Health: %d - %s' % (r.status_code, s))
        results.append(('Health', r.status_code == 200))
    except Exception as e:
        print('1. Health: ERROR - %s' % e)
        results.append(('Health', False))
    
    # 2. Seed scenario
    try:
        r = requests.post(f'{base}/seed/MULTI-SESSION-01', timeout=5)
        print('2. Seed scenario: %d - success=%s' % (r.status_code, r.json().get('success', False)))
        results.append(('Seed scenario', r.status_code == 200 and r.json().get('success', False)))
    except Exception as e:
        print('2. Seed scenario: ERROR - %s' % e)
        results.append(('Seed scenario', False))
    
    # 3. Start session
    try:
        r = requests.post(f'{base}/session/start', json={
            'session_id': 'SES-VERIFY-001', 'tenant_id': 'tenant_corp', 
            'user_id': 'user_test', 'agents': ['CustomerBot', 'MemoryAgent']
        }, timeout=5)
        print('3. Start session: %d - %s' % (r.status_code, r.json().get('status', 'unknown')))
        results.append(('Start session', r.status_code == 200))
    except Exception as e:
        print('3. Start session: ERROR - %s' % e)
        results.append(('Start session', False))
    
    # 4. Record turns
    turns_data = [
        ('CustomerBot', 'Hello, I need help with order #ORD-78901'),
        ('KnowledgeBase', 'Order #ORD-78901: In transit, ETA Oct 18'),
        ('MemoryAgent', 'Persisted customer profile: Alex Chen (Gold Tier)')
    ]
    turn_ok = True
    for i, (speaker, content) in enumerate(turns_data):
        try:
            r = requests.post(f'{base}/conversation/turn', json={
                'turn_id': 'T-VERIFY-%03d' % (i+1),
                'session_id': 'SES-VERIFY-001',
                'tenant_id': 'tenant_corp', 'speaker': speaker,
                'content': content, 'timestamp': 1234567890 + i,
                'intent': 'inquiry', 'entities_mentioned': ['ORD-78901', 'Alex Chen']
            }, timeout=5)
            status = r.status_code
            if status != 200:
                turn_ok = False
            print('  4.%d Turn: %s COMPLETED' % (i+1, status))
        except Exception as e:
            print('  4.%d Turn: ERROR - %s' % (i+1, e))
            turn_ok = False
    results.append(('Record turns', turn_ok))
    
    # 5. Add entity
    try:
        r = requests.post(f'{base}/entity', json={
            'name': 'Alex Chen', 'entity_type': 'customer', 
            'description': 'Gold Tier customer', 'tenant_id': 'tenant_corp'
        }, timeout=5)
        print('5. Add entity: %d - %s' % (r.status_code, r.json().get('status', 'unknown')))
        results.append(('Add entity', r.status_code == 200))
    except Exception as e:
        print('5. Add entity: ERROR - %s' % e)
        results.append(('Add entity', False))
    
    # 6. Add fact
    try:
        r = requests.post(f'{base}/fact', json={
            'statement': 'Alex Chen is a Gold Tier customer',
            'subject': 'Alex Chen', 'predicate': 'is', 'object': 'Gold Tier',
            'confidence': 0.95, 'source': 'session_data', 'tenant_id': 'tenant_corp'
        }, timeout=5)
        print('6. Add fact: %d - %s' % (r.status_code, r.json().get('status', 'unknown')))
        results.append(('Add fact', r.status_code == 200))
    except Exception as e:
        print('6. Add fact: ERROR - %s' % e)
        results.append(('Add fact', False))
    
    # 7. Get entity knowledge
    try:
        r = requests.get(f'{base}/entities/Alex%20Chen?tenant_id=tenant_corp', timeout=5)
        print('7. Get entity knowledge: %d - status=%s' % (r.status_code, r.json().get('status', 'unknown')))
        results.append(('Get entity knowledge', r.status_code == 200))
    except Exception as e:
        print('7. Get entity knowledge: ERROR - %s' % e)
        results.append(('Get entity knowledge', False))
    
    # 8. List entities (multi-tenant)
    try:
        r = requests.get(f'{base}/entities?tenant_id=tenant_corp', timeout=5)
        entity_count = len(r.json().get('entities', []))
        print('8. List entities: %d - %d entities' % (r.status_code, entity_count))
        results.append(('List entities', r.status_code == 200))
    except Exception as e:
        print('8. List entities: ERROR - %s' % e)
        results.append(('List entities', False))
    
    # 9. Cross-session recall
    try:
        r = requests.get(f'{base}/entities/Alex%20Chen?tenant_id=tenant_corp', timeout=5)
        print('9. Cross-session recall: %d - %s' % (r.status_code, r.json().get('status', 'unknown')))
        results.append(('Cross-session recall', r.status_code == 200))
    except Exception as e:
        print('9. Cross-session recall: ERROR - %s' % e)
        results.append(('Cross-session recall', False))
    
    # 10. Get skill
    try:
        r = requests.get(f'{base}/skills/Gold%20Tier%20Customization?tenant_id=tenant_corp', timeout=5)
        print('10. Get skill: %d - %s' % (r.status_code, r.json().get('status', 'unknown')))
        results.append(('Get skill', r.status_code == 200))
    except Exception as e:
        print('10. Get skill: ERROR - %s' % e)
        results.append(('Get skill', False))
    
    # 11. Graph endpoints
    try:
        r = requests.get(f'{base}/graphs', timeout=5)
        print('11. /api/graphs: %d' % r.status_code)
        results.append(('/api/graphs', r.status_code == 200))
    except Exception as e:
        print('11. /api/graphs: ERROR - %s' % e)
        results.append(('/api/graphs', False))
    
    try:
        r = requests.get(f'{base}/entities', timeout=5)
        print('12. /api/entities list: %d' % r.status_code)
        results.append(('/api/entities list', r.status_code == 200))
    except Exception as e:
        print('12. /api/entities list: ERROR - %s' % e)
        results.append(('/api/entities list', False))
    
    # 12. Scenario endpoint
    try:
        r = requests.get(f'{base}/scenarios', timeout=5)
        n = len(r.json()) if r.ok else 'unknown'
        print('13. /api/scenarios: %d - %s scenarios' % (r.status_code, n))
        results.append(('/api/scenarios', r.status_code == 200))
    except Exception as e:
        print('13. /api/scenarios: ERROR - %s' % e)
        results.append(('/api/scenarios', False))
    
    # 13. Skill suggest endpoint
    try:
        r = requests.get(f'{base}/skills/suggest?tenant_id=tenant_corp', timeout=5)
        print('14. /api/skills/suggest: %d' % r.status_code)
        results.append(('/api/skills/suggest', r.status_code == 200))
    except Exception as e:
        print('14. /api/skills/suggest: ERROR - %s' % e)
        results.append(('/api/skills/suggest', False))
    
    # 14. Coordination handoff endpoint
    try:
        r = requests.get(f'{base}/coordination/handoff', timeout=5)
        print('15. /api/coordination/handoff: %d' % r.status_code)
        results.append(('/api/coordination/handoff', r.status_code == 200))
    except Exception as e:
        print('15. /api/coordination/handoff: ERROR - %s' % e)
        results.append(('/api/coordination/handoff', False))
    
    print('\n=== SUMMARY ===')
    passed = sum(1 for _, ok in results if ok)
    total = len(results)
    print('Passed: %d/%d' % (passed, total))
    for name, ok in results:
        status = 'PASS' if ok else 'FAIL'
        print('  [%s] %s' % (status, name))
    
    return passed == total

if __name__ == '__main__':
    proc = start_server()
    try:
        success = test_endpoints()
    finally:
        stop_server(proc)
    
    sys.exit(0 if success else 1)
