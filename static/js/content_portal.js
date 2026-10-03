(function () {
  "use strict";

  var root = document.querySelector("[data-content-portal]");
  if (!root) return;

  var catalogNode = document.getElementById("content-portal-catalog");
  var courses = catalogNode ? JSON.parse(catalogNode.textContent) : [];
  var config = {
    storageReady: root.dataset.storageReady === "true",
    currentUserId: Number(root.dataset.currentUserId),
    canAuthor: root.dataset.canAuthor === "true",
    canReviewer: root.dataset.canReviewer === "true",
    canPublisher: root.dataset.canPublisher === "true",
    canImport: root.dataset.canImport === "true",
    uploadSignUrl: root.dataset.uploadSignUrl,
    assetCreateUrl: root.dataset.assetCreateUrl,
    importUrl: root.dataset.importUrl,
    previewPattern: root.dataset.previewPattern,
    transitionPattern: root.dataset.transitionPattern,
    replacementUploadPattern: root.dataset.replacementUploadPattern,
    replacePattern: root.dataset.replacePattern,
    csrfToken: (root.querySelector("input[name=csrfmiddlewaretoken]") || {}).value || ""
  };

  function escaped(value) {
    return String(value == null ? "" : value).replace(/[&<>'"]/g, function (character) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" }[character];
    });
  }

  function endpoint(pattern, id, action) {
    var url = pattern.replace("999999", String(id));
    return action ? url.replace("submit", action) : url;
  }

  function message(node, text, failed) {
    if (!node) return;
    node.textContent = text || "";
    node.classList.toggle("is-error", Boolean(failed));
    node.classList.toggle("is-success", Boolean(text && !failed));
  }

  async function api(url, method, body) {
    var options = { method: method, headers: { "Accept": "application/json" }, credentials: "same-origin" };
    if (method !== "GET") {
      options.headers["Content-Type"] = "application/json";
      options.headers["X-CSRFToken"] = config.csrfToken;
    }
    if (body !== undefined) options.body = JSON.stringify(body);
    var response = await fetch(url, options);
    var data;
    try { data = await response.json(); } catch (error) { data = { ok: false, error: "SWEEP returned an unexpected response." }; }
    if (!response.ok || !data.ok) throw new Error(data.error || "The request could not be completed.");
    return data;
  }

  function contentTypeFor(file) {
    if (file.type) return file.type.toLowerCase();
    var extension = (file.name.split(".").pop() || "").toLowerCase();
    return {
      pdf: "application/pdf", pptx: "application/vnd.openxmlformats-officedocument.presentationml.presentation",
      ppt: "application/vnd.ms-powerpoint", docx: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      doc: "application/msword", xlsx: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      xls: "application/vnd.ms-excel", txt: "text/plain", md: "text/plain", csv: "text/csv",
      mp4: "video/mp4", webm: "video/webm", mp3: "audio/mpeg", m4a: "audio/mp4"
    }[extension] || "";
  }

  function formPayload(form) {
    var data = new FormData(form);
    return {
      course_slug: data.get("course_slug"),
      module_order: data.get("module_order") === "" ? null : Number(data.get("module_order")),
      title: data.get("title"),
      asset_type: data.get("asset_type"),
      version: data.get("version"),
      language: data.get("language"),
      order: Number(data.get("order")),
      is_downloadable: data.get("is_downloadable") === "on"
    };
  }

  function formatBytes(value) {
    if (!value) return "";
    if (value < 1024 * 1024) return Math.round(value / 1024) + " KB";
    return (value / (1024 * 1024)).toFixed(1) + " MB";
  }

  function allAssets() {
    return courses.reduce(function (result, course) {
      return result.concat(course.assets.map(function (asset) { return Object.assign({ course_slug: course.slug, course_title: course.title }, asset); }));
    }, []);
  }

  var list = root.querySelector("[data-asset-list]");
  var assetCount = root.querySelector("[data-asset-count]");
  var catalogStatus = root.querySelector("[data-catalog-status]");

  function actionButton(asset, action, label, style) {
    return '<button type="button" class="content-action ' + style + '" data-asset-action="' + action + '" data-asset-id="' + asset.id + '">' + label + "</button>";
  }

  function assetActions(asset) {
    var output = [actionButton(asset, "preview", "Preview", "")];
    var owner = asset.created_by === config.currentUserId;
    if (config.canAuthor && owner && (asset.status === "published" || asset.status === "retired")) output.push(actionButton(asset, "replace", "Replace", ""));
    if (config.canAuthor && owner && asset.status === "draft") output.push(actionButton(asset, "submit", "Submit", "primary"));
    if (config.canReviewer && asset.status === "in_review") output.push(actionButton(asset, "approve", "Approve", "primary"));
    if (config.canPublisher && asset.status === "approved") output.push(actionButton(asset, "publish", "primary"));
    if (config.canPublisher && asset.status === "published") output.push(actionButton(asset, "retire", "danger"));
    return output.join("");
  }

  function renderAssets() {
    var assets = allAssets();
    assetCount.textContent = assets.length + (assets.length === 1 ? " asset" : " assets");
    if (!assets.length) {
      list.innerHTML = '<div class="content-empty">No course assets have been registered yet.</div>';
      return;
    }
    list.innerHTML = assets.map(function (asset) {
      var fileInfo = [asset.original_filename, formatBytes(asset.size_bytes)].filter(Boolean).join(" · ");
      var replacement = asset.replaces ? " Replacement for #" + asset.replaces : "";
      return '<article class="content-asset">' +
        '<div class="content-asset-main"><div class="content-asset-title"><h3>' + escaped(asset.title) + '</h3><span class="content-status-badge status-' + escaped(asset.status) + '">' + escaped(asset.status_label) + '</span></div>' +
        '<p class="meta">' + escaped(asset.course_title) + ' · ' + escaped(asset.module_title) + ' · ' + escaped(asset.asset_type_label) + ' · v' + escaped(asset.version) + replacement + '</p>' +
        (fileInfo ? '<p class="content-file-meta">' + escaped(fileInfo) + '</p>' : '') + '</div>' +
        '<div class="content-actions">' + assetActions(asset) + '</div></article>';
    }).join("");
  }

  function populateCourses(select) {
    if (!select) return;
    select.innerHTML = '<option value="">Select a course</option>' + courses.map(function (course) {
      return '<option value="' + escaped(course.slug) + '">' + escaped(course.title) + ' — ' + escaped(course.school) + '</option>';
    }).join("");
  }

  function populateModules(courseSelect, moduleSelect) {
    if (!courseSelect || !moduleSelect) return;
    var course = courses.find(function (item) { return item.slug === courseSelect.value; });
    moduleSelect.innerHTML = '<option value="">Course-wide resource</option>' + (course ? course.modules.map(function (module) {
      return '<option value="' + module.order + '">Module ' + module.order + ': ' + escaped(module.title) + '</option>';
    }).join("") : "");
  }

  var uploadForm = root.querySelector("[data-asset-upload-form]");
  if (uploadForm) {
    var courseSelect = uploadForm.querySelector("[data-course-select]");
    var moduleSelect = uploadForm.querySelector("[data-module-select]");
    populateCourses(courseSelect);
    courseSelect.addEventListener("change", function () { populateModules(courseSelect, moduleSelect); });
    uploadForm.addEventListener("submit", async function (event) {
      event.preventDefault();
      var status = uploadForm.querySelector("[data-upload-status]");
      var button = uploadForm.querySelector("button[type=submit]");
      var file = uploadForm.querySelector("input[name=file]").files[0];
      if (!file) return message(status, "Choose a file to upload.", true);
      if (!config.storageReady) return message(status, "Direct Supabase uploads are not configured here.", true);
      button.disabled = true;
      try {
        var payload = formPayload(uploadForm);
        var signed = await api(config.uploadSignUrl, "POST", {
          course_slug: payload.course_slug, module_order: payload.module_order, asset_type: payload.asset_type,
          filename: file.name, content_type: contentTypeFor(file), size_bytes: file.size
        });
        message(status, "Uploading directly to secure storage…", false);
        var upload = await fetch(signed.upload_url, {
          method: "PUT", body: file,
          headers: { "Content-Type": contentTypeFor(file), "x-upsert": "false" }
        });
        if (!upload.ok) throw new Error("Storage upload failed. Confirm the configured portal origin is allowed by the bucket's CORS policy.");
        payload.upload_intent_id = signed.upload_intent_id;
        await api(config.assetCreateUrl, "POST", payload);
        message(status, "Uploaded and registered as a draft.", false);
        window.setTimeout(function () { window.location.reload(); }, 700);
      } catch (error) {
        message(status, error.message, true);
        button.disabled = false;
      }
    });
  }

  var importForm = root.querySelector("[data-import-form]");
  if (importForm) {
    importForm.addEventListener("submit", async function (event) {
      event.preventDefault();
      var status = importForm.querySelector("[data-import-status]");
      try {
        var data = JSON.parse(importForm.elements.import_json.value);
        var response = await api(config.importUrl, "POST", data);
        message(status, response.assets.length + " assets imported as drafts.", false);
        window.setTimeout(function () { window.location.reload(); }, 700);
      } catch (error) { message(status, error.message || "The import JSON is invalid.", true); }
    });
  }

  var dialog = root.querySelector("[data-replace-dialog]");
  var replaceForm = root.querySelector("[data-replace-form]");
  function openReplacement(asset) {
    if (!dialog || !replaceForm) return;
    replaceForm.reset();
    replaceForm.elements.asset_id.value = asset.id;
    replaceForm.elements.title.value = asset.title;
    replaceForm.elements.asset_type.value = asset.asset_type;
    replaceForm.elements.version.value = asset.version;
    replaceForm.elements.language.value = asset.language;
    replaceForm.elements.order.value = asset.order;
    replaceForm.elements.is_downloadable.checked = true;
    root.querySelector("[data-replace-description]").textContent = "A replacement becomes a new draft. The current published file stays live until this version is approved and published.";
    message(root.querySelector("[data-replace-status]"), "", false);
    dialog.showModal();
  }

  if (replaceForm) {
    replaceForm.addEventListener("submit", async function (event) {
      event.preventDefault();
      var status = root.querySelector("[data-replace-status]");
      var file = replaceForm.elements.file.files[0];
      var button = replaceForm.querySelector("button[type=submit]");
      if (!file) return message(status, "Choose a replacement file.", true);
      button.disabled = true;
      try {
        var assetId = replaceForm.elements.asset_id.value;
        var payload = formPayload(replaceForm);
        var signed = await api(endpoint(config.replacementUploadPattern, assetId), "POST", {
          asset_type: payload.asset_type, filename: file.name, content_type: contentTypeFor(file), size_bytes: file.size
        });
        message(status, "Uploading replacement directly to secure storage…", false);
        var upload = await fetch(signed.upload_url, { method: "PUT", body: file, headers: { "Content-Type": contentTypeFor(file), "x-upsert": "false" } });
        if (!upload.ok) throw new Error("Storage upload failed. Confirm the bucket's CORS policy permits this portal origin.");
        payload.upload_intent_id = signed.upload_intent_id;
        await api(endpoint(config.replacePattern, assetId), "POST", payload);
        message(status, "Replacement registered as a draft.", false);
        window.setTimeout(function () { window.location.reload(); }, 700);
      } catch (error) { message(status, error.message, true); button.disabled = false; }
    });
  }

  if (list) list.addEventListener("click", async function (event) {
    var button = event.target.closest("[data-asset-action]");
    if (!button) return;
    var asset = allAssets().find(function (item) { return item.id === Number(button.dataset.assetId); });
    if (!asset) return;
    var action = button.dataset.assetAction;
    try {
      if (action === "preview") {
        var preview = await api(endpoint(config.previewPattern, asset.id), "GET");
        window.open(preview.url, "_blank", "noopener");
      } else if (action === "replace") {
        openReplacement(asset);
      } else {
        if ((action === "publish" || action === "retire") && !window.confirm("Continue with " + action + "?")) return;
        button.disabled = true;
        await api(endpoint(config.transitionPattern, asset.id, action), "POST");
        message(catalogStatus, "Asset " + action + "ed successfully.", false);
        window.setTimeout(function () { window.location.reload(); }, 600);
      }
    } catch (error) {
      message(catalogStatus, error.message, true);
      button.disabled = false;
    }
  });

  renderAssets();
}());
