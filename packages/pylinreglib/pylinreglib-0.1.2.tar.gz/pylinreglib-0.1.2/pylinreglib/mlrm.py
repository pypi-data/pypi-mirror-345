from typing import List, Optional
import numpy as np
import pandas as pd
from .BaseLRM import BaseLRM
from .lrm import lrm

class mlrm(BaseLRM):
    def __init__(self, data : pd.DataFrame, response_col : str | int, cat_col: int | str, predictor_cols : Optional[List[int] | List[str] | int | str] = None, base : str | int = None, interaction : bool = False) -> None:
        data.columns = data.columns.str.strip().str.replace('"', '', regex=False)
        df_temp = data.copy()

        if isinstance(predictor_cols, (int, str)):
            predictor_cols = [predictor_cols]
        if predictor_cols is None:
            if isinstance(response_col, int):
                predictor_cols = [i for i in range(df_temp.shape[1]) if i != response_col and i != cat_col]
            elif isinstance(response_col, str):
                predictor_cols = [col for col in df_temp.columns if col != response_col and col != cat_col]

        if all(isinstance(item, int) for item in predictor_cols) and isinstance(response_col, int) and isinstance(cat_col, int):
            X = df_temp.iloc[:, predictor_cols]
            y = df_temp.iloc[:, response_col]
        elif all(isinstance(item, str) for item in predictor_cols) and isinstance(response_col, str) and isinstance(cat_col, str):
            X = df_temp.loc[:, predictor_cols]
            y = df_temp.loc[:, response_col]
        else:
            raise ValueError("Los parámetros predictor_cols, cat_col y response_col deben contener el mismo tipo de dato (int o str)")
        
        cat_data = df_temp.iloc[:, cat_col] if isinstance(cat_col, int) else df_temp.loc[:, cat_col]
        dummies = pd.get_dummies(cat_data)
        col_to_drop = base if base is not None else dummies.columns[0]
        if col_to_drop not in dummies.columns:
            raise ValueError(f"La categoría '{base}' no existe entre las columnas: {list(dummies.columns)}")
        dummies.drop(columns=col_to_drop, inplace=True)

        if interaction:
            interactions = pd.DataFrame(index=X.index)
            for col in X.columns:
                for cat_col_name in dummies.columns:
                    inter_col_name = f"{col}*{cat_col_name}"
                    interactions[inter_col_name] = X[col] * dummies[cat_col_name]
            X = pd.concat([X, dummies, interactions], axis=1)
        else:
            X = pd.concat([X, dummies], axis=1)

        self.data = df_temp
        self.X = X
        self.y = y
        self.X_matrix = self.__get_X_matrix()
        self.coefficients = self.beta_coefficients()
        self.intercept = float(self.coefficients[0])
        self.residuals = self.y - self.predicted()
        self.base = col_to_drop
        self.interaction = interaction
        self.categories = dummies.columns.tolist()
        self.cat_col = cat_col
        self.predictor_cols = predictor_cols

    def get_coef_df(self) -> pd.DataFrame:
        """
        Retorna un DataFrame con los coeficientes del modelo.

        Returns:
            pd.DataFrame: columnas 'Columna' y 'Beta', incluyendo el intercepto.
        """
        col_names = ["Intercepto"] + list(self.X.columns)
        valores = list(self.coefficients)
        return pd.DataFrame({"Variable": col_names, "Beta": valores})
    
    def models_by_category(self) -> dict:
        """
        Genera un modelo `lrm` por cada categoría de la variable categórica.

        Returns:
            dict: Diccionario {categoria: lrm instance} para cada valor de la variable categórica.
        """
        if isinstance(self.cat_col, int):
            cat_col = self.data.columns[self.cat_col]
        else:
            cat_col = self.cat_col

        models = {}
        categories = self.categories + [self.base]
        for cat in categories:
            filtered = self.data[self.data[cat_col] == cat]
            models[cat] = lrm(filtered.reset_index(drop = True), self.y.name, self.predictor_cols)
        return models
    
    def __get_X_matrix(self) -> np.ndarray:
        """
        Convierte el DataFrame en una matriz NumPy agregando una columna de unos a la izquierda,
        que representa el término independiente (bias/intercepto).

        Returns:
            np.ndarray: Matriz de diseño con columna de unos.
        """
        nrows = self.X.shape[0]
        matrix = self.X.to_numpy().astype(float)
        ones = np.ones((nrows, 1))
        result = np.concatenate((ones, matrix), axis=1)
        return result