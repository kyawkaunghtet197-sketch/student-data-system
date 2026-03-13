import streamlit as st
import pandas as pd
import os

# --- FILE PATH FOR DATA ---
# GitHub ပေါ်မှာ ဒေတာမပျက်အောင် CSV file နဲ့ သိမ်းဆည်းပါမယ်
DATA_FILE = "student_records.csv"

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=["name", "father", "book", "page"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# --- UI CONFIG ---
st.set_page_config(page_title="Student Data System", layout="centered")

# Custom CSS for Mobile
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #4CAF50; color: white; font-weight: bold; }
    .stTextInput>div>div>input { font-size: 18px; }
    </style>
    """, unsafe_allow_html=True)

data = load_data()

# --- SIDEBAR MENU ---
# Password စနစ် (ကွန်ပျူတာကနေ ဒေတာသွင်းတဲ့သူပဲ Menu အပြည့်မြင်ရအောင်)
with st.sidebar:
    st.title("Menu")
    access_mode = st.radio("Access Mode:", ["View (Mobile)", "Admin (PC)"])
    
    if access_mode == "Admin (PC)":
        password = st.text_input("Admin Password", type="password")
        if password != "1234": # စကားဝှက်ကို ဒီမှာ ပြောင်းနိုင်ပါတယ်
            st.warning("Please enter correct password to edit data.")
            choice = "Search Only"
        else:
            choice = st.radio("Admin Actions:", ["Data Entry", "Search Only", "View All", "Upload/Delete"])
    else:
        choice = "Search Only"

# --- 1. SEARCH ONLY (For Mobile Users) ---
if choice == "Search Only":
    st.subheader("🔍 Search Student Records")
    search_name = st.text_input("Type Name to Search")
    
    if search_name:
        results = data[data['name'].str.contains(search_name, case=False, na=False)]
        
        if not results.empty:
            if len(results) > 1:
                st.warning(f"Found {len(results)} records. Refine by Father Name:")
                father_list = results['father'].unique().tolist()
                selected_father = st.selectbox("Select Father Name", ["-- Choose --"] + father_list)
                
                if selected_father != "-- Choose --":
                    final_res = results[results['father'] == selected_father]
                    for idx, row in final_res.iterrows():
                        st.info(f"**Name:** {row['name']} | **Father:** {row['father']}\n\n**Book:** {row['book']} | **Page:** {row['page']}")
            else:
                row = results.iloc[0]
                st.success("Record Found!")
                st.info(f"**Name:** {row['name']} | **Father:** {row['father']}\n\n**Book:** {row['book']} | **Page:** {row['page']}")
        else:
            st.error("No data found.")

# --- 2. ADMIN: DATA ENTRY ---
elif choice == "Data Entry":
    st.subheader("📝 Admin: Data Entry Form")
    with st.form(key="admin_form", clear_on_submit=True):
        name = st.text_input("Name")
        father = st.text_input("Father")
        book = st.text_input("Book")
        page = st.text_input("Page")
        submit = st.form_submit_button("Save Record")
        
        if submit:
            if name and father:
                new_row = pd.DataFrame([[name, father, book, page]], columns=["name", "father", "book", "page"])
                data = pd.concat([data, new_row], ignore_index=True)
                save_data(data)
                st.success(f"Saved: {name}")
            else:
                st.error("Name and Father are required!")

# --- 3. ADMIN: VIEW ALL ---
elif choice == "View All":
    st.subheader("📊 All Records")
    st.dataframe(data, use_container_width=True)

# --- 4. ADMIN: UPLOAD / DELETE ---
elif choice == "Upload/Delete":
    st.subheader("⚙️ Data Management")
    uploaded_file = st.file_uploader("Upload Excel to add data", type=['xlsx'])
    if uploaded_file:
        df_new = pd.read_excel(uploaded_file)
        if st.button("Merge with Existing Data"):
            data = pd.concat([data, df_new], ignore_index=True)
            save_data(data)
            st.success("Data merged successfully!")
            
    if st.button("⚠️ Clear All Data"):
        if st.checkbox("Confirm Delete?"):
            data = pd.DataFrame(columns=["name", "father", "book", "page"])
            save_data(data)
            st.rerun()