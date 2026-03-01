# ForHer

**Healthcare in the U.S. explained without the confusion.**

An AI-powered Shiny app for first-generation and international female students to understand preventive healthcare in the United States.

## Project Overview

| | |
|---|---|
| **Topic** | Women's Health for First-Gen / International Students |
| **API** | [MyHealthfinder API](https://odphp.health.gov/our-work/national-health-initiatives/health-literacy/consumer-health-content/free-web-content/apis-developers/api-content) (U.S. HHS) |
| **Stack** | R, Shiny, shinydashboard |

## Quick Start

```r
# 1. Install dependencies
source("install_packages.R")

# 2. Run app locally
shiny::runApp()
```

## Assignment Components

- **API Integration**: MyHealthfinder – personalized preventive care recommendations
- **Key Statistics**: Value boxes (recommendations, topics, categories)
- **AI Insights**: OpenAI or Ollama for plain-language summaries
- **UI**: shinydashboard, reactive text, value boxes
- **Visualizations**: Category bar chart, type pie chart, recommendations table
- **Deployment**: See `docs/DEPLOYMENT.md`

## Lab Documentation

- `docs/LAB_your_good_api_query.md` – API queries
- `docs/LAB_cursor_shiny_app.md` – Shiny app structure
- `docs/LAB_ai_reporter.md` – AI integration
