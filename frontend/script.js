const messages = [];


function scrollToBottom() {

  const chatBox = $("#chat-box");

  chatBox.scrollTop(
    chatBox[0].scrollHeight
  );
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


function addRecommendations(recommendations) {

  recommendations.forEach((item) => {

    $("#chat-box").append(`
      <div class="recommendation-card">

        <h3 class="text-lg font-bold mb-2">
          ${item.name}
        </h3>

        <p class="text-sm text-gray-500 mb-3">
        Duration: ${item.duration} mins
        </p>

        <div class="flex flex-col gap-2">

          <a
            href="${item.url}"
            target="_blank"
            class="text-blue-600 hover:underline"
          >
            Open Assessment
          </a>

          <a
            href="${item.pdf_url}"
            target="_blank"
            class="text-green-600 hover:underline"
          >
            Open PDF
          </a>

        </div>

      </div>
    `);

  });

  scrollToBottom();
}


async function sendMessage() {

  const input = $("#user-input");

  const query = input.val().trim();

  if (!query) {
    return;
  }


  addUserMessage(query);


  messages.push({
    role: "user",
    content: query
  });


  input.val("");


  try {

    const response = await fetch(
      "http://127.0.0.1:8000/chat",
      {
        method: "POST",

        headers: {
          "Content-Type": "application/json"
        },

        body: JSON.stringify({
          messages: messages
        })
      }
    );


    const data = await response.json();


    // =========================
    // NORMAL BOT MESSAGE
    // =========================
    
    if (data.reply) {
      addBotMessage(data.reply);
      messages.push({
        role: "assistant",
        content: data.reply
      });
    }

    // =========================
    // COMPARISON UI
// =========================

if (data.comparison === true) {

  let comparisonHTML = `
  <div class="comparison-table-container mt-4">
    <table class="comparison-table w-full text-left border-collapse">
      <thead>
        <tr>
          <th class="comparison-header"></th>
          <th class="comparison-header">${data.comparison_data[0].title}</th>
          <th class="comparison-header">${data.comparison_data[1].title}</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td class="comparison-cell font-semibold">Job Levels</td>
          <td class="comparison-cell">${data.comparison_data[0].job_levels || "N/A"}</td>
          <td class="comparison-cell">${data.comparison_data[1].job_levels || "N/A"}</td>
        </tr>
        <tr>
          <td class="comparison-cell font-semibold">Duration</td>
          <td class="comparison-cell">${data.comparison_data[0].assessment_length || "N/A"} mins</td>
          <td class="comparison-cell">${data.comparison_data[1].assessment_length || "N/A"} mins</td>
        </tr>
        <tr>
          <td class="comparison-cell font-semibold">Languages</td>
          <td class="comparison-cell">${data.comparison_data[0].languages || "N/A"}</td>
          <td class="comparison-cell">${data.comparison_data[1].languages || "N/A"}</td>
        </tr>
        <tr>
          <td class="comparison-cell font-semibold">Overview</td>
          <td class="comparison-cell">${truncate(data.comparison_data[0].description, 180)}</td>
          <td class="comparison-cell">${truncate(data.comparison_data[1].description, 180)}</td>
        </tr>
      </tbody>
    </table>
  </div>
  `;

  comparisonHTML += `
  <div class="grid grid-cols-1 md:grid-cols-2 gap-4 w-full mt-4">
  `;

  function truncate(text, length = 180) {
    if (!text) return "";
    return text.length > length
      ? text.slice(0, length).trim() + "..."
      : text;
  }

  data.comparison_data.forEach(item => {

    comparisonHTML += `
    <div class="bg-white border border-gray-200 rounded-3xl p-6 shadow-md">

      <h2 class="text-2xl font-bold mb-4 text-black">
        ${item.title}
      </h2>

      <div class="space-y-3 text-gray-700 text-sm">

        <div>
          <span class="font-semibold">Job Levels:</span>
          ${item.job_levels || "N/A"}
        </div>

        <div>
          <span class="font-semibold">Languages:</span>
          ${item.languages || "N/A"}
        </div>

        <div>
          <span class="font-semibold">Duration:</span>
          ${item.assessment_length || "N/A"} mins
        </div>

        <div>
          <span class="font-semibold">Overview:</span>
          ${truncate(item.description, 220)}
        </div>

      </div>

      <div class="flex flex-col gap-3 mt-6">

        <a
          href="${item.url}"
          target="_blank"
          class="bg-black text-white text-center py-2 rounded-xl hover:opacity-90 transition"
        >
          Open Assessment
        </a>

        <a
          href="${item.pdf_url}"
          target="_blank"
          class="border border-black text-black text-center py-2 rounded-xl hover:bg-gray-100 transition"
        >
          Open PDF
        </a>

      </div>

    </div>
    `;
  });

  comparisonHTML += `</div>`;

  $("#chat-box").append(comparisonHTML);

  scrollToBottom();
}
    
    // =========================
    // NORMAL RECOMMENDATIONS
    // =========================
    
    if (data.recommendations.length > 0) {
    
      addRecommendations(
        data.recommendations
      );
    }

  }

  catch (error) {

    addBotMessage(
      "Error connecting to backend."
    );

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

