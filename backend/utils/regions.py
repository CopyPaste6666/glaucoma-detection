# backend/utils/regions.py
import numpy as np

def generate_region_masks(h=384, w=384):
    Y, X = np.ogrid[:h, :w]
    cy, cx = h // 2, w // 2

    optic_cup = (X - cx)**2 + (Y - cy)**2 <= 30**2
    optic_disc = (X - cx)**2 + (Y - cy)**2 <= 55**2
    peripapillary = ((X - cx)**2 + (Y - cy)**2 <= 90**2) & ~optic_disc
    background = ~(optic_disc | peripapillary)

    return [
        ("Peripapillary", peripapillary.astype(float)),
        ("Optic Cup", optic_cup.astype(float)),
        ("Optic Disc", optic_disc.astype(float)),
        ("Background", background.astype(float))
    ]
