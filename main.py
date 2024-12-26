from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Edge(BaseModel):
    source: str
    target: str

class PipelineData(BaseModel):
    nodes: List[dict]  # Change this to List[dict] to handle dictionaries
    edges: List[Edge]

def is_dag(nodes, edges):
    graph = {node['id']: [] for node in nodes}
    for edge in edges:
        graph[edge.source].append(edge.target)

    visited = set()
    rec_stack = set()

    def dfs(node):
        if node in rec_stack:
            return False
        if node in visited:
            return True
        visited.add(node)
        rec_stack.add(node)
        for neighbor in graph[node]:
            if not dfs(neighbor):
                return False
        rec_stack.remove(node)
        return True

    return all(dfs(node) for node in graph)

@app.post('/pipelines/parse')
def parse_pipeline(pipeline_data: PipelineData):
    try:
        num_nodes = len(pipeline_data.nodes)
        num_edges = len(pipeline_data.edges)
        is_dag_flag = is_dag(pipeline_data.nodes, pipeline_data.edges)
        return {
            "num_nodes": num_nodes,
            "num_edges": num_edges,
            "is_dag": is_dag_flag
        }
    except Exception as e:
        print(f"Error: {e}")  # Log the error for debugging
        raise HTTPException(status_code=500, detail="An error occurred while processing the pipeline data")

@app.get('/')
def read_root():
    return {"message": "Welcome to the FastAPI backend for pipeline processing!"}