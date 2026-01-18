/**
 * FAForever Wiki - Editor JavaScript
 */

(function() {
    'use strict';

    let pendingChanges = new Map();
    let saveTimeout = null;

    // Initialize editor functionality
    function initEditor() {
        initToolbar();
        initInlineEditing();
        initAddPlaceholders();
        initSaveButton();
        initModalHandlers();
    }

    // Toolbar button handlers
    function initToolbar() {
        const toolbar = document.getElementById('editorToolbar');
        if (!toolbar) return;

        // Format buttons
        toolbar.querySelectorAll('.editor-btn[data-command]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const command = btn.dataset.command;
                const value = btn.dataset.value;

                // Get active editable element or Quill instance
                const activeQuill = window.activeQuill;
                if (activeQuill) {
                    applyQuillFormat(activeQuill, command, value);
                    btn.classList.toggle('active');
                }
            });
        });

        // Header select
        const headerSelect = document.getElementById('headerSelect');
        if (headerSelect) {
            headerSelect.addEventListener('change', (e) => {
                if (window.activeQuill) {
                    window.activeQuill.format('header', e.target.value ? parseInt(e.target.value) : false);
                }
            });
        }

        // Font select
        const fontSelect = document.getElementById('fontSelect');
        if (fontSelect) {
            fontSelect.addEventListener('change', (e) => {
                if (window.activeQuill) {
                    window.activeQuill.format('font', e.target.value || false);
                }
            });
        }
    }

    // Apply Quill formatting
    function applyQuillFormat(quill, command, value) {
        const format = quill.getFormat();

        switch (command) {
            case 'bold':
                quill.format('bold', !format.bold);
                break;
            case 'italic':
                quill.format('italic', !format.italic);
                break;
            case 'underline':
                quill.format('underline', !format.underline);
                break;
            case 'strike':
                quill.format('strike', !format.strike);
                break;
            case 'list':
                quill.format('list', format.list === value ? false : value);
                break;
            case 'align':
                quill.format('align', value || false);
                break;
            case 'link':
                const url = prompt('Enter URL:', format.link || 'https://');
                if (url !== null) {
                    quill.format('link', url || false);
                }
                break;
        }
    }

    // Inline text editing (contenteditable)
    function initInlineEditing() {
        document.querySelectorAll('.editable-text').forEach(el => {
            el.addEventListener('focus', () => {
                el.dataset.originalContent = el.innerHTML;
            });

            el.addEventListener('blur', () => {
                if (el.innerHTML !== el.dataset.originalContent) {
                    markChanged(el);
                    autoSave();
                }
            });

            el.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    el.blur();
                }
                if (e.key === 'Escape') {
                    el.innerHTML = el.dataset.originalContent;
                    el.blur();
                }
            });
        });
    }

    // Add content placeholders
    function initAddPlaceholders() {
        document.querySelectorAll('.add-content-placeholder').forEach(placeholder => {
            if (placeholder.hasAttribute('hx-get')) return; // HTMX handles this

            placeholder.addEventListener('click', () => {
                const action = placeholder.dataset.action;
                const section = placeholder.dataset.section;

                switch (action) {
                    case 'add-button':
                        showButtonModal(null, section);
                        break;
                    case 'add-text':
                        showTextModal(null, section);
                        break;
                    case 'add-faq':
                        showFAQModal(null, section);
                        break;
                }
            });
        });
    }

    // Save button
    function initSaveButton() {
        const saveBtn = document.getElementById('saveAllBtn');
        if (!saveBtn) return;

        saveBtn.addEventListener('click', async () => {
            await saveAllChanges();
        });
    }

    // Track changes
    function markChanged(element) {
        const id = element.dataset.id || element.closest('[data-id]')?.dataset.id;
        const field = element.dataset.field;

        if (id && field) {
            if (!pendingChanges.has(id)) {
                pendingChanges.set(id, {});
            }
            pendingChanges.get(id)[field] = element.innerHTML;
        }

        updateStatus('unsaved', 'Unsaved changes');
    }

    // Auto-save with debounce
    function autoSave() {
        if (saveTimeout) clearTimeout(saveTimeout);
        saveTimeout = setTimeout(() => {
            saveAllChanges();
        }, 2000);
    }

    // Save all changes
    async function saveAllChanges() {
        if (pendingChanges.size === 0) {
            // Check for Quill editors
            const quillEditors = document.querySelectorAll('[id^="pageEditor"], [id^="rulesEditor"]');
            if (quillEditors.length === 0) {
                updateStatus('saved', 'No changes');
                return;
            }
        }

        updateStatus('saving', 'Saving...');

        try {
            // Save inline changes
            for (const [id, changes] of pendingChanges) {
                const response = await fetch(`/api/content/${id}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(changes)
                });

                if (!response.ok) throw new Error('Save failed');
            }

            pendingChanges.clear();
            updateStatus('saved', 'Saved');

        } catch (error) {
            console.error('Save error:', error);
            updateStatus('error', 'Save failed');
        }
    }

    // Update status indicator
    function updateStatus(status, text) {
        const statusEl = document.getElementById('editorStatus');
        if (!statusEl) return;

        statusEl.className = 'editor-status ' + status;
        statusEl.querySelector('.editor-status-text').textContent = text;

        if (status === 'saved') {
            setTimeout(() => {
                if (statusEl.classList.contains('saved')) {
                    statusEl.className = 'editor-status';
                    statusEl.querySelector('.editor-status-text').textContent = 'Ready';
                }
            }, 3000);
        }
    }

    // Modal handlers
    function initModalHandlers() {
        // Close modal on backdrop click
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('edit-modal-overlay')) {
                closeModal();
            }
        });

        // Close modal on Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                closeModal();
            }
        });

        // Handle modal form submissions
        document.addEventListener('submit', async (e) => {
            const form = e.target.closest('.edit-modal form');
            if (!form) return;

            e.preventDefault();

            const formData = new FormData(form);
            const action = form.action;
            const method = form.method || 'POST';

            try {
                const response = await fetch(action, {
                    method: method,
                    body: formData
                });

                if (response.ok) {
                    closeModal();
                    // Reload page to show changes
                    window.location.reload();
                } else {
                    const error = await response.text();
                    alert('Error: ' + error);
                }
            } catch (err) {
                console.error('Form submit error:', err);
                alert('An error occurred');
            }
        });
    }

    // Close modal
    function closeModal() {
        const modal = document.querySelector('.edit-modal-overlay');
        if (modal) {
            modal.classList.add('fade-out');
            setTimeout(() => modal.remove(), 200);
        }
    }

    // Expose closeModal globally for inline handlers
    window.closeEditModal = closeModal;

    // Show button edit modal
    function showButtonModal(buttonId, section) {
        const modal = document.getElementById('editModal');
        if (!modal) return;

        const url = buttonId
            ? `/api/button/${buttonId}/form`
            : `/api/button/form?section=${section}`;

        htmx.ajax('GET', url, { target: '#editModal', swap: 'innerHTML' });
    }

    // Initialize on load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initEditor);
    } else {
        initEditor();
    }

    // Re-init after HTMX swaps
    document.body.addEventListener('htmx:afterSwap', (e) => {
        if (e.detail.target.id === 'editModal') {
            // Initialize Quill in modal if needed
            const quillContainer = e.detail.target.querySelector('.quill-editor');
            if (quillContainer && window.Quill) {
                const quill = new Quill(quillContainer, {
                    theme: 'snow',
                    modules: {
                        toolbar: [
                            ['bold', 'italic', 'underline'],
                            [{ 'list': 'ordered' }, { 'list': 'bullet' }],
                            ['link']
                        ]
                    }
                });

                // Store content in hidden input on change
                const hiddenInput = e.detail.target.querySelector('input[name="content_html"]');
                if (hiddenInput) {
                    quill.on('text-change', () => {
                        hiddenInput.value = quill.root.innerHTML;
                    });
                }
            }
        }

        initInlineEditing();
        initAddPlaceholders();
    });

})();
