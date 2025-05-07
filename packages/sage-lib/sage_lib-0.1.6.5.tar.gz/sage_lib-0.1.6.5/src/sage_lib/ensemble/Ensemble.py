from __future__ import annotations
from typing import Dict, Optional, Sequence, Tuple

import numpy as np
from scipy.stats import entropy
from sklearn.cluster import KMeans
import unittest
import os
from sage_lib.partition.Partition import Partition 
import matplotlib.pyplot as plt
from sklearn.linear_model import Ridge

_EPS = 1e-12

class Ensemble:
    """
    Container for managing and comparing sets of vibrational‐mode ensembles,
    with utilities for Boltzmann weighting, information‐theoretic metrics,
    and weighted k‐means clustering.
    """

    def __init__(self) -> None:
        """
        Initialize an empty Ensemble container.
        """
        self.ensembles: List[str, np.ndarray] = []

    def add_ensemble(self, data: object) -> None:
        """
        Add a new ensemble to the container.

        Parameters
        ----------
        data : np.ndarray
            Array of vibrational data (e.g., frequencies or mode amplitudes).
        """
        self.ensembles.append(data) 

    def read_ensembles(self, ensembles_path: Optional[Dict[str, str]] = None) -> None:
        """
        Load ensemble data from disk for all registered file paths.

        Parameters
        ----------
        ensembles_path : Optional[Dict[str, str]]
            If provided, overrides `self.ensembles_path`. Keys are ensemble
            identifiers and values are file paths.

        Notes
        -----
        This method assumes each file at `file_path` can be read into a
        NumPy array via `np.loadtxt`. Adjust as needed for other formats.
        """
        PT = Partition()
        PT.read_files( file_location=ensembles_path, verbose=True, )
        self.add_ensemble( PT )

    @staticmethod
    def boltzmann_weights_raw(energies: Sequence[float], temperature: float) -> np.ndarray:
        """
        Compute unnormalized Boltzmann weights for a set of energies.

        Parameters
        ----------
        energies : Sequence[float]
            Energies (E_i) in the same units as k_B * T.
        temperature : float
            Absolute temperature (same units as energies / k_B).

        Returns
        -------
        np.ndarray
            Array of weights ∝ exp(–E_i / (k_B T)). Not normalized.
        """
        beta = 1.0 / (temperature + _EPS)
        exponent = -beta * np.array(energies, dtype=float)
        return np.exp(exponent)

    @staticmethod
    def shannon_conditional(mass: np.ndarray) -> float:
        """
        Compute the Shannon entropy of a non‐normalized distribution.

        H = –∑ p_i log p_i, where p_i = mass_i / ∑ mass_i.

        Parameters
        ----------
        mass : np.ndarray
            Array of nonnegative weights.

        Returns
        -------
        float
            Shannon entropy in nats.
        """
        total = mass.sum() + 1e-20
        p = mass / total
        p = np.clip(p, 1e-12, None)
        return entropy(p, base=np.e)

    @staticmethod
    def shared_new_abs(
        massA: np.ndarray, massB: np.ndarray
    ) -> Tuple[Tuple[float, float, float], Tuple[float, float]]:
        """
        Compute shared and unique mass fractions between two ensembles.

        The output is:
          – (shared_fraction, newA_fraction, newB_fraction)
          – (fraction_A_total, fraction_B_total)

        Parameters
        ----------
        massA : np.ndarray
            Weights for ensemble A.
        massB : np.ndarray
            Weights for ensemble B.

        Returns
        -------
        Tuple[Tuple[float, float, float], Tuple[float, float]]
        """
        W_A = massA.sum()
        W_B = massB.sum()
        W = W_A + W_B
        shared_raw = np.minimum(massA, massB).sum()
        newA_raw = W_A - shared_raw
        newB_raw = W_B - shared_raw
        return (shared_raw / W, newA_raw / W, newB_raw / W), (W_A / W, W_B / W)


    @staticmethod
    def jsd_abs(massA: np.ndarray, massB: np.ndarray) -> float:
        """
        Compute the attenuated Jensen–Shannon divergence between two mass distributions.

        JSD_abs = (W_A/W)*(W_B/W) * JSD(PA, PB)
        where PA and PB are normalized distributions.

        Parameters
        ----------
        massA : np.ndarray
            Weights for ensemble A.
        massB : np.ndarray
            Weights for ensemble B.

        Returns
        -------
        float
            Attenuated Jensen–Shannon divergence.
        """
        W_A = massA.sum()
        W_B = massB.sum()
        W = W_A + W_B

        PA = massA / (W_A + 1e-20)
        PB = massB / (W_B + 1e-20)
        M = 0.5 * (PA + PB)

        klA = np.sum(PA * np.log((PA + 1e-12) / (M + 1e-12)))
        klB = np.sum(PB * np.log((PB + 1e-12) / (M + 1e-12)))
        J = 0.5 * (klA + klB)

        return (W_A / W) * (W_B / W) * J


    def kmeans_weighted_abs(
        self,
        freqs_A: np.ndarray,
        freqs_B: np.ndarray,
        E_A: Sequence[float],
        E_B: Sequence[float],
        T: float,
        n_clusters: int = 50,
        random_state: int = 0,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Perform weighted k‐means clustering on two ensembles.

        Clusters are formed over the concatenated frequency arrays,
        with sample weights given by the unnormalized Boltzmann weights.

        Parameters
        ----------
        freqs_A : np.ndarray
            Feature matrix for ensemble A (shape: n_A × d).
        freqs_B : np.ndarray
            Feature matrix for ensemble B (shape: n_B × d).
        E_A : Sequence[float]
            Energy values for A (length n_A).
        E_B : Sequence[float]
            Energy values for B (length n_B).
        T : float
            Temperature for Boltzmann weighting.
        n_clusters : int, optional
            Number of clusters (default: 50).
        random_state : int, optional
            Random seed for reproducibility (default: 0).

        Returns
        -------
        Tuple[np.ndarray, np.ndarray]
            Arrays of cluster‐mass weights for A and B (each length n_clusters).
        """
        # Compute raw (unnormalized) Boltzmann weights
        energies = np.concatenate([E_A, E_B])
        weights = self.boltzmann_weights_raw(energies, T)
        wA, wB = weights[: len(E_A)], weights[len(E_A) :]

        # Stack feature vectors and weights
        X = np.vstack([freqs_A, freqs_B])
        sample_weights = np.concatenate([wA, wB])

        # Fit weighted k-means
        km = KMeans(
            n_clusters=n_clusters,
            random_state=random_state,
            n_init=5,
        )
        sample_weights = np.nan_to_num(sample_weights, nan=0.0)
        if np.sum(sample_weights) < 1e-8:
            sample_weights = np.ones_like(sample_weights)

        km.fit(X, sample_weight=sample_weights)
        labels = km.labels_

        # Separate labels and compute cluster masses
        LA = labels[: len(freqs_A)]
        LB = labels[len(freqs_A) :]
        massA = np.bincount(LA, weights=wA, minlength=n_clusters)
        massB = np.bincount(LB, weights=wB, minlength=n_clusters)

        return massA, massB

    def compare_ensembles_abs(self, 
        max_clusters:int=30, 
        cluster_model:str='minibatch-kmeans',
        print_results:bool=False,
        temperature_min:float=0, 
        temperature_max:float=.0356, 
        reference_potentials:dict=None,
        reference_state:str=None,
        save_figures:bool=False,
        save_data:bool=True,
        fig_dir:str='.',
        ):
        """
        Compare two ensembles (A and B) using absolute-energy weighting.

        This method computes metrics such as absolute entropy for each ensemble,
        the Jensen-Shannon divergence, shared information, and novelty metrics
        across a range of chemical potentials and temperatures. Results can be
        printed and plotted via dedicated plotting methods.

        Parameters
        ----------
        max_clusters : int, optional
            Maximum number of clusters for structure analysis (default: 30).
        cluster_model : str, optional
            Clustering algorithm to use (default: 'minibatch-kmeans').
        print_results : bool, optional
            If True, prints the final computed metrics (default: False).
        temperature_min : float, optional
            Minimum temperature for analysis in eV (default: 0.0).
        temperature_max : float, optional
            Maximum temperature for analysis in eV (default: 0.0256).

        Returns
        -------
        H_abs_A : float
            Absolute entropy of ensemble A at final temperature and chemical potential.
        H_abs_B : float
            Absolute entropy of ensemble B at final temperature and chemical potential.
        JSD_abs : float
            Jensen-Shannon divergence between the two ensembles.
        shared : float
            Shared information metric.
        newA : float
            Novelty metric for ensemble A.
        newB : float
            Novelty metric for ensemble B.
        """
        import copy

        PT_all = Partition()
        PT_all.containers = self.ensembles[0].containers + self.ensembles[1].containers

        structure_labels, cluster_counts, class_labels = PT_all.compute_structure_cluster_counts(
            max_clusters=10,
            cluster_model='minibatch-kmeans',
            save=False
        )

        counts_A = cluster_counts[:len(self.ensembles[0].containers)]
        E_A = [c.AtomPositionManager.E for c in self.ensembles[0].containers ] 
        counts_B = cluster_counts[len(self.ensembles[0].containers):]
        E_B = [c.AtomPositionManager.E for c in self.ensembles[1].containers ]

        M = 20
 
        newA_matrix = np.zeros( (M,M) ) 
        newB_matrix = np.zeros( (M,M) ) 

        temperature_array = np.linspace(temperature_min, temperature_max, num=M)
        mu_array = np.linspace(-2, -1, num=M)

        HabsA_matrix, HabsB_matrix = np.zeros( (M,M) ), np.zeros( (M,M) ) 
        Jabs_matrix, shared_matrix = np.zeros( (M,M) ), np.zeros( (M,M) ) 
        newA_matrix, newB_matrix = np.zeros( (M,M) ), np.zeros( (M,M) ) 

        for j, mu in enumerate(mu_array):
            reference_potentials_j = copy.deepcopy(reference_potentials)
            reference_potentials_j[reference_state] = reference_potentials[reference_state]+mu
            # reference_potentials ={'Cu':-14.916443703626898/4, 'O':(-9.87396191+0.096)/2+mu_o }
            Ef_A = Ef(self.ensembles[0].containers, reference_potentials=reference_potentials_j )
            Ef_B = Ef(self.ensembles[1].containers, reference_potentials=reference_potentials_j )

            Emin = np.min( [np.min(Ef_A), np.min(Ef_B)] )
            Ef_A = Ef_A - Emin
            Ef_B = Ef_B - Emin


            for i, temperature in enumerate(temperature_array):

                HabsA, HabsB, Jabs, shared, newA, newB = self.estimate_metrics(
                    freqs_A=counts_A, freqs_B=counts_B, 
                    energies_A=Ef_A, energies_B=Ef_B, 
                    temperature=temperature,
                    n_clusters=5)

                HabsA_matrix[i,j] = HabsA
                HabsB_matrix[i,j] = HabsB

                Jabs_matrix[i,j] = Jabs
                shared_matrix[i,j] = shared

                newA_matrix[i,j] = newA
                newB_matrix[i,j] = newB


        # Plot with new interface
        metrics = {
            'HabsA': HabsA_matrix,
            'HabsB': HabsB_matrix,
            'JSD': Jabs_matrix,
            'shared': shared_matrix,
            'newA': newA_matrix,
            'newB': newB_matrix
        }
        self._plot_metrics(
            temperatures=temperature_array,
            metrics=metrics,
            mu=mu_array[-1],
            save_figures=save_figures,
            fig_dir=fig_dir
        )

        matrix_dict = {
            'H_abs_A': HabsA_matrix,
            'H_abs_B': HabsB_matrix,
            'JSD_abs': Jabs_matrix,
            'Shared': shared_matrix,
            'Novelty_A': newA_matrix,
            'Novelty_B': newB_matrix
        }
        self._plot_heatmaps(
            matrix_dict=matrix_dict,
            temperatures=temperature_array,
            mu_values=mu_array,
            save_figures=save_figures,
            fig_dir=fig_dir
        )

        if save_data:
            np.savetxt("newA_matrix.dat", newA_matrix, fmt="%.2f", delimiter=" ")
            np.savetxt("newB_matrix.dat", newB_matrix, fmt="%.2f", delimiter=" ")
            np.savetxt("HabsA_matrix.dat", HabsA_matrix, fmt="%.2f", delimiter=" ")
            np.savetxt("HabsB_matrix.dat", HabsB_matrix, fmt="%.2f", delimiter=" ")
            np.savetxt("Jabs_matrix.dat", Jabs_matrix, fmt="%.2f", delimiter=" ")
            np.savetxt("shared_matrix.dat", shared_matrix, fmt="%.2f", delimiter=" ")
            np.savetxt("temperature_array.dat", temperature_array, fmt="%.2f", delimiter=" ")
            np.savetxt("mu_array.dat", mu_array, fmt="%.2f", delimiter=" ")

        if print_results:
            # Header
            header = (
                f"{'T':>7} | {'H_abs_A':>9} | {'H_abs_B':>9} | "
                f"{'JSD_abs':>8} | {'shared':>7} | {'newA':>7} | "
                f"{'newB':>7} "
            )
            print(header)
            print("-" * len(header))
            print(
                f"{temperature:7.4f} | "
                f"{HabsA:9.6f} | "
                f"{HabsB:9.6f} | "
                f"{Jabs:8.6f} | "
                f"{shared:7.4f} | "
                f"{newA:7.4f} | "
                f"{newB:7.4f} | "
            )

        return HabsA, HabsB, Jabs, shared, newA, newB

    def _plot_metrics(self,
                       temperatures: np.ndarray,
                       metrics: Dict[str, np.ndarray],
                       mu: float,
                       save_figures: bool = False,
                       fig_dir: str = 'figures') -> None:
        """
        Plot multiple metrics vs temperature for a given mu and optionally save.

        Parameters
        ----------
        temperatures : np.ndarray
            Array of temperature values (eV).
        metrics : Dict[str, np.ndarray]
            Dictionary where keys are metric names and values are 2D arrays
            of shape (n_temps, n_series).
        mu : float
            Chemical potential (eV).
        save_figures : bool, optional
            If True, saves figure as PNG in fig_dir.
        fig_dir : str, optional
            Directory where figures are saved.
        """
        # Define groups of metrics to plot together
        from matplotlib import cm

        groups = [
            ("primary", {
                'H_abs_A': metrics['HabsA'],
                'H_abs_B': metrics['HabsB'],
                'JSD_abs': metrics['JSD']
            }),
            ("novelty", {
                'Shared': metrics['shared'],
                'Novelty A': metrics['newA'],
                'Novelty B': metrics['newB']
            })
        ]

        for group_name, metric_dict in groups:
            fig, ax = plt.subplots(figsize=(10, 7))
            cmap = cm.viridis

            for idx, (label, data) in enumerate(metric_dict.items()):
                # Ensure data is 2D: (n_temps, n_series)
                arr = np.atleast_2d(data)
                colors = cmap(np.linspace(0, 1, arr.shape[1]))
                for i in range(arr.shape[1]):
                    color = colors[i]
                    series = arr[:, i]
                    # Choose marker by label
                    markers = {'H_abs_A':'o','H_abs_B':'s','JSD_abs':'D',
                               'Shared':'o','Novelty A':'s','Novelty B':'D'}
                    marker = markers.get(label, 'o')
                    # Only label first series to avoid duplicate legend entries
                    ax.plot(temperatures, series, color=color,marker=marker,
                            label=label if i == 0 else None)

            ax.set_title(f"Metrics ({group_name}) vs Temperature (mu={mu:.2f} eV)")
            ax.set_xlabel("Temperature (eV)")
            ax.set_ylabel("Value")
            ax.legend(ncol=2, loc='upper left')
            ax.grid(True)
            fig.tight_layout()
            if save_figures:
                fname = f"metrics_{group_name}_mu_{mu:.2f}.png"
                fig.savefig(os.path.join(fig_dir, fname), dpi=300)

            #plt.show()

    def _plot_heatmaps(self,
                       matrix_dict: Dict[str, np.ndarray],
                       temperatures: np.ndarray,
                       mu_values: np.ndarray,
                       save_figures: bool = False,
                       fig_dir: str = 'figures') -> None:
        """
        Plot heatmaps of multiple matrices over mu and temperature.

        Parameters
        ----------
        matrix_dict : Dict[str, np.ndarray]
            Keys are titles and values are 2D arrays (temps × mu).
        temperatures : np.ndarray
            Array of temperature values (eV).
        mu_values : np.ndarray
            Array of chemical potentials (eV).
        save_figures : bool, optional
            If True, saves figure as PNG in fig_dir.
        fig_dir : str, optional
            Directory where figures are saved.
        """
        for title, matrix in matrix_dict.items():
            fig, ax = plt.subplots(figsize=(6, 5))
            im = ax.imshow(matrix,
                           aspect='auto',
                           origin='lower',
                           extent=[mu_values[0], mu_values[-1],
                                   temperatures[0], temperatures[-1]])
            ax.set_title(f"{title} Heatmap")
            ax.set_xlabel("mu (eV)")
            ax.set_ylabel("Temperature (eV)")
            fig.colorbar(im, ax=ax)
            fig.tight_layout()
            if save_figures:
                fname = f"heatmap_{title.replace(' ', '_')}.png"
                fig.savefig(os.path.join(fig_dir, fname), dpi=300)

            #plt.show()

    def estimate_metrics(self, freqs_A, freqs_B, energies_A, energies_B,
            temperature=0.0256, n_clusters=100, random_state=None):
        massA, massB = self.kmeans_weighted_abs(freqs_A, freqs_B, energies_A, energies_B, temperature, n_clusters=n_clusters)

        HcondA = self.shannon_conditional(massA)
        HcondB = self.shannon_conditional(massB)
        (F_A, F_B) = (massA.sum()/(massA.sum()+massB.sum()),
                      massB.sum()/(massA.sum()+massB.sum()))
        HabsA = F_A * HcondA
        HabsB = F_B * HcondB

        (shared, newA, newB), _ = self.shared_new_abs(massA, massB)

        Jabs = self.jsd_abs(massA, massB)

        return HabsA, HabsB, Jabs, shared, newA, newB

class TestEnsembleMethods(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Generate small synthetic data for testing
        np.random.seed(42)
        cls.N = 100
        cls.K = 5
        cls.freqs_A = np.random.rand(cls.N, cls.K)
        cls.freqs_A /= cls.freqs_A.sum(axis=1, keepdims=True)
        cls.freqs_B = np.random.rand(cls.N, cls.K)
        cls.freqs_B /= cls.freqs_B.sum(axis=1, keepdims=True)
        cls.E_A = np.random.rand(cls.N) / 2.0
        cls.E_B = np.random.rand(cls.N) / 2.0 + 0.1
        cls.T = 0.1
        cls.ensemble = Ensemble()

    def test_boltzmann_weights_raw(self):
        # Simple energy array
        energies = [0.0, 1.0, 2.0]
        T = 1.0
        w = Ensemble.boltzmann_weights_raw(energies, T)
        # Weights should be exp(-E/T): [1, exp(-1), exp(-2)]
        expected = np.exp(-np.array(energies))
        np.testing.assert_allclose(w, expected)

    def test_shannon_conditional_uniform(self):
        # Uniform mass should give log(n)
        mass = np.ones(10)
        H = Ensemble.shannon_conditional(mass)
        self.assertAlmostEqual(H, np.log(10), places=6)

    def test_shared_new_abs_extremes(self):
        # Non-overlapping masses
        massA = np.array([1.0, 0.0])
        massB = np.array([0.0, 1.0])
        (shared, newA, newB), (fA, fB) = Ensemble.shared_new_abs(massA, massB)
        # shared=0, newA=fA, newB=fB
        self.assertEqual(shared, 0.0)
        self.assertEqual(newA, fA)
        self.assertEqual(newB, fB)

    def test_jsd_abs_symmetry(self):
        # JSD should be symmetric
        massA = np.array([0.5, 0.5])
        massB = np.array([0.2, 0.8])
        jsd1 = Ensemble.jsd_abs(massA, massB)
        jsd2 = Ensemble.jsd_abs(massB, massA)
        self.assertAlmostEqual(jsd1, jsd2, places=8)

    def test_kmeans_weighted_abs_basic(self):
        # Ensure output shapes and non-negative masses
        massA, massB = self.ensemble.kmeans_weighted_abs(
            self.freqs_A, self.freqs_B, self.E_A, self.E_B, self.T,
            n_clusters=10, random_state=0
        )
        # Check shape
        self.assertEqual(massA.shape, (10,))
        self.assertEqual(massB.shape, (10,))
        # Check non-negativity
        self.assertTrue(np.all(massA >= 0))
        self.assertTrue(np.all(massB >= 0))
        # Sum of masses should equal sum of weights
        total_weight = np.sum(
            Ensemble.boltzmann_weights_raw(
                np.concatenate([self.E_A, self.E_B]), self.T
            )
        )
        self.assertAlmostEqual(massA.sum() + massB.sum(), total_weight, places=6)

def Ef(structures, reference_potentials=None):
    partition = Partition()
    partition.containers = structures
    
    X = np.array([
        [
            np.count_nonzero(structure.AtomPositionManager.atomLabelsList == label)
            for label in partition.uniqueAtomLabels
        ]
        for structure in structures
        ])
    y = np.array([getattr(s.AtomPositionManager, 'E', 0.0) for s in structures])

    if reference_potentials is not None:
        # Subtract the sum of reference potentials from total energy
        chemical_potentials = np.array([reference_potentials.get(ual, 0) for ual in partition.uniqueAtomLabels])
        formation_energies = y - X.dot(chemical_potentials)
    else:
        model = Ridge(alpha=1e-5, fit_intercept=False)
        model.fit(X, y)
        chemical_potentials = model.coef_
        formation_energies = y - X.dot(chemical_potentials)

    return np.array(formation_energies) / np.sum(X, axis=1)

'''
ens = Ensemble()
pa = '/Users/dimitry/Documents/Data/CuO/structures/config_full_pareto.xyz'
pb = '/Users/dimitry/Documents/Data/CuO/structures/config_out2.xyz'
ens.read_ensembles(pa)
ens.read_ensembles(pb)
#HabsA, HabsB, Jabs, shared, newA, newB
ens.compare_ensembles_abs(reference_potentials = {'Cu':-14.916443703626898/4, 'O':(-9.87396191+0.096)/2 }, reference_state='O' )
'''
if __name__ == "__main__":
    unittest.main()
