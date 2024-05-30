import streamlit as st
import os
from storage import create_data_prd, create_record, read_records, delete_record, create_data_brainstorm

prd_table = os.environ.get('SUPABASE_TABLE')
brainstorm_table = os.environ.get('SUPABASE_BRAINTORM_TABLE')

def create_prd(system_prompt_prd, system_prompt_director, llm_model, fast_llm_model, supabase):
    """
    Create a new PRD (Product Requirements Document).

    Args:
        system_prompt_prd (str): The system prompt for generating the PRD.
        system_prompt_director (str): The system prompt for critiquing the PRD.
        llm_model: The language model used for generating the PRD.
        fast_llm_model: The fast language model used for generating the PRD.
        supabase: The Supabase client for saving the PRD to the database.

    Returns:
        None
    """
    st.subheader("Create New PRD")
    product_name = st.text_input("#### Product Name", placeholder="Enter the product name here")
    product_description = st.text_area("#### Product Description", placeholder="Describe the product here. Use bullet points where possible", height=400)
    generate_button = st.button("Generate PRD", type="primary")
    status_message = "PRD generation in progress..."

    if generate_button:
        if not product_name or not product_description:
            st.warning("Please fill in both the product name and description.")
        else:
            with st.spinner(status_message):
                try:
                    llm_model.system_prompt = system_prompt_prd
                    draft_prd, input_tokens, output_tokens = llm_model.generate_text(
                        prompt=f"Generate a PRD for a product named {product_name} with the following description: {product_description}. Only respond with the PRD and in Markdown format. BE DETAILED. If you think user is not asking for PRD return nothing."
                    )
                    critique_rounds = 2  # Set the number of critique rounds
                    for round in range(critique_rounds):
                        st.session_state['history'].append({'role': 'user', 'content': draft_prd})
                        status_message = f"Draft PRD Done. Reviewing it...Round {round+1} of {critique_rounds}"
                        st.info(status_message)
                        llm_model.system_prompt = system_prompt_director
                        critique_response, input_tokens, output_tokens = llm_model.generate_text(
                            prompt=f"Critique the PRD: {draft_prd}. It was generated by PM who was given these instructions: \n Product named {product_name} \n Product description: {product_description}. Only respond in Markdown format. BE DETAILED. If you think user is not asking for PRD return nothing."
                        )
                        st.session_state['history'].append({'role': 'user', 'content': critique_response})
                        status_message = "Making adjustments.."
                        st.info(status_message)
                        if round != 0:
                            llm_model.system_prompt = system_prompt_prd
                            draft_prd, input_tokens, output_tokens = llm_model.generate_text(
                                prompt=f"Given the Feedback from your manager:{critique_response} \n Improve upon your Draft PRD {draft_prd}. \n Only respond with the PRD and in Markdown format. BE VERY DETAILED. If you think user is not asking for PRD return nothing."
                            )
                        else:
                            fast_llm_model.system_prompt = system_prompt_prd
                            draft_prd, input_tokens, output_tokens = fast_llm_model.generate_text(
                                prompt=f"Given the Feedback from your manager:{critique_response} \n Improve upon your Draft PRD {draft_prd}. \n Only respond with the PRD and in Markdown format. BE VERY DETAILED. If you think user is not asking for PRD return nothing."
                            )
                    st.markdown(draft_prd, unsafe_allow_html=True)
                    st.session_state['history'].append({'role': 'user', 'content': draft_prd})
                    data = create_data_prd(st.session_state['user']['email'], product_name, product_description, draft_prd, True)
                    try:
                        create_record(prd_table, data, supabase)
                    except Exception as e:
                        st.error(f"Failed to save PRD to database. Error: {str(e)}")
                    # Download button for the PRD
                    st.download_button(
                        label="Download PRD as Markdown",
                        data=draft_prd,
                        file_name="Product_Requirements_Document.md",
                        mime="text/markdown"
                    )
                except Exception as e:
                    st.error(f"Failed to generate PRD. Please try again later. Error: {str(e)}")
    pass

