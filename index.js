const messagesContainer = document.getElementById('messagesContainer');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const chatHistory = document.getElementById('chatHistory');

// Auto-ajuste do textarea
userInput.addEventListener('input', function () {
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight) + 'px';
});

// Enviar com Enter (sem Shift)
userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSend();
    }
});

sendBtn.addEventListener('click', handleSend);

async function handleSend() {
    const text = userInput.value.trim();
    if (!text) return;

    // Remove welcome message on first interaction
    const welcome = document.querySelector('.welcome-message');
    if (welcome) welcome.remove();

    // User Message
    addMessage(text, 'user');
    userInput.value = '';
    userInput.style.height = 'auto';

    // AI Typing Status
    const typingId = addTypingIndicator();

    try {
        const response = await fetch('/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question: text })
        });

        const data = await response.json();
        console.log("Hyper Agent Response:", data);
        removeTypingIndicator(typingId);

        if (data.error) {
            addMessage(`Erro: ${data.error}`, 'ai', true);
        } else {
            addAiResponse(data);
        }
    } catch (error) {
        removeTypingIndicator(typingId);
        addMessage('Houve um erro ao conectar com o agente. Verifique sua conexão.', 'ai', true);
        console.error(error);
    }
}

function addMessage(text, side, isError = false) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${side}`;

    msgDiv.innerHTML = `
        <div class="message-bubble ${isError ? 'error' : ''}">
            ${text}
        </div>
    `;

    messagesContainer.appendChild(msgDiv);
    scrollToBottom();
}

function addAiResponse(data) {
    const msgDiv = document.createElement('div');
    msgDiv.className = 'message ai';

    const confidence = data.confidence ? (data.confidence * 100).toFixed(0) : 0;
    const badgeClass = confidence > 70 ? 'badge-success' : 'badge-warning';

    let html = `
        <div class="message-bubble">
            <div class="msg-header">
                <strong>Hyper Agent</strong>
                <span class="badge ${badgeClass}">${confidence}% Confiança</span>
            </div>
            <p>De acordo com os dados no Firebird:</p>
            <div class="sql-container">
                <code>${data.sql || '-- Nenhum SQL gerado'}</code>
            </div>
    `;

    if (data.warnings && data.warnings.length > 0) {
        html += `<div class="warnings">⚠️ <em>${data.warnings[0]}</em></div>`;
    }

    if (data.results && data.results.length > 0) {
        html += `<div class="results-table-container"><table><thead><tr>`;
        data.columns.forEach(col => html += `<th>${col}</th>`);
        html += `</tr></thead><tbody>`;
        data.results.forEach(row => {
            html += `<tr>`;
            data.columns.forEach(col => html += `<td>${row[col] === null ? '-' : row[col]}</td>`);
            html += `</tr>`;
        });
        html += `</tbody></table></div>`;
    } else if (data.results && data.results.length === 0 && data.state === 'OK') {
        html += `<div class="note">A consulta foi executada, mas não retornou registros.</div>`;
    }

    if (data.note) {
        html += `<div class="note">ℹ️ ${data.note}</div>`;
    }
    if (data.execution_error) {
        html += `<div class="error-msg">❌ Erro na execução: ${data.execution_error}</div>`;
    }

    html += `</div>`;
    msgDiv.innerHTML = html;

    messagesContainer.appendChild(msgDiv);

    // Add to history
    addToHistory(data.question);
    scrollToBottom();
}

function addTypingIndicator() {
    const id = 'typing-' + Date.now();
    const msgDiv = document.createElement('div');
    msgDiv.className = 'message ai';
    msgDiv.id = id;
    msgDiv.innerHTML = `
        <div class="message-bubble">
            <div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        </div>
    `;
    messagesContainer.appendChild(msgDiv);
    scrollToBottom();
    return id;
}

function removeTypingIndicator(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

function scrollToBottom() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function addToHistory(question) {
    const item = document.createElement('div');
    item.className = 'history-item';
    item.style.padding = '8px';
    item.style.fontSize = '0.9rem';
    item.style.cursor = 'pointer';
    item.style.color = '#94a3b8';
    item.style.whiteSpace = 'nowrap';
    item.style.overflow = 'hidden';
    item.style.textOverflow = 'ellipsis';
    item.innerText = question;

    chatHistory.prepend(item);
}
