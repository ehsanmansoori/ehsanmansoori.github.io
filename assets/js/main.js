/**
 * Ehsan Mansoori - Cinema Narrator Portal
 * Interactive Film Archive with direct YouTube / Instagram links
 */

const YT = 'https://www.youtube.com/watch?v=';
const IG = 'https://www.instagram.com/reel/';

// هر ردیف مستقیماً به همان ویدیو یا ریلزی لینک است که فیلم در آن بررسی شده.
const FILMS_DATABASE = [
    // قبل از مرگ باید دید - قسمت اول
    { title: "Wild Tales", year: "2014", genre: "thriller", rating: "IMDb 8.1", note: "شش اپیزود دیدنی درباره خشم، جنون و مرز باریک انسانیت با توحش.", url: YT + "khUT8KhD7ak&t=71s", host: "یوتیوب" },
    { title: "Green Book", year: "2018", genre: "drama", rating: "IMDb 8.2", note: "روایتی گرم از دوستی نامتعارف پیانیست سیاه‌پوست و راننده ایتالیایی.", url: YT + "khUT8KhD7ak&t=258s", host: "یوتیوب" },
    { title: "Oldboy", year: "2003", genre: "thriller", rating: "IMDb 8.4", note: "شاهکار سینمای کره جنوبی در کالبدشکافی انتقام و گناه.", url: YT + "khUT8KhD7ak&t=417s", host: "یوتیوب" },
    { title: "Drive", year: "2011", genre: "thriller", rating: "IMDb 7.8", note: "استایل بصری خیره‌کننده، موسیقی سینث‌ویو و خشونت نئو-نوآر.", url: YT + "khUT8KhD7ak&t=585s", host: "یوتیوب" },
    { title: "Nocturnal Animals", year: "2016", genre: "thriller", rating: "IMDb 7.5", note: "استعاره‌ای گزنده از پشیمانی و انتقامی که در صفحات رمان نهفته است.", url: YT + "khUT8KhD7ak&t=783s", host: "یوتیوب" },

    // قسمت سوم
    { title: "The Collini Case", year: "2019", genre: "drama", rating: "IMDb 7.3", note: "معمای قضایی تکان‌دهنده در آلمان و افشای تباهی گذشته تاریخی.", url: YT + "uheHkI1dW-g&t=78s", host: "یوتیوب" },
    { title: "Knives Out", year: "2019", genre: "thriller", rating: "IMDb 7.9", note: "احیای باطراوت ژانر کارآگاهی با کنایه‌های اجتماعی.", url: YT + "uheHkI1dW-g&t=250s", host: "یوتیوب" },
    { title: "Gone Girl", year: "2014", genre: "thriller", rating: "IMDb 8.1", note: "جراحی بی‌رحمانه فینچر روی فریب رسانه‌ای و بحران زناشویی.", url: YT + "uheHkI1dW-g&t=408s", host: "یوتیوب" },
    { title: "The Hangover", year: "2009", genre: "drama", rating: "IMDb 7.7", note: "اوج کمدی موقعیت و فراموشی در لاس‌وگاس.", url: YT + "uheHkI1dW-g&t=572s", host: "یوتیوب" },
    { title: "The Devil's Advocate", year: "1997", genre: "thriller", rating: "IMDb 7.5", note: "نبرد اخلاق با وسوسه ثروت و قدرت شیطانی.", url: YT + "uheHkI1dW-g&t=717s", host: "یوتیوب" },

    // قسمت پنجم
    { title: "The Lives of Others", year: "2006", genre: "drama", rating: "IMDb 8.4", note: "انسانی‌ترین فیلم درباره رستگاری در دل خفقان آلمان شرقی.", url: YT + "_wMtIRojano&t=37s", host: "یوتیوب" },
    { title: "The Gentlemen", year: "2020", genre: "thriller", rating: "IMDb 7.8", note: "بازگشت پرانرژی گای ریچی به گانگسترهای شیک‌پوش بریتانیایی.", url: YT + "_wMtIRojano&t=183s", host: "یوتیوب" },
    { title: "3-Iron", year: "2004", genre: "drama", rating: "IMDb 7.9", note: "روایتی مینیمال از عشق بی‌کلام کیم کی‌دوک.", url: YT + "_wMtIRojano&t=348s", host: "یوتیوب" },
    { title: "The Platform", year: "2019", genre: "scifi", rating: "IMDb 7.0", note: "تمثیلی ترسناک از نابرابری و آزمون بقای انسان.", url: YT + "_wMtIRojano&t=513s", host: "یوتیوب" },
    { title: "Inception", year: "2010", genre: "scifi", rating: "IMDb 8.8", note: "معماری تو در توی رویا و سفر نولان به اعماق ناخودآگاه.", url: YT + "_wMtIRojano&t=680s", host: "یوتیوب" },

    // قسمت ششم
    { title: "21 Grams", year: "2003", genre: "drama", rating: "IMDb 7.6", note: "پازل تلخ ایناریتو درباره پیوند اعضا و گریزناپذیری تقدیر.", url: YT + "SrzSyfiKFNI&t=41s", host: "یوتیوب" },
    { title: "The Sea Inside", year: "2004", genre: "drama", rating: "IMDb 8.0", note: "بازی استثنایی خاویر باردم در ستایش کرامت و حق تعیین سرنوشت.", url: YT + "SrzSyfiKFNI&t=212s", host: "یوتیوب" },
    { title: "Bohemian Rhapsody", year: "2018", genre: "drama", rating: "IMDb 7.9", note: "شکوه یک نابغه موسیقی؛ فردی مرکوری و گروه کوئین.", url: YT + "SrzSyfiKFNI&t=350s", host: "یوتیوب" },
    { title: "Little Women", year: "2019", genre: "drama", rating: "IMDb 7.8", note: "ظرافت بلوغ و استقلال زنان در نیوانگلند.", url: YT + "SrzSyfiKFNI&t=479s", host: "یوتیوب" },
    { title: "Interstellar", year: "2014", genre: "scifi", rating: "IMDb 8.7", note: "ترانه‌ای برای پیوند پدر و دختر فراتر از بعد زمان.", url: YT + "SrzSyfiKFNI&t=629s", host: "یوتیوب" },

    // قسمت هفتم
    { title: "Room", year: "2015", genre: "drama", rating: "IMDb 8.1", note: "جهان کوچک یک اتاق و درخشش اولین دیدار با آسمان باز.", url: YT + "96WO971vZok&t=26s", host: "یوتیوب" },
    { title: "The Unknown Woman", year: "2006", genre: "drama", rating: "IMDb 7.4", note: "درامی ملتهب از رازهای مادری ناشناس.", url: YT + "96WO971vZok&t=161s", host: "یوتیوب" },
    { title: "Mud", year: "2012", genre: "drama", rating: "IMDb 7.4", note: "ماجراجویی دو نوجوان در کنار رودخانه می‌سی‌سی‌پی.", url: YT + "96WO971vZok&t=286s", host: "یوتیوب" },
    { title: "The Lobster", year: "2015", genre: "scifi", rating: "IMDb 7.1", note: "جهان ابزورد لانتیموس در نقد ازدواج‌های تحمیلی.", url: YT + "96WO971vZok&t=420s", host: "یوتیوب" },
    { title: "Pulp Fiction", year: "1994", genre: "thriller", rating: "IMDb 8.9", note: "انقلاب روایت غیرخطی و نبوغ دیالوگ کوئنتین تارانتینو.", url: YT + "96WO971vZok&t=568s", host: "یوتیوب" },

    // پاپ‌کورن - اینستاگرام (متادیتای تأییدشده از کپشن ریلزها)
    { title: "The Wave (موج)", year: "2008", genre: "drama", rating: "پاپ‌کورن ۱۴۳", note: "دنیس گانزل | IMDb ۷.۶ / RT ۹۱٪ - تبدیل یک کلاس به توده فاشیست.", url: IG + "DcypwZ1gChs/", host: "اینستاگرام" },
    { title: "Obsession (وسواس)", year: "2026", genre: "thriller", rating: "پاپ‌کورن ۱۴۰", note: "کری بارکر | IMDb ۸.۱ / RT ۹۴٪ - وابستگی بیمارگونه و فروپاشی ذهن.", url: IG + "DaQqnTZANwG/", host: "اینستاگرام" },
    { title: "Late Shift (شیفت شب)", year: "2025", genre: "drama", rating: "پاپ‌کورن ۱۳۴", note: "پترا بیوندینا ولپه | IMDb ۷.۸ / RT ۹۵٪ - یک شیفت شب و یک تصمیم خطرناک.", url: IG + "DOd_Hr2DCCU/", host: "اینستاگرام" },
    { title: "Silenced (ساکت شده)", year: "2011", genre: "drama", rating: "پاپ‌کورن ۱۲۵", note: "هوانگ دونگ-هیوک | IMDb ۸.۰ / RT ۱۰۰٪ - افشای خشونت در مدرسه ناشنوایان.", url: IG + "DCFFy7oO_eR/", host: "اینستاگرام" },
    { title: "Predestination (تقدیر)", year: "2014", genre: "scifi", rating: "پاپ‌کورن ۸۲", note: "برادران اسپریگ | IMDb ۷.۵ / RT ۸۴٪ - پیچش زمانی پیش از سریال دارک.", url: IG + "CPF0CPEno2m/", host: "اینستاگرام" },

    // بلیت - سینمای ایران
    { title: "اسکورت (Escort)", year: "1403", genre: "iran", rating: "بلیت", note: "بررسی یوسف حاتمی‌کیا، امیر جدیدی و چالش ساخت تریلر پلیسی.", url: YT + "Cg-HyOxAajs&t=60s", host: "یوتیوب" },
    { title: "بی‌دار (Bidar)", year: "1403", genre: "iran", rating: "بلیت", note: "نگاهی به جریان فیلم‌های دغدغه‌مند اجتماعی در اکران.", url: YT + "Cg-HyOxAajs&t=210s", host: "یوتیوب" },
    { title: "خانم والده", year: "1403", genre: "iran", rating: "بلیت", note: "تحلیل کیفیت کمدی و سلیقه مخاطب در آثار سرگرم‌کننده.", url: YT + "Cg-HyOxAajs&t=385s", host: "یوتیوب" },
    { title: "بت (Bot)", year: "1403", genre: "iran", rating: "بلیت", note: "نقدی بر تم‌های روان‌شناختی و اجرای بازیگران سینمای روز.", url: YT + "Cg-HyOxAajs&t=510s", host: "یوتیوب" }
];

