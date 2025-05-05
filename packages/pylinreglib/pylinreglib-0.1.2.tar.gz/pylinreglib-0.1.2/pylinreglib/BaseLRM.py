from abc import ABC
import numpy as np
import pandas as pd
from scipy.stats import t, shapiro
import matplotlib.pyplot as plt
import seaborn as sns
from warnings import warn
from typing import List, Tuple, Optional

class BaseLRM(ABC):
    """
    Clase base para modelos de regresión lineal. No debe ser instanciada directamente.
    """
    def beta_coefficients(self) -> np.ndarray:
        """
        Calcula los coeficientes beta utilizando la fórmula cerrada de mínimos cuadrados ordinarios:
        (XᵀX)⁻¹ Xᵀy

        Returns:
            np.ndarray: Vector de coeficientes estimados.
        """
        X = self.X_matrix
        y = self.y
        return np.linalg.inv(X.T @ X) @ X.T @ y
    
    def predicted(self) -> np.ndarray:
        """
        Calcula las respuestas estimadas (ŷ) usando los coeficientes beta.

        Returns:
            np.ndarray: Vector de valores estimados de y (ŷ).
        """
        return self.X_matrix @ self.coefficients
    
    def SSE(self) -> float:
        """
        Calcula la Suma de los Errores al Cuadrado (SSE - Sum of Squared Errors),
        que representa la variabilidad no explicada por el modelo.

        Returns:
            float: Valor de la SSE.
        """
        return float(np.sum(self.residuals ** 2))
    
    def var(self) -> float:
        """
        Calcula la varianza del error (error cuadrático medio - MSE),
        utilizando la suma de errores al cuadrado (SSE).

        Returns:
            float: Estimación de la varianza del error.
        """
        n, p = self.X_matrix.shape
        return self.SSE() / (n - p)
    
    def MSE(self) -> float:
        """
        Retorna el error cuadrático medio (MSE), equivalente a la varianza del error.

        Returns:
            float: Error cuadrático medio.
        """
        return self.var()

    def SSR(self) -> float:
        """
        Calcula la Suma de los Cuadrados de la Regresión (SSR), que representa
        la variabilidad explicada por el modelo.

        Returns:
            float: Valor de la SSR.
        """
        return float(np.sum((self.predicted() - self.y.mean()) ** 2))

    def SST(self) -> float:
        """
        Calcula la Suma Total de los Cuadrados (SST), que es la suma de SSR y SSE.

        Returns:
            float: Valor de la SST.
        """
        return float(np.sum((self.y - self.y.mean()) ** 2))

    def R2(self) -> float:
        """
        Calcula el coeficiente de determinación R², que indica la proporción
        de la varianza explicada por el modelo.

        Returns:
            float: Valor de R².
        """
        return 1 - self.SSE() / self.SST()
    
    def R2_adj(self) -> float:
        """
        Calcula el coeficiente de determinación ajustado (R² ajustado),
        que penaliza por el número de predictores.

        Returns:
            float: Valor de R² ajustado.
        """
        n = self.X.shape[0]
        return 1 - ((n - 1) * self.MSE()) / self.SST()
    
    def PRESSp(self):
        """
        Calcula el estadístico PRESS (Predicted Residual Error Sum of Squares) para el modelo de regresión.

        Returns:
            float: Valor escalar del estadístico PRESS.
        """
        return float(np.sum((self.residuals / (1 - np.diag(self.hat_matrix()))) ** 2))
    
    def hat_matrix(self) -> np.ndarray:
        """
        Calcula la matriz "hat" (H), que es utilizada para obtener las predicciones
        en la regresión lineal.

        La matriz hat se define como H = X(XᵀX)⁻¹Xᵀ, donde X es la matriz de diseño
        y Xᵀ es su transpuesta.

        Returns:
            np.ndarray: La matriz "hat", un arreglo de forma (n, n).
        """
        X = self.X_matrix
        return X @ np.linalg.inv(X.T @ X) @ X.T
    
    def summary(self) -> pd.DataFrame:
        """Genera un resumen con las métricas principales del modelo."""
        sse = self.SSE()
        mse = self.MSE()
        n, _ = self.X_matrix.shape
        data = {
            "SSR (Regresión)": [self.SSR()],
            "SSE (Error)": [sse],
            "SST (Total)": [self.SST()],
            "MSR (Media Regresión)": [self.MSR()],
            "MSE (Media Error)": [mse],
            "R²": [self.R2()],
            "R² ajustado": [self.R2_adj()],
            "PRESSp": [self.PRESSp()],
            "Cp": [(sse / mse) - (n - 2 * (self.X_matrix.shape[1] - 1))]
        }
        df = pd.DataFrame.from_dict(data, orient='index', columns=["Valor"])
        df.index.name = "Estadístico"
        pd.set_option("display.float_format", "{:.4f}".format)
        return df
    
    def MSR(self) -> float:
        """Calcula la Media de los Cuadrados de la Regresión (MSR)."""
        return self.SSR() / float(self.X_matrix.shape[1] - 1)
    
    def coefficients_var_matrix(self) -> np.ndarray:
        """
        Calcula la matriz de varianza-covarianza de los coeficientes estimados.

        Returns:
            np.ndarray: Matriz (p x p) con las varianzas y covarianzas de los coeficientes.
        """
        return self.var() * np.linalg.inv(self.X_matrix.T @ self.X_matrix)

    def coefficients_var(self) -> np.ndarray:
        """
        Extrae las varianzas individuales de los coeficientes desde la matriz de varianza-covarianza.

        Returns:
            np.ndarray: Vector con las varianzas de cada coeficiente.
        """
        return np.diag(self.coefficients_var_matrix())
    
    def coefficients_confidence_intervals(self, alpha : float = 0.05) -> List[Tuple[float, float]]:
        """
        Calcula los intervalos de confianza para cada coeficiente beta del modelo de regresión.

        Args:
            alpha (float): Nivel de significancia (por defecto 0.05 para un intervalo de confianza del 95%).

        Returns:
            List[Tuple[float, float]]: Lista de tuplas, donde cada tupla representa el intervalo de confianza
                                    (límite inferior, límite superior) para un coeficiente.
        """
        n, p = self.X_matrix.shape
        t_crit = t.ppf(1 - alpha / 2, n - p)
        errors = np.sqrt(self.coefficients_var())
        lower = self.coefficients - t_crit * errors
        upper = self.coefficients + t_crit * errors
        return [(float(l), float(u)) for l, u in zip(lower, upper)]
    
    def coefficients_hipotesis_test(self, values : Optional[list[float]] = None, alpha : float = 0.05) -> List[bool]:
        """
        Realiza la prueba de hipótesis sobre los coeficientes del modelo de regresión lineal.
        Compara cada coeficiente con el valor proporcionado en `values` y determina si se
        acepta la hipótesis nula (coeficiente igual a `value`) con un nivel de significancia `alpha`.

        Args:
            values (List[float]): Lista de valores hipotéticos para cada coeficiente. Si está vacía,
                                se asume que el valor hipotético para cada coeficiente es 0.
            alpha (float): Nivel de significancia para la prueba (por defecto 0.05).

        Returns:
            List[bool]: Lista de valores booleanos que indican si se acepta o no la hipótesis nula
                        para cada coeficiente. True si se acepta (coeficiente no significativamente distinto),
                        False en caso contrario.
        """
        if values is None:
            values = np.zeros(self.coefficients.shape[0])
        elif isinstance(values, list):
            values = np.array(values)
        if values.shape[0] != self.coefficients.shape[0]:
            raise ValueError("El tamaño de 'values' no coincide con el número de coeficientes")
        n, p = self.X_matrix.shape
        t_crit = t.ppf(1 - alpha / 2, n - p)
        std_errors = np.sqrt(np.diag(self.coefficients_var_matrix()))
        results = []
        for i, coef in enumerate(self.coefficients):
            t_stat = (coef - values[i]) / std_errors[i]
            results.append(not abs(t_stat) > abs(t_crit))
        return results
    
    def standardized_residuals(self) -> np.ndarray:
        """
        Calcula los residuales estandarizados dividiendo cada residual por 
        la desviación estándar común de los errores (raíz del MSE).

        Returns:
            np.ndarray: Vector de residuales estandarizados.
        """
        return (self.residuals) / np.sqrt(self.MSE())

    def studentized_residuals(self) -> np.ndarray:
        """
        Calcula los residuales studentizados, que ajustan la varianza del error
        para cada observación individual utilizando la matriz "hat".

        Returns:
            np.ndarray: Vector de residuales studentizados.
        """
        return (self.residuals) / np.sqrt(self.MSE() * (1 - np.diag(self.hat_matrix())))

    def get_outliers_std(self, threshold: Optional[float] = 3.0) -> List[int]:
        """
        Devuelve los índices de observaciones atípicas según residuos estandarizados.

        Args:
            threshold (Optional[float]): Umbral absoluto para considerar una observación como atípica.

        Returns:
            List[int]: Índices donde |residuo estandarizado| > threshold.
        """
        if threshold is None:
            threshold = 3.0
        res_std = np.abs(self.standardized_residuals())
        return [i for i, val in enumerate(res_std) if val > threshold]

    def get_outliers_stud(self, threshold: Optional[float] = 3.0) -> List[int]:
        """
        Devuelve los índices de observaciones atípicas según residuos studentizados.

        Args:
            threshold (Optional[float]): Umbral absoluto para considerar una observación como atípica.

        Returns:
            List[int]: Índices donde |residuo studentizado| > threshold.
        """
        if threshold is None:
            threshold = 3.0
        res_stud = np.abs(self.studentized_residuals())
        return [i for i, val in enumerate(res_stud) if val > threshold]
    
    def _leverage_points(self) -> np.ndarray:
        """
        Identifica los puntos de balanceo en el modelo.

        Returns:
            np.ndarray: Un arreglo booleano donde True indica un punto de alto apalancamiento.
        """
        n, p = self.X_matrix.shape
        threshold = 2 * p / n
        if threshold < 1:
            leverage_values = np.diag(self.hat_matrix())
            return leverage_values > threshold
        warn("La condición para revisar puntos de alto apalancamiento (2p/n < 1) no se cumple.", UserWarning)
        return np.full(n, False)
    
    def get_leverage_points(self) -> List[int]:
        """
        Devuelve los índices de los puntos de balanceo.

        Returns:
            List[int]: Lista de índices donde el balanceo supera el umbral.
        """
        mask = self._leverage_points()
        return [i for i, val in enumerate(mask) if val]

    
    def _influential_obs(self) -> np.ndarray:
        """
        Calcula la distancia de Cook para identificar observaciones influenciales en el modelo.

        Returns:
            np.ndarray: Arreglo booleano donde True indica una observación influencial.
        """
        _, p = self.X_matrix.shape
        leverage = np.diag(self.hat_matrix())
        Di = (self.residuals ** 2 / p) * (leverage / (1 - leverage))
        return Di > 1
    
    def get_influential_obs(self) -> List[int]:
        """
        Devuelve los índices de las observaciones influenciales según la distancia de Cook.

        Returns:
            List[int]: Lista de índices donde la distancia de Cook es mayor a 1.
        """
        mask = self._influential_obs()
        return [i for i, val in enumerate(mask) if val]
    
    def residuals_normality_test(self, alpha: float = 0.05) -> Tuple[float, bool]:
        """
        Verifica la normalidad de los residuales del modelo utilizando la prueba de Shapiro-Wilk.

        Args:
            alpha (float): Nivel de significancia para la prueba (por defecto 0.05).

        Returns:
                True si no se rechaza la hipótesis nula (los residuales son normales), False si se rechaza
        """
        residuals = self.y - self.predicted()
        p_val = shapiro(residuals)[1]
        return p_val, p_val > alpha
    
    def plot_residuals_vs_fitted(self):
        """
        Grafica los residuales del modelo vs los valores predichos usando seaborn.
        Permite identificar patrones no aleatorios, heterocedasticidad o outliers.
        """
        residuals = self.y - self.predicted()
        fitted = self.predicted()

        plt.figure(figsize=(8, 5))
        sns.scatterplot(x=fitted, y=residuals)
        sns.lineplot(x=fitted, y=[0]*len(fitted), color='red', linestyle='--')
        plt.xlabel("Valores ajustados (ŷ)")
        plt.ylabel("Residuales")
        plt.title("Residuales vs Valores ajustados")
        plt.grid(True)
        plt.show()