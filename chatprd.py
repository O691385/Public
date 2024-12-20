import streamlit as st 
st.set_page_config(
    page_title="PM Toolkit",
    page_icon="🥊",
    layout="wide",
    )

# import llm
from features.prd import create_prd, improve_prd
from features.view_history import view_history
from features.brainstorm import brainstorm_features
from features.tracking import tracking_plan
from features.gtm import gtm_planner
from features.ab_test import abc_test_significance
from features.test_duration import ab_test_duration_calculator
from utils.models import build_models
from utils.data_loading import load_prompts
from storage.supabase_client import create_client
import os
from supabase import create_client, Client
from utils.authentication import auth_screen 

#from dotenv import load_dotenv
#load_dotenv()

SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
#res = supabase.auth.get_session()
# Using Streamlit's session state to store temporary memory

def main():
    """
    Main function that serves as the entry point of the Streamlit application.

    This function performs the following tasks:
    1. Loads system prompts from a JSON file.
    2. Builds language models (Claude and GPT-4) using the utility function `build_models`.
    3. Sets up system prompts for various tasks such as PRD creation, brainstorming, tracking plans, GTM plans, and A/B testing.
    4. Authenticates the user using Supabase.
    5. Displays a sidebar menu for the user to select a task.
    6. Calls the appropriate function based on the user's selection:
       - "Create PRD": Calls `create_prd` to generate a new Product Requirements Document.
       - "Improve PRD": Calls `improve_prd` to enhance an existing PRD.
       - "Brainstorm Features": Calls `brainstorm_features` for feature brainstorming.
       - "Tracking Plan": Calls `tracking_plan` to generate a tracking plan.
       - "Create GTM Plan": Calls `gtm_planner` to develop a Go-To-Market plan.
       - "A/B Test Significance": Calls `abc_test_significance` to analyze A/B test results.
       - "A/B Test Duration Calculator": Calls `ab_test_duration_calculator` to calculate the duration needed for an A/B test.
       - "View History": Calls `view_history` to access and review previously generated PRDs and plans.

    The function also initializes Streamlit's session state to store temporary memory and ensures that the user is authenticated before accessing the toolkit features.
    """
   
    prompts = load_prompts()
    claude_llm, gpt4_llm = build_models()
    system_prompt_prd_experimental = prompts['system_prompt_prd_experimental']
    system_prompt_director = prompts['system_prompt_director']
    system_prompt_brainstorm = prompts['system_prompt_brainstorm']
    system_prompt_tracking = prompts['system_prompt_tracking']
    user_prompt_tracking = prompts['prompt_tracking_plan']
    system_prompt_directorDA = prompts['system_prompt_directorDA']
    system_prompt_GTM = prompts['system_prompt_GTM']
    system_prompt_GTM_critique = prompts['system_prompt_GTM_critique']
    system_prompt_ab_test = prompts['system_prompt_ab_test']
    # Authenticate the user
    # authenticate()
    if 'history' not in st.session_state:
        st.session_state['history'] = []
    auth_screen(supabase)
    # if st.session_state['authenticated']:
    if st.session_state['logged_in']:
        option = st.sidebar.radio(
            "# Select the Task 👉",
            key="task",
            options=[
                "Create PRD", 
                "Improve PRD",
                "Brainstorm Features", 
                "Tracking Plan",
                "Create GTM Plan",
                "A/B Test Significance",
                "A/B Test Duration Calculator",
                "View History"
            ],
        )
        
        # Function calls based on user selection
        if option == "Create PRD":
            create_prd(
                system_prompt_prd_experimental,
                system_prompt_director,
                claude_llm,
                gpt4_llm,
                supabase
            )
        elif option == "Improve PRD":
            improve_prd(
                system_prompt_prd_experimental,
                system_prompt_director,
                claude_llm,
                supabase
            )
        elif option == "Brainstorm Features":
            brainstorm_features(system_prompt_brainstorm, gpt4_llm, supabase)
        elif option == "Tracking Plan":
            tracking_plan(
                system_prompt_tracking,
                user_prompt_tracking,
                system_prompt_directorDA,
                claude_llm,
                gpt4_llm,
                supabase
            )
        elif option == "Create GTM Plan":
            gtm_planner(
                system_prompt_GTM,
                system_prompt_GTM_critique,
                gpt4_llm,
                claude_llm
            )
        elif option == "A/B Test Significance":
            abc_test_significance(claude_llm, system_prompt_ab_test)
        elif option == "A/B Test Duration Calculator":
            ab_test_duration_calculator()
        elif option == "View History":
            view_history(supabase)

if __name__ == "__main__":
    main()
