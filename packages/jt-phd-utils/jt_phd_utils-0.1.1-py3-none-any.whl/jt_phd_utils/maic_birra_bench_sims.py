import json
from scipy.stats import rankdata
from typing import List, Dict, Any, Optional, Union, Tuple
import numpy as np
import pandas as pd
from pydantic import BaseModel

from dantArrays import DantArray, index_field
from maic import Maic
from maic.models import EntityListModel
from birra.birra import birra
from ma_utils.rank_array_adapter import convert_rank_data, RankShape


class RankListMetadata(BaseModel):
    """
    Metadata for a single list within a rank-oriented DantArray.

    Fields:
    -------
    name : str
        Name of the list. Computed if none provided.
    category : str
        Category or grouping tag for the list.
    ranked : bool
        Whether the list is ranked.
    description : str, optional
        Description of the list.
    unique_items : int
        Count of valid (non-null) items in the list slice.
    """

    name: str = index_field("list_")
    category: str = index_field("category_")
    ranked: bool = True


class RankListAdapter:
    """
    Adapter managing rank data (potentially using DantArray with RankListMetadata)
    and providing methods to run MAIC, BIRRA analyses based on the data's shape.

    Data is stored internally in the format specified by the input `shape`.
    Methods like `run_maic` and `run_birra` adapt their behavior based on this
    internal shape to prepare appropriate inputs.
    """

    def __init__(
        self,
        data: Union[np.ndarray, pd.DataFrame, DantArray],
        shape: RankShape,
        item_identifiers: Optional[List[Any]] = None,
        list_identifiers: Optional[List[Any]] = None,
        categories: Optional[List[str]] = None,
        list_names: Optional[List[str]] = None,
        ranked_list_flags: Optional[List[bool]] = None,
    ):
        """
        Initializes the adapter, storing data and metadata.

        Parameters:
        -----------
        data : np.ndarray, pd.DataFrame, or DantArray
            Input rank data. If ndarray/DataFrame, a DantArray is created.
        shape : RankShape
            The semantic shape of the input `data` (e.g., LISTCOL_ITEMROW).
        item_identifiers : list, optional
            Identifiers for the items (e.g., gene names). Relevant for ITEM* shapes
            if not providing a DataFrame where index/columns can be inferred.
            Length must match the item dimension based on `shape`.
        list_identifiers : list, optional
            Identifiers for the lists (e.g., study names). Relevant if not
            providing a DataFrame where index/columns can be inferred.
            Length must match the list dimension based on `shape`.
        categories : list of str, optional
            Category for each list. Length must match the list dimension.
        list_names : list of str, optional
            Explicit names for each list (overrides inferred/default list_identifiers
            for metadata 'name'). Length must match the list dimension.
        ranked_list_flags : list of bool, optional
            Indicates whether each list is ranked. Length must match the list dimension.
            Defaults to True for all lists if not provided.
        """
        self._internal_shape = RankShape(shape)  # Ensure it's Enum

        if isinstance(data, DantArray):
            # If DantArray is passed, assume it's already configured correctly.
            if (
                not isinstance(data, DantArray)
                or data.metadata_class != RankListMetadata
            ):
                raise ValueError("Provided DantArray must use RankListMetadata")
            self.dant_array = data
            # Extract data and attempt to set identifiers if not provided
            array_data = self.dant_array.data  # Ideally use a safe accessor
            self._item_identifiers = item_identifiers  # Allow override
            self._list_identifiers = list_identifiers
            self.major_axis = (
                self.dant_array.major_axis
            )  # Get axis from existing DantArray
            # TODO: Add logic to infer identifiers from DantArray if needed and not provided

        else:
            # Handle ndarray or DataFrame input
            inferred_item_ids = None
            inferred_list_ids = None

            if isinstance(data, pd.DataFrame):
                array_data = data.values.astype(
                    float
                )  # Ensure float for NaN potential
                # Infer identifiers based on shape
                if self._internal_shape == RankShape.LISTCOL_ITEMROW:
                    inferred_item_ids = data.index.tolist()
                    inferred_list_ids = data.columns.tolist()
                elif self._internal_shape == RankShape.LISTROW_ITEMCOL:
                    inferred_item_ids = data.columns.tolist()
                    inferred_list_ids = data.index.tolist()
                elif self._internal_shape == RankShape.LISTCOL_RANKROW:
                    inferred_list_ids = data.columns.tolist()
                    # Items defined by rank position, no direct ID inference from index
                elif self._internal_shape == RankShape.LISTROW_RANKCOL:
                    inferred_list_ids = data.index.tolist()
                    # Items defined by rank position, no direct ID inference from columns

            elif isinstance(data, np.ndarray):
                if data.ndim != 2:
                    raise ValueError("Input numpy array must be 2D")
                try:
                    array_data = data.astype(float)  # Ensure float
                except ValueError as e:
                    raise ValueError(
                        f"Could not convert numpy array to float: {e}"
                    )
            else:
                raise TypeError(
                    "Input data must be np.ndarray, pd.DataFrame, or DantArray"
                )

            # Determine major_axis, dimensions, and validate identifiers
            if self._internal_shape == RankShape.LISTCOL_ITEMROW:
                n_items, n_lists = array_data.shape
                item_dim_len, list_dim_len = n_items, n_lists
                self.major_axis = 1  # Lists are columns
            elif self._internal_shape == RankShape.LISTROW_ITEMCOL:
                n_lists, n_items = array_data.shape
                item_dim_len, list_dim_len = n_items, n_lists
                self.major_axis = 0  # Lists are rows
            elif self._internal_shape == RankShape.LISTCOL_RANKROW:
                # n_items determined by rank length (shape[0])
                n_lists = array_data.shape[1]
                item_dim_len = array_data.shape[0]
                list_dim_len = n_lists
                self.major_axis = 1
            elif self._internal_shape == RankShape.LISTROW_RANKCOL:
                # n_items determined by rank length (shape[1])
                n_lists = array_data.shape[0]
                item_dim_len = array_data.shape[1]
                list_dim_len = n_lists
                self.major_axis = 0
            else:
                raise ValueError(
                    f"Unhandled shape: {self._internal_shape}"
                )  # Should not happen

            self._item_identifiers = (
                item_identifiers
                if item_identifiers is not None
                else inferred_item_ids
            )
            self._list_identifiers = (
                list_identifiers
                if list_identifiers is not None
                else inferred_list_ids
            )

            if self._internal_shape in (
                RankShape.LISTCOL_ITEMROW,
                RankShape.LISTROW_ITEMCOL,
            ):
                if self._item_identifiers is None:
                    raise ValueError(
                        f"item_identifiers are required for shape {self._internal_shape} if not inferrable from DataFrame"
                    )
                if len(self._item_identifiers) != item_dim_len:
                    raise ValueError(
                        f"Length of item_identifiers ({len(self._item_identifiers)}) must match item dimension ({item_dim_len}) for shape {self._internal_shape}"
                    )

            if self._list_identifiers is None:
                self._list_identifiers = [
                    f"list_{i}" for i in range(list_dim_len)
                ]
                print(
                    f"Warning: Using default list identifiers: {self._list_identifiers[:5]}..."
                )
            elif len(self._list_identifiers) != list_dim_len:
                raise ValueError(
                    f"Length of list_identifiers ({len(self._list_identifiers)}) must match list dimension ({list_dim_len})"
                )

            self.dant_array = DantArray(
                array_data,
                metadata_class=RankListMetadata,
                major_axis=self.major_axis,
            )

        actual_n_lists = self.dant_array.shape[self.major_axis]

        effective_list_names = (
            list_names if list_names is not None else self._list_identifiers
        )
        if (
            effective_list_names is None
            or len(effective_list_names) != actual_n_lists
        ):
            raise ValueError(
                f"Mismatch or missing effective list names/identifiers for {actual_n_lists} lists."
            )

        if ranked_list_flags is None:
            ranked_list_flags = [True] * actual_n_lists
        elif len(ranked_list_flags) != actual_n_lists:
            raise ValueError(
                f"Length of ranked_list_flags ({len(ranked_list_flags)}) must match number of lists ({actual_n_lists})"
            )

        if categories is None:
            categories = [str(name) for name in effective_list_names]
            print(f"Warning: Using list identifiers as default categories.")
        elif len(categories) != actual_n_lists:
            raise ValueError(
                f"Length of categories ({len(categories)}) must match number of lists ({actual_n_lists})"
            )

        for i in range(actual_n_lists):
            meta_updates = {
                "name": str(effective_list_names[i]),
                "category": str(categories[i]),
                "ranked": ranked_list_flags[i],
            }
            self.dant_array.update_metadata(
                i, create_default=True, **meta_updates
            )

    def get_shape(self) -> Tuple[int, int]:
        """Return the shape of the underlying data array."""
        return self.dant_array.shape

    def run_maic(
        self,
        threshold: float = 0.01,
        max_iterations: int = 100,
        output_folder: Optional[str] = None,
        plot: bool = False,
    ) -> Dict[str, Any]:
        """Run MAIC analysis using the data in this adapter."""

        entity_list_models = []
        n_lists = self.dant_array.shape[self.major_axis]

        if self._internal_shape in (
            RankShape.LISTCOL_ITEMROW,
            RankShape.LISTROW_ITEMCOL,
        ):
            if self._item_identifiers is None:
                raise RuntimeError(
                    "Cannot run MAIC on ITEM* shape without item_identifiers."
                )

            for i in range(n_lists):
                list_slice_ranks = self.dant_array.get_slice(i)
                metadata = self.dant_array.get_metadata(i, create_default=True)
                if metadata is None:
                    raise RuntimeError(f"Metadata missing for list {i}")

                valid_mask = ~np.isnan(list_slice_ranks)
                item_indices = np.where(valid_mask)[0]

                if len(item_indices) == 0:
                    string_items = []
                else:
                    rank_itemidx_pairs = list(
                        zip(list_slice_ranks[valid_mask], item_indices)
                    )
                    rank_itemidx_pairs.sort(key=lambda x: x[0])
                    sorted_item_ids = [
                        self._item_identifiers[idx]
                        for _, idx in rank_itemidx_pairs
                    ]
                    string_items = [str(item_id) for item_id in sorted_item_ids]

                elm = EntityListModel(
                    name=metadata.name,
                    category=metadata.category,
                    ranked=metadata.ranked,
                    entities=string_items,
                )
                entity_list_models.append(elm)

        elif self._internal_shape in (
            RankShape.LISTROW_RANKCOL,
            RankShape.LISTCOL_RANKROW,
        ):
            # RANK* shapes: Cell values are item IDs
            for i in range(n_lists):
                list_slice_ids = self.dant_array.get_slice(i)
                metadata = self.dant_array.get_metadata(i, create_default=True)
                if metadata is None:
                    raise RuntimeError(f"Metadata missing for list {i}")

                valid_mask = ~np.isnan(list_slice_ids)
                numeric_item_ids = list_slice_ids[valid_mask]
                string_items = [
                    str(item_id) for item_id in numeric_item_ids
                ]  # MAIC needs strings

                elm = EntityListModel(
                    name=metadata.name,
                    category=metadata.category,
                    ranked=metadata.ranked,
                    entities=string_items,
                )
                entity_list_models.append(elm)
        else:
            raise RuntimeError(
                f"Internal shape {self._internal_shape} not handled in run_maic"
            )

        if not entity_list_models:
            print("Warning: No valid lists found to run MAIC.")
            return {}

        maic = Maic(
            modellist=entity_list_models,
            threshold=threshold,
            maxiterations=max_iterations,
        )

        if output_folder:
            maic.output_folder = output_folder
            if plot:
                maic.add_plotter()

        maic.run(dump_result=(output_folder is not None))

        results = maic.sorted_results
        return results

    def run_birra(
        self,
        prior: float = 0.05,
        n_bins: int = 50,
        n_iter: int = 10,
        return_all: bool = False,
        cor_stop: Optional[float] = 0.999,
        impute_method: Optional[str] = "random",
    ) -> Dict[str, Any]:
        """Run BIRRA analysis on the rank data."""

        target_shape = (
            RankShape.LISTCOL_ITEMROW
        )  # BIRRA expects items=rows, lists=cols, cells=ranks
        birra_input_numeric = None
        map_birra_idx_to_orig = (
            None  # Function to map birra index to original item ID
        )

        current_data = self.dant_array.data.copy()  # Operate on a copy

        if self._internal_shape == target_shape:
            # Data is already in the correct shape (LISTCOL_ITEMROW)
            if not np.issubdtype(current_data.dtype, np.number):
                raise ValueError(
                    "Input data for BIRRA must be numeric (LISTCOL_ITEMROW)"
                )
            birra_input_numeric = current_data.astype(float)

            if self._item_identifiers is None:
                raise RuntimeError(
                    "item_identifiers needed for mapping BIRRA results from LISTCOL_ITEMROW"
                )
            if len(self._item_identifiers) != birra_input_numeric.shape[0]:
                raise ValueError(
                    f"Mismatch between item_identifiers ({len(self._item_identifiers)}) and BIRRA input rows ({birra_input_numeric.shape[0]})"
                )
            map_birra_idx_to_orig = (
                lambda idx: self._item_identifiers[idx]
                if 0 <= idx < len(self._item_identifiers)
                else None
            )

        else:
            # Need to convert to target_shape
            if not np.issubdtype(current_data.dtype, np.number):
                raise ValueError(
                    f"Input data for shape {self._internal_shape} must be numeric to convert for BIRRA"
                )

            try:
                converted = convert_rank_data(
                    current_data,
                    from_shape=self._internal_shape,
                    to_shape=target_shape,
                    na_value=np.nan,
                )
                birra_input_numeric = converted.data
                adapter_id_map = converted.id_to_index_mapping
                if not adapter_id_map:
                    raise ValueError(
                        "convert_rank_data did not return id_to_index_mapping"
                    )

                index_to_numeric_id = {v: k for k, v in adapter_id_map.items()}

                # Define mapping function based on original shape
                if self._internal_shape in (
                    RankShape.LISTROW_RANKCOL,
                    RankShape.LISTCOL_RANKROW,
                ):
                    # Original item ID was the numeric value in the cell.
                    # adapter_id_map maps this numeric value -> birra_row_idx.
                    # index_to_numeric_id maps birra_row_idx -> numeric value (which is the identifier).
                    map_birra_idx_to_orig = lambda idx: index_to_numeric_id.get(
                        idx
                    )
                elif self._internal_shape == RankShape.LISTROW_ITEMCOL:
                    # Original items defined by self._item_identifiers at column index.
                    # convert_rank_data uses the *column index* as the numeric ID internally.
                    # adapter_id_map maps column_index -> birra_row_idx.
                    # index_to_numeric_id maps birra_row_idx -> column_index.
                    if self._item_identifiers is None:
                        raise RuntimeError(
                            "item_identifiers needed for mapping BIRRA results from LISTROW_ITEMCOL"
                        )

                    def get_orig_identifier(idx):
                        col_idx = index_to_numeric_id.get(idx)
                        if col_idx is not None:
                            try:
                                int_col_idx = int(col_idx)
                                if (
                                    0
                                    <= int_col_idx
                                    < len(self._item_identifiers)
                                ):
                                    return self._item_identifiers[int_col_idx]
                            except (ValueError, TypeError):
                                pass  # Handle non-integer indices if they somehow occur
                        return None

                    map_birra_idx_to_orig = get_orig_identifier
                else:
                    # Should not happen if first check passed
                    raise RuntimeError(
                        f"Unhandled shape {self._internal_shape} in BIRRA conversion mapping"
                    )

            except Exception as e:
                print(f"Error converting data to {target_shape} for BIRRA: {e}")
                raise

        if birra_input_numeric is None or map_birra_idx_to_orig is None:
            raise RuntimeError(
                "Failed to prepare input or mapping function for BIRRA"
            )

        # --- Run BIRRA ---
        try:
            birra_result = birra(
                data=birra_input_numeric,
                prior=prior,
                n_bins=n_bins,
                n_iter=n_iter,
                return_all=return_all,
                cor_stop=cor_stop,
                impute_method=impute_method,
            )
        except Exception as e:
            print(f"Error during BIRRA execution: {e}")
            raise

        # --- Process Results ---
        results = {}
        final_ranks = (
            birra_result if not return_all else birra_result.get("result")
        )
        if not isinstance(final_ranks, np.ndarray) or final_ranks.ndim != 1:
            raise ValueError("BIRRA returned invalid rank results.")
        if len(final_ranks) != birra_input_numeric.shape[0]:
            raise ValueError(
                f"BIRRA returned {len(final_ranks)} ranks, but expected {birra_input_numeric.shape[0]}"
            )

        rankings = []
        birra_idx_to_original_item_map = {}
        for birra_idx in range(len(final_ranks)):
            original_item = map_birra_idx_to_orig(birra_idx)

            if original_item is None:
                original_item = f"UnknownItem_BIRRAIDX_{birra_idx}"
                print(
                    f"Warning: Could not map BIRRA index {birra_idx} to original identifier."
                )

            birra_idx_to_original_item_map[birra_idx] = original_item
            rank_value = final_ranks[birra_idx]
            rankings.append((original_item, rank_value))

        rankings.sort(key=lambda x: x[1])

        if return_all:
            results = {
                "ranks": final_ranks,
                "sorted_items": rankings,
                "data": birra_result.get("data"),
                "bayes_factors": birra_result.get("BF"),
                "imputed_input": birra_result.get("imputed_input"),
                "item_mapping": birra_idx_to_original_item_map,
            }
        else:
            results = {
                "ranks": final_ranks,
                "sorted_items": rankings,
                "item_mapping": birra_idx_to_original_item_map,
            }

        return results

    def get_data_as_shape(self, shape: RankShape) -> np.ndarray:
        """
        Convert internal data and return it in the specified rank shape.

        Parameters:
        -----------
        shape : RankShape
            Desired output shape enum value.

        Returns:
        --------
        np.ndarray
            Data in the specified shape format.
        """
        if self._internal_shape == shape:
            return self.dant_array.data.copy()  # Use safe accessor if available
        else:
            # Ensure internal data is numeric before conversion if needed
            current_data = self.dant_array.data
            if not np.issubdtype(current_data.dtype, np.number):
                # This case needs careful handling - how do we get numeric data
                # if the internal storage isn't numeric? Maybe _prepare_numeric...
                # logic needs to be available separately?
                # For now, assume internal data IS numeric or convert_rank_data handles it.
                print(
                    f"Warning: Internal data type is {current_data.dtype}, attempting conversion."
                )
                try:
                    current_data = current_data.astype(float)
                except ValueError:
                    raise TypeError(
                        f"Cannot convert internal data of shape {self._internal_shape} to numeric for shape conversion."
                    )

            converted_adapter = convert_rank_data(
                current_data,
                from_shape=self._internal_shape,
                to_shape=shape,
                na_value=np.nan,  # Default NA value
            )
            return converted_adapter.data


