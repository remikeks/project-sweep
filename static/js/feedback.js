/**
 * Site-wide feedback widget: a floating button (bottom-right, present on
 * every page via base.html) with an alternating text bubble, opening a
 * modal that posts to /feedback/submit/. No login required — works for
 * anonymous visitors and signed-in users alike.
 */
(function () {
  var BUBBLE_MESSAGES = ["Tell us what you think", "Help us improve"];
  var BUBBLE_INTERVAL_MS = 4000;

  function getCookie(name) {
    var match = document.cookie.match("(^|;)\\s*" + name + "\\s*=\\s*([^;]+)");
    return match ? decodeURIComponent(match.pop()) : "";
  }

  function initBubble(widget) {
    var bubble = widget.querySelector("[data-feedback-bubble]");
    if (!bubble) return;

    var index = 0;
    window.setInterval(function () {
      index = (index + 1) % BUBBLE_MESSAGES.length;
      bubble.classList.add("is-fading");
      window.setTimeout(function () {
        bubble.textContent = BUBBLE_MESSAGES[index];
        bubble.classList.remove("is-fading");
      }, 220);
    }, BUBBLE_INTERVAL_MS);
  }

  function initModal(widget) {
    var trigger = widget.querySelector("[data-feedback-trigger]");
    var overlay = widget.querySelector("[data-feedback-overlay]");
    var closeBtn = widget.querySelector("[data-feedback-close]");
    var doneBtn = widget.querySelector("[data-feedback-done]");
    var form = widget.querySelector("[data-feedback-form]");
    var thanks = widget.querySelector("[data-feedback-thanks]");
    var statusBox = widget.querySelector("[data-feedback-status]");
    var submitBtn = widget.querySelector("[data-feedback-submit]");
    if (!trigger || !overlay || !form) return;

    function resetForm() {
      form.reset();
      form.hidden = false;
      thanks.hidden = true;
      statusBox.textContent = "";
      statusBox.className = "feedback-status";
    }

    function openModal() {
      overlay.classList.add("is-open");
      window.setTimeout(function () {
        var firstField = form.querySelector("select, textarea, input");
        if (firstField) firstField.focus();
      }, 10);
    }

    function closeModal() {
      overlay.classList.remove("is-open");
    }

    trigger.addEventListener("click", openModal);
    if (closeBtn) closeBtn.addEventListener("click", closeModal);
    if (doneBtn) {
      doneBtn.addEventListener("click", function () {
        closeModal();
        resetForm();
      });
    }

    overlay.addEventListener("click", function (evt) {
      if (evt.target === overlay) closeModal();
    });

    document.addEventListener("keydown", function (evt) {
      if (evt.key === "Escape" && overlay.classList.contains("is-open")) closeModal();
    });

    form.addEventListener("submit", function (evt) {
      evt.preventDefault();

      var feedbackType = form.querySelector("#feedback-type").value;
      var message = form.querySelector("#feedback-message").value.trim();
      var email = form.querySelector("#feedback-email").value.trim();

      if (!message) {
        statusBox.textContent = "Please tell us a bit more before sending.";
        statusBox.className = "feedback-status is-error";
        return;
      }

      submitBtn.disabled = true;
      submitBtn.textContent = "Sending…";
      statusBox.textContent = "";
      statusBox.className = "feedback-status";

      fetch("/feedback/submit/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({
          feedback_type: feedbackType,
          message: message,
          email: email,
          page_url: window.location.href,
        }),
      })
        .then(function (response) {
          return response.json().then(function (data) {
            return { status: response.status, data: data };
          });
        })
        .then(function (result) {
          if (result.data && result.data.ok) {
            form.hidden = true;
            thanks.hidden = false;
          } else {
            statusBox.textContent = (result.data && result.data.error) || "Something went wrong. Please try again.";
            statusBox.className = "feedback-status is-error";
          }
        })
        .catch(function () {
          statusBox.textContent = "Couldn't reach the server. Check your connection and try again.";
          statusBox.className = "feedback-status is-error";
        })
        .finally(function () {
          submitBtn.disabled = false;
          submitBtn.textContent = "Send feedback";
        });
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("[data-feedback-widget]").forEach(function (widget) {
      initBubble(widget);
      initModal(widget);
    });
  });
})();
