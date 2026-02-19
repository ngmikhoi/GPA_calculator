import streamlit as st
import pandas as pd
from streamlit_javascript import st_javascript
from utils import calculate_grade
from ui_components import show_grade


def web():
    st.set_page_config(page_title="GPA Calculator HCMUT", page_icon="🌠", layout="wide")
    st.markdown("<h1 style='text-align: center;'>GPA Calculator HCMUT</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Hello, this is a website supporting HCMUT students calculating their GPA.</h3>", unsafe_allow_html=True)
    
    transcript_url = "https://mybk.hcmut.edu.vn/app/sinh-vien/ket-qua-hoc-tap/bang-diem-mon-hoc"
    st.link_button("Go to Academic Transcript page", transcript_url)
    if 'has_grade' not in st.session_state:
        st.session_state.has_grade = None
        st.session_state.summary = None
        st.session_state.semester_grade_list = None
        st.session_state.free_credit = None
    
    with st.form("Academic Transcript to GPA"):
        st.markdown("""
            <h5 style='text-align: center;'><br></br>
            Let go to your Academic Transcript page<br></br>
            Ctrl + A &nbsp; and &nbsp; Ctrl + C &nbsp; to copy all content<br></br>
            Ctrl + V &nbsp; to paste it into below input</h5>"""
        , unsafe_allow_html=True)
        
        clipped = st.text_area("")
        submitted = st.form_submit_button("Calculate GPA!")
        if submitted:
            st.session_state.has_grade, st.session_state.summary, st.session_state.semester_grade_list, st.session_state.free_credit = calculate_grade(False, clipped, None, None, None)

    if st.session_state.has_grade is not None:
        show_grade(st.session_state.has_grade, st.session_state.summary, st.session_state.semester_grade_list, st.session_state.free_credit)
    
    url = st_javascript("await fetch('').then(r => window.parent.location.href)")
    if (url == "http://localhost:8501/"):
        username = st.text_input("Username")
        password = st.text_input("Password")
        button_clicked = st.button("Calculate GPA!")
        if button_clicked:
            st.session_state.has_grade, st.session_state.summary, st.session_state.semester_grade_list, st.session_state.free_credit = calculate_grade(True, None, transcript_url, username, password)
            if st.session_state.has_grade is not None:                
                show_grade(st.session_state.has_grade, st.session_state.summary, st.session_state.semester_grade_list, st.session_state.free_credit)
            
        
    ft = """
    <style>
    a:link , a:visited{
    color: #BFBFBF;  /* theme's text color hex code at 75 percent brightness*/
    background-color: transparent;
    text-decoration: none;
    }

    a:hover,  a:active {
    color: #0283C3; /* theme's primary color*/
    background-color: transparent;
    text-decoration: underline;
    }

    #page-container {
    position: relative;
    min-height: 10vh;
    }

    footer{
        visibility:hidden;
    }

    .footer {
    position: relative;
    left: 0;
    top:230px;
    bottom: 0;
    width: 100%;
    background-color: transparent;
    color: #808080; /* theme's text color hex code at 50 percent brightness*/
    text-align: left; /* you can replace 'left' with 'center' or 'right' if you want*/
    }
    </style>

    <div id="page-container">

    <div class="footer">
    <p style='font-size: 0.875em;'>Made by <img src="https://em-content.zobj.net/source/skype/289/red-heart_2764-fe0f.png" alt="heart" height= "10"/><a style='display: inline; text-align: left;' href="https://github.com/ngmikhoi" target="_blank"> ngmikhoi</a></p>
    </div>

    </div>
    """
    st.write(ft, unsafe_allow_html=True)


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
