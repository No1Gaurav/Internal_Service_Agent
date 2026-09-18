class RequestClassifier:

    CATEGORIES = {
        "password": [
            "password",
            "forgot password",
            "reset password",
            "login"
        ],

        "access": [
            "access",
            "permission",
            "authorization",
            "account"
        ],

        "hardware": [
            "laptop",
            "computer",
            "keyboard",
            "mouse",
            "monitor",
            "printer"
        ],

        "software": [
            "software",
            "application",
            "install",
            "installation",
            "error"
        ],

        "network": [
            "wifi",
            "internet",
            "network",
            "vpn"
        ]
    }

    def classify(self, text: str) -> str:

        text = text.lower()

        for category, keywords in self.CATEGORIES.items():

            for keyword in keywords:

                if keyword in text:
                    return category

        return "general"