import numpy as np


def processar_scan(leituras_lidar):
    """Retorna a menor distância válida para frente, esquerda e direita."""
    arr = np.asarray(leituras_lidar, dtype=float).reshape(-1)

    if arr.size != 360:
        raise ValueError("leituras_lidar deve conter exatamente 360 leituras.")

    def menor_setor(indices):
        valores = arr[list(indices)]
        mascara = np.isfinite(valores) & (valores >= 0.1) & (valores <= 5.0)
        valores_validos = valores[mascara]

        if valores_validos.size == 0:
            return float("inf")
        return float(np.min(valores_validos))

    indices_frente = list(range(345, 360)) + list(range(0, 16))
    indices_esquerda = list(range(45, 136))
    indices_direita = list(range(225, 316))

    return {
        "frente": menor_setor(indices_frente),
        "esquerda": menor_setor(indices_esquerda),
        "direita": menor_setor(indices_direita),
    }


if __name__ == "__main__":
    scan = np.full(360, 5.0)
    scan[0:10] = 0.2
    scan[45:60] = 0.5
    scan[225:235] = 0.7
    scan[200] = 0.0
    scan[300] = 10.0
    scan[100] = np.inf
    scan[150] = np.nan
    print(processar_scan(scan))
