# LAB: Shiny Application - ForHer

## App Structure

```
ForHer/
├── app.R                 # Main Shiny application
├── R/
│   ├── api_client.R      # MyHealthfinder API integration
│   └── ai_insights.R     # AI-powered reporting (OpenAI/Ollama)
├── docs/
│   ├── ABOUT.md
│   ├── LAB_your_good_api_query.md
│   ├── LAB_cursor_shiny_app.md
│   └── LAB_ai_reporter.md
├── install_packages.R    # Dependency installation
└── README.md
```

## Required Components (Assignment Checklist)

| Requirement        | Implementation                                      |
|--------------------|-----------------------------------------------------|
| API Integration    | MyHealthfinder API via `R/api_client.R`            |
| Key Statistics     | Value boxes: recommendations count, topics, categories |
| AI-Powered Insights| `R/ai_insights.R` – OpenAI or Ollama summaries      |
| Clean UI           | shinydashboard with purple theme                    |
| Reactive Text      | `reactive_summary` updates with user inputs         |
| Value Boxes        | 3 value boxes for key metrics                      |
| Visualizations     | Category bar chart, recommendations table, topics table |
| Deployment         | rsconnect for Posit Connect / Cloud                |

## Running Locally

```r
# 1. Install packages
source("install_packages.R")

# 2. Run app
shiny::runApp()
```

## Cursor Usage

- Use Cursor to edit `app.R`, `R/api_client.R`, and `R/ai_insights.R`
- Ask Cursor to add new visualizations or fix API parsing
- Use Cursor for deployment configuration (rsconnect)
