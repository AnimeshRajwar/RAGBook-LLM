// --- FLASH MESSAGE AUTO-HIDE ---
document.addEventListener('DOMContentLoaded', function() {
    const flashes = document.querySelectorAll('.flash-messages .flash');
    flashes.forEach(flash => {
        setTimeout(() => {
            flash.classList.add('flash-hide');
        }, 2500);
        // Optional: remove from DOM after animation
        flash.addEventListener('transitionend', function() {
            if (flash.classList.contains('flash-hide')) {
                flash.remove();
            }
        });
    });
});
async function uploadFiles() {
    const fileInput = document.getElementById('fileInput');
    const statusMsg = document.getElementById('statusMsg');
    const uploadBtn = document.getElementById('uploadBtn');
    if (fileInput.files.length === 0) return alert("Please select files first.");

    const formData = new FormData();
    for (const file of fileInput.files) {
        formData.append('files', file);
    }

    // UI: disable button and show spinner
    uploadBtn.disabled = true;
    statusMsg.innerHTML = '<span class="spinner"></span> Uploading & indexing...';
    try{
        const res = await fetch('/upload', { method: 'POST', body: formData });
        const data = await res.json();

        if (data.error) {
            statusMsg.innerText = data.error;
        } else {
            statusMsg.innerText = data.message || 'Upload complete.';
            // populate file list from selected files
            addFilesToList(Array.from(fileInput.files));
            fileInput.value = null;
            // clear selected preview
            const preview = document.getElementById('selectedPreview');
            if(preview) preview.innerHTML = '';
        }
    }catch(err){
        console.error(err);
        statusMsg.innerText = 'Upload failed. See console for details.';
    }finally{
        uploadBtn.disabled = false;
    }
}

// Show selected files preview when user picks files (before upload)
function updateSelectedPreview(fileList){
    const preview = document.getElementById('selectedPreview');
    if(!preview) return;
    if(!fileList || fileList.length === 0){
        preview.innerHTML = '<span class="meta">No file selected</span>';
        return;
    }

    // show first 3 names and count
    const names = Array.from(fileList).map(f => f.name);
    const visible = names.slice(0,3).join(', ');
    const more = names.length > 3 ? ` + ${names.length-3} more` : '';

    // Use an HTML entity for the close glyph so tooling that parses files as ASCII-safe
    // (or gets accidentally passed to Python) won't raise a Unicode syntax error.
    preview.innerHTML = `<span class="meta">Selected: ${visible}${more}</span> <button class="clear-btn" onclick="clearSelection()">&#x2716;</button>`;
}

function clearSelection(){
    const fileInput = document.getElementById('fileInput');
    const preview = document.getElementById('selectedPreview');
    if(fileInput) fileInput.value = null;
    if(preview) preview.innerHTML = '<span class="meta">No file selected</span>';
}

// Attach change listener to update preview immediately
document.addEventListener('DOMContentLoaded', ()=>{
    // Clear the application context on every page load (uploads, outputs, vector DB, and chat)
    clearContextOnLoad();
    // Fetch and display user's previously uploaded files
    fetch('/user_files')
        .then(res => res.json())
        .then(data => {
            if (data.files && Array.isArray(data.files)) {
                // Convert to File-like objects for addFilesToList
                const files = data.files.map(f => ({ name: f.name }));
                addFilesToList(files);
            }
        });

    const fileInput = document.getElementById('fileInput');
    if(fileInput){
        fileInput.addEventListener('change', (e)=>{
            updateSelectedPreview(e.target.files);
        });
    }
    // initialize preview area with a helpful message
    const initialPreview = document.getElementById('selectedPreview');
    if(initialPreview && (!initialPreview.innerHTML || initialPreview.innerText.trim() === '')){
        initialPreview.innerHTML = '<span class="meta">No file selected</span>';
    }
    // Close mobile menu on resize to large screens
    window.addEventListener('resize', ()=>{
        if(window.innerWidth > 900 && document.body.classList.contains('mobile-menu-open')){
            document.body.classList.remove('mobile-menu-open');
        }
    });
});

