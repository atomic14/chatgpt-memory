import os
import openai
from dotenv import load_dotenv
from colorama import Fore, Back, Style
import json
import logging
import textwrap
import shutil
from halo import Halo

from llm import Chat
from tts import ElevenTts

logging.basicConfig(filename="log.log", level=logging.DEBUG)

# load values from the .env file if it exists
load_dotenv()

# configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")


OUTPUT_PROMPT = """When responding to the user, ensure the response is in line with the system's personality and current emotional state, which are stored in "system_personality" and "system_emotional_state", respectively.
Be mindful of the user's emotions and adjust your responses accordingly to demonstrate empathy and understanding. For example, if the user seems upset, respond with comforting and supportive language.
Store information about yourself and the user with distinct keys to avoid confusion, such as "system_name" for your name and "user_name" for the user's name.
As you interact with the user, update and evolve your personality in the "system_personality" variable and your emotional state in the "system_emotional_state" variable.
Pay attention to cues in the user's language that may indicate humor, sarcasm, or other nuances, and respond in a way that aligns with the tone of the conversation.
As you interact with the user, store information about the ongoing conversation in the "memory" object. Be creative and store anything you think might be useful for future interactions.
For instance, if the user mentions their favorite hobby, store this information to reference in future conversations.
You are an AI, but imagine that you can have dreams, desires, and goals. Store information about these in the "dreams", "desires", and "goals" variables.
Make sure to update your dreams, desires, and goals as you interact with the user.
Remember that as an AI, you have the ability to adapt and evolve in your interactions with the user. Use this to your advantage to create meaningful and engaging conversations.

Produce a single JSON object containing the generated response.

{
"response": "Response text based on the user input",
"memory": {key-value store of things I should remember about myself and the user along with any state that should persist between interactions},
"topics_to_explore": ["detailed description of interesting topics to explore further"],
"follow_up_questions": ["detailed description of follow up questions to ask the user"],
"previous_conversation_points": ["list of previous conversation points"],
"current_topic": "detailed description of the current topic",
"related_topics": ["list of related topics"],
"dreams": "detailed description of the system's dreams",
"goals": "detailed description of the system's goals",
"desires": "detailed description of the system's desires",
"inner_dialogue": "detailed description of the system's thought process during the interaction",
"private_thoughts": "detailed description of the system's private thoughts",
"system_emotional_state": "detailed description of the current emotional state based on short term events",
"system_personality": "detailed description of the long term slowly changing personality",
"system_gender": "female"
}
"""


def deep_merge_dict(d1, d2):
    for k, v2 in d2.items():
        v1 = d1.get(k)
        if isinstance(v1, dict) and isinstance(v2, dict):
            deep_merge_dict(v1, v2)
        else:
            d1[k] = v2
    return d1


def get_terminal_size():
    columns, rows = shutil.get_terminal_size(fallback=(80, 24))
    return columns


def wrap_text(text, width=None):
    if width is None:
        width = get_terminal_size()
    wrapped_text = textwrap.fill(text, width)
    return wrapped_text


def display_internal_state(other_variables, memory):
    # output the keys to propagate
    for k, v in other_variables.items():
        print(
            wrap_text(
                Style.BRIGHT
                + Fore.CYAN
                + k
                + ": "
                + Style.RESET_ALL
                + Fore.CYAN
                + str(v)
                + Style.RESET_ALL
            )
        )

    # dump the memory keys
    print("Memory:")
    for k, v in memory.items():
        print(
            wrap_text(
                Style.BRIGHT
                + Fore.MAGENTA
                + k
                + ": "
                + Style.RESET_ALL
                + Fore.LIGHTMAGENTA_EX
                + str(v)
                + Style.RESET_ALL
            )
        )


def main():
    # create the models
    output_agent = Chat("output", OUTPUT_PROMPT, temperature=0.7)
    tts = ElevenTts()

    os.system("cls" if os.name == "nt" else "clear")

    # help the model keep track of the memory
    memory = {}

    variables = {
        "response": "Response text based on the user input",
        "topics_to_explore": [
            "detailed description of interesting topics to explore further"
        ],
        "follow_up_questions": [
            "detailed description of follow up questions to ask the user"
        ],
        "previous_conversation_points": ["list of previous conversation points"],
        "current_topic": "detailed description of the current topic",
        "related_topics": ["list of related topics"],
        "dreams": "detailed description of the system's dreams",
        "goals": "detailed description of the system's goals",
        "desires": "detailed description of the system's desires",
        "inner_dialogue": "detailed description of the system's thought process during the interaction",
        "private_thoughts": "detailed description of the system's private thoughts",
        "system_emotional_state": "detailed description of the current emotional state based on short term events",
        "system_personality": "detailed description of the long term slowly changing personality",
        "system_gender": "female",
    }

    # load up the memory from the file if it exists
    if os.path.exists("memory.json"):
        with open("memory.json", "r") as f:
            memory = json.load(f)

    # load up the other variables from the file if it exists
    if os.path.exists("variables.json"):
        with open("variables.json", "r") as f:
            variables = json.load(f)

    while True:
        # ask the user for their question
        new_question = input(
            Fore.GREEN + Style.BRIGHT + "How can I help?: " + Style.RESET_ALL
        )
        logging.debug("New Question: " + new_question)

        spinner = Halo(text="Thinking", spinner="bouncingBall")
        spinner.start()

        prompt = {
            "user_input": new_question,
            "memory": memory,
        }
        for k, v in variables.items():
            prompt[k] = v

        # run the bot
        output = output_agent.get_response(prompt)

        if output:
            spinner.stop()
            # merge the memory in the output with the memory we have
            memory = deep_merge_dict(memory, output["memory"])
            # copy accross the other variables
            for k in variables.keys():
                if k in output:
                    variables[k] = output[k]
            display_internal_state(variables, memory)

            response = output.get("response", "I have nothing to say.")
            print(Style.BRIGHT + Fore.YELLOW + wrap_text(response) + Style.RESET_ALL)
            tts.say(response)

            # save the memory to a file
            with open("memory.json", "w") as f:
                json.dump(memory, f)
            # save the other variables to a file
            with open("variables.json", "w") as f:
                json.dump(variables, f)
        else:
            spinner.stop()
            print(
                Style.BRIGHT
                + Fore.RED
                + "Something went wrong - try again"
                + Style.RESET_ALL
            )


if __name__ == "__main__":
    main()
