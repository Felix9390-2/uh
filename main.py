from flask import Flask, request, render_template_string
from groq import Groq
import os

client = Groq(
    api_key="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"
)
app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Groq GPT Lite</title>
<style>
body { background:#000; color:#0f0; font-family: monospace; padding:10px; }
textarea, button { width:100%; background:#000; color:#0f0; border:1px solid #0f0; }
button { padding:10px; font-weight:bold; }
pre { white-space: pre-wrap; }
</style>
</head>
<body>
<h3>Groq GPT-OSS-120B</h3>
<form method="post">
<textarea name="msg" rows="4"></textarea><br><br>
<button type="submit">Send</button>
</form>
<pre>{{reply}}</pre>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def chat():
    reply = ""
    if request.method == "POST":
        user_msg = request.form["msg"]

        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": user_msg}],
            temperature=1,
            max_completion_tokens=2048,
            top_p=1,
            reasoning_effort="medium",
            stream=True
        )

        chunks = []
        for chunk in completion:
            if chunk.choices[0].delta.content:
                chunks.append(chunk.choices[0].delta.content)

        reply = "".join(chunks)

    return render_template_string(HTML, reply=reply)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
