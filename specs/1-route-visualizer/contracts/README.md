# API Contracts: Dual-Map Route Visualizer

**Feature**: 1-route-visualizer  
**Phase**: 1 (Design & Contracts)  
**Date**: 2026-02-06  
**Contract Type**: Python Function Interfaces (not REST API)

## Purpose

This directory defines the public interfaces for all modules in the route visualizer application. These contracts serve as the specification for implementation and enable contract testing.

**Note**: This is a Streamlit application, not a web service, so contracts are Python function signatures rather than HTTP endpoints.

## Contract Files

- [algorithm_contracts.py](algorithm_contracts.py) - A* and Dijkstra pathfinding functions
- [service_contracts.py](service_contracts.py) - Google Maps API integration functions
- [ui_contracts.py](ui_contracts.py) - Streamlit UI component functions

Each contract file includes:
- Type-annotated function signatures
- Docstring specifications (input/output formats, exceptions)
- Example usage
- Test assertions for contract validation
