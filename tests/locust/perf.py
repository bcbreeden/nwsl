from locust import HttpUser, task, between
import json

# Load config for host and wait time
with open("config.json") as f:
    config = json.load(f)

class WebsiteUser(HttpUser):
    wait_time = between(config["min_wait"], config["max_wait"])
    host = config["host"]

    @task
    def visit_homepage(self):
        self.client.get("/")

    @task
    def visit_league(self):
        self.client.get("/league")

    @task
    def visit_players(self):
        self.client.get("/players")

    @task
    def visit_goalkeepers(self):
        self.client.get("/goalkeepers")

    @task
    def visit_teams(self):
        self.client.get("/teams")

    @task
    def visit_team_comparison(self):
        self.client.get("/team_comparison")

    @task
    def visit_games(self):
        self.client.get("/games")

    @task
    def visit_simulations(self):
        self.client.get("/simulations")

    @task
    def visit_blog(self):
        self.client.get("/blog")
