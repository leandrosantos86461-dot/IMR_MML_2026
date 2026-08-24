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

# Velocidades do robô
VELOCIDADE_LINEAR = 80.0
VELOCIDADE_ANGULAR = math.pi / 2   # 90 graus/s


# ==========================================
# ROBÔ DIFERENCIAL
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

        # Parâmetros físicos
        self.L = float(wheelbase)
        self.radius = float(radius)

        # Velocidade linear e angular
        self.v = 0.0
        self.omega = 0.0

        # Histórico da trajetória
        self.history = []

    def set_wheel_velocities(self, v_left, v_right):

        """
        Converte as velocidades das rodas
        em velocidade linear e angular.
        """

        self.v = (v_right + v_left) / 2.0

        self.omega = (
            (v_right - v_left)
            / self.L
        )

    def set_direct_velocity(self, v, omega):

        """
        Define diretamente velocidade linear
        e velocidade angular.
        """

        self.v = v
        self.omega = omega

    def update(self, dt):

        # Atualiza orientação
        self.theta += self.omega * dt

        # Normaliza theta
        self.theta = (
            self.theta + math.pi
        ) % (2 * math.pi) - math.pi

        # Atualiza posição
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

        # Guarda trajetória
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

            if len(self.history) > 1000:
                self.history.pop(0)

    def draw(self, surface):

        # ------------------------------------------
        # Rastro
        # ------------------------------------------

        if len(self.history) > 1:

            pygame.draw.lines(
                surface,
                COR_TRAJETORIA,
                False,
                self.history,
                2
            )

        # ------------------------------------------
        # Corpo
        # ------------------------------------------

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

        # ------------------------------------------
        # Direção
        # ------------------------------------------

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
# PROGRAMA PRINCIPAL
# ==========================================

def main():

    pygame.init()

    screen = pygame.display.set_mode(
        (
            LARGURA_TELA,
            ALTURA_TELA
        )
    )

    pygame.display.set_caption(
        "Exercício 2 - Quadrado em Malha Aberta"
    )

    clock = pygame.time.Clock()

    font = pygame.font.SysFont(
        "monospace",
        14
    )

    # ==========================================
    # CRIAÇÃO DO ROBÔ
    # ==========================================

    robot = DiffDriveRobot(
        x=200,
        y=300,
        theta=0.0
    )

    # ==========================================
    # MÁQUINA DE ESTADOS
    # ==========================================

    estado = "ANDAR"

    tempo_estado = 0.0

    lado_atual = 0

    TOTAL_LADOS = 4

    running = True

    while running:

        # ------------------------------------------
        # Delta time
        # ------------------------------------------

        dt = clock.tick(FPS) / 1000.0

        # ------------------------------------------
        # Eventos
        # ------------------------------------------

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                running = False

        # ==========================================
        # CONTROLE POR MÁQUINA DE ESTADOS
        # ==========================================

        tempo_estado += dt

        # ==========================================
        # ESTADO 1 - ANDAR
        # ==========================================

        if estado == "ANDAR":

            # Anda para frente
            robot.set_direct_velocity(
                VELOCIDADE_LINEAR,
                0.0
            )

            # Depois de 2 segundos,
            # começa a girar
            if tempo_estado >= 2.0:

                tempo_estado = 0.0

                estado = "GIRAR"

        # ==========================================
        # ESTADO 2 - GIRAR
        # ==========================================

        elif estado == "GIRAR":

            # Gira 90 graus/s
            robot.set_direct_velocity(
                0.0,
                VELOCIDADE_ANGULAR
            )

            # Depois de 1 segundo
            if tempo_estado >= 1.0:

                tempo_estado = 0.0

                lado_atual += 1

                # Se completou os 4 lados
                if lado_atual >= TOTAL_LADOS:

                    estado = "FINALIZADO"

                else:

                    estado = "ANDAR"

        # ==========================================
        # ESTADO FINAL
        # ==========================================

        elif estado == "FINALIZADO":

            # Para o robô
            robot.set_direct_velocity(
                0.0,
                0.0
            )

        # ==========================================
        # ATUALIZA ROBÔ
        # ==========================================

        robot.update(dt)

        # ==========================================
        # RENDERIZAÇÃO
        # ==========================================

        screen.fill(COR_FUNDO)

        robot.draw(screen)

        # ==========================================
        # TELEMETRIA
        # ==========================================

        info_txt = [

            f"Estado: {estado}",

            f"Lado: {min(lado_atual + 1, 4)} / 4",

            f"Tempo no estado: {tempo_estado:.2f} s",

            f"X: {robot.x:.1f} px",

            f"Y: {robot.y:.1f} px",

            f"Theta: "
            f"{math.degrees(robot.theta):.1f} graus",

            f"v = {robot.v:.1f} px/s",

            f"omega = "
            f"{robot.omega:.2f} rad/s"

        ]

        for i, txt in enumerate(info_txt):

            rendered = font.render(
                txt,
                True,
                (220, 220, 220)
            )

            screen.blit(
                rendered,
                (
                    15,
                    15 + i * 20
                )
            )

        pygame.display.flip()

    pygame.quit()


# ==========================================
# EXECUÇÃO
# ==========================================

if __name__ == "__main__":
    main()
