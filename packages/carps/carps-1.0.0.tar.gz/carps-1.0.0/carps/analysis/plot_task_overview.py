from __future__ import annotations

from multiprocessing import Pool
from pathlib import Path

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from omegaconf import OmegaConf

from carps.analysis.utils import savefig, setup_seaborn


def read_task(p) -> dict:
    cfg = OmegaConf.load(p)
    task = OmegaConf.to_container(cfg.task)
    task["benchmark_id"] = cfg.benchmark_id
    task["task_id"] = cfg.task_id
    return task

def read_task_info(config_folder: str = "carps/configs/task") -> pd.DataFrame:
    config_folder = Path(config_folder)
    paths = list(config_folder.glob("**/*.yaml"))
    paths = [p for p in paths if "DUMMY" not in str(p)]

    with Pool() as pool:
        tasks = pool.map(read_task, paths)
    return pd.DataFrame(tasks)


def build_task_info(tasks: pd.DataFrame) -> pd.DataFrame:
    task_info = []
    for benchmark_id, tasks_id in tasks.groupby(by="benchmark_id"):
        BB = len(tasks_id[(tasks_id["n_objectives"]==1) & (~tasks_id["is_multifidelity"])])
        MF = len(tasks_id[(tasks_id["n_objectives"]==1) & (tasks_id["is_multifidelity"])])
        MO = len(tasks_id[(tasks_id["n_objectives"]>1) & (~tasks_id["is_multifidelity"])])
        MOMF = len(tasks_id[(tasks_id["n_objectives"]>1) & (tasks_id["is_multifidelity"])])
        dimensions = list(tasks_id["dimensions"])
        real = len(tasks_id[tasks_id["objective_function_approximation"]=="real"])
        tab = len(tasks_id[tasks_id["objective_function_approximation"]=="tabular"])
        surr = len(tasks_id[tasks_id["objective_function_approximation"]=="surrogate"])
        floats = tasks_id["search_space_n_floats"].sum()
        ints = tasks_id["search_space_n_integers"].sum()
        cats = tasks_id["search_space_n_categoricals"].sum()
        ords = tasks_id["search_space_n_ordinals"].sum()

        task_info.append( {
            "benchmark_id": benchmark_id,
            "Scenario": {
                "BB": BB,
                "MF": MF,
                "MO": MO,
                "MOMF": MOMF,
            },
            "Dimensions": dimensions,
            "Objective Function": {
                "real": real,
                "tab": tab,
                "surr": surr
            },
            "HP Types": {
                "float": floats,
                "int": ints,
                "cat": cats,
                "ord": ords,
            }
        }
    )
    return pd.DataFrame(task_info)


def plot_task_overview(tasks: pd.DataFrame) -> None:
    setup_seaborn()

    benchmark_id_list = tasks.benchmark_id.unique()

    colors = dict(zip(benchmark_id_list, ["#88CCEE", "#117733", "#999933", "#DDCC77", "#CC6677", "#882255"], strict=False))

    fig, axs = plt.subplots(1, 4, figsize=(20, 5))

    task_types = {}
    obj_fun = {}
    hp_types = {}
    dimensions = {}

    shift = 0.08
    bar_width = 0.4

    task_info = build_task_info(tasks=tasks)

    # Iterate over the dictionaries in the list
    for i, (_, data_entry) in enumerate(task_info.iterrows()):
        task_types[benchmark_id_list[i]] = data_entry["Scenario"]
        dimensions[benchmark_id_list[i]] = data_entry["Dimensions"]
        obj_fun[benchmark_id_list[i]] = data_entry["Objective Function"]
        hp_types[benchmark_id_list[i]] = data_entry["HP Types"]

    dimensions_sorted = dict(sorted(dimensions.items(), key=lambda item: max(item[1]), reverse=True))
    for _, (key, values) in enumerate(dimensions_sorted.items()):
        axs[1].hist(values, bins=np.arange(min(values), max(values) + 1,3), color=colors[key])

    task_types_sorted = dict(sorted(task_types.items(), key=lambda item: max(item[1].values()), reverse=True))
    for i, (key, values) in enumerate(task_types_sorted.items()):
        x = np.arange(len(values.keys())) + i * shift
        axs[0].bar(x, values.values(), color=colors[key], width=bar_width)
        axs[0].set_xticks(x)
        axs[0].set_xticklabels(values.keys())

    obj_fun_sorted = dict(sorted(obj_fun.items(), key=lambda item: max(item[1].values()), reverse=True))
    for i, (key, values) in enumerate(obj_fun_sorted.items()):
        x = np.arange(len(values.keys())) + i * shift
        axs[2].bar(x, values.values(), color=colors[key], width=bar_width)
        axs[2].set_xticks(x)
        axs[2].set_xticklabels(values.keys())

    hp_types_sorted = dict(sorted(hp_types.items(), key=lambda item: max(item[1].values()), reverse=True))
    for i, (key, values) in enumerate(hp_types_sorted.items()):
        x = np.arange(len(values.keys())) + i * shift
        axs[3].bar(x, values.values(), color=colors[key], width=bar_width)#, alpha=0.5)
        axs[3].set_xticks(x)
        axs[3].set_xticklabels(values.keys())

    # Add a legend to each subplot
    for i, ax in enumerate(axs):
        ax.tick_params(axis="both", which="major", labelsize=22)
        ax.set_yscale("log")
        ax.set_title(list(data_entry.keys())[i+1], fontsize=26)

    legend_handles = [mpatches.Patch(color=color, label=name) for name, color in colors.items()]

    ax.legend(handles=legend_handles, fontsize=20, bbox_to_anchor=(1.05, 1), loc="upper left")

    plt.tight_layout()
    savefig(fig, "benchmark_footprint")
    plt.show()


if __name__ == "__main__":
    tasks = read_task_info()
    plot_task_overview(tasks=tasks)