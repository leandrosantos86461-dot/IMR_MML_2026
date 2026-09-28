def converter_cmd_vel(v, omega, L=0.3, max_wheel_speed=1.5):
    """Converte (v, omega) em velocidades das rodas e aplica saturação."""
    v_esquerda = v + (omega * L / 2.0)
    v_direita = v - (omega * L / 2.0)

    velocidade_maxima = max(abs(v_esquerda), abs(v_direita))
    if velocidade_maxima == 0:
        return 0.0, 0.0

    if velocidade_maxima > max_wheel_speed:
        fator = max_wheel_speed / velocidade_maxima
        v_esquerda *= fator
        v_direita *= fator

    return v_esquerda, v_direita


if __name__ == "__main__":
    print(converter_cmd_vel(1.2, 3.0))
    print(converter_cmd_vel(0.5, 0.0))
    print(converter_cmd_vel(0.0, 4.0))
