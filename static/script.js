document.addEventListener("DOMContentLoaded", () => {
    const modal = document.getElementById("reviewModal");
    const closeModalBtn = document.getElementById("closeModal");
    const modalMovie = document.getElementById("modalMovie");
    const modalPoster = document.getElementById("modalPoster");
    const movieInput = document.getElementById("movieInput");
    const reviewForm = document.getElementById("reviewForm");
    const reviewText = document.getElementById("reviewText");
    const reviewError = document.getElementById("reviewError");
    const analysisResult = document.getElementById("analysisResult");
    const cartCount = document.getElementById("cartCount");
    const movieDescription = document.getElementById("movieDescription");
    const reviewsList = document.getElementById("reviewsList");
    const localFallbackPoster = "/static/poster-fallback.svg";
    const moodSelect = document.getElementById("moodSelect");
    const matchmakerBtn = document.getElementById("matchmakerBtn");
    const matchmakerResult = document.getElementById("matchmakerResult");

    function attachPosterFallback(imageNode, title) {
        if (!imageNode) {
            return;
        }

        let finished = false;
        const useFallback = () => {
            if (finished) {
                return;
            }
            finished = true;
            imageNode.src = localFallbackPoster;
            imageNode.alt = `${title} poster unavailable`;
        };

        const timeoutId = setTimeout(() => {
            if (!imageNode.complete || imageNode.naturalWidth === 0) {
                useFallback();
            }
        }, 5000);

        imageNode.addEventListener(
            "load",
            () => {
                clearTimeout(timeoutId);
                if (imageNode.naturalWidth === 0) {
                    useFallback();
                    return;
                }
                finished = true;
            },
            { once: true }
        );

        imageNode.addEventListener(
            "error",
            () => {
                clearTimeout(timeoutId);
                useFallback();
            },
            { once: true }
        );
    }

    function slugify(name) {
        return name
            .toLowerCase()
            .replace(/[^a-z0-9]+/g, "-")
            .replace(/^-+|-+$/g, "");
    }

    function formatReviewDate(createdAt) {
        if (!createdAt) {
            return "Date unavailable";
        }

        const dt = new Date(createdAt);
        if (Number.isNaN(dt.getTime())) {
            return "Date unavailable";
        }

        return dt.toLocaleString(undefined, {
            year: "numeric",
            month: "short",
            day: "2-digit",
            hour: "2-digit",
            minute: "2-digit",
        });
    }

    function renderReviews(reviews) {
        if (!reviewsList) {
            return;
        }

        if (!reviews || reviews.length === 0) {
            reviewsList.innerHTML = "<p class='empty-reviews'>No user reviews yet for this movie.</p>";
            return;
        }

        const cards = reviews
            .map((review) => {
                const reviewDate = formatReviewDate(review.created_at);
                return (
                    "<article class='review-item'>" +
                    `<p class='review-user'>${review.user}</p>` +
                    `<p class='review-text'>${review.text}</p>` +
                    `<p class='review-date'>${reviewDate}</p>` +
                    `<p class='review-score'>${review.sentiment} • ${review.rating}/5 ${review.stars}</p>` +
                    "</article>"
                );
            })
            .join("");

        reviewsList.innerHTML = cards;
    }

    async function loadMovieDetails(movie, fallbackDescription) {
        if (movieDescription) {
            movieDescription.textContent = fallbackDescription || "";
        }

        try {
            const response = await fetch(`/api/movie/${encodeURIComponent(movie)}/reviews`);
            const data = await response.json();

            if (response.ok && data.ok) {
                if (movieDescription) {
                    movieDescription.textContent = data.description;
                }
                renderReviews(data.reviews);
                return;
            }
        } catch (error) {
            // Keep fallback values when request fails.
        }

        renderReviews([]);
    }

    function openModal(movie, poster, description) {
        modalMovie.textContent = movie;
        modalPoster.src = poster;
        attachPosterFallback(modalPoster, movie);
        movieInput.value = movie;
        reviewText.value = "";
        reviewError.textContent = "";
        analysisResult.innerHTML = "";
        if (movieDescription) {
            movieDescription.textContent = description || "";
        }
        modal.classList.add("open");
        modal.setAttribute("aria-hidden", "false");
        reviewText.focus();
        loadMovieDetails(movie, description);
    }

    function closeModal() {
        modal.classList.remove("open");
        modal.setAttribute("aria-hidden", "true");
    }

    document.querySelectorAll(".review-trigger").forEach((btn) => {
        btn.addEventListener("click", () => {
            openModal(btn.dataset.movie, btn.dataset.poster, btn.dataset.description);
        });
    });

    document.querySelectorAll(".movie-card img").forEach((img) => {
        attachPosterFallback(img, img.alt || "Movie");
    });

    if (closeModalBtn) {
        closeModalBtn.addEventListener("click", closeModal);
    }

    if (modal) {
        modal.addEventListener("click", (event) => {
            if (event.target === modal) {
                closeModal();
            }
        });
    }

    if (reviewForm) {
        reviewForm.addEventListener("submit", async (event) => {
            event.preventDefault();

            const movie = movieInput.value;
            const review = reviewText.value.trim();

            if (!review) {
                reviewError.textContent = "Please fill this field.";
                return;
            }

            reviewError.textContent = "";
            const formData = new URLSearchParams();
            formData.append("movie", movie);
            formData.append("review", review);

            const response = await fetch("/api/review", {
                method: "POST",
                headers: { "Content-Type": "application/x-www-form-urlencoded" },
                body: formData,
            });

            const data = await response.json();
            if (!response.ok || !data.ok) {
                reviewError.textContent = data.error || "Unable to analyze right now.";
                return;
            }

            analysisResult.innerHTML =
                `<p><strong>Sentiment:</strong> ${data.sentiment}</p>` +
                `<p><strong>Predicted Rating:</strong> ${data.rating}/5 ${data.stars}</p>` +
                `<p><strong>Global Movie Score:</strong> ${data.avg_rating}/5 from ${data.review_count} reviews</p>`;

            const ratingId = "rating-" + slugify(movie);
            const ratingNode = document.getElementById(ratingId);
            if (ratingNode) {
                ratingNode.textContent = `${data.avg_rating}/5 from ${data.review_count} reviews`;
            }

            loadMovieDetails(movie, movieDescription ? movieDescription.textContent : "");
        });
    }

    document.querySelectorAll(".cart-trigger").forEach((btn) => {
        btn.addEventListener("click", async () => {
            const movie = btn.dataset.movie;
            const formData = new URLSearchParams();
            formData.append("movie", movie);

            const response = await fetch("/api/cart/add", {
                method: "POST",
                headers: { "Content-Type": "application/x-www-form-urlencoded" },
                body: formData,
            });

            const data = await response.json();
            if (response.ok && data.ok) {
                btn.textContent = "In Cart";
                btn.disabled = true;
                if (cartCount) {
                    cartCount.textContent = data.cart_count;
                }
            }
        });
    });

    document.querySelectorAll(".scroll-btn").forEach((btn) => {
        btn.addEventListener("click", () => {
            const rowElement = document.getElementById(btn.dataset.row);
            if (!rowElement) {
                return;
            }

            const direction = btn.dataset.dir === "left" ? -1 : 1;
            rowElement.scrollBy({
                left: direction * 420,
                behavior: "smooth",
            });
        });
    });

    if (matchmakerBtn && moodSelect && matchmakerResult) {
        matchmakerBtn.addEventListener("click", async () => {
            const mood = moodSelect.value;
            if (!mood) {
                matchmakerResult.innerHTML = "<p class='form-error'>Please choose a mood first.</p>";
                return;
            }

            matchmakerBtn.disabled = true;
            matchmakerBtn.textContent = "Matching...";

            try {
                const response = await fetch(`/api/matchmaker?mood=${encodeURIComponent(mood)}`);
                const data = await response.json();

                if (!response.ok || !data.ok) {
                    matchmakerResult.innerHTML = `<p class='form-error'>${data.error || "Unable to suggest now."}</p>`;
                    return;
                }

                matchmakerResult.innerHTML =
                    "<article class='match-card'>" +
                    `<img src='${data.poster_url}' alt='${data.movie} recommendation'>` +
                    "<div>" +
                    `<p class='match-tag'>${data.mood_label} Pick</p>` +
                    `<h3>${data.movie}</h3>` +
                    `<p class='match-rating'>${data.avg_rating}/5 from ${data.review_count} reviews</p>` +
                    `<p class='match-reason'>${data.reason}</p>` +
                    `<p class='match-desc'>${data.description}</p>` +
                    `<button type='button' class='mini-btn' id='openMatchReview'>Review This Movie</button>` +
                    "</div>" +
                    "</article>";

                const matchImg = matchmakerResult.querySelector("img");
                attachPosterFallback(matchImg, data.movie);

                const openReviewBtn = document.getElementById("openMatchReview");
                if (openReviewBtn) {
                    openReviewBtn.addEventListener("click", () => {
                        openModal(data.movie, data.poster_url, data.description);
                    });
                }
            } catch (error) {
                matchmakerResult.innerHTML = "<p class='form-error'>Unable to suggest now.</p>";
            } finally {
                matchmakerBtn.disabled = false;
                matchmakerBtn.textContent = "Find My Movie";
            }
        });
    }
});