// Mobile menu toggles
function toggleMobileMenu(){
    document.body.classList.toggle('mobile-menu-open');
}
function closeMobileMenu(){
    document.body.classList.remove('mobile-menu-open');
}

// Close mobile menu on Escape key
document.addEventListener('keydown', (e)=>{
    if(e.key === 'Escape' && document.body.classList.contains('mobile-menu-open')){
        closeMobileMenu();
    }
});

async function clearStorageButKeepChat(){
    try{
        await fetch('/clear_storage', { method: 'POST' });
        // clear UI lists but NOT chat history
        const fileList = document.getElementById('fileList');
        if (fileList) fileList.innerHTML = '';
        const status = document.getElementById('statusMsg');
        if (status) status.innerText = '';
        // Keep chat history intact
    }catch(e){
        console.warn('clearStorage failed', e);
    }
}

async function clearContextOnLoad(){
    try{
        await fetch('/clear_context', { method: 'POST' });
        // clear UI lists and chat history
        const fileList = document.getElementById('fileList');
        if (fileList) fileList.innerHTML = '';
        const status = document.getElementById('statusMsg');
        if (status) status.innerText = '';
        const history = document.getElementById('chatHistory');
        if (history) {
            // Re-insert the concise welcome message after clearing context so the UI isn't empty.
            history.innerHTML = '<div class="message bot">Welcome - Upload your sources then ask Questions</div>';
        }
        // reset preview area
        const preview = document.getElementById('selectedPreview');
        if(preview) preview.innerHTML = '<span class="meta">No file selected</span>';
    }catch(e){
        console.warn('clearContext failed', e);
    }
}

async function clearStorage(){
    try{
        await fetch('/clear_storage', { method: 'POST' });
        // clear UI lists
        const fileList = document.getElementById('fileList');
        if (fileList) fileList.innerHTML = '';
        const status = document.getElementById('statusMsg');
        if (status) status.innerText = '';
    }catch(e){
        console.warn('clearStorage failed', e);
    }
}

async function sendQuery() {
    const queryBox = document.getElementById('userQuery');
    const query = queryBox.value;
    if (!query) return;
    
    // Add user message and keep it visible
    addMessage(query, 'user');
    queryBox.value = '';
    
    // Scroll to ensure user message is visible
    const history = document.getElementById('chatHistory');
    if (history) history.scrollTop = history.scrollHeight;

    // Show loading
    const loadingId = addMessage("Thinking...", 'bot');

    try{
        const res = await fetch('/query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: query })
        });
        const data = await res.json();

        // Remove loading message
        const loadingEl = document.getElementById(loadingId);
        if (loadingEl) loadingEl.remove();

        if (data.error) {
            addMessage('Error: ' + data.error, 'bot');
        } else if (data.file_url) {
            // show answer and present inline options to Preview/Download/Play
            const msgId = addMessage(data.answer, 'bot');
            // append file action buttons into the message bubble
            const msgEl = document.getElementById(msgId);
            if (msgEl) {
                    const actions = createFileActions(data.file_url, data.download_url);
                    msgEl.appendChild(actions);
                }
        } else {
            // Add bot response and ensure it stays visible
            addMessage(data.answer, 'bot');
        }
        
        // Ensure scroll is at bottom
        if (history) history.scrollTop = history.scrollHeight;
    }catch(err){
        console.error(err);
        const loadingEl = document.getElementById(loadingId);
        if (loadingEl) loadingEl.remove();
        addMessage('Request failed. Check console for details.', 'bot');
    }
}

