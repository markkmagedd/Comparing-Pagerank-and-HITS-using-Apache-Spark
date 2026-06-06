# Phase 1: Data Model & State

## Entities Required

### Club Transer Record
Representation of a single transfer payload passed to the frontend.

**Fields**:
- `player_name` (String): Name of the transferred player
- `fee` (Float / String notation depending on app standard): Transfer cost in base currency
- `counterparty_club` (String): The club bought from or sold to
- `direction` (String): "in" or "out" (implicitly defining whether the counterparty is a seller or buyer)

## Frontend State Extensions
- `selected_node`: The club string currently selected in the D3.js/Cytoscape container.
- `popup_state`: 
  - `visible`: Boolean
  - `loading`: Boolean
  - `data`: Array of Transfer Record entities
  - `error`: Nullable String
  - `position`: Coordinates anchored near Graph boundaries or fixed window constraints.
