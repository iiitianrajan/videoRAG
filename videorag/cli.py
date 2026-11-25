"""Command-line interface for VideoRAG."""

from dotenv import load_dotenv

from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import ask_question, build_rag_chain
from core.summarizer import generate_title, summarize
from core.transcriber import transcribe_all
from utils.audio_processor import cleanup_audio_files, process_input


def run_pipeline(source: str, language: str = "english") -> dict:
    """Analyze a recording and return its transcript, insights, and RAG chain."""
    chunks = process_input(source)
    try:
        transcript = transcribe_all(chunks, language)
    finally:
        cleanup_audio_files(chunks)

    return {
        "title": generate_title(transcript),
        "transcript": transcript,
        "summary": summarize(transcript),
        "action_items": extract_action_items(transcript),
        "key_decisions": extract_key_decisions(transcript),
        "open_questions": extract_questions(transcript),
        "rag_chain": build_rag_chain(transcript),
    }


def main() -> None:
    load_dotenv()
    source = input("Enter YouTube URL or local file path: ").strip()
    language = input("Language (english/hinglish): ").strip() or "english"
    result = run_pipeline(source, language)

    print(f"\nTitle: {result['title']}")
    print(f"\nSummary:\n{result['summary']}")
    print(f"\nAction items:\n{result['action_items']}")
    print(f"\nKey decisions:\n{result['key_decisions']}")
    print(f"\nOpen questions:\n{result['open_questions']}")
    print("\nChat with your meeting (type 'exit' to quit)\n")
    while True:
        question = input("You: ").strip()
        if question.lower() in {"exit", "quit", "q"}:
            break
        if question:
            print(f"\nAssistant: {ask_question(result['rag_chain'], question)}\n")
