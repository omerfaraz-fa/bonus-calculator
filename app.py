import streamlit as st
import pandas as pd
import io

# --- Bonus ladder function ---
def calculate_bonus(diff_percent, baseline):
    """Calculate bonus using 5% ladder logic."""
    tiers = [
        (0, 5, 370),
        (5, 10, 740),
        (10, 15, 1110),
        (15, 20, 1480),
        (20, 25, 1850),
    ]

    bonus = baseline
    for start, end, rate in tiers:
        if diff_percent > start:
            covered = min(diff_percent, end) - start
            bonus += covered * rate
    return round(bonus, 2)


# --- Load Excel data ---
def load_data(file):
    xls = pd.ExcelFile(file)
    agents = pd.read_excel(xls, "Agents")
    perf = pd.read_excel(xls, "Performance")
    buckets = pd.read_excel(xls, "Buckets")
    return agents, perf, buckets


# --- Streamlit UI ---
st.title("Quarterly Bonus Calculator 💰")

# File uploader
uploaded_file = st.file_uploader("Upload latest Excel file", type=["xlsx"])

if uploaded_file:
    st.info("Using uploaded Excel file ✅")
    agents_df, perf_df, buckets_df = load_data(uploaded_file)
    # Keep a copy in memory for re-download
    uploaded_bytes = uploaded_file.getvalue()
else:
    st.warning("No Excel uploaded. Using default bonus_calculator.xlsx (demo data).")
    default_path = "bonus_calculator.xlsx"  # make sure this file exists in repo
    agents_df, perf_df, buckets_df = load_data(default_path)
    with open(default_path, "rb") as f:
        uploaded_bytes = f.read()

# Allow download of the current Excel file
st.download_button(
    label="Download Current Excel File",
    data=uploaded_bytes,
    file_name="bonus_calculator.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# Choose mode
view_mode = st.radio("Choose view:", ["Single Agent", "All Agents"])

if view_mode == "Single Agent":
    agent_name = st.selectbox("Select an agent", agents_df["Agent"].unique())

    if agent_name:
        agent_info = agents_df[agents_df["Agent"] == agent_name].iloc[0]
        perf_info = perf_df[perf_df["Agent"] == agent_name].iloc[0]

        salary = agent_info["Quarterly Salary"]
        bonus_pool = agent_info["Bonus Pool (40%)"]
        baseline = agent_info["Baseline Bonus"]
        actual = perf_info["Actual OTP Elkjop"]
        target = perf_info["Target OTP Elkjop"]
        diff_percent = actual - target

        st.subheader(f"Agent: {agent_name}")
        st.write(f"**Country:** {agent_info['Country']}")
        st.write(f"**Quarterly Salary:** {salary:,.0f}")
        st.write(f"**Bonus Pool (40%):** {bonus_pool:,.0f}")
        st.write(f"**Baseline Bonus:** {baseline:,.0f}")
        st.write(f"**Target OTP Elkjop:** {target}%")
        st.write(f"**Actual OTP Elkjop:** {actual}%")
        st.write(f"**Difference:** {diff_percent:.1f}%")

        payout = calculate_bonus(diff_percent, baseline)
        st.success(f"**Calculated Bonus Payout: {payout:,.0f} NOK**")

elif view_mode == "All Agents":
    results = []
    for _, row in agents_df.iterrows():
        name = row["Agent"]
        baseline = row["Baseline Bonus"]
        salary = row["Quarterly Salary"]
        country = row["Country"]

        perf_row = perf_df[perf_df["Agent"] == name].iloc[0]
        diff_percent = perf_row["Actual OTP Elkjop"] - perf_row["Target OTP Elkjop"]
        payout = calculate_bonus(diff_percent, baseline)

        results.append({
            "Agent": name,
            "Country": country,
            "Quarterly Salary": salary,
            "Baseline Bonus": baseline,
            "Diff %": diff_percent,
            "Calculated Bonus": payout
        })

    summary_df = pd.DataFrame(results)
    st.subheader("All Agents Bonus Summary")
    st.dataframe(summary_df)

    # Allow CSV download of results
    csv = summary_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download Bonus Results (CSV)",
        data=csv,
        file_name="bonus_summary.csv",
        mime="text/csv",
    )

# Show buckets for reference
st.subheader("Bonus Buckets (for reference)")
st.dataframe(buckets_df)
