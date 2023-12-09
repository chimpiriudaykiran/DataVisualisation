import os
from datetime import datetime

import pyttsx3

from DataVisualisation import settings
from home.dash_apps.finished_apps.Text_to_Speech import synthesize_text
from home.dash_apps.finished_apps.getDownloadFolder import get_downloads_folder

def list_filenames_in_directory(directory_path):

    try:
        all_files = os.listdir(directory_path)

        # Filter for Excel and CSV files
        excel_csv_files = [f for f in all_files if f.endswith('.xlsx') or f.endswith('.xls') or f.endswith('.csv')]
        numbered_files = [f"{index + 1}. {filename}" for index, filename in enumerate(excel_csv_files)]
        return excel_csv_files, numbered_files

    except FileNotFoundError:
        print("Directory not found.")
        return []


# Example usage
# downloads_folder_path = get_downloads_folder()
# filenames, numbered_files = list_filenames_in_directory(downloads_folder_path)
#
# # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
# # audio_filename = f'audio/files_audio_{timestamp}.mp3'
# #
# # audio_file_path = os.path.join(settings.MEDIA_ROOT, audio_filename)
# # synthesize_text(numbered_files, audio_file_path)
# # audio_url = settings.MEDIA_URL + audio_filename
#
# print(numbered_files)