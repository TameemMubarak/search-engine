from urllib.robotparser import RobotFileParser
from urllib.parse import urljoin


class RobotsChecker:

    def __init__(self, base_url, user_agent):

        self.base_url = base_url
        self.user_agent = user_agent

        self.robots_url = urljoin(
            base_url,
            "/robots.txt"
        )

        self.parser = RobotFileParser()

        self.parser.set_url(
            self.robots_url
        )

        self.loaded = False

    def load(self):

        try:

            self.parser.read()

            self.loaded = True

            print(
                f"Loaded robots.txt: "
                f"{self.robots_url}"
            )

        except Exception as error:

            print(
                f"Could not load robots.txt: "
                f"{error}"
            )

    def allowed(self, url):

        if not self.loaded:
            return False

        return self.parser.can_fetch(
            self.user_agent,
            url
        )