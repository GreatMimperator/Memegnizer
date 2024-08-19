from typing import Optional, Sequence

from sqlalchemy import select, insert, delete, and_, Connection, Executable
from sqlalchemy.orm import Session, selectinload, joinedload
from sqlalchemy.sql.operators import from_

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


def select_translated_prompts_filenames_for_processed_dir_query(processed_dir_path):
    return (
        select(File.filename_without_extension)
        .join(TranslatedPrompt)
        .where(File.namespace_dir_path == processed_dir_path)
    )


def execute_select_all_in_session(query: Executable, session_maker: sessionmaker):
    with (session_maker() as session):
        return session.execute(query).all()


def execute_insert_in_session(query: Executable, session_maker: sessionmaker, connection: Connection):
    with session_maker() as session:
        session.execute(query)

        session.commit()
        connection.commit()


def select_translated_prompts_filenames_for_processed_dir(processed_dir_path, *, session_maker: sessionmaker):
    rows = execute_select_all_in_session(
        select_translated_prompts_filenames_for_processed_dir_query(processed_dir_path),
        session_maker
    )
    return [row[0] for row in rows]


def select_file_and_prompt_for_processed_dir_query(processed_dir_path):
    return (
        select(File, Prompt)
        .join_from(File, Prompt)
        .where(File.namespace_dir_path == processed_dir_path)
    )


def select_file_and_prompt_for_processed_dir(processed_dir_path, session_maker: sessionmaker):
    return execute_select_all_in_session(
        select_file_and_prompt_for_processed_dir_query(processed_dir_path),
        session_maker
    )


def delete_translated_prompts_for_processed_dir_related_files_query(processed_dir_path):
    return delete(TranslatedPrompt).where(TranslatedPrompt.file.has(namespace_dir_path=processed_dir_path))


def delete_translated_prompts_for_processed_dir_related_files(processed_dir_path, connection: Connection):
    return connection.execute(delete_translated_prompts_for_processed_dir_related_files_query(processed_dir_path))


def select_ocr_done_filenames_for_processed_dir_query(processed_dir_path):
    return (
        select(File.filename_without_extension)
        .join_from(File, Ocr)
        .where(File.namespace_dir_path == processed_dir_path)
    )


def select_ocr_done_filenames_for_processed_dir(processed_dir_path, session_maker: sessionmaker):
    rows = execute_select_all_in_session(
        select_ocr_done_filenames_for_processed_dir_query(processed_dir_path),
        session_maker
    )
    return [row[0] for row in rows]
