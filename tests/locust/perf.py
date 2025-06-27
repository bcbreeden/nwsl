from locust import HttpUser, task, between
import json
import random

TEAM_IDS = ["4JMAk47qKg", "315VnJ759x", "aDQ0lzvQEv"]
GAME_IDS = ["2lqRpdR0Mr", "7VqGbYm65v", "Vj58bpE4Q8"]

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
        self.client.get("/")
        self.client.get("/league")

    @task
    def visit_players(self):
        self.client.get("/")
        self.client.get("/players")

    @task
    def visit_goalkeepers(self):
        self.client.get("/")
        self.client.get("/goalkeepers")

    @task
    def visit_teams(self):
        self.client.get("/")
        self.client.get("/teams")
        chosen_team = random.choice(TEAM_IDS)
        self.client.post("/team", data={"team_id": chosen_team})

    @task
    def visit_team_comparison(self):
        self.client.get("/")
        self.client.get("/team_comparison")

    @task
    def visit_games(self):
        self.client.get("/")
        self.client.get("/games")
        chosen_team = random.choice(GAME_IDS)
        self.client.post("/game", data={"game_id": chosen_team})

    @task
    def visit_simulations(self):
        self.client.get("/")
        self.client.get("/simulations")

    @task
    def visit_blog(self):
        self.client.get("/")
        self.client.get("/blog")

