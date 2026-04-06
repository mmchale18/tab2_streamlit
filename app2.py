import time 
import streamlit as st
import json

#st.set_page_config(page_title="Workout Studio Application")
st.title("UD Fitness Club Application - Made by: Sophia, Annie, and Mallory")


if "page" not in st.session_state:
    st.session_state['page'] = "login"
if "logged_in_user" not in st.session_state:
    st.session_state["logged_in_user"] = None
if "user_role" not in st.session_state: 
    st.session_state["user_role"] = None
if "registered_classes" not in st.session_state:
    st.session_state.registered_classes = []

#save users information in a json file to be used for log in and sign up functionality, the json file will store the username, password, and user type (user or instructor) for each user that creates an account
def save_user_info(username, password, user_type):
    user_info = {
        "username": username,
        "password": password,
        "user_type": user_type}
    
    with open("user_info.json", "w") as f:
        json.dump(user_info, f)

#login page for users to log in as either a user or an instructor, the login credentials will be checked against the information stored in the json file and if the credentials are correct, the user will be logged in and taken to the main page of the app
if st.session_state["page"] == "login":
    user_type = st.selectbox("Select User Type", ["User", "Instructor"])
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Log In"):
        st.session_state["logged_in_user"] = username
        st.session_state["user_role"] = user_type
        save_user_info(username, password, user_type)
        st.success(f"Logged in as {username} ({user_type})")
        st.session_state['page'] = "main"
        st.rerun()
    #sign up options for users to create an account as either a user or an instructor, the sign up information will be saved in the json file and the user will be logged in and taken to the main page of the app
    st.subheader("Don't have an account? Sign up below!")
    new_user_type = st.selectbox("Select User Type", ["User", "Instructor"], key="signup_user_type")
    new_username = st.text_input("Username", key="signup_username")
    new_password = st.text_input("Password", type="password", key="signup_password")
    if st.button("Sign Up"):
        save_user_info(new_username, new_password, new_user_type)
        st.success(f"Account created for {new_username} ({new_user_type})")
        st.session_state["logged_in_user"] = new_username
        st.session_state["user_role"] = new_user_type
        st.session_state['page'] = "main"
        st.rerun()
else:
    #create a login/ logout sidebar for either a user or a instructor
    st.sidebar.header(f"Welcome, {st.session_state['logged_in_user']}!")
    st.sidebar.info(f"Access Level: {st.session_state['user_role']}")

    #logout button in side bar to clear the user info from the json file and log the user out
    if st.sidebar.button("Log Out"):
        st.session_state['page'] = "login"
        st.session_state["logged_in_user"] = None
        st.session_state["user_role"] = None
        st.rerun()

    #sending to either user or instructor page/interface based on the user role stored in the session state 
    if st.session_state["user_role"] == "Instructor":
        #instructor view 
        #tabs!
        tab1, tab2, tab3 = st.tabs(["Home", "Workouts", "Profile"])
        with tab1:
            #sophia work
            st.header(":blue[Welcome to the UD Fitness Club!]")
            st.subheader("Established March 2026")
            st.write("This is the home page of the UD Fitness Club application. Here you can find information about our services and get started on your fitness journey.")
            st.write("The UD Fitness Club is dedicated to helping you achieve your fitness goals with multiple group workout classes available.")
            #creating columns for workout classes & instructors 
            col1, col2 = st.columns([2,3])
            with col1:
                #list of workout classes availble 
                st.subheader("Available Workout Classes")
                st.write("- Yoga 🧘🏻‍♀️")
                st.write("- Pilates 🤸🏻‍♀️")
                st.write("- Barre 💃")
                st.write("- Cycle 🚴🏻‍♀️")
            with col2:
                #meet the instructors info:
                st.subheader("Meet Our Instructors")
                st.write("- :blue[**Mallory**]: Certified Yoga Instructor with 5 years of experience.")
                st.write("- :blue[**Annie**]: Experienced Pilates Instructor with a passion for helping clients achieve their fitness goals.")
                st.write("- :blue[**Sophia**]: Skilled Barre Instructor with a background in dance and fitness.")

            #create upcoming events section in table format
            st.header(":blue[Upcoming Events]")
            events_data = {
                "Event": ["Spring Fitness Challenge", "Nutrition Workshop", "Outdoor Bootcamp", "Summer Merch Sale", "Yoga Retreat"],
                "Date": ["April 15, 2026", "May 10, 2026", "June 5, 2026", "July 1, 2026", "August 15, 2026"],
                "Location": ["UD Fitness Club", "UD Fitness Club", "Local Park", "UD Fitness Club", "Mountain Retreat"]
            }
            st.table(events_data)

            #ai chat bot/box
            #ensure chat history exists when the app first loads
            if "messages" not in st.session_state:
                st.session_state["messages"] = [
                    {"role": "assistant", "content": "Hi, how can I help you?"}
                ]
            # display chat history by looping through messages to show them on the UI
            for msg in st.session_state["messages"]:
                st.chat_message(msg["role"]).write(msg["content"])

            user_input = st.chat_input("Ask a question")

            if user_input:
                with st.spinner("Thinking..."):
                    st.session_state["messages"].append(
                        {"role": "user", "content": user_input})
                    #add four responses for the ai to choose from when a user asks a question about the fitness club, the responses should be about the workout classes, the instructors, the upcoming events, and the location of the fitness club
                    if "workout" in user_input.lower():
                        ai_response = "We offer Yoga, Pilates, Barre, and Cycle classes. Check out the Workouts tab for the schedule!"
                    elif "instructor" in user_input.lower():
                        ai_response = "Our instructors are Mallory (Yoga), Annie (Pilates and Cycle), and Sophia (Barre). They are all highly experienced and passionate about fitness!"
                    elif "event" in user_input.lower():
                        ai_response = "We have several upcoming events including the Spring Fitness Challenge, Nutrition Workshop, Outdoor Bootcamp, Summer Merch Sale, and Yoga Retreat. Check out the Home tab for more details!"
                    elif "location" in user_input.lower():
                        ai_response = "The UD Fitness Club is located at 123 Fitness Ave, Wilmington, DE. We have multiple studios and a welcoming community!"
                    else:   
                        ai_response = "I could not find an answer for it. Try again."
                    st.session_state["messages"].append(
                        {"role": "assistant", "content": ai_response}
                    )
                    time.sleep(1) 
                    st.rerun()

            if st.button("Clear Chat", key="clear_chat_btn"):
                st.session_state["messages"] = [
                    {"role": "assistant", "content": "Hi, how can I help you?"}
                ]
                st.rerun()
    else:
        #user view 
        #tabs again
        tab1, tab2, tab3 = st.tabs(["Home", "Workouts", "Profile"])
        with tab1:
            st.header(":blue[Welcome to the UD Fitness Club!]")
            st.subheader("Established March 2026")
            st.write("This is the home page of the UD Fitness Club application. Here you can find information about our services and get started on your fitness journey.")
            st.write("The UD Fitness Club is dedicated to helping you achieve your fitness goals with multiple group workout classes available.")
            #creating columns for workout classes & instructors 
            col1, col2 = st.columns([2,3])
            with col1:
                #list of workout classes availble 
                st.subheader("Available Workout Classes")
                st.write("- Yoga 🧘🏻‍♀️")
                st.write("- Pilates 🤸🏻‍♀️")
                st.write("- Barre 💃")
                st.write("- Cycle 🚴🏻‍♀️")
            with col2:
                #meet the instructors info:
                st.subheader("Meet Our Instructors")
                st.write("- :blue[**Mallory**]: Certified Yoga Instructor with 5 years of experience.")
                st.write("- :blue[**Annie**]: Experienced Pilates Instructor with a passion for helping clients achieve their fitness goals.")
                st.write("- :blue[**Sophia**]: Skilled Barre Instructor with a background in dance and fitness.")

            #create upcoming events section in table format
            st.header(":blue[Upcoming Events]")
            events_data = {
                "Event": ["Spring Fitness Challenge", "Nutrition Workshop", "Outdoor Bootcamp", "Summer Merch Sale", "Yoga Retreat"],
                "Date": ["April 15, 2026", "May 10, 2026", "June 5, 2026", "July 1, 2026", "August 15, 2026"],
                "Location": ["UD Fitness Club", "UD Fitness Club", "Local Park", "UD Fitness Club", "Mountain Retreat"]
            }
            st.table(events_data)
        with tab2: 
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
        #annie
