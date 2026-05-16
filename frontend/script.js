const messages = [];

function scrollToBottom() {
  const chatBox = $("#chat-box");
  chatBox.scrollTop(chatBox[0].scrollHeight);
}

function escapeHtml(text) {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function formatMessage(message) {
  const escaped = escapeHtml(message);
  const bolded = escaped.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
  const lines = bolded.split(/\r?\n/);
  let inList = false;
  const htmlLines = [];

  lines.forEach((line) => {
    const listMatch = line.match(/^\s*[-*+]\s+(.*)$/);
    if (listMatch) {
      if (!inList) {
        inList = true;
        htmlLines.push('<ul class="message-list">');
      }
      htmlLines.push(`<li>${listMatch[1]}</li>`);
      return;
    }
    if (inList) {
      inList = false;
      htmlLines.push('</ul>');
    }
    if (line.trim() === '') {
      htmlLines.push('<br>');
    } else {
      htmlLines.push(line);
    }
  });

  if (inList) {
    htmlLines.push('</ul>');
  }
  return htmlLines.join('<br>');
}

function addUserMessage(message) {
  const safeMessage = escapeHtml(message);
  $("#chat-box").append(`
    <div class="flex justify-end">
      <div class="user-message">
        ${safeMessage}
      </div>
    </div>
  `);
  scrollToBottom();
}

function addBotMessage(message) {
  const formatted = formatMessage(message);
  $("#chat-box").append(`
    <div class="flex justify-start">
      <div class="bot-message">
        ${formatted}
      </div>
    </div>
  `);
  scrollToBottom();
}

function showLoading() {
  $("#loading-indicator").removeClass("hidden");
  scrollToBottom();
}

function hideLoading() {
  $("#loading-indicator").addClass("hidden");
}

function truncate(text, length = 180) {
  if (!text) return "";
  return text.length > length ? text.slice(0, length).trim() + "..." : text;
}

function getDurationMinutes(duration) {
  if (!duration) return null;
  const match = String(duration).match(/\d+/);
  return match ? parseInt(match[0]) : null;
}

function inferDifficulty(description, duration) {
  const desc = String(description || "").toLowerCase();
  const mins = getDurationMinutes(duration);

  if (desc.includes("executive") || desc.includes("senior") || (mins && mins > 50)) {
    return "High";
  } else if (desc.includes("entry") || desc.includes("graduate") || (mins && mins < 25)) {
    return "Low";
  }
  return "Medium";
}

function generateComparisonFields(items) {
  const fields = [];
  const fieldSet = new Set();

  const standardFields = ["job_levels", "languages", "assessment_length"];
  standardFields.forEach((field) => {
    if (items.some((item) => item[field])) {
      fieldSet.add(field);
    }
  });

  const fieldLabels = {
    job_levels: "Job Levels",
    languages: "Languages",
    assessment_length: "Duration",
  };

  return Array.from(fieldSet).map((field) => ({
    key: field,
    label: fieldLabels[field] || field,
  }));
}

function buildComparisonTable(data) {
  if (!data.comparison_data || data.comparison_data.length < 2) {
    return "";
  }

  const items = data.comparison_data;
  const fields = generateComparisonFields(items);

  let tableHtml = `
    <div class="comparison-table-container mt-4" role="region" aria-label="Assessment Comparison Table">
      <table class="comparison-table" role="table">
        <thead>
          <tr>
            <th class="comparison-header" scope="col">Attribute</th>
            <th class="comparison-header" scope="col">${escapeHtml(items[0].title || "Assessment 1")}</th>
            <th class="comparison-header" scope="col">${escapeHtml(items[1].title || "Assessment 2")}</th>
          </tr>
        </thead>
        <tbody>
  `;

  fields.forEach((field) => {
    const val0 = items[0][field.key] || "N/A";
    const val1 = items[1][field.key] || "N/A";
    const displayVal0 = field.key === "assessment_length" ? `${val0} mins` : val0;
    const displayVal1 = field.key === "assessment_length" ? `${val1} mins` : val1;

    tableHtml += `
      <tr>
        <td class="comparison-cell font-semibold">${field.label}</td>
        <td class="comparison-cell">${escapeHtml(String(displayVal0))}</td>
        <td class="comparison-cell">${escapeHtml(String(displayVal1))}</td>
      </tr>
    `;
  });

  tableHtml += `
    <tr>
      <td class="comparison-cell font-semibold">Difficulty Level</td>
      <td class="comparison-cell">
        <span class="badge badge-level">${inferDifficulty(items[0].description, items[0].assessment_length)}</span>
      </td>
      <td class="comparison-cell">
        <span class="badge badge-level">${inferDifficulty(items[1].description, items[1].assessment_length)}</span>
      </td>
    </tr>
  `;

  tableHtml += `
        </tbody>
      </table>
    </div>
  `;

  return tableHtml;
}

function getBestFitRecommendation(items) {
  const d1 = getDurationMinutes(items[0].assessment_length);
  const d2 = getDurationMinutes(items[1].assessment_length);

  if (d1 && d2) {
    if (d1 < d2) {
      return { index: 0, reason: "shortest duration" };
    } else if (d2 < d1) {
      return { index: 1, reason: "shortest duration" };
    }
  }

  const desc0 = String(items[0].description || "").toLowerCase();
  const desc1 = String(items[1].description || "").toLowerCase();

  if (desc0.includes("entry") || desc0.includes("graduate")) return { index: 0, reason: "entry-level focus" };
  if (desc1.includes("entry") || desc1.includes("graduate")) return { index: 1, reason: "entry-level focus" };

  return { index: -1, reason: null };
}

function addRecommendations(recommendations) {
  recommendations.forEach((item) => {
    $("#chat-box").append(`
      <div class="recommendation-card">
        <h3 class="text-lg font-bold mb-2">
          ${escapeHtml(item.name || "Assessment")}
        </h3>
        <div class="flex flex-wrap gap-2 mb-3">
          <span class="badge badge-duration">⏱️ ${item.duration || "N/A"} mins</span>
        </div>
        <div class="flex flex-col gap-2">
          ${item.url ? `<a href="${item.url}" target="_blank" rel="noopener" class="text-blue-600 hover:underline">Open Assessment</a>` : ""}
          ${item.pdf_url ? `<a href="${item.pdf_url}" target="_blank" rel="noopener" class="text-green-600 hover:underline">Open PDF</a>` : ""}
        </div>
      </div>
    `);
  });
  scrollToBottom();
}

async function sendMessage() {
  const input = $("#user-input");
  const query = input.val().trim();

  if (!query) return;

  addUserMessage(query);
  messages.push({ role: "user", content: query });
  input.val("");

  showLoading();

  try {
    const response = await fetch("http://127.0.0.1:8000/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages: messages }),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const data = await response.json();
    hideLoading();

    if (data.error) {
      addBotMessage(data.reply || "An error occurred. Please try again.");
      return;
    }

    if (data.reply) {
      addBotMessage(data.reply);
      messages.push({ role: "assistant", content: data.reply });
    }

    if (data.comparison === true && data.comparison_data && data.comparison_data.length >= 2) {
      const tableHtml = buildComparisonTable(data);
      const bestFit = getBestFitRecommendation(data.comparison_data);

      let comparisonHtml = tableHtml;

      if (bestFit.reason) {
        const bestItem = data.comparison_data[bestFit.index];
        comparisonHtml += `
          <div class="bg-green-50 border border-green-300 rounded-lg p-4 mt-4" role="status" aria-label="Best fit recommendation">
            <div class="flex items-start gap-2">
              <span class="text-xl">💡</span>
              <div>
                <p class="font-bold text-green-800">Best Fit Recommendation</p>
                <p class="text-green-700 text-sm">${escapeHtml(bestItem.title)} is ideal for <strong>${bestFit.reason}</strong></p>
              </div>
            </div>
          </div>
        `;
      }

      comparisonHtml += `<div class="grid grid-cols-1 md:grid-cols-2 gap-4 w-full mt-4">`;

      data.comparison_data.forEach((item, idx) => {
        const difficulty = inferDifficulty(item.description, item.assessment_length);
        const isBestFit = idx === bestFit.index && bestFit.reason;

        comparisonHtml += `
          <div class="bg-white border ${isBestFit ? "border-green-400 border-2" : "border-gray-200"} rounded-3xl p-6 shadow-md">
            <div class="flex items-start justify-between mb-4">
              <h2 class="text-2xl font-bold text-black flex-1">${escapeHtml(item.title || "Assessment")}</h2>
              ${isBestFit ? '<span class="badge badge-best-fit">✓ Best</span>' : ""}
            </div>

            <div class="space-y-3 text-gray-700 text-sm">
              <div>
                <span class="font-semibold">Job Levels:</span>
                ${escapeHtml(item.job_levels || "N/A")}
              </div>
              <div>
                <span class="font-semibold">Languages:</span>
                ${escapeHtml(item.languages || "N/A")}
              </div>
              <div>
                <span class="font-semibold">Duration:</span>
                <span class="badge badge-duration">${item.assessment_length || "N/A"} mins</span>
              </div>
              <div>
                <span class="font-semibold">Difficulty:</span>
                <span class="badge badge-level">${difficulty}</span>
              </div>
              <div>
                <span class="font-semibold">Overview:</span>
                ${truncate(item.description, 220)}
              </div>
            </div>

            <div class="flex flex-col gap-3 mt-6">
              ${item.url ? `
                <a href="${item.url}" target="_blank" rel="noopener" aria-label="Open ${escapeHtml(item.title)} assessment" 
                  class="bg-black text-white text-center py-2 rounded-xl hover:opacity-90 transition">
                  Open Assessment
                </a>
              ` : ""}
              ${item.pdf_url ? `
                <a href="${item.pdf_url}" target="_blank" rel="noopener" aria-label="Open ${escapeHtml(item.title)} PDF"
                  class="border border-black text-black text-center py-2 rounded-xl hover:bg-gray-100 transition">
                  Open PDF
                </a>
              ` : ""}
            </div>
          </div>
        `;
      });

      comparisonHtml += `</div>`;
      $("#chat-box").append(comparisonHtml);
      scrollToBottom();
    }

    if (data.recommendations && data.recommendations.length > 0) {
      addRecommendations(data.recommendations);
    }
  } catch (error) {
    hideLoading();
    addBotMessage("Error connecting to backend. Please check your connection and try again.");
    console.error(error);
  }
}

$("#send-btn").click(function () {
  sendMessage();
});

$("#user-input").keypress(function (e) {
  if (e.which === 13) {
    sendMessage();
  }
});
