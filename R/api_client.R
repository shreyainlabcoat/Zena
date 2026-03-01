# MyHealthfinder API Client
# Base URL: https://odphp.health.gov/myhealthfinder/api/v4/
# No API key required - U.S. HHS public API

BASE_URL <- "https://odphp.health.gov/myhealthfinder/api/v4"

#' Fetch personalized preventive care recommendations
#' @param age User age (integer)
#' @param sex "male" or "female"
#' @param pregnant "yes" or "no" (if female)
#' @param sexually_active "yes" or "no"
#' @param tobacco_use "yes" or "no"
#' @param lang "en" or "es"
fetch_myhealthfinder <- function(age = 25, sex = "female", pregnant = "no",
                                 sexually_active = "yes", tobacco_use = "no",
                                 lang = "en") {
  url <- sprintf("%s/myhealthfinder.json?age=%d&sex=%s&pregnant=%s&sexuallyActive=%s&tobaccoUse=%s&Lang=%s",
                 BASE_URL, age, sex, pregnant, sexually_active, tobacco_use, lang)
  response <- tryCatch({
    jsonlite::fromJSON(url)
  }, error = function(e) {
    message("API Error: ", e$message)
    return(NULL)
  })
  return(response)
}

#' Fetch list of health topics or categories
#' @param type "topic" or "category"
#' @param lang "en" or "es"
fetch_itemlist <- function(type = "topic", lang = "en") {
  url <- sprintf("%s/itemlist.json?Type=%s&Lang=%s", BASE_URL, type, lang)
  response <- tryCatch({
    jsonlite::fromJSON(url)
  }, error = function(e) {
    message("API Error: ", e$message)
    return(NULL)
  })
  return(response)
}

#' Fetch details for a specific topic
#' @param topic_id Topic ID from itemlist
#' @param lang "en" or "es"
fetch_topic <- function(topic_id, lang = "en") {
  url <- sprintf("%s/topicsearch.json?TopicId=%s&Lang=%s", BASE_URL, topic_id, lang)
  response <- tryCatch({
    jsonlite::fromJSON(url)
  }, error = function(e) {
    message("API Error: ", e$message)
    return(NULL)
  })
  return(response)
}
