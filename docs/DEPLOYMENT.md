# Deployment Guide (Module 4)

## Option 1: Posit Cloud (Recommended for students)

1. Go to [posit.cloud](https://posit.cloud)
2. Create account / sign in
3. New Project → Shiny Application
4. Upload `app.R`, `R/` folder, and `install_packages.R`
5. In R console: `source("install_packages.R")`
6. Deploy via the Publish button

## Option 2: Posit Connect

```r
# Install rsconnect and configure
install.packages("rsconnect")
rsconnect::setAccountInfo(
  name = "your-account",
  token = "your-token",
  secret = "your-secret"
)
rsconnect::deployApp(appDir = ".", appName = "ForHer")
```

## Option 3: DigitalOcean App Platform

1. Create a new App from GitHub repo
2. Use Shiny/R runtime
3. Set build command: `R -e "source('install_packages.R')"`
4. Set run command: `R -e "shiny::runApp(host='0.0.0.0', port=8080)"`

## Environment Variables (for AI)

- `OPENAI_API_KEY` – Set in deployment platform for AI insights
- Without it, app works but shows "AI unavailable" message