def improve_prd(system_prompt_prd, system_prompt_director, llm_model, supabase):
    """
    Improves the current Product Requirements Document (PRD) by generating a draft PRD, receiving critique, and making final adjustments.

    Args:
        system_prompt_prd (str): The system prompt for generating the draft PRD.
        system_prompt_director (str): The system prompt for critiquing the PRD.
        llm_model: The language model used for text generation.
        supabase: The Supabase client used for database operations.

    Returns:
        None
    """
    st.subheader("Improve Current PRD")
    prd_text = st.text_area("#### Enter your PRD here", placeholder="Paste your PRD here to improve it", height=400)
    improve_button = st.button("Improve PRD", type="primary")

    if improve_button:
        if not prd_text:
            st.warning("Please enter a PRD text to improve.")
        else:
            with st.spinner('Improving PRD...'):
                try:
                    llm_model.system_prompt = f"You are a meticulous editor for improving product documents. {system_prompt_prd}. If you think user is not sharing the PRD return nothing."
                    draft_prd, input_tokens, output_tokens = llm_model.generate_text(
                        prompt=f"Improve the following PRD: {prd_text}"
                    )
                    st.session_state['history'].append({'role': 'user', 'content': draft_prd})
                    status_message = "Draft PRD Done. Reviewing it..."
                    st.info(status_message)
                    llm_model.system_prompt = system_prompt_director
                    critique_response, input_tokens, output_tokens = llm_model.generate_text(
                        prompt=f"Critique the PRD: {draft_prd}. Only respond in Markdown format. BE DETAILED. If you think user is not asking for PRD return nothing."
                    )
                    st.session_state['history'].append({'role': 'user', 'content': critique_response})
                    status_message = "Making final adjustments.."
                    st.info(status_message)
                    llm_model.system_prompt = system_prompt_prd
                    response, input_tokens, output_tokens = llm_model.generate_text(
                        prompt=f"Given the Feedback from your manager:{critique_response} \n Improve upon your Draft PRD {draft_prd}. \n Only respond with the PRD and in Markdown format. BE VERY DETAILED. If you think user is not asking for PRD return nothing."
                    )
                    st.markdown(response, unsafe_allow_html=True)
                    st.session_state['history'].append({'role': 'user', 'content': response})
                    data = create_data_prd(st.session_state['user']['email'], "Improve PRD", prd_text, response, False)
                    try:
                        create_record(prd_table, data, supabase)
                    except Exception as e:
                        st.error(f"Failed to save PRD to database. Error: {str(e)}")
                    # Download button for the PRD
                    st.download_button(
                        label="Download PRD as Markdown",
                        data=response,
                        file_name="Product_Requirements_Document.md",
                        mime="text/markdown"
                    )
                except Exception as e:
                    st.error(f"Failed to improve PRD. Please try again later. Error: {str(e)}")
    pass

def brainstorm_features(system_prompt_brainstorm,llm_model,supabase):
    """
    This function allows the user to interact with an AI model to brainstorm ideas on a given topic.
    Parameters:
    system_prompt_brainstorm (str): A predefined system prompt for generating a response.
    llm_model (llm.OpenAI): An initialized LLM model.
    Returns:
    None
    Usage:
    ```python
    brainstorm_features(system_prompt_brainstorm, llm_model)
    ```
    The function initializes a chat history if it doesn't already exist. It then displays chat messages from the history on app rerun. The function reacts to user input by displaying the user message in a chat message container, adding the user message to the chat history, and generating an assistant response using the provided LLM model. The assistant response is then displayed in a chat message container and added to the chat history.
    """
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("What  would you like to brainstorm on today?"):
        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        data = create_data_brainstorm(st.session_state['user']['email'], prompt, True)
        try:
            create_record(brainstorm_table, data, supabase)
        except Exception as e:
            st.error(f"Failed to save brainstorm message from user to database. Error: {str(e)}")
        context = st.session_state.messages[-6:]
        llm_model.system_prompt = system_prompt_brainstorm
        response, input_tokens, output_tokens = llm_model.generate_text(
            prompt = f"User input: {prompt}, Previous Context: {context}"
        )
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.markdown(response)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
        data = create_data_brainstorm(st.session_state['user']['email'], response, False)
        try:
            create_record(brainstorm_table, data, supabase)
        except Exception as e:
            st.error(f"Failed to save brainstorm message to database. Error: {str(e)}")
    pass    