document.addEventListener('DOMContentLoaded', () => {
    const grid = document.getElementById('filmsGrid');
    const chips = document.querySelectorAll('.filter-chip');
    if (!grid) return;

    function genreLabel(genre) {
        switch (genre) {
            case 'drama': return 'درام / داستانی';
            case 'thriller': return 'جنایی / معمایی / تریلر';
            case 'scifi': return 'علمی-تخیلی / نمادین';
            case 'iran': return 'اکران سینمای ایران';
            default: return 'عمومی';
        }
    }

    function renderFilms(filter = 'all') {
        grid.innerHTML = '';
        const filtered = FILMS_DATABASE.filter(f => filter === 'all' || f.genre === filter);

        filtered.forEach(item => {
            const card = document.createElement('a');
            card.className = 'film-item-card';
            card.href = item.url;
            card.target = '_blank';
            card.rel = 'noopener';
            card.setAttribute('aria-label', item.title + ' - تماشا در ' + item.host);

            card.innerHTML = `
                <div>
                    <div class="film-item-top">
                        <h4 class="film-title-en">${item.title}</h4>
                        <span class="film-year">${item.year}</span>
                    </div>
                    <div class="film-genre-tag">${genreLabel(item.genre)}</div>
                    <p class="film-note">${item.note}</p>
                </div>
                <div class="film-rating-badge">${item.rating} &bull; ${item.host} &larr;</div>
            `;

            grid.appendChild(card);
        });
    }

    chips.forEach(chip => {
        chip.addEventListener('click', () => {
            chips.forEach(c => c.classList.remove('active'));
            chip.classList.add('active');
            renderFilms(chip.getAttribute('data-genre') || 'all');
        });
    });

    renderFilms('all');
});
