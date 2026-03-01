# Run this script to install required R packages for ForHer
# install.packages("renv")  # Optional: for reproducible environments

pkgs <- c(
  "shiny",
  "shinydashboard",
  "ggplot2",
  "dplyr",
  "jsonlite",
  "httr",
  "DT",         # For dataTableOutput
  "rsconnect"   # For deployment to Posit Connect / Cloud
)

for (pkg in pkgs) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    install.packages(pkg, repos = "https://cloud.r-project.org")
  }
}

message("Packages installed. Run: shiny::runApp()")