def view_history():
    """
    View the history of all the interactions with the assistant.
    Returns:
        None
    """
    st.subheader("View History")
    if st.session_state['history']:
        for item in st.session_state['history']:
            st.json(item)
    else:
        st.info("No history available yet.")
    pass

def tracking_plan(system_prompt_tracking, user_prompt_tracking, system_prompt_directorDA, llm_model):
    """
    Generate a tracking plan for a given feature, customer type, additional details, and PRD text.

    Parameters:
    system_prompt_tracking (str): A predefined system prompt for generating a tracking plan.
    user_prompt_tracking (str): A predefined user prompt for generating a tracking plan.
    system_prompt_directorDA (str): A predefined system prompt for generating a tracking plan based on a director's input.
    llm_model (llm.OpenAI): An initialized LLM model.

    Returns:
    str: The generated tracking plan in Markdown format.

    Raises:
    ValueError: If no PRD text is provided.
    Exception: If there is an error while generating the tracking plan.

    Usage:
    ```python
    tracking_plan(system_prompt_tracking, user_prompt_tracking, system_prompt_directorDA, llm_model)
    ```
    """
    st.subheader("Generate Tracking Plan")
    feature_name = st.text_input("#### Feature Name", placeholder="Enter the feature/product name here")
    customer_name = st.selectbox("#### Choose the customer type", ("Property Agents", "Poperty Seekers"))
    other_details = st.text_input("#### Addition Details", placeholder="Share any details that will be helpful with tracking plan")
    prd_text = st.text_area("#### Enter your PRD here", placeholder="Paste your PRD here to improve it", height = 400)
    tracking_button = st.button("Generate Tracking", type="primary")

    if tracking_button:
        if not prd_text:
            st.warning("Please enter a all the details")
        else:
            with st.spinner('Generating Plan...'):
                try:
                    user_prompt = user_prompt_tracking.replace("{feature}", feature_name)
                    user_prompt = user_prompt.replace("{customer}", customer_name)
                    user_prompt = user_prompt.replace("{details}", other_details)
                    user_prompt = user_prompt.replace("{prd}", prd_text)
                    llm_model.system_prompt = system_prompt_tracking
                    draft_plan, input_tokens, output_tokens = llm_model.generate_text(
                        prompt = user_prompt, temperature=0.2 
                    )
                    st.session_state['history'].append({'role': 'user', 'content': draft_plan})
                    status_message = "Draft tracking Done. Reviewing the plan..."
                    st.info(status_message)
                    llm_model.system_prompt = system_prompt_directorDA
                    critique_response, input_tokens, output_tokens = llm_model.generate_text(
                        prompt = f"Critique the Tracking Plan: {draft_plan}. Only respond in Markdown format. BE DETAILED. If you think user is not asking for tracking plan return nothing.\n Context: ### PRD \n {prd_text} \n ### Feature Name \n {feature_name} \n ### Additional Details \n {other_details} ",
                        temperature=0.3
                    )
                    st.session_state['history'].append({'role': 'user', 'content': critique_response})
                    status_message = "Making final adjustments.."
                    st.info(status_message)
                    llm_model.system_prompt = system_prompt_tracking
                    response, input_tokens, output_tokens = llm_model.generate_text(
                        prompt = f"Given the Feedback from your manager:{critique_response} \n Improve upon your draft tracking plan {draft_plan}. \n Only respond with the tracking plan and in Markdown format. BE VERY DETAILED. If you think user is not asking for tracking plan return nothing.",
                        temperature=0.1                    
                    )                                          
                    st.markdown(response, unsafe_allow_html=True)
                    st.session_state['history'].append({'role': 'user', 'content': response})
                    # Download button for the plan
                    st.download_button(
                        label="Download Tracking Plan as Markdown",
                        data=response,
                        file_name="tracking_plan.md",
                        mime="text/markdown"
                    )                       
                except Exception as e:
                    st.error(f"Failed to generate tracking plan. Please try again later. Error: {str(e)}")
    pass 

