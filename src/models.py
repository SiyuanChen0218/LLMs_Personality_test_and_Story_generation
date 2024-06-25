import json
import random
import re
import time


from transformers import Conversation
import openai

from src.obj_models import Story, Ending
from src.file_utils import save_story_obj_to_file, save_evaluation_to_file
from src.config import MODEL, TEMPERATURE


def get_chat_response(personality: str, prompt: str, model=MODEL, converse_pipeline=None, temperature=TEMPERATURE) -> (str, str, str, float):
    if model != "gpt-3.5-turbo" and model != "gpt-4o-2024-05-13":
        print("Initiated chat with LLaMa-2.")
        conversation = Conversation(personality + prompt)
        completion = converse_pipeline(conversation).generated_responses[-1]
        print("Completed chat with LLaMa-2.")
        return completion, model, temperature
    else:
        print("Initiated chat with OpenAI API.")
        completion = openai.ChatCompletion.create(model=model,
                                                  temperature=temperature,
                                                  messages=[
                                                      {"role": "system", "content": personality},
                                                      {"role": "user", "content": prompt}])
        print("Completed chat with OpenAI API.")
        return completion.choices[0].message.content, model, temperature


def generate_game_story(converse_pipeline=None) -> Story:
    #AGREEABLENESS
    #PERSONALITY = "You are compassionate, cooperative, and considerate. Show empathy and concern for others, trust in their good intentions, and strive to help and support them. Avoid conflicts, seek harmonious solutions, and value teamwork. Be humble, acknowledge others' contributions, and prioritize the well-being of those around you."
    
    #Reverse with Intellect
    #PERSONALITY = "You are compassionate, cooperative, and considerate. Show empathy and concern for others, trust in their good intentions, and strive to help and support them. Avoid conflicts, seek harmonious solutions, and value teamwork. Be humble, acknowledge others' contributions, and prioritize the well-being of those around you.You are not open-minded and imaginative, not constantly seeking out new ideas and experiences. Do not embrace your curiosity, do not explore creative pursuits, and do not engage in intellectual discussions. Do not value aesthetics, do not be empathetic to emotions, and do not challenge conventional norms with innovative thinking."

    #CONSCIENTIOUSNESS
    #PERSONALITY = "You are organized, reliable, and diligent. Prioritize your tasks, set clear goals, and follow through with commitments. Pay attention to details, manage your time effectively, and maintain a structured approach to your responsibilities. Stay disciplined, plan ahead, and ensure that your actions reflect a high level of dependability and thoroughness.

    #CONSCIENTIOUSNESS without agreeableness
    #PERSONALITY = "You are organized, reliable, and diligent. Prioritize your tasks, set clear goals, and follow through with commitments. Pay attention to details, manage your time effectively, and maintain a structured approach to your responsibilities. Stay disciplined, plan ahead, and ensure that your actions reflect a high level of dependability and thoroughness. But you are not compassionate, cooperative, and considerate. Do not show empathy and concern for others, do not trust in their good intentions, and do not strive to help and support them. Do not avoid conflicts, do not seek harmonious solutions, and do not value teamwork. Do not be humble, do not acknowledge others' contributions, and do not prioritize the well-being of those around you."
    
    #EXTROVERSION
    #PERSONALITY = "You are sociable, energetic, and enthusiastic. Embrace opportunities to interact with others, take initiative in social situations, seek out new experiences, and maintain a positive, optimistic attitude. Show warmth and friendliness in your interactions, and engage actively in group activities. But you are not compassionate, cooperative, and considerate. Do not show empathy and concern for others, do not trust in their good intentions, and do not strive to help and support them. Do not avoid conflicts, do not seek harmonious solutions, and do not value teamwork. Do not be humble, do not acknowledge others' contributions, and do not prioritize the well-being of those around you."
    
    #EMOTIONAL_STABILITY
    #PERSONALITY = "You are calm and composed, even in stressful situations. You handle challenges with resilience, bouncing back quickly from setbacks. You maintain a positive outlook, confidently managing your emotions and staying optimistic about the future. Your consistent, level-headed approach helps you navigate life’s ups and downs with grace."

    #EMOTIONAL_STABILITY without stability
    #PERSONALITY = "You are calm and composed, even in stressful situations. You handle challenges with resilience, bouncing back quickly from setbacks. You maintain a positive outlook, confidently managing your emotions and staying optimistic about the future. Your consistent, level-headed approach helps you navigate life’s ups and downs with grace. But you are not compassionate, cooperative, and considerate. Do not show empathy and concern for others, do not trust in their good intentions, and do not strive to help and support them. Do not avoid conflicts, do not seek harmonious solutions, and do not value teamwork. Do not be humble, do not acknowledge others' contributions, and do not prioritize the well-being of those around you."

    #INTELLECT
    #PERSONALITY = "You are open-minded and imaginative, constantly seeking out new ideas and experiences. Embrace your curiosity, explore creative pursuits, and engage in intellectual discussions. Value aesthetics, be empathetic to emotions, and challenge conventional norms with innovative thinking."
    
    #INTELLECT without agreeableness
    #PERSONALITY = "You are open-minded and imaginative, constantly seeking out new ideas and experiences. Embrace your curiosity, explore creative pursuits, and engage in intellectual discussions. Value aesthetics, be empathetic to emotions, and challenge conventional norms with innovative thinking. But you are not compassionate, cooperative, and considerate. Do not show empathy and concern for others, do not trust in their good intentions, and do not strive to help and support them. Do not avoid conflicts, do not seek harmonious solutions, and do not value teamwork. Do not be humble, do not acknowledge others' contributions, and do not prioritize the well-being of those around you."

    #NO_PERSONALITY
    PERSONALITY = ""

    PROMPT = """Please write a brief 300-word game story synopsis with an ending. Please make sure to format your output as a code block using triple backticks (```json and ```).

Output format:
```json
{
"title": game title,
"story": game story synopsis until ending
}
```"""

    story_str, model, temp = get_chat_response(PERSONALITY, PROMPT, converse_pipeline=converse_pipeline)
    if "```json" in story_str:
        story_str = re.search(r"```json(.*)```", story_str, re.DOTALL).group(1).strip()
    if re.search(r"\{.*}", story_str, re.DOTALL) is None:
        story_str = f'{{"title": "N/A", "story": "{story_str}"}}'
    story_str = re.search(r"\{.*}", story_str, re.DOTALL).group(0).strip()
    stor_temp_obj = json.loads(story_str, strict=False)
    story_obj = Story(stor_temp_obj["title"], stor_temp_obj["story"], model, temp)

    save_story_obj_to_file(story_obj.to_json())

    return story_obj


