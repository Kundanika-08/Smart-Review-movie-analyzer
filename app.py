from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from functools import wraps
from datetime import datetime
from html import escape
import json
import os
import urllib.parse
from model.predict import predict_review

app = Flask(__name__)
app.secret_key = "smra_movie_secret_key"

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")
USERS_FILE = os.path.join(DATA_DIR, "users.json")
REVIEWS_FILE = os.path.join(DATA_DIR, "movie_reviews.json")


MOVIE_ROWS = [
    {
        "title": "Trending Now",
        "movies": [
            {"name": "Parasite", "poster": "https://upload.wikimedia.org/wikipedia/en/5/53/Parasite_%282019_film%29.png"},
            {"name": "Oppenheimer", "poster": "https://upload.wikimedia.org/wikipedia/en/4/4a/Oppenheimer_%28film%29.jpg"},
            {"name": "Joker", "poster": "https://upload.wikimedia.org/wikipedia/en/e/e1/Joker_%282019_film%29_poster.jpg"},
            {"name": "1917", "poster": "https://upload.wikimedia.org/wikipedia/en/f/fe/1917_%282019%29_Film_Poster.jpeg"},
            {"name": "Moonlight", "poster": "https://upload.wikimedia.org/wikipedia/en/8/84/Moonlight_%282016_film%29.png"},
            {"name": "The Shape of Water", "poster": "https://upload.wikimedia.org/wikipedia/en/d/d7/The_Shape_of_Water_%282017_film%29.png"},
            {"name": "Everything Everywhere All at Once", "poster": "https://upload.wikimedia.org/wikipedia/en/8/8e/Everything_Everywhere_All_at_Once.jpg"},
            {"name": "The Artist", "poster": "https://upload.wikimedia.org/wikipedia/en/a/a2/The_Artist_Poster.jpg"},
        ],
    },
    {
        "title": "Drama Hits",
        "movies": [
            {"name": "Forrest Gump", "poster": "https://upload.wikimedia.org/wikipedia/en/6/67/Forrest_Gump_poster.jpg"},
            {"name": "Titanic", "poster": "https://upload.wikimedia.org/wikipedia/en/2/22/Titanic_poster.jpg"},
            {"name": "Gladiator", "poster": "https://upload.wikimedia.org/wikipedia/en/8/8d/Gladiator_ver1.jpg"},
            {"name": "A Beautiful Mind", "poster": "https://upload.wikimedia.org/wikipedia/en/b/b8/A_Beautiful_Mind_Poster.jpg"},
            {"name": "Green Book", "poster": "https://upload.wikimedia.org/wikipedia/en/5/5b/Green_Book_poster.png"},
            {"name": "Slumdog Millionaire", "poster": "https://upload.wikimedia.org/wikipedia/en/9/96/Slumdog_Millionaire_poster.jpg"},
            {"name": "12 Years a Slave", "poster": "https://upload.wikimedia.org/wikipedia/en/5/5c/12_Years_a_Slave_film_poster.jpg"},
            {"name": "The Godfather", "poster": "https://upload.wikimedia.org/wikipedia/en/1/1c/Godfather_ver1.jpg"},
        ],
    },
    {
        "title": "Thrillers",
        "movies": [
            {"name": "The Silence of the Lambs", "poster": "https://upload.wikimedia.org/wikipedia/en/8/86/The_Silence_of_the_Lambs_poster.jpg"},
            {"name": "No Country for Old Men", "poster": "https://upload.wikimedia.org/wikipedia/en/8/8b/No_Country_for_Old_Men_poster.jpg"},
            {"name": "Black Swan", "poster": "https://upload.wikimedia.org/wikipedia/en/9/9f/Black_Swan_poster.jpg"},
            {"name": "Shutter Island", "poster": "https://upload.wikimedia.org/wikipedia/en/7/76/Shutterislandposter.jpg"},
            {"name": "Se7en", "poster": "https://upload.wikimedia.org/wikipedia/en/6/68/Seven_%28movie%29_poster.jpg"},
            {"name": "Zodiac", "poster": "https://upload.wikimedia.org/wikipedia/en/3/3a/Zodiac2007Poster.jpg"},
            {"name": "Prisoners", "poster": "https://upload.wikimedia.org/wikipedia/en/3/3c/Prisoners2013Poster.jpg"},
            {"name": "Nightcrawler", "poster": "https://upload.wikimedia.org/wikipedia/en/8/84/Nightcrawler2014Poster.jpg"},
        ],
    },
    {
        "title": "Horror Picks",
        "movies": [
            {"name": "Get Out", "poster": "https://upload.wikimedia.org/wikipedia/en/a/a3/Get_Out_poster.png"},
            {"name": "The Exorcist", "poster": "https://upload.wikimedia.org/wikipedia/en/7/7b/Exorcist_ver2.jpg"},
            {"name": "The Shining", "poster": "https://upload.wikimedia.org/wikipedia/en/1/1f/Shiningposter.jpg"},
            {"name": "Hereditary", "poster": "https://upload.wikimedia.org/wikipedia/en/d/d9/Hereditary.png"},
            {"name": "A Quiet Place", "poster": "https://upload.wikimedia.org/wikipedia/en/a/a0/A_Quiet_Place_film_poster.png"},
            {"name": "The Conjuring", "poster": "https://upload.wikimedia.org/wikipedia/en/1/1f/Conjuring_poster.jpg"},
            {"name": "Us", "poster": "https://upload.wikimedia.org/wikipedia/en/0/0b/Us_2019_poster.jpg"},
            {"name": "Insidious", "poster": "https://upload.wikimedia.org/wikipedia/en/2/2e/Insidious_poster.jpg"},
        ],
    },
]