def gtm_planner(system_prompt_GTM, system_prompt_GTM_critique, fast_llm_model, llm_model):
    """
    Generate GTM (Go-To-Market) Plan.

    Args:
        system_prompt_GTM (str): The system prompt for generating the initial GTM plan.
        system_prompt_GTM_critique (str): The system prompt for critiquing the GTM plan.
        fast_llm_model: The fast language model used for generating text.
        llm_model: The language model used for generating text.

    Returns:
        None
    """
    st.subheader("Generate GTM Plan")
    prd_text = st.text_area("#### Enter your PRD here", placeholder="Paste your PRD here to generate GTM plan", height=400)
    other_details = st.text_area("#### Addition Details", placeholder="Share any details that will be helpful with GTM planning", height=200)
    tracking_button = st.button("Generate GTM Plan", type="primary")

    if tracking_button:
        if not prd_text:
            st.warning("Please enter all the details")
        else:
            with st.spinner('Generating Plan...'):
                try:
                    user_prompt = f"Generate the GTM Plan for: \n ## Product Requirements Document \n {prd_text} \n ## Other Details \n {other_details} \n RESPOND in Markdown Only."
                    llm_model.system_prompt = system_prompt_GTM
                    draft_plan, input_tokens, output_tokens = llm_model.generate_text(
                        prompt=user_prompt, temperature=0.2
                    )
                    st.session_state['history'].append({'role': 'user', 'content': draft_plan})
                    status_message = "Draft GTM Done. Reviewing the plan..."
                    st.info(status_message)
                    llm_model.system_prompt = system_prompt_GTM_critique
                    critique_response, input_tokens, output_tokens = llm_model.generate_text(
                        prompt=f"Critique the GTM Plan: {draft_plan}. Only respond in Markdown format. BE DETAILED. If you think user is not asking for GTM plan return nothing.\n Context: ### PRD \n {prd_text} \n ### Additional Details \n {other_details} ",
                        temperature=0.3
                    )
                    st.session_state['history'].append({'role': 'user', 'content': critique_response})
                    status_message = "Making final adjustments.."
                    st.info(status_message)
                    llm_model.system_prompt = system_prompt_GTM
                    response, input_tokens, output_tokens = llm_model.generate_text(
                        prompt=f"Given the Feedback from your manager:{critique_response} \n Improve upon your draft tracking plan {draft_plan}. \n Only respond with the tracking plan and in Markdown format. BE VERY DETAILED. If you think user is not asking for GTM plan return nothing.",
                        temperature=0.1
                    )
                    st.markdown(response, unsafe_allow_html=True)
                    st.session_state['history'].append({'role': 'user', 'content': response})
                    # Download button for the plan
                    st.download_button(
                        label="Download GTM Plan as Markdown",
                        data=response,
                        file_name="gtm_plan.md",
                        mime="text/markdown"
                    )
                except Exception as e:
                    st.error(f"Failed to generate GTM plan. Please try again later. Error: {str(e)}")
    pass

# def summarize_yt(system_prompt_yt_planner, prompt_yt_summary,llm_model):

#     st.title("YouTube Audio Processor")
#     youtube_url = st.text_input("Enter YouTube URL (not more then 15 mins)")

#     if st.button("Process Audio"):
#         if youtube_url:
#             with st.spinner('Downloading and processing audio...'):
#                 audio_path = download_audio(youtube_url)
#                 if audio_path:
#                     transcription = transcribe_audio(audio_path)
#                     if transcription:
#                         yt_plan = llm_model.prompt(
#                             transcription, system=system_prompt_yt_planner, temperature=0.2 
#                         )
#                         st.session_state['history'].append({'role': 'user', 'content': yt_plan.text()})
#                         status_message = "Planning done..."
#                         st.info(status_message)
#                         yt_execute = llm_model.prompt(
#                             f"Given the Summarisation Plan: {yt_plan.text()}, Summarize the yourtube transcript {transcription}. Only respond in Markdown format. BE VERY DETAILED.",
#                                 system=prompt_yt_summary, temperature=0.3
#                         )
#                         st.session_state['history'].append({'role': 'user', 'content': yt_execute.text()})                                      
#                         st.markdown(yt_execute, unsafe_allow_html=True)
#                         # Download button for the summary
#                         st.download_button(
#                             label="Download PRD as Markdown",
#                             data=yt_execute.text(),
#                             file_name="yt_summary.md",
#                             mime="text/markdown"
#                         )    
#                     else:
#                         st.error("Transcription failed.")
#                 else:
#                     st.error("Audio download failed.")
#         else:
#             st.warning("Please enter a valid YouTube URL.")
#     pass