# AI-Powered Insights Module
# Supports Ollama (local) or OpenAI API

#' Generate AI insights from health data
#' Uses OpenAI API if OPENAI_API_KEY is set, otherwise tries Ollama
#' @param data_summary Text summary of the health data
#' @param user_context Optional context (age, country, etc.)
generate_ai_insights <- function(data_summary, user_context = "") {
  api_key <- Sys.getenv("OPENAI_API_KEY")
  
  if (nchar(api_key) > 0) {
    return(generate_openai_insights(data_summary, user_context, api_key))
  }
  
  # Fallback: try Ollama (local)
  return(generate_ollama_insights(data_summary, user_context))
}

#' OpenAI API integration
generate_openai_insights <- function(data_summary, user_context, api_key) {
  prompt <- sprintf(
    "You are a helpful health educator for first-generation and international female students in the U.S. 
Summarize these preventive health recommendations in plain, friendly language. Keep it under 150 words.
%s

User context: %s

Provide a brief, encouraging summary with 2-3 key takeaways.",
    data_summary,
    if (nchar(user_context) > 0) user_context else "General audience"
  )
  
  response <- tryCatch({
    result <- httr::POST(
      url = "https://api.openai.com/v1/chat/completions",
      httr::add_headers(
        "Authorization" = paste("Bearer", api_key),
        "Content-Type" = "application/json"
      ),
      body = jsonlite::toJSON(list(
        model = "gpt-4o-mini",
        messages = list(list(role = "user", content = prompt)),
        max_tokens = 300
      ), auto_unbox = TRUE),
      encode = "json"
    )
    if (httr::status_code(response) == 200) {
      content <- httr::content(response, "parsed")
      content$choices[[1]]$message$content
    } else {
      paste("AI unavailable. Status:", httr::status_code(response))
    }
  }, error = function(e) {
    paste("AI error:", e$message)
  })
  return(response)
}

#' Ollama integration (local LLM)
generate_ollama_insights <- function(data_summary, user_context) {
  prompt <- sprintf(
    "Summarize these U.S. preventive health recommendations in plain language for international students. 2-3 key takeaways. Under 150 words.\n\n%s",
    data_summary
  )
  
  response <- tryCatch({
    result <- httr::POST(
      url = "http://localhost:11434/api/generate",
      body = jsonlite::toJSON(list(
        model = "llama2",
        prompt = prompt,
        stream = FALSE
      ), auto_unbox = TRUE),
      encode = "json",
      httr::timeout(30)
    )
    if (httr::status_code(result) == 200) {
      content <- httr::content(result, "parsed")
      content$response
    } else {
      "Ollama not running. Set OPENAI_API_KEY for cloud AI, or start Ollama locally."
    }
  }, error = function(e) {
    "AI unavailable. Set OPENAI_API_KEY or run Ollama (ollama run llama2)."
  })
  return(response)
}
