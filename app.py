import psycopg2
import os
import base64
import requests
from psycopg2.errors import UniqueViolation
from typing import Dict, List, Any
from flask import Flask, jsonify, request
from werkzeug.utils import secure_filename
from src.utils.db import get_cursor, get_sensors_data
from src.utils.env import get_env_vars
from src.log.logger import logger
from src.twilio.sim_cmds import activate_watering
from src.trefle.trefle import get_plant_info
from pathlib import Path

app = Flask(__name__)
app.testing = True
app.config['UPLOAD_FOLDER'] = f"{os.path.dirname(os.path.realpath(__file__))}/tmp_img"
Path(app.config['UPLOAD_FOLDER']).mkdir(parents=True, exist_ok=True)
env_vars = get_env_vars()
db_creds = {k: v for k, v in env_vars.items() if not k.startswith("twilio")}
Response = Dict[str, Any]
ALLOWED_IMG_EXTENSIONS = ['png', 'jpg', 'jpeg']


def allowed_file(filename: str, extensions: List[str]):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in extensions


@app.route("/metrics", methods=["GET"])
def get_metrics() -> Response:

    """
    Endpoint returning updated sensors data

    curl http://localhost:5000/metrics
    """

    try:
        with get_cursor(db_creds, commit=False) as cur:
            data = get_sensors_data(cur)
        return jsonify(status_code=200, data=data)
    except psycopg2.Error as e:
        return jsonify(
            message=f"Psycopg2 driver error: {type(e)}",
            args=e.args,
            status_code=500,
            error_type="Internal Server Error",
        )
    except Exception as e:
        return jsonify(
            message=f"Internal Server Error: {type(e)}",
            args=e.args,
            status_code=500,
            error_type="Internal Server Error",
        )


@app.route("/healthcheck", methods=["GET"])
def get_healthcheck() -> Response:

    """
    Endpoint returning updated healthcheck data
    """

    try:
        with get_cursor(db_creds, commit=False) as cur:
            cur.execute("SELECT * FROM events.healthchecks")
            data = cur.fetchall()
        return jsonify(status_code=200, data=data)
    except psycopg2.Error as e:
        return jsonify(
            message=f"Psycopg2 driver error: {type(e)}",
            args=e.args,
            status_code=500,
            error_type="Internal Server Error",
        )
    except Exception as e:
        return jsonify(
            message=f"Internal Server Error: {type(e)}",
            args=e.args,
            status_code=500,
            error_type="Internal Server Error",
        )


@app.route("/pi/sensors", methods=["POST"])
def post_sensors_data() -> Response:

    """
    Endpoint receiving sensors data

    Db table:

    CREATE TABLE events.sensors (
        uuid UUID DEFAULT uuid_generate_v4 (),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        measure_type VARCHAR(32) NOT NULL,
        unit VARCHAR(32) NOT NULL,
        value NUMERIC NOT NULL
    );

    curl -X POST http://localhost:5000/pi/sensors -H "Content-Type: application/json" -d @tests/resources/post_pi_sensor.json
    """

    try:
        payload = request.get_json()
        with get_cursor(db_creds, commit=True) as cur:
            logger.info(request.data)
            q = (
                f"INSERT INTO events.sensors (measure_type, unit, value) VALUES ('{payload['measure_type']}', "
                f"'{payload['unit']}', '{payload['value']}')"
            )
            cur.execute(q)
        return jsonify(status_code=200,)
    except KeyError as e:
        return jsonify(
            message=f"Missing key in payload: {type(e)}",
            args=e.args,
            status_code=400,
            error_type="Bad Request",
        )
    except UniqueViolation as e:
        return jsonify(
            message=f"Entity already exists: {type(e)}",
            args=e.args,
            status_code=409,
            error_type="Conflict",
        )
    except psycopg2.Error as e:
        return jsonify(
            message=f"Psycopg2 driver error: {type(e)}",
            args=e.args,
            status_code=500,
            error_type="Internal Server Error",
        )
    except Exception as e:
        return jsonify(
            message=f"Internal Server Error: {type(e)}",
            args=e.args,
            status_code=500,
            error_type="Internal Server Error",
        )


