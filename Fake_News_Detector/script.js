const titleInput = document.getElementById("title");
const textInput = document.getElementById("text");
const analyzeBtn = document.getElementById("analyze-btn");
const newAnalysisBtn = document.getElementById("new-analysis-btn");
const exportBtn = document.getElementById("export-btn");
const inputSection = document.querySelector(".input-section");
const resultSection = document.getElementById("result-section");
const resultCard = document.getElementById("result-card");
const loadingState = document.getElementById("loading-state");
const errorState = document.getElementById("error-state");
const errorMessage = document.getElementById("error-message");
const errorRetryBtn = document.getElementById("error-retry-btn");
const titleCount = document.getElementById("title-count");
const textCount = document.getElementById("text-count");
const statusText = document.querySelector(".status-text");
const statusDot = document.querySelector(".status-dot");
const revealElements = document.querySelectorAll(".reveal, .reveal-card");

const MAX_TITLE_LENGTH = 200;
const MAX_TEXT_LENGTH = 2000;

analyzeBtn.addEventListener("click", analyzeNews);
newAnalysisBtn.addEventListener("click", resetForm);
exportBtn.addEventListener("click", exportResult);
errorRetryBtn.addEventListener("click", () => analyzeNews());

titleInput.addEventListener("input", () => {
    enforceLength(titleInput, MAX_TITLE_LENGTH);
    titleCount.textContent = titleInput.value.length;
    clearError();
});

textInput.addEventListener("input", () => {
    enforceLength(textInput, MAX_TEXT_LENGTH);
    textCount.textContent = textInput.value.length;
    clearError();
});

titleInput.addEventListener("keypress", (event) => {
    if (event.key === "Enter" && textInput.value.trim() !== "") {
        analyzeNews();
    }
});

textInput.addEventListener("keypress", (event) => {
    if (event.key === "Enter" && event.ctrlKey) {
        analyzeNews();
    }
});

function enforceLength(input, limit) {
    if (input.value.length > limit) {
        input.value = input.value.substring(0, limit);
    }
}

function showOnly(target) {
    [inputSection, resultSection, loadingState, errorState].forEach((section) => {
        section.hidden = section !== target;
    });
}

function animateResultCard() {
    resultCard.classList.remove("is-entering");
    void resultCard.offsetWidth;
    resultCard.classList.add("is-entering");
}

function setStatus(state, message) {
    if (!statusText || !statusDot) {
        return;
    }

    statusText.textContent = message;
    statusDot.classList.remove("is-ready", "is-error");

    if (state === "ready") {
        statusDot.classList.add("is-ready");
    } else if (state === "error") {
        statusDot.classList.add("is-error");
    }
}

function scrollToSection(section) {
    section.scrollIntoView({
        behavior: "smooth",
        block: "start",
    });
}

function revealOnLoad() {
    document.body.classList.add("page-ready");

    revealElements.forEach((element, index) => {
        const delay = element.classList.contains("reveal-card") ? 160 + index * 70 : index * 90;
        window.setTimeout(() => {
            element.classList.add("is-visible");
        }, delay);
    });
}

async function analyzeNews() {
    const title = titleInput.value.trim();
    const text = textInput.value.trim();

    if (!title || !text) {
        showError("Please enter both a title and article content for analysis.");
        return;
    }

    if (title.length < 5) {
        showError("Title must be at least 5 characters long.");
        return;
    }

    if (text.length < 20) {
        showError("Content must be at least 20 characters long.");
        return;
    }

    showOnly(loadingState);
    analyzeBtn.disabled = true;
    setStatus("pending", "Analyzing article");

    try {
        const response = await fetch("/api/predict", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ title, text }),
        });

        const data = await response.json();

        if (response.ok && data.success) {
            displayResult(data);
            setStatus("ready", "Model ready for another review");
        } else {
            showError(data.error || "Failed to analyze the article.");
            setStatus("error", "Analysis needs attention");
        }
    } catch (error) {
        console.error("Prediction request failed:", error);
        showError(`Network error: ${error.message}`);
        setStatus("error", "Connection issue detected");
    } finally {
        analyzeBtn.disabled = false;
    }
}