# ---------------- PROFILE ----------------
            with tab3:
                st.header(":blue[My Profile]")
                st.divider()

            # -------- FAKE SESSION USER (replace later if you have login) --------
                if "user" not in st.session_state:
                    st.session_state.user = {
                        "email": "demo@udel.edu",
                        "role": "client"
                    }

                user = st.session_state.user

            # -------- ACCOUNT INFO --------
                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("Account Information")
                    st.write("Email:", user["email"])
                    st.write("Role:", user["role"])

            # -------- UPDATE PASSWORD --------
                with col2:
                    st.subheader("Update Password")

                    new_password = st.text_input("New Password", type="password", key="profile_pass")

                    if st.button("Update Password"):
                        if not new_password:
                            st.warning("Please enter a new password")
                        else:
                            st.success("Password updated successfully (demo)")

            # -------- BOOKING HISTORY (MVP CRUD READ) --------
                st.divider()
                st.subheader("My Bookings")

            # Example data if you don’t have JSON hooked up yet
                if "registered_classes" not in st.session_state:
                    st.session_state.registered_classes = [
                        {"class": "Pilates", "date": "2026-04-05", "time": "9:00 AM"},
                        {"class": "Yoga", "date": "2026-04-07", "time": "6:00 PM"}
                    ]

                registered_classes = st.session_state.registered_classes

                if len(registered_classes) == 0:
                    st.info("No bookings yet")
                else:
                    for b in registered_classes:
                        col1, col2 = st.columns([3,1])

                        with col1:
                            st.write(f"{b['class']} - {b['date']} at {b['time']}")

                        with col2:
                            if st.button("Cancel", key=f"cancel_{b['class']}_{b['date']}"):
                                registered_classes.remove(b)
                                st.success("Booking cancelled")
                                st.rerun()

                # -------- SIMPLE CHATBOT (PHASE 1 REQUIREMENT) --------
                st.divider()
                st.subheader("Chat Assistant")

                question = st.text_input("Ask something (e.g., 'next class')")

                if question:
                    q = question.lower()

                    if "next class" in q:
                        if registered_classes:
                            next_class = registered_classes[0]
                            st.write(f"Your next class is {next_class['class']} on {next_class['date']} at {next_class['time']}")
                        else:
                            st.write("You have no upcoming classes")

                    elif "available" in q:
                        st.write("Available classes: Yoga, Pilates, Barre, Cycle")

                    elif "bring" in q:
                        st.write("Bring water, grip socks, and a yoga mat")

                    else:
                        st.write("I can help with bookings and classes!")