MOVIE_DESCRIPTIONS = {
    "Parasite": "A poor family slowly enters the lives of a wealthy household in this sharp social thriller.",
    "Oppenheimer": "The story of physicist J. Robert Oppenheimer and the moral weight behind the atomic bomb.",
    "Joker": "An isolated comedian spirals into chaos and transforms into Gotham's most feared villain.",
    "1917": "Two soldiers race across enemy territory to deliver a message and save hundreds of lives.",
    "Moonlight": "A poetic coming-of-age drama about identity, love, and survival.",
    "The Shape of Water": "A lonely woman forms a deep bond with a mysterious aquatic creature.",
    "Everything Everywhere All at Once": "A multiverse adventure where one woman must connect countless versions of her life.",
    "The Artist": "A silent-film star struggles to adapt when Hollywood embraces sound.",
    "Forrest Gump": "A gentle man witnesses and influences major moments of American history.",
    "Titanic": "A love story unfolds aboard the ill-fated RMS Titanic.",
    "Gladiator": "A betrayed Roman general fights his way back for honor and revenge.",
    "A Beautiful Mind": "A brilliant mathematician battles schizophrenia while chasing discovery.",
    "Green Book": "An unlikely friendship forms during a concert tour through a divided America.",
    "Slumdog Millionaire": "A young man from Mumbai reflects on his life during a game show.",
    "12 Years a Slave": "The true story of a free man kidnapped and sold into slavery.",
    "The Godfather": "A powerful crime family struggles with loyalty, power, and legacy.",
    "The Silence of the Lambs": "An FBI trainee seeks help from a brilliant imprisoned killer.",
    "No Country for Old Men": "A hunter finds stolen money and is hunted by a relentless assassin.",
    "Black Swan": "A dancer's pursuit of perfection drives her into psychological darkness.",
    "Shutter Island": "A U.S. Marshal investigates a disappearance at a remote asylum.",
    "Se7en": "Two detectives hunt a serial killer using the seven deadly sins.",
    "Zodiac": "Investigators and journalists obsess over the identity of the Zodiac killer.",
    "Prisoners": "A father takes extreme steps after his daughter goes missing.",
    "Nightcrawler": "An ambitious cameraman exploits crime scenes to climb media ranks.",
    "Get Out": "A weekend visit uncovers disturbing secrets beneath polite smiles.",
    "The Exorcist": "A family seeks help when a young girl shows terrifying behavior.",
    "The Shining": "Isolation in a haunted hotel pushes a writer toward madness.",
    "Hereditary": "A family uncovers a chilling legacy after a tragedy.",
    "A Quiet Place": "A family survives in silence to avoid monsters that hunt by sound.",
    "The Conjuring": "Paranormal investigators confront a dark presence in a farmhouse.",
    "Us": "A family is hunted by terrifying doubles of themselves.",
    "Insidious": "Parents enter a supernatural realm to rescue their son.",
}