function displayResult(data) {
    const isFake = data.is_fake;
    const confidence = Number(data.confidence || 0);
    const badgeClass = isFake ? "badge-fake" : "badge-real";
    const badgeIcon = isFake ? "fa-triangle-exclamation" : "fa-shield-check";
    const summaryTitle = isFake ? "Treat this claim cautiously" : "This looks more credible";
    const summaryCopy = isFake
        ? "The model found patterns commonly associated with misinformation or sensationalized reporting."
        : "The article reads more like conventional reporting based on the signals available in the text.";
    const guidance = isFake
        ? "Verify the claim with multiple reliable sources before sharing it further."
        : "Even strong scores should still be cross-checked if the topic is high-stakes or fast-moving.";

    resultCard.innerHTML = `
        <div class="prediction-layout">
            <div class="prediction-banner">
                <div class="prediction-badge ${badgeClass}">
                    <i class="fas ${badgeIcon}"></i>
                    <span>${data.prediction}</span>
                </div>
                <div class="prediction-summary">
                    <strong>${summaryTitle}</strong>
                    <p>${summaryCopy}</p>
                </div>
            </div>

            <div class="result-stats">
                <article class="stat-item">
                    <span class="stat-label">Confidence</span>
                    <div class="stat-value">${confidence.toFixed(1)}%</div>
                </article>
                <article class="stat-item">
                    <span class="stat-label">Classification</span>
                    <div class="stat-value">${isFake ? "Fake" : "Real"}</div>
                </article>
                <article class="stat-item">
                    <span class="stat-label">Reviewed At</span>
                    <div class="stat-subtle">${formatTimestamp(data.timestamp)}</div>
                </article>
            </div>

            <div class="confidence-panel">
                <div class="confidence-label">
                    <span>Confidence scale</span>
                    <strong>${confidence.toFixed(1)}%</strong>
                </div>
                <div class="confidence-fill">
                    <div class="confidence-progress" style="width: ${confidence}%"></div>
                </div>
            </div>

            <div class="result-message">
                <strong>${data.message}</strong>
                <p>${guidance}</p>
            </div>
        </div>
    `;

    window.lastResult = {
        title: data.title,
        isFake: data.is_fake,
        confidence,
        timestamp: data.timestamp,
        prediction: data.prediction,
    };

    animateResultCard();
    showOnly(resultSection);
    scrollToSection(resultSection);
}

function showError(message) {
    errorMessage.textContent = message;
    showOnly(errorState);
    scrollToSection(errorState);
}

function clearError() {
    if (!errorState.hidden) {
        errorState.hidden = true;
        errorMessage.textContent = "";
        inputSection.hidden = false;
    }
}

function resetForm() {
    titleInput.value = "";
    textInput.value = "";
    titleCount.textContent = "0";
    textCount.textContent = "0";
    clearError();
    showOnly(inputSection);
    titleInput.focus();
    setStatus("ready", "Ready for article review");
}

function exportResult() {
    if (!window.lastResult) {
        showToast("Run an analysis before exporting a result.");
        return;
    }

    const result = window.lastResult;
    const csvContent = [
        "Title,Result,Confidence,Timestamp",
        `"${result.title.replace(/"/g, '""')}","${result.prediction}","${result.confidence.toFixed(1)}%","${result.timestamp}"`,
    ].join("\n");

    const link = document.createElement("a");
    link.setAttribute("href", `data:text/csv;charset=utf-8,${encodeURIComponent(csvContent)}`);
    link.setAttribute("download", `fake_news_result_${Date.now()}.csv`);
    link.style.display = "none";

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    showToast("Result exported successfully.");
}

function showToast(message) {
    const toast = document.createElement("div");
    toast.className = "toast";
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transform = "translateY(10px)";
        setTimeout(() => toast.remove(), 220);
    }, 2600);
}

function formatTimestamp(timestamp) {
    const parsed = new Date(timestamp);

    if (Number.isNaN(parsed.getTime())) {
        return timestamp;
    }

    return parsed.toLocaleString([], {
        dateStyle: "medium",
        timeStyle: "short",
    });
}

window.addEventListener("load", async () => {
    showOnly(inputSection);
    setStatus("pending", "Checking model availability");
    revealOnLoad();

    try {
        const response = await fetch("/api/health");
        const data = await response.json();

        if (response.ok && data.model_loaded) {
            setStatus("ready", "Model ready for article review");
        } else {
            setStatus("error", "Model not loaded");
        }
    } catch (error) {
        console.error("Health check failed:", error);
        setStatus("error", "Unable to reach the local API");
    }
});