@app.route("/pi/healthcheck", methods=["POST"])
def post_healthcheck() -> Response:

    """
    Endpoint receiving Rapsberry healthcheck data

    Db table:

    CREATE TABLE events.healthchecks (
        uuid UUID DEFAULT uuid_generate_v4 (),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        healthcheck_type VARCHAR(32) NOT NULL,
        unit VARCHAR(32) NOT NULL,
        value NUMERIC NOT NULL
    );


   curl -X POST http://localhost:5000/pi/sensors
   -H "Content-Type: application/json" -d @tests/resources/post_pi_healthcheck.json
    """
    try:
        payload = request.get_json()
        with get_cursor(db_creds, commit=True) as cur:
            q = (
                f"INSERT INTO events.healthchecks (healtcheck_type, unit, value) VALUES ('{payload['healthcheck_type']}', "
                f"'{payload['unit']}', '{payload['value']}')"
            )
            cur.execute(q)
        return jsonify(status_code=200,)
    except KeyError as e:
        return jsonify(
            message=f"Missing key in payload: {type(e)}",
            args=e.args,
            status_code=400,
            error_type="Bad Request",
        )
    except UniqueViolation as e:
        return jsonify(
            message=f"Entity already exists: {type(e)}",
            args=e.args,
            status_code=409,
            error_type="Conflict",
        )
    except psycopg2.Error as e:
        return jsonify(
            message=f"Psycopg2 driver error: {type(e)}",
            args=e.args,
            status_code=500,
            error_type="Internal Server Error",
        )
    except Exception as e:
        return jsonify(
            message=f"Internal Server Error: {type(e)}",
            args=e.args,
            status_code=500,
            error_type="Internal Server Error",
        )


@app.route("/watering", methods=["POST"])
def post_watering() -> Response:

    """
    Endpoint triggering plant watering on user request

    Db table:

    CREATE TABLE events.watering (
        uuid UUID DEFAULT uuid_generate_v4 (),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        quantity_ml DECIMAL NOT NULL
    );

    curl -X POST http://localhost:5000/watering -H "Content-Type: application/json" -d @tests/resources/post_watering.json
    :return:
    """

    try:
        payload = request.get_json()
        response = activate_watering(
            env_vars["twilio_account_sid"],
            env_vars["twilio_auth_token"],
            env_vars["twilio_supersim_sid"],
            payload["quantity_ml"],
        )
        with get_cursor(db_creds, commit=True) as cur:
            q = f"INSERT INTO events.watering (quantity_ml) VALUES ('{payload['quantity_ml']}')"
            cur.execute(q)
        return jsonify(status_code=200, response=response)
    except KeyError as e:
        return jsonify(
            message=f"Missing key in payload: {type(e)}",
            args=e.args,
            status_code=400,
            error_type="Bad Request",
        )
    except psycopg2.Error as e:
        return jsonify(
            message=f"Psycopg2 driver error: {type(e)}",
            args=e.args,
            status_code=500,
            error_type="Internal Server Error",
        )
    except Exception as e:
        return jsonify(
            message=f"Internal Server Error: {type(e)}",
            args=e.args,
            status_code=500,
            error_type="Internal Server Error",
        )


@app.route("/search_plant_info/<name>", methods=["GET"])
def search_plant_info(name: str) -> Response:

    """
    Endpoint fetching plant data from cache or from Trefle API

    curl http://localhost:5000/search_plant_info/tapertip%20onion
    """

    try:
        data = get_plant_info(name, 100)
        return jsonify(status_code=200, data=data)
    except Exception as e:
        return jsonify(
            message=f"Internal Server Error: {type(e)}",
            args=e.args,
            status_code=500,
            error_type="Internal Server Error",
        )


@app.route("/identify_plant", methods=["POST"])
def identify_plant():
    """
    Endpoint receiving an image and querying Plant.id to identify the plant species

    curl -X POST http://localhost:5000/identify_plant -F "file=@./tests/resources/test_flower_img.jpeg" -H "Content-Type: multipart/form-data"
    """

    if "file" not in request.files:
        return jsonify(
            message=f"Bad Request: file missing",
            status_code=400,
            error_type="Bad Request",
        )
    file = request.files["file"]
    # if user does not select file, browser also
    # submit a empty part without filename
    if file.filename == "" or not file \
            or not allowed_file(file.filename, ALLOWED_IMG_EXTENSIONS):
        return jsonify(
            message=f"Bad Request: file missing",
            status_code=400,
            error_type="Bad Request",
        )

    filename = secure_filename(file.filename)
    tmp_filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    try:
        logger.info(f"Saving tmp image file at {tmp_filename}")
        # Save temp file, clean afterwards
        file.save(tmp_filename)

        # Build plant.id request
        with open(tmp_filename, "rb") as f:
            images = [base64.b64encode(f.read()).decode("ascii")]
        plant_id_payload = {
            "images": images,
            "modifiers": ["similar_images"],
            "plant_details": ["name_authority", "common_names", "url", "wiki_description", "taxonomy"],
        }

        # Return plant.id response
        response = requests.post(
            "https://api.plant.id/v2/identify",
            json=plant_id_payload,
            headers={
                "Content-Type": "application/json",
                "Api-Key": os.environ["PLANT_ID_API_ACCESS_TOKEN"]
            }).json()
        return response
    except Exception as e:
        return jsonify(
            message=f"Internal Server Error: {type(e)}",
            args=e.args,
            status_code=500,
            error_type="Internal Server Error",
        )
    finally:
        if os.path.exists(tmp_filename):
            logger.info(f"Removing tmp image file at {tmp_filename}")
            os.remove(tmp_filename)
