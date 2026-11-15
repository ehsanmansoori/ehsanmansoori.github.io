/**
 * Ehsan Mansoori portal
 * Film library: bucket tabs, search, genre/country/decade filters and sorting.
 * All cards are rendered in the HTML already (SEO + no-JS safe); this only
 * shows/hides and reorders them.
 */
(function () {
    'use strict';

    const grid = document.getElementById('libGrid');
    if (!grid) return;

    const tabs = Array.from(document.querySelectorAll('.lib-tab'));
    const searchInput = document.getElementById('libSearch');
    const genreSel = document.getElementById('libGenre');
    const countrySel = document.getElementById('libCountry');
    const decadeSel = document.getElementById('libDecade');
    const sortSel = document.getElementById('libSort');
    const countLabel = document.getElementById('libCount');
    const emptyState = document.getElementById('libEmpty');

    const cards = Array.from(grid.querySelectorAll('.lib-card'));
    let activeBucket = 'all';

    const norm = (s) =>
        (s || '')
            .toLowerCase()
            .replace(/[\u064A\u06CC]/g, 'ی')
            .replace(/[\u0643\u06A9]/g, 'ک')
            .replace(/[\u200c\u200f\u200e]/g, '')
            .replace(/\s+/g, ' ')
            .trim();

    const items = cards.map((el) => ({
        el,
        bucket: el.dataset.bucket || 'watch',
        rating: parseFloat(el.dataset.rating || '0'),
        year: parseInt(el.dataset.year || '0', 10),
        genres: el.dataset.genres || '',
        country: el.dataset.country || '',
        title: norm(el.dataset.title || el.textContent)
    }));

    function matches(item) {
        if (activeBucket !== 'all' && item.bucket !== activeBucket) return false;

        const q = norm(searchInput ? searchInput.value : '');
        if (q && !item.title.includes(q)) return false;

        if (genreSel && genreSel.value !== 'all' && !item.genres.split('|').includes(genreSel.value)) return false;
        if (countrySel && countrySel.value !== 'all' && !item.country.split('|').includes(countrySel.value)) return false;

        if (decadeSel && decadeSel.value !== 'all') {
            const decade = parseInt(decadeSel.value, 10);
            if (!(item.year >= decade && item.year < decade + 10)) return false;
        }
        return true;
    }

    function sortValue(item, mode) {
        switch (mode) {
            case 'year-desc': return -item.year;
            case 'year-asc': return item.year;
            case 'title': return item.title;
            default: return -item.rating;
        }
    }

    function apply() {
        const mode = sortSel ? sortSel.value : 'rating';
        const visible = items.filter(matches);

        items.forEach((i) => { i.el.hidden = true; });
        visible
            .slice()
            .sort((a, b) => {
                const va = sortValue(a, mode);
                const vb = sortValue(b, mode);
                if (typeof va === 'string') return va.localeCompare(vb, 'fa');
                return va - vb;
            })
            .forEach((i) => {
                i.el.hidden = false;
                grid.appendChild(i.el);
            });

        if (countLabel) {
            const total = items.length.toLocaleString('fa-IR');
            const shown = visible.length.toLocaleString('fa-IR');
            countLabel.textContent = visible.length === items.length ? total + ' فیلم' : shown + ' از ' + total + ' فیلم';
        }
        if (emptyState) emptyState.hidden = visible.length !== 0;
    }

    tabs.forEach((tab) => {
        tab.addEventListener('click', () => {
            tabs.forEach((t) => {
                t.classList.remove('active');
                t.setAttribute('aria-selected', 'false');
            });
            tab.classList.add('active');
            tab.setAttribute('aria-selected', 'true');
            activeBucket = tab.dataset.bucket || 'all';
            apply();
        });
    });

    [genreSel, countrySel, decadeSel, sortSel].forEach((sel) => {
        if (sel) sel.addEventListener('change', apply);
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
