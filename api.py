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
import cechmate as cm
from scipy import sparse
from gtda.homology import VietorisRipsPersistence, EuclideanCechPersistence


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
    max_distance: float = 0.5


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
        "filtration": {
            "range": [0, 1],
            "simplices": [
                {
                    "value": cube.value,
                    "points": [grid[point] for point in cube.points],
                    "dimension": cube.dimension,
                } for cube in filtration.body
            ],
        },
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
async def get_vr_homology(data: VietorisRipsHomologyInput):
    points = np.array(data.points)
    N, dim = points.shape
    rips = cm.Rips()
    filt = rips.build(points)
    filt = [(simplex, value / 2) for simplex, value in filt]  # Make the indx to be the radius of circles
    filt_range = [min(filt, key=lambda x: x[1])[1], max(filt, key=lambda x: x[1])[1]]
    diagrams = cm.solver.phat_diagrams(filt, verbose=False)
    diagrams[0] = np.concatenate([diagrams[0], np.array([filt_range])])  # Append first connected component to compare with Cubix
    return {
        "filtration": {
            "range": filt_range,
            "simplices": [
                {
                    "value": value,
                    "points": points[simplex].tolist(),
                    "dimension": len(simplex) - 1,
                } for simplex, value in filt
            ],
        },
        "holes": [
            {
                "birth": birth,
                "death": death,
                "lifetime": death - birth,
                "dimension": dim,
            } for dim, simplices in enumerate(diagrams) for birth, death in simplices
        ],
    }


@app.post("/api/get-cech-homology/")
async def get_cech_homology(data: VietorisRipsHomologyInput):
    points = np.array(data.points)
    N, dim = points.shape
    cech = cm.Cech()
    filt = cech.build(points)
    filt_range = [min(filt, key=lambda x: x[1])[1], max(filt, key=lambda x: x[1])[1]]
    diagrams = cm.solver.phat_diagrams(filt, verbose=False)
    diagrams[0] = np.concatenate([diagrams[0], np.array([filt_range])])  # Append first connected component to compare with Cubix
    return {
        "filtration": {
            "range": filt_range,
            "simplices": [
                {
                    "value": value,
                    "points": points[simplex].tolist(),
                    "dimension": len(simplex) - 1,
                } for simplex, value in filt
            ],
        },
        "holes": [
            {
                "birth": birth,
                "death": death,
                "lifetime": death - birth,
                "dimension": dim,
            } for dim, simplices in enumerate(diagrams) for birth, death in simplices
        ],
    }
