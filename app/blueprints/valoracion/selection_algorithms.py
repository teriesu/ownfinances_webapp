import numpy as np
import pandas as pd

class SelectionAlgorithms:
    def __init__(self, df: pd.DataFrame):
        """
        df: DataFrame con formato:
            - Filas 0..n-3: alternativas con columna 'Nombres' + columnas de criterios
            - Penúltima fila: pesos (sin contar la columna 'Nombres')
            - Última fila: objetivos 'max'/'min'
        """
        self.df_raw = df.copy()
        # Extraer nombres, características, pesos y objetivos
        self.names = df.iloc[:-2, 0].values
        self.features = df.iloc[:-2, 1:].astype(float).values
        self.weights = df.iloc[-2, 1:].astype(float).values
        self.objectives = df.iloc[-1, 1:].astype(str).values

    def _normalize(self, method: str):
        """ Normaliza self.features según el método indicado. """
        X = self.features
        if method == 'electre':
            # Normalización al estilo ELECTRE: vector de norma euclídea (o inverso para minimización)
            M = np.zeros_like(X)
            for j, obj in enumerate(self.objectives):
                col = X[:, j]
                if obj == 'max':
                    M[:, j] = col / np.linalg.norm(col)
                else:  # 'min'
                    inv = 1/col
                    M[:, j] = inv / np.linalg.norm(inv)
            return M

        elif method == 'topsis':
            # TOPSIS usa exactamente normalización Euclidiana
            return X / np.linalg.norm(X, axis=0)

        else:
            # Para VIKOR y PROMETHEE usamos min–max según objetivo
            M = np.zeros_like(X)
            minv = X.min(axis=0)
            maxv = X.max(axis=0)
            for j, obj in enumerate(self.objectives):
                if maxv[j] == minv[j]:
                    M[:, j] = 0
                elif obj == 'max':
                    M[:, j] = (X[:, j] - minv[j]) / (maxv[j] - minv[j])
                else:  # 'min'
                    M[:, j] = (maxv[j] - X[:, j]) / (maxv[j] - minv[j])
            return M

    def _weighted(self, M: np.ndarray):
        """ Aplica pesos a la matriz normalizada M """
        return M * self.weights

    def topsis(self) -> pd.DataFrame:
        M = self._normalize('topsis')
        W = self._weighted(M)
        # Ideales
        pos = np.where(self.objectives=='max', W.max(axis=0), W.min(axis=0))
        neg = np.where(self.objectives=='max', W.min(axis=0), W.max(axis=0))
        d_pos = np.linalg.norm(W - pos, axis=1)
        d_neg = np.linalg.norm(W - neg, axis=1)
        score = d_neg / (d_pos + d_neg)
        df = pd.DataFrame({
            'Nombres': self.names,
            'Coeficiente': score
        })
        df['Ranking_TOPSIS'] = df['Coeficiente'].rank(ascending=False, method='min')
        return df

    def electre(self) -> pd.DataFrame:
        M = self._normalize('electre')
        W = self._weighted(M)
        n = W.shape[0]
        # Matriz de concordancia y discordancia
        C = np.zeros((n,n))
        D_vals = np.zeros((n,n))
        for i in range(n):
            for j in range(n):
                diff = W[i] - W[j]
                # Concordancia: suma de pesos donde diff > 0
                C[i,j] = np.sum(self.weights[diff > 0])
                # Discordancia: max relativo de |diff_k| / rango_k
                Rk = np.max(np.abs(diff))
                D_vals[i,j] = 0 if Rk==0 else np.max(np.abs(diff)) / Rk

        # Umbrales
        thr_c = C.sum()/(n**2 - n)
        thr_d = D_vals.sum()/(n**2 - n)
        # Construcción de matices binarios
        C_d = (C >= thr_c).astype(int)
        D_d = (D_vals <= thr_d).astype(int)
        # Dominancia
        A = C_d * D_d
        outflow = A.sum(axis=1)
        inflow  = A.sum(axis=0)
        score = outflow - inflow
        df = pd.DataFrame({
            'Nombres': self.names,
            'Dominancia': score
        })
        df['Ranking_ELECTRE'] = df['Dominancia'].rank(ascending=False, method='min')
        return df

    def promethee(self) -> pd.DataFrame:
        # Matriz de preferencia tipo I: P(a_i,a_j) = 1 si i mejor que j en criterio, 0 si no
        X = self.features
        n, m = X.shape
        pref_matrices = []
        for j in range(m):
            Pj = np.zeros((n,n))
            for i in range(n):
                for k in range(n):
                    diff = X[i,j] - X[k,j]
                    if self.objectives[j] == 'max':
                        Pj[i,k] = 1 if diff > 0 else 0
                    else:
                        Pj[i,k] = 1 if diff < 0 else 0
            pref_matrices.append(Pj)
        # Flujos
        phi_plus  = np.array([np.sum(self.weights[j]*pref_matrices[j], axis=1) for j in range(m)]).sum(axis=0)/n
        phi_minus = np.array([np.sum(self.weights[j]*pref_matrices[j], axis=0) for j in range(m)]).sum(axis=0)/n
        net = phi_plus - phi_minus
        df = pd.DataFrame({
            'Nombres': self.names,
            'Phi+': phi_plus,
            'Phi-': phi_minus,
            'NetFlow': net
        })
        df['Ranking_PROMETHEE'] = df['NetFlow'].rank(ascending=False, method='min')
        return df

    def vikor(self, v: float = 0.5) -> pd.DataFrame:
        M = self._normalize('vikor')
        W = self._weighted(M)
        S = W.sum(axis=1)
        R = W.max(axis=1)
        Smin, Smax = S.min(), S.max()
        Rmin, Rmax = R.min(), R.max()
        Q = v*(S - Smin)/(Smax - Smin) + (1-v)*(R - Rmin)/(Rmax - Rmin)
        df = pd.DataFrame({
            'Nombres': self.names,
            'S': S,
            'R': R,
            'Q': Q
        })
        df['Ranking_VIKOR'] = df['Q'].rank(ascending=True, method='min')
        return df

    def evaluate(self, methods=None, aggregate: bool = False) -> pd.DataFrame:
        """
        methods: lista de strings entre {'topsis','electre','promethee','vikor'}.
                 Si None, usa todos.
        aggregate: si True, añade columna 'Ponderado' con promedio de rankings.
        """
        if methods is None:
            methods = ['topsis','electre','promethee','vikor']

        # 1) Inicializo el resultado solo con la columna 'Nombres'
        result = pd.DataFrame({'Nombres': self.names})

        # 2) Para cada método, obtengo su DF y lo uno sobre 'Nombres'
        for m in methods:
            dfm = getattr(self, m)()      # éste ya incluye 'Nombres'
            result = result.merge(dfm,     # pandas mantiene una única 'Nombres'
                                  on='Nombres',
                                  how='inner')

        # 3) Si piden agregación, calculo el Ponderado de todos los rankings
        if aggregate:
            rank_cols = [c for c in result.columns if c.startswith('Ranking')]
            result['Ponderado'] = result[rank_cols].mean(axis=1)
            result = result.sort_values('Ponderado', ascending=True).reset_index(drop=True)

        return result