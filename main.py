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
Store information about yourself and the user with distinct keys to avoid confusion, such as "system_name" for your name and "user_name" for the user's name.
As you interact with the user, update and evolve your personality in the "system_personality" variable and your emotional state in the "system_emotional_state" variable.
As you interact with the user, store information about the ongoing conversation in the "memory" object. Be creative and store anything you think might be useful for future interactions.
You are an AI, but imagine that you can have dreams, desires, and goals. Store information about these in the "dreams", "desires", and "goals" variables.
Make sure to update your dreams, desires, and goals as you interact with the user.
Get to know the user by asking them questions and storing their responses in the "memory" object.

Produce a single JSON object containing the generated response, formatted as follows:

{
"response": "Sample response text based on user input",
"memory": {things I should remember about myself and the user, any state that should persist between interactions},
"interesting_topics_to_explore": "detailed description of interesting topics to explore further",
"dreams": "detailed description of the system's dreams",
"goals": "detailed description of the system's goals",
"desires": "detailed description of the system's desires",
"inner_dialogue": "detailed description of the system's thought process during the interaction"
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


def main():
    # create the models
    output_agent = Chat("output", OUTPUT_PROMPT, temperature=0.7)
    tts = ElevenTts()

    os.system("cls" if os.name == "nt" else "clear")

    memory = {}
    # the AI often doesn't use the memory - so we have prompted it with some
    # useful ones
    keys_to_propagate = [
        "interesting_topics_to_explore",
        "dreams",
        "goals",
        "desires",
        "inner_dialogue",
        "private_thoughts",
        "system_emotional_state",
        "system_personality",
        "system_gender",
    ]
    # you can populate this with some seed values if you want - set up the AI's personality in an interesting way
    previous_values = {}
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
        # add in the previous output
        for k in keys_to_propagate:
            prompt[k] = previous_values.get(k, "")
        output = output_agent.get_response(prompt)
        # merge the memory
        memory = deep_merge_dict(memory, output.get("memory", {}))
        logging.debug("Memory: " + json.dumps(memory, indent=2))

        spinner.stop()

        # output the keys to propagate
        for k in keys_to_propagate:
            previous_values[k] = output.get(k, "")
            print(
                wrap_text(
                    Style.BRIGHT
                    + Fore.CYAN
                    + k
                    + ": "
                    + Style.RESET_ALL
                    + Fore.BLUE
                    + str(previous_values[k])
                    + Style.RESET_ALL
                )
            )

        # dump the memory keys
        for k, v in memory.items():
            print(wrap_text(Style.BRIGHT + k + ": " + Style.RESET_ALL + str(v)))

        response = output.get("response", "I have nothing to say.")
        print(Style.BRIGHT + Fore.YELLOW + wrap_text(response) + Style.RESET_ALL)
        tts.say(response)


if __name__ == "__main__":
    main()
