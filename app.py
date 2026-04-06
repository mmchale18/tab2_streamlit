#st.set_page_config(page_title="Workout Studio Application")
import streamlit as st
st.title("UD Fitness Club Application - Made by: Sophia, Annie, and Mallory")
if "registered_classes" not in st.session_state:
    st.session_state.registered_classes = []

tab1, tab2, tab3 = st.tabs(["Home", "Workouts", "Profile"])

with tab2:
#creating a workout class schedule in a table format
    st.header(":blue[Workout Class Schedule]")
    st.write("Here is the schedule for our group workout classes:")
    schedule_data = {
        "Class": ["Yoga", "Pilates", "Barre", "Cycle"],
        "Instructor": ["Mallory", "Annie", "Sophia", "Annie"],
        "Time": ["Monday 6 PM", "Tuesday 7 PM", "Wednesday 6 PM", "Thursday 7 PM"],
        "Location": ["Studio A", "Studio B", "Studio C", "Studio D"]
    }
    st.table(schedule_data)   
    class_options = [
    f"{schedule_data['Class'][i]} - {schedule_data['Time'][i]}"
    for i in range(len(schedule_data["Class"]))
]

    st.subheader("Sign Up for a Class")

    # Dropdown to select class
    selected_class = st.selectbox("Choose a class:", class_options)

    # Sign up button
    if st.button("Sign Up"):
        if selected_class not in st.session_state.registered_classes:
            st.session_state.registered_classes.append(selected_class)
            st.success(f"You signed up for {selected_class}!")
        else:
            st.warning("You're already signed up for this class.")

    # Show registered classes
    st.subheader("Your Registered Classes")

    if st.session_state.registered_classes:
        for i, cls in enumerate(st.session_state.registered_classes):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.write(cls)

            with col2:
                if st.button("Cancel", key=f"cancel_{i}"):
                    st.session_state.registered_classes.remove(cls)
                    st.rerun()
    else:
        st.info("You haven't signed up for any classes yet.") 

