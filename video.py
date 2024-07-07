#MADE IN BRAZUCANY
#AQUI MEU YOU TUBE = https://www.youtube.com/channel/UCa2pvMyLz1LNIDy2qvlV2kw
#POR TER MUITOS ARQUIVOS DE VIDEO E SOMENTE PODENDO EDITAR ELES SEMANAS DEPOIS ESTE ARQUIVO FOI CRIADO. 

import os
import subprocess
import json
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_creation_time(video_file):
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-print_format', 'json', '-show_format', video_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        video_info = json.loads(result.stdout)
        creation_time = video_info['format']['tags'].get('creation_time')
        if creation_time:
            return datetime.fromisoformat(creation_time.replace('Z', '+00:00'))
        else:
            logging.warning(f"No creation time found for {video_file}")
            return None
    except Exception as e:
        logging.error(f"Error occurred while getting creation time for {video_file}: {e}")
        return None

def get_file_size(video_file):
    try:
        size = os.path.getsize(video_file)
        return size
    except Exception as e:
        logging.error(f"Error occurred while getting file size for {video_file}: {e}")
        return -1

def list_video_files(directory):
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv']
    video_files = []
    try:
        all_files = os.listdir(directory)
        for file in all_files:
            if any(file.lower().endswith(ext) for ext in video_extensions):
                video_files.append(file)
        logging.debug(f"Video files in directory: {video_files}")
    except Exception as e:
        logging.error(f"Error occurred while listing files in {directory}: {e}")
    return video_files

def process_files(directory):
    video_files = list_video_files(directory)
    file_info = []
    for video_file in video_files:
        full_path = os.path.join(directory, video_file)
        logging.debug(f"Processing file: {full_path}")
        creation_time = get_creation_time(full_path)
        if creation_time:
            file_size = get_file_size(full_path)
            if file_size > 0:
                file_info.append((full_path, creation_time, file_size))
            else:
                logging.warning(f"Skipping file {video_file} due to invalid file size.")
        else:
            logging.warning(f"Skipping file {video_file} due to missing creation time.")
    return file_info

def rename_files_in_order(file_info):
    file_info.sort(key=lambda x: (x[1], x[2]))  # Sort files based on creation time and file size
    existing_names = set()

    for idx, (file_path, _, _) in enumerate(file_info):
        file_name, file_extension = os.path.splitext(file_path)
        new_name = f"video_{idx + 1:02}{file_extension}"  # Format as video_01.MOV, video_02.MOV, ...

        # Check for duplicates
        while new_name in existing_names:
            idx += 1
            new_name = f"video_{idx:02}{file_extension}"
        
        existing_names.add(new_name)

        # Attempt to rename the file
        try:
            os.rename(file_path, os.path.join(os.path.dirname(file_path), new_name))
            logging.info(f"Renamed {file_path} to {new_name} (Size: {get_file_size(os.path.join(os.path.dirname(file_path), new_name))} bytes)")
        except FileExistsError:
            logging.warning(f"File {new_name} already exists. Renaming {file_path} to {new_name[:-4]}_DUPLICATED{file_extension}")
            os.rename(file_path, f"{new_name[:-4]}_DUPLICATED{file_extension}")
        except Exception as e:
            logging.error(f"Failed to rename {file_path} to {new_name}: {e}")

def main(directory):
    logging.info(f"Processing video files in directory: {directory}")
    file_info = process_files(directory)

    if file_info:
        logging.info("All files processed. Proceeding to rename.")
        rename_files_in_order(file_info)
    else:
        logging.warning("No valid video files found or all files were skipped due to errors.")

if __name__ == "__main__":
    directory = os.path.dirname(os.path.abspath(__file__))  # Get current script directory
    main(directory)
