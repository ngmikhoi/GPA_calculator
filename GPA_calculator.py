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


def clipped_to_semester_df(is_driver, clipped):
    if "Tích lũy học kỳ" in clipped:
        clipped = clipped.replace("0.0\t0\tTích lũy học kỳ", "0")
        clipped_semester_list = clipped.split("Tích lũy học kỳ")

    df_semester_list = []

    for i in range(len(clipped_semester_list) -1, 0, -1):
        clipped_semester = clipped_semester_list[i]
        if is_driver:
            clipped_semester = clipped_semester.split('\r\n')
        else:
            clipped_semester = clipped_semester.split('\n')
        clipped_semester = [item.split('\t') for item in clipped_semester]
        df_semester_list.append(pd.DataFrame(clipped_semester))
    return df_semester_list


def calculate_grade(is_driver, clipped, transcript_url, username, password):
    if is_driver:
        clipped = get_grade_driver(transcript_url, username, password)
        
    semester_grade_list = []
    
    cumulative_df = None
    
    if "Tích lũy học kỳ" in clipped:
        df_semester_list = clipped_to_semester_df(is_driver, clipped)
        
        free_credit = 0
        if "/miễn điểm" in clipped:
            free_credit = int(clipped.split("/miễn điểm\t")[1].split("\t")[0].strip())  
        
        for df in df_semester_list:
            df = df.rename(columns={df.columns[1]: "Course", df.columns[2]: "Course Name", df.columns[5]: "Credit", df.columns[3]: "Grade_10", df.columns[4]: "Grade"})
            map_grade_4 = {'A+': 4, 'A': 4, 'B+': 3.5, 'B': 3, 'C+': 2.5, 'C': 2, 'D+': 1.5, 'D': 1, 'F': 0}
            df = df.loc[:, ["Course", "Course Name", "Credit", "Grade_10", "Grade"]]
            has_grade = df.loc[df["Grade"].isin(map_grade_4.keys())]
            has_grade["Grade_4"] = list(map(lambda x: map_grade_4[x], has_grade["Grade"]))
            
            has_grade["Credit"] = has_grade["Credit"].astype(int)
            has_grade["Grade_10"] = has_grade["Grade_10"].astype(float)
            has_grade["Grade_4"] = has_grade["Grade_4"].astype(float)
            
            total_credit = sum(has_grade["Credit"])
            fail_credit = sum(has_grade.loc[has_grade["Grade_4"] == 0]["Credit"])
            
            total_grade = sum(has_grade["Grade_4"] * has_grade["Credit"])
            average_grade = total_grade / total_credit if total_credit else 0

            total_grade_10 = sum(has_grade["Grade_10"] * has_grade["Credit"])
            average_grade_10 = total_grade_10 / total_credit if total_credit else 0

            if cumulative_df is None:
                cumulative_df = has_grade
            else:
                cumulative_df = pd.concat([cumulative_df, has_grade], ignore_index=True)
                
            if cumulative_df is not None:
                cumulative_df = cumulative_df.sort_values(by=["Course", "Grade_4"], ascending=True)
                cumulative_df = cumulative_df.drop_duplicates(subset=["Course"], keep="last")
                cumulative_df = cumulative_df[cumulative_df["Grade_4"] > 0]
                cumulative_df = cumulative_df.reset_index(drop=True)
                cumulative_df.index += 1

                cumulative_total_credit = sum(cumulative_df["Credit"])
                cumulative_total_grade = sum(cumulative_df["Grade_4"] * cumulative_df["Credit"])
                cumulative_average_grade = cumulative_total_grade / cumulative_total_credit if cumulative_total_credit else 0
                cumulative_total_grade_10 = sum(cumulative_df["Grade_10"] * cumulative_df["Credit"])
                cumulative_average_grade_10 = cumulative_total_grade_10 / cumulative_total_credit if cumulative_total_credit else 0
            
            semester_grade_list.append({
                "Df": has_grade,
                "Credit": total_credit - fail_credit,
                "GPA scale of 4": average_grade,
                "GPA scale of 10": average_grade_10,
                "Cumulative Credit": cumulative_total_credit + free_credit,
                "Cumulative GPA scale of 4": cumulative_average_grade,
                "Cumulative GPA scale of 10": cumulative_average_grade_10,
            })

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
        has_grade["Grade_4"] = has_grade["Grade_4"].astype(float)
        
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
        return has_grade, summary, semester_grade_list, free_credit
    return None, None, None, None


