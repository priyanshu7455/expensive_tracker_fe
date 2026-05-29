import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import date

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Expense Tracker",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }

.stApp { background: #0b0f1a; color: #dde1ec; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #111827;
    border-right: 1px solid #1f2b3e;
}
section[data-testid="stSidebar"] * { color: #c4c9d9 !important; }
section[data-testid="stSidebar"] .stRadio label {
    background: #1a2235;
    border-radius: 10px;
    padding: 10px 16px;
    margin-bottom: 6px;
    display: block;
    transition: all 0.2s;
    border: 1px solid transparent;
}
section[data-testid="stSidebar"] .stRadio label:hover {
    background: #1f2d45;
    border-color: #3b5bdb;
}

/* Metric Cards */
div[data-testid="metric-container"] {
    background: #111827;
    border: 1px solid #1f2b3e;
    border-radius: 14px;
    padding: 20px 24px;
    transition: transform 0.2s;
}
div[data-testid="metric-container"]:hover { transform: translateY(-2px); }
div[data-testid="metric-container"] label { color: #6b7694 !important; font-size: 13px !important; text-transform: uppercase; letter-spacing: 0.5px; }
div[data-testid="metric-container"] div[data-testid="stMetricValue"] { color: #dde1ec !important; font-size: 26px !important; font-weight: 700 !important; }

/* Inputs */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stDateInput > div > div > input {
    background: #1a2235 !important;
    border: 1px solid #2a3a55 !important;
    border-radius: 10px !important;
    color: #dde1ec !important;
    padding: 10px 14px !important;
}
.stSelectbox > div > div {
    background: #1a2235 !important;
    border: 1px solid #2a3a55 !important;
    border-radius: 10px !important;
    color: #dde1ec !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #3b5bdb, #6741d9);
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 10px 26px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    width: 100%;
    transition: opacity 0.2s, transform 0.15s !important;
    letter-spacing: 0.3px;
}
.stButton > button:hover { opacity: 0.88; transform: translateY(-1px) !important; }

/* Danger button */
.danger .stButton > button {
    background: linear-gradient(135deg, #e03131, #c92a2a) !important;
}

/* DataFrames */
.stDataFrame { border-radius: 12px !important; overflow: hidden !important; }

/* Headings */
h1 { color: #dde1ec !important; font-weight: 700 !important; letter-spacing: -0.5px; }
h2, h3 { color: #b0b8d0 !important; font-weight: 600 !important; }

/* Alerts */
.stSuccess { background: #0a2e1a !important; border-left: 4px solid #2f9e44 !important; border-radius: 8px !important; }
.stError   { background: #2e0a0a !important; border-left: 4px solid #e03131 !important; border-radius: 8px !important; }
.stInfo    { background: #0a1e2e !important; border-left: 4px solid #3b5bdb !important; border-radius: 8px !important; }
.stWarning { background: #2e1e0a !important; border-left: 4px solid #f08c00 !important; border-radius: 8px !important; }

/* Divider */
hr { border-color: #1f2b3e !important; }

/* Title gradient */
.app-title {
    background: linear-gradient(135deg, #4c6ef5, #9775fa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 30px;
    font-weight: 700;
    margin-bottom: 2px;
}
.subtitle { color: #6b7694; font-size: 14px; margin-bottom: 16px; }

/* Form Card */
.form-card {
    background: #111827;
    border: 1px solid #1f2b3e;
    border-radius: 16px;
    padding: 24px;
}
</style>
""", unsafe_allow_html=True)

# ─── Backend URL ──────────────────────────────────────────────────────────────
SERVER = st.secrets["backend_server"]

# ─── Categories & Payment Methods ─────────────────────────────────────────────
CATEGORIES = [
    "🍔 Food", "✈️ Travel", "🛍️ Shopping",
    "💡 Bills", "🏥 Health", "🎬 Entertainment", "📦 Other"
]
PAYMENT_METHODS = ["💳 Card", "📲 UPI", "💵 Cash"]

# ─── Helper: safe GET ─────────────────────────────────────────────────────────
def safe_get(url, params=None):
    try:
        r = requests.get(url, params=params, timeout=10)
        return r
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend. Check your backend URL in secrets.")
        return None

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 💳 Expense Tracker")
    st.markdown("---")
    opt = st.radio(
        "Menu",
        [
            "📊 Dashboard",
            "➕ Add Expenses",
            "👁️ View Expenses",
            "✏️ Update Expenses",
            "🗑️ Delete Expenses",
            "🔍 Search Expenses",
            "🔃 Sort Expenses",
            "🎛️ Filter Expenses",
            "📈 Analyze Expenses",
        ],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.caption("Streamlit · FastAPI · MySQL")

# ══════════════════════════════════════════════════════════════════
#  DASHBOARD
# ══════════════════════════════════════════════════════════════════
if opt == "📊 Dashboard":
    st.markdown('<p class="app-title">Dashboard</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Your financial summary at a glance</p>', unsafe_allow_html=True)
    st.markdown("---")

    r = safe_get(f"{SERVER}/get_expenses")
    if r and r.status_code == 200:
        raw = r.json()
        expenses = raw.get("expenses", raw) if isinstance(raw, dict) else raw
        if expenses:
            df = pd.DataFrame(expenses)
            df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

            total   = df["amount"].sum()
            count   = len(df)
            avg     = df["amount"].mean()
            highest = df["amount"].max()

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("💰 Total Spent",    f"₹ {total:,.2f}")
            c2.metric("🧾 Transactions",   str(count))
            c3.metric("📊 Average",        f"₹ {avg:,.2f}")
            c4.metric("🔺 Highest",        f"₹ {highest:,.2f}")

            st.markdown("---")
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Spending by Category")
                cat_df = df.groupby("category")["amount"].sum().reset_index()
                fig = px.pie(cat_df, values="amount", names="category",
                             hole=0.5, color_discrete_sequence=px.colors.sequential.Plasma_r)
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="#c4c9d9",
                                  showlegend=True, margin=dict(t=10,b=10,l=10,r=10))
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.subheader("Payment Method Split")
                pay_df = df.groupby("payment_method")["amount"].sum().reset_index()
                fig2 = px.bar(pay_df, x="payment_method", y="amount",
                              color="amount", color_continuous_scale="Viridis",
                              labels={"amount": "₹ Amount", "payment_method": ""})
                fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                   font_color="#c4c9d9", coloraxis_showscale=False,
                                   margin=dict(t=10,b=10,l=10,r=10))
                fig2.update_xaxes(gridcolor="#1f2b3e"); fig2.update_yaxes(gridcolor="#1f2b3e")
                st.plotly_chart(fig2, use_container_width=True)

            # Category bar
            st.subheader("Top Spending Categories")
            cat_sorted = cat_df.sort_values("amount", ascending=True)
            fig3 = px.bar(cat_sorted, x="amount", y="category", orientation="h",
                          color="amount", color_continuous_scale="Plasma",
                          labels={"amount": "₹ Amount", "category": ""})
            fig3.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                               font_color="#c4c9d9", coloraxis_showscale=False,
                               margin=dict(t=10,b=10,l=10,r=10))
            fig3.update_xaxes(gridcolor="#1f2b3e"); fig3.update_yaxes(gridcolor="#1f2b3e")
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("No expenses yet. Add your first expense to see the dashboard.")

# ══════════════════════════════════════════════════════════════════
#  ADD EXPENSES
# ══════════════════════════════════════════════════════════════════
elif opt == "➕ Add Expenses":
    st.markdown('<p class="app-title">Add Expense</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Record a new transaction</p>', unsafe_allow_html=True)
    st.markdown("---")

    with st.form("add_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            title          = st.text_input("Title", placeholder="e.g. Lunch at Swiggy")
            payment_method = st.selectbox("Payment Method", PAYMENT_METHODS)
        with col2:
            amount    = st.number_input("Amount (₹)", min_value=0.01, step=1.0, format="%.2f")
            category  = st.selectbox("Category", CATEGORIES)

        spent_date = st.date_input("Date", value=date.today())
        submitted  = st.form_submit_button("✅ Add Expense")

    if submitted:
        if not title.strip():
            st.error("Title cannot be empty.")
        elif amount <= 0:
            st.error("Amount must be greater than 0.")
        else:
            payload = {
                "title": title,
                "payment_method": payment_method,
                "amount": amount,
                "category": category,
                "spent_at": str(spent_date)
            }
            r = requests.post(f"{SERVER}/expenses", json=payload)
            if r.status_code == 200:
                st.success(f"✅ Added **{title}** — ₹{amount:,.2f} ({category}) on {spent_date}")
            else:
                st.error(f"Backend error: {r.text}")

# ══════════════════════════════════════════════════════════════════
#  VIEW EXPENSES
# ══════════════════════════════════════════════════════════════════
elif opt == "👁️ View Expenses":
    st.markdown('<p class="app-title">All Expenses</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Browse your complete transaction history</p>', unsafe_allow_html=True)
    st.markdown("---")

    r = safe_get(f"{SERVER}/get_expenses")
    if r and r.status_code == 200:
        raw = r.json()
        expenses = raw.get("expenses", raw) if isinstance(raw, dict) else raw
        if expenses:
            df = pd.DataFrame(expenses)
            st.markdown(f"**{len(df)} records** · Total: **₹ {pd.to_numeric(df['amount'], errors='coerce').sum():,.2f}**")
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No expenses recorded yet.")

# ══════════════════════════════════════════════════════════════════
#  UPDATE EXPENSES
# ══════════════════════════════════════════════════════════════════
elif opt == "✏️ Update Expenses":
    st.markdown('<p class="app-title">Update Expense</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Edit an existing transaction</p>', unsafe_allow_html=True)
    st.markdown("---")

    expense_id = st.number_input("Enter Expense ID to Update", min_value=1, step=1)

    if st.button("🔍 Fetch Expense"):
        r = safe_get(f"{SERVER}/get_expenses_single/{expense_id}")
        if r and r.status_code == 200:
            data = r.json()
            expense = data.get("expenses_data", {})
            if expense:
                st.session_state.update({
                    "u_title":   expense.get("title", ""),
                    "u_amount":  float(expense.get("amount", 0)),
                    "u_cat":     expense.get("category", CATEGORIES[0]),
                    "u_pay":     expense.get("payment_method", PAYMENT_METHODS[0]),
                    "u_date":    str(expense.get("spent_at", str(date.today()))),
                })
                st.success("Expense loaded — edit below and click Update.")
        elif r:
            st.error(f"Expense ID {expense_id} not found.")

    if "u_title" in st.session_state:
        with st.form("update_form"):
            col1, col2 = st.columns(2)
            with col1:
                u_title = st.text_input("Title",          value=st.session_state.u_title)
                u_pay   = st.selectbox("Payment Method",  PAYMENT_METHODS,
                                       index=PAYMENT_METHODS.index(st.session_state.u_pay)
                                       if st.session_state.u_pay in PAYMENT_METHODS else 0)
            with col2:
                u_amount = st.number_input("Amount (₹)", value=st.session_state.u_amount,
                                           min_value=0.01, format="%.2f")
                u_cat   = st.selectbox("Category", CATEGORIES,
                                       index=CATEGORIES.index(st.session_state.u_cat)
                                       if st.session_state.u_cat in CATEGORIES else 0)
            u_date = st.date_input("Date", value=pd.to_datetime(st.session_state.u_date))
            update_btn = st.form_submit_button("✏️ Update Expense")

        if update_btn:
            payload = {
                "title": u_title, "payment_method": u_pay,
                "amount": u_amount, "category": u_cat,
                "spent_at": str(u_date)
            }
            r = requests.put(f"{SERVER}/update_expenses/{expense_id}", json=payload)
            if r.status_code == 200:
                st.success("✅ Expense updated successfully!")
                for k in ["u_title","u_amount","u_cat","u_pay","u_date"]:
                    st.session_state.pop(k, None)
            else:
                st.error(f"Update failed: {r.text}")

# ══════════════════════════════════════════════════════════════════
#  DELETE EXPENSES
# ══════════════════════════════════════════════════════════════════
elif opt == "🗑️ Delete Expenses":
    st.markdown('<p class="app-title">Delete Expense</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Remove a transaction from records</p>', unsafe_allow_html=True)
    st.markdown("---")

    r = safe_get(f"{SERVER}/get_expenses")
    if r and r.status_code == 200:
        raw = r.json()
        expenses = raw.get("expenses", raw) if isinstance(raw, dict) else raw
        if expenses:
            df = pd.DataFrame(expenses)
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.markdown("---")
            del_id = st.number_input("Enter Expense ID to Delete", min_value=1, step=1)
            with st.container():
                st.markdown('<div class="danger">', unsafe_allow_html=True)
                if st.button("🗑️ Delete Expense"):
                    dr = requests.delete(f"{SERVER}/delete_expense/{del_id}")
                    if dr.status_code == 200:
                        st.success(f"✅ Expense ID {del_id} deleted successfully!")
                        st.rerun()
                    else:
                        st.error(f"Failed: {dr.text}")
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No expenses to delete.")

# ══════════════════════════════════════════════════════════════════
#  SEARCH EXPENSES
# ══════════════════════════════════════════════════════════════════
elif opt == "🔍 Search Expenses":
    st.markdown('<p class="app-title">Search Expenses</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Find by title or category keyword</p>', unsafe_allow_html=True)
    st.markdown("---")

    col1, col2 = st.columns([3, 1])
    with col1:
        search_text = st.text_input("Search keyword", placeholder="e.g. Food, Zomato, Travel...")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        search_btn = st.button("🔍 Search")

    if search_btn:
        if not search_text.strip():
            st.warning("Please enter a keyword.")
        else:
            r = safe_get(f"{SERVER}/search_expenses", params={"search_text": search_text})
            if r and r.status_code == 200:
                expenses = r.json().get("expenses", [])
                if expenses:
                    df = pd.DataFrame(expenses)
                    st.success(f"Found **{len(df)}** matching records")
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.info(f"No results found for **'{search_text}'**")

# ══════════════════════════════════════════════════════════════════
#  SORT EXPENSES
# ══════════════════════════════════════════════════════════════════
elif opt == "🔃 Sort Expenses":
    st.markdown('<p class="app-title">Sort Expenses</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Reorder your expenses by any field</p>', unsafe_allow_html=True)
    st.markdown("---")

    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        sort_by  = st.selectbox("Sort By", ["amount", "spent_at", "category", "payment_method", "title"])
    with col2:
        order_by = st.selectbox("Order",   ["desc", "asc"])
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        sort_btn = st.button("🔃 Sort")

    if sort_btn:
        r = safe_get(f"{SERVER}/sort_expenses", params={"sort_by": sort_by, "order_by": order_by})
        if r and r.status_code == 200:
            expenses = r.json().get("expenses", [])
            if expenses:
                df = pd.DataFrame(expenses)
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("No expenses found.")

# ══════════════════════════════════════════════════════════════════
#  FILTER EXPENSES
# ══════════════════════════════════════════════════════════════════
elif opt == "🎛️ Filter Expenses":
    st.markdown('<p class="app-title">Filter Expenses</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Show expenses by category</p>', unsafe_allow_html=True)
    st.markdown("---")

    col1, col2 = st.columns([3, 1])
    with col1:
        filter_cat = st.selectbox("Select Category", CATEGORIES)
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        filter_btn = st.button("🎛️ Filter")

    if filter_btn:
        r = safe_get(f"{SERVER}/filter_expenses/{filter_cat}")
        if r and r.status_code == 200:
            expenses = r.json().get("expenses", [])
            if expenses:
                df = pd.DataFrame(expenses)
                total = pd.to_numeric(df["amount"], errors="coerce").sum()
                st.success(f"**{len(df)} records** in {filter_cat} · Total: **₹ {total:,.2f}**")
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info(f"No expenses found in **{filter_cat}**")

# ══════════════════════════════════════════════════════════════════
#  ANALYZE EXPENSES
# ══════════════════════════════════════════════════════════════════
elif opt == "📈 Analyze Expenses":
    st.markdown('<p class="app-title">Analyze Expenses</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Visual breakdown of your spending patterns</p>', unsafe_allow_html=True)
    st.markdown("---")

    col1, col2 = st.columns([3, 1])
    with col1:
        analyze_by = st.selectbox("Analyze By", ["category", "payment_method", "spent_at"])
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        analyze_btn = st.button("📈 Analyze")

    if analyze_btn:
        r = safe_get(f"{SERVER}/analyze_expenses/{analyze_by}")
        if r and r.status_code == 200:
            expenses = r.json().get("expenses", [])
            if expenses:
                df = pd.DataFrame(expenses)
                df["total"] = pd.to_numeric(df["total"], errors="coerce")

                col_t, col_c = st.columns(2)
                with col_t:
                    st.dataframe(df, use_container_width=True, hide_index=True)
                with col_c:
                    fig = px.pie(df, values="total", names=analyze_by,
                                 hole=0.5, color_discrete_sequence=px.colors.sequential.Plasma_r,
                                 title=f"Breakdown by {analyze_by}")
                    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="#c4c9d9",
                                      margin=dict(t=40,b=10,l=10,r=10))
                    st.plotly_chart(fig, use_container_width=True)

                fig2 = px.bar(df.sort_values("total"), x="total", y=analyze_by,
                              orientation="h", color="total",
                              color_continuous_scale="Viridis",
                              labels={"total": "₹ Total", analyze_by: ""},
                              title=f"Total Spent by {analyze_by}")
                fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                   font_color="#c4c9d9", coloraxis_showscale=False,
                                   margin=dict(t=40,b=10,l=10,r=10))
                fig2.update_xaxes(gridcolor="#1f2b3e"); fig2.update_yaxes(gridcolor="#1f2b3e")
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("No data available for analysis.")
