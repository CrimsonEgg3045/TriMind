/* ================================================================
   Tri Mind — Chat UI Logic
   Supports SVG/Canvas/Chart.js diagram rendering + image fallback
   ================================================================ */

const chatMessages = document.getElementById('chat-messages');
const queryInput   = document.getElementById('query-input');
const sendBtn      = document.getElementById('send-btn');
const welcomeState = document.getElementById('welcome-state');

let isProcessing = false;

// ── Auto-resize textarea ──────────────────────────────────────────
queryInput.addEventListener('input', () => {
    queryInput.style.height = 'auto';
    queryInput.style.height = Math.min(queryInput.scrollHeight, 160) + 'px';
});

// ── Keyboard shortcut: Enter to send ──────────────────────────────
queryInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSend();
    }
});

// ── Send message ──────────────────────────────────────────────────
async function handleSend() {
    const query = queryInput.value.trim();
    if (!query || isProcessing) return;

    if (welcomeState) welcomeState.classList.add('hidden');
    addMessage('user', query);
    queryInput.value = '';
    queryInput.style.height = 'auto';
    await processQuery(query);
}

// ── Demo shortcut ─────────────────────────────────────────────────
async function askDemo(query) {
    if (isProcessing) return;
    if (welcomeState) welcomeState.classList.add('hidden');
    addMessage('user', query);
    await processQuery(query);
}

// ── Process query ─────────────────────────────────────────────────
async function processQuery(query) {
    isProcessing = true;
    sendBtn.disabled = true;

    const thinkingId = showThinking();

    try {
        const response = await fetch('/api/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                query, 
                use_demo: true,
                user_id: window.currentUser ? window.currentUser.id : null,
                incognito: window.incognitoMode
            }),
        });

        if (!response.ok) throw new Error(`Server error: ${response.status}`);
        const data = await response.json();

        removeThinking(thinkingId);
        addAIResponse(data);

    } catch (error) {
        removeThinking(thinkingId);
        addMessage('assistant', `**Error:** ${error.message}\n\nPlease check that the server is running and try again.`);
    } finally {
        isProcessing = false;
        sendBtn.disabled = false;
    }
}

// ── Add user/assistant message ────────────────────────────────────
function addMessage(role, content) {
    const row = document.createElement('div');
    row.className = `message-row ${role}`;

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.innerHTML = role === 'user' ? '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="4"/><path d="M2 20c0-4 4.5-7 10-7s10 3 10 7"/></svg>' : '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="6" r="3"/><circle cx="5" cy="18" r="3"/><circle cx="19" cy="18" r="3"/><line x1="12" y1="9" x2="12" y2="14"/><line x1="9" y1="16" x2="7" y2="16"/><line x1="15" y1="16" x2="17" y2="16"/></svg>';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';

    if (role === 'user') {
        bubble.textContent = content;
    } else {
        bubble.innerHTML = renderMarkdown(content);
    }

    contentDiv.appendChild(bubble);
    row.appendChild(avatar);
    row.appendChild(contentDiv);
    chatMessages.appendChild(row);

    scrollToBottom();
    if (role === 'assistant') typesetMath();
}

