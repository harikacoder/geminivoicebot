import google.generativeai as genai


openai.api_key = 'AIzaSyAouRCCJ1AamoRC_Hb7TqcTmSz05M0bXqM'
def chat_with_gpt(prompt):
    response = openai.Completion.create(
        engine="gemini-1.5",
        prompt=prompt,
        max_tokens=150
    )
    return response.choices[0].text.strip()

if __name__ == "__main__":
    print("Chatbot: Hi! How can I help you today?")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Chatbot: Goodbye!")
            break
        response = chat_with_gpt(user_input)
        print(f"Chatbot: {response}")
