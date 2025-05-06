from sklearn.decomposition import PCA
import pandas as pd
from .general import apply_pca

class SubPCAByTaxonomy:
    """
    Performs sub-PCA on OTU features grouped by taxonomy level.

    Supports separate fit (on train) and transform (on test),
    while maintaining consistent feature space between them.
    """

    def __init__(self, level):
        self.level = level
        self.group_pcas = {}        # Mapping from taxonomy group to PCA model
        self.dict_bact = {}         # Mapping from group to list of features
        self.constant_cols = []     # Columns with constant value (same across all samples)
        self.train_columns = None   # Final column order (for aligning test)
        self.train_index = None

    def _build_taxonomy_groups(self, df):
        self.dict_bact = {'else': []}
        for col in df.columns:
            col_name = col.split(';')
            bact_level = self.level - 1
            if col_name[0][-1] == '_':
                continue
            if len(col_name) > bact_level:
                while col_name[bact_level][-1] == "_" and bact_level > 0:
                    bact_level -= 1
                key = ';'.join(col_name[:bact_level+1])
            else:
                key = 'else'
            self.dict_bact.setdefault(key, []).append(col)

    def fit(self, df_train):
        self.train_index = df_train.index
        self._build_taxonomy_groups(df_train)

        new_df = pd.DataFrame(index=self.train_index)
        col_counter = 0

        for key, values in self.dict_bact.items():
            new_data = df_train[values]

            # Handle constant-value columns
            if new_data.nunique(axis=0).eq(1).all():
                self.constant_cols.extend(values)
                continue

            # Fit PCA on group
            pca = PCA(n_components=min(round(new_data.shape[1] / 2) + 1, new_data.shape[0]))
            pca.fit(new_data)

            # Determine number of components to explain >50% variance
            explained = pca.explained_variance_ratio_
            sum_var = 0
            num_comp = 0
            for i, var in enumerate(explained):
                if sum_var <= 0.5:
                    sum_var += var
                else:
                    num_comp = i
                    break
            if num_comp == 0:
                num_comp = 1

            # Re-fit PCA with final number of components
            new_data_transformed, pca_obj = apply_pca(new_data, n_components=num_comp)
            self.group_pcas[key] = pca_obj

            # Add components to dataframe
            for j in range(new_data_transformed.shape[1]):
                col_name = 'else;' if key == 'else' else f"{values[0][0:values[0].find(key)+len(key)]}_{j}"
                new_df[col_name] = new_data_transformed[j]
            col_counter += num_comp

        # Add constant columns back
        if self.constant_cols:
            new_df = pd.concat([new_df, df_train[self.constant_cols]], axis=1)

        self.train_columns = new_df.columns
        return new_df

    def transform(self, df_test):
        new_df = pd.DataFrame(index=df_test.index)

        for key, values in self.dict_bact.items():
            if key not in self.group_pcas:
                continue  # No PCA was fitted for this group

            # Keep only columns from 'values' that actually exist in df_test
            existing_cols = [col for col in values if col in df_test.columns]
            if not existing_cols:
                continue  # Skip if no columns available

            test_group = df_test[existing_cols]
            test_pca = self.group_pcas[key]
            transformed = test_pca.transform(test_group)
            transformed = pd.DataFrame(transformed, index=df_test.index)

            for j in range(transformed.shape[1]):
                col_name = 'else;' if key == 'else' else f"{existing_cols[0][0:existing_cols[0].find(key) + len(key)]}_{j}"
                new_df[col_name] = transformed.iloc[:, j]

        # Add constant columns
        if self.constant_cols:
            const_existing = [col for col in self.constant_cols if col in df_test.columns]
            new_df = pd.concat([new_df, df_test[const_existing]], axis=1)

        # Align with training columns
        new_df = new_df.reindex(columns=self.train_columns, fill_value=0)
        return new_df