def get_gene_labels(n_genes: int, genes_json_file_path: str) -> List[str]:
    """Get a sample of random gene names from a JSON file."""
    with open(genes_json_file_path, "r") as f:
        all_genes = json.load(f)

    # Ensure uniqueness and convert to list
    gene_pool = list(set(all_genes))
    return np.random.choice(gene_pool, size=n_genes, replace=False).tolist()


def generate_effect_df(
    gene_list: List[str], mu: float = 0, sigma: float = 1, noise: bool = False
) -> pd.DataFrame:
    """
    Generate effect sizes for genes using log-normal distribution and provide them in a ranked DataFrame.

    Args:
        gene_list: List of gene identifiers
        mu: Log-normal mu parameter
        sigma: Log-normal sigma parameter
        noise: If True, generate random effect sizes from normal distribution

    Returns:
        DataFrame with gene names, effect sizes, and true ranks.
        N.B.: Sorted by true rank, so *the indices of this df = true ranks*.
    """
    n_genes = len(gene_list)

    if noise:
        effect_size = np.random.normal(0, 1, size=n_genes)
    else:
        effect_size = np.random.lognormal(mu, sigma / 2, size=n_genes)

    df = pd.DataFrame({"gene": gene_list, "effect_size": effect_size})
    df["true_rank"] = rankdata(-df["effect_size"], method="average")

    df = df.sort_values(by="true_rank").reset_index(drop=True)

    return df


