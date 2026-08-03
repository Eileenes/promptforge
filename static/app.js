// PromptForge Frontend Application

const API = '/api';

// Tab switching
document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        tab.classList.add('active');
        document.getElementById(`tab-${tab.dataset.tab}`).classList.add('active');
        if (tab.dataset.tab === 'prompts') loadPrompts();
        if (tab.dataset.tab === 'library') loadLibrary();
        if (tab.dataset.tab === 'test') loadTestConfig();
    });
});

// === Prompts ===
async function loadPrompts() {
    const search = document.getElementById('search-input').value;
    const category = document.getElementById('category-filter').value;
    const params = new URLSearchParams();
    if (search) params.set('search', search);
    if (category) params.set('category', category);

    const resp = await fetch(`${API}/prompts?${params}`);
    const prompts = await resp.json();
    const container = document.getElementById('prompts-list');

    if (prompts.length === 0) {
        container.innerHTML = '<div class="empty-state"><div class="icon">📝</div><p>还没有提示词，点击"新建提示词"开始</p></div>';
        return;
    }

    container.innerHTML = prompts.map(p => `
        <div class="prompt-card">
            <span class="category-badge">${p.category}</span>
            <h4>${escapeHtml(p.title)}</h4>
            <p class="description">${escapeHtml(p.description || '无描述')}</p>
            <div class="content-preview">${escapeHtml(p.content.substring(0, 150))}...</div>
            <div class="meta">
                <span>v${p.version} · ${p.token_count} tokens</span>
                <span>${p.tags.map(t => `<span class="tag">${t}</span>`).join('')}</span>
            </div>
            <div class="actions">
                <button class="btn btn-sm btn-secondary" onclick="editPrompt(${p.id})">编辑</button>
                <button class="btn btn-sm btn-primary" onclick="optimizeFromCard(${p.id})">优化</button>
                <button class="btn btn-sm btn-secondary" onclick="testFromCard(${p.id})">测试</button>
                <button class="btn btn-sm btn-danger" onclick="deletePrompt(${p.id})">删除</button>
            </div>
        </div>
    `).join('');
}

function showCreateModal() {
    document.getElementById('modal-title').textContent = '新建提示词';
    document.getElementById('prompt-id').value = '';
    document.getElementById('prompt-title').value = '';
    document.getElementById('prompt-category').value = 'general';
    document.getElementById('prompt-description').value = '';
    document.getElementById('prompt-content').value = '';
    document.getElementById('prompt-tags').value = '';
    document.getElementById('modal').classList.remove('hidden');
}

async function editPrompt(id) {
    const resp = await fetch(`${API}/prompts/${id}`);
    const p = await resp.json();
    document.getElementById('modal-title').textContent = '编辑提示词';
    document.getElementById('prompt-id').value = p.id;
    document.getElementById('prompt-title').value = p.title;
    document.getElementById('prompt-category').value = p.category;
    document.getElementById('prompt-description').value = p.description;
    document.getElementById('prompt-content').value = p.content;
    document.getElementById('prompt-tags').value = p.tags.join(', ');
    document.getElementById('modal').classList.remove('hidden');
}

function closeModal() {
    document.getElementById('modal').classList.add('hidden');
}

async function savePrompt() {
    const id = document.getElementById('prompt-id').value;
    const data = {
        title: document.getElementById('prompt-title').value,
        category: document.getElementById('prompt-category').value,
        description: document.getElementById('prompt-description').value,
        content: document.getElementById('prompt-content').value,
        tags: document.getElementById('prompt-tags').value.split(',').map(t => t.trim()).filter(Boolean),
    };

    if (id) {
        await fetch(`${API}/prompts/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });
    } else {
        await fetch(`${API}/prompts`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });
    }
    closeModal();
    loadPrompts();
}

async function deletePrompt(id) {
    if (!confirm('确定删除这个提示词？')) return;
    await fetch(`${API}/prompts/${id}`, { method: 'DELETE' });
    loadPrompts();
}

// === Library ===
async function loadLibrary() {
    const resp = await fetch(`${API}/library`);
    const data = await resp.json();
    const container = document.getElementById('library-list');

    let html = '';
    for (const cat of data.categories) {
        for (const t of cat.prompts) {
            html += `
                <div class="library-card">
                    <span class="category-icon">${cat.icon}</span>
                    <h4>${escapeHtml(t.title)}</h4>
                    <p class="description">${escapeHtml(t.description)}</p>
                    <div class="actions">
                        <button class="btn btn-sm btn-primary" onclick="importTemplate('${t.id}')">导入</button>
                        <button class="btn btn-sm btn-secondary" onclick="viewTemplate('${t.id}')">预览</button>
                    </div>
                </div>
            `;
        }
    }
    container.innerHTML = html || '<div class="empty-state"><div class="icon">📚</div><p>模板库为空</p></div>';
}

async function searchLibrary() {
    const q = document.getElementById('library-search').value;
    const resp = await fetch(`${API}/library/search?q=${encodeURIComponent(q)}`);
    const results = await resp.json();
    const container = document.getElementById('library-list');

    if (results.length === 0) {
        container.innerHTML = '<div class="empty-state"><div class="icon">🔍</div><p>未找到匹配的模板</p></div>';
        return;
    }

    container.innerHTML = results.map(t => `
        <div class="library-card">
            <h4>${escapeHtml(t.title)}</h4>
            <p class="description">${escapeHtml(t.description)}</p>
            <div class="actions">
                <button class="btn btn-sm btn-primary" onclick="importTemplate('${t.id}')">导入</button>
            </div>
        </div>
    `).join('');
}

async function importTemplate(id) {
    const resp = await fetch(`${API}/library/import`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ template_id: id }),
    });
    const result = await resp.json();
    alert(result.message || '导入成功');
}

function viewTemplate(id) {
    // Simple alert preview - could be enhanced with a modal
    fetch(`${API}/library`).then(r => r.json()).then(data => {
        for (const cat of data.categories) {
            for (const t of cat.prompts) {
                if (t.id === id) {
                    alert(`${t.title}\n\n${t.content}`);
                    return;
                }
            }
        }
    });
}

// === Optimize ===
async function runOptimize() {
    const content = document.getElementById('optimize-input-text').value;
    if (!content.trim()) {
        alert('请输入要优化的提示词');
        return;
    }
    const strategy = document.getElementById('optimize-strategy').value;

    const resp = await fetch(`${API}/optimize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content, strategy }),
    });
    const result = await resp.json();

    document.getElementById('optimize-output-text').value = result.optimized_content;
    document.getElementById('optimize-stats').innerHTML = `
        <span class="stat-pill reduction">节省 ${result.reduction_pct}%</span>
        <span class="stat-pill tokens">${result.original_tokens} → ${result.optimized_tokens} tokens</span>
        <span class="stat-pill strategy">策略: ${result.strategy}</span>
    `;
}

