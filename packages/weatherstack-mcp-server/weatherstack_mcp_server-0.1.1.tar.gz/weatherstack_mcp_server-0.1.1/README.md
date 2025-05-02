# ⛅ Weatherstack MCP Server

This is an **MCP (Model Context Protocol) server** for integrating with the [Weatherstack API](https://weatherstack.com/), enabling AI agents to access real-time, historical, forecast, and marine weather data using natural language input.

The goal of this project is to expose Weatherstack's functionality through MCP-compatible tools that can be used seamlessly by large language models and agent frameworks.

---

## 🧠 What is MCP?

MCP (Model Context Protocol) is a lightweight protocol designed to let **AI agents interact with external tools and APIs** in a structured and modular way. Think of it like **USB for AI** — this server acts as a "driver" for the Weatherstack platform.

With this MCP server, AI models can:

- 🌤️ Get current weather conditions for any location  
- 🕰️ Access historical weather data by date and hour  
- 📅 Retrieve multi-day weather forecasts  
- 🌊 Get marine/sailing weather and tide information  

---

# 🚀 How to Run

To use this MCP server, you'll need:

## ✅ Prerequisites

- Python 3.11+  
- [`uv`](https://github.com/astral-sh/uv) – a modern Python package manager  
- A supported LLM (e.g., Claude)  
- A Weatherstack API key – get it at [weatherstack.com](https://weatherstack.com/)

## Add this to Claude Desktop config

```json
{
  "mcpServers": {
    "weatherstack-mcp": {
      "command": "uvx",
      "args": [
        "weatherstack-mcp-server",
        "--api-key",
        "YOUR WEATHERSTACK API KEY"
      ]
    }
  }
}
```

---

## 🤝 Contributions Welcome!

Whether you're passionate about weather tech, AI agent development, or robust API integrations — we’d love your help improving this project. You can contribute by:

- Adding support for additional Weatherstack endpoints  
- Improving the structure of tool responses  
- Writing better tests and usage examples  
- Sharing feedback or ideas via Issues or Discussions

Feel free to fork, explore, and open a PR. Let’s empower agents with better environmental awareness — one forecast at a time. 🌍🛰️

---

**MCP-FORGE** – Building tools for the future of intelligent automation.
