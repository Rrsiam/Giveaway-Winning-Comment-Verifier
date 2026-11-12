import os
import time
from flask import Flask, jsonify, render_template, request
from youtube_comment_downloader import YoutubeCommentDownloader, SORT_BY_RECENT
from matcher import Target, english_time, parse_link

app = Flask(__name__)
MAX_COMMENTS = int(os.getenv("MAX_COMMENTS", 20000))
TIMEOUT = int(os.getenv("SCAN_TIMEOUT", 120))  # seconds
GOOD = 6  # author match + exact/partial text: stop early
cache = {}


@app.get("/")
def home():
    return render_template("index.html")


@app.post("/api/verify")
def verify():
    d = request.get_json(silent=True) or {}
    url, comment, user = d.get("url", ""), d.get("comment", ""), (d.get("username") or "").strip()
    if not url or not comment.strip():
        return jsonify(error="Enter a link and the comment text."), 400
    if len(comment) > 1000 or len(user) > 100:
        return jsonify(error="Input is too long."), 400
    kind, vid = parse_link(url)
    if kind is None:
        return jsonify(error=vid), 400
    if kind == "post":
        return jsonify(error="Community posts aren't supported."), 422

    key = (vid, comment.strip(), user)
    hit = cache.get(key)
    if hit and time.time() - hit[0] < 600:
        return jsonify(hit[1])

    target = Target(comment, user)
    if not target.text:
        return jsonify(error="The comment has no readable text."), 400

    best, scanned, complete, t0 = None, 0, True, time.time()
    try:
        dl, link = YoutubeCommentDownloader(), f"https://www.youtube.com/watch?v={vid}"
        try:
            gen = dl.get_comments_from_url(link, sort_by=SORT_BY_RECENT, language="en")
        except TypeError:  # older library version without the language option
            gen = dl.get_comments_from_url(link, sort_by=SORT_BY_RECENT)
        for c in gen:
            scanned += 1
            r = target.score(c)
            if r and (not best or r[0] > best["score"]):
                best = dict(score=r[0], matchType=r[1], authorMatch=r[2], author=c["author"],
                            text=c["text"], likes=c.get("votes", "0"), publishedAt=english_time(c.get("time", "")),
                            commentUrl=f"https://www.youtube.com/watch?v={vid}&lc={c['cid']}")
            if best and best["score"] >= GOOD:
                complete = None
                break
            if scanned >= MAX_COMMENTS or time.time() - t0 > TIMEOUT:
                complete = False
                break
    except Exception:
        return jsonify(error="Couldn't read comments. The video may be private, or YouTube blocked this server."), 502

    if scanned == 0:
        return jsonify(error="No comments could be read. Comments may be off, or YouTube blocked this server."), 502

    verdict = "not_found"
    if best:
        verdict = "author_mismatch" if not best["authorMatch"] else "likely" if best["matchType"] == "similar" else "verified"
    body = dict(verdict=verdict, match=best, scanned=scanned, complete=complete)
    cache[key] = (time.time(), body)
    return jsonify(body)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
