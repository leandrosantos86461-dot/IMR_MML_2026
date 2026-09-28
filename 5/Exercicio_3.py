import math


def controle_reativo(distancias):
    """Retorna comando de velocidade linear e angular para evitar obstáculos."""
    frente = float(distancias.get("frente", float("inf")))
    esquerda = float(distancias.get("esquerda", float("inf")))
    direita = float(distancias.get("direita", float("inf")))

    if not math.isfinite(esquerda):
        esquerda = 5.0
    if not math.isfinite(direita):
        direita = 5.0

    if frente < 0.4:
        omega = 1.0 if esquerda <= direita else -1.0
        return 0.0, omega

    omega = 0.5 * (direita - esquerda)
    omega = max(-1.0, min(1.0, omega))
    return 0.5, omega


if __name__ == "__main__":
    print(controle_reativo({"frente": 0.2, "esquerda": 1.0, "direita": 0.6}))
    print(controle_reativo({"frente": 1.0, "esquerda": 0.8, "direita": 1.5}))
