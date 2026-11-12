"""Link parsing and comment matching: English, Bengali, Banglish, Hindi, Hinglish."""
import re
import unicodedata
from difflib import SequenceMatcher
from urllib.parse import urlparse, parse_qs

BN_MAP = dict(zip("কখগঘঙচছজঝঞটঠডঢণতথদধনপফবভমযরলশষসৎং", "KKGGNCCJJNTTDDNTTDDNPFBBMJRLSSSTN"))
HI_MAP = dict(zip("कखगघङचछजझञटठडढणतथदधनपफबभमरलवशषसं", "KKGGNCCJJNTTDDNTTDDNPFBBMRLBSSSN"))
IND_MAP = {**BN_MAP, **HI_MAP}
LAT = dict(k="K", q="K", c="K", x="K", g="G", j="J", z="J", t="T", d="D", n="N",
           p="P", f="F", b="B", v="B", m="M", r="R", l="L", s="S")
DIGITS = str.maketrans("০১২৩৪৫৬৭৮৯०१२३४५६७८९", "01234567890123456789")
DIGRAPHS = (("cch", "C"), ("ph", "F"), ("ch", "C"), ("sh", "S"), ("kh", "K"),
            ("gh", "G"), ("bh", "B"), ("dh", "D"), ("th", "T"))


def parse_link(url):
    """Returns (type, video_id) or (None, error_message)."""
    try:
        u = urlparse(url.strip())
    except ValueError:
        return None, "That doesn't look like a valid link."
    host = (u.hostname or "").removeprefix("www.").removeprefix("m.")
    if host not in ("youtube.com", "youtu.be"):
        return None, "Enter a YouTube link."
    if host == "youtu.be":
        return "video", u.path.strip("/").split("/")[0]
    if u.path.startswith("/post/") or "/community" in u.path:
        return "post", None
    m = re.match(r"^/(shorts|embed|live)/([\w-]{11})", u.path)
    if m:
        return ("short" if m[1] == "shorts" else "video"), m[2]
    v = parse_qs(u.query).get("v")
    if v:
        return "video", v[0]
    return None, "Couldn't find a video ID in that link."


_UNITS = {"সেকেন্ড": "second", "মিনিট": "minute", "ঘণ্টা": "hour", "ঘন্টা": "hour", "দিন": "day",
          "সপ্তাহ": "week", "মাস": "month", "বছর": "year", "सेकंड": "second", "मिनट": "minute",
          "घंटे": "hour", "घंटा": "hour", "दिन": "day", "सप्ताह": "week", "हफ़्ते": "week",
          "हफ्ते": "week", "महीने": "month", "महीना": "month", "साल": "year", "वर्ष": "year"}
UNITS = {unicodedata.normalize("NFKC", k): v for k, v in _UNITS.items()}


def english_time(text):
    """'3 বছর পূর্বে' / '3 साल पहले' -> '3 years ago'. English text is returned unchanged."""
    t = unicodedata.normalize("NFKC", text).translate(DIGITS)
    m = re.search(r"(\d+)\s*(\S+)", t)
    unit = UNITS.get(m[2]) if m else None
    if not unit:
        return text
    n = int(m[1])
    out = f"{n} {unit}{'' if n == 1 else 's'} ago"
    return out + (" (edited)" if re.search("সম্পাদ|संपादित", t) else "")


def norm(s):
    s = unicodedata.normalize("NFKC", s).lower().translate(DIGITS)
    s = re.sub(r"[\u200b-\u200d\ufeff]", "", s)
    s = "".join(c for c in s if c.isalnum() or c.isspace() or unicodedata.category(c)[0] == "M")
    return re.sub(r"\s+", " ", s).strip()


def script(s):
    if re.search(r"[\u0980-\u09ff]", s):
        return "bn"
    return "hi" if re.search(r"[\u0900-\u097f]", s) else "lat"


def skel(s):
    """Consonant sounds only: 'bhalo', 'valo', 'ভালো' and 'भालो' all become 'BL'."""
    s = norm(s)
    for a, b in DIGRAPHS:
        s = s.replace(a, b)
    s = "".join(
        LAT.get(c, "") if "a" <= c <= "z" else IND_MAP.get(c, "") if "\u0900" <= c <= "\u09ff" else c for c in s
    )
    return re.sub(r"(.)\1+", r"\1", re.sub(r"\s", "", s))


def similar(a, b):
    a, b = a[:150], b[:150]
    m = max(len(a), len(b))
    if not m or abs(len(a) - len(b)) > m * 0.25:
        return False
    return SequenceMatcher(None, a, b).ratio() >= 0.85


def same_user(a, b):
    if norm(a) == norm(b):
        return True
    return script(a) != script(b) and len(skel(a)) >= 2 and skel(a) == skel(b)


class Target:
    def __init__(self, comment, username):
        self.text, self.sk, self.user = norm(comment), skel(comment), username

    def score(self, c):
        """Returns (score, match_type, author_match) or None if no match."""
        t = norm(c["text"])
        if t == self.text:
            kind = "exact"
        elif self.text in t:
            kind = "partial"
        elif len(self.sk) >= 8 and (self.sk in (k := skel(c["text"])) or similar(k, self.sk)):
            kind = "similar"
        else:
            return None
        author_ok = not self.user or same_user(c["author"], self.user)
        return (4 if author_ok else 0) + {"exact": 3, "partial": 2, "similar": 1}[kind], kind, author_ok
