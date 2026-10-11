import os
import sys
from pathlib import Path
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from google import genai
from google.genai import types

from schemas import QuizReport

app = typer.Typer(help="Dynamic Quiz & Flashcard Generator CLI")
console = Console()


def extract_text(file_path: str) -> str:
    path = Path(file_path)
    if not path.exists():
        console.print(f"[bold red]Error: File not found -> {file_path}[/bold red]")
        raise typer.Exit(1)

    try:
        return path.read_text(encoding="utf-8")
    except Exception as e:
        console.print(f"[bold red]Failed to read file: {e}[/bold red]")
        raise typer.Exit(1)


@app.command()
def generate(
    source_input: str = typer.Argument(
        ..., help="Path to text/markdown study file or raw input text string"
    ),
    num_questions: int = typer.Option(
        5, "--num", "-n", help="Number of quiz questions to generate"
    ),
):
    """Generate a dynamic multiple-choice quiz with difficulty tags and answer keys from study material."""

    if not os.environ.get("GEMINI_API_KEY"):
        console.print(
            "[bold red]Error: GEMINI_API_KEY environment variable is not set.[/bold red]"
        )
        raise typer.Exit(1)

    # Handle input being a file path or inline text
    if Path(source_input).exists():
        source_text = extract_text(source_input)
    else:
        source_text = source_input

    client = genai.Client()

    prompt = f"""
You are an expert educator and instructional designer. 
Analyze the following source text and generate a high-quality multiple-choice quiz consisting of exactly {num_questions} questions. Include 4 distinct options per question, the correct answer, a detailed explanation, and a difficulty tag (Easy, Medium, Hard).

=== SOURCE MATERIAL ===
{source_text}
"""

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(
            description="Analyzing study material & generating quiz questions...",
            total=None,
        )

        try:
            # Temporarily suppress stderr to keep terminal output clean
            original_stderr = sys.stderr
            sys.stderr = open(os.devnull, "w")
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=QuizReport,
                        temperature=0.3,
                    ),
                )
            finally:
                sys.stderr.close()
                sys.stderr = original_stderr

            result = QuizReport.model_validate_json(response.text)
        except Exception as e:
            console.print(f"[bold red]Quiz generation failed: {e}[/bold red]")
            raise typer.Exit(1)

    # Render Dashboard using Rich
    console.print("\n")
    console.print(
        Panel.fit(
            f"[bold cyan]🎓 {result.title}[/bold cyan]",
            title="Dynamic Quiz Generator",
            border_style="cyan",
        )
    )

    # Summary Panel
    console.print(
        Panel(
            result.topic_summary,
            title="[bold yellow]📖 Topic Summary[/bold yellow]",
            border_style="yellow",
        )
    )

    # Render Questions
    for idx, q in enumerate(result.questions, 1):
        diff_color = (
            "green"
            if q.difficulty.lower() == "easy"
            else ("yellow" if q.difficulty.lower() == "medium" else "red")
        )

        q_content = f"[bold]{q.question}[/bold]\n\n"
        for opt in q.options:
            q_content += f"  • {opt}\n"

        console.print(
            Panel(
                q_content,
                title=f"[cyan]Question #{idx}[/cyan] | Difficulty: [{diff_color}]{q.difficulty}[/{diff_color}]",
                border_style="cyan",
            )
        )

    # Answer Key Table
    console.print("\n[bold green]🔑 Answer Key & Explanations:[/bold green]")
    key_table = Table(show_header=True, header_style="bold magenta")
    key_table.add_column("Q#", justify="center", style="dim")
    key_table.add_column("Correct Answer", style="bold green")
    key_table.add_column("Explanation", style="cyan")

    for idx, q in enumerate(result.questions, 1):
        key_table.add_row(str(idx), q.correct_answer, q.explanation)

    console.print(key_table)
    console.print("\n")


if __name__ == "__main__":
    app()
