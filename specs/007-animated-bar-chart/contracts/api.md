# API Contract: Animated Bar Chart

## Endpoints

### `GET /api/rankings/historical`

Fetches the pre-calculated yearly historical rankings for animating the bar chart.

**Query Parameters:**
- `algorithm` (Optional Enum: `pagerank`, `hits`): Defines which algorithmic metric to retrieve history for. Defaults to `pagerank`.

**Response Format:**
```json
{
  "status": "success",
  "data": {
    "algorithm": "pagerank",
    "timeline": [
      {
        "year": 2010,
        "clubs": [
          {
            "club_id": "c1",
            "club_name": "FC Barcelona",
            "score": 0.0845,
            "rank": 1
          },
         // ... up to 10 clubs
        ]
      },
      // ... subsequent years
    ]
  }
}
```

**Errors:**
- `400 Bad Request`: If an invalid `algorithm` query parameter is provided.
- `500 Internal Server Error`: If Spark cluster calculation fails.
