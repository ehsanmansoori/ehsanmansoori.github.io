/**
 * Ehsan Mansoori portal
 * Client-side search + program filter over the statically rendered archive.
 * Cards already exist in the HTML (good for SEO and no-JS); this only shows/hides.
 */
(function () {
    'use strict';

    const grid = document.getElementById('filmsGrid');
    if (!grid) return;

    const searchInput = document.getElementById('filmSearch');
    const countLabel = document.getElementById('searchCount');
    const emptyState = document.getElementById('emptyState');
    const chips = Array.from(document.querySelectorAll('.filter-chip'));
    const cards = Array.from(grid.querySelectorAll('.film-card'));

    let activeGroup = 'all';

    const norm = (s) =>
        (s || '')
            .toLowerCase()
            .replace(/[\u064A\u06CC]/g, 'ی')
            .replace(/[\u0643\u06A9]/g, 'ک')
            .replace(/[\u200c\u200f\u200e]/g, '')
            .replace(/\s+/g, ' ')
            .trim();

    const indexed = cards.map((el) => ({
        el,
        group: el.dataset.group || 'all',
        name: norm(el.dataset.name || el.textContent)
    }));

    function apply() {
        const q = norm(searchInput ? searchInput.value : '');
        let shown = 0;

        indexed.forEach((item) => {
            const groupOk = activeGroup === 'all' || item.group === activeGroup;
            const queryOk = !q || item.name.includes(q);
            const visible = groupOk && queryOk;
            item.el.hidden = !visible;
            if (visible) shown += 1;
        });

        if (countLabel) {
            countLabel.textContent = shown === indexed.length
                ? indexed.length.toLocaleString('fa-IR') + ' فیلم'
                : shown.toLocaleString('fa-IR') + ' از ' + indexed.length.toLocaleString('fa-IR') + ' فیلم';
        }
        if (emptyState) emptyState.hidden = shown !== 0;
    }

    chips.forEach((chip) => {
        chip.addEventListener('click', () => {
            chips.forEach((c) => c.classList.remove('active'));
            chip.classList.add('active');
            activeGroup = chip.dataset.group || 'all';
            apply();
        });
    });

    if (searchInput) {
        let timer;
        searchInput.addEventListener('input', () => {
            clearTimeout(timer);
            timer = setTimeout(apply, 90);
        });
    }

    // in-page navigation that accounts for the sticky header height
    document.querySelectorAll('a[href^="#"]').forEach((link) => {
        link.addEventListener('click', (e) => {
            const id = link.getAttribute('href');
            if (!id || id === '#') return;
            const target = document.querySelector(id);
            if (!target) return;
            e.preventDefault();
            const top = target.getBoundingClientRect().top + window.pageYOffset - 78;
            window.scrollTo({ top, behavior: 'smooth' });
        });
    });

    apply();
})();
