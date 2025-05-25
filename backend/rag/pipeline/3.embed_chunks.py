from pathlib import Path
from sentence_transformers import SentenceTransformer
import numpy as np

def embed_chunks(input_folder: str, output_file: str, model_name: str = "all-MiniLM-L6-v2"):
    model = SentenceTransformer(model_name)
    input_path = Path(input_folder)
    embeddings = []
    metadata = []

    texts = []
    for chunk_file in sorted(input_path.glob("*.txt")):
        text = chunk_file.read_text(encoding="utf-8")
        embedding = model.encode(text)
        embeddings.append(embedding)
        metadata.append(chunk_file.name)
        texts.append(text)  # 👈 save the actual chunk

    np.savez(output_file,
            embeddings=np.array(embeddings),
            metadata=np.array(metadata),
            texts=np.array(texts))

if __name__ == "__main__":
    input_folder = "rag/raw_texts/chunks"
    output_file = "rag/embeddings/embeddings.npz"
    embed_chunks(input_folder, output_file)
    print(f"Embedded text chunks from '{input_folder}' to '{output_file}'")