// Create a small actions bar for a file returned by the server
function createFileActions(previewRel, downloadRel){
    const origin = window.location.origin;
    const previewFull = origin + previewRel;
    const downloadFull = downloadRel ? origin + downloadRel : previewFull;
    const extMatch = previewRel.match(/\.([a-z0-9]+)(?:\?.*)?$|$/i);
    const ext = (extMatch && extMatch[1]) ? extMatch[1].toLowerCase() : '';

    const wrapper = document.createElement('div');
    wrapper.className = 'file-actions';
    // Preview / Play button
    const previewBtn = document.createElement('button');
    previewBtn.type = 'button';
    previewBtn.className = 'btn preview-btn';
    previewBtn.textContent = (['mp3','wav','m4a','ogg'].includes(ext)) ? 'Play' : 'Preview';
    // For audio files, toggle an inline audio player inside the chat message
    if (['mp3','wav','m4a','ogg'].includes(ext)) {
        previewBtn.onclick = (e) => {
            e.preventDefault();
            toggleInlineAudio(previewRel, previewBtn);
        };
    } else if (['pptx','ppt'].includes(ext)) {
        // For PPTX, open a PDF-based preview modal using the server-side preview endpoint
        previewBtn.onclick = () => openPdfPreview(previewRel, downloadRel);
    } else {
        previewBtn.onclick = () => openPreview(previewRel, downloadRel);
    }

    // Download link
    const dl = document.createElement('a');
    dl.className = 'btn download-link';
    dl.href = downloadFull;
    dl.target = '_blank';
    // Force a sensible filename for the download attribute so browsers save with the correct name
    try {
        const dlName = decodeURIComponent((downloadFull.split('/').pop() || '').split('?')[0]);
        if (dlName) dl.setAttribute('download', dlName);
        else dl.setAttribute('download', 'download');
    } catch (e) {
        dl.setAttribute('download', 'download');
    }
    dl.textContent = 'Download';

    wrapper.appendChild(previewBtn);
    wrapper.appendChild(dl);
    return wrapper;
}

// Open a dedicated PDF preview modal for a PPTX by calling the server /preview endpoint.
async function openPdfPreview(previewRel, downloadRel){
    const modal = document.getElementById('previewModal');
    const content = document.getElementById('previewContent');
    const download = document.getElementById('previewDownload');
    content.innerHTML = '';

    // Compute preview endpoint (server will redirect to PDF or HTML)
    const parts = previewRel.split('/');
    const fname = decodeURIComponent(parts[parts.length - 1]);
    const previewEndpoint = '/preview/' + fname;

    // Set download link
    const downloadFull = downloadRel ? (window.location.origin + downloadRel) : (window.location.origin + '/static/outputs/' + fname);
    try{
        const modalName = decodeURIComponent((downloadFull.split('/').pop() || '').split('?')[0]);
        if (modalName) download.setAttribute('download', modalName);
        else download.setAttribute('download', 'download');
    }catch(e){ download.setAttribute('download','download'); }

    // show spinner while fetching preview
    const spinner = document.createElement('div');
    spinner.className = 'spinner';
    content.appendChild(spinner);

    try{
        const res = await fetch(previewEndpoint, { method: 'GET', redirect: 'follow' });
        // Use the final resolved URL for embedding
        const finalUrl = res.url || previewEndpoint;
        content.innerHTML = '';
        // If the final URL ends with .pdf, use embed for better PDF display
        if (finalUrl.toLowerCase().endsWith('.pdf')){
            const embed = document.createElement('embed');
            embed.src = finalUrl;
            embed.type = 'application/pdf';
            embed.style.width = '100%';
            embed.style.height = '100%';
            embed.setAttribute('aria-label','Presentation PDF preview');
            content.appendChild(embed);
        } else {
            // fallback to iframe (HTML preview or other)
            const iframe = document.createElement('iframe');
            iframe.src = finalUrl;
            iframe.style.width = '100%';
            iframe.style.height = '100%';
            iframe.frameBorder = 0;
            content.appendChild(iframe);
        }
    }catch(err){
        content.innerHTML = `<div><p>Preview failed. Try downloading the file instead.</p><pre>${String(err)}</pre></div>`;
    }
    modal.setAttribute('aria-hidden','false');
}

