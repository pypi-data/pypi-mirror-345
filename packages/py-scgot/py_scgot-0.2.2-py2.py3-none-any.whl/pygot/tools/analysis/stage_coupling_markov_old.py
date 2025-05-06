from tqdm import tqdm
from pygot.tools.traj import velocity_graph
from pygot.preprocessing import mutual_nearest_neighbors
import scanpy as sc
import numpy as np
import pandas as pd
from tqdm import tqdm
import scanpy as sc
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
import statsmodels.distributions.empirical_distribution as edf
from scipy.interpolate import interp1d

class TimeSeriesRoadmap:
    def __init__(self, adata, embedding_key, velocity_key, time_key):
        self.adata = adata
        self.embedding_key = embedding_key
        self.velocity_key = velocity_key
        self.time_key = time_key
        self.ts = np.sort(np.unique(adata.obs[time_key]))
        self.state_map = {t:{} for t in self.ts[:-1]}
        
    def compute_state_coupling(
        self,
        start = None,
        end = None,
        cell_type_key='cell_type',
        n_neighbors=None,
        permutation_iter_n=100,
        mutual=True,
    ):
        ad = self.adata
        
        if start is None or end is None:
            r = self.ts
        else:
            r = [start, end]
        ad.obs['idx'] = range(len(ad))
        for i in range(len(r) - 1):
            start = r[i]
            end = r[i+1]
            
            x0_obs = ad.obs.loc[ad.obs[self.time_key] == start]
            x1_obs = ad.obs.loc[ad.obs[self.time_key] == end]
            
            idx = pd.concat([x0_obs['idx'], x1_obs['idx']])
            embedding = ad.obsm[self.embedding_key][idx.tolist()]
            embedding_v = ad.obsm[self.velocity_key][idx.tolist()]
            x0x1_ad = sc.AnnData(obs=ad.obs.loc[idx.index])
            x0x1_ad.obsm[self.embedding_key] = embedding
            x0x1_ad.obsm[self.velocity_key] = embedding_v
            
            x0x1_ad = ad[np.concatenate([x0_obs.index, x1_obs.index])].copy()
            
            fwd, bwd, fbwd, null, descendant, ancestor, x0x1_markov, x1x0_markov = time_series_transition_map(
                x0x1_ad, 
                self.embedding_key, 
                self.velocity_key, 
                self.time_key, 
                start, end,
                norm=0, 
                n_neighbors=n_neighbors,
                cell_type_key=cell_type_key,
                permutation_iter_n=permutation_iter_n,
                mutual=mutual
            )
            self.state_map[start]['fwd'] = fwd
            self.state_map[start]['bwd'] = bwd
            self.state_map[start]['fbwd'] = fbwd
            self.state_map[start]['null'] = null
            self.state_map[start]['descendant'] = descendant
            self.state_map[start]['ancestor'] = ancestor
            self.state_map[start]['x0x1_markov'] = x0x1_markov
            self.state_map[start]['x1x0_markov'] = x1x0_markov
            
    def filter_state_coupling(
        self, 
        max_cutoff=0.5,
        pvalue=0.001
    ):
        filtered_fbwd_list = []
        for key in self.state_map.keys():
            cutoff = min(max_cutoff, get_cutoff(self.state_map[key]['null'], pvalue=pvalue))
            self.state_map[key]['cutoff'] = cutoff
            filtered_fbwd_list.append((self.state_map[key]['fbwd'] > cutoff) * self.state_map[key]['fbwd'])
            self.state_map[key]['filtered_fbwd'] = filtered_fbwd_list[-1]
        return filtered_fbwd_list


def get_cutoff(sample, pvalue=0.001):
    sample = sample[~np.isnan(sample)]
    sample_edf = edf.ECDF(sample)
    
    slope_changes = sorted(set(sample))
    
    sample_edf_values_at_slope_changes = [ sample_edf(item) for item in slope_changes]
    inverted_edf = interp1d(sample_edf_values_at_slope_changes, slope_changes)
    cutoff = inverted_edf(1-pvalue)
    return cutoff




