import pygame
import math
import numpy as np

# ==========================================
# CONSTANTES DE CONFIGURAÇÃO
# ==========================================

LARGURA_TELA = 800
ALTURA_TELA = 600
FPS = 60

COR_FUNDO = (30, 30, 30)
COR_ROBO = (0, 180, 255)
COR_DIRECAO = (255, 50, 50)
COR_TRAJETORIA = (100, 200, 100)
COR_ALVO = (255, 220, 0)

# ==========================================
# PARÂMETROS DO CONTROLADOR PROPORCIONAL
# ==========================================

Kp = 3.0

# Velocidade linear do robô
VELOCIDADE = 100.0  # pixels/s

# Distância máxima para considerar que chegou
DISTANCIA_MINIMA = 10.0  # pixels

# Limite da velocidade angular
LIMITE_OMEGA = 4.0  # rad/s


# ==========================================
# CLASSE DO ROBÔ
# ==========================================

class DiffDriveRobot:

    def __init__(
        self,
        x,
        y,
        theta=0.0,
        wheelbase=30.0,
        radius=15.0
    ):

        # Estado do robô
        self.x = float(x)
        self.y = float(y)
        self.theta = float(theta)

        # Distância entre as rodas
        self.L = float(wheelbase)

        # Raio visual do robô
        self.radius = float(radius)

        # Velocidade linear
        self.v = 0.0

        # Velocidade angular
        self.omega = 0.0

        # Histórico da trajetória
        self.history = []

    def set_direct_velocity(self, v, omega):
        """
        Define a velocidade linear
        e a velocidade angular.
        """

        self.v = v
        self.omega = omega

    def stop(self):
        """
        Para o robô.
        """

        self.v = 0.0
        self.omega = 0.0

    def update(self, dt):
        """
        Atualiza a posição e orientação do robô.
        """

        # Atualização angular
        self.theta += self.omega * dt

        # Normaliza o ângulo entre -pi e pi
        self.theta = (
            (self.theta + math.pi)
            % (2 * math.pi)
            - math.pi
        )

        # Atualização da posição
        self.x += (
            self.v
            * math.cos(self.theta)
            * dt
        )

        self.y += (
            self.v
            * math.sin(self.theta)
            * dt
        )

        # Guarda histórico da trajetória
        if (
            len(self.history) == 0
            or np.hypot(
                self.x - self.history[-1][0],
                self.y - self.history[-1][1]
            ) > 5
        ):

            self.history.append(
                (self.x, self.y)
            )

            if len(self.history) > 500:
                self.history.pop(0)

    def draw(self, surface):

        # ======================================
        # Desenha o rastro
        # ======================================

        if len(self.history) > 1:

            pygame.draw.lines(
                surface,
                COR_TRAJETORIA,
                False,
                self.history,
                2
            )

        # ======================================
        # Desenha o corpo do robô
        # ======================================

        pos_int = (
            int(self.x),
            int(self.y)
        )

        pygame.draw.circle(
            surface,
            COR_ROBO,
            pos_int,
            int(self.radius)
        )

        # ======================================
        # Desenha a direção do robô
        # ======================================

        linha_frente_x = (
            self.x
            + (self.radius + 10)
            * math.cos(self.theta)
        )

        linha_frente_y = (
            self.y
            + (self.radius + 10)
            * math.sin(self.theta)
        )

        pygame.draw.line(
            surface,
            COR_DIRECAO,
            pos_int,
            (
                int(linha_frente_x),
                int(linha_frente_y)
            ),
            3
        )


# ==========================================
# NORMALIZAÇÃO DO ÂNGULO
# ==========================================

def normalizar_angulo(angulo):

    return (
        (angulo + math.pi)
        % (2 * math.pi)
        - math.pi
    )


# ==========================================
# FUNÇÃO PRINCIPAL
# ==========================================