// Toggle an inline audio player in the parent chat message of the provided button
function toggleInlineAudio(relUrl, btn) {
    const origin = window.location.origin;
    const fullUrl = origin + relUrl;
    const msg = btn.closest('.message');
    if(!msg) return;

    // Look for an existing inline audio for this URL
    const existing = msg.querySelector(`audio.inline-audio[data-src="${fullUrl}"]`);

    // If there is an existing audio for this URL, toggle play/pause
    if (existing) {
        if (!existing.paused) {
            existing.pause();
            // leave the audio element in place but update button text
            btn.textContent = 'Play';
        } else {
            existing.play().catch(()=>{});
            btn.textContent = 'Pause';
        }
        return;
    }

    // Remove any other inline audio players in this message (only one at a time)
    const others = msg.querySelectorAll('audio.inline-audio');
    others.forEach(o => {
        const linked = o.getAttribute('data-linked-btn');
        if (linked) {
            const linkedBtn = document.getElementById(linked);
            if (linkedBtn) linkedBtn.textContent = 'Play';
        }
        o.remove();
    });

    // Ensure the button has an id so we can link it to the audio
    if (!btn.id) btn.id = 'btn-' + Date.now();

    // Create and append the audio element
    const audio = document.createElement('audio');
    audio.controls = true;
    audio.className = 'inline-audio';
    audio.setAttribute('data-src', fullUrl);
    audio.setAttribute('data-linked-btn', btn.id);
    audio.src = fullUrl;
    // Insert audio after the actions bar if present, otherwise at end
    const actions = btn.closest('.file-actions');
    if (actions && actions.parentNode) {
        actions.parentNode.insertBefore(audio, actions.nextSibling);
    } else {
        msg.appendChild(audio);
    }
    // hook up events to sync button text
    audio.addEventListener('play', () => { btn.textContent = 'Pause'; });
    audio.addEventListener('pause', () => { btn.textContent = 'Play'; });
    audio.addEventListener('ended', () => { btn.textContent = 'Play'; audio.remove(); });

    // play (may be blocked, but we'll try)
    audio.play().catch(()=>{});
}

