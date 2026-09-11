# PivotPoint-OR

Operations Research is elegant—until the third tableau starts looking suspiciously like the first.

PivotPoint-OR began as a way to turn lengthy handwritten calculations into understandable Python experiments. The goal is simple: implement common OR algorithms, display how each iteration works, and make learning optimization slightly less exhausting.

## Planned Methods

- Standard Simplex Method
- Big-M Method
- Two-Phase Method
- Dual Simplex Method
- Gomory Cutting-Plane Algorithm

## What the Tool Will Do

- Accept objective functions and constraints
- Solve problems step by step
- Display tableaux, pivot columns, pivot rows and key elements
- Show the final optimal solution
- Visualize selected two-variable problems

## Project Structure

```text
src/solvers/    Algorithm implementations
src/utils/      Input and tableau utilities
tests/          Algorithm tests
examples/       Sample OR problems
visuals/        Generated visualizations
results/        Experimental outputs
