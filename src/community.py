class Community:

    CHALLENGE_LENGTH = 16

    def association_response(self, challenge : str):
        # if the challenge if valid
        if challenge and len(bytes(challenge, 'utf-8')) == self.CHALLENGE_LENGTH:
            return "response"
        # challenge missing or invalid
        else:
            return "Challenge missing or incorrect length.", 400