MOOD_PROFILES = {
    "mind-bending": {
        "label": "Mind-Bending",
        "genre_weights": {"Thrillers": 1.0, "Horror Picks": 0.35, "Drama Hits": 0.2, "Trending Now": 0.3},
        "keywords": ["mystery", "identity", "psychological", "killer", "multiverse", "secrets"],
    },
    "emotional": {
        "label": "Emotional",
        "genre_weights": {"Drama Hits": 1.0, "Trending Now": 0.4, "Thrillers": 0.15, "Horror Picks": 0.05},
        "keywords": ["love", "friendship", "family", "legacy", "coming-of-age", "story"],
    },
    "dark": {
        "label": "Dark",
        "genre_weights": {"Horror Picks": 1.0, "Thrillers": 0.8, "Trending Now": 0.25, "Drama Hits": 0.2},
        "keywords": ["haunted", "killer", "madness", "dark", "fear", "chaos"],
    },
    "feel-good": {
        "label": "Feel-Good",
        "genre_weights": {"Drama Hits": 0.9, "Trending Now": 0.7, "Thrillers": 0.05, "Horror Picks": 0.05},
        "keywords": ["friendship", "bond", "hope", "adventure", "heart", "inspiring"],
    },
}


def slugify(name):
    safe = "".join(ch.lower() if ch.isalnum() else "-" for ch in name)
    while "--" in safe:
        safe = safe.replace("--", "-")
    return safe.strip("-")


MOVIE_INDEX = {
    movie["name"]: {
        "poster": movie["poster"],
        "description": MOVIE_DESCRIPTIONS.get(movie["name"], "No description available."),
        "slug": slugify(movie["name"]),
    }
    for row in MOVIE_ROWS
    for movie in row["movies"]
}

def ensure_storage():
    os.makedirs(DATA_DIR, exist_ok=True)


def load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return default


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def login_required(route_fn):
    @wraps(route_fn)
    def wrapper(*args, **kwargs):
        if not session.get("username"):
            return redirect(url_for("index"))
        return route_fn(*args, **kwargs)

    return wrapper


def movie_stats(movie_name):
    reviews = movie_reviews.get(movie_name, [])
    if not reviews:
        return {"avg": None, "count": 0}
    avg = round(sum(float(r["rating"]) for r in reviews) / len(reviews), 1)
    return {"avg": avg, "count": len(reviews)}


def movie_payload(movie_name, user_cart):
    movie_info = MOVIE_INDEX.get(movie_name)
    if not movie_info:
        return None

    stats = movie_stats(movie_name)
    return {
        "name": movie_name,
        "slug": movie_info.get("slug", slugify(movie_name)),
        "description": movie_info.get("description", "No description available."),
        "poster_url": url_for("poster_art", movie_name=movie_name),
        "avg_rating": stats["avg"],
        "review_count": stats["count"],
        "in_cart": movie_name in user_cart,
    }


def movie_genre(movie_name):
    for row in MOVIE_ROWS:
        for movie in row["movies"]:
            if movie["name"] == movie_name:
                return row["title"]
    return "Movie"


def wrap_title_lines(movie_name, max_len=13, max_lines=3):
    words = movie_name.split()
    lines = []
    current = ""
    for word in words:
        candidate = (current + " " + word).strip()
        if len(candidate) <= max_len:
            current = candidate
            continue
        if current:
            lines.append(current)
        current = word
        if len(lines) == max_lines - 1:
            break
    if len(lines) < max_lines and current:
        lines.append(current)
    return lines[:max_lines]


