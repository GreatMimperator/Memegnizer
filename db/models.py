from sqlalchemy import create_engine, Column, Integer, Text, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


class File(Base):
    __tablename__ = 'file'

    id = Column(Integer, primary_key=True, autoincrement=True)
    namespace_dir_path = Column(Text)
    filename_without_extension = Column(Text)

    # Define relationships
    prompts = relationship('Prompt', back_populates='file', uselist=False)
    translated_prompts = relationship('TranslatedPrompt', back_populates='file', uselist=False)
    ocr = relationship('Ocr', back_populates='file', uselist=False)
    speech_recognition = relationship('SpeechRecognition', back_populates='file', uselist=False)


class Prompt(Base):
    __tablename__ = 'prompt'

    file_id = Column(Integer, ForeignKey('file.id'), primary_key=True)
    text = Column(Text)

    # Define relationship
    file = relationship('File', back_populates='prompts')


class TranslatedPrompt(Base):
    __tablename__ = 'translated_prompt'

    file_id = Column(Integer, ForeignKey('file.id'), primary_key=True)
    text = Column(Text)

    # Define relationship
    file = relationship('File', back_populates='translated_prompts')


class Ocr(Base):
    __tablename__ = 'ocr'

    file_id = Column(Integer, ForeignKey('file.id'), primary_key=True)
    ocr = Column(Text)

    # Define relationship
    file = relationship('File', back_populates='ocr')


class SpeechRecognition(Base):
    __tablename__ = 'speech_recognition'

    file_id = Column(Integer, ForeignKey('file.id'), primary_key=True)
    language_code = Column(Enum('en', 'es', 'fr', 'de', 'other', name='language_codes'))
    text = Column(Text)

    # Define relationship
    file = relationship('File', back_populates='speech_recognition')
