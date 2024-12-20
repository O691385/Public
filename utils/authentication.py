import streamlit as st
import os
import re
import jwt
from datetime import datetime, timedelta

SECRET_KEY = os.environ.get('SECRET_KEY')

# ... (other functions: is_valid_email, generate_jwt, verify_jwt remain unchanged) ...

def set_auth_cookie(token):
    # Existing code for this function
    st.session_state.auth_token = token
    js_code = f"""
    <script>
    function setCookie(name, value, days) {{
        var expires = "";
        if (days) {{
            var date = new Date();
            date.setTime(date.getTime() + (days*24*60*60*1000));
            expires = "; expires=" + date.toUTCString();
        }}
        document.cookie = name + "=" + (value || "")  + expires + "; path=/";
    }}
    setCookie('auth_token', '{token}', 30);
    </script>
    """
    st.components.v1.html(js_code, height=0)

def get_auth_cookie():
    # Existing code for this function
    if 'auth_token' not in st.session_state:
        js_code = """
        <script>
        function getCookie(name) {
            var nameEQ = name + "=";
            var ca = document.cookie.split(';');
            for(var i=0;i < ca.length;i++) {
                var c = ca[i];
                while (c.charAt(0)==' ') c = c.substring(1,c.length);
                if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
            }
            return null;
        }
        var auth_token = getCookie('auth_token');
        if (auth_token) {
            window.parent.postMessage({type: 'SET_COOKIE', cookie: auth_token}, '*');
        }
        </script>
        """
        st.components.v1.html(js_code, height=0)
        
        # JavaScript to send the cookie value to session state
        st.components.v1.html(
            """
            <script>
            window.addEventListener('message', function(event) {
                if (event.data.type === 'SET_COOKIE') {
                    window.parent.Streamlit.setComponentValue(event.data.cookie);
                }
            }, false);
            </script>
            """,
            height=0
        )
    
    return st.session_state.get('auth_token')

def clear_auth_cookie():
    # Existing code for this function
    if 'auth_token' in st.session_state:
        del st.session_state.auth_token
    js_code = """
    <script>
    function deleteCookie(name) {
        document.cookie = name +'=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;';
    }
    deleteCookie('auth_token');
    </script>
    """
    st.components.v1.html(js_code, height=0)

def authenticate_user(email, password, supabase):
    # Bypassing actual authentication
    user_email = "guest@example.com"  # Default email for guest access
    token = generate_jwt(user_email)
    set_auth_cookie(token)
    st.session_state['logged_in'] = True
    st.session_state['user'] = {"email": user_email}
    st.success(f"Welcome {user_email}")
    st.rerun()

def send_reset_password_email(email, supabase):
    st.warning("Password reset is disabled in guest mode.")

def register_user(email, password, supabase):
     st.warning("Registration is disabled in guest mode.")

def auth_screen(supabase):
    # Check for existing auth token
    auth_token = get_auth_cookie()
    if auth_token:
        user_data = verify_jwt(auth_token)
        if user_data:
            st.session_state['logged_in'] = True
            st.session_state['user'] = {"email": user_data["email"]}
        else:
            st.session_state['logged_in'] = False
            clear_auth_cookie()

    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if st.session_state.get('logged_in', False):
        st.sidebar.success(f"Welcome {st.session_state['user']['email']}")
        if st.sidebar.button("Logout"):
            st.session_state['logged_in'] = False
            st.session_state.pop('user', None)
            clear_auth_cookie()
            # supabase.auth.sign_out() # No need to sign out from Supabase since we are not authenticating
            st.rerun()
    else:
        # Simplified login - no email/password needed
        st.markdown(f'## Welcome! Click below to access as a guest')
        if st.button("Log In as Guest"):
            authenticate_user("","") # Call authenticate_user without credentials
