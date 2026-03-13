# test.py
from rag_pipeline import initialize_pipeline

print("Initializing RAG pipeline...")
rag_chain = initialize_pipeline()

print("\nTesting chatbot...")
print("=" * 50)

questions = [
    "What was my best day and why?",
    "How does my sleep affect my productivity?",
    "Which apps am I spending too much time on?",
    "What should I do to improve my productivity?",
]

for question in questions:
    print(f"\nQ: {question}")
    answer = rag_chain.invoke(question)
    print(f"A: {answer}")
    print("-" * 50)