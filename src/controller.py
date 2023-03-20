from src.community import Community
from flask import Flask, jsonify, request

def start_api():
    community = Community()
    app = Flask(__name__)

    @app.route("/association", methods=['POST'])
    def associate():
        # get challenge from headers
        challenge = request.headers.get("challenge", None)

        return community.reply_association(challenge)

    app.run()
