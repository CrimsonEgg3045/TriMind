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
            body: JSON.stringify({ query, use_demo: true }),
        });

        if (!response.ok) throw new Error(`Server error: ${response.status}`);
        const data = await response.json();

        removeThinking(thinkingId);
        addAIResponse(data);

    } catch (error) {
        removeThinking(thinkingId);
        addMessage('assistant', `⚠️ **Error:** ${error.message}\n\nPlease check that the server is running and try again.`);
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
    avatar.textContent = role === 'user' ? '👤' : '🧠';

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
    avatar.textContent = '🧠';

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
            caption.textContent = '📊 ' + data.visual_diagram.description;
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
        caption.textContent = '🎨 Generated by Cloudflare Workers AI';

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
    avatar.textContent = '🧠';

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
        { name: '🧠 Explanation', delay: 300 },
        { name: '📐 Math', delay: 800 },
        { name: '🎨 Visual', delay: 1300 },
        { name: '✨ Synthesizer', delay: 3000 },
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
