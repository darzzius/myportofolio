(() => {
    'use strict';

    const UUID_PLACEHOLDER = '00000000-0000-0000-0000-000000000000';
    const escapeHtml = value => String(value ?? '').replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;').replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;').replaceAll("'", '&#39;');

    function csrfToken() {
        const cookie = document.cookie.split(';').map(value => value.trim())
            .find(value => value.startsWith('csrftoken='));
        return cookie ? decodeURIComponent(cookie.slice('csrftoken='.length)) : '';
    }

    function errorMessage(data) {
        if (typeof data === 'string') return data;
        if (Array.isArray(data)) return data.map(errorMessage).join(' ');
        if (data && typeof data === 'object') {
            return Object.entries(data).map(([key, value]) =>
                `${key === 'detail' || key === 'non_field_errors' ? '' : `${key}: `}${errorMessage(value)}`
            ).join(' ');
        }
        return '';
    }

    // datetime-local displays local time; the API receives an ISO date with a timezone.
    function localDateTime(value) {
        if (!value) return '';
        const date = new Date(value);
        const pad = number => String(number).padStart(2, '0');
        return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`
            + `T${pad(date.getHours())}:${pad(date.getMinutes())}`;
    }

    document.querySelectorAll('[data-portfolio-section]').forEach(section => {
        const config = section.dataset;
        const isEducation = config.portfolioSection === 'education';
        const isOwner = config.isOwner === 'true';
        const canEdit = isOwner || config.isEditor === 'true';
        const isAuthenticated = config.isAuthenticated === 'true';
        const results = section.querySelector('[data-results]');
        const searchForm = section.querySelector('[data-search-form]');
        const searchInput = section.querySelector('[data-search-input]');
        const form = section.querySelector('[data-portfolio-form]');
        const modal = section.querySelector('[data-form-modal]');
        const records = new Map();
        const pendingIds = new Set();
        let editingId = null;
        let controller;
        let searchTimer;

        const endpoint = (pattern, id) => pattern.replace(UUID_PLACEHOLDER, encodeURIComponent(id));

        function showState(state) {
            section.querySelectorAll('[data-state]').forEach(element => {
                element.classList.toggle('hide', element.dataset.state !== state);
            });
            results.classList.toggle('hide', state !== 'results');
            section.setAttribute('aria-busy', String(state === 'loading'));
        }

        async function request(url, { method = 'GET', payload, signal } = {}) {
            const headers = { Accept: 'application/json' };
            if (method !== 'GET') {
                headers['X-CSRFToken'] = csrfToken();
                headers['Content-Type'] = 'application/json';
            }
            const response = await fetch(url, {
                method, headers, signal, credentials: 'same-origin',
                body: payload === undefined ? undefined : JSON.stringify(payload),
            });
            if (response.status === 204) return null;
            const data = await response.json().catch(() => ({}));
            if (!response.ok) {
                throw new Error(errorMessage(data) || `Permintaan gagal (HTTP ${response.status}).`);
            }
            return data;
        }

        function card(item) {
            const id = escapeHtml(item.id);
            const title = isEducation ? item.institution : item.title;
            const subtitle = isEducation
                ? `${item.degree} \u2022 ${item.start_year} \u2014 ${item.end_year}`
                : item.category_display;
            const starTitle = item.starred_by_names
                ? `Dibintangi oleh ${item.starred_by_names}` : 'Jadilah yang pertama memberi star';
            const stars = isAuthenticated
                ? `<button type="button" class="button button-star${item.is_starred ? ' is-starred' : ''}"
                     data-action="star" data-id="${id}" aria-pressed="${Boolean(item.is_starred)}"
                     title="${escapeHtml(starTitle)}">
                     <span aria-hidden="true">&#9733;</span> ${item.is_starred ? 'Unstar' : 'Star'}
                     <span class="star-count">${escapeHtml(item.star_count)}</span></button>`
                : `<a href="${escapeHtml(config.loginUrl)}" class="button button-star">
                     Login untuk star (${escapeHtml(item.star_count)})</a>`;
            const edit = canEdit
                ? `<button type="button" class="button button-secondary" data-action="edit" data-id="${id}">Edit</button>` : '';
            const remove = isOwner
                ? `<button type="button" class="button button-danger" data-action="delete" data-id="${id}">Hapus</button>` : '';
            const ended = !isEducation && !item.is_ongoing && item.ended_at
                ? new Intl.DateTimeFormat('id-ID', { month: 'short', year: 'numeric' }).format(new Date(item.ended_at)) : '';
            const status = isEducation ? '' : `<p class="${item.is_ongoing ? 'status-text-ongoing' : 'status-text-completed'}">
                ${item.is_ongoing ? 'Masih berlangsung' : `Selesai ${escapeHtml(ended)}`}</p>`;
            const article = document.createElement('article');
            article.className = 'experience-card';
            article.innerHTML = `<h2 class="experience-title">${escapeHtml(title)}</h2>
                <p class="${isEducation ? 'edu-sub' : 'experience-category'}">${escapeHtml(subtitle)}</p>
                <p class="experience-description">${escapeHtml(item.description)}</p>${status}
                <div class="project-card-actions"><div class="project-actions">${stars}${edit}${remove}</div></div>`;
            if (!isEducation) return article;
            const wrapper = document.createElement('div');
            wrapper.className = 'timeline-item';
            const dot = document.createElement('div');
            dot.className = 'timeline-dot';
            wrapper.append(dot, article);
            return wrapper;
        }

        async function loadRecords() {
            if (controller) controller.abort();
            controller = new AbortController();
            showState('loading');
            const url = new URL(config.listUrl, window.location.origin);
            const query = searchInput.value.trim();
            if (query) url.searchParams.set('q', query);
            try {
                const items = await request(url, { signal: controller.signal });
                records.clear();
                items.forEach(item => records.set(item.id, item));
                results.replaceChildren(...items.map(card));
                showState(items.length ? 'results' : 'empty');
            } catch (error) {
                if (error.name === 'AbortError') return;
                showState('error');
                showToast('Gagal memuat data', error.message, 'error');
            }
        }

        function openForm(item = null) {
            if (!form || form.querySelector('[data-save]').disabled) return;
            editingId = item?.id ?? null;
            form.reset();
            if (item) {
                Array.from(form.elements).forEach(field => {
                    if (Object.hasOwn(item, field.name)) {
                        field.value = field.type === 'datetime-local'
                            ? localDateTime(item[field.name]) : item[field.name] ?? '';
                    }
                });
            }
            section.querySelector('[data-form-title]').textContent =
                `${item ? 'Edit' : 'Tambah'} ${config.itemLabel}`;
            form.querySelector('[data-save]').textContent = item ? 'Simpan perubahan' : 'Tambah';
            modal.showPopover();
            form.querySelector('input:not([type="hidden"]), select, textarea')?.focus();
        }

        section.querySelector('[data-create]')?.addEventListener('click', () => openForm());
        form?.addEventListener('submit', async event => {
            event.preventDefault();
            const submit = form.querySelector('[data-save]');
            if (submit.disabled) return;
            submit.disabled = true;
            const payload = Object.fromEntries(new FormData(form));
            delete payload.csrfmiddlewaretoken;
            if (Object.hasOwn(payload, 'ended_at')) {
                payload.ended_at = payload.ended_at ? new Date(payload.ended_at).toISOString() : null;
            }
            try {
                await request(editingId ? endpoint(config.detailUrl, editingId) : config.listUrl, {
                    method: editingId ? 'PATCH' : 'POST', payload,
                });
                modal.hidePopover();
                form.reset();
                showToast('Berhasil', `Data ${config.itemLabel} berhasil disimpan.`, 'success');
                await loadRecords();
            } catch (error) {
                showToast('Gagal menyimpan data', error.message, 'error');
            } finally {
                submit.disabled = false;
            }
        });

        results.addEventListener('click', async event => {
            const button = event.target.closest('button[data-action]');
            if (!button || button.disabled || pendingIds.has(button.dataset.id)) return;
            const { action, id } = button.dataset;
            if (action === 'edit') {
                openForm(records.get(id));
                return;
            }
            if (action === 'delete' && !window.confirm(`Hapus data ${config.itemLabel} ini?`)) return;
            button.disabled = true;
            pendingIds.add(id);
            try {
                await request(endpoint(action === 'star' ? config.starUrl : config.detailUrl, id), {
                    method: action === 'star' ? 'POST' : 'DELETE',
                });
                showToast('Berhasil', action === 'star' ? 'Star berhasil diperbarui.' : 'Data berhasil dihapus.', 'success');
                await loadRecords();
            } catch (error) {
                showToast('Permintaan ditolak atau gagal', error.message, 'error');
            } finally {
                button.disabled = false;
                pendingIds.delete(id);
            }
        });

        searchInput.addEventListener('input', () => {
            clearTimeout(searchTimer);
            searchTimer = setTimeout(loadRecords, 300);
        });
        searchForm.addEventListener('submit', event => {
            event.preventDefault();
            clearTimeout(searchTimer);
            loadRecords();
        });
        section.querySelector('[data-retry]').addEventListener('click', loadRecords);
        loadRecords();
    });
})();
