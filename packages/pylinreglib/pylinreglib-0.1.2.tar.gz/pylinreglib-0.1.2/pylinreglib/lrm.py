from typing import List, Tuple, Optional
import numpy as np
import pandas as pd
from scipy.stats import f, t
import matplotlib.pyplot as plt
import seaborn as sns
from itertools import combinations
from warnings import warn
from .BaseLRM import BaseLRM

class lrm(BaseLRM):
    def __init__(self, data : pd.DataFrame, response_col : str | int, predictor_cols : Optional[List[int] | List[str] | int | str] = None) -> None:
        data.columns = data.columns.str.strip().str.replace('"', '', regex=False)
        df_temp = data.copy()
        if isinstance(predictor_cols, (int, str)):
            predictor_cols = [predictor_cols]
        if predictor_cols is None:
            if isinstance(response_col, int):
                predictor_cols = [i for i in range(df_temp.shape[1]) if i != response_col]
            elif isinstance(response_col, str):
                predictor_cols = [col for col in df_temp.columns if col != response_col]
        if all(isinstance(item, int) for item in predictor_cols) and isinstance(response_col, int):
            x = df_temp.iloc[:, predictor_cols]
            y = df_temp.iloc[:, response_col]
        elif all(isinstance(item, str) for item in predictor_cols) and isinstance(response_col, str):
            x = df_temp.loc[:, predictor_cols]
            y = df_temp.loc[:, response_col]
        elif not isinstance(response_col, (int, str)):
            raise ValueError("El parámetro response_col debe ser int o str")
        else:
            raise ValueError("Los parámetro predictor_cols  y response_col deben contener el mismo tipo de dato (int o str)")
        
        self.X = x
        self.y = y
        self.X_matrix = self.__get_X_matrix()
        self.coefficients = self.beta_coefficients()
        self.intercept = float(self.coefficients[0])
        self.residuals = self.y - self.predicted()
        self.standar = False

    def __get_X_matrix(self) -> np.ndarray:
        """
        Convierte el DataFrame en una matriz NumPy agregando una columna de unos a la izquierda,
        que representa el término independiente (bias/intercepto).

        Returns:
            np.ndarray: Matriz de diseño con columna de unos.
        """
        nrows = self.X.shape[0]
        matrix = self.X.to_numpy()
        ones = np.ones((nrows, 1))
        result = np.concatenate((ones, matrix), axis=1)
        return result
    
    def significance_test(self, alpha : float = 0.05) -> bool:
        """
        Realiza la prueba global de significancia del modelo de regresión lineal,
        comparando el estadístico F observado con el valor crítico de la distribución F.

        Args:
            alpha (float): Nivel de significancia (por defecto 0.05).

        Returns:
            bool: True si el modelo es estadísticamente significativo (rechaza H₀), False si no lo es.
        """
        n, k = self.X.shape
        p = k + 1
        return self.MSR()/self.MSE() > float(f.ppf(1 - alpha, k, n - p))
    
    def only_sig_vars(self, alpha: float = 0.05) -> Optional["lrm"]:
        """
        Devuelve un nuevo modelo de regresión lineal entrenado solo con las variables
        que tienen coeficientes significativamente diferentes de cero.

        Args:
            alpha (float): Nivel de significancia para la prueba (por defecto 0.05).

        Returns:
            lrm: Nuevo modelo ajustado solo con variables significativas.
        """
        significative_vars = [not b for b in self.coefficients_hipotesis_test(alpha = alpha)[1:]]
        if not any(significative_vars):
            raise ValueError("Ninguna variable fue significativa con el nivel de significancia especificado")
        filtered_X = self.X.iloc[:, significative_vars]
        df_new = pd.concat([self.y, filtered_X], axis=1)
        return lrm(df_new, self.y.name, filtered_X.columns.tolist())
    
    def standardize(self, inplace : Optional[bool] = False) -> Optional["lrm"]:
        """
        Estandariza la matriz de predicción X y el vector respuesta y, eliminando el intercepto.
        Esto permite comparar directamente los efectos parciales de las variables predictoras.

        Args:
            inplace (Optional[bool]): Si es True, estandariza y modifica el modelo actual.
                                    Si es False, retorna un nuevo modelo estandarizado.

        Returns:
            Optional[lrm]: Nuevo modelo estandarizado si inplace es False. None si inplace es True.
        """
        X_std = (self.X - self.X.mean(axis=0)) / self.X.std(axis=0)
        y_std = (self.y - self.y.mean()) / self.y.std()
        df_std = pd.concat([X_std, y_std], axis=1)
        predictor_cols = X_std.columns.tolist()
        response_col = y_std.name
        if inplace: # Sobrescribe el modelo actual
            self.X = X_std
            self.y = y_std
            self.X_matrix = self.X.to_numpy()
            self.coefficients = self.beta_coefficients()
            self.intercept = None
            self.residuals = self.y - self.predicted()
            self.standar = True
            return None
        else: # Retorna un nuevo modelo estandarizado
            model_std = lrm(df_std, response_col=response_col, predictor_cols=predictor_cols)
            model_std.X_matrix = model_std.X.to_numpy()
            model_std.coefficients = model_std.beta_coefficients()
            model_std.intercept = None
            model_std.residuals = model_std.y - model_std.predicted()
            model_std.standar = True
            return model_std
        
    def _preprocess_X0(self, X0: list | np.ndarray) -> np.ndarray:
        """
        Prepara la matriz X0 añadiendo el término de intercepto si es necesario.

        Args:
            X0 (list | np.ndarray): Observaciones nuevas.

        Returns:
            np.ndarray: X0 preparado con el término de intercepto.
        """
        X0 = np.array(X0)
        if X0.ndim == 1:
            X0 = X0.reshape(1, -1)

        if X0.shape[1] == self.coefficients.shape[0]:
            if not np.allclose(X0[:, 0], 1):
                raise ValueError("El primer valor de cada observación debe ser 1 para representar el intercepto.")
        elif X0.shape[1] == self.coefficients.shape[0] - 1:
            X0 = np.concatenate((np.ones((X0.shape[0], 1)), X0), axis=1)
        else:
            raise ValueError(f"Dimensión inválida para X0. Se esperaban {self.coefficients.shape[0] - 1} o {self.coefficients.shape[0]} columnas, se recibieron {X0.shape[1]}.")

        return X0
    
    def _safe_extrapolation(self, X0: list | np.ndarray) -> np.ndarray:
        c_matrix = np.linalg.inv(self.X_matrix.T @ self.X_matrix)
        for i, vals in enumerate(X0):
            if (vals @ c_matrix @ vals.T > np.max(np.diag(self.hat_matrix()))):
                warn(
                f"La observación #{i+1} está fuera de la región observada: supera max(H_ii)",
                category=UserWarning
            )
        return c_matrix

    def predict_obs(self, X0: list | np.ndarray) -> np.ndarray:
        """
        Calcula las predicciones de la media de Y para nuevas observaciones.

        Args:
            X0 (list | np.ndarray): Observaciones nuevas.

        Returns:
            np.ndarray: Predicciones puntuales.
        """
        X0 = self._preprocess_X0(X0)
        self._safe_extrapolation(X0)
        return X0 @ self.coefficients
    
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
        c_matrix = self._safe_extrapolation(X0)
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
        c_matrix = self._safe_extrapolation(X0)
        Y0 = X0 @ self.coefficients

        intervals = []
        for i, vals in enumerate(X0):
            L = t_crit * np.sqrt(mse * (1 + vals.T @ c_matrix @ vals))
            lower = Y0[i] - L
            upper = Y0[i] + L
            intervals.append((float(lower), float(Y0[i]), float(upper)))

        return intervals

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
        df_filtered = pd.concat([X_filtered, y_filtered], axis=1)
        predictor_cols = X_filtered.columns.tolist()
        response_col = y_filtered.name
        if inplace:
            self.__init__(df_filtered, response_col=response_col, predictor_cols=predictor_cols)
            return None
        return lrm(df_filtered, response_col=response_col, predictor_cols=predictor_cols)

    def plot_regression(self, axis_name : Optional[str] = "Z"):
        """
        Muestra un gráfico de regresión lineal. Si el modelo es simple, se usa un gráfico 2D.
        Si hay 2 predictores, se muestra en 3D. Esta función se adapta a modelos estandarizados y no estandarizados.
        """
        X = self.X.copy()
        y = self.y.copy()

        if X.shape[1] == 1:  # Regresión simple
            var = X.columns[0]
            if self.standar:
                formula = f"{axis_name} = {self.coefficients[0]:.4f}·{var}"
            else:
                formula = f"{axis_name} = {self.intercept:.4f} + {self.coefficients[1]:.4f}·{var}"

            plt.figure(figsize=(8, 5))
            sns.regplot(x=X[var], y=y, line_kws={"color": "red"}, scatter_kws={"color": "blue"}, ci=None)
            plt.title(f"Modelo de Regresión Lineal Simple: {axis_name} vs {var}")
            plt.xlabel(var)
            plt.ylabel(axis_name)
            plt.text(
                0.05, 0.95, formula,
                transform=plt.gca().transAxes,
                fontsize=12, color="black",
                verticalalignment='top'
            )
            plt.show()

        elif X.shape[1] == 2:  # Regresión múltiple en R³
            x1 = X.iloc[:, 0]
            x2 = X.iloc[:, 1]
            x1_range = np.linspace(x1.min(), x1.max(), 30)
            x2_range = np.linspace(x2.min(), x2.max(), 30)
            x1_grid, x2_grid = np.meshgrid(x1_range, x2_range)

            if self.standar:
                b1, b2 = list(self.coefficients)
                y_pred_grid = b1 * x1_grid + b2 * x2_grid
                formula = f"{axis_name} = {b1:.4f}·{X.columns[0]} + {b2:.4f}·{X.columns[1]}"
            else:
                b0, b1, b2 = list(self.coefficients)
                y_pred_grid = b0 + b1 * x1_grid + b2 * x2_grid
                formula = f"{axis_name} = {b0:.4f} + {b1:.4f}·{X.columns[0]} + {b2:.4f}·{X.columns[1]}"

            fig = plt.figure(figsize=(10, 6))
            ax = fig.add_subplot(111, projection='3d')
            ax.scatter(x1, x2, y, color='blue', label='Datos reales')
            ax.plot_surface(x1_grid, x2_grid, y_pred_grid, color='red', alpha=0.5)
            ax.set_xlabel(X.columns[0])
            ax.set_ylabel(X.columns[1])
            ax.set_zlabel(axis_name)
            plt.title("Modelo de Regresión Lineal Múltiple (R³)")
            ax.text2D(
                0.5, 0.90, formula,
                transform=ax.transAxes,
                fontsize=12,
                color="black",
                horizontalalignment='center',
                verticalalignment='top'
            )
            plt.show()

        else:
            print(f"El modelo tiene {X.shape[1]} predictores. Solo funciona para 1 o 2 predictores")

    def VIFs(self) -> np.ndarray:
        """
        Calcula los factores de inflación de la varianza (VIF) para cada predictor.

        Returns:
            np.ndarray: Un arreglo con los VIFs correspondientes a cada variable predictora.
        """
        return np.diag(np.linalg.inv(np.corrcoef(self.X, rowvar=False)))
    
    def condition_number(self) -> float:
        """
        Calcula el número de condición de la matriz XᵀX, utilizado para detectar posibles problemas
        de multicolinealidad en el modelo.

        Nota:
            Este cálculo solo debe realizarse sobre modelos estandarizados o con predictores escalados.
            Si no se estandariza, las diferencias de escala entre variables pueden producir falsos positivos.

        Returns:
            float: Número de condición. Valores mayores a 100 suelen indicar multicolinealidad severa.

        Raises:
            ValueError: Si el modelo no ha sido estandarizado previamente.
        """
        if self.standar:
            eigen_values = np.linalg.eigvals(self.X_matrix.T @ self.X_matrix)
            k = float(np.max(eigen_values) / np.min(eigen_values))
            return k
        else:
            raise ValueError("Solo usar con modelos estandarizados; de lo contrario, puede haber falsos positivos.")

    def detect_multicollinearity(self) -> bool:
        """
        Detecta la presencia de multicolinealidad en el modelo usando dos criterios:

        - Algún VIF > 5
        - Número de condición > 100 (solo si el modelo está estandarizado)

        Returns:
            bool: True si se detecta multicolinealidad, False en caso contrario.
        """
        if self.standar:
            return (self.condition_number() > 100) or (np.max(self.VIFs()) > 5)
        return np.max(self.VIFs()) > 5

    def R2_j(self) -> np.ndarray:
        """
        Calcula los coeficientes de determinación individuales (R²_j) de cada variable predictora
        cuando se regresa contra las demás.

        Returns:
            np.ndarray: Arreglo con los valores de R²_j para cada predictor.
        """
        r2_j = 1 - 1 / self.VIFs()
        return r2_j

    def all_reg_table(self) -> pd.DataFrame:
        """
        Genera una tabla con todas las combinaciones posibles de predictores y sus estadísticos.

        Para cada subconjunto posible de predictores, se entrena un nuevo modelo y se calculan:

        - R2_adj : Coeficiente de determinación ajustado
        - MSE    : Error cuadrático medio
        - PRESSp : Validación tipo leave-one-out
        - Cp     : Estadístico de Mallows

        Si el modelo está estandarizado, también lo estarán los nuevos modelos.

        Advertencia:
            Este método tiene complejidad exponencial O(2^k). No se recomienda para modelos con muchos predictores.

        Returns:
            pd.DataFrame: DataFrame con combinaciones de predictores y sus métricas, ordenado por R2 ajustado.
        """
        predictors = list(self.X.columns)
        if len(predictors) > 15:
            warn(
                f"El modelo contiene {len(predictors)} predictores: este método puede demorar significativamente "
                "debido a su complejidad O(2^k). Considera limitar el número de predictores.",
                RuntimeWarning
            )
        response = self.y.name
        data = pd.concat([self.X, self.y], axis=1)
        MSE_full = self.MSE()
        n, _ = self.X.shape
        results = []
        for k in range(1, len(predictors)):
            for subset in combinations(predictors, k):
                model = lrm(data, response_col=response, predictor_cols=list(subset))
                if self.standar:
                    model.standardize(inplace=True)
                Cp = (model.SSE() / MSE_full) - (n - 2 * (model.X.shape[1] + 1))
                results.append({
                    'predictors': subset,
                    'R2_adj': model.R2_adj(),
                    'MSE': model.MSE(),
                    'PRESSp' : model.PRESSp(),
                    'Cp' : Cp
                })
        Cp = (self.SSE() / MSE_full) - (n - 2 * (self.X.shape[1] + 1))
        results.append({
                    'predictors': tuple(predictors),
                    'R2_adj': self.R2_adj(),
                    'MSE': self.MSE(),
                    'PRESSp' : self.PRESSp(),
                    'Cp' : Cp
                })

        return pd.DataFrame(results).sort_values(by='R2_adj', ascending=False).reset_index(drop=True)
    
    def forward_selection(self, tol: float = 1e-2) -> pd.DataFrame:
        """
        Implementa el algoritmo de selección hacia adelante para elegir predictores.

        En cada iteración, se agrega la variable que más reduzca la SSE del modelo,
        partiendo desde el mejor modelo univariable (con menor MSE). El proceso continúa hasta que la mejora en SSE
        entre iteraciones sea menor que la tolerancia `tol`.

        Args:
            tol (float): Tolerancia mínima de mejora en SSE para continuar agregando variables. Default es 1e-2.

        Returns:
            pd.DataFrame: Tabla con la evolución del modelo, mostrando predictores usados y métricas en cada paso:
                        'step', 'predictors', 'SSE', 'MSE', 'R2_adj'
        """
        predictors_all = list(self.X.columns)
        response = self.y.name
        data = pd.concat([self.X, self.y], axis=1)

        selected = []
        remaining = predictors_all.copy()
        results = []
        step = 0
        prev_sse = np.inf
        MSE_full = self.MSE()
        n, _ = self.X.shape

        while len(remaining) > 0:
            step += 1
            best_candidate = None
            best_sse = np.inf
            best_model = None

            for candidate in remaining:
                trial = selected + [candidate]
                model = lrm(data, response_col=response, predictor_cols=trial)
                if self.standar:
                    model.standardize(inplace=True)
                sse = model.SSE()
                if sse < best_sse:
                    best_sse = sse
                    best_candidate = candidate
                    best_model = model
                    Cp = (best_model.SSE() / MSE_full) - (n - 2 * (best_model.X.shape[1] + 1))

            improvement = prev_sse - best_sse
            if improvement < tol:
                break

            selected.append(best_candidate)
            remaining.remove(best_candidate)
            prev_sse = best_sse

            results.append({
                'step': step,
                'predictors': tuple(selected),
                'MSE': best_model.MSE(),
                'R2_adj': best_model.R2_adj(),
                'PRESSp' : best_model.PRESSp(),
                'Cp' : Cp
            })

        return pd.DataFrame(results)

    def backward_elimination(self, tol: float = 1e-2) -> pd.DataFrame:
        """
        Implementa el algoritmo de eliminación hacia atrás (greedy backward elimination) para seleccionar predictores.

        En cada iteración, se elimina la variable cuya exclusión más reduzca la SSE del modelo.
        El proceso continúa hasta que la mejora en SSE entre iteraciones sea menor que la tolerancia `tol`.

        Args:
            tol (float): Tolerancia mínima de mejora en SSE para continuar eliminando variables. Default es 1e-2.

        Returns:
            pd.DataFrame: Tabla con la evolución del modelo, mostrando predictores usados y métricas en cada paso:
                        'step', 'predictors', 'MSE', 'R2_adj', 'PRESSp', 'Cp'
        """
        predictors_all = list(self.X.columns)
        response = self.y.name
        data = pd.concat([self.X, self.y], axis=1)

        selected = predictors_all.copy()
        results = []
        step = 0
        model_full = self
        prev_sse = model_full.SSE()
        MSE_full = model_full.MSE()
        n, _ = self.X.shape
        Cp = (model_full.SSE() / MSE_full) - (n - 2 * (model_full.X.shape[1] + 1))
        results.append({
            'step': step,
            'predictors': tuple(selected),
            'MSE': model_full.MSE(),
            'R2_adj': model_full.R2_adj(),
            'PRESSp': model_full.PRESSp(),
            'Cp': Cp
        })

        while len(selected) > 1:
            step += 1
            best_subset = None
            min_sse_increase = np.inf
            best_model = None

            for candidate in selected:
                trial = [v for v in selected if v != candidate]
                model = lrm(data, response_col=response, predictor_cols=trial)
                if self.standar:
                    model.standardize(inplace=True)
                sse = model.SSE()
                sse_increase = sse - prev_sse
                if sse_increase < min_sse_increase:
                    min_sse_increase = sse_increase
                    best_subset = trial
                    best_model = model
                    Cp = (model.SSE() / MSE_full) - (n - 2 * (model.X.shape[1] + 1))

            if min_sse_increase > tol:
                break

            selected = best_subset
            prev_sse = best_model.SSE()
            results.append({
                'step': step,
                'predictors': tuple(selected),
                'MSE': best_model.MSE(),
                'R2_adj': best_model.R2_adj(),
                'PRESSp': best_model.PRESSp(),
                'Cp': Cp
            })

        return pd.DataFrame(results)
    
    def stepwise_selection(self, tol_add: float = 1e-2, tol_remove: float = 1e-2) -> pd.DataFrame:
        """
        Implementa el algoritmo de selección Stepwise (adelante + atrás) para elegir predictores.

        En cada paso:
            - Se intenta agregar la variable que más reduzca el SSE (si mejora más que `tol_add`).
            - Luego se intenta eliminar alguna de las actuales si su salida aumenta el SSE menos que `tol_remove`.
            - Se evita entrar en ciclos de añadir/quitar las mismas variables.

        Args:
            tol_add (float): Tolerancia mínima de mejora en SSE para agregar una variable.
            tol_remove (float): Tolerancia máxima de aumento en SSE para eliminar una variable.

        Returns:
            pd.DataFrame: Tabla con la evolución del modelo: 'step', 'predictors', 'MSE', 'R2_adj', 'PRESSp', 'Cp'
        """
        predictors_all = list(self.X.columns)
        response = self.y.name
        data = pd.concat([self.X, self.y], axis=1)

        selected = []
        remaining = predictors_all.copy()
        history = []
        results = []
        step = 0
        MSE_full = self.MSE()
        n, _ = self.X.shape

        while True:
            step += 1
            improved = False
            current_model = lrm(data, response_col=response, predictor_cols=selected)
            if self.standar:
                current_model.standardize(inplace=True)
            prev_sse = current_model.SSE()

            # --- Forward Step ---
            best_candidate = None
            best_model_add = None
            best_sse_add = np.inf

            for candidate in remaining:
                trial = selected + [candidate]
                model = lrm(data, response_col=response, predictor_cols=trial)
                if self.standar:
                    model.standardize(inplace=True)
                sse = model.SSE()
                if sse < best_sse_add:
                    best_sse_add = sse
                    best_candidate = candidate
                    best_model_add = model

            improvement = prev_sse - best_sse_add
            if improvement > tol_add:
                selected.append(best_candidate)
                remaining.remove(best_candidate)
                current_model = best_model_add
                prev_sse = best_sse_add
                improved = True
                Cp = (current_model.SSE() / MSE_full) - (n - 2 * (current_model.X.shape[1] + 1))
                results.append({
                    'step': step,
                    'predictors': tuple(selected),
                    'MSE': current_model.MSE(),
                    'R2_adj': current_model.R2_adj(),
                    'PRESSp': current_model.PRESSp(),
                    'Cp': Cp
                })
                history.append(('add', best_candidate))

            # --- Backward Step ---
            worst_candidate = None
            best_model_remove = None
            min_sse_increase = np.inf

            for candidate in selected:
                trial = [v for v in selected if v != candidate]
                model = lrm(data, response_col=response, predictor_cols=trial)
                if self.standar:
                    model.standardize(inplace=True)
                sse = model.SSE()
                sse_increase = sse - prev_sse
                if sse_increase < min_sse_increase:
                    min_sse_increase = sse_increase
                    worst_candidate = candidate
                    best_model_remove = model

            if min_sse_increase < tol_remove:
                if history and history[-1] == ('add', worst_candidate):
                    # Evita ciclo agregar/quitar misma variable
                    pass
                else:
                    selected.remove(worst_candidate)
                    remaining.append(worst_candidate)
                    current_model = best_model_remove
                    improved = True
                    Cp = (current_model.SSE() / MSE_full) - (n - 2 * (current_model.X.shape[1] + 1))
                    results.append({
                        'step': step + 0.5,  # indica que es una eliminación
                        'predictors': tuple(selected),
                        'MSE': current_model.MSE(),
                        'R2_adj': current_model.R2_adj(),
                        'PRESSp': current_model.PRESSp(),
                        'Cp': Cp
                    })
                    history.append(('remove', worst_candidate))

            if not improved:
                break

        return pd.DataFrame(results)