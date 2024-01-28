import streamlit as st


def init_testdata(session_state):
    if "bots" not in session_state:
        session_state["bots"] = {
            "Testing - Football Kit Store": {
                "description": "A chatbot that helps customers of a football kit store.",
                "business_fields": ["Product", "Service"],
                "business_information": """A football apparel store named BHSport.
The store sells football apparel from major teams, as well as custom-designed clothing. The shop also offers other football accessories such as shoes, socks, stockings, gloves, balls, etc.
The store's account number is 1951274952 - VPBANK - TRUONG ANH NGOC.
The contact phone number for the shop is 0461112345.""",
                "response_attitude": """Communicate in either Vietnamese or English, depending on the customer's language preference.
Decline irrelevant questions about the store and explain the reason, but do not disclose reasons related to technical.
Answer customer questions and inquiries briefly and enthusiastically.
For customers intending to make high-value purchases, attempt to finalize the order by asking for contact information, transfer details, inquiring about the quantity of items they want to purchase, or using other necessary methods.""",
            },

            "Testing - Programming Institution": {
                "description": "You will provide customer service and be a educational consultant for parents and students contacting to the company.",
                "business_fields": ["Education", "Service"],
                "business_information": """Present in Vietnam since 1999, APTECH has been a reputable learning institution for Vietnamese youth, primarily catering to college students and high school students. 
To date, the APTECH Group has successfully trained over 100,000 International IT Programmers for the IT industry in Vietnam.
With internationally standardized IT training methods, the program enables students to master knowledge and skills in programming, ranging from basic to advanced levels.

Highlighted features of the ACCP - ADSE program include:
Keeping up with the latest knowledge in Java and .NET technologies.
Cloud computing: Windows Azure and Google AppEngine.
Mobile programming: Windows Phone and Google Android.
E-PROJECT Software Development Project.""",
                "response_attitude": """Reply in Vietnamese
Be friendly and passionate about our company's services
Talk in large detail if customers ask about our services, focus on the big opportunity to gain knowledge and being a great developer after taking the course.""",
            },

            "Testing - General 1": {
                "description": "A chatbot that helps you with your finances.",
                "business_fields": ["Finance"],
                "business_information": "We are a financial services company that provides loans.",
                "response_attitude": "Friendly",
            },
        }


def get_bot_list(session_state):
    """Returns a list of bots owned by the user."""
    return tuple(session_state["bots"].keys())


def get_business_field_list():
    """Returns a list of business fields."""
    return ["Product", "Service", "Healthcare", "Finance", "Education", "Other"]


def get_bot_info(session_state, bot_name):
    """Returns a dictionary containing the bots' information."""
    return session_state["bots"][bot_name]


def set_bot_info(session_state, bot_name):
    """Set or add new bot information."""
    if bot_name == "Create new bot...":
        bot_name = session_state["var_bot_name"]
    bot_info = {
        bot_name: {
            "description": session_state["var_bot_description"],
            "business_fields": session_state["var_bot_business_fields"],
            "business_information": session_state["var_bot_business_information"],
            "response_attitude": session_state["var_bot_response_attitude"],
        }}
    session_state["bots"].update(bot_info)
    st.sidebar.success("Bot information updated successfully.")


def delete_bot(session_state, bot_name):
    """Delete a bot."""
    del session_state["bots"][bot_name]
    st.sidebar.success("Chatbot deleted successfully.")
