/* ============================================================================
   MEMORIX — Dashboard Engine
   Neural Canvas edition. Cinematic SVG graph, count-up stats,
   staggered reveals, toast system, modal orchestration.
   ========================================================================== */

const NODE_STYLE = {
  session: { fill: '#38bdf8', dim: 'rgba(56,189,248,0.14)', r: 26, label: 'Session' },
  agent:   { fill: '#34d399', dim: 'rgba(52,211,153,0.14)', r: 20, label: 'Agent' },
  turn:    { fill: '#fbbf24', dim: 'rgba(251,191,36,0.14)', r: 13, label: 'Turn' },
  entity:  { fill: '#a78bfa', dim: 'rgba(167,139,250,0.14)', r: 16, label: 'Entity' },
  skill:   { fill: '#fb7185', dim: 'rgba(251,113,133,0.14)', r: 16, label: 'Skill' },
  unknown: { fill: '#64748b', dim: 'rgba(100,116,139,0.14)', r: 16, label: 'Node' }
};

const EDGE_STYLE = {
  contains:      { stroke: 'rgba(148,163,189,0.35)', width: 1.5, dash: null },
  contains_turn: { stroke: 'rgba(56,189,248,0.4)',   width: 1.5, dash: null },
  handoff:       { stroke: 'rgba(52,211,153,0.7)',   width: 2,   dash: '5 4' }
};

class MemorixDashboard {
  constructor() {
    this.apiBase = '/api';
    this.currentSession = null;
    this.currentTenant = 'tenant_corp';
    this.graphData = { nodes: [], links: [] };
    this.isDemoRunning = false;

    this.initializeElements();
    this.initializeEventListeners();
    this.initializeGraph();
    this.updateHealth();
    this.loadInitialData();

    setInterval(() => this.updateHealth(), 5000);
  }

  escapeHtml(str) {
    if (!str && str !== 0) return '';
    return String(str).replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'})[m]);
  }

  sleep(ms) {
    return new Promise(r => setTimeout(r, ms));
  }

  /* ---- Wiring -------------------------------------------------------- */
  initializeElements() {
    this.sessionForm = document.getElementById('session-form');
    this.turnForm = document.getElementById('turn-form');
    this.endSessionForm = document.getElementById('end-session-form');
    this.entityForm = document.getElementById('entity-form');
    this.factForm = document.getElementById('fact-form');
    this.tenantSelect = document.getElementById('tenant-select');
    this.timeline = document.getElementById('session-time');
    this.entityList = document.getElementById('entity-list');
    this.entityDetail = document.getElementById('entity-detail');
    this.skillDetail = document.getElementById('skill-detail');
    this.skillSelect = document.getElementById('skills-list');
    this.queryResults = document.getElementById('query-results');
    this.statusIndicator = document.getElementById('status-indicator');
    this.serverStatus = document.getElementById('server-status');
    this.overlay = document.getElementById('coordinating-overlay');
    this.overlayMessage = document.getElementById('coordinating-message');
    this.modal = document.getElementById('handoff-modal');
    this.graphEmpty = document.getElementById('graph-empty');
  }

