import streamlit as st
import pandas as pd
import json
from dotenv import load_dotenv
load_dotenv()
import plotly.express as px
from src.database import get_inventory
from src.ai_search import parse_search_query, filter_inventory, generate_followup_questions
from src.deal_evaluator import evaluate_deal
from src.cost_estimator import estimate_tco
from src.dealer_advisor import generate_dealer_questions, summarize_history

st.set_page_config(page_title="Agentic Car Search", page_icon="🚗", layout="wide")

# Inject Glassmorphism CSS
st.markdown("""
    <style>
    /* Dark Mode Glassmorphism Theme */
    .stApp {
        background-color: #0f172a;
        color: #e2e8f0;
    }
    
    /* Top Search Container */
    .top-prompt-box {
        background: rgba(30, 41, 59, 0.85);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 14px;
        padding: 18px 24px;
        margin-bottom: 25px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    
    /* Card Container */
    .glass-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
    }
    
    /* Badges */
    .badge {
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 0.85em;
        font-weight: 600;
        margin-right: 8px;
        display: inline-block;
    }
    .badge-green { background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid #10b981; }
    .badge-blue { background: rgba(59, 130, 246, 0.2); color: #60a5fa; border: 1px solid #3b82f6; }
    .badge-red { background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid #ef4444; }
    
    h1, h2, h3, p { color: #f8fafc; }
    </style>
""", unsafe_allow_html=True)

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "search_params" not in st.session_state:
    st.session_state.search_params = None
if "favorites" not in st.session_state:
    st.session_state.favorites = []
if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

# Load Inventory
df = get_inventory()

