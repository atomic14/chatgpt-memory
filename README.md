# Experiments With ChatGPT and memory

This is a bit of fun to see how to get ChatGPT to remember things.

The inspiration was from some random tweets where someone was trying to play 20 questions with ChatGPT.

ChatGPT is very good at the guessing side of things, but asking it to think of something for the user to guess is a bit trickier as it doesn't have anywhere to store the thing it is thinking of.

This started with a simple prompt to give the AI somewhere to store information and expanded into some more fixed keys to help the bot know what to store.

It's quite fun to see the contents of the `inner_dialogue` and `private_thoughts` - you may need to keep reminding yourself that it is not thinking!

This code works best with `gpt-4`, but you can get reasonable results with `gpt-3.5-turbo`.

# Setup

Make sure you've got Python installed and then install the requirements:

```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

You will also need an API key from [OpenAI](https://openai.com/).

Once you've got your key copy `.env.sample` to `.env` and add your key.

# Usage

```
python main.py
```

# Fun things to try

Get the bot to give itself a human name and then ask it why it picked the name it did. "Give yourself a human name", "Why did you pick that name?".

Play guessing games with the bot "Let's play a game, you think of something and I'll guess it".

Hangman is interesting - particularly in terms of what the bot stores in the memory.

# Some challenges

It's quite hard to get the AI to remember things unless it needs to. Prompting it with specific keys helps, but I was hoping it would be more creative in how it uses the memory.

GPT-4 can be very slow... But GPT-3.5-TURBO struggles with detailed prompts and does not always produce pleasing responses.

For example, GPT-4 will usually pick a nice human name, GPT-3.5 will often just go with "AI" or "Assistant" unless you force it to pick a human name.

When playing the guessing game - you have to be very explicit with GPT-3.5 - for example:

`Think of a random object and I'll try and guess it` will generally work well with GPT-4, but GPT-3.5 will often not store anything.

You will need to say something like:

`Think of a random object and store it in your memory under "random_object". Now ask me to guess what it is.`

And then GPT-3.5 will remember the object.

For playing games like Hangman - even with GPT-4 - you will need to be very explicit about what the bot is doing. For example:

`Let's play hangman, think of a word and I'll try and guess it. Make sure you keep track of the guessed letters and their positions in the word.`

If you don't do this then it will often start off great, but then lose track of which letters in the word have been guessed. This can still happen so you can end up in a situation where the memory contains:

```
word: "elephant",
guesses_letters: ["e"],
display_word: "_ _ e _ _ _ _ _"
```

# Token Limit

This uses a lot of tokens - so it will cost quite a bit of money to run. There may be ways to optimize the prompts that are fed back into the system with each user input, but I haven't done much experimentation with that.

The code will try and be clever and will reduce the amount of chat history it sends up to the server. With the memory and the fixed keys this may not have a massive impact on the conversation.

# Future Work

The bot can be quite reluctant to remember things. Giving it explicit keys seems to help quite a bit - but it would be nice to see it be more creative in how it uses the memory.