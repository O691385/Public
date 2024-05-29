import streamlit as st
#from dotenv import load_dotenv
# import llm
import os
from authentication import authenticate , auth_screen 
from features import create_prd, improve_prd, brainstorm_features, view_history, tracking_plan, gtm_planner
from utils import load_prompts
from models import build_models
from supabase import create_client, Client



#load_dotenv()

SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
# Using Streamlit's session state to store temporary memory
if 'history' not in st.session_state:
    st.session_state['history'] = []

def main():
    """
    Main function that serves as the entry point of the program.
    
    This function loads prompts, builds models, and presents a menu of options to the user based on their selection.
    The user can choose to create a PRD, improve a PRD, brainstorm features, create a tracking plan, create a GTM plan, or view history.
    Each option calls a specific function to perform the corresponding task.
    """
    prompts = load_prompts()
    fast_llm, quality_llm = build_models()
    system_prompt_prd = prompts['system_prompt_prd']
    system_prompt_director = prompts['system_prompt_director']
    system_prompt_brainstorm = prompts['system_prompt_brainstorm']
    system_prompt_tracking = prompts['system_prompt_tracking']
    user_prompt_tracking = prompts['prompt_tracking_plan']
    system_prompt_directorDA = prompts['system_prompt_directorDA']
    system_prompt_yt_planner = prompts['system_prompt_yt_planner']
    prompt_yt_summary = prompts['prompt_yt_summary']
    system_prompt_GTM = prompts['system_prompt_GTM']
    system_prompt_GTM_critique = prompts['system_prompt_GTM_critique']
    # Authenticate the user
    # authenticate()
    st.set_page_config(
    page_title="PM Toolkit",
    page_icon="🧊",
    layout="wide",
    )
    auth_screen(supabase)
    # if st.session_state['authenticated']:
    if st.session_state['logged_in']:
        st.sidebar.title("Select the Task:")
        option = st.sidebar.selectbox("### Choose a feature", ("Create PRD", "Improve PRD","Brainstorm Features", "Tracking Plan","Create GTM Plan","View History"))
        if option == "Create PRD":
            create_prd(system_prompt_prd,system_prompt_director, quality_llm, fast_llm,supabase)
        elif option == "Improve PRD":
            improve_prd(system_prompt_prd,system_prompt_director,quality_llm,supabase)
        elif option == "Brainstorm Features":
            brainstorm_features(system_prompt_brainstorm,quality_llm)
        elif option == "Tracking Plan":
            tracking_plan(system_prompt_tracking, user_prompt_tracking, system_prompt_directorDA, quality_llm)
        elif option == "Create GTM Plan":
            gtm_planner(system_prompt_GTM,system_prompt_GTM_critique, fast_llm, quality_llm)
        elif option == "View History":
            view_history()

if __name__ == "__main__":
    main()
