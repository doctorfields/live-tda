from typing import List, Optional
from enum import Enum
from itertools import combinations

from fastapi import FastAPI, Request, Body
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
import cubix
from scipy.spatial import distance_matrix
from gtda.homology import VietorisRipsPersistence


class ShapeType(Enum):
    circle = "s1"
    two_circles = "s1vs1"

    @property
    def cloud(self):
        return {
            "s1": cubix.S1,
            "s1vs1": cubix.S1vS1,
        }.get(self.value)


class CubicalHomologyInput(BaseModel):
    points: List[List[float]]
    precision: int = 20
    margin: float = 0.5
    kde_precision: int = 100
    kde_bw: Optional[float] = None


class VietorisRipsHomologyInput(BaseModel):
    points: List[List[float]]


app = FastAPI()

# app.mount("/dist", StaticFiles(directory="frontend/dist/"), name="dist")
# app.mount("/css", StaticFiles(directory="frontend/dist/css"), name="css")
# app.mount("/img", StaticFiles(directory="frontend/dist/img"), name="img")
# app.mount("/js", StaticFiles(directory="frontend/dist/js"), name="js")
# templates = Jinja2Templates(directory="frontend/dist")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:8080", "https://doctorfields.github.io/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# @app.get("/", response_class=HTMLResponse)
# async def root(request: Request):
#     return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/generate-data/")
async def generate_data(shape: ShapeType = ShapeType.circle, N: int = 1000, error: float = 0.1, seed: int = 42):
    X = shape.cloud(N=N, err=error, seed=seed)
    return {
        "points": X.data.T.tolist(),
    }


@app.post("/api/get-cubical-homology/")
async def get_cubical_homology(data: CubicalHomologyInput):
    X = cubix.Cloud(data=np.array(data.points).T, bw_method=data.kde_bw)
    homology = X.persistent_homology(n=data.precision, margin=data.margin)
    filtration = homology.filtration
    grid = filtration.grid
    return {
        "filtration": [
            {
                "value": cube.value,
                "points": [grid[point] for point in cube.points],
                "dimension": cube.dimension,
            } for cube in filtration.body
        ],
        "grid": [m.tolist() for m in grid.mounting],
        "holes": [
            {
                "birth": g.born,
                "death": g.death,
                "lifetime": g.life(),
                "dimension": dim,
            } for dim, holes in enumerate(homology.holes) for g in holes
        ],
        "kde": cubix.Grid(X, data.kde_precision, data.margin).evaluate(X.kde).tolist(),
    }


@app.post("/api/get-vr-homology/")
async def vr_homology(data: VietorisRipsHomologyInput):
    points = np.array(data.points)
    N, dim = points.shape
    VR = VietorisRipsPersistence(homology_dimensions=list(range(dim)))
    d = distance_matrix(points, points)
    filtration = []
    for dim in range(dim + 1):
        for comb in combinations(range(N), dim+1):
            filtration.append({
                "points": [points[i].tolist() for i in comb],
                "value": max(d[i,j] for i,j in combinations(comb, 2)) if len(comb) > 1 else 0
            })
    filtration.sort(key=lambda x: x["value"])
    diagrams = VR.fit_transform([points])[0]
    return {
        "filtration": [
            {
                "value": simplex["value"],
                "points": simplex["points"],
                "dimension": len(simplex["points"]) - 1,
            } for simplex in filtration
        ],
        "holes": [
            {
                "birth": born,
                "death": death,
                "lifetime": death - born,
                "dimension": dim,
            } for born, death, dim in diagrams
        ],
    }
