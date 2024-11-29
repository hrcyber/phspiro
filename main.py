import streamlit as st
import sqlite3
import pandas as pd
from fpdf import FPDF
import os

# Initialize the SQLite database
def init_db():
    conn = sqlite3.connect("class_notes.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_name TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Add a new note
def add_note(class_name, title, content):
    conn = sqlite3.connect("class_notes.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO notes (class_name, title, content) VALUES (?, ?, ?)", (class_name, title, content))
    conn.commit()
    conn.close()

# Retrieve notes for a specific class
def get_notes(class_name):
    conn = sqlite3.connect("class_notes.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notes WHERE class_name = ?", (class_name,))
    rows = cursor.fetchall()
    conn.close()
    return rows

# Update an existing note
def update_note(id, title, content):
    conn = sqlite3.connect("class_notes.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE notes SET title = ?, content = ? WHERE id = ?", (title, content, id))
    conn.commit()
    conn.close()

# Delete a note
def delete_note(id):
    conn = sqlite3.connect("class_notes.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM notes WHERE id = ?", (id,))
    conn.commit()
    conn.close()

# Generate PDF for notes
def generate_pdf(data, class_name):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    try:
        # Add Unicode-compatible font (requires TTF file)
        pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
        pdf.set_font("DejaVu", size=12)
    except RuntimeError:
        # Fallback to default font
        pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt=f"Notes for {class_name}", ln=True, align="C")
    pdf.ln(10)

    for row in data:
        pdf.set_font("Arial", style="B", size=12)
        pdf.cell(0, 10, f"Title: {row[2]}", ln=True)
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, f"Content: {row[3]}")
        pdf.ln(5)

    pdf_file = f"{class_name}_notes.pdf"
    pdf.output(pdf_file)
    return pdf_file

# Streamlit application
def main():
    st.title("📚 Class Notes Management")

    # Initialize the database
    init_db()

    # List of classes
    classes = ["LKG", "UKG", "Class 1", "Class 2", "Class 3", "Class 4",
               "Class 5", "Class 6", "Class 7", "Class 8", "Class 9", "Class 10"]
    selected_class = st.sidebar.selectbox("Select a Class", classes)

    # Sidebar menu
    menu = st.sidebar.selectbox("Menu", ["Add Note", "View Notes", "Download PDF"])

    # Add a note
    if menu == "Add Note":
        st.header(f"Add a New Note for {selected_class}")
        with st.form("add_note_form"):
            title = st.text_input("Note Title")
            content = st.text_area("Note Content")
            submitted = st.form_submit_button("Save Note")

            if submitted:
                if title and content:
                    add_note(selected_class, title, content)
                    st.success(f"Note added successfully for {selected_class}!")
                else:
                    st.error("Please fill in both the title and the content.")

    # View and manage notes
    elif menu == "View Notes":
        st.header(f"View and Manage Notes for {selected_class}")
        data = get_notes(selected_class)

        if data:
            df = pd.DataFrame(data, columns=["ID", "Class", "Title", "Content"])
            st.dataframe(df[["ID", "Title", "Content"]], use_container_width=True)

            st.subheader("Edit or Delete a Note")
            selected_id = st.selectbox("Select a Note ID:", options=[row[0] for row in data])

            if selected_id:
                entry = next((row for row in data if row[0] == selected_id), None)
                if entry:
                    with st.form("edit_delete_form"):
                        new_title = st.text_input("Edit Title", value=entry[2])
                        new_content = st.text_area("Edit Content", value=entry[3])
                        update_btn = st.form_submit_button("Update Note")
                        delete_btn = st.form_submit_button("Delete Note")

                        if update_btn:
                            update_note(entry[0], new_title, new_content)
                            st.success("Note updated successfully!")
                        if delete_btn:
                            delete_note(entry[0])
                            st.success("Note deleted successfully!")

        else:
            st.info(f"No notes found for {selected_class}. Add a note first.")

    # Download notes as PDF
    elif menu == "Download PDF":
        st.header(f"Download Notes for {selected_class} as PDF")
        data = get_notes(selected_class)

        if data:
            if st.button("Generate PDF"):
                pdf_file = generate_pdf(data, selected_class)
                with open(pdf_file, "rb") as file:
                    st.download_button(
                        label="Download PDF",
                        data=file,
                        file_name=f"{selected_class}_notes.pdf",
                        mime="application/pdf"
                    )
        else:
            st.info(f"No notes to download for {selected_class}. Add some notes first.")

if __name__ == "__main__":
    main()
