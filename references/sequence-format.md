# Visio Sequence Diagram JSON Spec

Use this format with `scripts/New-VisioDiagram.py` to create UML-style sequence diagrams.

## Format Overview

```json
{
  "type": "sequence",
  "title": "User Login Flow",
  "actors": [],
  "messages": [],
  "layout": {}
}
```

## Top Level

```json
{
  "type": "sequence",
  "title": "Optional diagram title",
  "actors": [],
  "messages": [],
  "layout": {
    "actorSpacing": 3.0,
    "messageSpacing": 0.6,
    "startY": 8.0,
    "lifelineHeight": 6.0
  }
}
```

**Required**:
- `type`: Must be `"sequence"` to activate sequence diagram mode
- `actors`: Array of participants in the sequence
- `messages`: Array of interactions between actors

**Optional**:
- `title`: Document title
- `layout`: Override default spacing and positioning

## Actor

Represents a participant (user, system, service, database, etc.) in the sequence.

```json
{
  "id": "user",
  "name": "User",
  "type": "actor",
  "fill": "#EFF6FF",
  "line": "#3B82F6"
}
```

**Required**:
- `id`: Unique identifier (used in messages)
- `name`: Display text on the actor box

**Optional**:
- `type`: Visual style hint
  - `"actor"` - Person/user (default: blue)
  - `"system"` - Internal service (default: purple)
  - `"database"` - Data store (default: amber)
  - `"external"` - External API (default: green)
- `fill`: Background color (hex `#RRGGBB`)
- `line`: Border color (hex `#RRGGBB`)

**Default colors by type**:
- `actor`: `#EFF6FF` / `#3B82F6` (blue)
- `system`: `#F5F3FF` / `#8B5CF6` (purple)
- `database`: `#FEF3C7` / `#D97706` (amber)
- `external`: `#ECFDF5` / `#10B981` (green)

## Message

Represents a method call, data flow, or return value between actors.

```json
{
  "from": "user",
  "to": "api",
  "text": "POST /login",
  "type": "sync",
  "activation": true
}
```

**Required**:
- `from`: Source actor `id`
- `to`: Target actor `id`

**Optional**:
- `text`: Label on the arrow
- `type`: Arrow style
  - `"sync"` - Solid arrow (synchronous call, default)
  - `"async"` - Solid arrow (asynchronous call, visually same as sync)
  - `"return"` - Dashed arrow (return value/response)
- `activation`: Boolean, whether to draw an activation box on the target actor during this message (default: `false` for `return`, `true` for others)

**Rendering**:
- Messages are drawn **top-to-bottom** in array order
- Solid arrows (`sync`/`async`) use `endArrow: 4`
- Dashed arrows (`return`) use `linePattern: 2` and `endArrow: 1`
- Activation boxes are thin rectangles overlaid on the lifeline

## Layout (Optional)

```json
{
  "actorSpacing": 3.0,
  "messageSpacing": 0.6,
  "startY": 8.0,
  "lifelineHeight": 6.0
}
```

- `actorSpacing`: Horizontal distance between actor centerlines (default: `3.0` inches)
- `messageSpacing`: Vertical distance between consecutive messages (default: `0.6` inches)
- `startY`: Y coordinate for actor boxes (default: `8.0` inches, top of page)
- `lifelineHeight`: Total height of lifelines (default: `6.0` inches)

## Complete Example

```json
{
  "type": "sequence",
  "title": "User Authentication Flow",
  "actors": [
    {
      "id": "user",
      "name": "User",
      "type": "actor"
    },
    {
      "id": "web",
      "name": "Web App",
      "type": "system"
    },
    {
      "id": "api",
      "name": "Auth Service",
      "type": "system"
    },
    {
      "id": "db",
      "name": "Database",
      "type": "database"
    }
  ],
  "messages": [
    {
      "from": "user",
      "to": "web",
      "text": "Enter credentials",
      "type": "sync"
    },
    {
      "from": "web",
      "to": "api",
      "text": "POST /login",
      "type": "sync"
    },
    {
      "from": "api",
      "to": "db",
      "text": "Query user",
      "type": "sync"
    },
    {
      "from": "db",
      "to": "api",
      "text": "User record",
      "type": "return"
    },
    {
      "from": "api",
      "to": "web",
      "text": "JWT token",
      "type": "return"
    },
    {
      "from": "web",
      "to": "user",
      "text": "Redirect to dashboard",
      "type": "return"
    }
  ],
  "layout": {
    "actorSpacing": 2.8,
    "messageSpacing": 0.5
  }
}
```

## Notes

- Actors are positioned **left-to-right** in array order
- Messages flow **top-to-bottom** in array order
- `from` and `to` must reference valid actor `id` values
- Lifelines are vertical dashed lines extending from each actor box
- Activation boxes are automatically sized and positioned based on message flow
- For readability, limit actors to 4-6 participants; split complex flows into multiple diagrams
