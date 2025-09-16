import streamlit as st
import pandas as pd
import io

# --- Password protection ---
st.sidebar.title("Login")
password = st.sidebar.text_input("Enter password", type="password")

# ✅ Password is "workshop"
if password != "workshop":
    st.warning("Please enter the correct password to access the app.")
    st.stop()

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
    cmms = pd.read_excel(xls, "Agents")      # rename sheet to "Agents" but column = CMM
    perf = pd.read_excel(xls, "Performance")
    buckets = pd.read_excel(xls, "Buckets")
    return cmms, perf, buckets


st.title("Quarterly Bonus Calculator 💰")

# --- File uploader ---
uploaded_file = st.file_uploader("Upload latest Excel file", type=["xlsx"])

if uploaded_file:
    st.info("Using uploaded Excel file ✅")
    cmms_df, perf_df, buckets_df = load_data(uploaded_file)
    uploaded_bytes = uploaded_file.getvalue()
else:
    st.warning("No Excel uploaded. Using default bonus_calculator.xlsx (demo data).")
    default_path = "bonus_calculator.xlsx"
    cmms_df, perf_df, buckets_df = load_data(default_path)
    with open(default_path, "rb") as f:
        uploaded_bytes = f.read()

# --- Download current Excel file ---
st.download_button(
    label="Download Current Excel File",
    data=uploaded_bytes,
    file_name="bonus_calculator.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# --- Choose view ---
view_mode = st.radio("Choose view:", ["Single CMM", "All CMMs"])

if view_mode == "Single CMM":
    cmm_name = st.selectbox("Select a CMM", cmms_df["CMM"].unique())

    if cmm_name:
        cmm_info = cmms_df[cmms_df["CMM"] == cmm_name].iloc[0]
        perf_info = perf_df[perf_df["CMM"] == cmm_name].iloc[0]

        salary = cmm_info["Quarterly Salary"]
        bonus_pool = cmm_info["Bonus Pool (40%)"]
        baseline = cmm_info["Baseline Bonus"]
        actual = perf_info["Actual OTP Elkjop"]
        target = perf_info["Target OTP Elkjop"]
        diff_percent = actual - target

        st.subheader(f"CMM: {cmm_name}")
        st.write(f"**Country:** {cmm_info['Country']}")
        st.write(f"**Quarterly Salary:** {salary:,.0f}")
        st.write(f"**Bonus Pool (40%):** {bonus_pool:,.0f}")
        st.write(f"**Baseline Bonus:** {baseline:,.0f}")
        st.write(f"**Target OTP Elkjop:** {target}%")
        st.write(f"**Actual OTP Elkjop:** {actual}%")
        st.write(f"**Difference:** {diff_percent:.1f}%")

        payout = calculate_bonus(diff_percent, baseline)
        st.success(f"**Calculated Bonus Payout: {payout:,.0f} NOK**")

elif view_mode == "All CMMs":
    results = []
    for _, row in cmms_df.iterrows():
        name = row["CMM"]
        baseline = row["Baseline Bonus"]
        salary = row["Quarterly Salary"]
        country = row["Country"]

        perf_row = perf_df[perf_df["CMM"] == name].iloc[0]
        diff_percent = perf_row["Actual OTP Elkjop"] - perf_row["Target OTP Elkjop"]
        payout = calculate_bonus(diff_percent, baseline)

        results.append({
            "CMM": name,
            "Country": country,
            "Quarterly Salary": salary,
            "Baseline Bonus": baseline,
            "Diff %": diff_percent,
            "Calculated Bonus": payout
        })

    summary_df = pd.DataFrame(results)
    st.subheader("All CMM Bonus Summary")
    st.dataframe(summary_df)

    # Allow CSV download of results
    csv = summary_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download Bonus Results (CSV)",
        data=csv,
        file_name="bonus_summary.csv",
        mime="text/csv",
    )

# --- Show Buckets for reference ---
st.subheader("Bonus Buckets (for reference)")
st.dataframe(buckets_df)
