/**
 * Powers every "Ask AI Tutor" / "Summarise this lesson" / "What's this
 * course about?" widget on the site. One small JS module, one JSON
 * endpoint (POST /ai-tutor/ask/), reused everywhere the widget is
 * dropped in via templates/ai_tutor/widget.html.
 */
(function () {
  function getCookie(name) {
    var match = document.cookie.match("(^|;)\\s*" + name + "\\s*=\\s*([^;]+)");
    return match ? decodeURIComponent(match.pop()) : "";
  }

  function escapeHtml(str) {
    var div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
  }

  function renderAnswer(body, text) {
    var html = escapeHtml(text).replace(/\n/g, "<br>");
    body.innerHTML = '<div class="tutor-answer">' + html + "</div>";
  }

  function renderError(body, message) {
    body.innerHTML = '<div class="tutor-error">' + escapeHtml(message) + "</div>";
  }

  function renderLoading(body) {
    body.innerHTML = '<div class="tutor-loading">Thinking…</div>';
  }

  function askTutor(widget, payload) {
    var body = widget.querySelector("[data-tutor-body]");
    renderLoading(body);

    return fetch("/ai-tutor/ask/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      body: JSON.stringify(payload),
    })
      .then(function (response) {
        return response.json().then(function (data) {
          return { status: response.status, data: data };
        });
      })
      .then(function (result) {
        if (result.data && result.data.ok) {
          renderAnswer(body, result.data.answer);
        } else {
          renderError(body, (result.data && result.data.error) || "Something went wrong.");
        }
      })
      .catch(function () {
        renderError(body, "Couldn't reach the AI Tutor. Check your connection and try again.");
      });
  }

  function basePayload(widget) {
    var payload = { course_slug: widget.getAttribute("data-course-slug") };
    var moduleOrder = widget.getAttribute("data-module-order");
    if (moduleOrder !== null && moduleOrder !== "") {
      payload.module_order = parseInt(moduleOrder, 10);
    }
    return payload;
  }

  function initWidget(widget) {
    var trigger = widget.querySelector("[data-tutor-trigger]");
    var panel = widget.querySelector("[data-tutor-panel]");
    var closeBtn = widget.querySelector("[data-tutor-close]");
    var quickBtn = widget.querySelector("[data-tutor-quick]");
    var form = widget.querySelector("[data-tutor-form]");
    var input = widget.querySelector("[data-tutor-input]");
    var isAuthenticated = widget.getAttribute("data-authenticated") === "true";
    var loginUrl = widget.getAttribute("data-login-url");
    var isCompact = widget.getAttribute("data-tutor-compact") === "true";
    var hasFiredCompact = false;

    function openPanel() {
      panel.hidden = false;
      widget.classList.add("tutor-open");
    }

    function closePanel() {
      panel.hidden = true;
      widget.classList.remove("tutor-open");
    }

    trigger.addEventListener("click", function () {
      if (!isAuthenticated) {
        window.location.href = loginUrl;
        return;
      }
      if (panel.hidden) {
        openPanel();
        if (isCompact && !hasFiredCompact) {
          hasFiredCompact = true;
          var payload = basePayload(widget);
          payload.mode = "summary";
          askTutor(widget, payload);
        }
      } else {
        closePanel();
      }
    });

    if (closeBtn) {
      closeBtn.addEventListener("click", closePanel);
    }

    if (quickBtn) {
      quickBtn.addEventListener("click", function () {
        var payload = basePayload(widget);
        payload.mode = "summary";
        askTutor(widget, payload);
      });
    }

    if (form) {
      form.addEventListener("submit", function (evt) {
        evt.preventDefault();
        var question = (input.value || "").trim();
        if (!question) return;
        var payload = basePayload(widget);
        payload.mode = "chat";
        payload.question = question;
        askTutor(widget, payload);
      });
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("[data-tutor-widget]").forEach(initWidget);
  });
})();