def overall_performance(summary):
    st.subheader("Overall Performance")
    col1, col2, col3= st.columns(3)
    with col1:
        st.markdown(f"""
            {list(summary.keys())[0]} {list(summary.values())[0]}       
        """ )
    with col2:
        st.markdown(f"""
            {list(summary.keys())[2]} {round(list(summary.values())[2], 7)} ≈ {round(list(summary.values())[2], 1)}     
        """ )
    with col3:
        st.markdown(f"""
            {list(summary.keys())[4]} {round(list(summary.values())[4], 7)} ≈ {round(list(summary.values())[4], 2)}    
        """ )


def academic_transcript(has_grade):
    st.subheader("Academic Transcript")
    st.dataframe(has_grade.loc[:, ["Course", "Course Name", "Grade", "Grade_4", "Grade_10", "Credit"]])
    
    
def semester_performance(semester_grade_list, free_credit):
    st.subheader("Semester Performance")
    st.markdown(f"Free Credit: {free_credit}")
    st.divider()
    
    for i in range(len(semester_grade_list)):
        st.dataframe(semester_grade_list[i]["Df"].loc[:, ["Course", "Course Name", "Grade", "Grade_4", "Grade_10", "Credit"]])
        col1, col2, col3= st.columns(3)
        with col1:
            st.markdown(f"""
                Credit: {semester_grade_list[i]['Credit']}       
            """ )
            st.markdown(f"""
                Cumulative Credit: {semester_grade_list[i]['Cumulative Credit']}
            """ )
        with col2:
            st.markdown(f"""
                GPA scale of 4: {round(semester_grade_list[i]['GPA scale of 4'], 7)} ≈ {round(semester_grade_list[i]['GPA scale of 4'], 1)}
            """ )
            st.markdown(f"""
                Cumulative GPA scale of 4: {round(semester_grade_list[i]['Cumulative GPA scale of 4'], 7)} ≈ {round(semester_grade_list[i]['Cumulative GPA scale of 4'], 1)}
            """ )
        with col3:
            st.markdown(f"""
                GPA scale of 10: {round(semester_grade_list[i]['GPA scale of 10'], 7)} ≈ {round(semester_grade_list[i]['GPA scale of 10'], 2)}   
            """ )
            st.markdown(f"""
                Cumulative GPA scale of 10: {round(semester_grade_list[i]['Cumulative GPA scale of 10'], 7)} ≈ {round(semester_grade_list[i]['Cumulative GPA scale of 10'], 2)}
            """ )
        st.divider()
        

def show_grade(has_grade, summary, semester_grade_list, free_credit):
    tab1, tab2 = st.tabs(["Overall GPA", "Semester GPA"])
        
    with tab1:
        overall_performance(summary)
        academic_transcript(has_grade)
        
    with tab2:
        semester_performance(semester_grade_list, free_credit)


def web():
    st.set_page_config(page_title="GPA Calculator HCMUT", page_icon="🌠", layout="wide")
    st.markdown("<h1 style='text-align: center;'>GPA Calculator HCMUT</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Hello, this is a website supporting HCMUT students calculating their GPA.</h3>", unsafe_allow_html=True)
    
    transcript_url = "https://mybk.hcmut.edu.vn/app/sinh-vien/ket-qua-hoc-tap/bang-diem-mon-hoc"
    st.link_button("Go to Academic Transcript page", transcript_url)
    
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
            has_grade, summary, semester_grade_list, free_credit = calculate_grade(False, clipped, None, None, None)
            if has_grade is not None:                
                show_grade(has_grade, summary, semester_grade_list, free_credit)
    
    url = st_javascript("await fetch('').then(r => window.parent.location.href)")
    if (url == "http://localhost:8501/"):
        username = st.text_input("Username")
        password = st.text_input("Password")
        button_clicked = st.button("Calculate GPA!")
        if button_clicked:
            has_grade, summary, semester_grade_list, free_credit = calculate_grade(True, None, transcript_url, username, password)
            if has_grade is not None:                
                show_grade(has_grade, summary, semester_grade_list, free_credit)
            
        
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
    