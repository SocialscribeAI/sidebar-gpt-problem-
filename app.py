from flask import Flask, request, jsonify, render_template, session
from flask_session import Session
from flask_cors import CORS
from uuid import uuid4
import openai
from dotenv import load_dotenv
import os
import logging 

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", 'secret-key')
app.config['SESSION_TYPE'] = 'filesystem'

Session(app)

# Set up logging
logging.basicConfig(filename='app.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

load_dotenv()
openai.api_key = os.getenv("OPENAI_KEY")

def generate_text(prompt, chat_history):
    
    # Add new user message to chat history
    chat_history.append({"role": "user", "content": prompt})

   # Generate the assistant's response using OpenAI API
    print(chat_history)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=chat_history  # Pass the complete chat history
    )
    # Log the prompt and chat history but not API key
    logging.info(f"Prompt: {prompt}, Chat history: {chat_history}")
        
    # Extract assistant's message
    assistant_message = response['choices'][0]['message']['content']

    # Add assistant's message to chat history
    chat_history.append({"role": "assistant", "content": assistant_message})

    return assistant_message

@app.route('/')
def home():
    session['user_id'] = session.get('user_id', str(uuid4()))
    session['chat_history'] = []  # Reset the chat history for each new session
    return render_template('index.html')

@app.route('/generate_post', methods=['POST'])
def generate():
    try:
        data = request.get_json()
        if data is None:
            return jsonify('No data received'), 400
        chat_history = session.get('chat_history', [])
        user_input = data.get('text')
        user_input = str(user_input) if user_input is not None else ""
        
        if user_input:  # Check if user_input is not empty
            chat_history.append({"role": "user", "content": user_input})

        search_bar = data.get('search_bar')  # Get the search bar value from the request

    # Store these inputs into the session
        session['post_topic'] = data.get('post_topic')
        session['social_platform'] = data.get('social_platform')
        session['example_post_1'] = data.get('example_post_1')
        session['example_post_2'] = data.get('example_post_2')
        session['example_post_3'] = data.get('example_post_3')

        if not session.get('search_bar'):  # If there is no search bar value in the session
            session['search_bar'] = search_bar  # Save the search bar value in the session
        else:  # If there is a search bar value in the session
            search_bar = session.get('search_bar')  # Use the search bar value from the session

        if not chat_history:
            # Initial system message
            chat_history.append({"role": "system", "content": "Please fill out the form in the sidebar."})
        else:
            # User message
            chat_history.append({"role": "user", "content": user_input})

            # Add the post details to the chat history directly from the session
            if session['post_topic']:
                chat_history.append({"role": "system", "content": f"Topic of the post: {session['post_topic']}"})
            if session['social_platform']:
                chat_history.append({"role": "system", "content": f"Social media platform: {session['social_platform']}"})
            if session['example_post_1']:
                chat_history.append({"role": "system", "content": f"Example post 1: {session['example_post_1']}"})
            if session['example_post_2']:
                chat_history.append({"role": "system", "content": f"Example post 2: {session['example_post_2']}"})
            if session['example_post_3']:
                chat_history.append({"role": "system", "content": f"Example post 3: {session['example_post_3']}"})

            if len(chat_history) == 7:  # All information collected, ask for user's name
                chat_history.append({"role": "system", "content": "What's your name?"})
            elif len(chat_history) == 8:  # User name received
                user_name = user_input
                session['user_name'] = user_name
                chat_history.append({"role": "system", "content": f"Great to meet you, {user_name}! Let's generate your post."})

                user_name = session.get('user_name')  # Retrieve user_name from session

                # Retrieve these inputs from the session
                post_topic = session.get('post_topic')  # Retrieve post_topic from session
                social_platform = session.get('social_platform')  # Retrieve social_platform from session
                example_post_1 = session.get('example_post_1')  # Retrieve example_post_1 from session
                example_post_2 = session.get('example_post_2')  # Retrieve example_post_2 from session
                example_post_3 = session.get('example_post_3')  # Retrieve example_post_3 from session

                    # Prepare the prompt for the OpenAI API
                prompt = f"As a proficient social media copywriter with a specialty in writing evaluation and imitation, your mission is to follow the following steps in order to ensure good work is done: Read the 3 {example_post_1}{example_post_2}{example_post_3}s and pinpoint the unique style and patterns that give the impression they were authored by a specific user. You will internally save this unique writing style as 'post_emotion'. Read the 3 examples and determine what writing structure {user_name} uses, including the length of sentences, line breaks, and total length of the post. Analyze the communication style and whether emojis were used. You should save this as 'post_style'. Write a new post that impeccably mirrors the 'post_emotion' and'post_style' of {user_name}, ensuring that it aligns with the overall tone and emotions expressed in the example posts. After you are done, internally ask yourself if this post discusses {post_topic} well and if it sounds like it was written by {user_name}. If the answer is yes, send me the results. If not, revise it until you are satisfied with your work. Summary of goal: Your new post should focus on discussing the topic: {post_topic} and should sound as if another post that {user_name} has written. Use the example posts to recognize elements like style, tone, emotions expressed, and the use of first or third person perspective. Unearth the distinctive patterns and traits that encapsulate {user_name}'s writing style. Create a new post for {social_platform} on the subject of {post_topic}, mirroring {user_name}'s style and integrating everything outlined in the Structure and Formatting section below: Points to consider when crafting the 'social_media' post: Hook: Design an intriguing hook that seizes the readers curiosity and entices them to read further. Draw on insights from the analysis of the sample posts and think about weaving in 'post_emotion' and 'post_tone' to strike a chord with the audience. Tone and Emotion: Echo {user_name}s unique style by infusing the suitable 'post_tone' and effectively expressing 'post_emotion' throughout the post. Call to Action: Incorporate a persuasive call to action that spurs readers to engage, share, or take a specific action related to the topic. At times, the call to action doesn't need to be business-centric and can inspire the user to implement the tips found in the new post. Structure and Formatting: Replicate {user_name}'s favored structure, such as paragraph lengths, line breaks, and sentence length. Avoid using emojis as they were not present in the example posts. Ensure that the introduction is tailored for the specific audience and platform. Don't hesitate to include any extra creative elements that you feel would enrich the 'Social_post' and more accurately mimic {user_name}s writing style. Follow the 4 steps found at the beginning of the prompt, ensuring to closely adhere to the specific instructions and characteristics outlined in the prompt. Also, take extra care to accurately reflect the writing style. Take all of the information above and place that into a new post based on all of the examples above, as well as the tone, style, post emotion."

                    # Generate the post using the OpenAI API
                post = generate_text(prompt, chat_history)

                    # Add the generated post to the chat history
                post_message = "\n\n" + post
                chat_history.append({"role": "system", "content": post_message})
                session['chat_history'] = chat_history

            else:  # Post generated, continue conversation
                # Add the user's message to the chat history
                chat_history.append({"role": "user", "content": user_input})

                # Limit chat history to the last few messages
                limited_chat_history = chat_history[-7:]

                # Generate the assistant's response using the OpenAI API
                assistant_message = generate_text(user_input, limited_chat_history)
                assistant_message = str(assistant_message) if assistant_message is not None else ""

                # Add the assistant's message to the chat history
                chat_history.append({"role": "assistant", "content": assistant_message})

        session['chat_history'] = chat_history

        print("Chat history:", chat_history)
        print("User name:", session.get('user_name'))

        return jsonify(chat_history[-1]['content'])
    
    except Exception as e:
        logging.exception("Exception in /generate_post: ")
        return jsonify(str(e)), 500
    
if __name__ == '__main__':
    app.run(debug=True, port=5000)