  initializeEventListeners() {
    this.tenantSelect.addEventListener('change', async (e) => {
      this.currentTenant = e.target.value;
      this.currentSession = null;
      this.resetGraph();
      this.timeline.innerHTML = '';
      const timelineCount = document.getElementById('timeline-count');
      if (timelineCount) timelineCount.textContent = '0 events';
      if (this.entityDetail) this.entityDetail.hidden = true;
      if (this.skillDetail) this.skillDetail.innerHTML = '';
      if (this.queryResults) this.queryResults.hidden = true;
      this.showToast(`Switched to tenant: ${this.currentTenant}`, 'info');
      await this.loadInitialData();
    });

    this.sessionForm.addEventListener('submit', (e) => { e.preventDefault(); this.startSession(); });
    this.turnForm.addEventListener('submit', (e) => { e.preventDefault(); this.recordTurn(); });
    this.endSessionForm.addEventListener('submit', (e) => { e.preventDefault(); this.endSession(); });
    this.entityForm.addEventListener('submit', (e) => { e.preventDefault(); this.addEntity(); });
    this.factForm.addEventListener('submit', (e) => { e.preventDefault(); this.addFact(); });

    document.querySelectorAll('.scenario-btn').forEach(btn => {
      btn.addEventListener('click', () => this.loadScenario(btn.dataset.scenario));
    });

    this.skillSelect.addEventListener('change', (e) => this.loadSkill(e.target.value));

    document.getElementById('play-demo').addEventListener('click', () => this.playDemo());
    document.getElementById('reset-graph').addEventListener('click', () => this.resetGraph());
    document.getElementById('refresh-entities').addEventListener('click', () => this.loadEntities());

    const entitySearchInput = document.getElementById('entity-search');
    document.getElementById('search-entity').addEventListener('click', () => this.searchEntity());
    entitySearchInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') this.searchEntity(); });

    document.querySelectorAll('.query-tab').forEach(tab => {
      tab.addEventListener('click', () => {
        document.querySelectorAll('.query-tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.query-content').forEach(c => c.classList.remove('active'));
        tab.classList.add('active');
        document.querySelector(`.query-content[data-query="${tab.dataset.query}"]`).classList.add('active');
      });
    });

    document.getElementById('query-session-btn').addEventListener('click', () => this.querySession());
    document.getElementById('query-entity-btn').addEventListener('click', () => this.queryEntity());
    document.getElementById('query-skill-btn').addEventListener('click', () => this.querySkill());

    this.modal.querySelector('.modal-close').addEventListener('click', () => this.hideHandoffModal());
    this.modal.addEventListener('click', (e) => { if (e.target === this.modal) this.hideHandoffModal(); });
    document.getElementById('confirm-handoff').addEventListener('click', () => this.confirmHandoff());

    document.getElementById('skill-search').addEventListener('keypress', (e) => {
      if (e.key !== 'Enter') return;
      const v = e.target.value.trim();
      if (!v) return;
      const match = Array.from(this.skillSelect.options).find(o => 
        o.value.toLowerCase().includes(v.toLowerCase()) || 
        o.textContent.toLowerCase().includes(v.toLowerCase())
      );
      if (match) { this.skillSelect.value = match.value; this.loadSkill(match.value); }
    });

    let resizeTimeout;
    window.addEventListener('resize', () => {
      clearTimeout(resizeTimeout);
      resizeTimeout = setTimeout(() => this.renderGraph(), 200);
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.modal && this.modal.classList.contains('open')) {
        this.hideHandoffModal();
      }
    });
  }

  /* ---- API actions ---------------------------------------------------- */
  async startSession() {
    const sessionId = document.getElementById('session-id').value.trim();
    const userId = document.getElementById('user-id').value.trim();
    const selectedAgents = Array.from(document.getElementById('agents').selectedOptions).map(o => o.value);

    if (!sessionId || !userId || !selectedAgents.length) {
      this.showToast('Please fill all fields and select at least one agent', 'error');
      return;
    }

    this.showLoading('Starting session & coordinating memory…');
    try {
      const res = await fetch(`${this.apiBase}/session/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, tenant_id: this.currentTenant, user_id: userId, agents: selectedAgents })
      });
      if (!res.ok) throw new Error((await res.json()).detail || 'Failed to start session');

      this.currentSession = sessionId;
      const turnSessionField = document.getElementById('turn-session-id');
      if (turnSessionField) turnSessionField.value = sessionId;
      const endSessionField = document.getElementById('end-session-id');
      if (endSessionField) endSessionField.value = sessionId;
      const querySessionField = document.getElementById('query-session-id');
      if (querySessionField) querySessionField.value = sessionId;

      this.addTimelineEntry({ type: 'session_start', title: 'Session Started', description: `${sessionId} · ${selectedAgents.length} agents`, agent: 'Orchestrator' });
      this.addSessionToGraph(sessionId, selectedAgents);

      for (const agent of selectedAgents) await this.initializeAgentMemory(agent);

      this.showToast(`Session ${sessionId} started with ${selectedAgents.length} agents`, 'success');
      this.sessionForm.reset();
      this.updateStats();
    } catch (err) {
      console.error(err);
      this.showToast('Failed to start session: ' + err.message, 'error');
    } finally {
      this.hideLoading();
    }
  }

  async recordTurn() {
    const turnId = document.getElementById('turn-id').value.trim();
    const sessionId = document.getElementById('turn-session-id').value.trim();
    const speaker = document.getElementById('speaker').value.trim();
    const content = document.getElementById('content').value.trim();
    const intent = document.getElementById('intent').value.trim() || 'general';
    const entitiesStr = document.getElementById('entities').value.trim();

    if (!turnId || !sessionId || !speaker || !content) {
      this.showToast('Please fill all required fields', 'error');
      return;
    }

    this.showLoading('Recording turn in episodic memory…');
    try {
      const res = await fetch(`${this.apiBase}/conversation/turn`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          turn_id: turnId, session_id: sessionId, tenant_id: this.currentTenant,
          speaker, content, timestamp: Math.floor(Date.now() / 1000), intent,
          entities_mentioned: entitiesStr ? entitiesStr.split(',').map(s => s.trim()).filter(Boolean) : []
        })
      });
      if (!res.ok) throw new Error('Failed to record turn');

      this.addTimelineEntry({ type: 'turn', title: `Turn ${turnId}`, description: `${speaker}: ${content}`, agent: speaker });
      this.addTurnToGraph(turnId, sessionId, speaker, content);
      this.showToast(`Turn ${turnId} recorded in episodic memory`, 'success');
      this.turnForm.reset();
    } catch (err) {
      console.error(err);
      this.showToast('Failed to record turn: ' + err.message, 'error');
    } finally {
      this.hideLoading();
    }
  }

  async endSession() {
    const sessionId = document.getElementById('end-session-id').value.trim();
    const status = document.getElementById('session-status').value;
    if (!sessionId) { this.showToast('Please enter session ID', 'error'); return; }

    this.showLoading('Ending session & extracting learnings…');
    try {
      const res = await fetch(`${this.apiBase}/session/end`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, tenant_id: this.currentTenant, status })
      });
      if (!res.ok) throw new Error('Failed to end session');

      this.addTimelineEntry({ type: 'session_end', title: 'Session Ended', description: `${sessionId} → ${status}`, agent: 'Orchestrator' });
      this.showToast(`Session ${sessionId} ended (${status})`, 'success');
      this.endSessionForm.reset();
    } catch (err) {
      console.error(err);
      this.showToast('Failed to end session: ' + err.message, 'error');
    } finally {
      this.hideLoading();
    }
  }

  async addEntity() {
    const name = document.getElementById('entity-name').value.trim();
    const type = document.getElementById('entity-type').value.trim();
    const description = document.getElementById('entity-description').value.trim();
    if (!name) { this.showToast('Please enter entity name', 'error'); return; }

    this.showLoading('Persisting entity in knowledge graph…');
    try {
      const res = await fetch(`${this.apiBase}/entity`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, type: type, entity_type: type, description, tenant_id: this.currentTenant })
      });
      if (!res.ok) throw new Error('Failed to add entity');

      const entityNodeId = `entity-${name}`;
      if (!this.graphData.nodes.find(n => n.id === entityNodeId)) {
        this.graphData.nodes.push({ id: entityNodeId, label: name, type: 'entity', x: 0, y: 0, fresh: true });
        // Link to current session if active
        if (this.currentSession) {
          this.graphData.links.push({ source: this.currentSession, target: entityNodeId });
        }
        this.renderGraph();
      }

      this.addTimelineEntry({ type: 'entity', title: 'Entity Added', description: `${name}${type ? ` (${type})` : ''}`, agent: 'SemanticMemory' });
      this.showToast(`Entity "${name}" persisted`, 'success');
      this.entityForm.reset();
      await this.loadEntities();
    } catch (err) {
      console.error(err);
      this.showToast('Failed to add entity: ' + err.message, 'error');
    } finally {
      this.hideLoading();
    }
  }

  async addFact() {
    const statement = document.getElementById('fact-statement').value.trim();
    const subject = document.getElementById('fact-subject').value.trim();
    const predicate = document.getElementById('fact-predicate').value.trim();
    const object = document.getElementById('fact-object').value.trim();
    if (!statement) { this.showToast('Please enter a statement', 'error'); return; }

    this.showLoading('Recording fact with confidence scoring…');
    try {
      const res = await fetch(`${this.apiBase}/fact`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ statement, subject, predicate, object, confidence: 0.9, source: 'user', tenant_id: this.currentTenant })
      });
      if (!res.ok) throw new Error('Failed to add fact');

      this.addTimelineEntry({ type: 'fact', title: 'Fact Added', description: statement, agent: 'SemanticMemory' });
      this.showToast('Fact recorded in knowledge graph', 'success');
      this.factForm.reset();
    } catch (err) {
      console.error(err);
      this.showToast('Failed to add fact: ' + err.message, 'error');
    } finally {
      this.hideLoading();
    }
  }

  async loadScenario(scenarioId) {
    this.showLoading(`Seeding ${scenarioId} into memory…`);
    try {
      const res = await fetch(`${this.apiBase}/seed/${scenarioId}`, { method: 'POST' });
      if (!res.ok) throw new Error('Failed to load scenario');
      const result = await res.json();

      this.addTimelineEntry({ type: 'scenario', title: 'Scenario Loaded', description: `${result.title} · ${result.nodes_processed} nodes`, agent: 'SeedData' });
      this.showToast(`Scenario loaded: ${result.title}`, 'success');
      await this.loadInitialData();
      this.seedScenarioToGraph();
    } catch (err) {
      console.error(err);
      this.showToast('Failed to load scenario: ' + err.message, 'error');
    } finally {
      this.hideLoading();
    }
  }

  seedScenarioToGraph() {
    const known = [
      { id: 'SES-001', type: 'session', agents: ['CustomerBot', 'KnowledgeBase', 'MemoryAgent'] },
      { id: 'SES-002', type: 'session', agents: ['KnowledgeBase', 'SupportAnalytics', 'BudgetChecker'] },
      { id: 'SES-003', type: 'session', agents: ['MemoryAgent', 'Enforcer', 'TicketProxy'] }
    ];
    known.forEach((s, i) => setTimeout(() => this.addSessionToGraph(s.id, s.agents), i * 350));
  }

  async initializeAgentMemory(agent) {
    try {
      await fetch(`${this.apiBase}/skill`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: `${agent.toLowerCase()}-memory`, description: `${agent} agent memory system`,
          category: 'memory-agents', procedure: [{ step: 1, action: `${agent} knowledge initialization` }],
          difficulty: 2, learned_by: 'Orchestrator', tenant_id: this.currentTenant
        })
      });
    } catch (err) { console.warn('Agent memory init skipped:', err.message); }
  }

  /* ---- Data loading ------------------------------------------------------ */
  async loadInitialData() {
    await Promise.allSettled([this.loadEntities(), this.loadSkills()]);
    this.updateStats();
  }

  async loadEntities() {
    try {
      const res = await fetch(`${this.apiBase}/entities?tenant_id=${this.currentTenant}&limit=100`);
      if (!res.ok) return;
      const result = await res.json();
      const entities = result.Entities_Include || [];

      this.entityList.innerHTML = '';
      if (!entities.length) {
        this.entityList.innerHTML = '<p class="help-text" style="text-align:center;padding:16px 0">No entities yet — add one or load a scenario</p>';
        return;
      }

      entities.forEach((entity, i) => {
        const item = document.createElement('div');
        item.className = 'entity-item';
        item.style.setProperty('--stagger', `${Math.min(i * 45, 400)}ms`);
        item.setAttribute('tabindex', '0');
        item.setAttribute('role', 'button');
        item.innerHTML = `
          <span class="entity-dot entity"></span>
          <span class="entity-info">
            <strong>${this.escapeHtml(entity.name)}</strong>
            <small>${this.escapeHtml(entity.entity_type || 'unknown')}</small>
          </span>`;
        item.addEventListener('click', () => this.showEntityDetail(entity.name));
        item.addEventListener('keypress', (e) => { if (e.key === 'Enter') this.showEntityDetail(entity.name); });
        this.entityList.appendChild(item);
      });

      this.updateStats();
    } catch (err) {
      console.error('Load entities failed:', err);
    }
  }

  async showEntityDetail(name) {
    try {
      const res = await fetch(`${this.apiBase}/entities/${encodeURIComponent(name)}?tenant_id=${this.currentTenant}`);
      if (!res.ok) throw new Error('Not found');
      const result = await res.json();
      const facts = result.Entity_Facts || [];

      const entityType = (typeof result.query_entity === 'object' && result.query_entity?.entity_type)
        || result.query_entity?.type
        || 'entity';

      this.entityDetail.hidden = false;
      this.entityDetail.innerHTML = `
        <div class="entity-detail-card">
          <h4>${this.escapeHtml(name)}</h4>
          <div class="entity-meta">
            <span class="badge">${this.escapeHtml(entityType)}</span>
            <span class="badge bright">${this.escapeHtml(result.Connections_Detected ?? 0)} connections</span>
          </div>
          <div class="entity-facts">
            <h5>Known Facts</h5>
            ${facts.length ? facts.map(f => `
              <div class="fact-item">
                <p>${this.escapeHtml(f.fact || f.statement || '—')}</p>
                <small>confidence ${((f.confidence ?? 0.9) * 100).toFixed(0)}% · ${this.escapeHtml(f.source || 'system')}</small>
              </div>`).join('') : '<p class="help-text">No facts recorded yet</p>'}
          </div>
        </div>`;
    } catch (err) {
      this.showToast(`No knowledge found for "${name}"`, 'error');
    }
  }

  async loadSkills() {
    const commonSkills = ['gold-tier-customization', 'standard-order-processing', 'complex-multi-part-order-handler'];
    this.skillSelect.innerHTML = '<option value="">Load Skills from Memory…</option>';
    commonSkills.forEach(s => {
      const opt = document.createElement('option');
      opt.value = s;
      opt.textContent = s.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
      this.skillSelect.appendChild(opt);
    });
  }

  async loadSkill(skillName) {
    if (!skillName) { this.skillDetail.innerHTML = ''; return; }
    this.showLoading(`Retrieving "${skillName}" from procedural memory…`);
    try {
      const res = await fetch(`${this.apiBase}/skills/${skillName}?tenant_id=${this.currentTenant}`);
      if (!res.ok) throw new Error('Skill not found');
      const skill = await res.json();

      const skillNodeId = `skill-${skillName}`;
      if (!this.graphData.nodes.find(n => n.id === skillNodeId)) {
        this.graphData.nodes.push({ id: skillNodeId, label: skillName.replace(/-/g, ' '), type: 'skill', x: 0, y: 0, fresh: true });
        this.renderGraph();
      }

      const procStr = typeof skill.Skill_Procedure === 'object'
        ? JSON.stringify(skill.Skill_Procedure, null, 2)
        : (skill.Skill_Procedure || 'No procedure defined');

      this.skillDetail.innerHTML = `
        <div class="skill-card">
          <h4>${this.escapeHtml(skill.Skill_Name || skillName)}</h4>
          <p><strong>Category</strong><span>${this.escapeHtml(skill.Skill_Category || 'general')}</span></p>
          <p><strong>Difficulty</strong><span>${this.escapeHtml(skill.Skill_Difficulty ?? '—')}/5</span></p>
          <p><strong>Success</strong><span>${Math.round((skill.Skill_Success_Rate || 0) * 100)}%</span></p>
          <p><strong>Executions</strong><span>${(skill.Skill_Execution_Count || 0).toLocaleString()}</span></p>
          <p><strong>Avg Duration</strong><span>${(skill.Skill_Avg_Duration_ms || 0).toLocaleString()}ms</span></p>
          <p><strong>Learned By</strong><span>${this.escapeHtml(skill.Skill_Learned_By || 'System')}</span></p>
          <details>
            <summary>Procedure steps</summary>
            <pre>${this.escapeHtml(procStr)}</pre>
          </details>
        </div>`;
    } catch (err) {
      console.error(err);
      this.showToast('Skill not found in procedural memory', 'error');
    } finally {
      this.hideLoading();
    }
  }

  /* ---- Health & stats ------------------------------------------------------- */
  async updateHealth() {
    try {
      const res = await fetch(`${this.apiBase}/health`);
      if (!res.ok) throw new Error();
      const data = await res.json();

      if (data.status === 'healthy') {
        this.statusIndicator.className = 'status-indicator healthy';
        this.serverStatus.textContent = data.falkor_fallback ? 'Live · In-Memory Fallback' : 'Live · FalkorDB Connected';
      } else {
        this.statusIndicator.className = 'status-indicator unhealthy';
        this.serverStatus.textContent = 'Degraded';
      }
    } catch {
      this.statusIndicator.className = 'status-indicator unhealthy';
      this.serverStatus.textContent = 'Offline';
    }
  }

  updateStats() {
    const counts = {
      sessions: this.graphData.nodes.filter(n => n.type === 'session').length,
      entities: this.entityList.querySelectorAll('.entity-item').length,
      skills: Math.max(this.skillSelect.options.length - 1, 0),
      turns: this.graphData.nodes.filter(n => n.type === 'turn').length
    };
    const map = { sessions: 'stat-sessions', entities: 'stat-entities', skills: 'stat-skills', turns: 'stat-turns' };
    Object.entries(counts).forEach(([key, value]) => {
      const el = document.getElementById(map[key]);
      if (el) this.countUp(el, value);
    });
  }

  countUp(el, target) {
    const current = parseInt(el.textContent, 10) || 0;
    if (current === target) { el.textContent = target; return; }
    const start = performance.now();
    const duration = 500;
    const step = (now) => {
      const t = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - t, 3);
      el.textContent = Math.round(current + (target - current) * eased);
      if (t < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }

  /* ---- Graph engine ------------------------------------------------------------ */
  initializeGraph() {
    this.graphData = { nodes: [], links: [] };
    this.renderGraph();
  }

  addSessionToGraph(sessionId, agents) {
    if (!this.graphData.nodes.find(n => n.id === sessionId)) {
      this.graphData.nodes.push({ id: sessionId, label: sessionId, type: 'session', x: 0, y: 0, fresh: true });
    }
    agents.forEach(agent => {
      const agentId = `agent-${agent}`;
      if (!this.graphData.nodes.find(n => n.id === agentId)) {
        this.graphData.nodes.push({ id: agentId, label: agent, type: 'agent', x: 0, y: 0, fresh: true });
      }
      if (!this.graphData.links.find(l => (l.source === sessionId && l.target === agentId))) {
        this.graphData.links.push({ source: sessionId, target: agentId, type: 'contains' });
      }
    });
    this.renderGraph();
    this.updateStats();
  }

  addTurnToGraph(turnId, sessionId, speaker, content) {
    const turnNodeId = `turn-${turnId}`;
    if (this.graphData.nodes.find(n => n.id === turnNodeId)) return;
    // Also ensure parent session exists:
    if (!this.graphData.nodes.find(n => n.id === sessionId)) {
      this.addSessionToGraph(sessionId, [speaker]);
    }
    this.graphData.nodes.push({ id: turnNodeId, label: turnId, type: 'turn', speaker, content, x: 0, y: 0, fresh: true });
    this.graphData.links.push({ source: sessionId, target: turnNodeId, type: 'contains_turn' });

    const agentNode = this.graphData.nodes.find(n => n.id === `agent-${speaker}`);
    if (agentNode && !this.graphData.links.find(l => l.source === agentNode.id && l.target === turnNodeId)) {
      this.graphData.links.push({ source: agentNode.id, target: turnNodeId, type: 'contains' });
    }
    this.renderGraph();
    this.updateStats();
  }

  addHandoffToGraph(fromAgent, toAgent) {
    const fromNode = this.graphData.nodes.find(n => n.label === fromAgent && n.type === 'agent');
    const toNode = this.graphData.nodes.find(n => n.label === toAgent && n.type === 'agent');
    if (fromNode && toNode) {
      this.graphData.links.push({ source: fromNode.id, target: toNode.id, type: 'handoff', fresh: true });
      this.renderGraph();
    }
  }

  /* Force layout: rings around session centers, sessions in an arc */
  computeLayout(width, height) {
    const sessions = this.graphData.nodes.filter(n => n.type === 'session');
    const cx = width / 2, cy = height / 2;

    if (sessions.length === 0) {
      // No sessions: place remaining nodes in a loose circle
      const others = this.graphData.nodes;
      others.forEach((n, i) => {
        const a = (i / Math.max(others.length, 1)) * Math.PI * 2;
        n.x = cx + Math.cos(a) * Math.min(width, height) * 0.3;
        n.y = cy + Math.sin(a) * Math.min(width, height) * 0.3;
      });
    } else {
      // Sessions arranged in an arc
      const arcRadius = Math.min(width, height) * 0.34;
      sessions.forEach((s, i) => {
        const spread = sessions.length === 1 ? 0 : (Math.PI * 0.9);
        const a = sessions.length === 1 ? -Math.PI / 2 : (-Math.PI / 2 - spread / 2 + spread * (i / Math.max(sessions.length - 1, 1)));
        s.x = cx + Math.cos(a) * arcRadius;
        s.y = cy + Math.sin(a) * arcRadius + 20;
      });

      // Everything else orbits its nearest linked session
      this.graphData.nodes.filter(n => n.type !== 'session').forEach(node => {
        const link = this.graphData.links.find(l => l.target === node.id || l.source === node.id);
        const anchorId = link ? (link.source === node.id ? link.target : link.source) : null;
        const anchor = anchorId ? this.graphData.nodes.find(n => n.id === anchorId) : null;
        const base = anchor && anchor.type === 'session' ? anchor : sessions[0];
        if (!base) return;

        const siblings = this.graphData.links.filter(l => l.source === base.id || l.target === base.id)
          .map(l => (l.source === base.id ? l.target : l.source))
          .filter(id => id !== base.id);
        const idx = siblings.indexOf(node.id);
        const orbitR = node.type === 'agent' ? 110 : node.type === 'turn' ? 165 : 200;
        const angle = (idx / Math.max(siblings.length, 1)) * Math.PI * 2 + (base.x % 7) * 0.4;
        node.x = base.x + Math.cos(angle) * orbitR;
        node.y = base.y + Math.sin(angle) * orbitR;
      });
    }

    const margin = 30;
    this.graphData.nodes.forEach(node => {
      node.x = Math.max(margin, Math.min(width - margin, node.x));
      node.y = Math.max(margin, Math.min(height - margin, node.y));
    });
  }

  renderGraph() {
    const svg = document.getElementById('episodic-graph');
    const width = svg.clientWidth || 800;
    const height = 520;
    const NS = 'http://www.w3.org/2000/svg';

    svg.setAttribute('viewBox', `0 0 ${width} ${height}`);
    svg.innerHTML = '';

    const hasNodes = this.graphData.nodes.length > 0;
    this.graphEmpty.style.display = hasNodes ? 'none' : 'flex';

    this.computeLayout(width, height);

    // defs: glow filters + radial gradients per node type
    const defs = document.createElementNS(NS, 'defs');
    Object.entries(NODE_STYLE).forEach(([type, s]) => {
      const grad = document.createElementNS(NS, 'radialGradient');
      grad.id = `node-grad-${type}`;
      const stop1 = document.createElementNS(NS, 'stop');
      stop1.setAttribute('offset', '0%'); stop1.setAttribute('stop-color', '#ffffff'); stop1.setAttribute('stop-opacity', '0.9');
      const stop2 = document.createElementNS(NS, 'stop');
      stop2.setAttribute('offset', '45%'); stop2.setAttribute('stop-color', s.fill);
      const stop3 = document.createElementNS(NS, 'stop');
      stop3.setAttribute('offset', '100%'); stop3.setAttribute('stop-color', s.fill); stop3.setAttribute('stop-opacity', '0.55');
      grad.append(stop1, stop2, stop3);
      defs.appendChild(grad);
    });
    svg.appendChild(defs);

    const nodeById = new Map(this.graphData.nodes.map(n => [n.id, n]));

    // --- Edges (curved bezier paths) ---
    this.graphData.links.forEach((link, i) => {
      const s = nodeById.get(link.source);
      const t = nodeById.get(link.target);
      if (!s || !t) return;
      const style = EDGE_STYLE[link.type] || EDGE_STYLE.contains;

      const mx = (s.x + t.x) / 2, my = (s.y + t.y) / 2;
      const dx = t.x - s.x, dy = t.y - s.y;
      const len = Math.hypot(dx, dy) || 1;
      const curve = Math.min(len * 0.12, 28);
      const c1x = mx - dy / len * curve, c1y = my + dx / len * curve;

      const path = document.createElementNS(NS, 'path');
      path.setAttribute('d', `M ${s.x} ${s.y} Q ${c1x} ${c1y} ${t.x} ${t.y}`);
      path.setAttribute('fill', 'none');
      path.setAttribute('stroke', style.stroke);
      path.setAttribute('stroke-width', style.width);
      path.setAttribute('stroke-linecap', 'round');
      if (style.dash) path.setAttribute('stroke-dasharray', style.dash);
      path.style.opacity = '0';
      path.style.transition = 'opacity 0.6s cubic-bezier(0.22,1,0.36,1)';
      if (link.type === 'handoff') {
        path.style.filter = 'drop-shadow(0 0 6px rgba(52,211,153,0.5))';
        const anim = document.createElementNS(NS, 'animate');
        anim.setAttribute('attributeName', 'stroke-dashoffset');
        anim.setAttribute('values', '18;0');
        anim.setAttribute('dur', '1.2s');
        anim.setAttribute('repeatCount', 'indefinite');
        path.appendChild(anim);
      }
      svg.appendChild(path);
      setTimeout(() => { path.style.opacity = link.fresh ? '1' : '0.9'; }, i * 35);
      link.fresh = false;
    });

    // --- Nodes ---
    this.graphData.nodes.forEach((node, i) => {
      const style = NODE_STYLE[node.type] || NODE_STYLE.unknown;
      const g = document.createElementNS(NS, 'g');
      g.setAttribute('transform', `translate(${node.x}, ${node.y})`);
      g.style.cursor = node.type === 'agent' ? 'pointer' : 'default';
      g.style.opacity = '0';
      g.style.transition = 'opacity 0.5s cubic-bezier(0.22,1,0.36,1)';

      // Halo
      const halo = document.createElementNS(NS, 'circle');
      halo.setAttribute('r', style.r + 12);
      halo.setAttribute('fill', style.dim);
      g.appendChild(halo);

      // Main sphere with gradient
      const circle = document.createElementNS(NS, 'circle');
      circle.setAttribute('r', style.r);
      circle.setAttribute('fill', `url(#node-grad-${node.type})`);
      circle.setAttribute('stroke', 'rgba(255,255,255,0.5)');
      circle.setAttribute('stroke-width', '1.5');
      circle.setAttribute('filter', 'drop-shadow(0 0 10px rgba(0,0,0,0.4))');
      g.appendChild(circle);

      // Fresh-node pulse
      if (node.fresh) {
        const pulse = document.createElementNS(NS, 'circle');
        pulse.setAttribute('r', style.r);
        pulse.setAttribute('fill', 'none');
        pulse.setAttribute('stroke', style.fill);
        pulse.setAttribute('stroke-width', '2');
        const anim = document.createElementNS(NS, 'animate');
        anim.setAttribute('attributeName', 'r');
        anim.setAttribute('from', style.r); anim.setAttribute('to', style.r + 26);
        anim.setAttribute('dur', '1.4s');
        anim.setAttribute('repeatCount', '3');
        const anim2 = document.createElementNS(NS, 'animate');
        anim2.setAttribute('attributeName', 'opacity');
        anim2.setAttribute('from', '0.8'); anim2.setAttribute('to', '0');
        anim2.setAttribute('dur', '1.4s');
        anim2.setAttribute('repeatCount', '3');
        pulse.append(anim, anim2);
        g.appendChild(pulse);
        node.fresh = false;
      }

      // Label — dark pill with crisp text
      const label = node.label.length > 14 ? node.label.substring(0, 12) + '…' : node.label;
      const labelGroup = document.createElementNS(NS, 'g');
      const text = document.createElementNS(NS, 'text');
      text.setAttribute('text-anchor', 'middle');
      text.setAttribute('y', style.r + 16);
      text.setAttribute('font-family', "'JetBrains Mono', monospace");
      text.setAttribute('font-size', node.type === 'turn' ? '9' : '10');
      text.setAttribute('font-weight', '500');
      text.setAttribute('fill', '#cbd5e1');
      text.setAttribute('paint-order', 'stroke');
      text.setAttribute('stroke', '#05070d');
      text.setAttribute('stroke-width', '3');
      text.setAttribute('stroke-linejoin', 'round');
      text.textContent = label;
      labelGroup.appendChild(text);
      g.appendChild(labelGroup);

      // Hover interactions
      g.addEventListener('mouseenter', () => {
        circle.setAttribute('stroke', '#ffffff');
        circle.setAttribute('stroke-width', '2.5');
        halo.setAttribute('r', style.r + 18);
      });
      g.addEventListener('mouseleave', () => {
        circle.setAttribute('stroke', 'rgba(255,255,255,0.5)');
        circle.setAttribute('stroke-width', '1.5');
        halo.setAttribute('r', style.r + 12);
      });

      if (node.type === 'agent') {
        g.addEventListener('click', () => this.showHandoffModal(node.label));
        g.setAttribute('tabindex', '0');
        g.setAttribute('role', 'button');
        g.setAttribute('aria-label', `Agent ${node.label}. Click to coordinate handoff.`);
        g.addEventListener('keypress', (e) => { if (e.key === 'Enter') this.showHandoffModal(node.label); });
      }

      svg.appendChild(g);
      setTimeout(() => { g.style.opacity = '1'; }, i * 45);
    });
  }

  resetGraph() {
    this.graphData = { nodes: [], links: [] };
    this.renderGraph();
    this.updateStats();
    this.showToast('Graph cleared', 'info');
  }

  /* ---- Handoff modal -------------------------------------------------------- */
  showHandoffModal(agentName) {
    document.getElementById('handoff-from').value = agentName;
    document.getElementById('handoff-to').value = '';
    document.getElementById('handoff-context').value = '';
    this.modal.classList.add('open');
    setTimeout(() => document.getElementById('handoff-to').focus(), 80);
  }

  hideHandoffModal() {
    this.modal.classList.remove('open');
  }

  async confirmHandoff() {
    const fromAgent = document.getElementById('handoff-from').value;
    const toAgent = document.getElementById('handoff-to').value.trim();
    const context = document.getElementById('handoff-context').value.trim();
    if (!toAgent) { this.showToast('Please specify the target agent', 'error'); return; }

    this.showLoading(`Coordinating handoff: ${fromAgent} → ${toAgent}…`);
    try {
      const res = await fetch(`${this.apiBase}/coordination/handoff`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: this.currentSession || 'SES-DEMO', tenant_id: this.currentTenant,
          from_agent: fromAgent, to_agent: toAgent, context_summary: context
        })
      });
      if (!res.ok) throw new Error('Handoff request failed');

      this.addTimelineEntry({ type: 'handoff', title: 'Agent Handoff', description: `${fromAgent} → ${toAgent}${context ? ` · ${context}` : ''}`, agent: 'Orchestrator' });
      this.addHandoffToGraph(fromAgent, toAgent);
      this.showToast(`Handoff coordinated: ${fromAgent} → ${toAgent}`, 'success');
      this.hideHandoffModal();
    } catch (err) {
      console.error(err);
      this.showToast('Handoff coordination failed', 'error');
    } finally {
      this.hideLoading();
    }
  }

  /* ---- Timeline --------------------------------------------------------------- */
  addTimelineEntry(entry) {
    const icons = { session_start: '🚀', session_end: '🏁', turn: '💬', entity: '🧠', fact: '📝', handoff: '🔄', scenario: '📋' };
    const item = document.createElement('div');
    item.className = 'timeline-item';
    item.innerHTML = `
      <div class="timeline-icon">${icons[entry.type] || '📋'}</div>
      <div class="timeline-content">
        <h4>${this.escapeHtml(entry.title)}</h4>
        <p>${this.escapeHtml(entry.description)}</p>
        <small>${this.escapeHtml(entry.agent)} · ${new Date().toLocaleTimeString()}</small>
      </div>`;
    this.timeline.insertBefore(item, this.timeline.firstChild);
    document.getElementById('timeline-count').textContent = `${this.timeline.children.length} events`;
  }

  /* ---- Queries ------------------------------------------------------------------ */
  async searchEntity() {
    const name = document.getElementById('entity-search').value.trim();
    if (!name) return;
    await this.showEntityDetail(name);
  }

  async querySession() {
    const sessionId = document.getElementById('query-session-id').value.trim();
    if (!sessionId) return;
    await this.executeQuery(async () => {
      const res = await fetch(`${this.apiBase}/sessions/${sessionId}?tenant_id=${this.currentTenant}`);
      return { ok: res.ok, data: await res.json() };
    }, `Session · ${sessionId}`);
  }

  async queryEntity() {
    const name = document.getElementById('query-entity-name').value.trim();
    if (!name) return;
    await this.executeQuery(async () => {
      const res = await fetch(`${this.apiBase}/entities/${encodeURIComponent(name)}?tenant_id=${this.currentTenant}`);
      return { ok: res.ok, data: await res.json() };
    }, `Entity · ${name}`);
  }

  async querySkill() {
    const name = document.getElementById('query-skill-name').value.trim();
    if (!name) return;
    await this.executeQuery(async () => {
      const res = await fetch(`${this.apiBase}/skills/${encodeURIComponent(name)}?tenant_id=${this.currentTenant}`);
      return { ok: res.ok, data: await res.json() };
    }, `Skill · ${name}`);
  }

  async executeQuery(fetcher, title) {
    this.showLoading('Querying memory graph…');
    try {
      const { ok, data } = await fetcher();
      this.queryResults.hidden = false;
      this.queryResults.innerHTML = `
        <div class="query-result-card">
          <h4>${ok ? '✓ ' : '⚠ '}${this.escapeHtml(title)}</h4>
          <pre>${this.escapeHtml(JSON.stringify(data, null, 2))}</pre>
        </div>`;
    } catch (err) {
      this.queryResults.hidden = false;
      this.queryResults.innerHTML = `<div class="query-result-card"><h4>⚠ ${this.escapeHtml(title)}</h4><pre>${this.escapeHtml(err.message)}</pre></div>`;
    } finally {
      this.hideLoading();
    }
  }

  /* ---- Demo mode -------------------------------------------------------------------- */
  async playDemo() {
    if (this.isDemoRunning) {
      this.showToast('Demo is already running', 'error');
      return;
    }
    this.isDemoRunning = true;
    try {
      this.showToast('Running guided demo — watch the canvas', 'info');
      await this.loadScenario('MULTI-SESSION-01');

      await this.sleep(1200);
      document.getElementById('session-id').value = 'SES-LIVE-DEMO';
      document.getElementById('user-id').value = 'user_demo';
      const agentSelect = document.getElementById('agents');
      Array.from(agentSelect.options).forEach(opt => {
        opt.selected = ['CustomerBot', 'KnowledgeBase', 'MemoryAgent'].includes(opt.value);
      });
      await this.startSession();

      const turns = [
        { turn: 'T-DEMO-001', speaker: 'CustomerBot', content: 'Hello, I need help with order #ORD-78901 — it is urgent.', intent: 'inquiry', entities: 'ORD-78901' },
        { turn: 'T-DEMO-002', speaker: 'KnowledgeBase', content: 'Order #ORD-78901: In transit, ETA Oct 18. Gold Tier priority applied.', intent: 'information', entities: 'ORD-78901' },
        { turn: 'T-DEMO-003', speaker: 'MemoryAgent', content: 'Persisted customer profile: Alex Chen (Gold Tier). Cross-session recall linked to SES-001.', intent: 'persistence', entities: 'Alex Chen' }
      ];
      for (const t of turns) {
        await this.sleep(1600);
        document.getElementById('turn-id').value = t.turn;
        document.getElementById('turn-session-id').value = 'SES-LIVE-DEMO';
        document.getElementById('speaker').value = t.speaker;
        document.getElementById('content').value = t.content;
        document.getElementById('intent').value = t.intent;
        document.getElementById('entities').value = t.entities;
        await this.recordTurn();
      }
    } finally {
      this.isDemoRunning = false;
    }
  }

  /* ---- Feedback: toasts & loading ------------------------------------------------------ */
  showToast(message, type = 'info') {
    const existingToasts = document.querySelectorAll('.toast');
    if (existingToasts.length >= 3) {
      existingToasts[0].remove();
    }
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = this.escapeHtml(message);
    toast.addEventListener('click', () => toast.remove());
    container.appendChild(toast);
    requestAnimationFrame(() => toast.classList.add('show'));
    setTimeout(() => {
      toast.classList.remove('show');
      setTimeout(() => toast.remove(), 400);
    }, 3200);
  }

  showLoading(message) {
    this.overlayMessage.textContent = message;
    this.overlay.classList.add('open');
  }

  hideLoading() {
    this.overlay.classList.remove('open');
  }
}

document.addEventListener('DOMContentLoaded', () => {
  window.dashboard = new MemorixDashboard();
});
