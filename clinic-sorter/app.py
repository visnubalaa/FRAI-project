import json
from datetime import datetime
import pandas as pd
import streamlit as st
from classifier import process_complaint, VALID_CATEGORIES, VALID_PRIORITIES
from storage import load_records, add_record, update_reviewed, delete_record


st.set_page_config(page_title="Clinic Visitor Sorter", page_icon="🏥", layout="wide")
st.title("🏥 Clinic Visitor Sorter")
st.caption("AI-assisted complaint sorting for the college health-centre nurse. Classification is only a support tool; the nurse makes all decisions.")


# Simple navigation in the sidebar
page = st.sidebar.radio("Navigate", ["Dashboard", "New Complaint", "Nurse Queue", "About / Safety"])
records = load_records()

if page == "Dashboard":
    st.subheader("Dashboard overview")
    total = len(records)
    pending = sum(not r.get("reviewed", False) for r in records)
    urgent = sum(r.get("classification", {}).get("priority") == "see_now" for r in records)
    today_count = sum(r.get("classification", {}).get("priority") == "today" for r in records)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total complaints", total)
    c2.metric("Awaiting nurse review", pending)
    c3.metric("Immediate attention", urgent)
    c4.metric("Review today", today_count)
    st.divider()
    if records:
        df = pd.DataFrame([{
            "Time": r.get("created_at", "")[:19].replace("T", " "),
            "Queue ID": r.get("record_id", ""),
            "Category": r.get("classification", {}).get("category", "other"),
            "Priority": r.get("classification", {}).get("priority", "today"),
            "Status": "Reviewed" if r.get("reviewed") else "Pending",
            "Summary": r.get("classification", {}).get("summary", ""),
        } for r in records])
        st.write("Recent complaints")
        st.dataframe(df.head(10), use_container_width=True, hide_index=True)
    else:
        st.info("No complaints have been added yet. Use New Complaint to start.")

elif page == "New Complaint":
    st.subheader("Register a complaint")
    provider = st.radio("AI provider", ["Gemini", "Ollama (local)"], horizontal=True, help="Gemini needs an API key. Ollama needs the local model installed and running.")
    with st.form("complaint_form", clear_on_submit=True):
        complaint = st.text_area("Student complaint", placeholder="Type the student's complaint in English, Tamil, or Tanglish...", height=140)
        submitted = st.form_submit_button("Classify and add to nurse queue", type="primary")
    if submitted:
        if not complaint.strip():
            st.warning("Please enter a complaint first.")
        else:
            with st.spinner("Classifying complaint and checking safety rules..."):
                result = process_complaint(complaint, provider=provider.split()[0])
                record = add_record(result)
            st.success("Complaint added to nurse queue.")
            if record["status"] == "fallback_used":
                st.warning("AI classification could not be validated. Safe fallback was used; nurse review is required.")
            priority = record["classification"]["priority"]
            if priority == "see_now":
                st.error("Immediate attention flag: the nurse should review this complaint now.")
            st.json(record["classification"])
            st.caption(f"Queue ID: {record['record_id']} | Status: {record['status']}")

elif page == "Nurse Queue":
    st.subheader("Nurse queue")
    if not records:
        st.info("Queue is empty.")
    else:
        filter_priority = st.selectbox("Filter by priority", ["All", *VALID_PRIORITIES])
        filter_category = st.selectbox("Filter by category", ["All", *VALID_CATEGORIES])
        filtered = [r for r in records if (filter_priority == "All" or r.get("classification", {}).get("priority") == filter_priority) and (filter_category == "All" or r.get("classification", {}).get("category") == filter_category)]
        st.write(f"Showing {len(filtered)} of {len(records)} record(s)")
        for r in filtered:
            cls = r.get("classification", {})
            title = f"{r.get('record_id')} · {cls.get('priority', 'today').upper()} · {cls.get('category', 'other')} · {'Reviewed' if r.get('reviewed') else 'Pending'}"
            with st.expander(title, expanded=cls.get("priority") == "see_now"):
                st.markdown(f"**Received:** {r.get('created_at', '')}")
                st.markdown("**Original complaint:**")
                st.write(r.get("original_complaint", ""))
                st.markdown("**AI summary:**")
                st.write(cls.get("summary", ""))
                st.write(f"**Classification status:** `{r.get('status', '')}`")
                st.write(f"**Category:** `{cls.get('category', 'other')}`")
                st.write(f"**Priority:** `{cls.get('priority', 'today')}`")
                left, right = st.columns(2)
                if left.button("Mark reviewed" if not r.get("reviewed") else "Mark pending", key=f"review_{r['record_id']}"):
                    update_reviewed(r["record_id"], not r.get("reviewed", False))
                    st.rerun()
                if right.button("Delete record", key=f"delete_{r['record_id']}"):
                    delete_record(r["record_id"])
                    st.rerun()
        st.divider()
        csv_rows = [{
            "record_id": r.get("record_id"), "created_at": r.get("created_at"),
            "original_complaint": r.get("original_complaint"), "status": r.get("status"),
            "category": r.get("classification", {}).get("category"),
            "priority": r.get("classification", {}).get("priority"),
            "summary": r.get("classification", {}).get("summary"), "reviewed": r.get("reviewed", False),
        } for r in records]
        csv_data = pd.DataFrame(csv_rows).to_csv(index=False).encode("utf-8")
        st.download_button("Download queue as CSV", csv_data, file_name="clinic_nurse_queue.csv", mime="text/csv")

elif page == "About / Safety":
    st.subheader("Project information")
    st.markdown("This application classifies complaints into a queue category and urgency level for nurse review. It does **not** diagnose or recommend treatment.")
    st.markdown("**Categories:** " + ", ".join(VALID_CATEGORIES))
    st.markdown("**Priorities:** `see_now`, `today`, `routine`")
    st.markdown("**Validation:** response must be valid JSON with exactly three fields, approved category and priority, and a summary of 12 words or fewer.")
    st.markdown("**Retries:** invalid or failed AI response is retried once. After two failures, fallback category `other`, priority `today`, and neutral summary are used.")
    st.markdown("**Safety override:** selected red-flag phrases in the original complaint override the priority to `see_now`, including after fallback. Keyword checking is limited and may miss emergencies.")
    st.warning("This is a student prototype, not a medical triage system. If someone appears seriously unwell or may be in immediate danger, alert a healthcare professional or emergency service directly. Do not rely on this application.")
    st.caption("Queue data is stored locally in clinic-sorter/data/queue.json. Keep this prototype on a private device and do not enter unnecessary personal information.")
