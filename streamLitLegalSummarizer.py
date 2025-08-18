import heapq
import streamlit as st

class CaseDigestAssigner:
    def __init__(self, num_groups=6):
        self.num_groups = num_groups

    def assign_cases(self, cases):
        """
        cases: list of tuples (case_name, num_pages)
        returns: dict {group_number: [(case_name, num_pages), ...]}
        """
        # Initialize groups with (total_pages, group_id, cases_list)
        groups = [(0, group_id, []) for group_id in range(1, self.num_groups + 1)]
        heapq.heapify(groups)  # min-heap based on total pages

        # Sort cases by descending number of pages (greedy balancing)
        cases_sorted = sorted(cases, key=lambda x: x[1], reverse=True)

        for case_name, num_pages in cases_sorted:
            total_pages, group_id, case_list = heapq.heappop(groups)
            case_list.append((case_name, num_pages))
            total_pages += num_pages
            heapq.heappush(groups, (total_pages, group_id, case_list))

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

uploaded_file = st.file_uploader("Upload a CSV file with two columns: Case Name, Number of Pages", type=["csv"])

if uploaded_file is not None:
    import pandas as pd
    df = pd.read_csv(uploaded_file)

    if "Case Name" in df.columns and "Number of Pages" in df.columns:
        cases = [(row["Case Name"], int(row["Number of Pages"])) for _, row in df.iterrows()]

        assigner = CaseDigestAssigner(num_groups=6)
        result = assigner.assign_cases(cases)

        for group, data in result.items():
            st.subheader(f"Group {group} (Total Pages: {data['total_pages']})")
            st.table(pd.DataFrame(data["cases"], columns=["Case Name", "Pages"]))
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

        assigner = CaseDigestAssigner(num_groups=6)
        result = assigner.assign_cases(cases)

        for group, data in result.items():
            st.subheader(f"Group {group} (Total Pages: {data['total_pages']})")
            st.table(pd.DataFrame(data["cases"], columns=["Case Name", "Pages"]))
    except Exception as e:
        st.error(f"Error: {e}")
