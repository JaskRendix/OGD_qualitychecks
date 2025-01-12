import json
import time

import pandas as pd
import requests
import streamlit as st
from frictionless import Schema, validate

from mapping import ogdNbr_mapping

# translation dictionaries
translations = {
    "Deutsch": {
        "title": "CSV-Qualitätsprüfung mit Frictionless",
        "upload": "Laden Sie eine CSV-Datei hoch",
        "uploaded_success": "Datei erfolgreich hochgeladen!",
        "check_button": "Überprüfen",
        "error": "Fehler während der Validierung:",
        "validation_complete": "Validierung abgeschlossen!",
        "valid": "Das Dokument ist gültig.",
    },
    "Français": {
        "title": "Contrôle de qualité CSV avec Frictionless",
        "upload": "Télécharger un fichier CSV",
        "uploaded_success": "Fichier téléchargé avec succès !",
        "check_button": "Vérifier",
        "error": "Erreur de validation:",
        "validation_complete": "Validation terminée !",
        "valid": "Le document est valide.",
    },
    "Italiano": {
        "title": "Controllo qualità CSV con Frictionless",
        "upload": "Caricare un file CSV",
        "uploaded_success": "File caricato con successo!",
        "check_button": "Controllo",
        "error": "Errore durante la validazione:",
        "validation_complete": "Validazione completata!",
        "valid": "Il documento è valido.",
    },
    "English": {
        "title": "CSV Quality Check with Frictionless",
        "upload": "Upload a CSV file",
        "uploaded_success": "File uploaded successfully!",
        "check_button": "Check",
        "error": "Error during validation:",
        "validation_complete": "Validation complete!",
        "valid": "The document is valid.",
    },
}

MAX_ATTEMPTS = 2
INITIAL_DELAY = 1


def fetch_datapackage(datapackage_url: str) -> str:
    """Fetches the datapackage from the provided URL."""
    attempts = 0
    while attempts < MAX_ATTEMPTS:
        try:
            response = requests.get(datapackage_url)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching datapackage: {e}")
        attempts += 1
        time.sleep(INITIAL_DELAY * attempts)
    return None


def get_schema(datapackage: str, file_name: str) -> dict:
    """Extracts the schema from the datapackage."""
    datapackage_json = json.loads(datapackage)
    for resource in datapackage_json.get("resources", []):
        if "path" in list(resource.keys()) and file_name in resource["path"]:
            return resource["schema"]
    return None


def perform_quality_check(frame: pd.DataFrame, file_name: str) -> str:
    """Performs the quality check on the provided frame and file name."""
    try:
        if file_name in ogdNbr_mapping:
            ID = ogdNbr_mapping[file_name]
            datapackage_url = (
                f"https://www.uvek-gis.admin.ch/BFE/ogd/{ID}/datapackage.json"
            )
            datapackage = fetch_datapackage(datapackage_url)
            if datapackage:
                schema = get_schema(datapackage, file_name)
                if schema:
                    for field in schema["fields"]:
                        if field["type"] == "year":
                            field["type"] = "integer"
                    schema = Schema(schema)
                    if all(frame.dtypes == "int64"):
                        frame.iloc[:, 0] = frame.iloc[:, 0].astype(float)
                    report = validate(frame, schema=schema)
                    if report.valid:
                        return "The document is valid."
                    else:
                        error_messages = ""
                        for err in report.tasks[0].errors:
                            error_messages += err.title + ":\n" + err.message + "\n\n"
                        return error_messages
                else:
                    return f"No schema found for the uploaded file '{file_name}' in the datapackage."
            else:
                return f"Failed to fetch datapackage after multiple attempts."
        else:
            return f"There is no datapackage for the file '{file_name}' "
    except Exception as e:
        return f"An error occurred: {str(e)}"


def main():
    # default language German
    if "language" not in st.session_state:
        st.session_state.language = "Deutsch"

    # language selection dropdown
    selected_language = st.sidebar.selectbox(
        "Select Language",
        list(translations.keys()),
        index=list(translations.keys()).index(st.session_state.language),
    )
    st.session_state.language = selected_language

    # display content based on selected language
    translation = translations[st.session_state.language]

    # set title
    st.title(translation["title"])

    # create upload element
    uploaded_file = st.file_uploader(translation["upload"], type=["csv"])

    if uploaded_file is not None:
        st.write(translation["uploaded_success"])

        dataframe = pd.read_csv(
            uploaded_file, sep="[;,]", engine="python", skip_blank_lines=False
        )
        st.write(dataframe)
        if st.button(translation["check_button"]):
            progress_bar = st.progress(0)
            report = perform_quality_check(dataframe, uploaded_file.name)

            if report.startswith("The document is valid."):
                st.success(translation["validation_complete"])
                st.success(report)
            else:
                st.error(translation["validation_complete"])
                st.error(report)

            progress_bar.progress(100)


if __name__ == "__main__":
    main()
