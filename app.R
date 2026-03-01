# ForHer - Women's Health for First-Gen / International Students
# Healthcare in the U.S. explained without the confusion.
# Shiny App: API + AI Insights + Visualizations

library(shiny)
library(shinydashboard)
library(ggplot2)
library(dplyr)
library(DT)
library(jsonlite)
library(httr)

# Source modules
source("R/api_client.R")
source("R/ai_insights.R")

# UI ----
ui <- dashboardPage(
  skin = "purple",
  dashboardHeader(title = "ForHer", titleWidth = 280),
  dashboardSidebar(
    width = 280,
    sidebarMenu(
      menuItem("Dashboard", tabName = "dashboard", icon = icon("heart")),
      menuItem("Health Topics", tabName = "topics", icon = icon("list")),
      menuItem("About", tabName = "about", icon = icon("info-circle"))
    ),
    hr(),
    h4("Your Profile", style = "padding: 10px 15px;"),
    numericInput("age", "Age", value = 25, min = 18, max = 100),
    selectInput("sex", "Sex", choices = c("female" = "female", "male" = "male")),
    selectInput("pregnant", "Pregnant?", choices = c("No" = "no", "Yes" = "yes")),
    selectInput("sexually_active", "Sexually Active?", choices = c("Yes" = "yes", "No" = "no")),
    selectInput("tobacco_use", "Tobacco Use?", choices = c("No" = "no", "Yes" = "yes")),
    selectInput("country_bg", "Country Background", 
                choices = c("International", "U.S. First-Gen", "Other")),
    actionButton("fetch_btn", "Get Recommendations", icon = icon("refresh"), 
                 class = "btn-primary", style = "margin: 10px;")
  ),
  dashboardBody(
    tabItems(
      tabItem("dashboard",
        fluidRow(
          valueBoxOutput("vb_recommendations", width = 4),
          valueBoxOutput("vb_topics", width = 4),
          valueBoxOutput("vb_categories", width = 4)
        ),
        fluidRow(
          box(
            title = "AI-Powered Summary", status = "primary", solidHeader = TRUE,
            width = 12,
            uiOutput("ai_insight_text")
          )
        ),
        fluidRow(
          box(
            title = "Recommendations by Category", status = "info",
            width = 6,
            plotOutput("plot_category")
          ),
          box(
            title = "Recommendation Types", status = "info",
            width = 6,
            plotOutput("plot_type")
          )
        ),
        fluidRow(
          box(
            title = "Your Preventive Care Checklist", status = "success",
            width = 12,
            tableOutput("recommendations_table")
          )
        ),
        fluidRow(
          box(
            title = "Reactive Summary", status = "warning",
            width = 12,
            textOutput("reactive_summary")
          )
        )
      ),
      tabItem("topics",
        fluidRow(
          box(
            title = "Available Health Topics", width = 12,
            dataTableOutput("topics_table")
          )
        )
      ),
      tabItem("about",
        box(
          title = "About ForHer", width = 12,
          includeMarkdown("docs/ABOUT.md")
        )
      )
    )
  )
)

