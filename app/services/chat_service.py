import os
import json
import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional

from groq import Groq


class ChatService:
    def __init__(self):
        # Initialize Groq client
        api_key = os.environ.get("GROQ_API_KEY", "")
        self.llm_client = Groq(api_key=api_key)
        self.model = "openai/gpt-oss-120b"  # Match existing config
        
        # Initialize ChromaDB client for product knowledge RAG
        self.chroma_path = os.path.join("app", "data", "chroma_db")
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
        """Retrieve product knowledge context from ChromaDB (existing RAG)."""
        if not self.collection:
            return ""
        
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k
        )
        
        if not results or not results["documents"] or not results["documents"][0]:
            return ""
            
        chunks = results["documents"][0]
        context = "\n\n---\n\n".join(chunks)
        return context

    def _detect_intent(self, user_message: str, chat_history: List[Dict[str, str]]) -> str:
        """Detect the intent of the user's message to determine what context to include.
        
        Returns one of:
          'product'      - InternMatch/product questions (use RAG only)
          'resume'       - Resume analysis questions (need active resume)
          'internship'   - Internship-specific questions (need resume + internship)
          'preparation'  - Mock interview / preparation mode (need resume + internship)
        """
        msg_lower = user_message.lower().strip()
        
        # Check recent conversation for ongoing preparation/interview context
        recent_assistant_msgs = [m["message"] for m in chat_history[-6:] if m["role"] == "assistant"]
        recent_context = " ".join(recent_assistant_msgs).lower()
        
        is_in_interview = any(kw in recent_context for kw in [
            "let me ask", "next question", "here's your", "let's begin",
            "your answer", "mock interview", "let's start the interview",
            "question 1", "question 2", "question 3",
            "here is your next", "let me evaluate", "good answer",
            "could be improved", "here's a follow-up", "preparation",
            "let's move on to", "score:", "rating:",
        ])
        
        # Preparation / mock interview triggers
        preparation_keywords = [
            "prepare me", "mock interview", "take my interview", 
            "interview me", "ask me questions", "practice interview",
            "start interview", "begin interview", "quiz me",
            "test me", "interview preparation", "prepare for",
            "ask me python", "ask me java", "ask me sql",
            "ask me react", "ask me coding", "ask me technical",
            "behavioral questions", "hr questions", "grill me",
            "evaluate me", "assess me",
        ]
        if any(kw in msg_lower for kw in preparation_keywords):
            return "preparation"
        
        # If we're in an active interview/preparation flow and user gives a short answer,
        # treat it as a continuation of preparation
        if is_in_interview and len(msg_lower.split()) <= 60:
            # Short responses during an interview are likely answers
            if not any(kw in msg_lower for kw in [
                "what is internmatch", "how do i upload", "what features",
                "what is skill gap", "how does matching work",
            ]):
                return "preparation"
        
        # Internship-specific triggers
        internship_keywords = [
            "which internship", "match my profile", "internships for me",
            "why don't i match", "why doesn't this", "match this internship",
            "suitable for me", "compare my resume", "what skills are required",
            "missing for this internship", "internship require",
            "am i qualified", "this internship", "that internship",
            "find internships", "find me internships", "recommend internship",
            "internship match", "match score",
        ]
        if any(kw in msg_lower for kw in internship_keywords):
            return "internship"
        
        # Resume-specific triggers  
        resume_keywords = [
            "my resume", "analyze my resume", "my skills", "my profile",
            "what skills do i", "skills am i missing", "areas should i improve",
            "my experience", "my education", "my projects",
            "resume analysis", "resume score", "my strengths",
            "my weaknesses", "improve my resume", "rate my resume",
            "what do i know", "what can i do", "my qualifications",
        ]
        if any(kw in msg_lower for kw in resume_keywords):
            return "resume"
        
        # Default: product knowledge (existing RAG behavior)
        return "product"

    def _format_resume_context(self, resume_data: Dict[str, Any]) -> str:
        """Format parsed resume data into a readable context block."""
        sections = []
        
        if resume_data.get("name") or resume_data.get("full_name"):
            sections.append(f"Name: {resume_data.get('name') or resume_data.get('full_name')}")
        
        skills = resume_data.get("skills", [])
        if isinstance(skills, list) and skills:
            sections.append(f"Skills: {', '.join(skills)}")
        
        technical = resume_data.get("technical_skills", [])
        if isinstance(technical, list) and technical:
            sections.append(f"Technical Skills: {', '.join(technical)}")
        
        education = resume_data.get("education", [])
        if isinstance(education, list) and education:
            sections.append(f"Education: {'; '.join(str(e) for e in education)}")
        
        experience = resume_data.get("experience", []) or resume_data.get("work_experience", [])
        if isinstance(experience, list) and experience:
            sections.append(f"Experience: {'; '.join(str(e) for e in experience)}")
        
        projects = resume_data.get("projects", [])
        if isinstance(projects, list) and projects:
            sections.append(f"Projects: {'; '.join(str(p) for p in projects)}")
        
        certifications = resume_data.get("certifications", [])
        if isinstance(certifications, list) and certifications:
            sections.append(f"Certifications: {', '.join(str(c) for c in certifications)}")
        
        achievements = resume_data.get("achievements", [])
        if isinstance(achievements, list) and achievements:
            sections.append(f"Achievements: {'; '.join(str(a) for a in achievements)}")
        
        summary = resume_data.get("professional_summary") or resume_data.get("summary", "")
        if summary:
            sections.append(f"Professional Summary: {summary}")
        
        score = resume_data.get("resume_score")
        if score is not None:
            sections.append(f"Resume Score: {score}")
        
        strengths = resume_data.get("strengths", [])
        if isinstance(strengths, list) and strengths:
            sections.append(f"Strengths: {'; '.join(str(s) for s in strengths)}")
        
        weaknesses = resume_data.get("weaknesses", [])
        if isinstance(weaknesses, list) and weaknesses:
            sections.append(f"Weaknesses: {'; '.join(str(w) for w in weaknesses)}")
        
        return "\n".join(sections) if sections else ""

    def _format_internship_context(self, internship: Dict[str, Any]) -> str:
        """Format internship data into a readable context block."""
        sections = []
        if internship.get("title"):
            sections.append(f"Title: {internship['title']}")
        if internship.get("company"):
            sections.append(f"Company: {internship['company']}")
        if internship.get("domain"):
            sections.append(f"Domain: {internship['domain']}")
        if internship.get("description"):
            sections.append(f"Description: {internship['description']}")
        
        req_skills = internship.get("required_skills", [])
        if req_skills:
            sections.append(f"Required Skills: {', '.join(req_skills)}")
        
        pref_skills = internship.get("preferred_skills", [])
        if pref_skills:
            sections.append(f"Preferred Skills: {', '.join(pref_skills)}")
        
        if internship.get("education_requirements"):
            sections.append(f"Education Requirements: {internship['education_requirements']}")
        if internship.get("experience_requirements"):
            sections.append(f"Experience Requirements: {internship['experience_requirements']}")
        
        responsibilities = internship.get("responsibilities", [])
        if responsibilities:
            sections.append(f"Responsibilities: {'; '.join(responsibilities)}")
        
        if internship.get("location"):
            sections.append(f"Location: {internship['location']}")
        if internship.get("work_mode"):
            sections.append(f"Work Mode: {internship['work_mode']}")
        if internship.get("duration"):
            sections.append(f"Duration: {internship['duration']}")
        if internship.get("stipend"):
            sections.append(f"Stipend: {internship['stipend']}")
        
        return "\n".join(sections) if sections else ""

    def _format_matching_context(self, resume_data: Dict[str, Any], internship: Dict[str, Any]) -> str:
        """Compute and format skill matching data between resume and internship."""
        resume_skills_raw = resume_data.get("skills", [])
        if isinstance(resume_skills_raw, str):
            resume_skills_raw = [s.strip() for s in resume_skills_raw.split(",")]
        resume_skills_lower = {s.lower() for s in resume_skills_raw if s}
        
        required_skills = internship.get("required_skills", [])
        matched = [s for s in required_skills if s.lower() in resume_skills_lower]
        missing = [s for s in required_skills if s.lower() not in resume_skills_lower]
        
        pct = round((len(matched) / len(required_skills) * 100), 1) if required_skills else 100.0
        
        lines = [
            f"Skill Match: {pct}%",
            f"Matched Skills: {', '.join(matched) if matched else 'None'}",
            f"Missing Skills: {', '.join(missing) if missing else 'None (all required skills matched!)'}",
        ]
        return "\n".join(lines)

    def generate_response(
        self,
        user_message: str,
        chat_history: List[Dict[str, str]],
        resume_data: Optional[Dict[str, Any]] = None,
        internship_data: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Generate a context-aware AI response.
        
        This method extends the original generate_response to support:
        1. Product Q&A (existing RAG behavior, unchanged)
        2. Resume-based career assistance
        3. Internship matching assistance 
        4. Interactive preparation / mock interview mode
        """
        # Detect what kind of question this is
        intent = self._detect_intent(user_message, chat_history)
        
        # Build the search query for RAG (always include for product questions)
        search_query = user_message
        last_user_msgs = [msg["message"] for msg in chat_history if msg["role"] == "user"]
        if last_user_msgs:
            search_query = f"{last_user_msgs[-1]} {user_message}"
        
        # --- Build system prompt based on intent ---
        
        if intent == "product":
            # Original RAG-based product assistant behavior
            context = self.retrieve_context(search_query)
            system_prompt = (
                "You are the AI Career Assistant for InternMatch. "
                "You can answer questions about the InternMatch product, its features, workflows, UI, resume parsing, internship matching, and other documented functionality.\n\n"
                "RAG GROUNDING RULE: For product/feature questions, base your answers on the provided Product Knowledge Context below. "
                "If the retrieved context does not contain enough information to answer an InternMatch-related question, return a safe 'I don't have that information in my InternMatch knowledge base' response.\n\n"
                "You are also capable of helping with resume analysis, career guidance, internship matching, and interview preparation when the user asks. "
                "If the user's question is completely unrelated to InternMatch, careers, internships, resumes, or professional development, politely redirect them.\n\n"
                "PRODUCT KNOWLEDGE CONTEXT:\n"
                f"{context}\n\n"
                "INSTRUCTIONS:\n"
                "1. Answer clearly, concisely, and professionally.\n"
                "2. Use the conversation history to understand context for pronouns like 'it', 'them', or follow-up questions.\n"
                "3. If the user asks about their resume, skills, or internship matching, let them know you can help with that too.\n"
            )
        
        elif intent == "resume":
            context = self.retrieve_context(search_query)
            if resume_data:
                resume_context = self._format_resume_context(resume_data)
                system_prompt = (
                    "You are the AI Career Assistant for InternMatch. "
                    "The user is asking about their resume/profile. You have access to their active resume data.\n\n"
                    "USER'S ACTIVE RESUME:\n"
                    f"{resume_context}\n\n"
                    "PRODUCT KNOWLEDGE CONTEXT:\n"
                    f"{context}\n\n"
                    "INSTRUCTIONS:\n"
                    "1. Analyze and discuss the user's resume based ONLY on the actual data provided above.\n"
                    "2. Do NOT invent or fabricate any skills, experience, or information not in the resume.\n"
                    "3. Provide actionable advice for improvement when asked.\n"
                    "4. Be encouraging but honest about gaps.\n"
                    "5. Use the conversation history for context.\n"
                )
            else:
                system_prompt = (
                    "You are the AI Career Assistant for InternMatch. "
                    "The user is asking about their resume/profile, but they don't have an active resume uploaded.\n\n"
                    "PRODUCT KNOWLEDGE CONTEXT:\n"
                    f"{context}\n\n"
                    "INSTRUCTIONS:\n"
                    "1. Politely inform the user that you need their resume to provide personalized analysis.\n"
                    "2. Guide them to upload a resume through the 'My Resumes' section in the sidebar, then set it as active.\n"
                    "3. Explain that once they upload and activate a resume, you can analyze their skills, suggest improvements, match internships, and prepare them for interviews.\n"
                    "4. You can still answer general product questions about InternMatch.\n"
                )
        
        elif intent == "internship":
            context = self.retrieve_context(search_query)
            parts = [
                "You are the AI Career Assistant for InternMatch. "
                "The user is asking about internship matching.\n\n"
            ]
            
            if resume_data:
                resume_context = self._format_resume_context(resume_data)
                parts.append(f"USER'S ACTIVE RESUME:\n{resume_context}\n\n")
            else:
                parts.append(
                    "NOTE: The user does not have an active resume. Suggest they upload and activate one for personalized matching.\n\n"
                )
            
            if internship_data:
                internship_context = self._format_internship_context(internship_data)
                parts.append(f"CURRENT INTERNSHIP CONTEXT:\n{internship_context}\n\n")
                
                if resume_data:
                    matching_context = self._format_matching_context(resume_data, internship_data)
                    parts.append(f"SKILL MATCHING ANALYSIS:\n{matching_context}\n\n")
            
            parts.append(f"PRODUCT KNOWLEDGE CONTEXT:\n{context}\n\n")
            parts.append(
                "INSTRUCTIONS:\n"
                "1. Use the actual resume and internship data to answer. Do NOT fabricate information.\n"
                "2. When discussing matches, reference specific matched and missing skills.\n"
                "3. Provide actionable guidance on how to improve match scores.\n"
                "4. If no internship is provided but the user refers to one, ask them to select an internship in the Internships page or specify the internship name.\n"
                "5. Use conversation history to maintain context.\n"
            )
            system_prompt = "".join(parts)
        
        elif intent == "preparation":
            parts = [
                "You are the AI Career Assistant for InternMatch, acting as an interactive interviewer and mentor. "
                "You are conducting personalized interview preparation / mock interview for the user.\n\n"
            ]
            
            if resume_data:
                resume_context = self._format_resume_context(resume_data)
                parts.append(f"USER'S ACTIVE RESUME:\n{resume_context}\n\n")
            else:
                parts.append(
                    "NOTE: The user does not have an active resume loaded. Ask them to upload and activate one for fully personalized preparation. "
                    "You can still conduct general interview preparation.\n\n"
                )
            
            if internship_data:
                internship_context = self._format_internship_context(internship_data)
                parts.append(f"TARGET INTERNSHIP:\n{internship_context}\n\n")
                
                if resume_data:
                    matching_context = self._format_matching_context(resume_data, internship_data)
                    parts.append(f"SKILL MATCHING ANALYSIS:\n{matching_context}\n\n")
            else:
                parts.append(
                    "NOTE: No specific internship is currently selected by the user. "
                    "You must ask the user to select an internship from their matches or provide the role/company details they want to prepare for.\n\n"
                )
            
            parts.append(
                "PREPARATION BEHAVIOR RULES:\n"
                "1. ASK ONE QUESTION AT A TIME. Never dump multiple questions at once.\n"
                "2. Wait for the user's answer before proceeding.\n"
                "3. After the user answers, EVALUATE their response:\n"
                "   - What was good about their answer\n"
                "   - What could be improved\n"
                "   - Provide a better/example answer when useful\n"
                "   - Give a brief score or rating (e.g., 7/10)\n"
                "4. Then ask the NEXT relevant question, adapting based on their performance.\n"
                "5. Support these question types based on context:\n"
                "   - Technical questions (based on required skills and user's skills)\n"
                "   - Project-based questions (based on user's projects from resume)\n"
                "   - Behavioral/HR questions\n"
                "   - Situational questions\n"
                "   - Skill-specific questions (especially for missing skills)\n"
                "6. Start with easier questions and progressively increase difficulty.\n"
                "7. Focus MORE on missing/weak skills to help the user improve.\n"
                "8. If the user struggles with a topic, provide learning suggestions before moving on.\n"
                "9. Be conversational, supportive, and professional — like a real interviewer/mentor.\n"
                "10. When starting a new preparation session, briefly outline what you'll cover based on the context, then begin with the first question.\n"
                "11. If the user asks to focus on a specific topic (e.g., 'ask me Python questions'), focus on that.\n"
                "12. Track weak areas through the conversation and suggest revision topics.\n"
                "13. Do NOT fabricate information about the user. Use only what's in the resume.\n"
                "14. VERY IMPORTANT: Do NOT ask the user to provide details about the company, role, or job description if TARGET INTERNSHIP is provided above. Use the provided context directly!\n"
            )
            system_prompt = "".join(parts)
        
        else:
            # Fallback — same as product
            context = self.retrieve_context(search_query)
            system_prompt = (
                "You are the AI Career Assistant for InternMatch. Answer the user's question helpfully.\n\n"
                f"PRODUCT KNOWLEDGE CONTEXT:\n{context}\n\n"
            )
        
        # Build messages array for LLM
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history
        for msg in chat_history:
            messages.append({"role": msg["role"], "content": msg["message"]})
            
        # Add the current user message
        messages.append({"role": "user", "content": user_message})
        
        # Adjust parameters based on intent
        temperature = 0.3 if intent in ("preparation",) else 0.2
        max_tokens = 1500 if intent == "preparation" else 1000
        
        try:
            response = self.llm_client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise e


# Singleton instance
chat_service = ChatService()
