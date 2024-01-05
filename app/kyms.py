import os
import zipfile
import streamlit as st
from generate_podcast import generate_podcast

# Set Streamlit page configuration
st.set_page_config(page_title="Podcast Generator", page_icon="🎙️")


# Streamlit app
def main():
    st.title("Podcast Generator")

    # User input form
    name = st.text_input("Podcast Name:")
    desc = st.text_area("Podcast Description:")
    topic1 = st.text_input("Topic 1:")
    topic2 = st.text_input("Topic 2:")
    topic3 = st.text_input("Topic 3:")
    advert1 = st.text_input("Advertisement 1:")
    advert2 = st.text_input("Advertisement 2:")

    if st.button("Generate Podcast"):
        # Generate the podcast
        topics = [topic1, topic2, topic3]
        adverts = [advert1, advert2]
        mp3_file, txt_file = generate_podcast(name, desc, topics, adverts)

        # Set the working directory to the script's directory
        script_directory = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_directory)

        # Use relative paths for the files, assuming the script is in the 'app' directory
        mp3_file = os.path.join(".", "downloads", mp3_file)
        txt_file = os.path.join(".", "downloads", txt_file)

        zip_folder = os.path.join(".", "downloads")
        zip_filename = f"{zip_folder}/{name}_podcast.zip"

        # Ensure the output directory exists
        os.makedirs(zip_folder, exist_ok=True)

        # Zip the two files
        with zipfile.ZipFile(zip_filename, "w") as zip_file:
            zip_file.write(mp3_file, arcname=os.path.basename(mp3_file))
            zip_file.write(txt_file, arcname=os.path.basename(txt_file))

        # Send the zip file to the user for download
        st.success("Podcast generated successfully!")
        st.markdown(f"[Download Podcast Zip]({zip_filename})", unsafe_allow_html=True)


# Run the Streamlit app
if __name__ == "__main__":
    main()