function optimizeFromCard(id) {
    // Switch to optimize tab and load prompt
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    document.querySelector('[data-tab="optimize"]').classList.add('active');
    document.getElementById('tab-optimize').classList.add('active');

    fetch(`${API}/prompts/${id}`).then(r => r.json()).then(p => {
        document.getElementById('optimize-input-text').value = p.content;
    });
}

// === Test ===
async function loadTestConfig() {
    // Load prompts
    const promptsResp = await fetch(`${API}/prompts`);
    const prompts = await promptsResp.json();
    const promptSelect = document.getElementById('test-prompt-select');
    promptSelect.innerHTML = '<option value="">选择提示词...</option>' +
        prompts.map(p => `<option value="${p.id}">${p.title}</option>`).join('');

    // Load providers
    const providersResp = await fetch(`${API}/test/providers`);
    const providers = await providersResp.json();
    const providerSelect = document.getElementById('test-provider');
    providerSelect.innerHTML = Object.entries(providers).map(([key, val]) =>
        `<option value="${key}">${val.label}</option>`
    ).join('');
    updateModelOptions();
}

function updateModelOptions() {
    const provider = document.getElementById('test-provider').value;
    fetch(`${API}/test/providers`).then(r => r.json()).then(providers => {
        const models = providers[provider]?.models || [];
        document.getElementById('test-model').innerHTML =
            models.map(m => `<option value="${m}">${m}</option>`).join('');
    });
}

async function runTest() {
    const promptId = document.getElementById('test-prompt-select').value;
    if (!promptId) { alert('请选择提示词'); return; }

    const provider = document.getElementById('test-provider').value;
    const model = document.getElementById('test-model').value;
    const inputText = document.getElementById('test-input').value;

    document.getElementById('test-output').textContent = '运行中...';

    const resp = await fetch(`${API}/test/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt_id: parseInt(promptId), provider, model, input_text: inputText }),
    });
    const result = await resp.json();

    document.getElementById('test-output').textContent = result.output;
    document.getElementById('test-history').innerHTML = `
        <div class="history-item">
            <strong>${result.provider} / ${result.model}</strong> ·
            延迟 ${result.latency_ms}ms ·
            输入 ${result.tokens_input} tokens ·
            输出 ${result.tokens_output} tokens
        </div>
    `;
}

async function runBenchmark() {
    const promptId = document.getElementById('test-prompt-select').value;
    if (!promptId) { alert('请选择提示词'); return; }

    const promptResp = await fetch(`${API}/prompts/${promptId}`);
    const prompt = await promptResp.json();

    const resp = await fetch(`${API}/test/benchmark`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: prompt.content, prompt_id: parseInt(promptId) }),
    });
    const result = await resp.json();

    const colors = {
        clarity: '#6366f1',
        specificity: '#10b981',
        structure: '#f59e0b',
        token_efficiency: '#ec4899',
    };

    document.getElementById('benchmark-output').innerHTML = `
        <h3>效果评分</h3>
        ${['clarity', 'specificity', 'structure', 'token_efficiency'].map(key => `
            <div class="score-bar">
                <span class="score-label">${{clarity:'清晰度',specificity:'具体性',structure:'结构性',token_efficiency:'Token效率'}[key]}</span>
                <div class="score-track"><div class="score-fill" style="width:${result[key]*10}%;background:${colors[key]}"></div></div>
                <span class="score-value">${result[key]}</span>
            </div>
        `).join('')}
        <div class="score-bar" style="margin-top:12px;padding-top:8px;border-top:1px solid var(--border)">
            <span class="score-label" style="font-weight:700">总分</span>
            <div class="score-track"><div class="score-fill" style="width:${result.overall_score*10}%;background:var(--primary)"></div></div>
            <span class="score-value" style="font-weight:700">${result.overall_score}</span>
        </div>
        <div style="margin-top:12px;font-size:13px;color:var(--text-secondary)">
            <strong>建议:</strong>
            <ul style="margin-top:4px;padding-left:20px">
                ${result.suggestions.map(s => `<li>${s}</li>`).join('')}
            </ul>
        </div>
    `;
}

function testFromCard(id) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    document.querySelector('[data-tab="test"]').classList.add('active');
    document.getElementById('tab-test').classList.add('active');
    loadTestConfig().then(() => {
        document.getElementById('test-prompt-select').value = id;
    });
}

// Utils
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Init
loadPrompts();
