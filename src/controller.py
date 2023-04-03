from src.community import Community
from flask import Flask, jsonify, request
import json

def start_api():
    community = Community()
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

        # get a response from the challenge
        response = community.reply_challenge(challenge)
        
        # if the challenge is valid
        if response:
            return  response
        # invalid challenge
        else:
            return f"Challenge missing or of incorrect length. Should be {community.CHALLENGE_LENGTH} bytes long.", 400

    @app.route("/auth/associate", methods=['POST'])
    def associate():
        """Associates to the community as a member"""
        # get challenge from headers TODO: hardcoded direct approximation
        password = request.headers.get("password", None)

        # attempts to get association token
        token = community.issue_association_token(password)

        # if the association was successful...
        if token:
            return token
        else:
            return "Association failed.", 400

    @app.route("/auth/challenge", methods=['GET'])
    def get_register_challenge():
        """Gets a authentication challenge for a public key"""
        # get token and challenge from headers
        token = request.headers.get("token", None)
        public_key = request.headers.get("public_key", None)

        # let them know if a header is missing
        v = []
        if not token:
            v.append("'token' header missing.")
        if not public_key:
            v.append("'public_key' header missing.")
        if v:
            return '\n'.join(v), 400

        # gets a token and challenge
        challenge = community.issue_authentication_challenge(token, public_key)

        if challenge:
            return challenge, 201
        else:
            #TODO: unambigious error response?
            return "Public key is invalid or already registered. / Invalid association token", 400

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

        # registers account
        res = community.register_account(account)

        if res:
            return "Registration successful."
        else:
            # TODO: unambigious error response?
            return "Registration failed. Account data incorrect / invalid challenge reply", 400

        return str(account), 200

    # TODO: Enable TLS for secure communication
    app.run()
