"""
Streamlit Frontend for Autonomous AI Interviewer - Conversational Chat Style
"""

import streamlit as st
import requests
import json
from datetime import datetime
import time
from gtts import gTTS
import os
import base64
from io import BytesIO
from st_audiorec import st_audiorec
import random

# Configuration
API_BASE_URL = "http://localhost:5000"

# Page configuration
st.set_page_config(
    page_title="AI Interviewer",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'candidate_id' not in st.session_state:
    st.session_state.candidate_id = None
if 'session_id' not in st.session_state:
    st.session_state.session_id = None
if 'current_question_id' not in st.session_state:
    st.session_state.current_question_id = None
if 'interview_started' not in st.session_state:
    st.session_state.interview_started = False
if 'candidate_name' not in st.session_state:
    st.session_state.candidate_name = None


def check_api_health():
    """Check if API is running."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def upload_resume(file):
    """Upload resume to API."""
    try:
        files = {'file': file}
        response = requests.post(f"{API_BASE_URL}/api/upload-resume", files=files)
        return response.json()
    except Exception as e:
        return {'success': False, 'error': str(e)}


def start_interview(candidate_id):
    """Start interview session."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/start-interview",
            json={'candidate_id': candidate_id}
        )
        return response.json()
    except Exception as e:
        return {'success': False, 'error': str(e)}


def get_next_question(session_id):
    """Get next interview question."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/next-question",
            params={'session_id': session_id}
        )
        return response.json()
    except Exception as e:
        return {'success': False, 'error': str(e)}


def submit_answer(question_id, answer_text):
    """Submit answer for evaluation."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/evaluate-answer",
            json={'question_id': question_id, 'transcript': answer_text}
        )
        return response.json()
    except Exception as e:
        return {'success': False, 'error': str(e)}


def get_interview_status(session_id):
    """Get interview status."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/interview-status/{session_id}")
        return response.json()
    except Exception as e:
        return {'success': False, 'error': str(e)}


def get_report(session_id):
    """Get interview report."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/report/{session_id}")
        return response.json()
    except Exception as e:
        return {'success': False, 'error': str(e)}


def text_to_speech(text):
    """Convert text to speech and return audio bytes."""
    try:
        tts = gTTS(text=text, lang='en', slow=False)
        audio_fp = BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        return audio_fp.read()
    except Exception as e:
        st.error(f"Audio generation error: {e}")
        return None


def autoplay_audio(audio_bytes):
    """Autoplay audio in Streamlit."""
    if audio_bytes:
        b64 = base64.b64encode(audio_bytes).decode()
        audio_html = f"""
        <audio autoplay>
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        """
        st.markdown(audio_html, unsafe_allow_html=True)


def transcribe_audio(audio_bytes):
    """Send audio to backend for transcription."""
    try:
        files = {'audio': ('audio.wav', audio_bytes, 'audio/wav')}
        response = requests.post(f"{API_BASE_URL}/api/transcribe", files=files)
        return response.json()
    except Exception as e:
        return {'success': False, 'error': str(e)}


# Main app
def main():
    # Header
    st.markdown('<div class="main-header">🤖 AI Interviewer</div>', unsafe_allow_html=True)
    
    # Check API health
    if not check_api_health():
        st.error("⚠️ API is not running! Please start the Flask backend first: `python app.py`")
        st.stop()
    
    # Sidebar
    with st.sidebar:
        st.title("📋 Navigation")
        page = st.radio(
            "Select Page",
            ["🏠 Home", "📄 Upload Resume", "🎤 Interview", "📊 Results"],
            label_visibility="collapsed"
        )
        
        st.divider()
        
        # Session info
        if st.session_state.candidate_name:
            st.success(f"**Candidate:** {st.session_state.candidate_name}")
        
        if st.session_state.session_id:
            st.info(f"**Session ID:** {st.session_state.session_id}")
            
            # Get status
            status_data = get_interview_status(st.session_state.session_id)
            if status_data.get('success'):
                progress = status_data['data']['progress']
                st.metric("Questions Answered", 
                         f"{progress['answered_questions']}/{progress['total_questions']}")
                st.progress(progress['completion_percentage'] / 100)
        
        st.divider()
        
        # Reset button
        if st.button("🔄 Start New Interview", use_container_width=True):
            st.session_state.candidate_id = None
            st.session_state.session_id = None
            st.session_state.current_question_id = None
            st.session_state.interview_started = False
            st.session_state.candidate_name = None
            if 'chat_messages' in st.session_state:
                del st.session_state.chat_messages
            if 'current_question' in st.session_state:
                del st.session_state.current_question
            if 'waiting_for_answer' in st.session_state:
                del st.session_state.waiting_for_answer
            st.rerun()
    
    # Page routing
    if page == "🏠 Home":
        show_home_page()
    elif page == "📄 Upload Resume":
        show_upload_page()
    elif page == "🎤 Interview":
        show_interview_page()
    elif page == "📊 Results":
        show_results_page()


