# Phase 1: API Contract

## New Endpoint: Fetch Club Transfers

### `GET /api/transfers/{club_name}`

**Query Parameters:**
- `top_n` (int) [Optional, Default=10]: Maximum number of most expensive transfers to return.
- `start_season` (str) [Optional]: Start season filter.
- `end_season` (str) [Optional]: End season filter.

**Response Structure (200 OK):**
```json
{
  "club": "Manchester City",
  "transfers": [
    {
      "player_name": "Jack Grealish",
      "fee": 117.5,
      "counterparty_club": "Aston Villa",
      "direction": "in"
    },
    ...
  ]
}
```

**Response Structure (404/500):**
```json
{
  "error": "Club not found or internal processing error"
}
```
