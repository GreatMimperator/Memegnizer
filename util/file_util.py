import os


def get_file_name_without_extension(file_name: str):
    return os.path.splitext(file_name)[0]


def list_dir_no_ext(dir_path: str) -> list[str]:
    filenames = os.listdir(dir_path)
    filenames_no_ext = []
    for filename in filenames:
        filenames_no_ext.append(get_file_name_without_extension(filename))
    return filenames_no_ext
