/**
 * Ehsan Mansoori - Cinema Narrator Portal
 * Interactive Film Archive & Navigation
 */

const FILMS_DATABASE = [
    { title: "Wild Tales", year: "2014", genre: "thriller", rating: "IMDb 8.1", note: "شش اپیزود دیدنی درباره خشم، جنون و مرز باریک انسانیت با توحش." },
    { title: "Green Book", year: "2018", genre: "drama", rating: "IMDb 8.2", note: "روایتی گرم و ملموس از دوستی نامتعارف پیانیست سیاهپوست و راننده ایتالیایی." },
    { title: "Oldboy", year: "2003", genre: "thriller", rating: "IMDb 8.4", note: "شاهکار بی بدیل سینمای کره جنوبی در کالبدشکافی انتقام و گناه." },
    { title: "Drive", year: "2011", genre: "thriller", rating: "IMDb 7.8", note: "استایل بصری خیره کننده، موسیقی سینث ویو و بازی درخشان رایان گاسلینگ." },
    { title: "Nocturnal Animals", year: "2016", genre: "thriller", rating: "IMDb 7.5", note: "استعاره ای گزنده از پشیمانی و انتقامی که در صفحات یک رمان نهفته است." },
    { title: "The Collini Case", year: "2019", genre: "drama", rating: "IMDb 7.3", note: "معمای تکان دهنده قضایی در آلمان و افشای تباهی های گذشته تاریخی." },
    { title: "Knives Out", year: "2019", genre: "thriller", rating: "IMDb 7.9", note: "احیای باطراوت ژانر کارآگاهی با لحنی پر از کنایه های اجتماعی." },
    { title: "Gone Girl", year: "2014", genre: "thriller", rating: "IMDb 8.1", note: "جراحی بی رحمانه دیوید فینچر روی فریب رسانه ای و بحران زناشویی." },
    { title: "The Lives of Others", year: "2006", genre: "drama", rating: "IMDb 8.4", note: "شاید انسانی ترین فیلم درباره رستگاری در دل خفقان استراق سمع آلمان شرقی." },
    { title: "The Gentlemen", year: "2020", genre: "thriller", rating: "IMDb 7.8", note: "بازگشت پرانرژی گای ریچی به دنیای گانگسترهای شیک پوش بریتانیایی." },
    { title: "3-Iron", year: "2004", genre: "drama", rating: "IMDb 7.9", note: "روایتی مینیمال و پر از استعاره از عشق بی کلام کیم کی دوک." },
    { title: "The Platform", year: "2019", genre: "scifi", rating: "IMDb 7.0", note: "تمثیلی ترسناک از نابرابری و آزمونی بی رحمانه برای سرشت بقای انسان." },
    { title: "Inception", year: "2010", genre: "scifi", rating: "IMDb 8.8", note: "معماری تو در توی رویا و سفر اودیسه وار نولان به اعماق ناخودآگاه." },
    { title: "21 Grams", year: "2003", genre: "drama", rating: "IMDb 7.6", note: "پازل تلخ ایناریتو درباره پیوند اعضا، ایمان و گریزناپذیری تقدیر." },
    { title: "The Sea Inside", year: "2004", genre: "drama", rating: "IMDb 8.0", note: "بازی استثنایی خاویر باردم در ستایش کرامت انسانی و حق تعیین سرنوشت." },
    { title: "Bohemian Rhapsody", year: "2018", genre: "drama", rating: "IMDb 7.9", note: "شکوه و سقوط یک نابغه موسیقی، فردی مرکوری در گروه کوئین." },
    { title: "Interstellar", year: "2014", genre: "scifi", rating: "IMDb 8.7", note: "فراتر از ابعاد فضا و زمان؛ ترانه ای برای پیوند پدر و دختر." },
    { title: "The Lobster", year: "2015", genre: "scifi", rating: "IMDb 7.1", note: "جهان ابزورد لانتیموس در نقد فشارهای اجباری جوامع برای ازدواج." },
    { title: "Pulp Fiction", year: "1994", genre: "thriller", rating: "IMDb 8.9", note: "انقلاب روایت های غیرخطی و نبوغ دیالوگ نویسی کوئنتین تارانتینو." },
    { title: "اسکورت (Escort)", year: "1403", genre: "iran", rating: "سینمای ایران", note: "بررسی یوسف حاتمی کیا، امیر جدیدی و چالش های ساخت تریلر پلیسی." },
    { title: "بی دار (Bidar)", year: "1403", genre: "iran", rating: "سینمای ایران", note: "نگاهی به جریان فیلم های دغدغه مند اجتماعی در اکران سینماها." },
    { title: "خانم والده", year: "1403", genre: "iran", rating: "سینمای ایران", note: "تحلیل کیفیت کمدی و سلیقه مخاطب در مواجهه با آثار سرگرم کننده." },
    { title: "بت (Bot)", year: "1403", genre: "iran", rating: "سینمای ایران", note: "نقدی بر تم های روان شناختی و اجرای بازیگران در سینمای روز." }
];

document.addEventListener('DOMContentLoaded', () => {
    const grid = document.getElementById('filmsGrid');
    const chips = document.querySelectorAll('.filter-chip');

    function renderFilms(filter = 'all') {
        if (!grid) return;
        grid.innerHTML = '';

        const filtered = FILMS_DATABASE.filter(f => filter === 'all' || f.genre === filter);

        filtered.forEach(item => {
            const card = document.createElement('article');
            card.className = 'film-item-card';

            card.innerHTML = `
                <div>
                    <div class="film-item-top">
                        <h4 class="film-title-en">${item.title}</h4>
                        <span class="film-year">${item.year}</span>
                    </div>
                    <div class="film-genre-tag">${getGenreLabel(item.genre)}</div>
                    <p class="film-note">${item.note}</p>
                </div>
                <div class="film-rating-badge">${item.rating}</div>
            `;

            grid.appendChild(card);
        });
    }

    function getGenreLabel(genre) {
        switch (genre) {
            case 'drama': return 'درام / داستانی';
            case 'thriller': return 'جنایی / معمایی / تریلر';
            case 'scifi': return 'علمی-تخیلی / نمادین';
            case 'iran': return 'اکران سینمای ایران';
            default: return 'عمومی';
        }
    }

    chips.forEach(chip => {
        chip.addEventListener('click', () => {
            chips.forEach(c => c.classList.remove('active'));
            chip.classList.add('active');
            const targetGenre = chip.getAttribute('data-genre') || 'all';
            renderFilms(targetGenre);
        });
    });

    renderFilms('all');
});
