The **Dynamic Quiz & Flashcard Generator** (`study-flash`) is an automated study assistant CLI utility.

![Summary](https://github.com/user-attachments/assets/e6212c33-411d-4c08-a2fa-52c8dc46ea3f "Note: Ignore vepython, it's just an alias")

It ingests textbook chapters, lecture notes, markdown files, or raw text blocks, processes the core concepts using **Gemini 2.5 Flash**, and generates a structured, professional multiple-choice quiz complete with difficulty ratings, topic summaries, correct answer keys, and detailed explanations.

---

### Breakdown of Each File in the Project

The project consists of three core components:

#### 1. `quiz_gen.py` (The Core CLI Execution Engine)

This file manages user input handling, command-line routing, Gemini API communication, error suppression, and the terminal display layout.

* **CLI & Argument Parsing (`Typer`):** Sets up the `generate` command, accepting required study file paths or raw text strings along with optional flags like `--num` (or `-n`) to control the question count.
* **File Ingestion (`extract_text`):** Safely reads local input files using UTF-8 encoding or falls back to treating inputs as raw inline strings, while ensuring your `GEMINI_API_KEY` is configured.
* **Gemini API Integration:** Submits your study notes to `gemini-2.5-flash` with structured JSON enforcement (`response_schema=QuizReport`) and a custom instructional designer prompt, while temporarily suppressing background SDK warning logs.
* **Terminal UI Rendering (`Rich`):** Uses Python's `rich` library to draw clean cyan headers, yellow summary panels, color-coded difficulty question cards (Green/Yellow/Red), and a structured table for answer keys and explanations.

#### 2. `schemas.py` (The Data Contract & Schema Definition)

This file defines the strict data validation models using **Pydantic V2**. By supplying these classes to Gemini's configuration, it guarantees that the API response always returns structured, perfectly-typed JSON.

* **`QuizQuestion`**: Validates individual quiz items, capturing the question text, a list of 4 options, the correct answer, the pedagogical explanation, and a difficulty tag (`Easy`, `Medium`, `Hard`).
* **`QuizReport`**: Serves as the root container model, wrapping the quiz `title`, a 2–3 sentence `topic_summary`, and the full list of generated questions.

#### 3. `requirements.txt` (Project Dependencies)

Contains the common developer stack required to run and build the application:

* `google-genai`: The official Google GenAI SDK for communicating with Gemini 2.5 Flash.
* `pydantic`: Powers data validation and schema enforcement (`schemas.py`).
* `typer`: Manages command-line argument and flag routing (`quiz_gen.py`).
* `rich`: Handles high-end terminal dashboard rendering, panels, tables, and colors.
