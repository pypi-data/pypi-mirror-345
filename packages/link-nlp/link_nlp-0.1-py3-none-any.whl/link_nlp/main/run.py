"""
Main entry point for demonstrating the LINK system functionality.
This script provides examples of using the various components of the system.
"""

import os
import sys
import argparse

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.milvusDb import MilvusConnectionManager, ContextCollection, ArticoliCollection, CorrettivoCollection
from retrieval.ContextualRetrieval import test_question_answer_codice_appalti, test_question_answer_correttivo


def main():
    """
    Main function to demonstrate system functionality.
    """
    parser = argparse.ArgumentParser(description="LINK: Legal Information Knowledge with NLP")
    parser.add_argument("--test", choices=["appalti", "correttivo"], help="Test to run")
    parser.add_argument("--test-file", help="Test file path")
    
    args = parser.parse_args()
    
    # Initialize Milvus connection
    MilvusConnectionManager.get_connection(first_attempt=True)
    
    if args.test == "appalti":
        test_file = args.test_file or "../data/codice_appalti_qa.jsonl"
        print(f"Running test on Codice Appalti with file: {test_file}")
        test_question_answer_codice_appalti(test_file)
    
    elif args.test == "correttivo":
        test_file = args.test_file or "../data/generated_output_mc.jsonl"
        print(f"Running test on Correttivo with file: {test_file}")
        test_question_answer_correttivo(test_file)
    
    else:
        print("No test specified. Available options:")
        print("  --test appalti     Test question answering on Codice Appalti")
        print("  --test correttivo  Test question answering on Correttivo")
    
    # Close connection
    MilvusConnectionManager.close_connection()


if __name__ == "__main__":
    main()