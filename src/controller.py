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
    def get_authentication_challenge():
        """Gets a authentication challenge for a public key"""

        # NOTE: people can ask for challanges in behalf of someone else, revoking the previous one. is that an issue?
        # NOTE: the same challenge is used for login, registering and key storage. is that an issue?

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
            # TODO: unambigious error response?
            return "Public key is invalid or already registered. / Invalid association token", 400

    @app.route("/acc/register", methods=['POST'])
    def register():
        """Registers a account with a valid token and challenge response"""
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
        res = community.register(account)

        if res:
            return "Registration successful."
        else:
            # TODO: unambigious error response?
            return "Registration failed. Account data incorrect / invalid challenge reply", 400

        return str(account), 200

    @app.route("/acc/login", methods=['POST'])
    def login():
        """Verifies that your account is successfuly registered"""
        # get public key and challenge from headers
        public_key = request.headers.get("public_key", None)
        response = request.headers.get("response", None)

        # let them know if a header is missing
        v = []
        if not response:
            v.append("'response' header missing.")
        if not public_key:
            v.append("'public_key' header missing.")
        if v:
            return '\n'.join(v), 400

        # attemps login
        res = community.login(public_key, response)

        if res:
            return "Login successful."
        else:
            return "Login failed. Public key / challenge response is invalid", 400

    @app.route("/acc/store_key", methods=['POST'])
    def store_private_key():
        """Stores an (encrypted) version of an user's private key on their behalf"""

        # gets challange response, public and (encrypted) private from headers
        public_key = request.headers.get("public_key", None)
        private_key = request.headers.get("private_key", None)
        response = request.headers.get("response", None)

        # let them know if a header is missing
        v = []
        if not private_key:
            v.append("'private_key' header missing.")
        if not public_key:
            v.append("'public_key' header missing.")
        if not response:
            v.append("'response' header missing.")
        if v:
            return '\n'.join(v), 400

        # attempts to store key
        res = community.store_key(public_key, private_key, response)

        if res:
            return "Key stored successful."
        else:
            return "Key storage failed. Public key / challenge response is invalid", 400

    @app.route("/acc/remove_key", methods=['POST'])
    def delete_private_key():
        """Removes storaged key from the community db"""

        # gets challange response, public and (encrypted) private from headers
        public_key = request.headers.get("public_key", None)
        response = request.headers.get("response", None)

        # let them know if a header is missing
        v = []
        if not public_key:
            v.append("'public_key' header missing.")
        if not response:
            v.append("'response' header missing.")
        if v:
            return '\n'.join(v), 400

        # attempts to store key
        try:
            res = community.delete_key(public_key, private_key, response)
        # if there was no key stored...
        except ResourceWarning as e:
            return str(e), 205

        if res:
            return "Key stored successful."
        else:
            return "Key storage failed. Public key / challenge response is invalid", 400

    # TODO: Enable TLS for secure communication
    app.run()
