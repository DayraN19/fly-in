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
- [List any dependencies here, e.g. `rich`, `colorama`, `pygame`... or "No external dependencies" if applicable]

### Installation

```bash
make install
```

[Describe what this actually does in your project — e.g. creates a venv and installs requirements via pip/uv/pipx.]

### Running the simulation

```bash
make run
```

[Specify how the map file is passed in — e.g. `python3 main.py maps/easy_2.txt` — and any CLI flags you support (visual mode, verbose output, etc.).]

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

[Describe how the map file is parsed and validated: zone/connection objects, metadata handling, error reporting on malformed input.]

### Pathfinding

- **Algorithm used:** [Dijkstra / A* / BFS / custom heuristic / other]
- **Why this algorithm:** [Justify the choice given the cost model — restricted zones cost 2 turns, priority zones should be favored, etc.]
- **Complexity:** [State the time/space complexity, e.g. O(E log V) per drone, or for the whole fleet]
- **Path caching:** [Do you recompute paths every turn, cache them, or recompute only on conflict? Explain the trade-off.]

### Turn-by-turn scheduling

[Explain how you coordinate multiple drones moving simultaneously: how you detect and resolve zone/connection capacity conflicts, how deadlocks are avoided, how drones are made to wait strategically, and how multi-turn movement into restricted zones is handled (no waiting mid-connection).]

### Design choices / object-oriented structure

[Briefly describe your main classes (e.g. `Zone`, `Connection`, `Drone`, `Map`, `Simulator`, `Scheduler`) and how responsibilities are split between them.]

## Visual Representation

[Describe what you implemented: colored terminal output and/or a graphical interface.]

- **Mode:** [Terminal / GUI / Both]
- **What it shows:** [Drone positions per turn, zone colors matching the metadata, occupancy/capacity indicators, etc.]
- **Why it helps:** [Explain how this visual feedback makes it easier to follow the simulation and verify correctness during peer review.]

[If you have screenshots or a short demo GIF, add them here.]

## Performance

[Optional but recommended — fill in the turn counts you actually achieve on the provided maps, compared to the benchmark targets.]

| Map | Drones | Target (turns) | Your result |
|---|---|---|---|
| Easy — Linear path | 2 | ≤ 6 | [ ] |
| Easy — Simple fork | 4 | ≤ 8 | [ ] |
| Easy — Basic capacity | 4 | ≤ 6 | [ ] |
| Medium — Dead end trap | 5 | ≤ 12 | [ ] |
| Medium — Circular loop | 6 | ≤ 15 | [ ] |
| Medium — Priority puzzle | 5 | ≤ 12 | [ ] |
| Hard — Maze nightmare | 8 | ≤ 30 | [ ] |
| Hard — Capacity hell | 12 | ≤ 35 | [ ] |
| Hard — Ultimate challenge | 15 | ≤ 45 | [ ] |
| Challenger — The Impossible Dream (bonus) | 25 | ≤ 45 (record) | [ ] |

## Resources

### References

[List the classic references you actually used, for example:]

- [Dijkstra's algorithm — Wikipedia / original paper]
- [A* search algorithm — documentation or article]
- [Python `typing` and `mypy` documentation]
- [Any article/tutorial on multi-agent pathfinding or scheduling you consulted]

### AI usage

[This section is mandatory. Be specific and honest about what you used AI for. Example structure below — replace with what actually happened on your project.]

AI tools were used during this project for the following tasks:

- **[Task, e.g. brainstorming pathfinding strategies]:** [What you asked, what you got, how you validated/adapted it]
- **[Task, e.g. debugging a specific scheduling conflict]:** [Same]
- **[Task, e.g. reviewing docstring/PEP 257 formatting]:** [Same]

AI-generated suggestions were reviewed, tested, and discussed with peers before being integrated. No code was used without being fully understood by the team.
