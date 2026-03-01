# LAB: AI-Powered Reporting

## Overview

ForHer uses AI to generate friendly, plain-language summaries of preventive health recommendations. This helps first-gen and international students understand U.S. healthcare guidance without medical jargon.

## AI Providers

### Option 1: OpenAI (Recommended for deployment)

1. Get API key from [platform.openai.com](https://platform.openai.com)
2. Set environment variable:
   ```r
   Sys.setenv(OPENAI_API_KEY = "your-key-here")
   ```
   Or create `.Renviron` in project root:
   ```
   OPENAI_API_KEY=your-key-here
   ```

### Option 2: Ollama (Local, no API key)

1. Install [Ollama](https://ollama.ai)
2. Run: `ollama run llama2`
3. AI module will auto-detect and use Ollama

## Implementation

See `R/ai_insights.R`:
- `generate_ai_insights()` – main entry point
- `generate_openai_insights()` – OpenAI API
- `generate_ollama_insights()` – local Ollama

## Prompt Design

The AI is prompted to:
- Act as a health educator for international students
- Summarize in plain, friendly language
- Keep under 150 words
- Provide 2–3 key takeaways
