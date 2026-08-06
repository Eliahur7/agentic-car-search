import streamlit as st
import pandas as pd
import json
from dotenv import load_dotenv
load_dotenv()
import plotly.express as px
from src.database import get_inventory
from src.ai_search import parse_search_query, filter_inventory, generate_followup_questions
from src.live_scraper import live_search
from src.deal_evaluator import evaluate_deal
from src.cost_estimator import estimate_tco, calculate_out_the_door
from src.dealer_advisor import generate_dealer_questions, summarize_history
from src.tradein_agent import evaluate_trade_in

st.set_page_config(page_title="Agentic Car Search Engine", page_icon="🚗", layout="wide")

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
if "active_trade_in" not in st.session_state:
    st.session_state.active_trade_in = None

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
    st.header("🔄 Active Trade-In")
    if st.session_state.active_trade_in:
        tr = st.session_state.active_trade_in
        st.success(f"**{tr['year']} {tr['make']} {tr['model']}**")
        st.write(f"Estimated Value: **${tr['trade_in_value']:,}**")
        st.write(f"Net Equity: **${tr['net_equity']:,}**")
        if st.button("❌ Clear Active Trade-In"):
            st.session_state.active_trade_in = None
            st.rerun()
    else:
        st.info("No trade-in active. Visit the Trade-In Agent tab to value your vehicle!")
        
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
st.markdown("An AI-first car search & negotiation platform powered by conversational agents.")

# Top Navigation Tabs
tab_search, tab_tradein, tab_comparison = st.tabs([
    "🔍 AI Car Search Agent", 
    "🔄 Trade-In Valuation Agent", 
    "⚡ Why AI Beats Legacy CarGurus"
])


