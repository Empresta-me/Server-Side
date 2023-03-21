from src.community import Community
from flask import Flask, jsonify, request

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
        
        # if the challenge is valid
        if challenge and len(bytes(challenge, 'utf-8')) == community.CHALLENGE_LENGTH:
            return community.verify_key(challenge)
        else:
            return f"Challenge missing or of incorrect length. Should be {community.CHALLENGE_LENGTH} bytes long.", 400

    @app.route("/auth/associate", methods=['POST'])
    def associate():
        # get challenge from headers TODO: hardcoded direct approximation
        password = request.headers.get("password", None)

        # attempts to get association token
        token = community.get_association_token(password)

        # if the association was successful...
        if token:
            return token
        else:
            return "Association failed.", 400

    # TODO: Enable TLS for secure communication
    app.run()