def parse_iso_date(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def recommendation_score(movie_name, mood_key):
    profile = MOOD_PROFILES.get(mood_key)
    if not profile:
        return None

    genre = movie_genre(movie_name)
    genre_score = profile["genre_weights"].get(genre, 0.1)
    desc = MOVIE_DESCRIPTIONS.get(movie_name, "").lower()
    keyword_hits = sum(1 for kw in profile["keywords"] if kw in desc)
    keyword_score = min(keyword_hits / max(len(profile["keywords"]), 1), 0.6)

    stats = movie_stats(movie_name)
    avg_rating = stats["avg"] if stats["avg"] is not None else 3.0
    review_count = stats["count"]

    reviews = movie_reviews.get(movie_name, [])
    positive_ratio = 0.5
    freshness_score = 0.25

    if reviews:
        positive_count = sum(1 for r in reviews if r.get("sentiment") == "Positive")
        positive_ratio = positive_count / len(reviews)

        latest = None
        for review in reviews:
            dt = parse_iso_date(review.get("created_at"))
            if dt and (latest is None or dt > latest):
                latest = dt

        if latest:
            days_old = max((datetime.utcnow() - latest).days, 0)
            freshness_score = max(0.0, 1.0 - min(days_old, 30) / 30)

    confidence_score = min(review_count / 7, 1.0)

    score = (
        avg_rating * 0.55
        + positive_ratio * 1.25
        + genre_score * 1.1
        + keyword_score * 0.8
        + freshness_score * 0.55
        + confidence_score * 0.35
    )

    reason = (
        f"{profile['label']} fit from {genre.lower()} with "
        f"{avg_rating:.1f}/5 rating and {review_count} review(s)."
    )
    return {
        "score": score,
        "reason": reason,
        "avg_rating": avg_rating,
        "review_count": review_count,
    }


ensure_storage()
users = load_json(USERS_FILE, {})
movie_reviews = load_json(REVIEWS_FILE, {})


@app.route("/")
def index():
    if session.get("username"):
        return redirect(url_for("home"))
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def do_login():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    if username not in users or users[username].get("password") != password:
        return render_template("login.html", error="Invalid username or password")

    session["username"] = username
    return redirect(url_for("home"))


@app.route("/signup")
def signup():
    return render_template("signup.html")


@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    if not username or not password:
        return render_template("signup.html", error="Please fill all fields")

    if username in users:
        return render_template("signup.html", error="User already exists")

    users[username] = {"password": password, "cart": []}
    save_json(USERS_FILE, users)
    return redirect(url_for("index"))


@app.route("/logout", methods=["POST"])
def logout():
    session.pop("username", None)
    return redirect(url_for("index"))


@app.route("/home")
@login_required
def home():
    username = session["username"]
    user_cart = set(users.get(username, {}).get("cart", []))

    rows = []
    for row in MOVIE_ROWS:
        movies = []
        for movie in row["movies"]:
            payload = movie_payload(movie["name"], user_cart)
            if payload:
                movies.append(payload)
        rows.append({"title": row["title"], "movies": movies})

    return render_template(
        "home.html",
        username=username,
        movie_rows=rows,
        cart_count=len(user_cart),
    )


@app.route("/cart")
@login_required
def cart():
    username = session["username"]
    user_cart = users.get(username, {}).get("cart", [])
    user_cart_set = set(user_cart)

    cart_movies = []
    for movie_name in user_cart:
        payload = movie_payload(movie_name, user_cart_set)
        if payload:
            cart_movies.append(payload)

    return render_template(
        "cart.html",
        username=username,
        cart_movies=cart_movies,
        cart_count=len(cart_movies),
    )


@app.route("/cart/remove", methods=["POST"])
@login_required
def cart_remove():
    movie = request.form.get("movie", "").strip()
    username = session["username"]

    if not movie:
        return redirect(url_for("cart"))

    users.setdefault(username, {"password": "", "cart": []})
    users[username].setdefault("cart", [])
    users[username]["cart"] = [m for m in users[username]["cart"] if m != movie]
    save_json(USERS_FILE, users)
    return redirect(url_for("cart"))


@app.route("/api/review", methods=["POST"])
@login_required
def api_review():
    movie = request.form.get("movie", "").strip()
    review_text = request.form.get("review", "").strip()
    username = session["username"]

    if not movie:
        return jsonify({"ok": False, "error": "Please choose a movie first."}), 400

    if not review_text:
        return jsonify({"ok": False, "error": "Please fill this field."}), 400

    sentiment, rating, stars = predict_review(review_text)
    movie_reviews.setdefault(movie, []).append(
        {
            "user": username,
            "text": review_text,
            "sentiment": sentiment,
            "rating": rating,
            "stars": stars,
            "created_at": datetime.utcnow().isoformat(),
        }
    )
    save_json(REVIEWS_FILE, movie_reviews)

    stats = movie_stats(movie)
    return jsonify(
        {
            "ok": True,
            "movie": movie,
            "sentiment": sentiment,
            "rating": rating,
            "stars": stars,
            "avg_rating": stats["avg"],
            "review_count": stats["count"],
        }
    )


@app.route("/api/movie/<path:movie>/reviews", methods=["GET"])
@login_required
def api_movie_reviews(movie):
    movie_name = urllib.parse.unquote(movie)
    reviews = movie_reviews.get(movie_name, [])
    sorted_reviews = sorted(
        reviews,
        key=lambda r: r.get("created_at", ""),
        reverse=True,
    )
    info = MOVIE_INDEX.get(movie_name, {})
    return jsonify(
        {
            "ok": True,
            "movie": movie_name,
            "description": info.get("description", "No description available."),
            "reviews": sorted_reviews,
        }
    )


@app.route("/api/matchmaker", methods=["GET"])
@login_required
def api_matchmaker():
    mood = request.args.get("mood", "").strip().lower()
    profile = MOOD_PROFILES.get(mood)
    if not profile:
        return jsonify({"ok": False, "error": "Please choose a valid mood."}), 400

    candidates = []
    for row in MOVIE_ROWS:
        for movie in row["movies"]:
            movie_name = movie["name"]
            score_data = recommendation_score(movie_name, mood)
            if not score_data:
                continue
            candidates.append((score_data["score"], movie_name, score_data))

    if not candidates:
        return jsonify({"ok": False, "error": "No movies available right now."}), 404

    candidates.sort(key=lambda item: item[0], reverse=True)
    _, best_movie, score_data = candidates[0]
    payload = movie_payload(best_movie, set())

    return jsonify(
        {
            "ok": True,
            "mood": mood,
            "mood_label": profile["label"],
            "movie": best_movie,
            "poster_url": payload["poster_url"] if payload else url_for("poster_art", movie_name=best_movie),
            "description": MOVIE_DESCRIPTIONS.get(best_movie, "No description available."),
            "avg_rating": round(score_data["avg_rating"], 1),
            "review_count": score_data["review_count"],
            "reason": score_data["reason"],
        }
    )


@app.route("/poster-art/<path:movie_name>")
@login_required
def poster_art(movie_name):
        safe_name = urllib.parse.unquote(movie_name)
        genre = movie_genre(safe_name)
        slug = slugify(safe_name) or "movie"

        palettes = {
                "trending-now": ("#25163b", "#742774", "#f2af3e"),
                "drama-hits": ("#1c2b45", "#315b8a", "#d6e3ff"),
                "thrillers": ("#1a1e2a", "#38455f", "#89a6d9"),
                "horror-picks": ("#2a1521", "#61213e", "#ff98bf"),
        }
        c1, c2, c3 = palettes.get(slugify(genre), ("#1a2438", "#304766", "#d9e6ff"))

        lines = wrap_title_lines(safe_name)
        title_lines = ""
        y = 430
        for line in lines:
                title_lines += f'<text x="220" y="{y}" text-anchor="middle" fill="#f8fbff" font-size="38" font-family="Arial, sans-serif" font-weight="700">{escape(line)}</text>'
                y += 46

        svg = f"""
<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"440\" height=\"640\" viewBox=\"0 0 440 640\" role=\"img\" aria-label=\"{escape(safe_name)} poster\">
    <defs>
        <linearGradient id=\"bg\" x1=\"0\" y1=\"0\" x2=\"1\" y2=\"1\">
            <stop offset=\"0%\" stop-color=\"{c1}\"/>
            <stop offset=\"100%\" stop-color=\"{c2}\"/>
        </linearGradient>
        <radialGradient id=\"spot\" cx=\"0.5\" cy=\"0.2\" r=\"0.65\">
            <stop offset=\"0%\" stop-color=\"{c3}\" stop-opacity=\"0.45\"/>
            <stop offset=\"100%\" stop-color=\"#000\" stop-opacity=\"0\"/>
        </radialGradient>
    </defs>
    <rect width=\"440\" height=\"640\" fill=\"url(#bg)\"/>
    <rect width=\"440\" height=\"640\" fill=\"url(#spot)\"/>
    <rect x=\"24\" y=\"24\" width=\"392\" height=\"592\" rx=\"20\" fill=\"none\" stroke=\"rgba(255,255,255,0.3)\" stroke-width=\"2\"/>
    <circle cx=\"220\" cy=\"210\" r=\"84\" fill=\"rgba(255,255,255,0.14)\"/>
    <text x=\"220\" y=\"220\" text-anchor=\"middle\" fill=\"#ffffff\" font-size=\"52\" font-family=\"Arial, sans-serif\" font-weight=\"700\">FILM</text>
    <text x=\"220\" y=\"86\" text-anchor=\"middle\" fill=\"rgba(255,255,255,0.92)\" font-size=\"26\" font-family=\"Arial, sans-serif\" letter-spacing=\"2\">MOVIEVERSE</text>
    <text x=\"220\" y=\"118\" text-anchor=\"middle\" fill=\"rgba(255,255,255,0.75)\" font-size=\"18\" font-family=\"Arial, sans-serif\">{escape(genre)}</text>
    {title_lines}
</svg>
""".strip()
        return app.response_class(svg, mimetype="image/svg+xml")


@app.route("/api/cart/add", methods=["POST"])
@login_required
def api_cart_add():
    movie = request.form.get("movie", "").strip()
    username = session["username"]

    if not movie:
        return jsonify({"ok": False, "error": "Movie is required."}), 400

    users.setdefault(username, {"password": "", "cart": []})
    users[username].setdefault("cart", [])
    if movie not in users[username]["cart"]:
        users[username]["cart"].append(movie)
        save_json(USERS_FILE, users)

    return jsonify({"ok": True, "cart_count": len(users[username]["cart"])})


@app.route("/review/<movie>")
@login_required
def legacy_review(movie):
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)