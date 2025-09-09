import sys
import os
import copy
import json

import pandas as pd
import numpy as np
from evo.core import metrics
from evo.tools import file_interface


def evo_ape(traj, ref_traj):  # Run APE with evo for the ref and gt trajectories
    '''
    Run APE with evo for the ref and gt trajectories.
    This function does not align the trajectories.

    Parameters:
    ref_traj (trajectory): reference trajectory
    gt_traj (trajectory): ground truth trajectory

    Returns:
    dict: APE statistics
    '''
    ape_metric = metrics.APE(metrics.PoseRelation.translation_part)
    ape_metric.process_data((traj, ref_traj))
    ape_stats = ape_metric.get_all_statistics()
    return ape_stats

def evo_rpe(traj, ref_traj):  # Run RPE with evo for the ref and gt trajectories
    '''
    Run RPE with evo for the ref and gt trajectories.
    This function does not align the trajectories.

    Parameters:
    ref_traj (trajectory): reference trajectory
    gt_traj (trajectory): ground truth trajectory

    Returns:
    dict: RPE statistics
    '''
    rpe_metric = metrics.RPE(metrics.PoseRelation.translation_part)
    rpe_metric.process_data((traj, ref_traj))
    rpe_stats = rpe_metric.get_all_statistics()
    return rpe_stats


def set_evo_metric(metric_name):
    if metric_name == 'RPE':
        return metrics.RPE(metrics.PoseRelation.translation_part)
    elif metric_name == 'APE':
        return metrics.APE(metrics.PoseRelation.translation_part)
    else:
        print("Error: Invalid metric")
        sys.exit(1)

def load_euroc_csv_trajectories(paths):
    """
    Load trajectories from Euroc CSV files.

    Parameters:
    paths (list): file paths to load

    Returns:.
    List of trajectories in the same order as paths.
    """
    traj = []
    for path in paths:
        traj.append(file_interface.read_euroc_csv_trajectory(path))
    return traj

def aligned_trajectories(trajectories, align_to):
    """
    Aligns all trajectories to the reference trajectory.

    Parameters:
        trajectories (list): list of trajectories to align
    Returns
        list of aligned trajectories
    """
    aligned = []
    for traj in trajectories:
        aligned_traj = copy.deepcopy(traj)
        aligned_traj.align(align_to, True)
        aligned.append(aligned_traj)
    return aligned

def get_evo_slices(trajectories, ids):
    """
    Get slices of the trajectories in evo format.

    Parameters:
    trajectories (list): list of trajectories
    ids (list): list of ids to slice

    Returns:
    list of slices
    """
    slices = []
    for traj in trajectories:
        slice = copy.deepcopy(traj)
        slice.reduce_to_ids(ids)
        slices.append(slice)
    return slices


def parse_evo_json_files(sequence_paths):
    ape_data = []
    rpe_data = []

    for sequence_path in sequence_paths:
        evo_dirs = [d for d in os.listdir(sequence_path)
                    if os.path.isdir(os.path.join(sequence_path, d)) and (d.startswith('evo_ape') or d.startswith('evo_rpe'))]

        for evo_dir in evo_dirs:
            evo_path = os.path.join(sequence_path, evo_dir)
            info_path = os.path.join(evo_path, 'info.json')
            stats_path = os.path.join(evo_path, 'stats.json')
            timestamps_path = os.path.join(evo_path, 'timestamps.npy')

            if os.path.exists(info_path) and os.path.exists(stats_path):
                with open(info_path, 'r') as info_file:
                    info = json.load(info_file)

                with open(stats_path, 'r') as stats_file:
                    stats = json.load(stats_file)

                no_timestamps = len(np.load(timestamps_path))

                # For ref_name and est_name remove the extension
                if not os.path.splitext((str(info.get('ref_name'))))[1]:
                    ref_name = info.get('ref_name')
                else:
                    ref_name = os.path.splitext((str(info.get('ref_name'))))[0]
                if not os.path.splitext((str(info.get('est_name'))))[1]:
                    est_name = info.get('est_name')
                else:
                    est_name = os.path.splitext((str(info.get('est_name'))))[0]

                entry = {
                    'sequence': os.path.relpath(sequence_path),
                    'title': info.get('label', ''),
                    'ref_name': ref_name,
                    'est_name': est_name,
                    'est_no_poses': no_timestamps,
                    'rmse': stats.get('rmse', ''),
                    'mean': stats.get('mean', ''),
                    'median': stats.get('median', ''),
                    'std': stats.get('std', ''),
                    'min': stats.get('min', ''),
                    'max': stats.get('max', ''),
                    'sse': stats.get('sse', '')
                }

                if evo_dir.startswith('evo_ape'):
                    ape_data.append(entry)
                elif evo_dir.startswith('evo_rpe'):
                    rpe_data.append(entry)

    return ape_data, rpe_data

