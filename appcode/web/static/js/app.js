let conversationId = null;

const messagesDiv = document.getElementById("messages");
const promptEl = document.getElementById("prompt");
const sendBtn = document.getElementById("send-btn");
const convIdSpan = document.getElementById("conv-id");

function appendMessage(role, text) {
  const div = document.createElement("div");
  div.className = role === "user" ? "msg-user" : "msg-assistant";
  div.innerText = (role === "user" ? "You: " : "Assistant: ") + text;
  messagesDiv.appendChild(div);
  messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function getProvider() {
  const radios = document.querySelectorAll('input[name="provider"]');
  for (const radio of radios) {
    if (radio.checked) {
      return radio.value;
    }
  }
  return "openai";
}

async function sendMessage() {
  const text = promptEl.value.trim();
  if (!text) {
    return;
  }

  const provider = getProvider();
  appendMessage("user", text);
  promptEl.value = "";

  sendBtn.disabled = true;
  sendBtn.innerText = "Thinking...";

  try {
    const response = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        provider: provider,
        conversation_id: conversationId,
        message: text,
      }),
    });

    if (!response.ok) {
      throw new Error("HTTP " + response.status);
    }

    const data = await response.json();
    conversationId = data.conversation_id;
    convIdSpan.innerText = conversationId;
    appendMessage("assistant", data.reply);
  } catch (error) {
    appendMessage("assistant", "[Error] " + error);
  } finally {
    sendBtn.disabled = false;
    sendBtn.innerText = "Send";
  }
}

sendBtn.addEventListener("click", sendMessage);

promptEl.addEventListener("keydown", function (event) {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    sendMessage();
  }
});
