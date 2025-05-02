import numpy as np
import pandas as pd
from rdkit import Chem, DataStructs
from rdkit.Chem import AllChem
from rdkit.Chem import PandasTools
import scipy.spatial.distance as ssd
from scipy.cluster import hierarchy

class MolecularFingerprint:
    def __init__(self, array):
        self.array = array

    def __str__(self):
        return self.array.__str__()

def compute_fingerprint(molecule, radius=2, nBits=2048):
    """Return an RDKit Morgan fingerprint as a numpy array wrapped in MolecularFingerprint."""
    fp = AllChem.GetMorganFingerprintAsBitVect(molecule, radius, nBits=nBits)
    arr = np.zeros((nBits,), dtype=np.int8)
    DataStructs.ConvertToNumpyArray(fp, arr)
    return MolecularFingerprint(arr)

def tanimoto_distances_yield(fps):
    """Yield row-by-row 1–TanimotoDistance lists for a list of RDKit ExplicitBitVect."""
    for i in range(1, len(fps)):
        sims = DataStructs.BulkTanimotoSimilarity(fps[i], fps[:i])
        yield [1.0 - x for x in sims]

def butina_cluster(fps, cutoff=0.56):
    """Butina clustering on a list of RDKit ExplicitBitVect fingerprints."""
    n = len(fps)
    # build neighbor lists
    nbrs = [[] for _ in range(n)]
    gen = tanimoto_distances_yield(fps)
    for i in range(1, n):
        dists = next(gen)
        for j, dij in enumerate(dists):
            if dij <= cutoff:
                nbrs[i].append(j)
                nbrs[j].append(i)

    # sort by neighbor count
    order = sorted([(len(nei), idx) for idx, nei in enumerate(nbrs)], reverse=True)
    clusters = []
    seen = [False]*n

    for _, idx in order:
        if seen[idx]:
            continue
        tovisit = [idx]
        seen[idx] = True
        for other in nbrs[idx]:
            if not seen[other]:
                seen[other] = True
                tovisit.append(other)
        clusters.append(tuple(tovisit))

    return tuple(clusters)

def hierarchal_cluster(fps, avg_cluster_size=8):
    """Agglomerative clustering based on average linkage and Tanimoto distance."""
    n = len(fps)
    # build full distance matrix
    dists = []
    for i in range(n):
        sims = DataStructs.BulkTanimotoSimilarity(fps[i], fps)
        dists.append([1.0 - x for x in sims])
    dist_array = ssd.squareform(dists)
    Z = hierarchy.linkage(dist_array, method='average')
    n_clusters = max(1, int(n/avg_cluster_size))
    labels = hierarchy.cut_tree(Z, n_clusters=n_clusters).flatten()

    clusters = [[] for _ in range(labels.max()+1)]
    for idx, lab in enumerate(labels):
        clusters[lab].append(idx)
    return [tuple(c) for c in clusters]

def cluster_fingerprints(fps, method="auto"):
    """Wrapper: choose Butina or Hierarchical based on size or explicit choice."""
    n = len(fps)
    if method == "auto":
        method = "tb" if n >= 10000 else "hierarchy"
    if method == "tb":
        return butina_cluster(fps)
    else:
        return hierarchal_cluster(fps)

def realistic_split(df, smiles_col_index, frac_train, split_for_exact_frac=True, cluster_method="auto"):
    """
    Add a 'group' column with 'training'/'testing' based on clustering.
    Returns a new DataFrame with columns: original + 'group'.
    """
    # add RDKit molecule column
    smi_col = df.columns[smiles_col_index]
    PandasTools.AddMoleculeColumnToFrame(df, smi_col, "Mol", includeFingerprints=False)
    df = df[df["Mol"].notna()].copy()

    # compute fingerprints
    rdkit_fps = []
    for mol in df["Mol"]:
        fp = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=2048)
        rdkit_fps.append(fp)

    clusters = cluster_fingerprints(rdkit_fps, method=cluster_method)

    # assign clusters back to rows
    df["_cluster_id"] = -1
    for cid, members in enumerate(clusters):
        for idx in members:
            df.iat[idx, df.columns.get_loc("_cluster_id")] = cid

    # sort by cluster, then split by fraction
    df.sort_values("_cluster_id", inplace=True)
    n = len(df)
    cutoff = int(np.ceil(n * frac_train))
    df["group"] = ["training"]*n
    if split_for_exact_frac:
        df.iloc[cutoff:, df.columns.get_loc("group")] = "testing"
    else:
        # assign entire clusters to training until we exceed cutoff
        acc = 0
        for cid in sorted(df["_cluster_id"].unique()):
            members = df["_cluster_id"]==cid
            size = members.sum()
            if acc + size <= cutoff:
                df.loc[members, "group"] = "training"
                acc += size
            else:
                df.loc[members, "group"] = "testing"

    df.drop(columns=["Mol","_cluster_id"], inplace=True)
    return df

def split_df_into_train_and_test_sets(df):
    """Split a DataFrame with a 'group' column into (train_df, test_df)."""
    return df[df["group"]=="training"].copy(), df[df["group"]=="testing"].copy()