def evo_map_to_pandas_df(data, precision = 4, basic_info=['ref_name', 'est_name'], metrics = ['est_no_poses', 'rmse', 'mean', 'median', 'std', 'min', 'max', 'sse']):
    """
    Creates a pandas DataFrame with the evo data provided. The format of the data is specific and produced by `parse_evo_json_files`.

    Parameters
    ----------
    data : list of dict
        List of dictionaries containing the evo data.
    precision : int
        Precision of the floating point numbers. (Default: 4, means 4 decimal places)
    basic_info : list of str
        Basic information to be exported.
        Default and available values:
        - 'title'
        - 'ref_name'
        - 'est_name'
        - 'est_no_poses'

    selected_metrics : list of str
        Metrics to be used.
        Default and available values:
        - 'rmse'
        - 'mean'
        - 'median'
        - 'std'
        - 'min'
        - 'max'
        - 'sse'

    Returns
    -------
    pandas.DataFrame
        A DataFrame containing the specified evo data.
    """

    # Input check
    for v in basic_info:
        if not v in ['title', 'ref_name', 'est_name', 'sequence']:
            raise ValueError("[evo_map_to_pandas_df]: Invalid input in basic_info: ", v)
    for metric in metrics:
        if not metric in ['est_no_poses', 'rmse', 'mean', 'median', 'std', 'min', 'max', 'sse']:
            raise ValueError(f"[evo_map_to_pandas_df] Invalid input metric: {metric}")

    rows = basic_info + metrics

    sequences = sorted([(d['sequence']) for d in data])

    for i in range(len(sequences)):
        for j in range(i+1, len(sequences)):
            if sequences[i] == sequences[j]:
                raise ValueError(f"[evo_map_to_pandas_df]: Duplicated sequence names found. {sequences[i]}")

    df_data = {}
    for sequence in sequences:
        df_data[sequence] = {}
        for row in rows:
            if row in metrics:
                if row == 'est_no_poses':
                    df_data[sequence][row] = "{}".format(
                        next((int(d[row]) for d in data if (d['sequence']) == sequence), 0))
                else:
                    df_data[sequence][row] = "{:.{}f}".format(
                        next((float(d[row]) for d in data if (d['sequence']) == sequence), 0),
                        precision)
            else:
                df_data[sequence][row] = next((d[row] for d in data if (d['sequence']) == sequence), '')

    # Calculate the mean for each row. Add extra column with avgs
    df_data['avg'] = {}
    for row in rows:
        if row in metrics:
            if row == 'est_no_poses':
                df_data['avg'][row] = "{}".format(
                    int(np.mean([int(df_data[sequence][row]) for sequence in df_data if sequence != 'avg'])))
            else:
                df_data['avg'][row] = "{:.{}f}".format(
                    np.mean([float(df_data[sequence][row]) for sequence in df_data if sequence != 'avg']),
                    precision)
        else:
            df_data['avg'][row] = ''

    df = pd.DataFrame(df_data)
    return df

def _evo_pandas_df_to_csv(ape_df, rpe_df, output_file):
    with open(output_file, 'w') as f:
        f.write('APE Metrics\n')
        ape_df.to_csv(f)
        f.write('RPE Metrics\n')
        rpe_df.to_csv(f)

