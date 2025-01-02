from flask import Flask, jsonify, request
import openai
import time
import threading

app = Flask(__name__)

@app.route('/')
def home():
    return 'Hello, World!'
    
@app.route('/about')
def about():
    return 'About'

@app.route('/test')
def test():
    return 'Test'

api_key = "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"

openai.api_key = api_key
lang = 'en'
conversation_histories = {}
last_interaction_times = {}
HISTORY_TIMEOUT = 15 * 60

@app.route('/process-ai', methods=['POST'])
def process_ai():
    try:
        data = request.json
        user_id = data.get('user_id')
        audio_command = data.get('command').lower()
        ai_name = data.get('ai_name', 'Friday').lower()

        if not user_id:
            return jsonify({"error": "User ID is required."}), 400
        
        # Record the current timestamp for the user
        last_interaction_times[user_id] = time.time()

        # Initialize user conversation history if not present
        if user_id not in conversation_histories:
            conversation_histories[user_id] = [
                {"role": "system", "content": f"You are an AI assistant named {ai_name}. Always remember any user information provided during the conversation."}
            ]

        # Add user input to their conversation history
        conversation_histories[user_id].append({"role": "user", "content": audio_command})

        if ai_name in audio_command:
            # Make the OpenAI API call
            completion = openai.chat.completions.create(
                model="gpt-3.5-turbo", 
                messages=conversation_histories[user_id]
            )

            # Extract AI response
            response_text = completion.choices[0].message.content

            # Add AI response to the user's conversation history
            conversation_histories[user_id].append({"role": "assistant", "content": response_text})

            return jsonify({"response": response_text}), 200

        return jsonify({"response": f"Command not recognized or '{ai_name}' not mentioned."}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# Background thread to clean up old conversation histories
def clear_old_histories():
    while True:
        current_time = time.time()
        to_delete = [
            user_id
            for user_id, last_time in last_interaction_times.items()
            if current_time - last_time > HISTORY_TIMEOUT
        ]
        for user_id in to_delete:
            conversation_histories.pop(user_id, None)
            last_interaction_times.pop(user_id, None)
        time.sleep(60)  # Check every minute
        
# Start the cleanup thread
cleanup_thread = threading.Thread(target=clear_old_histories, daemon=True)
cleanup_thread.start()

if __name__ == '__main__':
    app.run(debug=True)
