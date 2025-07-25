TEAM_STYLE_MAP = {
    "315VnJ759x": {
        "abbreviation": "BAY",
        "dot_color": "#0a1f38",
        "stroke_color": "#dce1e7"
    },
    "4wM4Ezg5jB": {
        "abbreviation": "BOS",
        "dot_color": "#9ec1f7",
        "stroke_color": "#0033a0"
    },
    "KPqjw8PQ6v": {
        "abbreviation": "CHI",
        "dot_color": "#c8102e",
        "stroke_color": "#092944"
    },
    "4JMAk47qKg": {
        "abbreviation": "HOU",
        "dot_color": "#ff6a13",
        "stroke_color": "#0d1b2a"
    },
    "4wM4rZdqjB": {
        "abbreviation": "KC",
        "dot_color": "#51c5c0",
        "stroke_color": "#ffffff"
    },
    "kRQa8JOqKZ": {
        "abbreviation": "LA",
        "dot_color": "#111111",
        "stroke_color": "#f5b3a7"
    },
    "eV5DR6YQKn": {
        "abbreviation": "LOU",
        "dot_color": "#cba3dd",
        "stroke_color": "#57278f"
    },
    "zeQZeazqKw": {
        "abbreviation": "NC",
        "dot_color": "#003049",
        "stroke_color": "#bfa46f"
    },
    "raMyrr25d2": {
        "abbreviation": "NJY",
        "dot_color": "#000000",
        "stroke_color": "#b9e9f6"
    },
    "XVqKeVKM01": {
        "abbreviation": "ORL",
        "dot_color": "#612885",
        "stroke_color": "#00b6e4"
    },
    "Pk5LeeNqOW": {
        "abbreviation": "POR",
        "dot_color": "#7a0019",
        "stroke_color": "#d9b38c"
    },
    "7VqG1lYMvW": {
        "abbreviation": "SD",
        "dot_color": "#ffffff",
        "stroke_color": "#e51884"
    },
    "7vQ7BBzqD1": {
        "abbreviation": "SEA",
        "dot_color": "#1e1d26",
        "stroke_color": "#bda873"
    },
    "eV5D2w9QKn": {
        "abbreviation": "UTA",
        "dot_color": "#f4b92a",
        "stroke_color": "#0b0d3b"
    },
    "aDQ0lzvQEv": {
        "abbreviation": "WAS",
        "dot_color": "#1a1a1a",
        "stroke_color": "#fff700"
    },
    "xW5pwDBMg1": {
        "abbreviation": "WNY",
        "dot_color": "#1a1a1a",
        "stroke_color": "#c8102e"
    }
}

def _make_logo_image(path, x, y, xanchor="center", yanchor="middle"):
    return dict(
        source=path,
        xref="paper",         # Use paper coordinates to position independently of axis ranges
        yref="paper",
        x=x,
        y=y,
        sizex=0.4,
        sizey=0.4,
        xanchor=xanchor,
        yanchor=yanchor,
        opacity=0.15,
        layer="below"
    )