# Sidebar
with st.sidebar:
    st.header("🔄 Controls")
    if st.button("New Search / Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.search_params = None
        st.session_state.pending_prompt = None
        st.rerun()
        
    st.markdown("---")
    st.header("❤️ Favorites")
    if not st.session_state.favorites:
        st.write("No favorite vehicles saved yet.")
    else:
        fav_df = df[df['id'].isin(st.session_state.favorites)]
        for idx, car in fav_df.iterrows():
            st.markdown(f"**{car['year']} {car['make']} {car['model']}**")
            st.write(f"${car['price']:,} • {car['mileage']:,} miles")
            if st.button(f"❌ Remove", key=f"remove_sidebar_{car['id']}"):
                st.session_state.favorites.remove(car['id'])
                st.rerun()
            st.markdown("---")

st.title("🤖 Agentic Car Search Engine")
st.markdown("Describe the vehicle you want in plain English. Our AI Agent scans sources, remembers your context, and asks follow-ups to refine your search!")

# TOP PROMPT BAR (Positioned at the Top of the Main View)
st.markdown('<div class="top-prompt-box">', unsafe_allow_html=True)
top_col1, top_col2 = st.columns([5, 1])

with top_col1:
    top_input = st.text_input(
        "💬 Type your car search or reply to the agent here:",
        key="top_prompt_input",
        placeholder="e.g., Looking for a sporty car under 20k miles in 53024, I have a trade-in...",
        label_visibility="visible"
    )

with top_col2:
    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    submit_clicked = st.button("🔍 Send Prompt", use_container_width=True, type="primary")

st.markdown('</div>', unsafe_allow_html=True)

# Handle top prompt submission
if submit_clicked and top_input.strip():
    st.session_state.messages.append({"role": "user", "content": top_input.strip()})
    st.rerun()

# Handle pending prompt from quick action chips
if st.session_state.pending_prompt:
    prompt_to_send = st.session_state.pending_prompt
    st.session_state.pending_prompt = None
    st.session_state.messages.append({"role": "user", "content": prompt_to_send})
    st.rerun()


def render_car_card(car, msg_idx):
    deal_info = evaluate_deal(car)
    tco_info = estimate_tco(car)
    questions = generate_dealer_questions(car)
    history = summarize_history(car)
    
    badge_class = "badge-green" if deal_info['color'] == 'green' else "badge-blue" if deal_info['color'] == 'blue' else "badge-red"
    url = car.get('listing_url', f"https://www.google.com/search?q={car['year']}+{car['make']}+{car['model']}+for+sale")
    
    st.markdown(f"""
    <div class="glass-card">
        <h3><a href="{url}" target="_blank" style="color: #93c5fd; text-decoration: none;">
            {car['year']} {car['make']} {car['model']} {car['trim']} ↗
        </a></h3>
        <p style="font-size: 1.5em; font-weight: bold; margin: 0;">${car['price']:,}</p>
        <p>{car['mileage']:,} miles • {car['color']} • Found on <strong><a href="{url}" target="_blank" style="color: #93c5fd;">{car['source']}</a></strong></p>
        <div>
            <span class="badge {badge_class}">{deal_info['rating']}</span>
        </div>
        <p style="margin-top:10px;"><em>{deal_info['explanation']}</em></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Action Buttons
    col_btn1, col_btn2 = st.columns([1, 4])
    with col_btn1:
        is_fav = car['id'] in st.session_state.favorites
        button_label = "❌ Remove" if is_fav else "❤️ Save"
        if st.button(button_label, key=f"fav_{car['id']}_msg_{msg_idx}"):
            if is_fav:
                st.session_state.favorites.remove(car['id'])
            else:
                st.session_state.favorites.append(car['id'])
            st.rerun()
            
    with col_btn2:
        st.link_button(f"🔗 View on {car['source']}", url)
    
    with st.expander("📊 View Deal Breakdown & 5-Year Cost"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("#### Features Included")
            for feat in car['features']:
                st.write(f"- ✅ {feat.title()}")
                
            st.write("#### History Summary")
            hist_icon = "🟢" if history['status'] == "Positive" else "⚠️"
            st.write(f"{hist_icon} {history['summary']}")
        
        with col2:
            st.write("#### 5-Year Ownership Cost Estimate")
            tco_df = pd.DataFrame({
                "Category": ["Depreciation", "Maintenance & Repairs", "Fuel/Energy", "Insurance"],
                "Cost": [tco_info["Depreciation"], tco_info["Maintenance & Repairs"], tco_info["Fuel/Energy"], tco_info["Insurance"]]
            })
            fig = px.pie(tco_df, values='Cost', names='Category', hole=0.5, 
                         color_discrete_sequence=px.colors.sequential.Teal)
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#e2e8f0',
                margin=dict(t=0, b=0, l=0, r=0),
                height=250
            )
            st.plotly_chart(fig, use_container_width=True)
            st.write(f"**Estimated 5-Year Total:** ${tco_info['Total 5-Year Cost']:,.0f}")
    
    with st.expander("📋 Dealer Negotiation Agent"):
        st.write("Here are high-leverage questions to ask before visiting:")
        for q in questions:
            st.write(f"❓ {q}")
    
    st.markdown("---")


# Display chat history
for idx, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Render follow-up chips if present on latest assistant message
        if message.get("followup_chips") and idx == len(st.session_state.messages) - 1:
            st.markdown("##### 💡 Quick Reply / Answer Follow-ups:")
            chip_cols = st.columns(len(message["followup_chips"]))
            for chip_idx, (chip_label, chip_val) in enumerate(message["followup_chips"].items()):
                with chip_cols[chip_idx]:
                    if st.button(chip_label, key=f"chip_{idx}_{chip_idx}"):
                        st.session_state.pending_prompt = chip_val
                        st.rerun()
                        
        # If this message has results (car list), render the cards below the text
        if message.get("results"):
            for car in message["results"]:
                render_car_card(car, idx)


# Assistant Processing Logic
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    prompt = st.session_state.messages[-1]["content"]
    with st.chat_message("assistant"):
        with st.spinner("Agent is scanning sources, evaluating deals, and preparing follow-ups..."):
            
            # Parse query contextually
            new_params = parse_search_query(prompt, previous_params=st.session_state.search_params)
            st.session_state.search_params = new_params
            
            # Format the parameters block
            params_md = f"**🧠 Agent Understood:**\n```json\n{json.dumps(new_params, indent=2)}\n```\n"
            
            # Generate proactive follow-up questions
            followups = generate_followup_questions(new_params)
            followup_md = ""
            followup_chips = {}
            
            if followups:
                followup_md = "\n\n🙋 **Agent Follow-Up Questions to Refine Your Results:**\n"
                for q in followups:
                    followup_md += f"- {q}\n"
                    
                # Generate quick-reply chip options
                if not new_params.get("condition"):
                    followup_chips["🚗 Used Car"] = "I am looking for a Used car"
                    followup_chips["🆕 New Car"] = "I am looking for a brand New car"
                if not new_params.get("zip_code"):
                    followup_chips["📍 Set Zip 53024"] = "My zip code is 53024"
                if not new_params.get("trade_in"):
                    followup_chips["🔄 Have Trade-In"] = "I have a vehicle to trade in"
            
            filtered_df = filter_inventory(df, new_params)
            
            if filtered_df.empty:
                response_text = f"{params_md}\n⚠️ No vehicles match your strict criteria. Try loosening your budget or mileage.{followup_md}"
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response_text,
                    "followup_chips": followup_chips
                })
            else:
                response_text = f"{params_md}\n✅ I found {len(filtered_df)} vehicles matching your criteria:{followup_md}"
                results_list = [row.to_dict() for _, row in filtered_df.iterrows()]
                
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response_text,
                    "results": results_list,
                    "followup_chips": followup_chips
                })
    # Rerun to render natively
    st.rerun()