# ==============================================================================
# TAB 1: AI CAR SEARCH AGENT
# ==============================================================================
with tab_search:
    # TOP PROMPT BAR
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
        
        # Calculate OTD expenses considering active trade-in
        trade_val = st.session_state.active_trade_in['trade_in_value'] if st.session_state.active_trade_in else 0.0
        trade_loan = st.session_state.active_trade_in['loan_balance'] if st.session_state.active_trade_in else 0.0
        otd_info = calculate_out_the_door(car['price'], trade_in_value=trade_val, loan_balance=trade_loan)
        
        badge_class = "badge-green" if deal_info['color'] == 'green' else "badge-blue" if deal_info['color'] == 'blue' else "badge-red"
        url = car.get('listing_url', f"https://www.google.com/search?q={car['year']}+{car['make']}+{car['model']}+for+sale")
        
        st.markdown(f"""
        <div class="glass-card">
            <h3><a href="{url}" target="_blank" style="color: #93c5fd; text-decoration: none;">
                {car['year']} {car['make']} {car['model']} {car['trim']} ↗
            </a></h3>
            <p style="font-size: 1.5em; font-weight: bold; margin: 0;">${car['price']:,} <span style="font-size: 0.6em; color: #94a3b8; font-weight: normal;">(Sticker)</span></p>
            <p style="color: #38bdf8; font-weight: 600;">Est. Out-The-Door: ${otd_info['final_otd_price']:,.2f} • ${otd_info['monthly_payment']:,.2f}/mo (60 mo)</p>
            <p>{car['mileage']:,} miles • {car['color']} • Found on <strong><a href="{url}" target="_blank" style="color: #93c5fd;">{car['source']}</a></strong> • 🏢 {car.get('dealer','')}</p>
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
        
        # Expanders for OTD, TCO, and Negotiation
        with st.expander("💵 Out-The-Door (OTD) Expense & Financing Breakdown"):
            otd_col1, otd_col2 = st.columns(2)
            with otd_col1:
                st.write("#### Itemized Costs")
                st.write(f"- Vehicle Asking Price: **${car['price']:,}**")
                st.write(f"- Estimated Sales Tax (5%): **+${otd_info['sales_tax']:,.2f}**")
                st.write(f"- Dealer Doc Fee: **+${otd_info['doc_fee']:,.2f}**")
                st.write(f"- Title & Registration Fee: **+${otd_info['reg_fee']:,.2f}**")
                if trade_val > 0:
                    st.write(f"- Trade-In Tax Savings (5%): **-${otd_info['tax_savings_from_trade']:,.2f}**")
                    st.write(f"- Net Trade Equity Deduction: **-${otd_info['net_trade_equity']:,.2f}**")
            with otd_col2:
                st.write("#### Estimated Cash / Financing")
                st.markdown(f"### **Total OTD Price:** `${otd_info['final_otd_price']:,.2f}`")
                st.markdown(f"### **Est. Monthly Payment:** `${otd_info['monthly_payment']:,.2f}/mo`")
                st.caption(f"Based on 60-month loan @ {otd_info['apr']}% APR.")

        with st.expander("📊 View 5-Year Ownership Cost Estimate"):
            col1, col2 = st.columns(2)
            with col1:
                st.write("#### Features Included")
                for feat in car['features']:
                    st.write(f"- ✅ {feat.title()}")
                    
                st.write("#### History Summary")
                hist_icon = "🟢" if history['status'] == "Positive" else "⚠️"
                st.write(f"{hist_icon} {history['summary']}")
            
            with col2:
                st.write("#### 5-Year Cost Breakdown")
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
                    height=220
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
            with st.spinner("🔍 Scanning CarGurus, Autotrader, and Cars.com for live inventory..."):

                # Parse query contextually
                new_params = parse_search_query(prompt, previous_params=st.session_state.search_params)
                st.session_state.search_params = new_params

                # Format the parameters block
                params_md = f"**\U0001f9e0 Agent Understood:**\n```json\n{json.dumps(new_params, indent=2)}\n```\n"

                # Generate proactive follow-up questions
                followups = generate_followup_questions(new_params)
                followup_md = ""
                followup_chips = {}

                if followups:
                    followup_md = "\n\n\U0001f64b **To improve results, please tell me:**\n"
                    for q in followups:
                        followup_md += f"- {q}\n"
                    if not new_params.get("condition"):
                        followup_chips["\U0001f697 Used Car"] = "I am looking for a Used car"
                        followup_chips["\U0001f195 New Car"] = "I am looking for a brand New car"
                    if not new_params.get("zip_code"):
                        followup_chips["\U0001f4cd Enter Zip"] = "My zip code is "
                    if not new_params.get("trade_in"):
                        followup_chips["\U0001f504 Have Trade-In"] = "I have a vehicle to trade in"

                # ── LIVE SEARCH ─────────────────────────────────────────────
                region_label = new_params.get("region_label") or ""
                zip_code     = new_params.get("zip_code") or "10001"
                region_md    = f"\n\U0001f5fa\ufe0f **Searching near:** {region_label} (zip: {zip_code}, 50-mile radius)\n" if region_label else f"\n\U0001f5fa\ufe0f **Searching within 50 miles of zip:** {zip_code}\n"

                search_result   = live_search(new_params)
                live_listings   = search_result["listings"]
                platform_links  = search_result["platform_links"]

                # Always show the cross-platform live search links
                links_md = "\n\n\U0001f50e **Live Search Links** — click to browse full real-time inventory:\n"
                for link_name, link_url in platform_links:
                    links_md += f"- [{link_name}]({link_url})\n"

                if live_listings:
                    response_text = (
                        f"{params_md}{region_md}\n"
                        f"\u2705 Found **{len(live_listings)} live listings** from CarGurus near **{region_label or zip_code}**. "
                        f"Each card links directly to the vehicle detail page.{followup_md}{links_md}"
                    )
                    st.session_state.messages.append({
                        "role":           "assistant",
                        "content":        response_text,
                        "results":        live_listings,
                        "followup_chips": followup_chips,
                    })
                else:
                    response_text = (
                        f"{params_md}{region_md}\n"
                        f"\u26a0\ufe0f CarGurus did not return parseable listings for this search in our automated scan. "
                        f"This can happen if CarGurus requires browser session cookies. "
                        f"**Please click the live search links below** to view real matching inventory directly on each platform — "
                        f"all filters (year, mileage, zip code, distance) are pre-applied.{followup_md}{links_md}"
                    )
                    st.session_state.messages.append({
                        "role":           "assistant",
                        "content":        response_text,
                        "followup_chips": followup_chips,
                    })
        # Rerun to render natively
        st.rerun()


# ==============================================================================
# TAB 2: TRADE-IN VALUATION AGENT
# ==============================================================================
with tab_tradein:
    st.header("🔄 Specialized Trade-In Valuation Agent")
    st.markdown("Enter your vehicle's details below. The AI Agent will calculate estimated dealer trade-in offers, private party value, tax savings, and negotiation leverage.")
    
    with st.form("tradein_form"):
        t_col1, t_col2 = st.columns(2)
        with t_col1:
            t_year = st.number_input("Vehicle Year", min_value=2000, max_value=2024, value=2018)
            t_make = st.selectbox("Vehicle Make", ["Honda", "Toyota", "Ford", "Chevrolet", "Subaru", "Nissan", "BMW", "Porsche", "Tesla", "Hyundai", "Kia", "Other"])
            t_model = st.text_input("Vehicle Model", value="Civic")
            t_trim = st.text_input("Trim Level", value="EX-L")
            
        with t_col2:
            t_mileage = st.number_input("Current Mileage", min_value=0, max_value=300000, value=45000)
            t_condition = st.selectbox("Overall Condition", ["Good", "Excellent", "Fair", "Poor"])
            t_loan = st.number_input("Remaining Loan / Lien Balance ($)", min_value=0.0, value=4000.0, step=500.0)
            
        t_submit = st.form_submit_button("📊 Calculate Trade-In Valuation", type="primary", use_container_width=True)
        
    if t_submit:
        trade_res = evaluate_trade_in(t_year, t_make, t_model, t_trim, t_mileage, t_condition, loan_balance=t_loan)
        
        st.success("### 🎯 Trade-In Valuation Summary")
        
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        m_col1.metric("Dealer Trade-In Target", f"${trade_res['trade_in_value']:,}", f"${trade_res['trade_in_min']:,} - ${trade_res['trade_in_max']:,}")
        m_col2.metric("Private Party Value", f"${trade_res['private_party_value']:,}", "+18% vs Dealer")
        m_col3.metric("Net Trade Equity", f"${trade_res['net_equity']:,}", f"After ${trade_res['loan_balance']:,} Loan")
        m_col4.metric("Est. Sales Tax Savings", f"${trade_res['tax_savings']:,.2f}", "5% Tax Credit")
        
        st.markdown("---")
        st.subheader("💡 Dealer Trade-In Negotiation Tactics")
        for tactic in trade_res['tactics']:
            st.markdown(tactic)
            
        st.markdown("---")
        if st.button("✅ Apply This Trade-In to Active Car Search", type="primary", use_container_width=True):
            st.session_state.active_trade_in = trade_res
            st.success(f"Applied {t_year} {t_make} {t_model} (Net Equity: ${trade_res['net_equity']:,}) to your car search! Go to the 'AI Car Search' tab to see updated Out-The-Door pricing.")


# ==============================================================================
# TAB 3: WHY AI BEATS LEGACY CARGURUS
# ==============================================================================
with tab_comparison:
    st.header("⚡ Why AI Agentic Search Beats Legacy CarGurus")
    st.markdown("Traditional car search engines rely on rigid dropdowns and hide key financial details. Here is how our Agentic AI gives buyers an unfair advantage:")
    
    comparison_data = {
        "Feature Capability": [
            "Input Experience",
            "Multi-Constraint Search",
            "Contextual Follow-Ups",
            "Trade-In Integration",
            "Out-The-Door (OTD) Pricing",
            "Negotiation Assistance",
            "Multi-Source Coverage"
        ],
        "Legacy CarGurus": [
            "Rigid, manual drop-down menus & filter checkboxes",
            "Fails or returns zero results on complex multi-rule prompts",
            "No memory — changing one filter resets your search",
            "Separate ad-heavy valuation tool; no automatic tax credit integration",
            "Shows only sticker price — hides sales tax, doc fees, and title costs",
            "Generic blog articles",
            "CarGurus inventory only"
        ],
        "🤖 Agentic Car Search": [
            "Free-form natural language prompts in plain English",
            "AI Agent extracts budget, mileage, features, and body style automatically",
            "Remembers search context — refine prompts naturally (e.g. 'Make it under 25k')",
            "Integrated Trade-In Valuation Agent applies equity & sales tax credits to search results",
            "Full itemized Out-The-Door breakdown + estimated monthly payments",
            "Tailored high-leverage negotiation questions generated for every specific car",
            "Multi-source simulated inventory (CarGurus, Autotrader, Cars.com, CPO, Dealer Direct)"
        ]
    }
    
    comp_df = pd.DataFrame(comparison_data)
    st.table(comp_df)
