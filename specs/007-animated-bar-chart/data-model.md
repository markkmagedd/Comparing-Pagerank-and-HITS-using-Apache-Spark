# Data Model: Animated Bar Chart

## Entities

### `YearlyRankings`
Represents the state of the top clubs for a specific calendar year.

**Fields**:
- `year` (Integer): The calendar year for these rankings.
- `clubs` (Array of `ClubRank`): An ordered list of the top clubs for this year.

### `ClubRank`
Represents an individual club's score and position in a given year.

**Fields**:
- `club_id` (String): Unique identifier for the club (used to trigger details popup).
- `club_name` (String): Display name of the club.
- `score` (Float): The PageRank or HITS score for this year.
- `rank` (Integer): The integer ranking position (1 through 10).
