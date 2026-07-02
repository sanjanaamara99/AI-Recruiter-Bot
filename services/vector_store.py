import logging
from typing import List, Dict, Any, Optional
import chromadb
from sentence_transformers import SentenceTransformer
from config import Config
import json

logger = logging.getLogger(__name__)


class VectorStore:
    """Service for managing interview context using ChromaDB."""
    
    def __init__(self):
        """Initialize ChromaDB and embedding model."""
        try:
            # Initialize ChromaDB client (new API)
            self.client = chromadb.PersistentClient(path=Config.CHROMA_DB_PATH)
            
            # Initialize embedding model
            logger.info("Loading sentence transformer model...")
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            logger.info("Vector store initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing vector store: {str(e)}")
            raise
    
    def get_or_create_collection(self, session_id: int) -> chromadb.Collection:
        """
        Get or create a collection for an interview session.
        
        Args:
            session_id: Interview session ID
            
        Returns:
            ChromaDB collection
        """
        try:
            collection_name = f"interview_session_{session_id}"
            collection = self.client.get_or_create_collection(name=collection_name)
            return collection
        except Exception as e:
            logger.error(f"Error getting/creating collection: {str(e)}")
            raise
    
    def add_resume_context(self, session_id: int, resume_text: str, resume_analysis: Dict[str, Any]):
        """
        Add resume context to vector store.
        
        Args:
            session_id: Interview session ID
            resume_text: Raw resume text
            resume_analysis: Structured resume analysis
        """
        try:
            collection = self.get_or_create_collection(session_id)
            
            # Add resume text
            collection.add(
                documents=[resume_text],
                metadatas=[{
                    "type": "resume",
                    "session_id": str(session_id),
                    "analysis": json.dumps(resume_analysis)
                }],
                ids=[f"resume_{session_id}"]
            )
            
            logger.info(f"Added resume context for session {session_id}")
        except Exception as e:
            logger.error(f"Error adding resume context: {str(e)}")
            raise
    
    def add_question(self, session_id: int, question_id: int, question_text: str, question_type: str):
        """
        Add question to vector store.
        
        Args:
            session_id: Interview session ID
            question_id: Question ID
            question_text: Question text
            question_type: Type of question
        """
        try:
            collection = self.get_or_create_collection(session_id)
            
            collection.add(
                documents=[question_text],
                metadatas=[{
                    "type": "question",
                    "session_id": str(session_id),
                    "question_id": str(question_id),
                    "question_type": question_type
                }],
                ids=[f"question_{session_id}_{question_id}"]
            )
            
            logger.info(f"Added question {question_id} for session {session_id}")
        except Exception as e:
            logger.error(f"Error adding question: {str(e)}")
            raise
    
    def add_answer(self, session_id: int, question_id: int, answer_text: str, evaluation: Dict[str, Any]):
        """
        Add answer to vector store.
        
        Args:
            session_id: Interview session ID
            question_id: Question ID
            answer_text: Answer text
            evaluation: Answer evaluation
        """
        try:
            collection = self.get_or_create_collection(session_id)
            
            collection.add(
                documents=[answer_text],
                metadatas=[{
                    "type": "answer",
                    "session_id": str(session_id),
                    "question_id": str(question_id),
                    "evaluation": json.dumps(evaluation)
                }],
                ids=[f"answer_{session_id}_{question_id}"]
            )
            
            logger.info(f"Added answer for question {question_id} in session {session_id}")
        except Exception as e:
            logger.error(f"Error adding answer: {str(e)}")
            raise
    
    def search_similar_questions(self, session_id: int, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar questions in the session.
        
        Args:
            session_id: Interview session ID
            query: Query text
            n_results: Number of results to return
            
        Returns:
            List of similar questions
        """
        try:
            collection = self.get_or_create_collection(session_id)
            
            results = collection.query(
                query_texts=[query],
                n_results=n_results,
                where={"type": "question"}
            )
            
            similar_questions = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    similar_questions.append({
                        'text': doc,
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i] if 'distances' in results else None
                    })
            
            return similar_questions
        except Exception as e:
            logger.error(f"Error searching similar questions: {str(e)}")
            return []
    
    def get_discussed_topics(self, session_id: int) -> List[str]:
        """
        Get list of topics discussed in the interview.
        
        Args:
            session_id: Interview session ID
            
        Returns:
            List of discussed topics
        """
        try:
            collection = self.get_or_create_collection(session_id)
            
            # Get all questions and answers
            results = collection.get(
                where={"session_id": str(session_id)}
            )
            
            topics = []
            if results['metadatas']:
                for metadata in results['metadatas']:
                    if metadata.get('type') == 'question':
                        topics.append(metadata.get('question_type', 'unknown'))
            
            return list(set(topics))
        except Exception as e:
            logger.error(f"Error getting discussed topics: {str(e)}")
            return []
    
    def check_duplicate_question(self, session_id: int, question_text: str, threshold: float = 0.8) -> bool:
        """
        Check if a similar question has already been asked.
        
        Args:
            session_id: Interview session ID
            question_text: Question text to check
            threshold: Similarity threshold (0-1)
            
        Returns:
            True if duplicate found, False otherwise
        """
        try:
            similar_questions = self.search_similar_questions(session_id, question_text, n_results=1)
            
            if similar_questions and similar_questions[0].get('distance'):
                # Lower distance means more similar
                similarity = 1 - similar_questions[0]['distance']
                if similarity >= threshold:
                    logger.warning(f"Duplicate question detected (similarity: {similarity:.2f})")
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Error checking duplicate question: {str(e)}")
            return False
    
    def delete_session_data(self, session_id: int):
        """
        Delete all data for a session.
        
        Args:
            session_id: Interview session ID
        """
        try:
            collection_name = f"interview_session_{session_id}"
            self.client.delete_collection(name=collection_name)
            logger.info(f"Deleted vector store data for session {session_id}")
        except Exception as e:
            logger.error(f"Error deleting session data: {str(e)}")
            raise


# Global vector store instance
vector_store = VectorStore()
