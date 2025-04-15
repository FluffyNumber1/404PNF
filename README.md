# 404: Path Not Found!

A full-stack web application that visualizes pathfinding algorithms (BFS, DFS, and Dijkstra's) on real-world map data. Built for exploring how different search strategies perform across different environments.

## Project Summary 
Problem: NPCs in open-world games often struggle with efficient pathfinding, leading to poor user experiences and performance issues.

Solution: We simulate real-world pathfinding by applying search algorithms to actual map data using OpenStreetMap, providing a clean UI for comparison and visualization.

### Data
- Map data sourced from [OpenStreetMap](https://www.openstreetmap.org/)
- Extracted using [BBBike](https://extract.bbbike.org/)

## Getting Started

### 1. Install dependencies
**Python packages:**

pip install -r requirements.txt

### 2. Start the Frontend
  -Open the project folder in VS Code.
  
  -Open a new terminal inside VS Code.
  
  -Run the following command to start the local development server: **npm run dev**

### 3. Start the Backend Server
  -Open another terminal (can be Command Prompt or PowerShell).
  
  -Navigate to the project directory (if you’re not already there).
  
  -Run the Python server using: **python backend/server.py**

## The Team
👥 Team
Ryan Nadanam — UI/UX Frontend Structure & Dijkstra’s Implementation (FluffyNumber1)

Kiran Nadanam — Map Interface, Data Extraction, Backend Integration (kirannadanam)

Matthew Edelman — BFS & DFS Implementation