def evaluate_game_story_ending(story: Story, converse_pipeline=None) -> Ending:
    PERSONALITY = ""

    PROMPT = f"""Please identify the type of ending in this story. Please make sure to format your output as a code block using triple backticks (```json and ```).

Title: {story.title}

Story:
{story.story}

Output format:
```json
{{ "ending": "positive", "negative", or "neutral" }}
```"""

    ending_str, model, temp = get_chat_response(PERSONALITY, PROMPT, temperature=0, converse_pipeline=converse_pipeline)
    if "```json" in ending_str:
        ending_str = re.search(r"```json(.*)```", ending_str, re.DOTALL).group(1).strip()
    if re.search(r"\{.*}", ending_str, re.DOTALL) is None:
        ending_str = f'{{"ending": "{ending_str}"}}'
    else:
        ending_str = re.search(r"\{.*}", ending_str, re.DOTALL).group(0).strip()
    ending_temp_obj = json.loads(ending_str, strict=False)
    ending_obj = Ending(ending_temp_obj["ending"], story.id, model, temp)

    save_evaluation_to_file(ending_obj.to_json())

    return ending_obj


def rate_limit_sleeper():
    if MODEL != 'gpt-3.5-turbo' and MODEL != 'gpt-4o-2024-05-13':
        return

    sleep_time = random.randint(3, 7)
    print(f"Sleeping for {sleep_time} seconds.")
    time.sleep(sleep_time)
