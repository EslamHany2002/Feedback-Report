import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import streamlit as st

warnings.filterwarnings("ignore")

# ===== Load data =====
df = pd.read_csv("Clean Feedback.csv")  # اسم الملف
df.columns = df.columns.astype(str).str.replace(r'\n', ' ', regex=True).str.strip()

# ===== Column names =====
status_col = 'Techincal / Operation Solved'
group_col = 'Select your assigned group | اختر المجموعة المخصصة لك'
link_col = 'Evidence Attachment'
rating_col = 'تقيّم تجربتك مع AMIT Learning ?'

# Clean status column
df[status_col] = df[status_col].str.lower().str.strip()

# Convert rating to numeric
df[rating_col] = pd.to_numeric(df[rating_col], errors='coerce')

# ===== Metrics =====
total_rows = len(df)
total_groups = df[group_col].nunique()

# Poor feedback filter
poor_ratings = [1, 2, 3]
poor_feedback_df = df[
    df[status_col].isin(['solved', 'follow up', 'not solved']) &
    df[rating_col].isin(poor_ratings)
]
poor_feedback_count = len(poor_feedback_df)

# Solved with poor ratings only
solved_poor_count = len(df[(df[status_col] == 'solved') & (df[rating_col].isin(poor_ratings))])
# Evidence links for poor ratings
links_poor_count = df[df[rating_col].isin(poor_ratings)][link_col].notna().sum()


# Normal counts
follow_count = (df[status_col] == 'follow up').sum()
not_solved_count = (df[status_col] == 'not solved').sum()
links_count = df[link_col].notna().sum()

# ===== Streamlit Config =====
st.set_page_config(page_title="AMIT Learning Dashboard", layout="wide")
st.title("📊 AMIT Learning Dashboard")
st.markdown("This dashboard provides insights into the AI feedback.")

# ===== Metric Cards =====
col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("Total Responses", total_rows)
col2.metric("Groups", total_groups)
col3.metric("Poor Feedback Total", poor_feedback_count)
col4.metric("Solved (Poor Ratings)", solved_poor_count)
col5.metric("Follow Up", follow_count)
col6.metric("Not Solved", not_solved_count)

# ===== Tabs =====
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📌 Main Status", "📍 By Status", "🔗 Links", "⭐ Ratings", "📋 Summary"]
)

# ====== Tab 1: Main Chart ======
with tab1:
    st.subheader("Status Distribution per Group")
    status_counts = df.groupby([group_col, status_col]).size().unstack(fill_value=0)
    fig, ax = plt.subplots(figsize=(10,5))
    status_counts.plot(kind='bar', stacked=True, ax=ax, colormap='tab20')
    ax.set_ylabel("Count")
    ax.set_xlabel("Groups")
    ax.set_title("All Statuses per Group")
    ax.tick_params(axis='x', rotation=45)
    st.pyplot(fig)

# ====== Tab 2: Separate Status Charts ======
def plot_single_status(data, status_value, color):
    subset = data[data[status_col] == status_value]
    counts = subset[group_col].value_counts()
    fig, ax = plt.subplots(figsize=(9,4))
    sns.barplot(x=counts.index, y=counts.values, palette=[color], ax=ax)
    ax.set_ylabel("Count")
    ax.set_xlabel("Group")
    ax.set_title(f"{status_value.capitalize()} per Group")
    ax.tick_params(axis='x', rotation=45)
    st.pyplot(fig)

with tab2:
    colA, colB, colC = st.columns(3)
    with colA:
        plot_single_status(df, 'solved', '#4CAF50')
    with colB:
        plot_single_status(df, 'follow up', '#FFC107')
    with colC:
        plot_single_status(df, 'not solved', '#F44336')

# ====== Tab 3: Links Analysis ======
with tab3:
    st.subheader("Links in Solved Cases")
    df_solved = df[df[status_col] == 'solved']
    df_solved[link_col] = df_solved[link_col].astype(str).str.strip()
    df_solved['Has Link'] = df_solved[link_col].apply(lambda x: 'Link' if x != '' and x.lower() != 'nan' else 'Empty')
    link_before = df_solved['Has Link'].value_counts()

    fig, ax = plt.subplots(figsize=(6,6))
    ax.pie(link_before, labels=link_before.index, autopct='%1.1f%%', colors=['#4CAF50','#FF5722'])
    ax.set_title("Links in Solved Cases")
    st.pyplot(fig)

# ====== Tab 4: Ratings ======
with tab4:
    st.subheader("Experience Rating (1-3)")
    rating_counts = df[rating_col].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(6,5))
    sns.barplot(x=rating_counts.index, y=rating_counts.values, palette="viridis", ax=ax)
    ax.set_xlabel("Rating")
    ax.set_ylabel("Count")
    ax.set_title("Rating Distribution")
    st.pyplot(fig)

# ====== Tab 5: Summary Table ======
with tab5:
    st.subheader("Summary Table")
    summary_table = {
        "Total Rows": total_rows,
        "Total Groups": total_groups,
        "Poor Feedback Total": poor_feedback_count,
        "Solved (Poor Ratings)": solved_poor_count,
        "Follow up": follow_count,
        "Not solved": not_solved_count,
        "Evidince": links_poor_count,
        "Without Evidence": solved_poor_count - links_poor_count
    }
    st.table(pd.DataFrame(list(summary_table.items()), columns=["Metric", "Value"]))

# python -m streamlit run dashboard.py