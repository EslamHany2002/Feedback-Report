import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import streamlit as st

warnings.filterwarnings("ignore")

# ===== Load data =====
df = pd.read_csv("Clean Feedback.csv")  # change file name if needed

# ===== Clean columns =====
df.columns = df.columns.astype(str).str.replace(r'\n', ' ', regex=True).str.strip()
status_col = 'Techincal / Operation Solved'
group_col = 'Select your assigned group | اختر المجموعة المخصصة لك'
link_col = 'Evidence Attachment'
improve_col = 'What aspects do you think need improvement in the training? | ما الأمور التي تعتقد أنها بحاجة إلى تحسين في التدريب؟'
rating_col = 'تقيّم تجربتك مع AMIT Learning ?'

# Clean status column
df[status_col] = df[status_col].str.lower().str.strip()

# ===== Streamlit UI =====
st.title("📊 AMIT Learning Report")

# ========= Function to plot status counts =========
def plot_status_counts(data, title_prefix):
    status_counts = data.groupby([group_col, status_col]).size().unstack(fill_value=0)
    fig, ax = plt.subplots(figsize=(10,5))
    status_counts.plot(kind='bar', stacked=True, ax=ax, colormap='tab20')
    ax.set_ylabel("Count")
    ax.set_title(f"{title_prefix} - All Statuses")
    ax.tick_params(axis='x', rotation=45)
    st.pyplot(fig)
    return status_counts

# ====== 1. Main status plot ======
st.subheader("Main Status Distribution")
plot_status_counts(df, "Status per Group")

# ====== 2. Separate plots ======
def plot_single_status(data, status_value, color):
    subset = data[data[status_col] == status_value]
    counts = subset[group_col].value_counts()
    fig, ax = plt.subplots(figsize=(8,4))
    sns.barplot(x=counts.index, y=counts.values, palette=[color], ax=ax)
    ax.set_ylabel("Count")
    ax.set_xlabel("Group")
    ax.set_title(f"{status_value.capitalize()} per Group")
    ax.tick_params(axis='x', rotation=45)
    st.pyplot(fig)

st.subheader("Solved per Group")
plot_single_status(df, 'solved', '#4CAF50')

st.subheader("Follow up per Group")
plot_single_status(df, 'follow up', '#FFC107')

st.subheader("Not solved per Group")
plot_single_status(df, 'not solved', '#F44336')

# ====== 3. Link ratio in Solved ======
st.subheader("Link Ratio in Solved")

def link_stats(data):
    df_solved = data[data[status_col] == 'solved']
    df_solved[link_col] = df_solved[link_col].astype(str).str.strip()
    df_solved['Has Link'] = df_solved[link_col].apply(lambda x: 'Link' if x != '' and x.lower() != 'nan' else 'Empty')
    return df_solved['Has Link'].value_counts()

link_before = link_stats(df)

fig, ax = plt.subplots(figsize=(6,6))
ax.pie(link_before, labels=link_before.index, autopct='%1.1f%%', colors=['#4CAF50','#FF5722'])
ax.set_title("Links in Solved")
st.pyplot(fig)

# ====== 5. Rating Analysis ======
st.subheader("Experience Rating (1-3)")
rating_counts = df[rating_col].value_counts().sort_index()
fig, ax = plt.subplots(figsize=(6,5))
sns.barplot(x=rating_counts.index, y=rating_counts.values, palette="viridis", ax=ax)
ax.set_xlabel("Rating")
ax.set_ylabel("Count")
ax.set_title("Rating Distribution")
st.pyplot(fig)

# ====== 6. Summary Table ======
st.subheader("Summary Table")
summary_table = {
    "Total Rows": len(df),
    "Total Groups": df[group_col].nunique(),
    "Solved": (df[status_col] == 'solved').sum(),
    "Follow up": (df[status_col] == 'follow up').sum(),
    "Not solved": (df[status_col] == 'not solved').sum(),
    "Links": link_before.get('Link', 0),
    "Empty Links": link_before.get('Empty', 0)
}
st.table(pd.DataFrame(list(summary_table.items()), columns=["Metric", "Value"]))

st.success("✅ Dashboard ready")
