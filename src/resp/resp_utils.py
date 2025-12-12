from typing import Dict, Any, List, Optional, Tuple
import networkx as nx
from shapely.geometry import (
    Polygon,
    MultiPolygon,
    LineString,
    MultiLineString,
    Point,
    GeometryCollection,
)
from matplotlib.axes import Axes
import matplotlib.pyplot as plt
import geopandas as gpd


CATEGORY_COLORS: Dict[str, str] = {
    "living": "#d9d9d9",  # light gray
    "bedroom": "#66c2a5",  # greenish
    "bathroom": "#fc8d62",  # orange
    "kitchen": "#8da0cb",  # blue
    "door": "#e78ac3",  # pink
    "window": "#a6d854",  # lime
    "wall": "#ffd92f",  # yellow
    "front_door": "#a63603",  # dark reddish-brown
    "balcony": "#b3b3b3",  # dark gray
}


def normalize_keys(plan: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize common key typos / variations in-place (balacony→balcony)."""
    if "balacony" in plan and "balcony" not in plan:
        plan["balcony"] = plan.pop("balacony")
    return plan


def get_geometries(geom_data: Any) -> List[Any]:
    """Safely extract individual geometries from single/multi/collections."""
    if geom_data is None:
        return []
    if isinstance(geom_data, (Polygon, LineString, Point)):
        return [] if geom_data.is_empty else [geom_data]
    if isinstance(geom_data, (MultiPolygon, MultiLineString, GeometryCollection)):
        return [g for g in geom_data.geoms if g is not None and not g.is_empty]
    return []


def plan_to_graph(plan: Dict[str, Any], buffer_factor: float = 0.75) -> nx.Graph:
    """Create a simple room graph: nodes are room parts; edges denote adjacency or connections via door/window."""
    plan = normalize_keys(plan)
    G = nx.Graph()
    ww = float(plan.get("wall_width", 0.1) or 0.1)
    buf = max(ww * buffer_factor, 0.01)

    nodes_by_type: Dict[str, List[str]] = {
        k: []
        for k in ["living", "kitchen", "bedroom", "bathroom", "balcony", "front_door"]
    }

    # rooms
    for room_type in ["living", "kitchen", "bedroom", "bathroom", "balcony"]:
        parts = get_geometries(plan.get(room_type))
        # for living, keep separate parts; user can union beforehand if desired
        for i, geom in enumerate(parts):
            if isinstance(geom, Polygon) and not geom.is_empty:
                nid = f"{room_type}_{i}"
                G.add_node(nid, geometry=geom, type=room_type, area=geom.area)
                nodes_by_type[room_type].append(nid)

    # front door (may be line/polygon)
    for i, geom in enumerate(get_geometries(plan.get("front_door"))):
        nid = f"front_door_{i}"
        G.add_node(
            nid, geometry=geom, type="front_door", area=getattr(geom, "area", 0.0)
        )
        nodes_by_type["front_door"].append(nid)

    doors = get_geometries(plan.get("door"))
    wins = get_geometries(plan.get("window"))
    conns = [(d, "via_door") for d in doors] + [(w, "via_window") for w in wins]

    # front_door → living
    for fd in nodes_by_type["front_door"]:
        fd_geom = G.nodes[fd]["geometry"]
        for gen in nodes_by_type["living"]:
            gen_geom = G.nodes[gen]["geometry"]
            if fd_geom.intersects(gen_geom.buffer(buf)):
                G.add_edge(fd, gen, type="direct")

    # adjacency: kitchen/bedroom ↔ living
    for room_type in ["kitchen", "bedroom"]:
        for rn in nodes_by_type[room_type]:
            rgeom = G.nodes[rn]["geometry"].buffer(buf)
            for gen in nodes_by_type["living"]:
                gen_geom = G.nodes[gen]["geometry"]
                if rgeom.buffer(buf).intersects(gen_geom.buffer(buf)):
                    G.add_edge(rn, gen, type="adjacency")

    # bathroom & balcony connections via door/window to living/bedroom
    for room_type in ["bathroom", "balcony"]:
        for rn in nodes_by_type[room_type]:
            rgeom = G.nodes[rn]["geometry"].buffer(buf)
            for cgeom, ctype in conns:
                if not cgeom.intersects(rgeom):
                    continue
                for target_type in ["living", "bedroom"]:
                    for tn in nodes_by_type[target_type]:
                        tgeom = G.nodes[tn]["geometry"].buffer(buf)
                        if cgeom.intersects(tgeom):
                            if not G.has_edge(rn, tn):
                                G.add_edge(rn, tn, type=ctype)
    return G


def plot_plan(
    plan: Dict[str, Any],
    categories: Optional[List[str]] = None,
    colors: Dict[str, str] = CATEGORY_COLORS,
    ax: Optional[Axes] = None,
    legend: bool = True,
    title: Optional[str] = None,
    tight: bool = True,
) -> Axes:
    """Plot a single plan with colored layers."""
    plan = normalize_keys(plan)
    if categories is None:
        categories = [
            "living",
            "bedroom",
            "bathroom",
            "kitchen",
            "door",
            "window",
            "wall",
            "front_door",
            "balcony",
        ]

    geoms, color_list, present = [], [], []
    for key in categories:
        geom = plan.get(key)
        if geom is None:
            continue
        parts = get_geometries(geom)
        if not parts:
            continue
        geoms.extend(parts)
        color_list.extend([colors.get(key, "#000000")] * len(parts))
        present.append(key)

    if not geoms:
        raise ValueError("No geometries to plot.")

    gseries = gpd.GeoSeries(geoms)
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 8))
    gseries.plot(ax=ax, color=color_list, edgecolor="black", linewidth=0.5)
    ax.set_aspect("equal", adjustable="box")
    ax.set_axis_off()

    if title:
        ax.set_title(title)

    if legend:
        from matplotlib.patches import Patch

        uniq_present = list(dict.fromkeys(present))  # preserve order
        handles = [
            Patch(
                facecolor=colors.get(k, "#000000"),
                edgecolor="black",
                label=k.replace("_", " "),
            )
            for k in uniq_present
        ]
        ax.legend(
            handles=handles, loc="upper left", bbox_to_anchor=(1, 1), frameon=False
        )

    if tight:
        plt.tight_layout()
    return ax


def plot_plan_and_graph(
    plan: Dict[str, Any],
    ax: Optional[Axes] = None,
    node_scale: Tuple[float, float] = (150, 1000),
    title: Optional[str] = None,
) -> Axes:
    """Plot plan and overlay the room graph (node size scaled by room area)."""
    G = plan["graph"] if "graph" in plan else plan_to_graph(plan)
    ax = plot_plan(plan, legend=True, ax=ax, title=title)

    # node positions = centroids
    pos = {}
    for n, data in G.nodes(data=True):
        geom = data.get("geometry")
        if geom is None or geom.is_empty:
            continue
        c = geom.centroid
        pos[n] = (c.x, c.y)

    # style maps
    node_style = {
        "living": dict(color="white", shape="o", size=400, edgecolor="black"),
        "bedroom": dict(color="cyan", shape="s", size=300, edgecolor="black"),
        "bathroom": dict(color="magenta", shape="D", size=260, edgecolor="black"),
        "kitchen": dict(color="yellow", shape="^", size=300, edgecolor="black"),
        "balcony": dict(color="lightgray", shape="X", size=260, edgecolor="black"),
        "front_door": dict(color="red", shape="*", size=420, edgecolor="black"),
    }

    # draw nodes per type for shapes
    nodes_plotted = set()
    min_size, max_size = node_scale
    # area-based scaling
    areas = [G.nodes[n].get("area", 0.0) for n in G.nodes]
    a_min = min(areas) if areas else 0.0
    a_max = max(areas) if areas else 1.0

    def scale_size(a):
        if a_max <= a_min:
            return (min_size + max_size) / 2
        t = (a - a_min) / (a_max - a_min)
        return min_size + t * (max_size - min_size)

    for t, style in node_style.items():
        nlist = [n for n, d in G.nodes(data=True) if d.get("type") == t and n in pos]
        if not nlist:
            continue
        sizes = [scale_size(G.nodes[n].get("area", 0.0)) for n in nlist]
        nx.draw_networkx_nodes(
            G,
            pos,
            nodelist=nlist,
            node_size=sizes,
            node_shape=style["shape"],  # pyright: ignore[reportArgumentType]
            node_color=style["color"],
            edgecolors=style["edgecolor"],
            linewidths=1.0,
            ax=ax,
            alpha=0.9,
        )
        nodes_plotted.update(nlist)

    # edges by type
    edge_style = {
        "direct": dict(color="darkred", width=2.0, style="-"),
        "adjacency": dict(color="darkgreen", width=1.5, style="--"),
        "via_door": dict(color="darkblue", width=1.2, style="-"),
        "via_window": dict(color="orange", width=1.0, style=":"),
    }
    for etype, style in edge_style.items():
        elist = [
            (u, v)
            for u, v, d in G.edges(data=True)
            if d.get("type") == etype and u in pos and v in pos
        ]
        if not elist:
            continue
        nx.draw_networkx_edges(
            G,
            pos,
            edgelist=elist,
            width=style["width"],
            edge_color=style["color"],
            style=style["style"],
            ax=ax,
            alpha=0.8,
        )

    if title:
        ax.set_title(title)
    plt.tight_layout()
    return ax
