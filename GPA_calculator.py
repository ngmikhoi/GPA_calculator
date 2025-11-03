import subprocess
import time
import sys
        
def get_grade_driver(transcript_url, username, password):
    driver = webdriver.Chrome()
    driver.get(transcript_url)
     
    is_input = True
    time.sleep(1)
    get_url = driver.current_url
    while (get_url != transcript_url):
        if ("https://sso.hcmut.edu.vn/cas/login" in get_url):
            input_username = driver.find_element(By.ID, 'username')
            input_password = driver.find_element(By.ID, 'password')
            if is_input:
                input_username.send_keys(username)
                if username and username != "" and password and password != "":
                    input_password.send_keys(password)
                is_input = False
            username = input_username.get_attribute("value")
            password = input_password.get_attribute("value")   
        time.sleep(1)
        get_url = driver.current_url
        
    time.sleep(7)
    body = driver.find_element(By.TAG_NAME, 'body')
    body.send_keys(Keys.CONTROL, 'a')
    body.send_keys(Keys.CONTROL, 'c')
    driver.quit()
    return pyperclip.paste()


def clipped_to_df(is_driver, clipped):
    if is_driver:
        clipped = clipped.split('\r\n')
    else:
        clipped = clipped.split('\n')
    clipped = [item.split('\t') for item in clipped]
    return pd.DataFrame(clipped)


def calculate_grade(is_driver, clipped, transcript_url, username, password):
    if is_driver:
        clipped = get_grade_driver(transcript_url, username, password)
    if "myBk/app" in clipped:        
        df = clipped_to_df(is_driver, clipped)
        df = df.rename(columns={df.columns[1]: "Course", df.columns[2]: "Course Name", df.columns[5]: "Credit", df.columns[3]: "Grade_10", df.columns[4]: "Grade"})
        map_grade_4 = {'A+': 4, 'A': 4, 'B+': 3.5, 'B': 3, 'C+': 2.5, 'C': 2, 'D+': 1.5, 'D': 1}
        df = df.loc[:, ["Course", "Course Name", "Credit", "Grade_10", "Grade"]]
        
        has_grade = df.loc[df["Grade"].isin(map_grade_4.keys())]
        has_grade["Grade_4"] = list(map(lambda x: map_grade_4[x], has_grade["Grade"]))
        has_grade = has_grade.sort_values(by=["Course", "Grade_4"], ascending=True)
        has_grade = has_grade.drop_duplicates(subset=["Course"], keep="last")
        has_grade = has_grade.reset_index(drop=True)
        has_grade.index += 1
        has_grade["Credit"] = has_grade["Credit"].astype(int)
        has_grade["Grade_10"] = has_grade["Grade_10"].astype(float)
        
        map_grade_free = {"12": "MT", "21": "DT"}
        grade_free = df.loc[df["Grade_10"].isin(map_grade_free.keys())]
        grade_free["Credit"] = grade_free["Credit"].astype(int)
        
        free_credit = sum(grade_free["Credit"])
        total_credit = sum(has_grade["Credit"])

        total_grade = sum(has_grade["Grade_4"] * has_grade["Credit"])
        average_grade = total_grade / total_credit if total_credit else 0

        total_grade_10 = sum(has_grade["Grade_10"] * has_grade["Credit"])
        average_grade_10 = total_grade_10 / total_credit if total_credit else 0
        
        summary = {}
        summary["Total credits:"] = total_credit + free_credit
        summary["Total grade 4:"] = total_grade
        summary["GPA scale of 4:"] = average_grade
        summary["Total grade 10:"] = total_grade_10
        summary["GPA scale of 10:"] = average_grade_10
        return has_grade, summary
    return None, None


def overall_performance(summary):
    st.subheader("Overall Performance")
    col1, col2, col3= st.columns(3)
    with col1:
        st.markdown(f"""
            {list(summary.keys())[0]} {list(summary.values())[0]}       
        """ )
    with col2:
        st.markdown(f"""
            {list(summary.keys())[2]} {round(list(summary.values())[2], 7)}     
        """ )
    with col3:
        st.markdown(f"""
            {list(summary.keys())[4]} {round(list(summary.values())[4], 7)}    
        """ )


def academic_transcript(has_grade):
    st.subheader("Academic Transcript")
    st.dataframe(has_grade.loc[:, ["Course", "Course Name", "Credit", "Grade_10", "Grade"]])


def show_grade(has_grade, summary):
    tab1, tab2, tab3 = st.tabs(["Only GPA", "Detailed Transcript", "Both"])
        
    with tab1:
        overall_performance(summary)

    with tab2:
        academic_transcript(has_grade)
        
    with tab3:
        academic_transcript(has_grade)
        overall_performance(summary)


def web():
    st.set_page_config(page_title="HCMUT GPA Calculator", layout="centered")
    st.markdown("<h1 style='text-align: center;'>HCMUT GPA Calculator</h1>", unsafe_allow_html=True)
    st.markdown("### Hello, this is a website supporting HCMUT students calculating their GPA. I hope it can help you!")
    st.divider()
    
    transcript_url = "https://mybk.hcmut.edu.vn/app/sinh-vien/ket-qua-hoc-tap/bang-diem-mon-hoc"
    st.link_button("Go to Academic Transcript page", transcript_url)
    
    with st.form("Academic Transcript to GPA"):
        st.markdown("""
            <h5 style='text-align: center;'><br></br>
            Let go to your Academic Transcript page<br></br>
            Ctrl + A &nbsp; and &nbsp; Ctrl + C &nbsp; to copy all content<br></br>
            Ctrl + V &nbsp; to paste it into below input<br></br></h5>"""
        , unsafe_allow_html=True)
        
        clipped = st.text_area("")
        submitted = st.form_submit_button("Calculate GPA!")
        if submitted:
            has_grade, summary = calculate_grade(False, clipped, None, None, None)
            if has_grade is not None:                
                show_grade(has_grade, summary)
    
    url = st_javascript("await fetch('').then(r => window.parent.location.href)")
    if (url == "http://localhost:8501/"):
        username = st.text_input("Username")
        password = st.text_input("Password")
        button_clicked = st.button("Calculate GPA!")
        if button_clicked:
            has_grade, summary = calculate_grade(True, None, transcript_url, username, password)
            if has_grade is not None:                
                show_grade(has_grade, summary)
        
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
    
    for package in required:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            subprocess.run([sys.executable, "-m", "pip", "install", package])
            
    import pyperclip
    import streamlit as st
    import pandas as pd
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from streamlit_javascript import st_javascript
    
    web()