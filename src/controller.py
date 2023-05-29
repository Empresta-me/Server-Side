from src.community import Community
from src.protocol import Proto
from flask import Flask, jsonify, request, render_template
import json
import os

def start_api(pem : str):
    community = Community(pem)
    template_dir = os.path.abspath('src/template')
    static_dir = os.path.abspath('src/static')
    app = Flask("Community API", template_folder=template_dir, static_folder=static_dir)

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
        public_key = request.headers.get("public-key", None)

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
        public_key = request.headers.get("public-key", None)
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
        public_key = request.headers.get("public-key", None)
        private_key = request.headers.get("private-key", None)
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
        public_key = request.headers.get("public-key", None)
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

    @app.route("/acc/request-info", methods=['GET'])
    def request_info():
        host_key = request.headers.get("host-key", None)
        guest_key = request.headers.get("guest-key", None)
        response = request.headers.get("response", None)

        # let them know if a header is missing
        v = []
        if not host_key:
            v.append("'host-key' header missing.")
        if not guest_key:
            v.append("'guest-key' header missing.")
        if not response:
            v.append("'response' header missing.")
        if v:
            return '\n'.join(v), 400

        res = community.request_info(host_key, guest_key, response)

        if res:
            return res
        else:
            return "Incorrect signature / not permitted to access info", 400


    @app.route("/acc/permit-info", methods=['POST'])
    def permit_info():
        host_key = request.headers.get("host-key", None)
        guest_key = request.headers.get("guest-key", None)
        response = request.headers.get("response", None)

        # let them know if a header is missing
        v = []
        if not host_key:
            v.append("'host-key' header missing.")
        if not guest_key:
            v.append("'guest-key' header missing.")
        if not response:
            v.append("'response' header missing.")
        if v:
            return '\n'.join(v), 400

        res = community.permit_info(host_key, guest_key)

        print('res ' + str(res))

        if res:
            return "Info sharing confirmed"
        else:
            return "Incorrect signature", 400

    @app.route("/network/diagram", methods=['GET'])
    def serve_diagram():
        """Gets the community's public information"""
        observer = request.args.get("observer", None)
        #topology = community.get_topology(observer)

        topology = '''{"nodes":[{"name":"Alice","id":1,"reputation":90,"logo":"logos/1.png"},{"name":"Bob","id":2,"reputation":82,"logo":"logos/2.png","is_observer":true},{"name":"Chen","id":3,"reputation":94,"logo":"logos/3.png"},{"name":"Dawg","id":4,"reputation":91,"logo":"logos/4.png"},{"name":"Ethan","id":5,"reputation":87,"logo":"logos/5.png"},{"name":"Frank","id":6,"reputation":93,"logo":"logos/6.png"},{"name":"George","id":7,"reputation":85,"logo":"logos/7.png"},{"name":"Hanes","id":8,"reputation":75,"logo":"logos/8.png"},{"name":"Ivan","id":9,"reputation":99,"logo":"logos/9.png"},{"name":"Juan","id":10,"reputation":96,"logo":"logos/10.png"}],"links":[{"source":"Alice","target":"Bob","value":1,"message":"He is like a brother to me:)"},{"source":"Bob","target":"Alice","value":1,"message":"dont't really trust her but she's hot"},{"source":"Chen","target":"Bob","value":1,"message":"cool guy"},{"source":"Bob","target":"Chen","value":0,"message":"asshole"},{"source":"Chen","target":"Dawg","value":1,"message":"my dawg"},{"source":"Dawg","target":"Chen","value":1,"message":"bees"},{"source":"Hanes","target":"Frank","value":1,"message":"Gave my toaster back in good conditions. 10/10 would lend again 👍"},{"source":"Frank","target":"Hanes","value":1,"message":"Has a nice toaster!"},{"source":"George","target":"Hanes","value":0,"message":"Can't believe he folded the corner of my book 😡😡"},{"source":"Hanes","target":"George","value":1,"message":"Boring book honestly"},{"source":"Dawg","target":"Ethan","value":0},{"source":"Ethan","target":"Dawg","value":0},{"source":"Ivan","target":"Chen","value":1},{"source":"Chen","target":"Ivan","value":0},{"source":"Juan","target":"Alice","value":1},{"source":"Alice","target":"Juan","value":0,"message":"he returned my book all dirty >:("},{"source":"Juan","target":"Bob","value":1},{"source":"Bob","target":"Juan","value":1}]}'''

        if not topology:
            return render_template('visualizer.html')
            #return "Observer does not exist", 400
        else:
            return render_template('visualizer.html', topology=topology)

    @app.route("/network/topology", methods=['GET'])
    def serve_topology():
        """Gets the community's public information"""
        observer = request.headers.get("observer", None)

        topology = community.get_topology(observer)

        if not topology:
            return "Observer does not exist", 400

        return topology
    
    @app.route("/vouch", methods=['POST'])
    def vouch():
        """Gets the community's public information"""
        vouch_json = request.data
        print(type(vouch_json))
        msg = Proto.parse(vouch_json)
        community.handle_vouch(msg)

        return "Vouch Sent!"

    # TODO: Enable TLS for secure communication
    app.run(host='0.0.0.0')
