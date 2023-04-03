from src.community import Community
from flask import Flask, jsonify, request
import json

def start_api():
    community = Community(b'testpassword')
    app = Flask("Community API")

    @app.route("/meta/info", methods=['GET'])
    def get_info():
        """Gets the community's public information"""
        return community.get_info()

    @app.route("/meta/verify_key", methods=['POST'])
    def verify_key():
        """Verifies ownership of public key through challenge response authentication"""
        # get challenge from headers
        challenge = request.headers.get("challenge", None)
        
        # if the challenge is valid
        if challenge and len(bytes(challenge, 'utf-8')) == community.CHALLENGE_LENGTH:
            return community.reply_challenge(challenge)
        else:
            return f"Challenge missing or of incorrect length. Should be {community.CHALLENGE_LENGTH} bytes long.", 400

    @app.route("/auth/associate", methods=['POST'])
    def associate():
        """Associates to the community as a member"""
        # get challenge from headers TODO: hardcoded direct approximation
        password = request.headers.get("password", None)

        # attempts to get association token
        token = community.get_association_token(password)

        # if the association was successful...
        if token:
            return token
        else:
            return "Association failed.", 400

    @app.route("/acc/register", methods=['GET'])
    def get_register_challenge():
        """Gets a register token associated with the public key"""
        # get challenge from headers TODO: hardcoded direct approximation
        public_key = request.headers.get("public_key", None)

        # if public key is missing, let em know
        if not public_key:
            return "public_key header missing.", 400

        # gets a token and challenge
        challenge = community.get_register_challenge(public_key)

        if challenge:
            return challenge, 201
        else:
            return "Public key is invalid or already registered.", 400

    @app.route("/acc/register", methods=['POST'])
    def reply_register_challenge():
        # get json from body
        account_json = request.data

        # converts json to dict
        # TODO: maybe we should check the schema
        try:
            account = json.loads(account_json)
        except:
            # TODO: write this better
            return "Failed to parse body as accoun JSON.", 400

        # TODO: actual registration
        return str(account), 200

    # TODO: Enable TLS for secure communication
    app.run()
