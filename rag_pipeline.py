# rag_pipeline.py
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFacePipeline
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from transformers import pipeline as hf_pipeline

# ── Step 1: Load the log file ──
def load_documents():
    loader = TextLoader("data/logs.txt")
    documents = loader.load()
    print(f"Loaded {len(documents)} document")
    return documents

# ── Step 2: Split into chunks ──
def chunk_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50
    )
    chunks = splitter.split_documents(documents)
    print(f"Created {len(chunks)} chunks")
    return chunks

# ── Step 3: Create vector store ──
def create_vectorstore(chunks):
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'}
    )
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory="./chroma_db"
    )
    print(f"Vector store created with {vectorstore._collection.count()} chunks")
    return vectorstore

# ── Step 4: Load LLM ──
def load_llm():
    print("Loading LLM... (first time takes a few minutes)")
    hf_pipe = hf_pipeline(
        "text-generation",
        model="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        max_new_tokens=300,
        do_sample=False,
        temperature=None,
        top_p=None,
    )
    llm = HuggingFacePipeline(pipeline=hf_pipe)
    print("LLM loaded!")
    return llm

# ── Step 5: Build RAG chain ──
def build_rag_chain(vectorstore, llm):
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3}
    )

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    def extract_answer(text):
        """Extract only the answer part after 'Answer:'"""
        if "Answer:" in text:
            answer = text.split("Answer:")[-1].strip()
            lines = answer.split("\n")
            seen = set()
            unique_lines = []
            for line in lines:
                if line.strip() not in seen:
                    seen.add(line.strip())
                    unique_lines.append(line)
            return "\n".join(unique_lines).strip()
        return text.strip()

    prompt = ChatPromptTemplate.from_template("""
You are a personal productivity coach analyzing someone's daily habits.
Use the log data below to answer the question.
Give specific observations and actionable suggestions based on the data.
If the data doesn't contain enough information, say so honestly.

Log Data:
{context}

Question: {question}

Answer:""")

    from langchain_core.runnables import RunnableLambda

    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
        | RunnableLambda(extract_answer)
    )

    return rag_chain
# ── Step 6: Full pipeline ──
def initialize_pipeline():
    documents = load_documents()
    chunks = chunk_documents(documents)
    vectorstore = create_vectorstore(chunks)
    llm = load_llm()
    rag_chain = build_rag_chain(vectorstore, llm)
    return rag_chain
# ── Rebuild vectorstore with fresh data ──
def rebuild_vectorstore():
    documents = load_documents()
    chunks = chunk_documents(documents)
    vectorstore = create_vectorstore(chunks)
    return vectorstore