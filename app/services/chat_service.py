import os
import json
import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer
from typing import List, Dict

# Assuming Groq client is imported from a central utils/llm_parser if available,
# but we will instantiate it here based on groq environment variable.
from groq import Groq

class ChatService:
    def __init__(self):
        # Initialize Groq client
        api_key = os.environ.get("GROQ_API_KEY", "")
        self.llm_client = Groq(api_key=api_key)
        self.model = "openai/gpt-oss-120b" # Match existing config
        
        # Initialize ChromaDB client
        self.chroma_path = os.path.join("app", "data", "chroma_db")
        # Ensure path exists, otherwise RAG will fail gracefully
        if os.path.exists(self.chroma_path):
            self.chroma_client = chromadb.PersistentClient(path=self.chroma_path)
            self.embedding_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
            try:
                self.collection = self.chroma_client.get_collection(
                    name="internmatch_knowledge",
                    embedding_function=self.embedding_ef
                )
            except Exception:
                self.collection = None
        else:
            self.chroma_client = None
            self.collection = None

    def retrieve_context(self, query: str, top_k: int = 3) -> str:
        if not self.collection:
            return ""
        
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k
        )
        
        if not results or not results["documents"] or not results["documents"][0]:
            return ""
            
        chunks = results["documents"][0]
        # Combine the retrieved chunks into a single context string
        context = "\n\n---\n\n".join(chunks)
        return context

    def generate_response(self, user_message: str, chat_history: List[Dict[str, str]]) -> str:
        # Retrieve context from RAG
        # Prepend the last user message to the current query to resolve pronouns for vector search
        search_query = user_message
        last_user_msgs = [msg["message"] for msg in chat_history if msg["role"] == "user"]
        if last_user_msgs:
            search_query = f"{last_user_msgs[-1]} {user_message}"
            
        context = self.retrieve_context(search_query)
        
        # Construct System Prompt
        system_prompt = (
            "You are the AI Product Assistant strictly for InternMatch. "
            "Your ONLY goal is to answer questions about the InternMatch product, its features, workflows, UI, resume parsing, internship matching, and other documented functionality.\n\n"
            "CRITICAL SCOPE RULE: You MUST NOT answer general-knowledge questions (e.g., 'What is the capital of France?', 'Who is Elon Musk?', 'Write a Python program', etc.). "
            "If the user's question, when interpreted in the context of the conversation history, is unrelated to InternMatch, you MUST politely refuse to answer and state that you can only help with InternMatch and its documented features. Do NOT reject contextual follow-ups like 'How do I use it?' if 'it' refers to an InternMatch feature discussed previously.\n\n"
            "RAG GROUNDING RULE: You MUST base your answers ONLY on the provided Product Knowledge Context below. Do NOT use your pretrained knowledge to state facts. "
            "If the retrieved context does not contain enough information to answer an InternMatch-related question, return a safe 'I don't have that information in my InternMatch knowledge base' response.\n\n"
            "PRODUCT KNOWLEDGE CONTEXT:\n"
            f"{context}\n\n"
            "INSTRUCTIONS:\n"
            "1. Answer clearly, concisely, and professionally.\n"
            "2. Use the conversation history to understand context for pronouns like 'it', 'them', or follow-up questions.\n"
        )
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history
        for msg in chat_history:
            messages.append({"role": msg["role"], "content": msg["message"]})
            
        # Add the current user message
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = self.llm_client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.2,
                max_tokens=1000,
            )
            return response.choices[0].message.content
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise e

# Singleton instance
chat_service = ChatService()
