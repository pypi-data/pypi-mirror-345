# Updater updates previously imported note types.
# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU GPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
import os
from typing import Any

from .ankiconnect import invoke, request_model_names
from .common import NoteType, find_referenced_media_files, select
from .consts import NOTE_TYPES_DIR
from .importer import read_model, save_files_to_anki_col


def format_templates(model: NoteType) -> dict[str, Any]:
    return {
        "model": {
            "name": model.name,
            "templates": {
                template.name: {"Front": template.front, "Back": template.back} for template in model.templates
            },
        }
    }


def format_styling(model: NoteType) -> dict[str, Any]:
    return {"model": {"name": model.name, "css": model.css}}


def send_note_type(model: NoteType):
    invoke("updateModelTemplates", **format_templates(model))
    invoke("updateModelStyling", **format_styling(model))


def update_note_type():
    anki_models = request_model_names()
    models_on_disk = {(model := read_model(dir_name)).name: model for dir_name in os.listdir(NOTE_TYPES_DIR)}
    updatable_models = [model_name for model_name in models_on_disk if model_name in anki_models]
    if not updatable_models:
        print("No note types can be updated.")
        return
    if model_name := select(updatable_models):
        print(f"Selected note type: {model_name}")
        model = models_on_disk[model_name]
        save_files_to_anki_col(find_referenced_media_files(model))
        send_note_type(model)
        print("Done.")
