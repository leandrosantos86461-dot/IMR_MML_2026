import math

from exercicio3 import controle_reativo
from exercicio4 import calcular_orientacao_alvo


def maquina_de_estados(x, y, theta, x_alvo, y_alvo, dist_frente, dist_esq, dist_dir):
    """Retorna o estado atual e o comando de velocidade correspondente."""
    distancia_ao_alvo = math.hypot(x_alvo - x, y_alvo - y)

    if distancia_ao_alvo < 0.2:
        return "OBJETIVO_ALCANÇADO", 0.0, 0.0

    if dist_frente < 0.5:
        estado = "DESVIAR_OBSTACULO"
        v_cmd, omega_cmd = controle_reativo({
            "frente": dist_frente,
            "esquerda": dist_esq,
            "direita": dist_dir,
        })
        return estado, v_cmd, omega_cmd

    estado = "IR_PARA_ALVO"
    omega_cmd = calcular_orientacao_alvo(x, y, theta, x_alvo, y_alvo)
    return estado, 0.5, omega_cmd


if __name__ == "__main__":
    print(maquina_de_estados(0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 1.0, 1.0))
    print(maquina_de_estados(0.0, 0.0, 0.0, 1.0, 0.0, 0.2, 0.9, 0.7))
    print(maquina_de_estados(0.1, 0.1, 0.0, 0.11, 0.11, 1.0, 1.0, 1.0))
