#!/usr/bin/env python3
"""
Resolve every covered film to TMDB metadata: poster, backdrop, Persian title,
synopsis, runtime, genres, director, cast, country, rating and IMDb id.

TMDB is the single source of truth for film info (per project rule).
Writes build/films_meta.json
"""
from __future__ import annotations

import json
import ssl
import time
import urllib.parse
import urllib.request
from pathlib import Path


def _ssl_context() -> ssl.SSLContext:
    try:
        import certifi  # type: ignore

        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE  # local python without a CA bundle
        return ctx


SSL_CTX = _ssl_context()

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
API_KEY = "1dc4cbf81f0accf4fa108820d551dafc"
LANG_FA = "fa-IR"
LANG_EN = "en-US"

# names the channel spelled loosely, mapped to a clean search query
QUERY_FIX = {
    "without": None,
    "3iron": "3-Iron",
    "21grams": "21 Grams",
    "devils advocate": "The Devil's Advocate",
    "the gentelmen": "The Gentlemen",
    "the secret in their eyes 2009": "The Secret in Their Eyes",
    "legend 1900": "The Legend of 1900",
    "august:osage county": "August: Osage County",
    "in bruges": "In Bruges",
    "eternal sunshine of the spotless mind": "Eternal Sunshine of the Spotless Mind",
    "kite runner": "The Kite Runner",
    "tick, tick...boom!": "tick, tick... BOOM!",
    "are you there god? it's me, margaret.": "Are You There God? It's Me, Margaret.",
    "spider-man: across the spider-verse": "Spider-Man: Across the Spider-Verse",
    "shawshank redemption": "The Shawshank Redemption",
    "the collini case": "The Collini Case",
    "the lives of others": "The Lives of Others",
    "mother!": "mother!",
    "the handmaiden": "The Handmaiden",
    "the wailing": "The Wailing",
    "requiem for a dream": "Requiem for a Dream",
    "silver linings playbook": "Silver Linings Playbook",
    "children of men": "Children of Men",
    "saving private ryan": "Saving Private Ryan",
    "run lola run": "Run Lola Run",
    "the father": "The Father",
    "i saw the devil": "I Saw the Devil",
    "persian lessons": "Persian Lessons",
    "shutter island": "Shutter Island",
    "the worst person in the world": "The Worst Person in the World",
    "night on earth": "Night on Earth",
    "memories of murder": "Memories of Murder",
    "there will be blood": "There Will Be Blood",
    "the northman": "The Northman",
    "cinema paradiso": "Cinema Paradiso",
    "pieces of a woman": "Pieces of a Woman",
    "better days": "Better Days",
    "the farewell": "The Farewell",
    "ex machina": "Ex Machina",
    "amores perros": "Amores Perros",
    "12 angry men": "12 Angry Men",
    "train to busan": "Train to Busan",
    "nocturnal animals": "Nocturnal Animals",
    "bohemian rhapsody": "Bohemian Rhapsody",
    "little women": "Little Women",
    "the unknown woman": "The Unknown Woman",
    "the sea inside": "The Sea Inside",
    "green book": "Green Book",
    "wild tales": "Wild Tales",
    "knives out": "Knives Out",
    "gone girl": "Gone Girl",
    "the hangover": "The Hangover",
    "the platform": "The Platform",
    "the lobster": "The Lobster",
    "pulp fiction": "Pulp Fiction",
    "the lives of others": "The Lives of Others",
    "another round": "Another Round",
    "before sunrise/before sunset/before midnight": "Before Sunrise",
}

