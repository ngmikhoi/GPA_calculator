import streamlit as st
import pandas as pd
from utils import convert_10_to_4, convert_10_to_A


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
    has_grade["Priority"] = (has_grade["Credit"] * (4 - has_grade["Grade_4"])).round(2)
    has_grade["Priority"] = has_grade["Priority"].astype(float)
    has_grade["Priority_10"] = (has_grade["Credit"] * (10 - has_grade["Grade_10"])).round(2)
    has_grade["Priority_10"] = has_grade["Priority_10"].astype(float)

    has_grade = has_grade.sort_values(["Priority", "Priority_10"], ascending=False, ignore_index=True)
    has_grade.index += 1
    
    tab1, tab2, tab3 = st.tabs(["Overall GPA", "Semester GPA", "Predict GPA"])
        
    with tab1:
        overall_performance(summary)
        st.subheader("Academic Transcript (Original)")
        st.dataframe(has_grade.loc[:, ["Course", "Course Name", "Grade", "Grade_4", "Grade_10", "Credit"]])
        
    with tab2:
        semester_performance(semester_grade_list, free_credit)

    with tab3:
        st.subheader("Edit Academic Transcript")
        edited_df = st.data_editor(has_grade.loc[:, ["Course", "Course Name", "Grade_10", "Credit"]], num_rows="dynamic")
        
        if st.button("Recalculate GPA", key="recalculate_overall"):
            map_grade_4 = {'A+': 4, 'A': 4, 'B+': 3.5, 'B': 3, 'C+': 2.5, 'C': 2, 'D+': 1.5, 'D': 1}
            
            edited_df["Grade"] = edited_df["Grade_10"].apply(convert_10_to_A)
            edited_df["Grade_4"] = edited_df["Grade_10"].apply(convert_10_to_4)

            valid_grades = edited_df[edited_df["Grade_4"].isin(map_grade_4.values())]
            
            total_credit = valid_grades["Credit"].sum()
            total_grade = (valid_grades["Grade_4"] * valid_grades["Credit"]).sum()
            average_grade = total_grade / total_credit if total_credit else 0
            
            total_grade_10 = (valid_grades["Grade_10"] * valid_grades["Credit"]).sum()
            average_grade_10 = total_grade_10 / total_credit if total_credit else 0
            
            new_summary = {}
            new_summary["Total credits:"] = total_credit
            new_summary["Total grade 4:"] = total_grade
            new_summary["GPA scale of 4:"] = average_grade
            new_summary["Total grade 10:"] = total_grade_10
            new_summary["GPA scale of 10:"] = average_grade_10
            
            st.toast("GPA recalculated successfully!", icon="✅")
            overall_performance(new_summary)

            st.subheader("Updated Academic Transcript")
            display_df = valid_grades.copy()
            
            st.write("Sorting by Priority (= Credit * (4 - Grade_4)), higher priority means higher potential improvement")

            display_df["Priority"] = (display_df["Credit"] * (4 - display_df["Grade_4"])).round(2)
            display_df["Priority"] = display_df["Priority"].astype(float)
            display_df["Priority_10"] = (display_df["Credit"] * (10 - display_df["Grade_10"])).round(2)
            display_df["Priority_10"] = display_df["Priority_10"].astype(float)

            display_df = display_df.sort_values(["Priority", "Priority_10"], ascending=False, ignore_index=True)
            display_df.index += 1
            
            st.dataframe(display_df.loc[:, ["Course", "Course Name", "Grade", "Grade_4", "Grade_10", "Credit", "Priority", "Priority_10"]])
