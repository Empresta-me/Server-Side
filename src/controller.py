from community import Community

from flask import Flask, jsonify, request

app = Flask(__name__)

community = Community()

@app.route("/association", methods=['POST'])
def associate():
    # get challenge from headers
    challenge = request.headers.get("challenge", None)

    return community.association_response(challenge)
