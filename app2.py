import time
import streamlit as st
import json
import openai

# st.set_page_config(page_title="Workout Studio Application")
st.title("UD Fitness Club Application - Made by: Sophia, Annie, and Mallory")

if "page" not in st.session_state:
    st.session_state['page'] = "login"
if "logged_in_user" not in st.session_state:
    st.session_state["logged_in_user"] = None
if "user_role" not in st.session_state:
    st.session_state["user_role"] = None
if "registered_classes" not in st.session_state:
    st.session_state.registered_classes = []

# UserManager class to handle user authentication and data management
class UserManager:
    def __init__(self):
        self.users = self.load_users()
        self.bookings = self.load_bookings()

    def load_users(self):
        try:
            with open("user_info.json", "r") as f:
                data = json.load(f)
                if isinstance(data, dict) and "username" in data:
                    # Old format: single user dict
                    return [data]
                elif isinstance(data, dict):
                    # Dict of users format (from previous version)
                    return list(data.values())
                elif isinstance(data, list):
                    # List format
                    return data
                else:
                    return []
        except FileNotFoundError:
            return []

    def save_users(self):
        with open("user_info.json", "w") as f:
            json.dump(self.users, f)

    def load_bookings(self):
        try:
            with open("bookings.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_bookings(self):
        with open("bookings.json", "w") as f:
            json.dump(self.bookings, f)

    def get_user_bookings(self, username):
        return self.bookings.get(username, [])

    def add_booking(self, username, class_name):
        if username not in self.bookings:
            self.bookings[username] = []
        if class_name not in self.bookings[username]:
            self.bookings[username].append(class_name)
            self.save_bookings()
            return True
        return False

    def remove_booking(self, username, class_name):
        if username in self.bookings and class_name in self.bookings[username]:
            self.bookings[username].remove(class_name)
            self.save_bookings()
            return True
        return False

    def signup(self, username, password, user_type):
        for user in self.users:
            if user["username"] == username:
                return False  # Username already exists
        self.users.append({
            "username": username,
            "password": password,
            "user_type": user_type,
            "display_name": username,
            "email": "",
            "bio": ""
        })
        self.save_users()
        return True

    def get_user_profile(self, username):
        for user in self.users:
            if user["username"] == username:
                return user
        return None

    def update_profile(self, username, display_name, email, bio):
        for user in self.users:
            if user["username"] == username:
                user["display_name"] = display_name
                user["email"] = email
                user["bio"] = bio
                self.save_users()
                return True
        return False

    def login(self, username, password):
        for user in self.users:
            if user["username"] == username and user["password"] == password:
                return user["user_type"]
        return None

# Create UserManager instance
user_manager = UserManager()

# WorkoutManager class to handle workout-related functionality
class WorkoutManager:
    def __init__(self, user_manager):
        self.user_manager = user_manager
        self.classes = self.load_classes()

    def load_classes(self):
        try:
            with open("classes.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_classes(self):
        with open("classes.json", "w") as f:
            json.dump(self.classes, f)

    def add_class(self, class_name, instructor, time, location):
        self.classes.append({
            "class": class_name,
            "instructor": instructor,
            "time": time,
            "location": location
        })
        self.save_classes()

    def edit_class(self, index, class_name, instructor, time, location):
        if 0 <= index < len(self.classes):
            self.classes[index] = {
                "class": class_name,
                "instructor": instructor,
                "time": time,
                "location": location
            }
            self.save_classes()

    def delete_class(self, index):
        if 0 <= index < len(self.classes):
            del self.classes[index]
            self.save_classes()

    def display_available_classes(self):
        st.subheader("Available Workout Classes")
        for cls in self.classes:
            emoji = {"Yoga": "🧘🏻‍♀️", "Pilates": "🤸🏻‍♀️", "Barre": "💃", "Cycle": "🚴🏻‍♀️"}.get(cls["class"], "💪")
            st.write(f"- {cls['class']} {emoji}")

    def display_available_classes_calendar(self):
        """Display available classes in a calendar format"""
        st.subheader("📅 Class Schedule Calendar")
        if not self.classes:
            st.info("📭 No classes available yet.")
            return
        
        # Days of week in order
        days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        # Group classes by day
        classes_by_day = {day: [] for day in days_order}
        for cls in self.classes:
            # Extract day from time field (e.g., "Monday 6 PM" -> "Monday")
            time_parts = cls["time"].split()
            day = time_parts[0] if time_parts else "Unknown"
            if day in classes_by_day:
                classes_by_day[day].append(cls)
        
        # Display calendar grid
        cols = st.columns(7)
        for i, day in enumerate(days_order):
            with cols[i]:
                st.markdown(f"### **{day[:3]}**")
                if classes_by_day[day]:
                    for idx, cls in enumerate(classes_by_day[day]):
                        emoji = {"Yoga": "🧘", "Pilates": "🤸", "Barre": "💃", "Cycle": "🚴"}.get(cls["class"], "💪")
                        st.markdown(f"**{emoji} {cls['class']}**")
                        st.caption(f"🕐 {' '.join(cls['time'].split()[1:])}")
                        st.caption(f"👨‍🏫 {cls['instructor']}")
                        st.caption(f"📍 {cls['location']}")
                        if st.button(
                            "Sign Up",
                            key=f"cal_signup_{i}_{idx}",
                            use_container_width=True
                        ):
                            username = st.session_state["logged_in_user"]
                            class_identifier = self.get_class_identifier(cls)
                            if self.user_manager.add_booking(username, class_identifier):
                                st.session_state.registered_classes.append(class_identifier)
                                st.success(f"✅ Signed up for {cls['class']}!")
                                st.rerun()
                            else:
                                st.warning(f"⚠️ Already signed up!")
                        st.divider()
                else:
                    st.caption("No classes")

    def display_available_classes_with_signup(self):
        """Display available classes with inline sign-up buttons for users"""
        st.subheader("💪 Available Classes")
        if self.classes:
            for idx, cls in enumerate(self.classes):
                col1, col2, col3, col4, col5 = st.columns([2.5, 2, 1.5, 1.5, 0.8])
                with col1:
                    emoji = {"Yoga": "🧘🏻‍♀️", "Pilates": "🤸🏻‍♀️", "Barre": "💃", "Cycle": "🚴🏻‍♀️"}.get(cls["class"], "💪")
                    st.markdown(f"**{emoji} {cls['class']}**")
                with col2:
                    st.caption(f"👨‍🏫 {cls['instructor']}")
                with col3:
                    st.caption(f"🕐 {cls['time']}")
                with col4:
                    st.caption(f"📍 {cls['location']}")
                with col5:
                    if st.button("➕", key=f"signup_btn_{idx}", help="Sign up for this class", use_container_width=True):
                        username = st.session_state["logged_in_user"]
                        class_identifier = self.get_class_identifier(cls)
                        if self.user_manager.add_booking(username, class_identifier):
                            st.session_state.registered_classes.append(class_identifier)
                            st.success(f"✅ Signed up for {cls['class']}!")
                            st.rerun()
                        else:
                            st.warning(f"⚠️ Already signed up for this class!")
                st.divider()
        else:
            st.info("📭 No classes available yet.")

    def display_schedule(self):
        st.header("📅 Workout Class Schedule")
        st.write("Browse our available group fitness classes:")

        if self.classes:
            # Display as cards instead of table
            for cls in self.classes:
                with st.container():
                    col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
                    with col1:
                        emoji = {"Yoga": "🧘‍♀️", "Pilates": "🤸‍♀️", "Barre": "💃", "Cycle": "🚴‍♀️"}.get(cls["class"], "💪")
                        st.markdown(f"**{emoji} {cls['class']}**")
                    with col2:
                        st.caption(f"👨‍🏫 {cls['instructor']}")
                    with col3:
                        st.caption(f"🕐 {cls['time']}")
                    with col4:
                        st.caption(f"📍 {cls['location']}")
                    st.divider()
        else:
            st.info("📭 No classes scheduled yet.")

    def display_schedule_with_signup(self):
        """Display workout schedule with inline sign-up buttons"""
        st.header("📅 Workout Class Schedule")
        st.write("Browse and sign up for our group fitness classes:")

        if self.classes:
            for idx, cls in enumerate(self.classes):
                col1, col2, col3, col4, col5 = st.columns([2.5, 2, 1.5, 1.5, 0.8])
                with col1:
                    emoji = {"Yoga": "🧘‍♀️", "Pilates": "🤸‍♀️", "Barre": "💃", "Cycle": "🚴‍♀️"}.get(cls["class"], "💪")
                    st.markdown(f"**{emoji} {cls['class']}**")
                with col2:
                    st.caption(f"👨‍🏫 {cls['instructor']}")
                with col3:
                    st.caption(f"🕐 {cls['time']}")
                with col4:
                    st.caption(f"📍 {cls['location']}")
                with col5:
                    if st.button("➕", key=f"schedule_signup_{idx}", help="Sign up for this class", use_container_width=True):
                        username = st.session_state["logged_in_user"]
                        class_identifier = self.get_class_identifier(cls)
                        if self.user_manager.add_booking(username, class_identifier):
                            st.session_state.registered_classes.append(class_identifier)
                            st.success(f"✅ Signed up for {cls['class']}!")
                            st.rerun()
                        else:
                            st.warning(f"⚠️ Already signed up for this class!")
                st.divider()
        else:
            st.info("📭 No classes scheduled yet.")

    def get_class_options(self):
        return [f"{c['class']} - {c['time']}" for c in self.classes]

    def get_class_identifier(self, class_obj):
        return f"{class_obj['class']} - {class_obj['time']}"

    def get_student_count_for_class(self, class_identifier):
        count = 0
        for bookings in self.user_manager.bookings.values():
            if class_identifier in bookings:
                count += 1
        return count

    def get_instructor_classes(self, instructor_name):
        return [cls for cls in self.classes if cls["instructor"] == instructor_name]

    def get_instructor_summary(self, instructor_name):
        instructor_classes = self.get_instructor_classes(instructor_name)
        total_classes = len(instructor_classes)
        total_students = 0
        class_summaries = []

        for cls in instructor_classes:
            identifier = self.get_class_identifier(cls)
            count = self.get_student_count_for_class(identifier)
            total_students += count
            class_summaries.append({
                "class": cls["class"],
                "time": cls["time"],
                "location": cls["location"],
                "students": count,
                "identifier": identifier
            })

        return {
            "total_classes": total_classes,
            "total_students": total_students,
            "class_summaries": class_summaries
        }

    def display_instructor_summary(self, instructor_name):
        summary = self.get_instructor_summary(instructor_name)
        st.subheader("📊 Class Manager Summary")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Classes Taught", summary["total_classes"])
        with col2:
            st.metric("Total Student Sign-Ups", summary["total_students"])

        if summary["class_summaries"]:
            st.markdown("**Class-level enrollment**")
            for cls in summary["class_summaries"]:
                st.write(f"**{cls['class']}** ({cls['time']}) — {cls['students']} student(s)")
        else:
            st.info("Add classes in the Workouts tab to begin tracking your students.")

    def display_instructor_classes(self, instructor_name):
        instructor_classes = self.get_instructor_classes(instructor_name)
        st.subheader("👩‍🏫 Your Teaching Schedule")
        if instructor_classes:
            for cls in instructor_classes:
                with st.container():
                    col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
                    with col1:
                        emoji = {"Yoga": "🧘‍♀️", "Pilates": "🤸‍♀️", "Barre": "💃", "Cycle": "🚴‍♀️"}.get(cls["class"], "💪")
                        st.markdown(f"**{emoji} {cls['class']}**")
                    with col2:
                        st.caption(f"📍 {cls['location']}")
                    with col3:
                        st.caption(f"🕐 {cls['time']}")
                    with col4:
                        st.caption(f"👥 Instructor: {cls['instructor']}")
                    st.divider()
        else:
            st.info("📭 You are not assigned to any classes yet.")

    def display_sign_up(self):
        if self.classes:
            st.subheader("🎯 Sign Up for Classes")
            with st.form("signup_form"):
                selected_class = st.selectbox("Choose a class:", self.get_class_options())
                submitted = st.form_submit_button("📝 Sign Me Up!")
                if submitted:
                    username = st.session_state["logged_in_user"]
                    if self.user_manager.add_booking(username, selected_class):
                        st.session_state.registered_classes.append(selected_class)
                        st.success(f"✅ Successfully signed up for {selected_class}!")
                        st.rerun()
                    else:
                        st.warning("⚠️ You're already signed up for this class.")
        else:
            st.info("📭 No classes available for sign-up.")

    def display_registered_classes(self):
        st.subheader("📋 Your Registered Classes")
        if st.session_state.registered_classes:
            st.write("Manage your upcoming classes:")
            for i, cls in enumerate(st.session_state.registered_classes):
                with st.container():
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.write(f"🎯 {cls}")
                    with col2:
                        if st.button("❌ Cancel", key=f"cancel_{i}", help="Cancel this booking"):
                            username = st.session_state["logged_in_user"]
                            if self.user_manager.remove_booking(username, cls):
                                st.session_state.registered_classes.remove(cls)
                                st.success(f"✅ Cancelled {cls}")
                                st.rerun()
                            else:
                                st.error("❌ Failed to cancel booking")
        else:
            st.info("📭 You haven't signed up for any classes yet.")

    def display_instructor_crud(self):
        st.header("⚙️ Manage Workout Classes")

        # Add new class form
        with st.expander("➕ Add New Class", expanded=False):
            with st.form("add_class_form"):
                st.write("Enter class details:")
                col1, col2 = st.columns(2)
                with col1:
                    class_name = st.text_input("Class Name", placeholder="e.g., Yoga")
                    instructor = st.text_input("Instructor", placeholder="e.g., Mallory")
                with col2:
                    time = st.text_input("Time", placeholder="e.g., Monday 6 PM")
                    location = st.text_input("Location", placeholder="e.g., Studio A")

                submitted = st.form_submit_button("✅ Add Class")
                if submitted:
                    if class_name and instructor and time and location:
                        self.add_class(class_name, instructor, time, location)
                        st.success(f"✅ Class '{class_name}' added successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Please fill in all fields.")

        st.divider()

        # Display existing classes with edit/delete
        st.subheader("📝 Existing Classes")
        if self.classes:
            for i, cls in enumerate(self.classes):
                emoji = {"Yoga": "🧘‍♀️", "Pilates": "🤸‍♀️", "Barre": "💃", "Cycle": "🚴‍♀️"}.get(cls["class"], "💪")
                with st.expander(f"{emoji} {cls['class']} - {cls['time']}", expanded=False):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**👨‍🏫 Instructor:** {cls['instructor']}")
                        st.write(f"**📍 Location:** {cls['location']}")
                    with col2:
                        st.write("")  # spacing
                        if st.button("✏️ Edit", key=f"edit_{i}", help="Edit this class"):
                            st.session_state[f"edit_mode_{i}"] = True
                        if st.button("🗑️ Delete", key=f"delete_{i}", help="Delete this class"):
                            self.delete_class(i)
                            st.success(f"✅ Class '{cls['class']}' deleted!")
                            st.rerun()

                    # Edit form
                    if st.session_state.get(f"edit_mode_{i}", False):
                        st.divider()
                        with st.form(f"edit_form_{i}"):
                            st.write("Edit class details:")
                            col1, col2 = st.columns(2)
                            with col1:
                                edit_class = st.text_input("Class Name", value=cls["class"])
                                edit_instructor = st.text_input("Instructor", value=cls["instructor"])
                            with col2:
                                edit_time = st.text_input("Time", value=cls["time"])
                                edit_location = st.text_input("Location", value=cls["location"])

                            save = st.form_submit_button("💾 Save Changes")
                            cancel = st.form_submit_button("❌ Cancel")
                            if save:
                                self.edit_class(i, edit_class, edit_instructor, edit_time, edit_location)
                                st.success(f"✅ Class updated successfully!")
                                st.session_state[f"edit_mode_{i}"] = False
                                st.rerun()
                            if cancel:
                                st.session_state[f"edit_mode_{i}"] = False
                                st.rerun()
        else:
            st.info("📭 No classes to manage yet. Add your first class above!")

# FitnessChatbot class to handle AI-powered chatbot logic
class FitnessChatbot:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.system_prompt = "You are a helpful fitness assistant for the UD Fitness Club. Answer questions about workouts, instructors, events, and general fitness advice. Be friendly and informative."
        self.model = "gpt-4o-mini"
        self.max_tokens = 500
        self.temperature = 0.7
        
    def initialize_chat_history(self):
        """Initialize chat history with system message and greeting."""
        return [
            {"role": "system", "content": self.system_prompt},
            {"role": "assistant", "content": "Hi, how can I help you with your fitness questions?"}
        ]
    
    def process_question(self, user_question, chat_history):
        """Process user question and generate response from OpenAI API."""
        if not self.api_key:
            return "Error: OpenAI API key not configured."
        
        openai.api_key = self.api_key
        
        # Add user message to history
        chat_history.append({"role": "user", "content": user_question})
        
        try:
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=chat_history,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            ai_response = response.choices[0].message.content
        except Exception as e:
            ai_response = f"Sorry, I couldn't process your request right now. Error: {str(e)}"
        
        # Add assistant response to history
        chat_history.append({"role": "assistant", "content": ai_response})
        
        return ai_response
    
    def get_initial_message(self):
        """Get the initial greeting message."""
        return "Hi, how can I help you with your fitness questions?"
    
    def get_chat_history_messages(self, chat_history):
        """Filter out system messages for display."""
        return [msg for msg in chat_history if msg["role"] != "system"]
    
    def clear_history(self):
        """Return a fresh chat history."""
        return self.initialize_chat_history()

# Create WorkoutManager instance
workout_manager = WorkoutManager(user_manager)

# Create FitnessChatbot instance
try:
    api_key = st.secrets.get("OPENAI_API_KEY") if "OPENAI_API_KEY" in st.secrets else None
except:
    api_key = None
fitness_chatbot = FitnessChatbot(api_key=api_key)

# Reusable function for the sidebar
def display_sidebar():
    with st.sidebar:
        st.title("🏋️‍♀️ UD Fitness Club")

        st.header(f"👋 Welcome, {st.session_state['logged_in_user']}!")
        st.info(f"Role: {st.session_state['user_role']}")

        st.divider()

        # Quick stats
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Your Classes", len(st.session_state.get('registered_classes', [])))
        with col2:
            total_classes = len(workout_manager.classes)
            st.metric("Total Classes", total_classes)

        st.divider()

        # Navigation hints
        st.subheader("📋 Quick Access")
        if st.session_state["user_role"] == "Instructor":
            st.write("• Manage classes in Workouts tab")
            st.write("• View analytics in Home")
        else:
            st.write("• Browse classes in Workouts")
            st.write("• Check bookings in Profile")

        st.divider()

        # Logout button
        if st.button("🚪 Log Out", type="secondary"):
            st.session_state['page'] = "login"
            st.session_state["logged_in_user"] = None
            st.session_state["user_role"] = None
            st.rerun()

# Reusable function for instructor information section
def display_instructor_info():
    instructors = [
        {"name": "Mallory", "specialty": "Yoga", "experience": "5 years", "emoji": "🧘‍♀️"},
        {"name": "Annie", "specialty": "Pilates & Cycle", "experience": "7 years", "emoji": "🤸‍♀️"},
        {"name": "Sophia", "specialty": "Barre", "experience": "6 years", "emoji": "💃"}
    ]

    for instructor in instructors:
        st.markdown(f"**{instructor['emoji']} {instructor['name']}** - {instructor['specialty']} Instructor")
        st.caption(f"*{instructor['experience']} of experience*")
        st.write("")  # spacing

# Reusable function for events table
def display_events_table():
    events = [
        {"name": "Spring Fitness Challenge", "date": "April 15, 2026", "location": "UD Fitness Club", "emoji": "🌸"},
        {"name": "Nutrition Workshop", "date": "May 10, 2026", "location": "UD Fitness Club", "emoji": "🥗"},
        {"name": "Outdoor Bootcamp", "date": "June 5, 2026", "location": "Local Park", "emoji": "🏞️"},
        {"name": "Summer Merch Sale", "date": "July 1, 2026", "location": "UD Fitness Club", "emoji": "🛍️"},
        {"name": "Yoga Retreat", "date": "August 15, 2026", "location": "Mountain Retreat", "emoji": "🏔️"}
    ]

    for event in events:
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.write(f"{event['emoji']} **{event['name']}**")
        with col2:
            st.caption(event['date'])
        with col3:
            st.caption(event['location'])

# Reusable function for the Home page
def display_home_page():
    st.title("🏋️‍♀️ UD Fitness Club")
    st.markdown("### *Established March 2026*")
    st.write("Welcome to your premier fitness destination! Discover our group workout classes and achieve your fitness goals.")

    st.divider()

    # Metrics dashboard
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📅 Total Classes", len(workout_manager.classes))
    with col2:
        instructors = len(set(c["instructor"] for c in workout_manager.classes))
        st.metric("👨‍🏫 Instructors", instructors)
    with col3:
        st.metric("📍 Locations", len(set(c["location"] for c in workout_manager.classes)))
    with col4:
        user_bookings = len(st.session_state.get('registered_classes', []))
        st.metric("🎯 Your Bookings", user_bookings)

    st.divider()

    # Available Classes
    with st.container():
        # Show different class display based on user role
        if st.session_state.get("user_role") == "User":
            workout_manager.display_available_classes_calendar()
        else:
            st.subheader("💪 Available Classes")
            workout_manager.display_available_classes()

    st.divider()

    # Meet Our Instructors
    with st.container():
        st.subheader("👥 Meet Our Instructors")
        display_instructor_info()

    st.divider()

    # Events section
    with st.expander("📅 Upcoming Events", expanded=True):
        display_events_table()

# Reusable function for the chatbot
def display_chatbot():
    # Check for OpenAI API key
    try:
        has_api_key = "OPENAI_API_KEY" in st.secrets
    except:
        has_api_key = False
    
    if not has_api_key:
        st.error("OpenAI API key not found in secrets. Please add it to enable the chatbot.")
        return

    # Ensure chat history exists when the app first loads
    if "messages" not in st.session_state:
        st.session_state["messages"] = fitness_chatbot.initialize_chat_history()

    # Display chat history by looping through messages (excluding system messages)
    display_messages = fitness_chatbot.get_chat_history_messages(st.session_state["messages"])
    for msg in display_messages:
        st.chat_message(msg["role"]).write(msg["content"])

    user_input = st.chat_input("Ask a fitness-related question")

    if user_input:
        with st.spinner("Thinking..."):
            # Process the question and get AI response
            fitness_chatbot.process_question(user_input, st.session_state["messages"])
            st.rerun()

    st.divider()
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🗑️ Clear Chat", key="clear_chat_btn", help="Start a new conversation"):
            st.session_state["messages"] = fitness_chatbot.clear_history()
            st.success("💬 Chat cleared!")
            st.rerun()

# Reusable function for the workout schedule section
def display_workout_schedule():
    workout_manager.display_schedule_with_signup()
    workout_manager.display_registered_classes()

# Reusable function for the user profile section
def display_user_profile():
    st.header(":blue[My Profile]")
    st.divider()

    username = st.session_state["logged_in_user"]

    # -------- ACCOUNT INFO --------
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("👤 Account Information")
        st.write(f"**Username:** {username}")
        st.write(f"**Account Type:** {st.session_state['user_role']}")

    # -------- UPDATE PASSWORD --------
    with col2:
        st.subheader("🔐 Update Password")

        new_password = st.text_input("New Password", type="password", key="profile_pass")

        if st.button("Update Password"):
            if not new_password:
                st.warning("Please enter a new password")
            else:
                # Find user and update password
                for user in user_manager.users:
                    if user["username"] == username:
                        user["password"] = new_password
                        user_manager.save_users()
                        st.success("✅ Password updated successfully!")
                        break

    # -------- BOOKING HISTORY --------
    st.divider()
    st.subheader("📅 My Bookings")

    # Get user's bookings from UserManager
    user_bookings = user_manager.get_user_bookings(username)

    if len(user_bookings) == 0:
        st.info("ℹ️ No bookings yet. Browse available classes to book!")
    else:
        for class_name in user_bookings:
            # Find class details
            class_info = None
            for cls in workout_manager.classes:
                if cls["class"] == class_name:
                    class_info = cls
                    break
            
            col1, col2 = st.columns([3, 1])

            with col1:
                if class_info:
                    st.write(f"**{class_info['class']}** | {class_info['time']} | {class_info['location']}")
                else:
                    st.write(f"**{class_name}**")

            with col2:
                if st.button("❌ Cancel", key=f"cancel_{class_name}"):
                    user_manager.remove_booking(username, class_name)
                    st.success("✅ Booking cancelled")
                    st.rerun()


def display_instructor_profile():
    username = st.session_state["logged_in_user"]
    profile = user_manager.get_user_profile(username) or {}

    st.header(":blue[Instructor Profile]")
    st.divider()

    # -------- ACCOUNT INFO --------
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("👤 Profile Details")
        st.write(f"**Username:** {username}")
        st.write(f"**Role:** {st.session_state['user_role']}")
        st.write(f"**Email:** {profile.get('email', '') or 'Not set'}")
        st.write(f"**Display Name:** {profile.get('display_name', '') or username}")

    # -------- PROFILE EDIT --------
    with col2:
        st.subheader("✏️ Edit Profile")
        display_name = st.text_input("Display Name", value=profile.get("display_name", username), key="instr_display_name")
        email = st.text_input("Email", value=profile.get("email", ""), key="instr_email")
        bio = st.text_area("Bio", value=profile.get("bio", ""), key="instr_bio")

        if st.button("💾 Save Profile", key="instr_save_profile"):
            if user_manager.update_profile(username, display_name, email, bio):
                st.success("✅ Instructor profile updated successfully!")
            else:
                st.error("❌ Unable to update profile")

    st.divider()

    # -------- CLASSES AND STATS --------
    st.subheader("📊 Teaching Summary")
    workout_manager.display_instructor_summary(username)
    st.divider()
    st.subheader("👩‍🏫 Classes You Teach")
    workout_manager.display_instructor_classes(username)

#login page for users to log in as either a user or an instructor, the login credentials will be checked against the information stored in the json file and if the credentials are correct, the user will be logged in and taken to the main page of the app
if st.session_state["page"] == "login":
    st.title("🏋️‍♀️ UD Fitness Club")
    st.header("🔐 Welcome Back!")

    with st.container():
        st.subheader("👤 Log In")
        with st.form("login_form"):
            username = st.text_input("👤 Username", placeholder="Enter your username")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
            role_choice = st.radio("Login as", ["User", "Teacher"], index=0)
            login_submitted = st.form_submit_button("🚀 Log In")

            if login_submitted:
                expected_role = "Instructor" if role_choice == "Teacher" else "User"
                user_type = user_manager.login(username, password)
                if user_type == expected_role:
                    st.session_state["logged_in_user"] = username
                    st.session_state["user_role"] = user_type
                    st.session_state.registered_classes = user_manager.get_user_bookings(username)
                    st.success(f"✅ Welcome back, {username}!")
                    st.session_state['page'] = "main"
                    st.rerun()
                elif user_type and user_type != expected_role:
                    st.error(f"❌ Account exists as {user_type}, please choose the correct role.")
                else:
                    st.error("❌ Invalid username or password")

    st.divider()

    #sign up options for users to create an account as either a user or an instructor, the sign up information will be saved in the json file and the user will be logged in and taken to the main page of the app
    with st.container():
        st.subheader("✨ Create Account")
        st.write("Join our fitness community!")

        with st.form("signup_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_username = st.text_input("👤 Username", key="signup_username", placeholder="Choose a username")
                selected_role = st.selectbox("🎭 Account Type", ["User", "Teacher"], key="signup_user_type")
            with col2:
                new_password = st.text_input("🔒 Password", type="password", key="signup_password", placeholder="Create a password")

            signup_submitted = st.form_submit_button("🎉 Sign Up")

            if signup_submitted:
                new_user_type = "Instructor" if selected_role == "Teacher" else "User"
                if user_manager.signup(new_username, new_password, new_user_type):
                    st.session_state["logged_in_user"] = new_username
                    st.session_state["user_role"] = new_user_type
                    st.session_state.registered_classes = user_manager.get_user_bookings(new_username)
                    st.success(f"🎊 Account created successfully! Welcome, {new_username}!")
                    st.session_state['page'] = "main"
                    st.rerun()
                else:
                    st.error("❌ Username already exists. Please choose a different one.")
else:
    display_sidebar()

    #sending to either user or instructor page/interface based on the user role stored in the session state 
    if st.session_state["user_role"] == "Instructor":
        #instructor view 
        #tabs!
        tab1, tab2, tab3 = st.tabs(["Home", "Workouts", "Profile"])
        with tab1:
            display_home_page()
            workout_manager.display_instructor_summary(st.session_state["logged_in_user"])
            workout_manager.display_instructor_classes(st.session_state["logged_in_user"])
            display_chatbot()
        with tab2:
            workout_manager.display_instructor_crud()
        with tab3:
            display_instructor_profile()
    else:
        #user view 
        #tabs again
        tab1, tab2, tab3 = st.tabs(["Home", "Workouts", "Profile"])
        with tab1:
            display_home_page()
            display_chatbot()
        with tab2:
            display_workout_schedule() 
        with tab3:
            display_user_profile()