# Server ----
server <- function(input, output, session) {
  
  # Reactive API data
  api_data <- eventReactive(input$fetch_btn, {
    fetch_myhealthfinder(
      age = as.integer(input$age),
      sex = input$sex,
      pregnant = input$pregnant,
      sexually_active = input$sexually_active,
      tobacco_use = input$tobacco_use
    )
  })
  
  # Extract recommendations from API (handles varying response structures)
  recs_df <- reactive({
    data <- api_data()
    if (is.null(data) || is.null(data$Result)) return(NULL)
    r <- data$Result
    recs <- r$Recommendations %||% r$Topics %||% 
            tryCatch(r$Items$Item, error = function(e) NULL) %||%
            r$Item
    if (is.null(recs)) return(NULL)
    if (!is.data.frame(recs)) recs <- as.data.frame(recs, stringsAsFactors = FALSE)
    recs
  })
  
  topics_data <- reactive({
    fetch_itemlist(type = "topic")
  })
  
  categories_data <- reactive({
    fetch_itemlist(type = "category")
  })
  
  # Value boxes
  output$vb_recommendations <- renderValueBox({
    recs <- recs_df()
    n <- if (!is.null(recs)) nrow(recs) else 0
    valueBox(n, "Recommendations", icon = icon("stethoscope"), color = "purple")
  })
  
  output$vb_topics <- renderValueBox({
    data <- topics_data()
    n <- if (!is.null(data) && !is.null(data$Result$Items$Item)) {
      nrow(data$Result$Items$Item)
    } else 0
    valueBox(n, "Health Topics", icon = icon("book-medical"), color = "blue")
  })
  
  output$vb_categories <- renderValueBox({
    data <- categories_data()
    n <- if (!is.null(data) && !is.null(data$Result$Items$Item)) {
      nrow(data$Result$Items$Item)
    } else 0
    valueBox(n, "Categories", icon = icon("folder"), color = "green")
  })
  
  # AI insights
  output$ai_insight_text <- renderUI({
    recs <- recs_df()
    if (is.null(recs)) {
      return(HTML("<p>Click <b>Get Recommendations</b> to fetch your personalized health data, then AI will generate insights.</p>"))
    }
    title_col <- names(recs)[grep("(?i)title", names(recs))][1] %||% names(recs)[1]
    desc_col <- names(recs)[grep("(?i)desc|myhf", names(recs), ignore.case = TRUE)][1] %||% names(recs)[2]
    summary_text <- paste(
      sapply(1:min(5, nrow(recs)), function(i) {
        t <- recs[[title_col]][i]
        d <- if (!is.null(desc_col)) recs[[desc_col]][i] else ""
        paste("-", t, ":", d)
      }), collapse = "\n"
    )
    ctx <- sprintf("Age %s, %s, %s background", input$age, input$sex, input$country_bg)
    insight <- generate_ai_insights(summary_text, ctx)
    HTML(gsub("\n", "<br>", insight))
  })
  
  # Visualization 1: Category distribution
  output$plot_category <- renderPlot({
    recs <- recs_df()
    if (is.null(recs)) {
      return(ggplot() + geom_blank() + theme_minimal() + 
               labs(title = "Fetch data to see chart"))
    }
    cat_col <- names(recs)[grep("category|type", names(recs), ignore.case = TRUE)][1]
    if (is.na(cat_col) || identical(cat_col, character(0))) {
      recs$Category <- "General"
      cat_col <- "Category"
    }
    df <- recs %>% count(.data[[cat_col]], name = "count") %>% arrange(desc(count))
    ggplot(df, aes(x = reorder(.data[[cat_col]], count), y = count, fill = .data[[cat_col]])) +
      geom_col() + coord_flip() + theme_minimal() +
      labs(x = "", y = "Count", title = "Recommendations by Category") +
      theme(legend.position = "none")
  })
  
  # Visualization 2: Type distribution (pie)
  output$plot_type <- renderPlot({
    recs <- recs_df()
    if (is.null(recs)) {
      return(ggplot() + geom_blank() + theme_minimal() + labs(title = "Fetch data to see chart"))
    }
    type_col <- names(recs)[grep("type|category|title", names(recs), ignore.case = TRUE)][1]
    if (is.na(type_col) || identical(type_col, character(0))) recs$Type <- "Recommendation"; type_col <- "Type"
    df <- recs %>% count(.data[[type_col]], name = "n") %>% mutate(pct = n / sum(n) * 100)
    ggplot(df, aes(x = "", y = n, fill = .data[[type_col]])) +
      geom_col() + coord_polar("y") + theme_minimal() +
      labs(title = "Distribution", fill = "") + theme(axis.text = element_blank(), axis.title = element_blank())
  })
  
  # Visualization 3: Recommendations table
  output$recommendations_table <- renderTable({
    recs <- recs_df()
    if (is.null(recs)) return(NULL)
    cols <- intersect(c("Title", "Category", "Type"), names(recs))
    if (length(cols) == 0) cols <- names(recs)[1:min(2, ncol(recs))]
    recs[, cols, drop = FALSE]
  }, striped = TRUE, hover = TRUE)
  
  # Reactive text
  output$reactive_summary <- renderText({
    recs <- recs_df()
    age <- input$age
    sex <- input$sex
    country <- input$country_bg
    if (is.null(recs)) {
      return(sprintf("Hi! You're a %d-year-old %s with %s background. Click 'Get Recommendations' to see your personalized U.S. preventive care guidance.", age, sex, country))
    }
    n <- nrow(recs)
    sprintf("Based on your profile (age %d, %s, %s), the U.S. MyHealthfinder API recommends %d preventive care items. These are evidence-based guidelines from the U.S. Department of Health and Human Services.", age, sex, country, n)
  })
  
  # Topics table
  output$topics_table <- renderDataTable({
    data <- topics_data()
    if (is.null(data) || is.null(data$Result$Items$Item)) return(data.frame())
    data$Result$Items$Item
  }, options = list(pageLength = 10))
}

# Run app
shinyApp(ui, server)