// ── Add AI response with diagram or image ─────────────────────────
function addAIResponse(data) {
    const row = document.createElement('div');
    row.className = 'message-row assistant';

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="6" r="3"/><circle cx="5" cy="18" r="3"/><circle cx="19" cy="18" r="3"/><line x1="12" y1="9" x2="12" y2="14"/><line x1="9" y1="16" x2="7" y2="16"/><line x1="15" y1="16" x2="17" y2="16"/></svg>';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';

    // Render synthesized content
    const synthesized = data.synthesized || '_No response available._';
    bubble.innerHTML = renderMarkdown(synthesized);
    contentDiv.appendChild(bubble);

    // ── Render diagram (PRIMARY) ──────────────────────────────────
    if (data.visual_diagram && data.visual_diagram.code) {
        const diagramWrapper = document.createElement('div');
        diagramWrapper.className = 'diagram-container';

        const diagramContent = document.createElement('div');
        diagramContent.className = 'diagram-render';

        try {
            const format = data.visual_diagram.format || 'svg';

            if (format === 'svg') {
                diagramContent.innerHTML = data.visual_diagram.code;
            } else if (format === 'canvas' || format === 'chartjs') {
                const canvas = document.createElement('canvas');
                canvas.id = 'diagram-canvas-' + Date.now();
                canvas.width = 600;
                canvas.height = 400;
                diagramContent.appendChild(canvas);

                if (format === 'chartjs' && typeof Chart !== 'undefined') {
                    try {
                        const chartConfig = JSON.parse(data.visual_diagram.code);
                        new Chart(canvas, chartConfig);
                    } catch (e) {
                        console.warn('Chart.js config parse failed:', e);
                    }
                } else if (format === 'canvas') {
                    try {
                        const ctx = canvas.getContext('2d');
                        const drawFn = new Function('ctx', 'canvas', data.visual_diagram.code);
                        drawFn(ctx, canvas);
                    } catch (e) {
                        console.warn('Canvas render failed:', e);
                    }
                }
            }
        } catch (e) {
            console.warn('Diagram render error:', e);
            diagramContent.innerHTML = '<p class="diagram-error">Diagram could not be rendered</p>';
        }

        // Add description caption
        if (data.visual_diagram.description) {
            const caption = document.createElement('p');
            caption.className = 'diagram-description';
            caption.textContent = data.visual_diagram.description;
            diagramWrapper.appendChild(diagramContent);
            diagramWrapper.appendChild(caption);
        } else {
            diagramWrapper.appendChild(diagramContent);
        }

        contentDiv.appendChild(diagramWrapper);
    }

    // ── Render fallback image (SECONDARY — mutually exclusive) ────
    else if (data.visual_image && data.visual_image.data) {
        const imgWrapper = document.createElement('div');
        imgWrapper.className = 'generated-image';

        const img = document.createElement('img');
        img.src = data.visual_image.data;
        img.alt = 'AI Generated Educational Visual';
        img.loading = 'lazy';

        const caption = document.createElement('p');
        caption.className = 'image-caption';
        caption.textContent = 'Generated by Cloudflare Workers AI';

        imgWrapper.appendChild(img);
        imgWrapper.appendChild(caption);
        contentDiv.appendChild(imgWrapper);
    }

    row.appendChild(avatar);
    row.appendChild(contentDiv);
    chatMessages.appendChild(row);

    scrollToBottom();
    typesetMath();
}

// ── Thinking indicator ────────────────────────────────────────────
let thinkingCounter = 0;

function showThinking() {
    const id = `thinking-${++thinkingCounter}`;

    const row = document.createElement('div');
    row.className = 'message-row assistant';
    row.id = id;

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="6" r="3"/><circle cx="5" cy="18" r="3"/><circle cx="19" cy="18" r="3"/><line x1="12" y1="9" x2="12" y2="14"/><line x1="9" y1="16" x2="7" y2="16"/><line x1="15" y1="16" x2="17" y2="16"/></svg>';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';

    bubble.innerHTML = `
        <div class="thinking-indicator">
            <div class="thinking-dots">
                <span></span><span></span><span></span>
            </div>
            <span class="thinking-text">Agents are collaborating on your question...</span>
        </div>
        <div class="agent-progress" id="${id}-progress"></div>
    `;

    contentDiv.appendChild(bubble);
    row.appendChild(avatar);
    row.appendChild(contentDiv);
    chatMessages.appendChild(row);

    scrollToBottom();

    const agents = [
        { name: '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="6" r="3"/><circle cx="5" cy="18" r="3"/><circle cx="19" cy="18" r="3"/><line x1="12" y1="9" x2="12" y2="14"/><line x1="9" y1="16" x2="7" y2="16"/><line x1="15" y1="16" x2="17" y2="16"/></svg> Explanation', delay: 300 },
        { name: '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polygon points="3 22 12 2 21 22"/><line x1="8" y1="16" x2="16" y2="16"/></svg> Math', delay: 800 },
        { name: '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="3"/><line x1="12" y1="2" x2="12" y2="5"/><line x1="12" y1="19" x2="12" y2="22"/><line x1="2" y1="12" x2="5" y2="12"/><line x1="19" y1="12" x2="22" y2="12"/></svg> Visual', delay: 1300 },
        { name: '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg> Synthesizer', delay: 3000 },
    ];

    agents.forEach(({ name, delay }) => {
        setTimeout(() => {
            const progress = document.getElementById(`${id}-progress`);
            if (progress) {
                const tag = document.createElement('span');
                tag.className = 'agent-tag working';
                tag.innerHTML = `<span class="mini-spinner"></span> ${name}`;
                progress.appendChild(tag);
                scrollToBottom();
            }
        }, delay);
    });

    return id;
}