# year hints keep search results from drifting to remakes or namesakes
YEAR_HINT = {
    "wild tales": 2014, "green book": 2018, "oldboy": 2003, "drive": 2011,
    "nocturnal animals": 2016, "the collini case": 2019, "knives out": 2019,
    "gone girl": 2014, "the hangover": 2009, "devils advocate": 1997,
    "the lives of others": 2006, "the gentelmen": 2019, "3iron": 2004,
    "the platform": 2019, "inception": 2010, "21grams": 2003, "the sea inside": 2004,
    "bohemian rhapsody": 2018, "little women": 2019, "interstellar": 2014,
    "room": 2015, "the unknown woman": 2006, "mud": 2012, "the lobster": 2015,
    "pulp fiction": 1994, "locke": 2013, "joker": 2019, "parasite": 2019,
    "1917": 2019, "shawshank redemption": 1994, "silver linings playbook": 2012,
    "babel": 2006, "the secret in their eyes 2009": 2009,
    "before sunrise/before sunset/before midnight": 1995, "12 angry men": 1957,
    "omar": 2013, "amores perros": 2000, "fences": 2016, "ex machina": 2014,
    "the handmaiden": 2016, "the hunt": 2012, "the wailing": 2016,
    "requiem for a dream": 2000, "wonder": 2017, "children of men": 2006,
    "tenet": 2020, "another round": 2020, "godfather": 1972, "mother!": 2017,
    "her": 2013, "the gift": 2015, "train to busan": 2016, "better days": 2019,
    "pieces of a woman": 2020, "saving private ryan": 1998, "run lola run": 1998,
    "the father": 2020, "i saw the devil": 2010, "luca": 2021,
    "predestination": 2014, "persian lessons": 2020, "shutter island": 2010,
    "august:osage county": 2013, "legend 1900": 1998, "in bruges": 2008,
    "eternal sunshine of the spotless mind": 2004, "kite runner": 2007, "coda": 2021,
    "rushmore": 1998, "the worst person in the world": 2021, "night on earth": 1991,
    "memories of murder": 2003, "tick, tick...boom!": 2021, "there will be blood": 2007,
    "the northman": 2022, "incendies": 2010, "cinema paradiso": 1988,
    "victoria": 2015, "air": 2023, "snatch": 2000,
    "spider-man: across the spider-verse": 2023, "the farewell": 2019,
    "are you there god? it's me, margaret.": 2023,
    "the wave": 2008, "silenced": 2011, "late shift": 2019, "obsession": 2026,
}



# pinned TMDB ids for titles whose search result is ambiguous (verified by hand)
PIN = {
    "wild tales": 265195,
    "oldboy": 670,
    "the lives of others": 582,
    "the sea inside": 1913,
    "the handmaiden": 290098,
    "another round": 580175,
    "memories of murder": 11423,
    "the wave": 7735,
    "late shift": 1356670,
    "the worst person in the world": 660120,
    "silenced": 81481,
    "parasite": 496243,
    "the platform": 619264,
    "wonder": 406997,
    "the hunt": 103663,
    "the wailing": 293670,
    "better days": 575813,
    "omar": 187028,
    "i saw the devil": 49797,
    "train to busan": 396535,
    "3iron": 1280,
}

def api(path: str, params: dict, lang: str = LANG_FA) -> dict:
    p = dict(params)
    p["api_key"] = API_KEY
    p["language"] = lang
    url = "https://api.themoviedb.org/3" + path + "?" + urllib.parse.urlencode(p)
    req = urllib.request.Request(url, headers={"User-Agent": "ehsan-archive/1.0"})
    with urllib.request.urlopen(req, timeout=30, context=SSL_CTX) as r:
        return json.loads(r.read().decode())


def norm(s: str) -> str:
    return "".join(ch for ch in (s or "").lower() if ch.isalnum() or ch == " ").strip()


def pick(results: list[dict], title: str, year: int | None) -> dict | None:
    if not results:
        return None
    want = norm(title)

    def score(m: dict) -> tuple:
        names = {norm(m.get("title", "")), norm(m.get("original_title", ""))}
        exact = want in names or any(want and want in n for n in names)
        y = (m.get("release_date") or "")[:4]
        dy = abs(int(y) - year) if (year and y.isdigit()) else 99
        return (0 if exact else 1, dy, -(m.get("popularity") or 0))

    best = sorted(results, key=score)[0]
    y = (best.get("release_date") or "")[:4]
    if year and y.isdigit() and abs(int(y) - year) > 1:
        return None
    return best


