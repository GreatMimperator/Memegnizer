from ocr.meme_ocr_receiver import ocr_receive
from prompt_receive.media_prompt_receiver import prompts_receive
from source_process.media_mover_with_conversion import move_source_media_and_convert_if_needed
from translate.prompt_translator import prompts_translation_receive

if __name__ == '__main__':
    move_source_media_and_convert_if_needed()
    prompts_receive()
    prompts_translation_receive()
    ocr_receive()
