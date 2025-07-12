# import os
# import streamlit as st

# st.title("📂 Set Up Your File Paths")

# # --- Input fields for folder paths ---
# raw_folder = st.text_input("📥 Path to folder with raw files", value="./data/raw")
# processed_folder = st.text_input("📤 Path to folder for processed files", value="./data/processed")

# # --- Validate paths ---
# if not os.path.exists(raw_folder):
#     st.error(f"❌ The raw folder path '{raw_folder}' does not exist.")
# else:
#     st.success("✅ Raw folder path looks good!")

# if not os.path.exists(processed_folder):
#     st.warning(f"⚠️ The processed folder path '{processed_folder}' does not exist.")
#     create = st.button("📁 Create processed folder")
#     if create:
#         os.makedirs(processed_folder)
#         st.success(f"✅ Created folder: {processed_folder}")
# else:
#     st.success("✅ Processed folder path is valid.")

# # --- Save paths in session_state for later use ---
# st.session_state["raw_folder"] = raw_folder
# st.session_state["processed_folder"] = processed_folder
