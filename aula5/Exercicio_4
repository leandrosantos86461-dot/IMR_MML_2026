import math


def calcular_orientacao_alvo(x, y, theta, x_alvo, y_alvo, Kp=1.5):
    """Calcula omega para alinhar o robô na direção do alvo."""
    theta_alvo = math.atan2(y_alvo - y, x_alvo - x)
    erro = theta_alvo - theta
    erro = (erro + math.pi) % (2 * math.pi) - math.pi
    omega = Kp * erro
    return omega


if __name__ == "__main__":
    print(calcular_orientacao_alvo(0.0, 0.0, 0.0, 1.0, 0.0))
    print(calcular_orientacao_alvo(0.0, 0.0, 0.0, 0.0, 1.0))