function removeThinking(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

// ── LaTeX-safe Markdown rendering ─────────────────────────────────
function renderMarkdown(text) {
    // Protect LaTeX blocks from markdown parser mangling
    const latexBlocks = [];
    let placeholder = '%%LATEX_BLOCK_';

    // Protect display math: $$...$$
    text = text.replace(/\$\$([\s\S]*?)\$\$/g, (match) => {
        const idx = latexBlocks.length;
        latexBlocks.push(match);
        return placeholder + idx + '%%';
    });

    // Protect inline math: $...$  (but not $$)
    text = text.replace(/\$([^$\n]+?)\$/g, (match) => {
        const idx = latexBlocks.length;
        latexBlocks.push(match);
        return placeholder + idx + '%%';
    });

    // Protect \( ... \) and \[ ... \]
    text = text.replace(/\\\(([\s\S]*?)\\\)/g, (match) => {
        const idx = latexBlocks.length;
        latexBlocks.push(match);
        return placeholder + idx + '%%';
    });
    text = text.replace(/\\\[([\s\S]*?)\\\]/g, (match) => {
        const idx = latexBlocks.length;
        latexBlocks.push(match);
        return placeholder + idx + '%%';
    });

    // Run markdown parser
    let html;
    if (typeof marked !== 'undefined') {
        marked.setOptions({ breaks: true, gfm: true });
        html = marked.parse(text);
    } else {
        html = text
            .replace(/### (.*)/g, '<h3>$1</h3>')
            .replace(/## (.*)/g, '<h2>$1</h2>')
            .replace(/# (.*)/g, '<h1>$1</h1>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
            .replace(/`(.*?)`/g, '<code>$1</code>')
            .replace(/\n/g, '<br>');
    }

    // Restore LaTeX blocks
    latexBlocks.forEach((block, idx) => {
        html = html.replace(placeholder + idx + '%%', block);
    });

    return html;
}

// ── MathJax typesetting ───────────────────────────────────────────
function typesetMath() {
    if (typeof MathJax !== 'undefined' && MathJax.typesetPromise) {
        MathJax.typesetPromise().catch(() => {});
    }
}

// ── Reset chat ────────────────────────────────────────────────────
function resetChat() {
    const messages = chatMessages.querySelectorAll('.message-row');
    messages.forEach(m => m.remove());
    if (welcomeState) welcomeState.classList.remove('hidden');
    queryInput.value = '';
    queryInput.style.height = 'auto';
    queryInput.focus();
}

// ── Scroll to bottom ──────────────────────────────────────────────
function scrollToBottom() {
    requestAnimationFrame(() => {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    });
}

// ── Focus input on load ───────────────────────────────────────────
queryInput.focus();

// ── Global State & Initialization ─────────────────────────────────
window.currentUser = null;
window.incognitoMode = false;

document.addEventListener("DOMContentLoaded", async () => {
    // Check health & initialize Google Auth
    try {
        const res = await fetch('/api/health');
        const data = await res.json();
        if (data.google_client_id) {
            initGoogleAuth(data.google_client_id);
        } else {
            console.warn("Google Client ID not set on server.");
        }
    } catch (e) {
        console.error("Failed to check health", e);
    }

    // Auto-open sidebar and highlight support me on load
    if (window.innerWidth > 768) {
        const supportBtn = document.getElementById('support-me-btn');
        if (supportBtn) {
            supportBtn.classList.add('highlight');
            setTimeout(() => supportBtn.classList.remove('highlight'), 4000);
        }
    }
});

// ── Google Auth ───────────────────────────────────────────────────
function initGoogleAuth(clientId) {
    if (typeof google === 'undefined') {
        setTimeout(() => initGoogleAuth(clientId), 500);
        return;
    }
    google.accounts.id.initialize({
        client_id: clientId,
        callback: handleCredentialResponse
    });
    google.accounts.id.renderButton(
        document.getElementById("google-login-btn"),
        { theme: "outline", size: "large", width: 230 }
    );
}

async function handleCredentialResponse(response) {
    try {
        const res = await fetch('/api/auth/verify', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ credential: response.credential })
        });
        const data = await res.json();
        
        if (data.status === 'success') {
            window.currentUser = data.user;
            document.getElementById('google-login-btn').classList.add('hidden');
            const profile = document.getElementById('user-profile');
            profile.classList.remove('hidden');
            document.getElementById('user-avatar').src = window.currentUser.picture;
            document.getElementById('user-name').textContent = window.currentUser.name;
            
            document.getElementById('incognito-btn').classList.remove('hidden');
            
            // Highlight support me on login
            const sidebar = document.getElementById('sidebar');
            sidebar.classList.remove('collapsed');
            const supportBtn = document.getElementById('support-me-btn');
            supportBtn.classList.add('highlight');
            setTimeout(() => supportBtn.classList.remove('highlight'), 4000);
            
            fetchHistory();
        } else {
            alert('Login failed: ' + data.message);
        }
    } catch (e) {
        console.error('Error verifying token', e);
    }
}

function toggleLogout() {
    document.getElementById('logout-popover').classList.toggle('hidden');
}

function logout() {
    window.currentUser = null;
    document.getElementById('google-login-btn').classList.remove('hidden');
    document.getElementById('user-profile').classList.add('hidden');
    document.getElementById('logout-popover').classList.add('hidden');
    document.getElementById('incognito-btn').classList.add('hidden');
    
    document.getElementById('chat-history-list').innerHTML = '<div class="empty-history">Login to see your history</div>';
}

// ── History ───────────────────────────────────────────────────────
async function fetchHistory() {
    if (!window.currentUser) return;
    try {
        const res = await fetch(`/api/history?user_id=${window.currentUser.id}`);
        const data = await res.json();
        if (data.status === 'success') {
            renderHistory(data.history);
        }
    } catch (e) {
        console.error('Failed to fetch history', e);
    }
}

function renderHistory(history) {
    const list = document.getElementById('chat-history-list');
    list.innerHTML = '';
    
    if (history.length === 0) {
        list.innerHTML = '<div class="empty-history">No history found</div>';
        return;
    }
    
    // Sort latest first
    history.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    
    history.forEach(item => {
        const btn = document.createElement('button');
        btn.className = 'history-item';
        btn.textContent = item.query;
        btn.onclick = () => loadHistoryChat(item);
        list.appendChild(btn);
    });
}

function loadHistoryChat(item) {
    resetChat();
    addMessage('user', item.query);
    addAIResponse(item.response);
}

// ── Sidebar & UI Toggles ──────────────────────────────────────────
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    const isCollapsed = sidebar.classList.toggle('collapsed');

    // Manage mobile overlay
    if (overlay) {
        if (isCollapsed) {
            overlay.classList.remove('active');
        } else {
            overlay.classList.add('active');
        }
    }
}

function closeSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    if (!sidebar.classList.contains('collapsed')) {
        sidebar.classList.add('collapsed');
    }
    if (overlay) {
        overlay.classList.remove('active');
    }
}

function toggleIncognito() {
    window.incognitoMode = !window.incognitoMode;
    const btn = document.getElementById('incognito-btn');
    if (window.incognitoMode) {
        btn.classList.add('active');
        btn.innerHTML = '<span class="incognito-icon"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="4"/><path d="M2 20c0-4 4.5-7 10-7s10 3 10 7"/><line x1="3" y1="12" x2="7" y2="12"/><line x1="17" y1="12" x2="21" y2="12"/></svg></span> <span class="incognito-text">Incognito: On</span>';
    } else {
        btn.classList.remove('active');
        btn.innerHTML = '<span class="incognito-icon"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="4"/><path d="M2 20c0-4 4.5-7 10-7s10 3 10 7"/><line x1="3" y1="12" x2="7" y2="12"/><line x1="17" y1="12" x2="21" y2="12"/></svg></span> <span class="incognito-text">Incognito: Off</span>';
    }
}

function toggleSupport() {
    document.getElementById('support-me-content').classList.toggle('hidden');
}

// ── Razorpay Donation ─────────────────────────────────────────────
function donateWithRazorpay() {
    window.open('https://razorpay.me/@imad', '_blank');
}
