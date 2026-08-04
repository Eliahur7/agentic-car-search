import streamlit as st
import pandas as pd
from dotenv import load_dotenv
load_dotenv()
import plotly.express as px
from src.database import get_inventory
from src.ai_search import parse_search_query, filter_inventory
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

st.title("🤖 Agentic Car Search Engine")
st.markdown("Type exactly what you're looking for in plain English. Our AI agent will scan multiple sources, evaluate deals, and guide you through the process.")

# Load Inventory
df = get_inventory()

# Search Input
query = st.text_input("💬 Tell the Agent what you want:", 
                      placeholder="e.g., Looking for a reliable SUV under $35k with under 40k miles, adaptive cruise, and clean accident history")

if query:
    with st.spinner("Agent is scanning sources, evaluating deals, and estimating costs..."):
        # Parse query & filter
        params = parse_search_query(query)
        st.write("### 🧠 Agent Understood:")
        st.json(params)
        
        filtered_df = filter_inventory(df, params)
        
        if filtered_df.empty:
            st.warning("No vehicles match your strict criteria. Try loosening your budget or mileage.")
        else:
            st.success(f"Found {len(filtered_df)} matches across multiple sources!")
            
            # Display Results
            for idx, car in filtered_df.iterrows():
                # Evaluate Deal
                deal_info = evaluate_deal(car)
                # Estimate TCO
                tco_info = estimate_tco(car)
                # Get Dealer Questions
                questions = generate_dealer_questions(car)
                # Summarize History
                history = summarize_history(car)
                
                badge_class = "badge-green" if deal_info['color'] == 'green' else "badge-blue" if deal_info['color'] == 'blue' else "badge-red"
                
                # Card HTML setup
                st.markdown(f"""
                <div class="glass-card">
                    <h3>{car['year']} {car['make']} {car['model']} {car['trim']}</h3>
                    <p style="font-size: 1.5em; font-weight: bold; margin: 0;">${car['price']:,}</p>
                    <p>{car['mileage']:,} miles • {car['color']} • Found on <strong>{car['source']}</strong></p>
                    <div>
                        <span class="badge {badge_class}">{deal_info['rating']}</span>
                    </div>
                    <p style="margin-top:10px;"><em>{deal_info['explanation']}</em></p>
                </div>
                """, unsafe_allow_html=True)
                
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
