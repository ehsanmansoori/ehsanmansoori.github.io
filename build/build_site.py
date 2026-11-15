#!/usr/bin/env python3
"""
Ehsan Mansoori portal generator.

Builds a fully static index.html from verified YouTube/Instagram data plus the
standard SEO companion files (robots, sitemap, 404, manifest, OG image).

Run:  python3 build/build_site.py
Data: build/episodes_raw.json  (scraped chapter lists, see bottom of this file)
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
ASSETS = ROOT / "assets"

SITE = "https://ehsanmansoori.github.io"
PERSON_FA = "احسان منصوری"
PERSON_EN = "Ehsan Mansoori"
YT_CHANNEL = "https://www.youtube.com/@ehsanmansoori"
IG = "https://www.instagram.com/ehsan_mansoori"
X = "https://x.com/EhsanMansoorii"
PLAYLIST = "https://www.youtube.com/playlist?list=PLHPi-Jd5RkUEDw2PoJelP0bTz1EqteVd3"
GOOGLE_VERIFICATION = "1bSuT-QoDy7ukGYtf0DVP8jBzHzIhxEqGPHMJVxjD94"

JUNK = re.compile(r"^(معرفی|جریان چیه|اولویت بندی|اسپانسر|حمایت|تبلیغ)\s*$", re.I)
PERSIAN_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
FA_MONTH_UNUSED = None


def fa(n: int | str) -> str:
    return str(n).translate(PERSIAN_DIGITS)


def ts(total: int) -> str:
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


# --------------------------------------------------------------------------- data
def load_episodes() -> list[dict]:
    raw = json.loads((BUILD / "episodes_raw.json").read_text(encoding="utf-8"))
    eps: list[dict] = []
    for key, item in raw.items():
        films = [
            {"t": f["t"], "ts": f["ts"], "name": f["name"].replace("\u200b", "").strip()}
            for f in item["films"]
            if not JUNK.match(f["name"].replace("\u200b", "").strip())
        ]
        # the "پنج فیلم" era kept two housekeeping chapters; drop the trailing one too
        films = [f for f in films if not f["name"].startswith("اولویت")]
        num = key if key.startswith("special") else int(key)
        eps.append(
            {
                "key": key,
                "num": num,
                "vid": item["vid"],
                "title": item["title"].replace("\u200b", "").strip(),
                "films": films,
            }
        )
    eps.sort(key=lambda e: (isinstance(e["num"], str), e["num"] if not isinstance(e["num"], str) else 99))
    return eps


def episode_label(ep: dict) -> str:
    if ep["key"] == "special1":
        return "ویژه | بهترین فیلم‌های ۲۵ سال اخیر"
    if ep["key"] == "special2":
        return "ویژه | ۱۰۰ فیلم جذاب سینما"
    return f"قسمت {fa(ep['num'])}"


def episode_group(ep: dict) -> str:
    if ep["key"].startswith("special"):
        return "special"
    return "early" if ep["num"] <= 7 else "late"


# verified Instagram reels (caption metadata read from Instagram, not guessed)
POPCORN = [
    {"ep": 143, "fa": "موج", "en": "The Wave", "dir": "دنیس گانزل", "where": "آلمان ۲۰۰۸",
     "score": "IMDb ۷.۶ | RT ۹۱٪", "code": "DcypwZ1gChs",
     "note": "هیجان‌انگیز و سیاسی-اجتماعی؛ چگونه یک معلم در یک هفته کلاسی را به توده‌ای فاشیست تبدیل می‌کند."},
    {"ep": 140, "fa": "وسواس", "en": "Obsession", "dir": "کری بارکر", "where": "آمریکا ۲۰۲۶",
     "score": "IMDb ۸.۱ | RT ۹۴٪", "code": "DaQqnTZANwG",
     "note": "روان‌شناختی و ترسناک؛ واکاوی وابستگی بیمارگونه و فروپاشی ذهن در بستری دلهره‌آور."},
    {"ep": 134, "fa": "شیفت شب", "en": "Late Shift", "dir": "پترا بیوندینا ولپه", "where": "سوئیس و آلمان ۲۰۲۵",
     "score": "IMDb ۷.۸ | RT ۹۵٪", "code": "DOd_Hr2DCCU",
     "note": "درام؛ یک تصمیم اشتباه در یک شیفت شب، زندگی پرستاری جوان را به گردابی از خطر می‌کشاند."},
    {"ep": 125, "fa": "ساکت شده", "en": "Silenced", "dir": "هوانگ دونگ-هیوک", "where": "کره جنوبی ۲۰۱۱",
     "score": "IMDb ۸.۰ | RT ۱۰۰٪", "code": "DCFFy7oO_eR",
     "note": "درام و جنایی؛ روایت واقعی افشای خشونت در مدرسه ناشنوایان که به تغییر قانون انجامید."},
    {"ep": 82, "fa": "تقدیر", "en": "Predestination", "dir": "میشل و پیتر اسپریگ", "where": "استرالیا ۲۰۱۴",
     "score": "IMDb ۷.۵ | RT ۸۴٪", "code": "CPF0CPEno2m",
     "note": "علمی-تخیلی؛ پیچش زمانی که سال‌ها پیش از سریال دارک، ذهن را منفجر می‌کند."},
]

# بلیت: every timestamp below is a real chapter of that single review video
BILIT_VID = "Cg-HyOxAajs"
BILIT = [
    {"fa": "اسکورت", "credit": "یوسف حاتمی‌کیا | امیر جدیدی، هدی زین‌العابدین", "genre": "اکشن اجتماعی و تعلیق",
     "focus": "ریتم، باورپذیری چالش‌های امنیتی و بازی نقش اول", "t": 60, "ts": "1:00"},
    {"fa": "بی‌دار", "credit": "سینمای مستقل داستانی", "genre": "درام تلخ اجتماعی",
     "focus": "عمق شخصیت‌پردازی و روایت دغدغه‌های فرودستان", "t": 210, "ts": "3:30"},
    {"fa": "خانم والده", "credit": "کمدی خانوادگی", "genre": "موقعیت و اجتماعی",
     "focus": "مرز شوخی استاندارد با کمدی‌های دم‌دستی تجاری", "t": 385, "ts": "6:25"},
    {"fa": "بت", "credit": "درام روان‌شناختی", "genre": "معمایی",
     "focus": "کالبدشکافی قدرت و کاریزمای دروغین کاراکترها", "t": 510, "ts": "8:30"},
]


def yt(vid: str, t: int | None = None) -> str:
    return f"https://youtu.be/{vid}" + (f"?t={t}" if t is not None else "")


def thumb(vid: str) -> str:
    return f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"


# --------------------------------------------------------------------------- render

GENRE_FA = {
    "Drama": "درام", "Thriller": "هیجان‌انگیز", "Comedy": "کمدی", "Crime": "جنایی",
    "Romance": "عاشقانه", "Mystery": "معمایی", "Science Fiction": "علمی-تخیلی",
    "Action": "اکشن", "Horror": "ترسناک", "History": "تاریخی", "War": "جنگی",
    "Music": "موسیقی", "Adventure": "ماجراجویی", "Family": "خانوادگی",
    "Animation": "انیمیشن", "Fantasy": "فانتزی", "Documentary": "مستند",
    "Western": "وسترن", "TV Movie": "تله‌فیلم",
}

COUNTRY_FA = {
    "United States of America": "آمریکا", "United Kingdom": "بریتانیا",
    "South Korea": "کره جنوبی", "France": "فرانسه", "Germany": "آلمان",
    "Canada": "کانادا", "Spain": "اسپانیا", "Italy": "ایتالیا", "China": "چین",
    "Argentina": "آرژانتین", "Japan": "ژاپن", "Mexico": "مکزیک", "Switzerland": "سوئیس",
    "Australia": "استرالیا", "Iran": "ایران", "Denmark": "دانمارک", "Norway": "نروژ",
    "Sweden": "سوئد", "Netherlands": "هلند", "Belgium": "بلژیک", "India": "هند",
    "Hong Kong": "هنگ‌کنگ", "Taiwan": "تایوان", "Poland": "لهستان", "Russia": "روسیه",
    "Turkey": "ترکیه", "Brazil": "برزیل", "Ireland": "ایرلند", "New Zealand": "نیوزیلند",
    "Austria": "اتریش", "Portugal": "پرتغال", "Finland": "فنلاند",
    "Czech Republic": "چک", "Hungary": "مجارستان", "Greece": "یونان", "Ukraine": "اوکراین",
}



def asset_stamp() -> str:
    """short hash of css+js so returning visitors never get a stale bundle"""
    import hashlib

    h = hashlib.sha1()
    for rel in ("assets/css/style.css", "assets/js/main.js"):
        p = ROOT / rel
        if p.exists():
            h.update(p.read_bytes())
    return h.hexdigest()[:8]


def load_films() -> dict:
    path = BUILD / "films_meta.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def _lookup_meta(meta: dict, name: str) -> dict | None:
    """Match a channel title to its TMDB record, tolerating Persian wrappers."""
    key = name.lower().strip()
    if key in meta:
        return meta[key]
    simple = re.sub(r"\s*\(.*\)\s*", "", name).lower().strip()
    if simple in meta:
        return meta[simple]
    inner = re.findall(r"\((.*?)\)", name)
    for part in inner:
        if part.lower().strip() in meta:
            return meta[part.lower().strip()]
    return None


def _poster(p: str) -> str:
    """TMDB serves every size from one path, so downgrade to a list-friendly width."""
    return p.replace("/w500/", "/w342/") if p else ""


def build_library(eps: list[dict], meta: dict) -> list[dict]:
    items: list[dict] = []
    seen: set[str] = set()

    def add(name: str, bucket: str, source: str, href: str, chip: str, t: int | None):
        m = _lookup_meta(meta, name) or {}
        key = f"tmdb:{m['tmdb_id']}" if m.get("tmdb_id") else "name:" + name.lower()
        if key in seen:
            return
        seen.add(key)
        ok = bool(m.get("ok"))
        fa_title = m.get("title_fa") if ok else None
        # TMDB sometimes has no Persian translation and returns the original script
        if not fa_title or not any("\u0600" <= ch <= "\u06FF" for ch in fa_title):
            fa_title = m.get("title_en") or name
        items.append(
            {
                "name": name,
                "bucket": bucket,
                "source": source,
                "href": href,
                "chip": chip,
                "t": t,
                "title": fa_title,
                "title_en": m.get("title_en") or name,
                "year": m.get("year"),
                "runtime": m.get("runtime"),
                "poster": _poster(m.get("poster") or ""),
                "overview": m.get("overview") or "",
                "genres": [GENRE_FA.get(g, g) for g in (m.get("genres") or [])],
                "raw_genres": m.get("genres") or [],
                "director": m.get("director") or [],
                "cast": m.get("cast") or [],
                "country": [COUNTRY_FA.get(c, c) for c in (m.get("country") or [])],
                "raw_country": m.get("country") or [],
                "rating": m.get("rating") or 0,
                "votes": m.get("votes") or 0,
                "imdb": m.get("imdb"),
                "tmdb_url": m.get("tmdb_url"),
                "ok": ok,
            }
        )

    for ep in eps:
        for f in ep["films"]:
            add(f["name"], "watch", "سری فیلم‌ها", yt(ep["vid"], f["t"]), episode_label(ep), f["t"])
    for b in BILIT:
        add(b["fa"], "skip", "بلیت", yt(BILIT_VID, b["t"]), f'دقیقه {b["ts"]}', b["t"])
    for pc in POPCORN:
        add(f'{pc["fa"]} ({pc["en"]})', "watch", "پاپ‌کورن",
            f'https://www.instagram.com/reel/{pc["code"]}/', f'پاپ‌کورن {fa(pc["ep"])}', None)

    items.sort(key=lambda i: (-(i["rating"] or 0), i["year"] or 0))
    return items


def render_library(items: list[dict]) -> str:
    genres = sorted({g for i in items for g in i["genres"]})
    countries = sorted({c for i in items for c in i["country"]})
    decades = sorted({(i["year"] // 10) * 10 for i in items if i["year"]}, reverse=True)
    watch = sum(1 for i in items if i["bucket"] == "watch")
    skip = sum(1 for i in items if i["bucket"] == "skip")

    genre_opts = "".join(f'<option value="{g}">{g}</option>' for g in genres)
    country_opts = "".join(f'<option value="{c}">{c}</option>' for c in countries)
    decade_opts = "".join(f'<option value="{d}">{fa(str(d))}s</option>' for d in decades)

    cards = []
    for i in items:
        stars = f'{i["rating"]:.1f}' if i["rating"] else ""
        stars_fa = fa(stars) if stars else ""
        meta_bits = []
        if i["year"]:
            meta_bits.append(fa(i["year"]))
        if i["runtime"]:
            meta_bits.append(f'{fa(i["runtime"])} دقیقه')
        if i["genres"]:
            meta_bits.append("، ".join(i["genres"][:2]))
        if i["country"]:
            meta_bits.append(i["country"][0])
        meta_line = " • ".join(meta_bits)

        poster = (
            f'<img src="{i["poster"]}" alt="پوستر {i["title"]}" width="342" height="513" loading="lazy" decoding="async">'
            if i["poster"] else '<span class="lib-noimg">بدون پوستر</span>'
        )
        badge = "ببینیم" if i["bucket"] == "watch" else "نبینیم"
        rating_html = f'<span class="lib-rate">{stars_fa}</span>' if stars_fa and i["rating"] else ""
        extra_links = []
        if i["imdb"]:
            extra_links.append(f'<a href="https://www.imdb.com/title/{i["imdb"]}/" target="_blank" rel="noopener">IMDb</a>')
        if i["tmdb_url"]:
            extra_links.append(f'<a href="{i["tmdb_url"]}" target="_blank" rel="noopener">TMDB</a>')
        cast_html = (
            f'<p class="lib-line"><b>بازیگران:</b> {"، ".join(i["cast"][:3])}</p>' if i["cast"] else ""
        )
        dir_html = f'<p class="lib-line"><b>کارگردان:</b> {"، ".join(i["director"])}</p>' if i["director"] else ""
        overview = (
            f'<p class="lib-overview">{i["overview"]}</p>' if i["overview"] else ""
        )
        cards.append(f'''<article class="lib-card" data-bucket="{i["bucket"]}" data-rating="{i["rating"]}"
  data-year="{i["year"] or 0}" data-genres="{"|".join(i["raw_genres"])}" data-country="{"|".join(i["raw_country"])}"
  data-title="{i["title"]} {i["title_en"]} {" ".join(i["director"])} {" ".join(i["cast"])}">
  <div class="lib-poster">
    {poster}
    <span class="lib-badge {i["bucket"]}">{badge}</span>
    {rating_html}
  </div>
  <div class="lib-body">
    <h4 class="lib-title">{i["title"]}</h4>
    <p class="lib-en" dir="ltr">{i["title_en"]}</p>
    <p class="lib-meta">{meta_line}</p>
    {dir_html}
    {cast_html}
    {overview}
    <div class="lib-links">
      <a class="lib-watch" href="{i["href"]}" target="_blank" rel="noopener">تحلیل احسان | {i["chip"]}</a>
      {"".join(extra_links)}
    </div>
  </div>
</article>''')

    return f'''<section id="all-movies" class="section alt-bg">
  <div class="container">
    <div class="section-head">
      <h2 class="section-title">کتابخانه فیلم‌ها</h2>
      <p class="section-subtitle">{fa(len(items))} فیلم با پوستر و اطلاعات کامل از TMDB، هر کدام وصل به تحلیل احسان منصوری</p>
    </div>

    <div class="lib-tabs" role="tablist" aria-label="دسته‌بندی">
      <button class="lib-tab active" data-bucket="all" role="tab" aria-selected="true">همه ({fa(len(items))})</button>
      <button class="lib-tab" data-bucket="watch" role="tab" aria-selected="false">چی ببینیم ({fa(watch)})</button>
      <button class="lib-tab" data-bucket="skip" role="tab" aria-selected="false">چی نبینیم ({fa(skip)})</button>
    </div>
    <p class="lib-note">«چی ببینیم» فیلم‌هایی است که احسان منصوری در سری معرفی کرده و در پاپ‌کورن توصیه کرده. «چی نبینیم» فیلم‌های اکران روز است که در برنامه بلیت نقد شده‌اند؛ برچسب این دسته به معنی توصیه نبودن است، نه حکم قطعی به ندیدن.</p>

    <div class="lib-controls">
      <input type="search" id="libSearch" class="search-input" placeholder="جستجوی نام فیلم یا بازیگر…" aria-label="جستجوی فیلم" autocomplete="off">
      <select id="libGenre" class="lib-select" aria-label="ژانر"><option value="all">همه ژانرها</option>{genre_opts}</select>
      <select id="libCountry" class="lib-select" aria-label="کشور"><option value="all">همه کشورها</option>{country_opts}</select>
      <select id="libDecade" class="lib-select" aria-label="دهه"><option value="all">همه دهه‌ها</option>{decade_opts}</select>
      <select id="libSort" class="lib-select" aria-label="ترتیب">
        <option value="rating">بیشترین امتیاز</option>
        <option value="year-desc">جدیدترین</option>
        <option value="year-asc">قدیمی‌ترین</option>
        <option value="title">الفبایی</option>
      </select>
      <span class="search-count" id="libCount"></span>
    </div>

    <div class="lib-grid" id="libGrid">
{"".join(cards)}
    </div>
    <p class="empty-state" id="libEmpty" hidden>فیلمی با این فیلترها پیدا نشد.</p>
    <p class="lib-credit">اطلاعات و پوسترها از <a href="https://www.themoviedb.org/" target="_blank" rel="noopener">TMDB</a>. این سایت توسط TMDB تأیید نشده و صرفاً از API آن استفاده می‌کند.</p>
  </div>
</section>

'''


def render(eps: list[dict]) -> str:
    ep_cards = []
    for ep in eps:
        if ep["films"]:
            films_html = "\n".join(
                f'<li><a href="{yt(ep["vid"], f["t"])}" target="_blank" rel="noopener">'
                f'<span class="ep-t">{f["ts"]}</span><span class="ep-name">{f["name"]}</span></a></li>'
                for f in ep["films"]
            )
            body = f'<ul class="ep-films">{films_html}</ul>'
            count = f'{fa(len(ep["films"]))} فیلم'
        else:
            body = '<p class="ep-empty">فهرست فیلم‌ها در توضیحات این ویدیو درج نشده است. برای دیدن فهرست کامل، ویدیو را باز کنید.</p>'
            count = "فهرست در ویدیو"
        ep_cards.append(
            f'''<article class="episode-card" data-group="{episode_group(ep)}">
  <a class="ep-thumb" href="{yt(ep["vid"])}" target="_blank" rel="noopener" aria-label="{episode_label(ep)}">
    <img src="{thumb(ep["vid"])}" alt="کاور {episode_label(ep)}" width="480" height="360" loading="lazy" decoding="async">
    <span class="ep-play" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg></span>
  </a>
  <div class="ep-body">
    <div class="ep-head">
      <h3>{episode_label(ep)}</h3>
      <span class="ep-count">{count}</span>
    </div>
    {body}
  </div>
</article>'''
        )

    popcorn_cards = "\n".join(
        f'''<a class="popcorn-card" href="https://www.instagram.com/reel/{p["code"]}/" target="_blank" rel="noopener">
  <div class="popcorn-top"><span class="popcorn-ep">پاپ‌کورن {fa(p["ep"])}</span>
  <span class="popcorn-link-hint">اینستاگرام &larr;</span></div>
  <h3 class="popcorn-name">{p["fa"]} ({p["en"]})</h3>
  <div class="popcorn-meta">کارگردان: {p["dir"]} | {p["where"]} | {p["score"]}</div>
  <p class="popcorn-synopsis">{p["note"]}</p>
</a>'''
        for p in POPCORN
    )

    bilit_rows = "\n".join(
        f'''<tr>
  <td><strong>{b["fa"]}</strong></td>
  <td>{b["credit"]}</td>
  <td>{b["genre"]}</td>
  <td>{b["focus"]}</td>
  <td><a href="{yt(BILIT_VID, b["t"])}" target="_blank" rel="noopener" class="table-link-btn">دقیقه {b["ts"]} &larr;</a></td>
</tr>'''
        for b in BILIT
    )

    STAMP = asset_stamp()
    library = build_library(eps, load_films())
    library_section = render_library(library)
    films_total = len(library)
    eps_with_list = sum(1 for e in eps if e["films"])

    jsonld = json.dumps(
        [
            {
                "@context": "https://schema.org",
                "@type": "Person",
                "name": PERSON_FA,
                "alternateName": PERSON_EN,
                "jobTitle": "منتقد و راوی سینما",
                "description": "راوی سینما؛ تحلیل و معرفی فیلم و سریال در یوتیوب و اینستاگرام.",
                "url": SITE + "/",
                "image": SITE + "/assets/images/profile.jpg",
                "sameAs": [YT_CHANNEL, IG, X],
            },
            {
                "@context": "https://schema.org",
                "@type": "WebSite",
                "name": f"{PERSON_FA} | راوی سینما",
                "url": SITE + "/",
                "inLanguage": "fa-IR",
                "about": {"@type": "Person", "name": PERSON_FA},
            },
            {
                "@context": "https://schema.org",
                "@type": "ItemList",
                "name": "قسمت‌های سری فیلم‌هایی که قبل از مرگ باید دید",
                "numberOfItems": len(eps),
                "itemListElement": [
                    {"@type": "ListItem", "position": i, "url": yt(e["vid"]), "name": episode_label(e)}
                    for i, e in enumerate(eps, 1)
                ],
            },
        ],
        ensure_ascii=False,
        indent=1,
    )

    return f'''<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{PERSON_FA} | راوی سینما و آرشیو کامل فیلم‌ها</title>
<meta name="description" content="آرشیو یکپارچه {fa(len(eps))} قسمت از سری فیلم‌هایی که قبل از مرگ باید دید، {fa(films_total)} فیلم فهرست‌شده با تایم‌کد دقیق، بررسی اکران سینمای ایران و قسمت‌های پاپ‌کورن. همه لینک‌ها به یوتیوب و اینستاگرام رسمی {PERSON_FA}.">
<link rel="canonical" href="{SITE}/">
<meta name="theme-color" content="#0b0d11">
<meta name="author" content="{PERSON_FA}">
<meta name="google-site-verification" content="{GOOGLE_VERIFICATION}">

<meta property="og:type" content="website">
<meta property="og:site_name" content="{PERSON_FA} | راوی سینما">
<meta property="og:locale" content="fa_IR">
<meta property="og:title" content="{PERSON_FA} | آرشیو کامل فیلم‌ها و نقدهای سینمایی">
<meta property="og:description" content="{fa(len(eps))} قسمت سری فیلم، {fa(films_total)} فیلم با تایم‌کد دقیق، پاپ‌کورن و بررسی اکران سینمای ایران.">
<meta property="og:url" content="{SITE}/">
<meta property="og:image" content="{SITE}/assets/images/og-image.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{PERSON_EN} | {PERSON_FA}">

<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{PERSON_FA} | راوی سینما">
<meta name="twitter:description" content="آرشیو کامل قسمت‌ها و {fa(films_total)} فیلم با لینک مستقیم به یوتیوب و اینستاگرام.">
<meta name="twitter:image" content="{SITE}/assets/images/og-image.jpg">

<link rel="icon" href="assets/images/favicon-32.png" sizes="32x32" type="image/png">
<link rel="icon" href="assets/images/favicon-192.png" sizes="192x192" type="image/png">
<link rel="apple-touch-icon" href="assets/images/apple-touch-icon.png">
<link rel="manifest" href="manifest.json">
<link rel="stylesheet" href="assets/css/style.css?v={STAMP}">
<script type="application/ld+json">
{jsonld}
</script>
</head>
<body>
<header class="site-header">
  <div class="nav-container">
    <a href="#hero" class="brand">
      <span class="brand-title">{PERSON_FA}</span>
      <span class="brand-badge">راوی سینما</span>
    </a>
    <nav class="main-nav" aria-label="ناوبری اصلی">
      <a href="#episodes">قسمت‌ها</a>
      <a href="#all-movies">آرشیو فیلم‌ها</a>
      <a href="#popcorn">پاپ‌کورن</a>
      <a href="#bilit">بلیت</a>
      <a href="#social">شبکه‌ها</a>
    </nav>
  </div>
</header>

<div class="yt-channel-banner-wrap">
  <div class="yt-banner-bg" style="background-image: url('assets/images/header_banner.jpg');"></div>
  <div class="yt-banner-overlay"></div>
  <div class="yt-banner-content container">
    <div class="yt-banner-info">
      <span class="yt-badge">کانال رسمی یوتیوب</span>
      <p class="yt-banner-title">{PERSON_EN} | راوی سینما</p>
      <span class="yt-handle" dir="ltr">@ehsanmansoori</span>
    </div>
    <a href="{YT_CHANNEL}?sub_confirmation=1" target="_blank" rel="noopener" class="btn btn-yt-sub">عضویت در کانال یوتیوب</a>
  </div>
</div>

<main>
<section id="hero" class="hero-section">
  <div class="container hero-grid">
    <div class="hero-text">
      <span class="pill-badge">آرشیو یکپارچه و مستقل محتوا</span>
      <h1 class="hero-title">هر فیلمی که معرفی کرده، با لینک دقیق به همان لحظه</h1>
      <p class="hero-desc">
        {fa(len(eps))} قسمت از سری «فیلم‌هایی که قبل از مرگ باید دید» و ادامه‌هایش، {fa(films_total)} فیلم با تایم‌کد واقعی از خود ویدیوها، بررسی اکران سینمای ایران و قسمت‌های پاپ‌کورن. بدون نیاز به گشتن در یوتیوب و اینستاگرام.
      </p>
      <div class="hero-metrics">
        <div class="metric-box"><span class="metric-num">{fa(len(eps))}</span><span class="metric-lbl">قسمت سری فیلم</span></div>
        <div class="metric-box"><span class="metric-num">{fa(films_total)}</span><span class="metric-lbl">فیلم با تایم‌کد</span></div>
        <div class="metric-box"><span class="metric-num">{fa(eps_with_list)}</span><span class="metric-lbl">قسمت با فهرست کامل</span></div>
      </div>
      <div class="hero-actions">
        <a href="#episodes" class="btn btn-primary">دیدن قسمت‌ها</a>
        <a href="#all-movies" class="btn btn-secondary">جستجوی فیلم</a>
        <a href="{PLAYLIST}" target="_blank" rel="noopener" class="btn btn-ghost">پلی‌لیست یوتیوب</a>
      </div>
    </div>
    <div class="hero-card">
      <div class="profile-card">
        <div class="profile-avatar-wrap">
          <img src="assets/images/profile.jpg" alt="{PERSON_FA} | راوی سینما" class="profile-avatar-img" width="110" height="110">
        </div>
        <h2 class="profile-name">{PERSON_FA}</h2>
        <p class="profile-role">منتقد، راوی و تحلیل‌گر سینما</p>
        <div class="profile-tags"><span>سینمای ایران</span><span>شاهکارهای جهان</span><span>سریال‌های روز</span></div>
        <div class="profile-contact-note">همکاری و اسپانسرینگ: <span dir="ltr">@mansoori_ads</span></div>
      </div>
    </div>
  </div>
</section>

<section id="episodes" class="section">
  <div class="container">
    <div class="section-head">
      <h2 class="section-title">تمام قسمت‌های سری فیلم‌ها</h2>
      <p class="section-subtitle">{fa(len(eps))} قسمت، هر فیلم لینک دقیق به لحظه معرفی خودش دارد</p>
    </div>
    <div class="episodes-grid">
{chr(10).join(ep_cards)}
    </div>
  </div>
</section>

{library_section}

<section id="popcorn" class="section">
  <div class="container">
    <div class="section-head">
      <h2 class="section-title">پاپ‌کورن در اینستاگرام</h2>
      <p class="section-subtitle">قسمت‌های تأییدشده با متادیتای خود کپشن</p>
    </div>
    <div class="popcorn-grid">
{popcorn_cards}
    </div>
  </div>
</section>

<section id="bilit" class="section alt-bg">
  <div class="container">
    <div class="section-head">
      <h2 class="section-title">بلیت | پیشخوان سینمای ایران</h2>
      <p class="section-subtitle">بررسی چهار فیلم اکران روز در یک ویدیو، هر فیلم با تایم‌کد خودش</p>
    </div>
    <div class="bilit-table-wrap">
      <table class="bilit-table">
        <thead><tr><th>فیلم</th><th>عوامل</th><th>ژانر</th><th>محور بررسی</th><th>دیدن تحلیل</th></tr></thead>
        <tbody>
{bilit_rows}
        </tbody>
      </table>
    </div>
  </div>
</section>

<section id="social" class="section">
  <div class="container">
    <div class="section-head">
      <h2 class="section-title">ارتباط مستقیم با {PERSON_FA}</h2>
      <p class="section-subtitle">در هر پلتفرم، یک جنس محتوای مکمل سینمایی</p>
    </div>
    <div class="social-channels-grid">
      <a href="{YT_CHANNEL}" target="_blank" rel="noopener" class="channel-card">
        <div class="channel-icon yt" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M23.5 6.2a3 3 0 0 0-2.1-2.1C19.5 3.6 12 3.6 12 3.6s-7.5 0-9.4.5A3 3 0 0 0 .5 6.2C0 8.1 0 12 0 12s0 3.9.5 5.8a3 3 0 0 0 2.1 2.1c1.9.5 9.4.5 9.4.5s7.5 0 9.4-.5a3 3 0 0 0 2.1-2.1c.5-1.9.5-5.8.5-5.8s0-3.9-.5-5.8zM9.5 15.6V8.4L15.8 12l-6.3 3.6z"/></svg></div>
        <h3>یوتیوب (Ehsan Mansoori)</h3>
        <p>ویدیوهای کامل تحلیلی، سری فیلم‌ها، برنامه بلیت و نقد سریال‌ها</p>
        <span class="channel-stat">۱۵۹K+ مشترک</span>
      </a>
      <a href="{IG}" target="_blank" rel="noopener" class="channel-card">
        <div class="channel-icon ig" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M12 2.2c3.2 0 3.6 0 4.9.1 1.2 0 1.8.2 2.2.4.6.2 1 .5 1.4.9.4.4.7.8.9 1.4.2.4.4 1 .4 2.2.1 1.3.1 1.7.1 4.9s0 3.6-.1 4.9c0 1.2-.2 1.8-.4 2.2-.2.6-.5 1-.9 1.4-.4.4-.8.7-1.4.9-.4.2-1 .4-2.2.4-1.3.1-1.7.1-4.9.1s-3.6 0-4.9-.1c-1.2 0-1.8-.2-2.2-.4-.6-.2-1-.5-1.4-.9-.4-.4-.7-.8-.9-1.4-.2-.4-.4-1-.4-2.2C2.2 15.6 2.2 15.2 2.2 12s0-3.6.1-4.9c0-1.2.2-1.8.4-2.2.2-.6.5-1 .9-1.4.4-.4.8-.7 1.4-.9.4-.2 1-.4 2.2-.4C8.4 2.2 8.8 2.2 12 2.2zm0 1.8c-3.1 0-3.5 0-4.7.1-.9 0-1.4.2-1.7.3-.4.2-.7.4-1 .7-.3.3-.5.6-.7 1-.1.3-.3.8-.3 1.7-.1 1.2-.1 1.6-.1 4.2s0 3 .1 4.2c0 .9.2 1.4.3 1.7.2.4.4.7.7 1 .3.3.6.5 1 .7.3.1.8.3 1.7.3 1.2.1 1.6.1 4.7.1s3.5 0 4.7-.1c.9 0 1.4-.2 1.7-.3.4-.2.7-.4 1-.7.3-.3.5-.6.7-1 .1-.3.3-.8.3-1.7.1-1.2.1-1.6.1-4.2s0-3-.1-4.2c0-.9-.2-1.4-.3-1.7-.2-.4-.4-.7-.7-1-.3-.3-.6-.5-1-.7-.3-.1-.8-.3-1.7-.3-1.2-.1-1.6-.1-4.7-.1zm0 3.1a4.9 4.9 0 1 1 0 9.8 4.9 4.9 0 0 1 0-9.8zm0 1.8a3.1 3.1 0 1 0 0 6.2 3.1 3.1 0 0 0 0-6.2zm6.3-2a1.15 1.15 0 1 1-2.3 0 1.15 1.15 0 0 1 2.3 0z"/></svg></div>
        <h3>اینستاگرام (ehsan_mansoori)</h3>
        <p>ریلزهای معرفی سریع پاپ‌کورن و استوری‌های پاسخ به سوالات فیلم‌بازها</p>
        <span class="channel-stat">۶۶۹K+ دنبال‌کننده</span>
      </a>
      <a href="{X}" target="_blank" rel="noopener" class="channel-card">
        <div class="channel-icon tw" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M18.9 2h3.7l-8.1 9.3L24 22h-7.4l-5.8-7.6L4.2 22H.5l8.7-10L0 2h7.6l5.2 6.9L18.9 2zm-1.3 18h2L6.5 4H4.4l13.2 16z"/></svg></div>
        <h3>توییتر / X (@EhsanMansoorii)</h3>
        <p>یادداشت‌های کوتاه، واکنش به جشنواره‌ها، جوایز اسکار و نظرسنجی‌های سینمایی</p>
        <span class="channel-stat">بحث آزاد سینمایی</span>
      </a>
    </div>
  </div>
</section>
</main>

<footer class="site-footer">
  <div class="container footer-inner">
    <div class="footer-brand">
      <span class="footer-title">{PERSON_FA} | راوی سینما</span>
      <p>هاب مستقل برای دسترسی مستقیم به تمامی معرفی‌ها، نقدها و ویدیوها. آخرین بروزرسانی: {LAST_UPDATE}</p>
    </div>
    <div class="footer-copy">
      <span>تمامی محتوای ویدیویی و تصویری متعلق به {PERSON_FA} است.</span>
    </div>
  </div>
</footer>

<script src="assets/js/main.js?v={STAMP}"></script>
</body>
</html>
'''


LAST_UPDATE = "آبان ۱۴۰۵"


# --------------------------------------------------------------------------- side files
def write_side_files(eps: list[dict]) -> None:
    stamp = asset_stamp()
    (ROOT / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n\nSitemap: " + SITE + "/sitemap.xml\n", encoding="utf-8"
    )

    urls = [f"  <url><loc>{SITE}/</loc><changefreq>weekly</changefreq><priority>1.0</priority></url>"]
    sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls)
        + "\n</urlset>\n"
    )
    (ROOT / "sitemap.xml").write_text(sitemap, encoding="utf-8")

    (ROOT / "404.html").write_text(
        f'''<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>صفحه پیدا نشد | {PERSON_FA}</title>
<meta name="robots" content="noindex">
<link rel="icon" href="/assets/images/favicon-32.png" sizes="32x32" type="image/png">
<link rel="stylesheet" href="/assets/css/style.css?v={stamp}">
</head>
<body>
<main class="section notfound">
  <div class="container">
    <h1 class="hero-title">این صفحه وجود ندارد</h1>
    <p class="hero-desc">آدرسی که باز کردید پیدا نشد. از آرشیو کامل فیلم‌ها شروع کنید.</p>
    <div class="hero-actions">
      <a href="/" class="btn btn-primary">صفحه اصلی</a>
      <a href="/#all-movies" class="btn btn-secondary">آرشیو فیلم‌ها</a>
    </div>
  </div>
</main>
</body>
</html>
''',
        encoding="utf-8",
    )

    (ROOT / "manifest.json").write_text(
        json.dumps(
            {
                "name": f"{PERSON_FA} | راوی سینما",
                "short_name": PERSON_FA,
                "lang": "fa-IR",
                "dir": "rtl",
                "start_url": "/",
                "display": "standalone",
                "background_color": "#0b0d11",
                "theme_color": "#0b0d11",
                "icons": [
                    {"src": "/assets/images/favicon-192.png", "sizes": "192x192", "type": "image/png"},
                    {"src": "/assets/images/favicon-512.png", "sizes": "512x512", "type": "image/png"},
                ],
            },
            ensure_ascii=False,
            indent=1,
        ),
        encoding="utf-8",
    )


def write_images() -> None:
    from PIL import Image, ImageDraw

    RESAMPLE = Image.Resampling.LANCZOS
    imgs = ASSETS / "images"
    profile = Image.open(imgs / "profile.jpg").convert("RGB")
    banner = Image.open(imgs / "header_banner.jpg").convert("RGB")

    for size in (32, 192, 512):
        profile.resize((size, size), RESAMPLE).save(imgs / f"favicon-{size}.png")
    profile.resize((180, 180), RESAMPLE).save(imgs / "apple-touch-icon.png")

    # 1200x630 OG card: banner strip + round avatar + latin wordmark (no shaping risk)
    W, H = 1200, 630
    og = Image.new("RGB", (W, H), (11, 13, 17))
    strip = banner.resize((W, int(W * banner.height / banner.width)), RESAMPLE)
    og.paste(strip, (0, 0))
    grad = Image.new("L", (1, H))
    for y in range(H):
        grad.putpixel((0, y), max(0, int(255 * (y / H) ** 0.6)))
    og.paste(Image.new("RGB", (W, H), (11, 13, 17)), (0, 0), grad.resize((W, H)))
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    dg = ImageDraw.Draw(glow)
    dg.ellipse((-180, H - 320, 520, H + 180), fill=(150, 6, 14))
    og = Image.blend(og, glow, 0.28)

    av = profile.resize((188, 188), RESAMPLE)
    mask = Image.new("L", (188, 188), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, 187, 187), fill=255)
    ring = Image.new("RGB", (208, 208), (229, 9, 20))
    ImageDraw.Draw(ring).ellipse((0, 0, 207, 207), fill=(229, 9, 20))
    og.paste(ring, (86, 214))
    og.paste(av, (96, 224), mask)

    try:
        font_big = "/Users/ricksabchez/workspace/projects/craft-reel-video/fonts/Vazirmatn-Black.ttf"
        font_med = "/Users/ricksabchez/workspace/projects/craft-reel-video/fonts/Vazirmatn-Medium.ttf"
    except Exception:
        font_big = font_med = None
    from PIL import ImageFont

    d = ImageDraw.Draw(og)
    f1 = ImageFont.truetype(font_big, 62) if font_big else ImageFont.load_default()
    f2 = ImageFont.truetype(font_med, 34) if font_med else ImageFont.load_default()
    f3 = ImageFont.truetype(font_med, 28) if font_med else ImageFont.load_default()
    d.text((330, 236), "EHSAN MANSOORI", font=f2, fill=(245, 158, 11))
    d.text((330, 288), "CINEMA REVIEWS", font=f1, fill=(248, 250, 252))
    d.text((330, 372), "@ehsanmansoori", font=f3, fill=(148, 163, 184))
    d.text((330, 414), "youtube  |  instagram  |  x", font=f3, fill=(100, 116, 139))
    og.save(imgs / "og-image.jpg", quality=88, optimize=True)


def main() -> None:
    eps = load_episodes()
    html = render(eps)
    (ROOT / "index.html").write_text(html, encoding="utf-8")
    write_side_files(eps)
    write_images()
    films_with_list = sum(len(e["films"]) for e in eps)
    print(f"episodes: {len(eps)} | chapter rows: {films_with_list}")
    print("wrote index.html, robots.txt, sitemap.xml, 404.html, manifest.json, images")


if __name__ == "__main__":
    main()
