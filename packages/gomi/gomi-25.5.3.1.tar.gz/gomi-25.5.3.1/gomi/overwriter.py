# Overwriter acts like Updater but allows mapping models with different names.
# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU GPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
import os

from .ankiconnect import request_model_names
from .common import find_referenced_media_files, select
from .consts import NOTE_TYPES_DIR
from .importer import read_model, save_files_to_anki_col
from .updater import send_note_type


def overwrite_note_type():
    anki_models = request_model_names()
    models_on_disk = {(model := read_model(dir_name)).name: model for dir_name in os.listdir(NOTE_TYPES_DIR)}
    model_name_on_disk = select(list(models_on_disk), "Take stored model: ")
    model_name_in_anki = select(anki_models, "Replace templates in model: ")

    print(f"Writing templates from {model_name_on_disk} onto {model_name_in_anki}...")

    model = models_on_disk[model_name_on_disk]
    save_files_to_anki_col(find_referenced_media_files(model))
    send_note_type(model.rename(model_name_in_anki))

    print("Done.")
