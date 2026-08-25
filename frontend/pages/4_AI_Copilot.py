import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
import streamlit as st
from frontend.theme import apply_theme
from frontend.components.widgets import render_status_bar
from frontend.api_client import chat_copilot

st.set_page_config(page_title="Intelligence Copilot", page_icon="🤖", layout="wide")
apply_theme()
render_status_bar()

st.title("🤖 Intelligence Copilot")
st.markdown("Conversational AI analyst powered by RAG and live intelligence feeds (GDELT / NewsAPI). Ask for briefings, summaries, or comparative analysis.")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Add initial greeting
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Sentinel Intelligence Copilot online. How can I assist with your threat analysis today?",
        "meta": None
    })

# Render chat history
st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"""
        <div style="background: #161B22; border: 1px solid #30363D; border-radius: 8px; padding: 12px 16px; margin: 8px 0 8px 10%; width: 90%;">
            <b style="color: #79C0FF;">COMMAND:</b><br>{msg["content"]}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background: #0D1117; border: 1px solid #21262D; border-left: 3px solid #58A6FF; border-radius: 8px; padding: 16px; margin: 8px 10% 8px 0; width: 90%;">
            <b style="color: #58A6FF;">SENTINEL AI:</b><br>
            <div style="margin-top: 8px; font-size: 0.95rem; line-height: 1.6;">{msg["content"]}</div>
        </div>
        """, unsafe_allow_html=True)
        
        if msg.get("meta"):
            st.markdown(f"""
            <div style="margin: -8px 10% 16px 0; padding: 4px 16px; font-size: 0.75rem; color: #8B949E; text-align: right;">
                {msg["meta"]}
            </div>
            """, unsafe_allow_html=True)

# Chat input at bottom
query = st.chat_input("Request an intelligence briefing, summary, or analysis...")

if query:
    # 1. Show user message instantly
    st.session_state.messages.append({"role": "user", "content": query, "meta": None})
    st.rerun()  # Rerun to display user message before processing

# Handle processing after rerun if last message is from user
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    query = st.session_state.messages[-1]["content"]
    
    with st.spinner("Compiling intelligence briefing..."):
        # Format history for API (excluding current query)
        history_for_api = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[:-1]]
        
        response = chat_copilot(query=query, history=history_for_api, top_k=8)
        
        if response and "response" in response:
            reply = response["response"]
            ref_count = response.get("retrieved_incidents", 0)
            live_mode = response.get("live_mode", False)
            disclaimer = response.get("source_disclaimer", "")
            
            # Construct metadata string
            meta = f"Context: {ref_count} historical records"
            if live_mode:
                meta += " | 🟢 Live Intel Active"
            else:
                meta += " | 🟡 Historical Mode Only"
                
            if disclaimer:
                meta += f" | {disclaimer}"
                
            st.session_state.messages.append({
                "role": "assistant", 
                "content": reply,
                "meta": meta
            })
            st.rerun()
        else:
            err = "Failed to connect to the intelligence backend or received invalid response."
            st.session_state.messages.append({
                "role": "assistant", 
                "content": f"⚠️ **SYSTEM ERROR:** {err}",
                "meta": None
            })
            st.rerun()

# ── Sidebar Quick Actions ────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚡ Quick Prompts")
    if st.button("Summarize global threat landscape"):
        st.session_state.messages.append({"role": "user", "content": "Provide a high-level summary of the global threat landscape based on recent intelligence.", "meta": None})
        st.rerun()
    if st.button("Analyze Middle East activity"):
        st.session_state.messages.append({"role": "user", "content": "Analyze recent operational activity and threat patterns in the Middle East & North Africa region.", "meta": None})
        st.rerun()
    if st.button("Compare IED vs Armed Assault"):
        st.session_state.messages.append({"role": "user", "content": "Compare the impact, frequency, and typical targets of Bombing/Explosion events versus Armed Assaults.", "meta": None})
        st.rerun()
    
    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = [{
            "role": "assistant",
            "content": "Conversation cleared. Ready for new intelligence requests.",
            "meta": None
        }]
        st.rerun()
