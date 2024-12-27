from flask import Flask, jsonify, request
import openai

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

@app.post('/process-ai', methods=['POST'])
def process_ai():
    try: 
        data = request.json
        user_id = data.get('user_id')
        audio_command = data.get('command')
        ai_name = data.get('ai_name', 'Friday')
        
        if not user_id:
            return jsonify({"error": "User ID is required."}), 400
        
         # Initialize user conversation history if not present
        if user_id not in conversation_histories:
            conversation_histories[user_id] = [
                {"role": "system", "content": "You are an AI assistant named {ai_name}."}
            ]
        
        # Add user input to their conversation history
        conversation_histories[user_id].append({"role": "user", "content": audio_command})
        
        if ai_name in audio_command:
            
            # Make the OpenAI API call
            completion = openai.chat.completions.create(
                model="gpt-3.5-turbo", 
                messages=[{"role": "user", "content": audio_command}]
            )
            
            # Add AI response to the user's conversation history
            conversation_histories[user_id].append({"role": "assistant", "content": response_text})
            response_text = completion.choices[0].message.content
            
            return jsonify({"response": response_text}), 200
        
        return jsonify({"response": f"Command not recognized or '{ai_name}' not mentioned."}), 400
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
