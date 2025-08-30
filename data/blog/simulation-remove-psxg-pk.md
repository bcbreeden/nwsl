---
title: Popping the Hood - Simplifying the Simulation Tool
excerpt: This update explores how the match simulator works and why some recent changes were made to improve it. The model uses real shot-level data, adjusts for opponent strength and home advantage, and runs thousands of simulations to generate win probabilities, scoreline distributions, and top scorers. Along the way, we revisit the difference between xG and PSxG, and explain why penalty kicks and PSxG have been removed from the tool. The goal is a cleaner, more accurate simulator that emphasizes repeatable patterns and sustainable performance.
tags: [Analysis, Data Modeling]
publish_date: 2025-08-30
draft: False
featured_image: img/blog/shot.png
---
<p class="text-small">Image Credit: Ira L. Black - Corbis/Getty Images</p>

### The Story So Far
The match simulator works by using real shot-level data from each team’s season and then adjusting it to reflect the upcoming matchup. First, it looks at how many shots a team typically takes, then modifies that number based on the defensive strength of the opponent — using both expected goals against (xGA) and shots allowed per game as benchmarks against league averages. On top of that, it applies a home/away advantage multiplier, giving the home team slightly more chances and the away team slightly fewer.

Once the expected shot volume is set, the simulator randomly samples from each team’s historical shots. Each sampled shot carries its own probability of becoming a goal, determined by xG or post-shot xG (PSxG). Goalkeeper performance is also factored in when using xG, so stronger or weaker keepers adjust the likelihood that any given attempt results in a goal.

By running this process thousands of times, the simulator produces a distribution of possible scorelines, win/draw/loss probabilities, average goals scored, and even top scorers. The result is a data-driven picture of how a match might play out, balancing the strengths and weaknesses of both teams with the inherent randomness of soccer.

### xG vs PSxG
When we talk about shot quality, we are really talking about two different metrics: xG and PSxG. Both are built from the same idea, estimating how likely a shot is to become a goal, but they measure it at different moments. xG looks at the chance before the shot is taken (location, angle, pressure, body part, etc.), while PSxG looks at the chance after the ball has been struck (placement, power, trajectory).

This distinction matters for modeling. xG is about repeatable chance creation, which makes it much more useful for predicting future performance. Teams and players who consistently generate high xG chances are likely to keep doing so. PSxG, on the other hand, is about one-time execution. It is excellent for describing how a specific shot was hit, whether it was top corner, right at the keeper, or something in between, but it does not generalize well for forecasting.

In short: xG is predictive, PSxG is descriptive. One helps us project what is likely to happen next, while the other helps us explain what just happened.

### Simulation Tool Changes
With these ideas in mind, I have made a few changes to the simulation tool.

1. #### Removal of the PSxG option
PSxG was not enabled by default, however I originally left it as an option during the configuration of a simulation run. To simplify the UI and make the tool more approachable, PSxG toggle has been removed.

2. #### Removal of Penalty Kicks
In the spirit of modeling sustainable performance, penalty kicks are not a good candidate. They are not repeatable and are often isolated incidents that occur sporadically, offering little indication of a team’s overall strength. The option to include penalty kicks has been removed from the configuration.

---

These changes are an effort to make the tool easier to use while also limiting the options to make the model more accurate in how it the simulations.

Until next time!
