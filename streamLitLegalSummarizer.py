import streamlit as st
import pandas as pd

class CaseDigestAssigner:
    def __init__(self, num_groups=6, existing_loads=None):
        self.num_groups = num_groups
        # Accept existing page load per group if provided
        self.existing_loads = existing_loads if existing_loads else [0] * num_groups

    def assign_cases(self, cases):
        """
        cases: list of tuples (case_name, num_pages)
        returns: dict {group_number: [(case_name, num_pages), ...]}
        """
        # Initialize groups with existing load
        groups = [(self.existing_loads[group_id-1], group_id, []) for group_id in range(1, self.num_groups + 1)]

        # Sort cases by descending number of pages (greedy balancing)
        cases_sorted = sorted(cases, key=lambda x: x[1], reverse=True)

        for case_name, num_pages in cases_sorted:
            # Find group with minimum pages so far
            groups.sort(key=lambda g: g[0])
            total_pages, group_id, case_list = groups[0]
            case_list.append((case_name, num_pages))
            total_pages += num_pages
            groups[0] = (total_pages, group_id, case_list)

        # Convert to dictionary output
        assignments = {}
        for total_pages, group_id, case_list in groups:
            assignments[group_id] = {
                "total_pages": total_pages,
                "cases": case_list
            }

        return assignments

# Streamlit app
st.title("📚 Case Digest Assigner")
st.write("This app assigns cases into 6 groups while balancing the page load.")

st.write("### Step 1: Provide Existing Page Loads")
existing_load_input = st.text_input("Enter existing total page loads for 6 groups (comma-separated)", "0,0,0,0,0,0")
try:
    existing_loads = [int(x.strip()) for x in existing_load_input.split(",")]
    if len(existing_loads) != 6:
        st.error("You must provide exactly 6 numbers.")
        existing_loads = [0]*6
except:
    st.error("Invalid format. Defaulting to zero loads.")
    existing_loads = [0]*6

uploaded_file = st.file_uploader("Upload a CSV file with two columns: Case Name, Number of Pages", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    if "Case Name" in df.columns and "Number of Pages" in df.columns:
        cases = [(row["Case Name"], int(row["Number of Pages"])) for _, row in df.iterrows()]

        assigner = CaseDigestAssigner(num_groups=6, existing_loads=existing_loads)
        result = assigner.assign_cases(cases)

        export_data = []
        summary_data = []
        for group, data in result.items():
            st.subheader(f"Group {group} (New Total Pages: {data['total_pages']})")
            df_out = pd.DataFrame(data["cases"], columns=["Case Name", "Pages"])
            st.table(df_out)
            for case in data["cases"]:
                export_data.append([group, case[0], case[1], data["total_pages"]])
            summary_data.append([group, data["total_pages"]])

        # Show summary table of all groups
        st.write("### 📊 Group Totals Summary")
        summary_df = pd.DataFrame(summary_data, columns=["Group", "New Total Pages"])
        st.table(summary_df)

        # Create downloadable file
        export_df = pd.DataFrame(export_data, columns=["Group", "Case Name", "Pages", "New Total Pages"])
        csv = export_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Assignment CSV", data=csv, file_name="case_assignments.csv", mime="text/csv")
    else:
        st.error("CSV must have 'Case Name' and 'Number of Pages' columns.")

st.write("Or, enter cases manually:")
case_input = st.text_area("Enter cases (format: Case Name - Pages, one per line)")

if st.button("Assign Cases") and case_input.strip():
    try:
        cases = []
        for line in case_input.strip().split("\n"):
            name, pages = line.split("-")
            cases.append((name.strip(), int(pages.strip())))

        assigner = CaseDigestAssigner(num_groups=6, existing_loads=existing_loads)
        result = assigner.assign_cases(cases)

        export_data = []
        summary_data = []
        for group, data in result.items():
            st.subheader(f"Group {group} (New Total Pages: {data['total_pages']})")
            df_out = pd.DataFrame(data["cases"], columns=["Case Name", "Pages"])
            st.table(df_out)
            for case in data["cases"]:
                export_data.append([group, case[0], case[1], data["total_pages"]])
            summary_data.append([group, data["total_pages"]])

        # Show summary table of all groups
        st.write("### 📊 Group Totals Summary")
        summary_df = pd.DataFrame(summary_data, columns=["Group", "New Total Pages"])
        st.table(summary_df)

        export_df = pd.DataFrame(export_data, columns=["Group", "Case Name", "Pages", "New Total Pages"])
        csv = export_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Assignment CSV", data=csv, file_name="case_assignments.csv", mime="text/csv")
    except Exception as e:
        st.error(f"Error: {e}")
