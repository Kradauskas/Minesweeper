# KRsweeper 💣

OOP 2026 coursework project — Minesweeper game with a planned AI solver, 
built in Python using Tkinter.

ⓘ *AI was used in this project. Generation Then Comprehension strategy.*

## KNOWN LIMITATIONS:
- AI can still hit a mine
- scores.json could get corrupted if the app crashed mid-write.
- Password is stored in plaintext

## Timeline
- **Feb 10–15** — Initial Minesweeper logic (no classes)
- **Feb 15–17** — Simple UI with Tkinter
- **Mar 10–13** — Rewrote logic into a single class
- **Apr 15** — Branched the code out to a total of 3 classes (GameEntity, Player and KRsweeper)
- **Apr 17** —
  - Cleaned the code up (Lithuanian function names -> English);
  - Added standard minesweeper mine count colors (1-blue, 2-green, 3-red, etc.);
  - Added a timer to track PB's;
  - Save PB's in scores.json with a password so 2 people with same usernames wouldn't have their score overwritten (**DO NOT USE REAL PASSWORDS, THEY ARE SAVED AS TEXT IN THE JSON FILE**)
- **Apr 18** - Added all planned features (the game needs UI polishing, retry button upon failing, various bug fixed, etc.)
- **Apr 19** - Game is pretty much done. I am happy how it turned out.
  
## ~~Planned features~~ (DONE)
- ~~AI solver~~

- ~~Difficulty presets (Easy / Medium / Hard)~~

- ~~Timer & scoreboard~~

## How to run

### 1. Clone the repository

```bash
git clone https://github.com/Kradauskas/KRsweeper.git
```

### 2. Navigate into the project folder

```bash
cd KRsweeper
```

### 3. (Optional) Create a virtual environment

```bash
python -m venv venv
```

Activate it:

* **Windows (PowerShell):**

  ```bash
  venv\Scripts\activate
  ```
* **Mac/Linux:**

  ```bash
  source venv/bin/activate
  ```

### 4. Run the game

```bash
python main.py
```

---

### Notes

* Make sure you have Python installed (recommended 3.10+).
* If `python` doesn’t work, try `python3`.


