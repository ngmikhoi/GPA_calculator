import streamlit as st
import pandas as pd
from streamlit_javascript import st_javascript
from utils import calculate_grade
from ui_components import show_grade


def web():
    # Enhanced page configuration with custom theme
    st.set_page_config(
        page_title="GPA Calculator HCMUT", 
        page_icon="🌠", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Load CSS from separate file
    with open("styles.css", "r") as f:
        css_content = f.read()
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)

    # Impressive header with gradient
    st.markdown("""
    <div class="main-header">
        <h1 style="margin: 0; font-size: 3rem; font-weight: bold;">🎓 GPA Calculator HCMUT</h1>
        <p style="margin: 0; font-size: 1rem; opacity: 0.8;">
            Empowering HCMUT students with intelligent grade analysis
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Feature cards
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>📋 Smart Analytics</h3>
            <p>GPA calculation with detailed breakdown by semester and overall performance metrics.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>✏️ Interactive Editing</h3>
            <p>Edit grades and predict future GPA scenarios with instant recalculation.</p>
        </div>
        """, unsafe_allow_html=True)


    transcript_url = "https://mybk.hcmut.edu.vn/app/sinh-vien/ket-qua-hoc-tap/bang-diem-mon-hoc"
    st.markdown(f"""
    <div style="text-align: center; margin: 2rem 0;">
        <a href="{transcript_url}" target="_blank" 
           style="background: linear-gradient(135deg, #00897b 0%, #004d40 100%); 
                  color: white; padding: 1rem 2rem; text-decoration: none; 
                  border-radius: 25px; font-weight: bold; display: inline-block;
                  box-shadow: 0 4px 15px rgba(0,0,0,0.2); transition: all 0.3s ease;"
           onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 20px rgba(0,0,0,0.3)'"
           onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 15px rgba(0,0,0,0.2)'">
            🔗 Go to Academic Transcript
        </a>
    </div>
    """, unsafe_allow_html=True)

    if 'has_grade' not in st.session_state:
        st.session_state.has_grade = None
        st.session_state.summary = None
        st.session_state.semester_grade_list = None
        st.session_state.free_credit = None
    
    with st.form("Academic Transcript to GPA"):
        st.markdown("""
        <div class="instruction-box" style="background: #f8f9fa; padding: 2rem; border-radius: 10px; margin: 2rem 0;">
            <h3 style="text-align: center; color: #2c3e50; margin-bottom: 1.5rem;">
                Input Your Academic Data 
            </h3>
            <p style="text-align: center; color: #7f8c8d; line-height: 1.6;">
                <strong>Step 1:</strong> Go to your Academic Transcript page<br>
                <strong>Step 2:</strong> Press <kbd style="background: #f1f3f4; color: #333; padding: 0.2rem 0.4rem; border-radius: 3px; border: 1px solid #ccc;">Ctrl + A</kbd> to select all<br>
                <strong>Step 3:</strong> Press <kbd style="background: #f1f3f4; color: #333; padding: 0.2rem 0.4rem; border-radius: 3px; border: 1px solid #ccc;">Ctrl + C</kbd> to copy<br>
                <strong>Step 4:</strong> Press <kbd style="background: #f1f3f4; color: #333; padding: 0.2rem 0.4rem; border-radius: 3px; border: 1px solid #ccc;">Ctrl + V</kbd> to paste below
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        clipped = st.text_area("", 
                           placeholder="Paste your academic transcript data here...",
                           height=200,
                           help="Copy and paste your complete academic transcript from myBK")

        submitted = st.form_submit_button("🚀 Calculate GPA!", 
                                     use_container_width=True)
        if submitted:
            with st.spinner("🔄 Processing your academic data..."):
                st.session_state.has_grade, st.session_state.summary, st.session_state.semester_grade_list, st.session_state.free_credit = calculate_grade(False, clipped, None, None, None)


    if st.session_state.has_grade is not None:
        show_grade(st.session_state.has_grade, st.session_state.summary, st.session_state.semester_grade_list, st.session_state.free_credit)
    
    url = st_javascript("await fetch('').then(r => window.parent.location.href)")
    if (url == "http://localhost:8501/"):
        st.markdown("""
        <div class="feature-card">
            <h3>🔐 Quick Login Access</h3>
            <p>Enter your credentials for automatic data retrieval</p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            username = st.text_input("👤 Username", 
                                placeholder="Enter your mybk username",
                                help="Your mybk student account username")
        with col2:
            password = st.text_input("🔒 Password", 
                                type="password",
                                placeholder="Enter your mybk password",
                                help="Your mybk student account password")

        button_clicked = st.button("🚀 Auto-Login & Calculate GPA!", 
                               use_container_width=True,
                               help="Automatically login and fetch your academic data")
        if button_clicked:
            with st.spinner("🔄 Logging in and fetching data..."):
                st.session_state.has_grade, st.session_state.summary, st.session_state.semester_grade_list, st.session_state.free_credit = calculate_grade(True, None, transcript_url, username, password)
                if st.session_state.has_grade is not None:                
                    show_grade(st.session_state.has_grade, st.session_state.summary, st.session_state.semester_grade_list, st.session_state.free_credit)

    st.markdown("""
    <div class="footer">
        <p style="margin: 0.5rem 0 0 0; opacity: 0.7; font-size: 0.9rem;">
            © 2025 <a href="https://github.com/ngmikhoi" target="_blank" 
                           style="color: #38ef7d; text-decoration: none; font-weight: bold;">
                ngmikhoi
            </a>. All rights reserved.
        </p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":    
    required = [
    "selenium", 
    "pyperclip", 
    "pandas", 
    "streamlit", 
    "streamlit_javascript", 
    ]
    
    import subprocess
    import sys
    
    for package in required:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            subprocess.run([sys.executable, "-m", "pip", "install", package])
    
    web()
