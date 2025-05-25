from pathlib import Path
import textwrap

def chunk_text_files(input_folder: str, output_folder: str, max_chunk_size: int = 500):
    input_path = Path(input_folder)
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)

    for text_file in input_path.glob("*.txt"):
        text = text_file.read_text(encoding="utf-8")
        chunks = textwrap.wrap(text, max_chunk_size)
        for i, chunk in enumerate(chunks):
            chunk_file = output_path / f"{text_file.stem}_chunk{i}.txt"
            chunk_file.write_text(chunk, encoding="utf-8")

if __name__ == "__main__":
    input_folder = "rag/raw_texts/texts"
    output_folder = "rag/raw_texts/chunks"
    chunk_text_files(input_folder, output_folder)
    print(f"Chunked text files from '{input_folder}' to '{output_folder}'")