async function openPreview(relUrl, downloadRel=null){
    // relUrl is expected to be a relative path like /static/outputs/filename
    const origin = window.location.origin;
    const previewFull = origin + relUrl;
    const downloadFull = downloadRel ? origin + downloadRel : previewFull;
    // Extract extension robustly (handles query strings and no-extension paths)
    const extMatch = relUrl.match(/\.([a-z0-9]+)(?:\?.*)?$|$/i);
    let ext = (extMatch && extMatch[1]) ? extMatch[1].toLowerCase() : '';

    const modal = document.getElementById('previewModal');
    const content = document.getElementById('previewContent');
    const download = document.getElementById('previewDownload');
    content.innerHTML = '';
    download.href = downloadFull;
    // Set a clear filename for the modal download button as well
    try {
        const modalName = decodeURIComponent((downloadFull.split('/').pop() || '').split('?')[0]);
        if (modalName) download.setAttribute('download', modalName);
        else download.setAttribute('download', 'download');
    } catch (e) {
        download.setAttribute('download', 'download');
    }

    // (source note removed — preview should be shown without an extra source line)

    // If extension is missing or unknown, probe the resource headers to detect content-type
    if (!ext) {
        // show spinner while probing
        const spinner = document.createElement('div');
        spinner.className = 'spinner';
        content.appendChild(spinner);
        try {
            const res = await fetch(previewFull, { method: 'HEAD' });
            const ctype = res.headers.get('content-type') || '';
            if (ctype.includes('pdf')) ext = 'pdf';
            else if (ctype.startsWith('audio/')) ext = 'mp3';
            else if (ctype.includes('html')) ext = 'html';
            else if (ctype.includes('presentation') || ctype.includes('powerpoint') || ctype.includes('officedocument')) ext = 'pptx';
        } catch (e) {
            // ignore and fall back to unknown
        } finally {
            content.innerHTML = '';
        }
    }

    // After detection, render appropriate viewer
    if(['mp3','wav','m4a','ogg'].includes(ext) || ext === 'mp3'){
        // audio player
        const audio = document.createElement('audio');
        audio.controls = true;
        audio.src = previewFull;
    content.appendChild(audio);
    } else if(['pptx','ppt'].includes(ext)){
        // For local PPTX previews, request the server-side preview endpoint which will
        // convert to PDF or HTML when possible and redirect to a previewable file.
        const embed = document.createElement('iframe');
        // Compute basename and call preview endpoint
        const parts = relUrl.split('/');
        const fname = decodeURIComponent(parts[parts.length - 1]);
        const previewEndpoint = '/preview/' + fname;
        embed.src = previewEndpoint;
    content.appendChild(embed);
    } else if(['pdf'].includes(ext)){
        const embed = document.createElement('iframe');
        embed.src = previewFull;
    content.appendChild(embed);
    } else if(ext === 'html'){
        // simple HTML preview (fallback created server-side)
        const embed = document.createElement('iframe');
        embed.src = previewFull;
        content.appendChild(embed);
        if (sourceNote.textContent) content.prepend(sourceNote);
    } else {
        // fallback: provide download link + message
        const p = document.createElement('div');
        const extLabel = ext ? `.${ext}` : '(unknown type)';
        p.innerHTML = `<p>Preview not available for ${extLabel}. You can download the file below.</p>`;
        
        content.appendChild(p);
    }

    modal.setAttribute('aria-hidden','false');
}

function closePreview(){
    const modal = document.getElementById('previewModal');
    const content = document.getElementById('previewContent');
    modal.setAttribute('aria-hidden','true');
    content.innerHTML = '';
}

function sendSpecial(text) {
    document.getElementById('userQuery').value = text;
    sendQuery();
}

function addMessage(text, sender) {
    const history = document.getElementById('chatHistory');
    const div = document.createElement('div');
    div.classList.add('message', sender);
    div.id = 'msg-' + Date.now();
    
    // Convert markdown formatting to HTML
    let formattedText = String(text);
    // Handle **bold** markdown
    formattedText = formattedText.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    // Handle *italic* markdown
    formattedText = formattedText.replace(/\*([^*]+)\*/g, '<em>$1</em>');
    // Handle newlines
    formattedText = formattedText.replace(/\n/g, '<br>');
    // Handle bullet points and numbered lists
    formattedText = formattedText.replace(/^(\d+)\.\s+/gm, '<strong>$1.</strong> ');
    // Preserve leading * for plain text bullets (do not convert to HTML bullet, just keep as-is)
    // No replacement for ^\*\s+ so that * is preserved in plain text
    div.innerHTML = formattedText;
    history.appendChild(div);
    history.scrollTop = history.scrollHeight;
    
    // If this is a bot message that contains markdown-style links to generated files,
    // automatically append inline Preview/Download actions.
    if (sender === 'bot' && typeof text === 'string') {
        try {
            const linkRe = /\[([^\]]+)\]\(([^)]+)\)/g;
            let m;
            const groups = {}; // base -> {pdf:rel, pptx:rel, audio:rel}
            while ((m = linkRe.exec(text)) !== null) {
                const linkText = m[1];
                let url = m[2];
                // Normalize relative filenames to static outputs path
                if (!url.startsWith('http') && !url.startsWith('/')) {
                    // assume it's a filename in outputs
                    url = '/static/outputs/' + encodeURIComponent(url);
                }
                // extract filename and ext
                const parts = url.split('/');
                const fname = parts[parts.length - 1];
                const extMatch = fname.match(/\.([a-z0-9]+)(?:\?.*)?$/i);
                const ext = extMatch ? extMatch[1].toLowerCase() : '';
                const base = fname.replace(/(\.[^/.]+)$/,'');
                if (!groups[base]) groups[base] = {};
                if (ext === 'pdf') groups[base].pdf = url;
                else if (ext === 'pptx' || ext === 'ppt') groups[base].pptx = url;
                else if (ext === 'mp3' || ext === 'wav' || ext === 'm4a' || ext === 'ogg') groups[base].audio = url;
                else if (ext === 'html') groups[base].html = url;
            }

            // For each detected group, create actions and append to message
            for (const base in groups) {
                const g = groups[base];
                let previewRel = null;
                let downloadRel = null;
                if (g.pdf && g.pptx) {
                    previewRel = g.pdf;
                    downloadRel = g.pptx;
                } else if (g.pdf && !g.pptx) {
                    previewRel = g.pdf;
                    downloadRel = g.pdf;
                } else if (g.pptx) {
                    previewRel = g.pptx;
                    downloadRel = g.pptx;
                } else if (g.html) {
                    previewRel = g.html;
                    downloadRel = g.html;
                } else if (g.audio) {
                    previewRel = g.audio;
                    downloadRel = g.audio;
                }
                if (previewRel) {
                    // create actions and append
                    const acts = createFileActions(previewRel, downloadRel);
                    div.appendChild(acts);
                }
            }
        } catch (e) {
            console.error('Failed to parse links in bot message:', e);
        }
    }
    return div.id;
}