def time_series_transition_map(
    x0x1_ad, 
    embedding_key, 
    velocity_key, 
    time_key, 
    current_stage, 
    next_stage, 
    cell_type_key = 'cell_type', 
    n_neighbors=None, 
    norm=0,
    permutation_iter_n = 100,
    return_cell_coupling = True,
    mutual=True,
):
    """
    Function to compute Markov transition maps between two stages of cells.

    Parameters:
        x0x1_ad: AnnData object containing the single-cell data.
        embedding_key: Key for the embedding used to compute neighbors.
        velocity_key: Key for the velocity data.
        time_key: Key for the time or stage information.
        current_stage: The stage corresponding to time_key for the initial state.
        next_stage: The stage corresponding to time_key for the final state.
        cell_type_key: Key for the cell type information (default is 'cell_type').
        n_neighbors: Number of neighbors to use for the neighborhood graph (default is 30).
        norm: Determines normalization direction (0 for column normalization, 1 for row normalization).
        permutation_iter_n: Number of permutations for significance testing (default is 10).

    Returns:
        state_coupling_fwd: Forward state coupling matrix.
        state_coupling_bwd: Backward state coupling matrix.
        state_coupling: Combined state coupling matrix.
        permutation_list: Flattened permutation coupling matrices.
    """
    # Add an index column
    x0x1_ad.obs['idx'] = range(len(x0x1_ad))

    if n_neighbors is None:
        n_neighbors = min(100, max(30, int(len(x0x1_ad) * 0.0025)))
        print('{} to {} | Number of neighbors: {}'.format(current_stage,  next_stage, n_neighbors))
    # Compute neighbors based on the embedding
    
    if len(x0x1_ad) < 8192: #scanpy exact nn cutoff
        #symetric graph
        #sc.pp.neighbors(x0x1_ad, n_neighbors=n_neighbors, use_rep=embedding_key)
        #graph = x0x1_ad.obsp['connectivities']
        graph = mutual_nearest_neighbors(x0x1_ad, n_neighbors=n_neighbors, use_rep=embedding_key, mutual=False, sym=True)
    else:
        #mutual nearest neighbors graph
        if mutual:
            graph = mutual_nearest_neighbors(x0x1_ad, n_neighbors=n_neighbors, use_rep=embedding_key, mutual=True, sym=False)
        else:
            graph = mutual_nearest_neighbors(x0x1_ad, n_neighbors=n_neighbors, use_rep=embedding_key, mutual=False, sym=True)
    
    # Compute the velocity graph
    velocity_graph(x0x1_ad, embedding_key, velocity_key, graph=graph, split_negative=True)

    # Get indices for the current and next stage cells
    x0_idx = x0x1_ad.obs.loc[x0x1_ad.obs[time_key] == current_stage, 'idx'].to_numpy()
    x1_idx = x0x1_ad.obs.loc[x0x1_ad.obs[time_key] == next_stage, 'idx'].to_numpy()
    
    x0x1_markov = x0x1_ad.uns['velocity_graph'][x0_idx][:, x1_idx]
    x1x0_markov = -x0x1_ad.uns['velocity_graph_neg'][x1_idx][:, x0_idx]

    def compute_state_coupling(x0x1_ad, x0_idx, x1_idx, cell_type_key, norm=0, individual=False):
        """
        Computes the forward and backward state coupling matrices.

        Parameters:
            x0x1_ad: AnnData object containing the single-cell data.
            x0_idx: Indices of the cells at the current stage.
            x1_idx: Indices of the cells at the next stage.
            cell_type_key: Key for the cell type information.
            norm: Determines normalization direction (0 for column normalization, 1 for row normalization).

        Returns:
            fwd: Forward state coupling matrix.
            bwd: Backward state coupling matrix.
            state_coupling: Combined state coupling matrix.
        """
        x0_obs = x0x1_ad.obs.iloc[x0_idx]
        x1_obs = x0x1_ad.obs.iloc[x1_idx]

        # Get unique cell types and their indices
        x0_cell_list = x0_obs[cell_type_key].unique()
        x0_cell_idx_list = [np.where(x0_obs[cell_type_key] == c)[0] for c in x0_cell_list]
        x0_cell_num_list = np.array([len(n) for n in x0_cell_idx_list])
        
        x1_cell_list = x1_obs[cell_type_key].unique()
        x1_cell_idx_list = [np.where(x1_obs[cell_type_key] == c)[0] for c in x1_cell_list]
        x1_cell_num_list = np.array([len(n) for n in x1_cell_idx_list])
        
        ancestor = np.stack([x1x0_markov[:,x0_cell_idx_list[j]].sum(axis=1).flatten() for j in range(len(x0_cell_list))]).T
        ancestor /= x0_cell_num_list
        
        descendant = np.stack([x0x1_markov[:, x1_cell_idx_list[j]].sum(axis=1).flatten() for j in range(len(x1_cell_list))]).T
        descendant /= x1_cell_num_list
        
        
        # Compute the forward state coupling matrix
        fwd = np.zeros((len(x0_cell_list), len(x1_cell_list)))
        for i in range(len(x0_cell_list)):
            fwd[i, :] = descendant[x0_cell_idx_list[i], :].sum(axis=0)
        fwd = fwd / fwd.sum(axis=1)[:, None]  # Normalize by rows
        fwd[np.isnan(fwd)] = 0.
        fwd += 1e-3
        
        # Compute the backward state coupling matrix 
        bwd = np.zeros((len(x0_cell_list), len(x1_cell_list)))
        for j in range(len(x1_cell_list)):
                bwd[:, j] = ancestor[x1_cell_idx_list[j], :].sum(axis=0) 
        bwd = bwd / bwd.sum(axis=0)  # Normalize by columns
        bwd[np.isnan(bwd)] = 0.
        bwd += 1e-3
        # Combine the forward and backward matrices
        state_coupling = fwd * bwd
        state_coupling = state_coupling / (state_coupling.sum(axis=0) if norm == 0 else state_coupling.sum(axis=1)[:, None])
        
        if individual:
            
            ancestor = ancestor / ancestor.sum(axis=1)
            descendant = descendant / descendant.sum(axis=1)
            
            ancestor = pd.DataFrame(ancestor, 
                                    columns=x0_cell_list,
                                    index=x1_obs.index)
            descendant = pd.DataFrame(descendant, 
                                    columns=x1_cell_list,
                                    index=x0_obs.index)
            return fwd, bwd, pd.DataFrame(state_coupling, index=x0_cell_list, columns=x1_cell_list), descendant, ancestor
        
        
        return fwd, bwd, pd.DataFrame(state_coupling, index=x0_cell_list, columns=x1_cell_list)

    # Make sure cell type is treated as a string
    x0x1_ad.obs[cell_type_key] = x0x1_ad.obs[cell_type_key].astype(str)
    
    # Calculate the forward and backward state couplings
    state_coupling_fwd, state_coupling_bwd, state_coupling, descendant, ancestor = compute_state_coupling(
        x0x1_ad, x0_idx, x1_idx, cell_type_key, norm, individual=True)

    # Perform permutation testing
    permutation_list = []
    for k in tqdm(range(permutation_iter_n)):
        permuted_idx = np.random.permutation(len(x0x1_ad))
        x0x1_ad.obs[cell_type_key + '_permu'] = (x0x1_ad.obs[cell_type_key].astype(str)).to_numpy()[permuted_idx]

        _, _, permu_state_coupling = compute_state_coupling(x0x1_ad, x0_idx, x1_idx, cell_type_key + '_permu', norm)
        permutation_list.append(permu_state_coupling.to_numpy().flatten())

    x0x1_markov = x0x1_markov / x0x1_markov.sum(axis=1)
    x1x0_markov = x1x0_markov / x1x0_markov.sum(axis=1)
    return state_coupling_fwd, state_coupling_bwd, state_coupling, np.concatenate(permutation_list, axis=0), \
            descendant, ancestor, x0x1_markov, x1x0_markov
    
    