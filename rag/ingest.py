from pathlib import Path

import pandas as pd
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATASET_PATH = PROJECT_ROOT / "data" / "Dataset" / "Perfume_Dataset.csv"
CHROMA_PATH = PROJECT_ROOT / "data" / "processed" / "chroma_db"


def load_perfume_documents():
    """Load the perfume dataset and convert each perfume into a LangChain Document."""

    df = pd.read_csv(DATASET_PATH, sep=";")

    documents = []

    for index, row in df.iterrows():

        content = f"""
        Perfume Name: {row['Name']}
        Brand: {row['Brand']}
        Top Notes: {row['Top_Notes']}
        Middle Notes: {row['Middle_Notes']}
        Base Notes: {row['Base_Notes']}
        Fragrance Family: {row['Fragrance_Family']}
        Gender Target: {row['Gender_Target']}
        Occasion: {row['Occasion']}
        Season: {row['Season']}
        """.strip()

        document = Document(
        page_content=content,
        metadata={
            "source_type": "perfume_dataset",
            "perfume_name": str(row["Name"]),
            "brand": str(row["Brand"]),
            "top_notes": str(row["Top_Notes"]),
            "middle_notes": str(row["Middle_Notes"]),
            "base_notes": str(row["Base_Notes"]),
            "fragrance_family": str(row["Fragrance_Family"]),
            "occasion": str(row["Occasion"]),
            "season": str(row["Season"]),
            "gender_target": str(row["Gender_Target"]),
            "row_id": index,
        },
)

        documents.append(document)

    return documents


def build_vector_store():
    """Create and persist the Chroma vector database."""

    documents = load_perfume_documents()

    print(f"Loaded {len(documents)} perfume documents.")

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-mpnet-base-v2"
    )

    Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=str(CHROMA_PATH),
        collection_name="perfumes",
    )

    print(f"Vector database created at: {CHROMA_PATH}")


if __name__ == "__main__":
    build_vector_store()