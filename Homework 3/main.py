import json
import logging
import db_controller as db
from flask import Flask, render_template, request, Response
from wtforms import Form, TextAreaField, TextField, validators, StringField, SubmitField
import cloud_functions as cloud
from OTTERCONFIG import project_id, s_acc
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = "1310a7d075f989192b9bb7c69ab6b043"


# noinspection PyDeprecation
'''class MainForm(Form):
    name = TextField('Name:', validators=[validators.DataRequired()])
    @app.route("/", methods=['GET', 'POST'])
    def mainPage():
        form = MainForm(request.form)
        name = ""
        print(form.errors)
        if request.method == 'POST':
            name = request.form['name']
        print(name)
        if form.validate():
            # Save the comment here.
            flash('Hello ' + name)
        else:
            flash('Error: All the form fields are required. ')
        return render_template('main.html', form=form)
    @app.errorhandler(500)
    def server_error(e):
        logging.exception('An error occurred during a request.')
        return """
        An internal error occurred: <pre>{}</pre>
        See logs for full stacktrace.
        """.format(e), 500
    @app.errorhandler(404)
    def server_error(e):
        logging.exception('Accessed resource that doesnt exist!')
        # TODO: 404 message maby ?
        # return """
        # SOME 404 message
        # """.format(e),
        return render_template("404.html")
'''

import uuid

def log_dict(log_name, log_data):
    from google.cloud import error_reporting
    client = error_reporting.Client.from_service_account_json(s_acc)
    try:
        from google.cloud import logging
        logging_client = logging.Client.from_service_account_json(s_acc)
        logger = logging_client.logger(log_name)
        logger.log_struct(log_data)
    except Exception:
        client.report_exception()


def log_string(log_name, log_data):
    from google.cloud import error_reporting
    client = error_reporting.Client.from_service_account_json(s_acc)
    try:
        from google.cloud import logging
        logging_client = logging.Client.from_service_account_json(s_acc)
        logger = logging_client.logger(log_name)
        logger.log_text(log_data)
    except Exception:
        client.report_exception()


def error_report(module):
    from google.cloud import error_reporting
    client = error_reporting.Client.from_service_account_json(s_acc)
    client.report("An error has occurred in " + module + ".")


def text_to_speech(text, target):
    from google.cloud import texttospeech
    client = texttospeech.TextToSpeechClient.from_service_account_json(s_acc)
    synthesis_input = texttospeech.types.cloud_tts_pb2.SynthesisInput(text=text)
    voice = texttospeech.types.cloud_tts_pb2.VoiceSelectionParams(
        language_code=target,
        ssml_gender=texttospeech.enums.SsmlVoiceGender.NEUTRAL)
    audio_config = texttospeech.types.cloud_tts_pb2.AudioConfig(
        audio_encoding=texttospeech.enums.AudioEncoding.MP3)
    response = client.synthesize_speech(synthesis_input, voice, audio_config)
    file_name = 'Audio/' + str(uuid.uuid4()) + ".mp3"
    with open(file_name, 'wb') as out:
        out.write(response.audio_content)
    log_string("text_to_speech_log", "Generated file " + file_name + " for the text \"" + text + "\".")
    return file_name


def translate_text(text: str = "", lang: str = "en-US", target: str = "ro"):
    from google.cloud import error_reporting
    error_client = error_reporting.Client.from_service_account_json(s_acc)
    try:
        from google.cloud import translate
        if text != "":
            # storage_client = storage.Client()
            client = translate.TranslationServiceClient.from_service_account_json(s_acc)
            parent = client.location_path(project_id, "global")
            response = client.translate_text(
                parent=parent,
                contents=[text],
                mime_type="text/plain",  # mime types: text/plain, text/html
                source_language_code=lang,
                target_language_code=target,
            )
            resp = []
            log_string("translation_log", "Translated text \"" + text + "\" from \"" + lang + "\" to \"" + target + "\".")
            for translation in response.translations:
                file_name = text_to_speech(translation.translated_text, target)
                resp.append({"translation": translation.translated_text, "file_name": file_name})
            return resp
    except Exception:
        error_client.report_exception()

# a = {"apples": 1, "oranges": 2}
# log_dict("homework-log", a)
# log_string("homework-log", "abcd")


# error_report("error_report")


# print(translate_text("Ana has apples", "ro-RO", "en-US"))





@app.before_first_request
def create_table_translations():
    db.create_table_translations()
    #tst = db.insert_translation("en", "ro", "hello", "salut")


@app.route("/", methods=["GET"])
def index():
    translations = db.get_all_translations()
    log_string("db_log", "GET All Translations")
    return render_template(
        "home.html", translations=translations
    )

@app.route("/home", methods=["GET"])
def home():
    translations = db.get_all_translations()
    log_string("db_log", "GET All Translations")
    return render_template(
        "home.html", translations=translations
    )

@app.route("/translations", methods=["GET"])
def translate():
    translations = db.get_all_translations()
    log_string("db_log", "GET All Translations")
    return render_template(
        "translations.html", translations=translations
    )

@app.route("/translations", methods=["POST"])
def translate_post():
    from google.cloud import error_reporting
    error_client = error_reporting.Client.from_service_account_json(s_acc)
    try:
        init_lang = request.form["initial_language"]
        target_lang = request.form["target_language"]
        text = request.form["initial_text"]
        translations = translate_text(text, init_lang, target_lang)
        db.insert_translation(init_lang,target_lang,text,translations[0]["translation"])
        log_dict("db_log", {"action": "DB POST Translation", "data": {
            "text": text,
            "language": init_lang,
            "translation": translations[0]["translation"],
            "target_language": target_lang
        }})
        return json.dumps(translations[0])
    except Exception:
        error_client.report_exception()

@app.route("/text-to-speech", methods=["GET"])
def text_to_speech():
    translations = db.get_all_translations()

    return render_template(
        "text_to_speech.html", translations=translations
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)



if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8080, debug=True)