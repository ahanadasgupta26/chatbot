from flask import Flask, render_template, request, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from traffic_fetcher import get_traffic_info

tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")

app = Flask(__name__)

chat_history_ids = None

@app.route("/")
def index():
    return render_template('chat.html')

@app.route("/get", methods=["POST"])
def chat():
    global chat_history_ids
    msg = request.form["msg"].lower()

    if "traffic" in msg or "road conditions" in msg:
        traffic_info = get_traffic_info(msg)
        return jsonify({"response": traffic_info})

    input_ids = tokenizer.encode(msg, return_tensors='pt')
    if chat_history_ids is None:
        chat_history_ids = input_ids
    else:
        chat_history_ids = torch.cat([chat_history_ids, input_ids], dim=-1)
    
    response = get_Chat_response(chat_history_ids)
    return jsonify({"response": response})

def get_Chat_response(input_ids):
    global chat_history_ids
    response_ids = model.generate(input_ids, max_length=1000, pad_token_id=tokenizer.eos_token_id)
    response = tokenizer.decode(response_ids[:, input_ids.shape[-1]:][0], skip_special_tokens=True)
    chat_history_ids = torch.cat([chat_history_ids, response_ids[:, input_ids.shape[-1]:]], dim=-1)
    return response

if __name__ == '__main__':
    app.run(debug=True)