def evo_to_csv(sequence_paths, output_file='evo_to_csv.csv', metrics = ['est_no_poses', 'rmse', 'mean', 'median', 'std', 'min', 'max', 'sse'], precision=4, verbose=False):
    """
    Export evo data from multiple sequences to a CSV file with all basic information and selected metrics.
    Args:
        sequence_paths: Paths to the sequences containing the evo data.
        output_file: Output file name. (Default: 'evo_to_csv.csv')
        metrics: Metrics to be exported. (Default: ['est_no_poses', 'rmse', 'mean', 'median', 'std', 'min', 'max', 'sse'])
        precision: Number of decimal places for the floating point numbers. (Default: 4)

    """
    if verbose:
        print("EVO to CSV Exporter\n")
        print(f"Sequence Paths: {sequence_paths}")
        print(f"Metrics: {metrics}")
    if not output_file.endswith('.csv'):
        output_file += '.csv'

    ape_data, rpe_data = parse_evo_json_files(sequence_paths)
    ape_df = evo_map_to_pandas_df(ape_data, metrics=metrics, precision=precision)
    rpe_df = evo_map_to_pandas_df(rpe_data, metrics=metrics, precision=precision)
    _evo_pandas_df_to_csv(ape_df, rpe_df, output_file)

def evo_to_csv_simplified(sequence_paths, output_file='evo_to_csv_simplified.csv', metrics=['est_no_poses', 'mean', 'rmse'], verbose=False):
    """
    Export evo data from multiple sequences to a CSV file in a simplified format.
    The simplified format contains only the basic metrics (est_no_poses, mean, rmse).
    Args:
        sequence_paths: Paths to the sequences containing the evo data.
        output_file: Output file name. (Default: 'evo_to_csv.csv')
        metrics: Metrics to be exported. (Default: ['est_no_poses', 'rmse', 'mean']

    """
    if verbose:
        print("EVO to CSV Exporter. Simplified\n")
        print(f"Sequence Paths: {sequence_paths}")
        print(f"Metrics: {metrics}")


    if not output_file.endswith('.csv'):
        output_file += '.csv'

    ape_data, rpe_data = parse_evo_json_files(sequence_paths)
    ape_df = evo_map_to_pandas_df(ape_data, basic_info=[], metrics=metrics)
    rpe_df = evo_map_to_pandas_df(rpe_data, basic_info=[], metrics=metrics)
    _evo_pandas_df_to_csv(ape_df, rpe_df, output_file)

def read_evo_csv(file_path):
    """
    Read an evo CSV file and return the data as a pandas DataFrame.
    Args:
        file_path: Path to the evo CSV file.
    Returns:
        Dict, Dict: APE and RPE data as dictionaries.
    """
    with open(file_path, 'r') as f:
        lines = f.readlines()
    ape_data = {}
    rpe_data = {}
    ape = False
    rpe = False
    sequences = []
    for line in lines:
        if 'APE Metrics' in line:
            ape = True
            rpe = False
            continue
        if 'RPE Metrics' in line:
            rpe = True
            ape = False
            continue

        line = line.strip().split(',')

        if line[0] == '':
            for i in range(1, len(line)):
                if not line[i] in sequences:
                    sequences.append(line[i])
            for sequence in sequences:
                if ape:
                    ape_data[sequence] = {}
                if rpe:
                    rpe_data[sequence] = {}
        else:
            if ape:
                for i in range(1, len(line)):
                    ape_data[sequences[i-1]][line[0]] = line[i]
            if rpe:
                for i in range(1, len(line)):
                    rpe_data[sequences[i-1]][line[0]] = line[i]

    return ape_data, rpe_data

def write_evo_to_csv(*dicts, output_file):
    """
    Convert multiple dictionaries to pandas DataFrames and write them to a CSV file.

    Parameters:
    -----------
    output_file : str
        The path to the output CSV file.
    *dicts : dict
        Dicts to write to output file
    """
    # Convert each dictionary to a pandas DataFrame
    dataframes = [pd.DataFrame(d) for d in dicts]

    # Use the _evo_pandas_df_to_csv function to write the DataFrames to the output file
    _evo_pandas_df_to_csv(*dataframes, output_file)

