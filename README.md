# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🚨 The Situation

You asked an AI to build a simple "Number Guessing Game" using Streamlit.
It wrote the code, ran away, and now the game is unplayable. 

- You can't win.
- The hints lie to you.
- The secret number seems to have commitment issues.

## 🛠️ Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the broken app: `python -m streamlit run app.py`

## 🕵️‍♂️ Your Mission

1. **Play the game.** Open the "Developer Debug Info" tab in the app to see the secret number. Try to win.
2. **Find the State Bug.** Why does the secret number change every time you click "Submit"? Ask ChatGPT: *"How do I keep a variable from resetting in Streamlit when I click a button?"*
3. **Fix the Logic.** The hints ("Higher/Lower") are wrong. Fix them.
4. **Refactor & Test.** - Move the logic into `logic_utils.py`.
   - Run `pytest` in your terminal.
   - Keep fixing until all tests pass!

## 📝 Document Your Experience

- [Guess a number from a range ] Describe the game's purpose.
- [the hints were backwards, when the game is over the new game button does not seem to reset the game, number of attempt in the UI does not reflect the actual number of attempts remaining, easy has less normal of attempts than normal, the scoring was incorrect ] Detail which bugs you found.
- [worked with claude to apply fixes for the bugs mentioned above] Explain what fixes you applied.

## 📸 Demo Walkthrough

Describe your fixed game in numbered steps so a reader can follow along without watching a video:

1. user choose difficulity and enter a guess based on the range provided
2. user choose easy and enter a guess of 2, Game returns "Go HIGHER!"
3. User enters a guess of 15, Game returns "Go LOWER!"
4. Score updates correctly after each guess in the backend
5. Game ends after the correct guess.

**Screenshot** *(optional)*: <!-- Insert a screenshot of your fixed, winning game here -->

## 🧪 Test Results

```
# Paste your pytest output here, e.g.:
# pytest tests/
# ========================= X passed in 0.XXs =========================
```

pytest test/ 
=================================================== test session starts ====================================================
platform win32 -- Python 3.10.11, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Drive D\Courses\codepath\AI101\module2\ai110-module1show-gameglitchinvestigator-starter
plugins: anyio-4.15.1
collected 25 items                                                                                                          

test\test_game_logic.py .........................                                                                     [100%]

==================================================== 25 passed in 0.04s ====================================================

## 🚀 Stretch Features

- [ ] [If you choose to complete Challenge 4, describe the Enhanced UI changes here — a screenshot is optional]