def study_rank(
    df: pd.DataFrame, n_studies: int, noise_sd: float = 1
) -> np.ndarray:
    """
    Create ranked matrices by adding noise to effect sizes.

    Args:
        df: DataFrame with genes and effect sizes
        n_studies: Number of study columns to generate
        noise_sd: Standard deviation of noise to add

    Returns:
        NumPy array of ranks with shape (n_genes, n_studies)
    """
    error_matrix = np.random.normal(0, noise_sd, size=(len(df), n_studies))
    measured_effects = error_matrix + df["effect_size"].values.reshape(-1, 1)

    ranked_effects = np.zeros_like(measured_effects)
    for i in range(n_studies):
        ranked_effects[:, i] = rankdata(-measured_effects[:, i])

    return ranked_effects


def mix_dfs(
    df1: pd.DataFrame, df2: pd.DataFrame, mix_ratio: float = 0.5
) -> pd.DataFrame:
    """
    Creates a new DataFrame with effect sizes mixed from two input DataFrames.

    Args:
        df1: First DataFrame (must have 'gene' and 'effect_size').
        df2: Second DataFrame (must have 'gene' and 'effect_size').
             Gene order must be identical to df1.
        mix_ratio: Probability of choosing effect size from df1.

    Returns:
        A new DataFrame with mixed effect sizes and recalculated true ranks.
        Gene order matches the input DataFrames.
    """
    if not df1["gene"].equals(df2["gene"]):
        raise ValueError("Gene order/content in df1 and df2 must be identical")

    n_genes = len(df1)
    selector = np.random.rand(n_genes) < mix_ratio

    mixed_effect_size = np.where(
        selector, df1["effect_size"], df2["effect_size"]
    )

    mixed_df = pd.DataFrame(
        {
            "gene": df1["gene"],  # Keep original gene order
            "effect_size": mixed_effect_size,
        }
    )
    mixed_df["true_rank"] = rankdata(-mixed_df["effect_size"], method="average")

    return mixed_df
