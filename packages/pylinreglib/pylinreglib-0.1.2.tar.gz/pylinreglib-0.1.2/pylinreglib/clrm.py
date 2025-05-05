from typing import List, Tuple, Optional
import numpy as np
import pandas as pd
from scipy.stats import t
from .BaseLRM import BaseLRM
from .lrm import lrm

class clrm(BaseLRM):
    def __init__(self, data : pd.DataFrame, response_col : str | int, predictor_col : int | str, how : str = 'drop_category', base : str | int = None) -> None:
        data.columns = data.columns.str.strip().str.replace('"', '', regex=False)
        df_temp = data.copy()
        if isinstance(predictor_col, int) and isinstance(response_col, int):
            x = df_temp.iloc[:, predictor_col]
            y = df_temp.iloc[:, response_col]
        elif isinstance(predictor_col, str) and isinstance(response_col, str):
            x = df_temp.loc[:, predictor_col]
            y = df_temp.loc[:, response_col]
        elif not isinstance(response_col, (int, str)):
            raise ValueError("El parámetro response_col debe ser int o str")
        else:
            raise ValueError("Los parámetro predictor_cols  y response_col deben contener el mismo tipo de dato (int o str)")
        
        self.data = df_temp
        self.X = x
        self.y = y
        self.how = how
        self.base = base
        self.predictor_col = predictor_col
        dummies = pd.get_dummies(x)

        if how == 'drop_category':
            if base is None:
                col_to_drop = dummies.columns[0]
            else:
                if base not in dummies.columns:
                    raise ValueError(f"La categoría '{base}' no existe entre las columnas: {list(dummies.columns)}")
                col_to_drop = base

            dummies.drop(columns=col_to_drop, inplace=True)
            dummies.insert(0, 'Intercept', 1)

        elif how == 'no_intercept':
            self.intercept = None

        else:
            raise ValueError("El parámetro 'how' debe ser 'drop_category' o 'no_intercept'")

        self.X_matrix = dummies.astype(int).to_numpy()
        self.coefficients = self.beta_coefficients()
        if how != 'no_intercept':
            self.intercept = float(self.coefficients[0])
        self.residuals = self.y - self.predicted()
        self.dummy_columns = dummies.columns.tolist()

    def remove_anomalies(self, inplace: Optional[bool] = False, threshold: Optional[float] = 3.0) -> Optional["lrm"]:
        """
        Modifica el modelo excluyendo observaciones anómalas según:
        - |Residuales estandarizados| > 3
        - |Residuales studentizados| > 3
        - Puntos de balanceo (H_ii > 2p/n)
        - Observaciones influenciales (Distancia de Cook > 1)

        Args:
        inplace (bool): Si es True, modifica el modelo actual.
        threshold (Optional[float]): Umbral para definir outliers. Por defecto 3.0.

        Returns:
            Optional[lrm]: Nuevo modelo sin anomalías si inplace es False.
        Raises:
            ValueError: Si todas las observaciones son marcadas como anómalas.
        """
        n = len(self.y)
        mask = np.full(n, False)
        anomalous_indices = set(self.get_outliers_std(threshold))
        anomalous_indices.update(self.get_outliers_stud(threshold))
        anomalous_indices.update(self.get_leverage_points())
        anomalous_indices.update(self.get_influential_obs())
        for idx in anomalous_indices:
            mask[idx] = True
        if np.all(mask):
            raise ValueError("Todas las observaciones fueron marcadas como anómalas. No se puede ajustar un nuevo modelo")
        X_filtered = self.X.loc[~mask]
        y_filtered = self.y.loc[~mask]
        df_filtered = pd.concat([X_filtered.reset_index(drop=True), y_filtered.reset_index(drop=True)], axis=1)

        if inplace:
            self.__init__(df_filtered, response_col=self.y.name, predictor_col=self.predictor_col, how=self.how, base=self.base)
            return None

        return clrm(df_filtered, response_col=self.y.name, predictor_col=self.predictor_col, how=self.how, base=self.base)

    def _preprocess_X0(self, W_values: list | str) -> np.ndarray:
        """
        Convierte una o varias observaciones categóricas (W) en matriz de diseño X0,
        utilizando la misma codificación dummy que en el entrenamiento.

        Args:
            W_values (list | str): Uno o varios valores de la variable categórica.

        Returns:
            np.ndarray: Matriz X0 codificada correctamente.
        """
        if isinstance(W_values, str):
            W_values = [W_values]
        dummies_input = pd.get_dummies(pd.Series(W_values), dtype=int)
        for col in self.dummy_columns:
            if col not in dummies_input.columns:
                dummies_input[col] = 0

        # Ordenar las columnas según el modelo entrenado
        dummies_input = dummies_input[self.dummy_columns]

        # Si el modelo tiene intercepto, sobreescribe su valor a 1
        if self.intercept is not None and 'Intercept' in dummies_input.columns:
            dummies_input['Intercept'] = 1

        return dummies_input.to_numpy()
    
    def obs_confidence_intervals(self, X0: list | np.ndarray, alpha: float = 0.05) -> List[Tuple[float, float, float]]:
        """
        Calcula los intervalos de confianza para la media de respuesta.

        Args:
            X0 (list | np.ndarray): Observaciones nuevas.
            alpha (float): Nivel de significancia.

        Returns:
            List[Tuple[float, float, float]]: Intervalos (inferior, media, superior).
        """
        X0 = self._preprocess_X0(X0)
        n, p = self.X_matrix.shape
        t_crit = t.ppf(1 - alpha / 2, n - p)
        mse = self.MSE()
        c_matrix = np.linalg.inv(self.X_matrix.T @ self.X_matrix)
        Y0 = X0 @ self.coefficients

        intervals = []
        for i, vals in enumerate(X0):
            L = t_crit * np.sqrt(mse * vals.T @ c_matrix @ vals)
            lower = Y0[i] - L
            upper = Y0[i] + L
            intervals.append((float(lower), float(Y0[i]), float(upper)))

        return intervals

    def obs_prediction_intervals(self, X0: list | np.ndarray, alpha: float = 0.05) -> List[Tuple[float, float, float]]:
        """
        Calcula los intervalos de predicción para una nueva observación.

        Args:
            X0 (list | np.ndarray): Observaciones nuevas.
            alpha (float): Nivel de significancia.

        Returns:
            List[Tuple[float, float, float]]: Intervalos (inferior, media, superior).
        """
        X0 = self._preprocess_X0(X0)
        n, p = self.X_matrix.shape
        t_crit = t.ppf(1 - alpha / 2, n - p)
        mse = self.MSE()
        c_matrix = np.linalg.inv(self.X_matrix.T @ self.X_matrix)
        Y0 = X0 @ self.coefficients

        intervals = []
        for i, vals in enumerate(X0):
            L = t_crit * np.sqrt(mse * (1 + vals.T @ c_matrix @ vals))
            lower = Y0[i] - L
            upper = Y0[i] + L
            intervals.append((float(lower), float(Y0[i]), float(upper)))

        return intervals