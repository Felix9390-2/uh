from flask import Flask, request, render_template_string
from groq import Groq
import os

client = Groq(
    api_key="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"
)
MODEL = "openai/gpt-oss-120b"
app = Flask(__name__)

MEMORY_FILE = "database.txt"

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return []
    messages = []
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("USER:"):
                messages.append({"role": "user", "content": line[5:].strip()})
            elif line.startswith("ASSISTANT:"):
                messages.append({"role": "assistant", "content": line[10:].strip()})
    return messages

def save_message(role, content):
    with open(MEMORY_FILE, "a", encoding="utf-8") as f:
        if role == "user":
            f.write("USER: " + content + "\n")
        else:
            f.write("ASSISTANT: " + content + "\n")


HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Assistant</title>
<meta name="viewport" content="width=device-width, initial-scale=1">

<style>
body {
  margin: 0;
  font-family: -apple-system, Helvetica, Arial, sans-serif;
  background: #fff;
}

.center {
  text-align: center;
  margin-top: 120px;
  padding: 16px;
}

.response {
  padding: 16px;
  font-size: 18px;
  line-height: 1.5;
  margin-bottom: 160px;
  white-space: pre-wrap;
}

.bottom-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #f6f6f6;
  border-top: 1px solid #ddd;
  padding: 10px;
}

.row {
  display: flex;
  gap: 8px;
}

textarea {
  flex: 1;
  height: 50px;
  font-size: 18px;
  padding: 10px;
  border-radius: 12px;
  border: 1px solid #ccc;
  resize: none;
}

button {
  padding: 12px;
  font-size: 18px;
  border-radius: 12px;
  border: none;
  background: #000;
  color: #fff;
}

.mic {
  background: #e0e0e0;
  color: #000;
  width: 56px;
}
</style>
</head>

<body>

<div class="center">
  <h1>What’s on your mind today?</h1>
</div>

<div class="response">{{reply}}</div>

<form method="post" class="bottom-bar">
  <div class="row">
    <textarea id="msg" name="msg" placeholder="Ask anything"></textarea>
    <button type="button" class="mic" onclick="startMic()">🎤</button>
  </div>
  <button type="submit" style="margin-top:8px;width:100%;">Send</button>
</form>

<script>
function startMic() {
  if (!('webkitSpeechRecognition' in window)) {
    alert('Mic not supported');
    return;
  }

  var recognition = new webkitSpeechRecognition();
  recognition.lang = 'en-US';
  recognition.continuous = false;
  recognition.interimResults = false;

  recognition.onresult = function(event) {
    document.getElementById('msg').value =
      event.results[0][0].transcript;
  };

  recognition.start();
}
</script>

</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def index():
    reply = ""
    if request.method == "POST":
        user_msg = request.form.get("msg", "")
        if user_msg.strip():
            messages = load_memory()
            messages.append({"role": "user", "content": user_msg})
            save_message("user", user_msg)

            completion = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=1,
                max_completion_tokens=2048,
                stream=True
            )

            out = []
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    out.append(chunk.choices[0].delta.content)

            reply = "".join(out)
            save_message("assistant", reply)

    return render_template_string(HTML, reply=reply)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
