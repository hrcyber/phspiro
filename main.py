import streamlit as st
import sqlite3
#from docx import *
from docxtpl import DocxTemplate
import pandas as pd
from PIL import Image


rr = Image.open("sr.jpg")
srw = Image.open("sr2.jpg")
fr = Image.open("fr.jpg")


st.image(
    rr,
    width= 1200,
    channels="RGB"
)
st.image(
    srw,
    width= 1200,
    channels="RGB"
)

st.image(
    fr,
    width= 1200,
    channels="RGB"
)



# Initialize SQLite Database
def init_database():
    conn = sqlite3.connect("class_notes.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS class_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_name TEXT,
            note TEXT,
            date TEXT
        )
    """)
    conn.commit()
    conn.close()


# Function to add new note for a specific class
def add_note_to_class(class_name, note, date):
    conn = sqlite3.connect("class_notes.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO class_notes (class_name, note, date)
        VALUES (?, ?, ?)
    """, (class_name, note, date))
    conn.commit()
    conn.close()


# Fetch all notes for a specific class
def fetch_notes_by_class(class_name):
    conn = sqlite3.connect("class_notes.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM class_notes WHERE class_name = ? ORDER BY date DESC", (class_name,))
    entries = cursor.fetchall()
    conn.close()
    return entries


# Fetch a specific note by ID
def fetch_note_by_id(note_id):
    conn = sqlite3.connect("class_notes.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM class_notes WHERE id = ?", (note_id,))
    entry = cursor.fetchone()
    conn.close()
    return entry


# Update a note
def update_note_by_id(note_id, class_name, note, date):
    conn = sqlite3.connect("class_notes.db")
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE class_notes 
        SET class_name = ?, note = ?, date = ?
        WHERE id = ?
    """, (class_name, note, date, note_id))
    conn.commit()
    conn.close()


# Delete a note
def delete_note_by_id(note_id):
    conn = sqlite3.connect("class_notes.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM class_notes WHERE id = ?", (note_id,))
    conn.commit()
    conn.close()


# Generate .docx file with all notes for a specific class
def generate_docx_for_class(class_name, notes):
    doc = Document()
    doc.add_heading(f'{class_name} Notes', 0)

    for entry in notes:
        doc.add_heading(f"Note ID: {entry[0]}", level=1)
        doc.add_paragraph(f"Date: {entry[3]}")
        doc.add_paragraph(f"Note: {entry[2]}")
        doc.add_paragraph("\n" + "-" * 50 + "\n")

    doc_path = f"{class_name}_notes.docx"
    doc.save(doc_path)
    return doc_path


# Streamlit App UI
def main():
    st.title("📝 PUSHPA HIGH SCHOOL")

    # Sidebar menu with class options
    menu = st.sidebar.radio(
        "Select Class",
        ("Home", "Teacher's Application", "Class UKG", "Class 1", "Class 2", "Class 3", "Class 4", "Class 5", "Class 6", "Class 7",
         "Class 8", "Class 9", "Class 10")
    )

    # Display content based on selected class
    if menu == "Home":
        st.header("🏠 Welcome to the Home Page")
        st.write("Created by Naseem Khan  Pushpa High School. (Software Developer)")

    else:
        class_name = menu
        st.header(f"📚 {class_name} Notes")

        # Option to Add New Notes
        with st.form("add_note_form"):
            note_input = st.text_area("Write your note here:")
            date_input = st.date_input("Date", value=pd.to_datetime("today").date())
            add_note_button = st.form_submit_button("Add Note")

            if add_note_button and note_input:
                add_note_to_class(class_name, note_input, str(date_input))
                st.success(f"Note added for {class_name} on {date_input}")
            elif add_note_button:
                st.error("Please write a note before submitting.")

        # Display Notes for the selected class
        notes = fetch_notes_by_class(class_name)
        if notes:
            # Show Notes
            df = pd.DataFrame(notes, columns=["ID", "Class Name", "Note", "Date"])
            st.dataframe(df)

            # Option to update or delete notes
            note_id_to_update = st.selectbox("Select Note to Update/Delete", options=[entry[0] for entry in notes])
            selected_note = fetch_note_by_id(note_id_to_update)

            # Update the note
            with st.form("update_note_form"):
                new_note = st.text_area("Update Note", value=selected_note[2])
                new_date = st.date_input("Update Date", value=pd.to_datetime(selected_note[3]).date())
                update_button = st.form_submit_button("Update Note")

                if update_button and new_note:
                    update_note_by_id(note_id_to_update, class_name, new_note, str(new_date))
                    st.success("Note updated!")

                # Delete the note
                delete_button = st.form_submit_button("Delete Note")
                if delete_button:
                    delete_note_by_id(note_id_to_update)
                    st.success("Note deleted!")

            # Option to download the notes as a .docx file
            if st.button(f"Download {class_name} Notes as .docx"):
                generate_docx_for_class(class_name, notes)
                with open(f"{class_name}_notes.docx", "rb") as file:
                    st.download_button(
                        label="Download Notes",
                        data=file,
                        file_name=f"{class_name}_notes.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
        else:
            st.info(f"No notes found for {class_name}. Add a note above!")


if __name__ == "__main__":
    init_database()  # Initialize the database
    main()  # Run the main Streamlit app
