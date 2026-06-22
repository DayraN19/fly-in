*This project has been created as part of the 42 curriculum by bgranier*

# Fly-in

## Description

**Fly-in** is a drone routing simulation project that schedules a fleet of autonomous drones across a network of connected zones, from a unique start hub to a unique end hub, in the minimum number of simulation turns.

The project parses a custom map file format describing zones (`normal`, `restricted`, `priority`, `blocked`) and connections between them (with optional capacity constraints), then computes a turn-by-turn movement plan for every drone while respecting:

- Zone occupancy limits (`max_drones`)
- Connection capacity limits (`max_link_capacity`)
- Movement costs tied to zone type (1 turn for `normal`/`priority`, 2 turns for `restricted`, impossible for `blocked`)
- Collision and deadlock avoidance between simultaneously moving drones

The goal is to deliver all drones to the end zone as fast as possible, while providing a clear visual representation of the simulation as it unfolds.

[Add a short paragraph here describing what makes your specific implementation interesting: e.g. your overall approach, what problem you found most challenging, what you're proud of.]

## Instructions

### Requirements

- Python 3.10 or later
- [`pygame`]

### Installation

```bash
make install
```



### Running the simulation

```bash
make run
```

### Debug mode

```bash
make debug
```

Runs the main script under Python's built-in debugger (`pdb`).

### Linting

```bash
make lint
```

Runs `flake8` and `mypy` with the required flags. An optional stricter check is available via:

```bash
make lint-strict
```

### Cleaning

```bash
make clean
```

Removes `__pycache__`, `.mypy_cache`, and other temporary artifacts.

## Algorithm and Implementation Strategy

[This section is mandatory — describe your actual choices in detail. Suggested structure below.]

### Parsing


### Pathfinding

- **Algorithm used:** [Dijkstra / A* / BFS / custom heuristic / other]
- **Why this algorithm:** [Justify the choice given the cost model — restricted zones cost 2 turns, priority zones should be favored, etc.]
- **Complexity:** [State the time/space complexity, e.g. O(E log V) per drone, or for the whole fleet]
- **Path caching:** [Do you recompute paths every turn, cache them, or recompute only on conflict? Explain the trade-off.]


## Performance



| Map | Drones | Target (turns) | Your result |
|---|---|---|---|
| Easy — Linear path | 2 | ≤ 6 | [4] |
| Easy — Simple fork | 4 | ≤ 8 | [6] |
| Easy — Basic capacity | 4 | ≤ 6 | [4] |
| Medium — Dead end trap | 5 | ≤ 12 | [8] |
| Medium — Circular loop | 6 | ≤ 15 | [15] |
| Medium — Priority puzzle | 5 | ≤ 12 | [7] |
| Hard — Maze nightmare | 8 | ≤ 30 | [14] |
| Hard — Capacity hell | 12 | ≤ 35 | [17] |
| Hard — Ultimate challenge | 15 | ≤ 45 | [30] |
| Challenger — The Impossible Dream (bonus) | 25 | ≤ 45 (record) | [74] |

## Resources

### References

- [Dijkstra's algorithm — Wikipedia / original paper]
- [A* search algorithm — documentation or article]
- [Python `typing` and `mypy` documentation]

### AI usage


AI tools were used during this project for the following tasks:

- **[Task, e.g. brainstorming pathfinding strategies]:** 
- **[Task, e.g. debugging a specific scheduling conflict]:** 
- **[Task, e.g. reviewing docstring/PEP 257 formatting]:**

AI-generated suggestions were reviewed, tested, and discussed with peers before being integrated. No code was used without being fully understood by the team.
