from typing import Optional

from sqlalchemy import *
from sqlalchemy.orm import Session

from db.models import *


def select_processed_dir_related_file_ids_query(processed_dir_path):
    return (
        select(File.id)
        .where(File.namespace_dir_path == processed_dir_path)
    )


def delete_prompts_for_processed_dir_related_files_query(processed_dir_path):
    return (
        delete(Prompt)
        .where(
            Prompt.file_id
            .in_(select_processed_dir_related_file_ids_query(processed_dir_path))
        )
    )


def select_already_received_prompts_filenames_query(processed_dir_path):
    return (
        select(File.filename_without_extension)
        .where(File.namespace_dir_path == processed_dir_path)
    )


def select_already_received_prompts_filenames(processed_dir_path, *, connection: Connection):
    return [row[0] for row in connection.execute(select_already_received_prompts_filenames_query(processed_dir_path))]


def select_file_id_query(processed_dir_path, filename_without_extension):
    return (
        select(File.id)
        .filter(
            and_(
                File.namespace_dir_path == processed_dir_path,
                File.filename_without_extension == filename_without_extension
            )
        )
    )


def select_file_id(processed_dir_path, filename_without_extension, *, connection: Connection) -> Optional[int]:
    row_or_none = connection.execute(
        select_file_id_query(processed_dir_path, filename_without_extension)
    ).one_or_none()
    return row_or_none[0] if row_or_none else None


def insert_file_get_id(processed_dir_path, filename_without_extension, *, session: Session) -> int:
    inserted_file = session.execute(
        insert(File)
        .values(
            namespace_dir_path=processed_dir_path,
            filename_without_extension=filename_without_extension
        )
    )
    return inserted_file.inserted_primary_key[0]