def main():

    pygame.init()

    screen = pygame.display.set_mode(
        (LARGURA_TELA, ALTURA_TELA)
    )

    pygame.display.set_caption(
        "Exercicio 3 - Controle Proporcional"
    )

    clock = pygame.time.Clock()

    font = pygame.font.SysFont(
        "monospace",
        14
    )

    # ======================================
    # CRIAÇÃO DO ROBÔ
    # ======================================

    robot = DiffDriveRobot(
        x=LARGURA_TELA // 2,
        y=ALTURA_TELA // 2,
        theta=0.0
    )

    # Ponto alvo
    alvo = None

    # Indica se o robô atingiu o alvo
    alvo_atingido = False

    running = True

    while running:

        # Delta time
        dt = clock.tick(FPS) / 1000.0

        # ==================================
        # EVENTOS
        # ==================================

        for event in pygame.event.get():

            # Fechar janela
            if event.type == pygame.QUIT:

                running = False

            # ==================================
            # CLIQUE DO MOUSE
            # ==================================

            if event.type == pygame.MOUSEBUTTONDOWN:

                # Botão esquerdo do mouse
                if event.button == 1:

                    # Define o novo ponto alvo
                    alvo = (
                        float(event.pos[0]),
                        float(event.pos[1])
                    )

                    # Permite iniciar novamente
                    alvo_atingido = False

                    print(
                        f"Alvo definido: "
                        f"x={alvo[0]:.0f}, "
                        f"y={alvo[1]:.0f}"
                    )

        # ==================================
        # EXERCÍCIO 3
        # CONTROLE PROPORCIONAL
        # ==================================

        if alvo is not None and not alvo_atingido:

            x_alvo = alvo[0]
            y_alvo = alvo[1]

            # ==================================
            # DISTÂNCIA ATÉ O ALVO
            # ==================================

            distancia = math.hypot(
                x_alvo - robot.x,
                y_alvo - robot.y
            )

            # ==================================
            # VERIFICA SE CHEGOU
            #
            # Para quando estiver a 10 pixels
            # ou menos do destino
            # ==================================

            if distancia <= DISTANCIA_MINIMA:

                robot.stop()

                alvo_atingido = True

            else:

                # ==================================
                # ÂNGULO DESEJADO
                #
                # theta_desejado =
                # atan2(y_alvo - y,
                #       x_alvo - x)
                # ==================================

                theta_desejado = math.atan2(
                    y_alvo - robot.y,
                    x_alvo - robot.x
                )

                # ==================================
                # ERRO ANGULAR
                #
                # erro_theta =
                # theta_desejado - theta
                # ==================================

                erro_theta = (
                    theta_desejado
                    - robot.theta
                )

                # Normaliza o erro entre -pi e pi
                erro_theta = normalizar_angulo(
                    erro_theta
                )

                # ==================================
                # CONTROLADOR PROPORCIONAL
                #
                # omega = Kp * erro_theta
                # ==================================

                omega = Kp * erro_theta

                # Limita a velocidade angular
                omega = max(
                    -LIMITE_OMEGA,
                    min(LIMITE_OMEGA, omega)
                )

                # ==================================
                # MOVIMENTO DO ROBÔ
                # ==================================

                robot.set_direct_velocity(
                    VELOCIDADE,
                    omega
                )

        else:

            # Sem alvo ou alvo atingido
            robot.stop()

        # ==================================
        # ATUALIZAÇÃO DO ROBÔ
        # ==================================

        robot.update(dt)

        # ==================================
        # RENDERIZAÇÃO
        # ==================================

        screen.fill(COR_FUNDO)

        # Desenha o robô
        robot.draw(screen)

        # ==================================
        # DESENHA O ALVO
        # ==================================

        if alvo is not None:

            alvo_int = (
                int(alvo[0]),
                int(alvo[1])
            )

            # Círculo externo
            pygame.draw.circle(
                screen,
                COR_ALVO,
                alvo_int,
                10,
                2
            )

            # Ponto central
            pygame.draw.circle(
                screen,
                COR_ALVO,
                alvo_int,
                3
            )

            # Linha entre robô e alvo
            pygame.draw.line(
                screen,
                COR_ALVO,
                (
                    int(robot.x),
                    int(robot.y)
                ),
                alvo_int,
                1
            )

        # ==================================
        # TELEMETRIA
        # ==================================

        if alvo is None:

            status = (
                "Clique na tela para definir "
                "o ponto alvo"
            )

            distancia_txt = "Distancia: --"
            erro_txt = "Erro theta: --"

        elif alvo_atingido:

            status = "ALVO ATINGIDO - ROBÔ PARADO"

            distancia_final = math.hypot(
                alvo[0] - robot.x,
                alvo[1] - robot.y
            )

            distancia_txt = (
                f"Distancia: "
                f"{distancia_final:.1f} px"
            )

            erro_txt = "Erro theta: --"

        else:

            distancia = math.hypot(
                alvo[0] - robot.x,
                alvo[1] - robot.y
            )

            theta_desejado = math.atan2(
                alvo[1] - robot.y,
                alvo[0] - robot.x
            )

            erro_theta = normalizar_angulo(
                theta_desejado - robot.theta
            )

            status = "Robô seguindo o alvo"

            distancia_txt = (
                f"Distancia: {distancia:.1f} px"
            )

            erro_txt = (
                f"Erro theta: {erro_theta:.2f} rad"
            )

        # ==================================
        # PAINEL DE INFORMAÇÕES
        # ==================================

        info_txt = [

            "EXERCICIO 3 - CONTROLE PROPORCIONAL",

            status,

            (
                f"Pose X: {robot.x:.1f} px | "
                f"Y: {robot.y:.1f} px | "
                f"Theta: "
                f"{math.degrees(robot.theta):.1f} deg"
            ),

            distancia_txt,

            erro_txt,

            (
                f"Kp: {Kp:.1f} | "
                f"omega: {robot.omega:.2f} rad/s"
            ),

            (
                f"Velocidade: "
                f"{robot.v:.1f} px/s"
            ),

            "Clique com o botao esquerdo para definir um alvo"
        ]

        for i, txt in enumerate(info_txt):

            rendered = font.render(
                txt,
                True,
                (220, 220, 220)
            )

            screen.blit(
                rendered,
                (15, 15 + i * 20)
            )

        pygame.display.flip()

    pygame.quit()


# ==========================================
# EXECUÇÃO
# ==========================================

if __name__ == "__main__":
    main()
