<p align="center">
  <a href="" rel="noopener">
    <img width=200px height=200px src="https://i.imgur.com/J2NT0Vd.png" alt="Project logo">
  </a>
</p>

<h3 align="center">Botato</h3>

<div align="center">

[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![GitHub Issues](https://img.shields.io/github/issues/shivkun/botato.svg)](https://github.com/shivkun/botato/issues)
[![GitHub Pull Requests](https://img.shields.io/github/issues-pr/shivkun/botato.svg)](https://github.com/shivkun/botato/pulls)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](/LICENSE)

</div>

---

<p align="center"> A modern, minimal, and well-documented Discord bot framework for Python. Built to fix everything the others got wrong.
  <br>
</p>

## 📝 Table of Contents

* [About](#about)
* [Getting Started](#getting_started)
* [Deployment](#deployment)
* [Usage](#usage)
* [Built Using](#built_using)
* [TODO](../TODO.md)
* [Contributing](../CONTRIBUTING.md)
* [Authors](#authors)
* [Acknowledgments](#acknowledgement)

## 😮 About <a name = "about"></a>

**Botato** is a Discord bot framework designed for developers who want clarity, simplicity, and reliability.
Where other frameworks suffer from outdated docs, bloated abstractions, and lack of transparency, Botato provides a modern, well-typed, extensible alternative.

It includes a dynamic Gateway client, a fast REST API wrapper, JSON-driven intent management, and typed data models powered by Pydantic.

## 🏁 Getting Started <a name = "getting_started"></a>

These instructions will get you a copy of the project up and running locally for development and testing.

### Prerequisites

* Python 3.10+
* Poetry ([https://python-poetry.org/docs/](https://python-poetry.org/docs/))
* A Discord bot token

### Installing

Clone the repo and install dependencies:

```bash
poetry install
```

Activate the environment:

```bash
poetry env activate
```

Run the example bot:

```bash
DISCORD_TOKEN=your-token-here poetry run python examples/basic_bot.py
```

## 🔧 Running the tests <a name = "tests"></a>

To run the test suite:

```bash
poetry run pytest
```

## 🎈 Usage <a name="usage"></a>

Register events with decorators:

```python
@bot.event
async def on_message_create(data):
    print(data["content"])
```

## 🚀 Deployment <a name = "deployment"></a>

For production usage, you can use a process manager like `systemd`, `supervisord`, or `pm2` (for cross-platform Python apps).

Make sure to secure your token using environment variables or secret managers.

## ⛏️ Built Using <a name = "built_using"></a>

* [Python](https://python.org/) - Language
* [aiohttp](https://docs.aiohttp.org/) - Async HTTP client
* [websockets](https://websockets.readthedocs.io/) - Gateway support
* [pydantic](https://docs.pydantic.dev/) - Data validation
* [loguru](https://github.com/Delgan/loguru) - Logging

## ✍️ Authors <a name = "authors"></a>

* [@shivkun](https://github.com/shivkun) - Project lead and developer

## 🎉 Acknowledgements <a name = "acknowledgement"></a>

* Discord API team & community docs
* [discord.py](https://github.com/Rapptz/discord.py) for inspiration (and showing us what not to do)
* Contributors and early testers