def show_home_page():
    """Home page."""
    st.title("Welcome to AI Interviewer! 👋")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 📄 Step 1")
        st.write("Upload your resume")
        st.info("Supported formats: PDF, DOCX")
    
    with col2:
        st.markdown("### 🎤 Step 2")
        st.write("Answer interview questions")
        st.info("Text or voice answers with AI evaluation")
    
    with col3:
        st.markdown("### 📊 Step 3")
        st.write("Get your results")
        st.info("Comprehensive report with scores")
    
    st.divider()
    
    st.markdown("### ✨ Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        - 🤖 **AI-Powered Analysis** - Resume parsed with Google Gemini
        - 🎯 **Personalized Questions** - Based on your skills and experience
        - 💬 **Conversational Chat** - Natural ChatGPT-style interview
        - 🔊 **Audio Support** - Questions read aloud, voice answers supported
        """)
    
    with col2:
        st.markdown("""
        - 📊 **Multi-Dimensional Scoring** - Technical, communication, problem-solving
        - 💡 **Intelligent Follow-ups** - Dynamic probing questions
        - 📈 **Real-time Feedback** - Get immediate responses
        - 📑 **Professional Reports** - JSON and PDF formats
        """)
    
    st.divider()
    
    if not st.session_state.candidate_id:
        st.warning("👉 Get started by uploading your resume in the **Upload Resume** page!")
    elif not st.session_state.interview_started:
        st.warning("👉 Your resume is uploaded! Go to the **Interview** page to start!")
    else:
        st.success("✅ Interview in progress! Continue in the **Interview** page.")


def show_upload_page():
    """Resume upload page."""
    st.title("📄 Upload Resume")
    
    if st.session_state.candidate_id:
        st.success(f"✅ Resume already uploaded for: {st.session_state.candidate_name}")
        st.info("You can start the interview from the **Interview** page.")
        return
    
    st.write("Upload your resume to get started. We support PDF and DOCX formats.")
    
    uploaded_file = st.file_uploader(
        "Choose a resume file",
        type=['pdf', 'docx'],
        help="Upload your resume in PDF or DOCX format"
    )
    
    if uploaded_file:
        st.write(f"**File:** {uploaded_file.name}")
        st.write(f"**Size:** {uploaded_file.size / 1024:.2f} KB")
        
        if st.button("🚀 Analyze Resume", type="primary", use_container_width=True):
            with st.spinner("Analyzing resume with AI... This may take a minute."):
                result = upload_resume(uploaded_file)
                
                if result.get('success'):
                    data = result['data']
                    candidate = data['candidate']
                    analysis = data['analysis']
                    skills = data['skills']
                    
                    # Save to session state
                    st.session_state.candidate_id = candidate['id']
                    st.session_state.candidate_name = candidate['name']
                    
                    st.success("✅ Resume analyzed successfully!")
                    
                    # Display results
                    st.divider()
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("### 👤 Candidate Information")
                        st.write(f"**Name:** {candidate['name']}")
                        st.write(f"**Email:** {candidate['email']}")
                        st.write(f"**Experience:** {candidate['experience_years']} years")
                    
                    with col2:
                        st.markdown("### 💼 Skills Detected")
                        st.write(f"**Total Skills:** {len(skills)}")
                        
                        # Group skills by category
                        categories = {}
                        for skill in skills:
                            cat = skill['category']
                            if cat not in categories:
                                categories[cat] = []
                            categories[cat].append(skill['skill_name'])
                        
                        for cat, skill_list in categories.items():
                            with st.expander(f"**{cat}** ({len(skill_list)})"):
                                st.write(", ".join(skill_list))
                    
                    st.divider()
                    
                    st.markdown("### 🎯 Next Step")
                    st.info("Your resume has been analyzed! Go to the **Interview** page to start your interview.")
                    
                else:
                    st.error(f"❌ Error: {result.get('error', 'Unknown error')}")


def show_interview_page():
    """Interview page - Conversational ChatGPT style with audio."""
    st.title("💬 AI Interview Chat")
    
    if not st.session_state.candidate_id:
        st.warning("⚠️ Please upload your resume first!")
        return
    
    # Initialize chat history in session state
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    if 'current_question' not in st.session_state:
        st.session_state.current_question = None
    if 'waiting_for_answer' not in st.session_state:
        st.session_state.waiting_for_answer = False
    if 'last_audio_played' not in st.session_state:
        st.session_state.last_audio_played = None
    if 'audio_enabled' not in st.session_state:
        st.session_state.audio_enabled = True
    
    # Audio toggle at the top
    col1, col2 = st.columns([4, 1])
    with col2:
        st.session_state.audio_enabled = st.toggle("🔊 Audio", value=st.session_state.audio_enabled)
    
    # Start interview if not started
    if not st.session_state.interview_started:
        st.markdown("### 👋 Welcome to Your AI Interview!")
        st.write(f"**Hi {st.session_state.candidate_name}!**")
        st.write("I'm your AI interviewer today. We'll have a natural conversation about your skills and experience.")
        
        st.info("💡 **How this works:**")
        st.markdown("""
        - I'll ask you questions one at a time, just like chatting
        - You can **type** your answer OR **record it** using your voice 🎤
        - Questions will be **read aloud** automatically (you can toggle audio on/off above)
        - You'll get immediate feedback on each answer
        - Just relax and answer naturally - there's no timer!
        """)
        
        if st.button("🚀 Start Interview", type="primary", use_container_width=True):
            with st.spinner("Preparing your personalized interview..."):
                result = start_interview(st.session_state.candidate_id)
                
                if result.get('success'):
                    data = result['data']
                    st.session_state.session_id = data['session']['id']
                    st.session_state.interview_started = True
                    st.session_state.current_question_id = data['first_question']['id']
                    
                    # Add welcome message to chat
                    welcome_msg = f"Hello {st.session_state.candidate_name}! 👋\n\nI'm excited to chat with you today. I've reviewed your resume and prepared some questions for our conversation.\n\nLet's begin!"
                    st.session_state.chat_messages.append({
                        "role": "assistant",
                        "content": welcome_msg,
                        "play_audio": False  # Don't play audio for welcome message
                    })
                    
                    # Add first question
                    first_question = data['first_question']
                    st.session_state.current_question = first_question
                    st.session_state.chat_messages.append({
                        "role": "assistant",
                        "content": f"**Question 1:**\n\n{first_question['question_text']}",
                        "play_audio": True  # Only play audio for the actual question
                    })
                    st.session_state.waiting_for_answer = True
                    st.session_state.last_audio_played = None  # Reset to play new audio
                    
                    st.rerun()
                else:
                    st.error(f"❌ Error: {result.get('error', 'Unknown error')}")
        return
    
    # Display chat interface
    st.markdown("### 💬 Interview Conversation")
    
    # Get progress
    status_data = get_interview_status(st.session_state.session_id)
    if status_data.get('success'):
        progress = status_data['data']['progress']
        st.progress(progress['completion_percentage'] / 100, 
                   text=f"Progress: {progress['answered_questions']}/{progress['total_questions']} questions answered")
    
    st.divider()
    
    # Chat container
    chat_container = st.container(height=400)
    
    with chat_container:
        for idx, message in enumerate(st.session_state.chat_messages):
            if message["role"] == "assistant":
                with st.chat_message("assistant", avatar="🤖"):
                    st.write(message["content"])
                    
                    # Play audio for the last assistant message if enabled and not already played
                    if (st.session_state.audio_enabled and 
                        message.get("play_audio") and 
                        idx == len(st.session_state.chat_messages) - 1 and
                        st.session_state.last_audio_played != idx):
                        
                        audio_bytes = text_to_speech(message["content"])
                        if audio_bytes:
                            autoplay_audio(audio_bytes)
                            st.session_state.last_audio_played = idx
            else:
                with st.chat_message("user", avatar="👤"):
                    st.write(message["content"])
    
    # Check if interview is complete
    if st.session_state.waiting_for_answer == False:
        result = get_next_question(st.session_state.session_id)
        
        if result.get('success') and not result['data']['has_more_questions']:
            if st.session_state.waiting_for_answer != None:  # Only show once
                st.success("🎉 **Interview Complete!**")
                st.balloons()
                
                completion_msg = "Excellent! We've completed all the questions. Thank you for your time and thoughtful answers. You can now view your comprehensive results in the Results page!"
                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": completion_msg,
                    "play_audio": False  # Don't play audio for completion message
                })
                
                st.session_state.waiting_for_answer = None  # Mark as complete
                st.rerun()
            
            st.info("👉 Go to the **Results** page to view your comprehensive report and hiring recommendation.")
            return
        
        # Get next question if interview not complete
        if result.get('success') and result['data']['has_more_questions']:
            next_question = result['data']['question']
            st.session_state.current_question = next_question
            st.session_state.current_question_id = next_question['id']
            
            # Get question number
            answered = progress['answered_questions']
            question_num = answered + 1
            
            # Add conversational transition
            transitions = [
                "Great answer! Let me ask you about something else...",
                "Thanks for sharing that. Moving on...",
                "Interesting perspective! Now I'd like to know...",
                "Got it! Here's my next question...",
                "Perfect! Let's continue...",
                "That makes sense. Let me ask you this...",
                "Wonderful! Now, let's talk about...",
            ]
            transition = random.choice(transitions)
            
            # Separate transition and question for selective audio
            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": transition,
                "play_audio": False  # Don't play transition audio
            })
            
            full_question = f"**Question {question_num}:**\n\n{next_question['question_text']}"
            
            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": full_question,
                "play_audio": True  # Only play audio for the question itself
            })
            st.session_state.waiting_for_answer = True
            st.session_state.last_audio_played = None  # Reset to play new audio
            st.rerun()
    
    # Show status when waiting
    if st.session_state.waiting_for_answer == True:
        st.info("💬 **Your turn!** Answer the question above using text or voice below.")
    
    st.divider()
    
    # Input area - Text and Voice options
    st.markdown("### 📝 Your Answer")
    
    input_method = st.radio(
        "Choose input method:",
        ["⌨️ Type Answer", "🎤 Record Audio"],
        horizontal=True,
        key="input_method_radio"
    )
    
    user_answer = None
    
    if input_method == "⌨️ Type Answer":
        # Text input
        user_input = st.chat_input("Type your answer here and press Enter...", key="chat_input")
        
        if user_input:
            user_answer = user_input
    
    else:
        # Audio recording
        st.write("Click the microphone button below to start recording your answer:")
        audio_data = st_audiorec()
        
        if audio_data:
            st.success("✅ Audio recorded!")
            
            if st.button("📤 Submit Audio Answer", type="primary", use_container_width=True):
                with st.spinner("🎧 Transcribing your audio..."):
                    transcribe_result = transcribe_audio(audio_data)
                    
                    if transcribe_result.get('success'):
                        user_answer = transcribe_result['data']['transcript']
                        st.success(f"✅ Transcribed: {user_answer}")
                    else:
                        st.error(f"❌ Transcription failed: {transcribe_result.get('error', 'Unknown error')}")
                        st.info("💡 Tip: Try typing your answer instead!")
    
    # Process answer when submitted
    if user_answer and st.session_state.waiting_for_answer == True:
        # Add user message to chat
        st.session_state.chat_messages.append({
            "role": "user",
            "content": user_answer,
            "play_audio": False
        })
        
        # Evaluate answer
        with st.spinner("🤔 Analyzing your answer..."):
            question = st.session_state.current_question
            result = submit_answer(question['id'], user_answer)
            
            if result.get('success'):
                data = result['data']
                evaluation = data['evaluation']
                
                # Create conversational feedback
                feedback_parts = []
                
                # Calculate average score
                avg_score = (
                    evaluation['technical_score'] + 
                    evaluation['communication_score'] + 
                    evaluation['problem_solving_score'] + 
                    evaluation['confidence_score'] + 
                    evaluation['depth_score']
                ) / 5
                
                # Overall impression
                if avg_score >= 8.5:
                    feedback_parts.append("Excellent answer! 🌟")
                elif avg_score >= 7:
                    feedback_parts.append("Great response! 👍")
                elif avg_score >= 5.5:
                    feedback_parts.append("Good answer.")
                else:
                    feedback_parts.append("Thanks for your response.")
                
                # Add specific positive feedback
                if evaluation.get('strengths') and len(evaluation['strengths']) > 0:
                    strength = evaluation['strengths'][0]
                    feedback_parts.append(f"I particularly appreciated {strength.lower()}.")
                
                # Quick score summary
                feedback_parts.append(f"(Score: {avg_score:.1f}/10)")
                
                # Combine feedback
                feedback_message = " ".join(feedback_parts)
                
                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": feedback_message,
                    "play_audio": False  # Don't play audio for feedback - too slow
                })
                
                st.session_state.waiting_for_answer = False
                st.session_state.last_audio_played = None  # Reset to play new audio
                time.sleep(0.5)  # Brief pause for natural feel
                st.rerun()
            else:
                st.error(f"❌ Error evaluating answer: {result.get('error', 'Unknown error')}")


def show_results_page():
    """Results page."""
    st.title("📊 Interview Results")
    
    if not st.session_state.session_id:
        st.warning("⚠️ No interview session found. Please complete an interview first!")
        return
    
    # Get interview status
    status_data = get_interview_status(st.session_state.session_id)
    
    if not status_data.get('success'):
        st.error(f"❌ Error: {status_data.get('error', 'Unknown error')}")
        return
    
    session = status_data['data']['session']
    progress = status_data['data']['progress']
    
    # Check if interview is complete
    if progress['remaining_questions'] > 0:
        st.warning(f"⚠️ Interview not complete yet! {progress['remaining_questions']} questions remaining.")
        st.info("Complete the interview to view your full report.")
        return
    
    # Get report
    with st.spinner("Generating comprehensive report..."):
        report_data = get_report(st.session_state.session_id)
    
    if not report_data.get('success'):
        st.error(f"❌ Error: {report_data.get('error', 'Unknown error')}")
        return
    
    report = report_data['data']['report']
    
    # Display results
    st.success("✅ Interview Complete!")
    
    # Overall metrics
    st.markdown("### 🎯 Overall Performance")
    
    metrics = report['performance_metrics']
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        score = metrics['overall_score']
        st.metric("Overall Score", f"{score:.1f}/100", 
                 delta=None if score < 60 else "Good" if score < 75 else "Excellent")
    
    with col2:
        st.metric("Technical", f"{metrics['technical_score']:.1f}/100")
    
    with col3:
        st.metric("Communication", f"{metrics['communication_score']:.1f}/100")
    
    with col4:
        st.metric("Problem Solving", f"{metrics['problem_solving_score']:.1f}/100")
    
    st.divider()
    
    # Recommendation
    recommendation = report['hiring_recommendation']
    rec_type = recommendation['recommendation']
    
    st.markdown("### 💼 Hiring Recommendation")
    
    if rec_type == "strong_hire":
        st.success(f"🌟 **STRONG HIRE** - {recommendation['summary']}")
    elif rec_type == "hire":
        st.success(f"✅ **HIRE** - {recommendation['summary']}")
    elif rec_type == "borderline":
        st.warning(f"⚠️ **BORDERLINE** - {recommendation['summary']}")
    else:
        st.error(f"❌ **NOT RECOMMENDED** - {recommendation['summary']}")
    
    # Detailed results
    col1, col2 = st.columns(2)
    
    with col1:
        with st.expander("✅ Strengths", expanded=True):
            for strength in recommendation.get('strengths', [])[:5]:
                st.write(f"- {strength}")
    
    with col2:
        with st.expander("⚠️ Areas for Improvement", expanded=True):
            for weakness in recommendation.get('weaknesses', [])[:5]:
                st.write(f"- {weakness}")
    
    # Download report
    st.divider()
    
    st.markdown("### 📥 Download Report")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.download_button(
            label="📄 Download JSON Report",
            data=json.dumps(report, indent=2),
            file_name=f"interview_report_{st.session_state.session_id}.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col2:
        st.info("📑 PDF report available at API endpoint")
        st.code(f"GET /api/download-report/{st.session_state.session_id}")


if __name__ == "__main__":
    main()
