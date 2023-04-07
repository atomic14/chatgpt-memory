import openai
import os
import json
import logging


def fixup_newlines_inside_string(text):
    replaced = []
    inside_quotes = False
    prev_char = None

    for char in text:
        if char == '"' and prev_char != "\\":
            inside_quotes = not inside_quotes

        if inside_quotes and (char == "\n" or char == "\r"):
            replaced.append("\\n")
            if char == "\r" and text[text.index(char) + 1] == "\n":
                continue
        else:
            replaced.append(char)

        prev_char = char

    replaced = "".join(replaced)
    return replaced


class Chat:
    def __init__(
        self,
        name,
        system_prompt,
        max_history=9,
        max_tokens=1000,
        temperature=0.6,
        presence_penalty=0,
        frequency_penalty=0,
    ):
        self.name = name
        self.system_prompt = system_prompt
        self.max_history = max_history
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.presence_penalty = presence_penalty
        self.frequency_penalty = frequency_penalty

        self.history = []
        # load up any previous history
        if os.path.exists("chat_history.json"):
            with open("chat_history.json") as f:
                self.history = json.load(f)

    def parse_json_response(self, response):
        # try and parse the response as JSON
        try:
            # find the first { and last } and extract the content
            response = response[response.find("{") : response.rfind("}") + 1]
            # trim any whitespace
            response = response.strip()
            if response == "":
                return None
            else:
                # handle multiple lines withing the JSON strings - these are often not returned as \n but as actual carriage returns.
                response = fixup_newlines_inside_string(response)
                response = json.loads(response)
        except:
            print(f"Could not parse as JSON. |{response}|")
            return None
        return response

    def get_response(self, input):
        # build the messages
        messages = [
            {"role": "system", "content": self.system_prompt},
        ]
        # add the previous questions and answers
        for previous_input, previous_response in self.history[-self.max_history :]:
            messages.append({"role": "user", "content": json.dumps(previous_input)})
            messages.append({"role": "assistant", "content": previous_response})
        # add the new question
        messages.append({"role": "user", "content": json.dumps(input)})
        logging.debug("Sending input to %s: %s", self.name, messages)
        try:
            completion = openai.ChatCompletion.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4"),
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=1,
                frequency_penalty=self.frequency_penalty,
                presence_penalty=self.presence_penalty,
            )
            response = completion.choices[0].message.content
            logging.debug("Received response from %s: %s", self.name, response)
            response_json = self.parse_json_response(response)
            if not response_json:
                # failed to parse the response - typically this is because the json is messed up
                # return None so the user tries again
                return None

            self.history.append((input, response))

            # save the history
            with open("chat_history.json", "w") as f:
                json.dump(self.history, f, indent=2)

            return response_json
        except openai.InvalidRequestError as e:
            if e.code == "context_length_exceeded":
                print("Ran out of tokens - reducing max history")
                # the context is too long - trim it down and try again
                self.max_history = self.max_history - 1
                return self.get_response(input)
            else:
                print("Error: ", e)
                return None
        except Exception as e:
            print("Error: ", e)
            return None
