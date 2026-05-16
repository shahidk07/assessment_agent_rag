const messages = [];


function scrollToBottom() {

  const chatBox = $("#chat-box");

  chatBox.scrollTop(
    chatBox[0].scrollHeight
  );
}


function addUserMessage(message) {

  $("#chat-box").append(`
    <div class="flex justify-end">
      <div class="user-message">
        ${message}
      </div>
    </div>
  `);

  scrollToBottom();
}


function addBotMessage(message) {

  $("#chat-box").append(`
    <div class="flex justify-start">
      <div class="bot-message">
        ${message}
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
          Test Type: ${item.test_type}
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


    addBotMessage(data.reply);


    messages.push({
      role: "assistant",
      content: data.reply
    });


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