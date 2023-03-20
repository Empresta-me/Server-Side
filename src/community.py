class Community:

    CHALLENGE_LENGTH = 16

    def __init__():
        pass

    def reply_association(self, challenge : str):
        """Replies to association request with the response for the challenge issued"""
        # if the challenge if valid
        if challenge and len(bytes(challenge, 'utf-8')) == self.CHALLENGE_LENGTH:
            return "response"
        # challenge missing or invalid
        else:
            return "Challenge missing or incorrect length.", 400
