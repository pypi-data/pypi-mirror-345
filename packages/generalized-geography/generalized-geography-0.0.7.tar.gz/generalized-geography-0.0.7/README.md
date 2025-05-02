# Generalized Geography Game Solver

## Install

```console
$ pip install generalized-geography
```

## Example

```python
import generalized_geography as gg
graph = gg.UnlabeledMultiDiGraph()
graph.add_edges_from([(0, 1), (0, 1), (1, 2), (2, 3),
                     (3, 0), (1, 2), (2, 3), (0, 2)])
solver = gg.DEGSolver(graph)
solver.completely_classify()
print(solver.winlose)
# {0: 1, 1: 0, 2: 1, 3: 0}
```

## Documentation

### RDG

Directed Edge/Vertex Geography with Repetitions

### DEG

Directed Edge Geography

### DVG

Directed Vertex Geography

### CDEG

Changeable Directed Vertex Geography