// Add files to sidebar list
function addFilesToList(files){
    const list = document.getElementById('fileList');
    for(const f of files){
        const li = document.createElement('li');
        li.dataset.filename = f.name;
        // Always show plain text for file name, no preview
        const nameSpan = document.createElement('span');
        nameSpan.className = 'file-link-disabled';
        nameSpan.textContent = f.name;
        // Add Unicode trash emoji button
        const delBtn = document.createElement('button');
        delBtn.className = 'dustbin-btn';
        delBtn.innerHTML = '🗑️';
        delBtn.setAttribute('aria-label', 'Delete file and embeddings');
        delBtn.onclick = () => deleteFile(f.name);
        li.appendChild(nameSpan);
        li.appendChild(delBtn);
        list.prepend(li);
    }
// Delete file and its embeddings
async function deleteFile(filename) {
    if (!confirm(`Delete ${filename}? This will also remove its embeddings from the cloud.`)) return;
    try {
        const res = await fetch('/delete_file', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filename })
        });
        const data = await res.json();
        if (data.status === 'deleted') {
            removeFileFromList(filename);
            showFlash('File deleted successfully.', 'success');
        } else {
            showFlash(data.error || 'Delete failed.', 'danger');
        }
    } catch (e) {
        showFlash('Delete failed. See console.', 'danger');
        console.error(e);
    }
}

function removeFileFromList(filename) {
    const fileList = document.getElementById('fileList');
    if (!fileList) return;
    const items = fileList.querySelectorAll('li');
    items.forEach(item => {
        if (item.dataset.filename === filename) {
            item.remove();
        }
    });
}

function showFlash(msg, type) {
    const container = document.querySelector('.flash-messages');
    if (!container) return;
    const div = document.createElement('div');
    div.className = `flash flash-${type}`;
    div.textContent = msg;
    container.appendChild(div);
    setTimeout(() => div.classList.add('flash-hide'), 2500);
    div.addEventListener('transitionend', () => div.remove());
}
}

// Keyboard shortcut: Ctrl+Enter to send
document.addEventListener('keydown', (e) => {
    const el = document.activeElement;
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
        if (el && el.id === 'userQuery') {
            e.preventDefault();
            sendQuery();
        }
    }
});