def main() -> None:
    raw = json.loads((BUILD / "episodes_raw.json").read_text(encoding="utf-8"))
    titles: list[str] = []
    for item in raw.values():
        for f in item["films"]:
            n = f["name"].replace("\u200b", "").strip()
            if not n or n.startswith(("معرفی", "جریان", "اولویت")):
                continue
            if n.lower() not in [t.lower() for t in titles]:
                titles.append(n)
    # popcorn + bilit films are part of the library too
    extra = ["The Wave", "Obsession", "Late Shift", "Silenced", "Predestination"]
    for e in extra:
        if e.lower() not in [t.lower() for t in titles]:
            titles.append(e)

    cache_path = BUILD / "films_meta.json"
    meta: dict = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.exists() else {}
    meta = {k: v for k, v in meta.items() if v.get("source") == "tmdb"}

    for i, name in enumerate(titles, 1):
        key = name.lower()
        if key in meta and meta[key].get("ok"):
            continue
        query = QUERY_FIX.get(key, name)
        if key in QUERY_FIX and QUERY_FIX[key] is None:
            meta[key] = {"name": name, "ok": False, "source": "tmdb", "reason": "skipped"}
            continue
        year = YEAR_HINT.get(key)
        try:
            pin = PIN.get(key)
            if pin:
                m = {"id": pin, "title": query, "original_title": query}
            else:
                found = api("/search/movie", {"query": query, "include_adult": "false"})
                m = pick(found.get("results", []), query, year)
            if not m:
                meta[key] = {"name": name, "ok": False, "source": "tmdb", "reason": "no confident match"}
                print(f"{i:>3}. MISS {name}")
                time.sleep(0.06)
                continue
            mid = m["id"]
            d = api(f"/movie/{mid}", {"append_to_response": "credits,release_dates"})
            if not (d.get("overview") or "").strip():
                d_en = api(f"/movie/{mid}", {"append_to_response": "credits"}, LANG_EN)
                d["overview"] = d_en.get("overview") or ""
                d.setdefault("title_en", d_en.get("title"))
            crew = (d.get("credits") or {}).get("crew") or []
            cast = (d.get("credits") or {}).get("cast") or []
            directors = [c["name"] for c in crew if c.get("job") == "Director"][:2]
            countries = [c.get("name") for c in (d.get("production_countries") or [])][:2]
            release = d.get("release_date") or m.get("release_date") or ""
            meta[key] = {
                "name": name,
                "ok": True,
                "source": "tmdb",
                "tmdb_id": mid,
                "title_fa": d.get("title") or m.get("title"),
                "title_en": m.get("original_title") or d.get("original_title"),
                "year": int(release[:4]) if release[:4].isdigit() else None,
                "poster": ("https://image.tmdb.org/t/p/w500" + d["poster_path"]) if d.get("poster_path") else None,
                "poster_small": ("https://image.tmdb.org/t/p/w342" + d["poster_path"]) if d.get("poster_path") else None,
                "backdrop": ("https://image.tmdb.org/t/p/w780" + d["backdrop_path"]) if d.get("backdrop_path") else None,
                "overview": (d.get("overview") or "").strip(),
                "runtime": d.get("runtime") or None,
                "genres": [g["name"] for g in (d.get("genres") or [])][:3],
                "director": directors,
                "cast": [c["name"] for c in cast][:4],
                "country": countries,
                "rating": round(d.get("vote_average") or 0, 1),
                "votes": d.get("vote_count") or 0,
                "imdb": d.get("imdb_id"),
                "tmdb_url": f"https://www.themoviedb.org/movie/{mid}",
            }
            print(f"{i:>3}. OK   {name} -> {meta[key]['title_fa']} ({meta[key]['year']}) "
                  f"| poster={'y' if meta[key]['poster'] else 'N'} | rate={meta[key]['rating']}")
        except Exception as e:
            meta[key] = {"name": name, "ok": False, "source": "tmdb", "reason": str(e)[:80]}
            print(f"{i:>3}. ERR  {name} :: {str(e)[:60]}")
        time.sleep(0.06)

    cache_path.write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    ok = sum(1 for v in meta.values() if v.get("ok"))
    posters = sum(1 for v in meta.values() if v.get("poster"))
    print(f"\ntotal {len(meta)} | resolved {ok} | poster {posters}")
    misses = [v["name"] for v in meta.values() if not v.get("ok")]
    if misses:
        print("misses:", ", ".join(misses))


if __name__ == "__main__":
    main()
