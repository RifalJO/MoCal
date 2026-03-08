# Log Detail Documentation

## Overview

The `/api/estimate` endpoint now saves detailed logs of every request to the database in the `log_detail` column (JSONB format).

## Log Detail Structure

```json
{
  "parsing": {
    "llm_raw_response": "...",        // First 500 chars of LLM response
    "parsed_items_count": 3,           // Number of items parsed
    "parse_time_ms": 245.67,          // Time taken to parse
    "errors": [],                      // Any errors encountered
    "llm_model": "llama-3.1-8b-instant",
    "input_length": 45
  },
  "matching": [
    {
      "search_name": "nasi padang",
      "search_name_en": "padang rice",
      "steps_tried": ["exact_match", "fuzzy_match"],
      "match_found": true,
      "matched_step": "exact_match",
      "fuzzy_score": 0.95
    },
    {
      "search_name": "tunjang",
      "search_name_en": "beef tendon",
      "steps_tried": ["exact_match", "fuzzy_match", "usda_api"],
      "match_found": true,
      "matched_step": "usda_api",
      "usda_query": "beef tendon"
    }
  ],
  "summary": {
    "total_items_parsed": 3,
    "total_items_matched": 3,
    "unknown_items": [],
    "total_time_ms": 1234.56
  },
  "input": {
    "raw_text": "nasi padang dengan tunjang",
    "text_length": 32
  }
}
```

## Fields Explanation

### Parsing Section
- `llm_raw_response`: Raw LLM output (truncated to 500 chars)
- `parsed_items_count`: Number of food items successfully parsed
- `parse_time_ms`: Time taken for parsing in milliseconds
- `errors`: Array of error messages if any
- `llm_model`: Which LLM model was used
- `input_length`: Length of input text in characters

### Matching Section (Array)
One entry per food item:
- `search_name`: Name searched in database
- `search_name_en`: English name for USDA lookup
- `steps_tried`: Which matching steps were attempted
- `match_found`: Whether a match was found
- `matched_step`: Which step found the match
- `fuzzy_score`: Fuzzy match score (if applicable)
- `usda_query`: USDA search query (if used)
- `llm_estimate`: Whether LLM estimation was used
- `llm_estimate_time_ms`: Time for LLM estimation

### Summary Section
- `total_items_parsed`: Total items from parser
- `total_items_matched`: Items successfully matched
- `unknown_items`: Items that couldn't be identified
- `total_time_ms`: Total processing time

## How to View Logs

### Using psql
```sql
-- View latest logs with details
SELECT 
    id,
    raw_input,
    total_kcal,
    log_detail,
    logged_at
FROM food_logs
ORDER BY logged_at DESC
LIMIT 10;
```

### View specific log detail
```sql
SELECT log_detail->'parsing'->>'parse_time_ms' as parse_time,
       log_detail->'summary'->>'total_time_ms' as total_time,
       jsonb_array_length(log_detail->'matching') as items_matched
FROM food_logs
WHERE id = 'your-log-id';
```

### Find logs with errors
```sql
SELECT id, raw_input, log_detail->'parsing'->'errors' as errors
FROM food_logs
WHERE jsonb_array_length(log_detail->'parsing'->'errors') > 0
ORDER BY logged_at DESC;
```

### Find unknown items
```sql
SELECT id, raw_input, log_detail->'summary'->'unknown_items' as unknown
FROM food_logs
WHERE jsonb_array_length(log_detail->'summary'->'unknown_items') > 0
ORDER BY logged_at DESC;
```

## Migration

If you have an existing database, run the migration:

```bash
# Connect to your PostgreSQL database
psql -U postgres -d calorie_tracker

# Run the migration
\i scripts/add_log_detail_column.sql
```

Or manually:
```sql
ALTER TABLE food_logs ADD COLUMN log_detail JSONB;
```

## Benefits

1. **Debugging**: See exactly what the LLM returned
2. **Performance**: Track parsing and matching times
3. **Quality**: Monitor fuzzy match scores
4. **Analytics**: Understand which matching methods are used most
5. **Troubleshooting**: Identify unknown items easily
