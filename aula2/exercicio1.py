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


# ==========================================
# ROBÔ DIFERENCIAL
# ==========================================

class DiffDriveRobot:

    def __init__(self, x, y, theta=0.0, wheelbase=30.0, radius=15.0):

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
        Converte as velocidades individuais das rodas
        em velocidade linear (v) e angular (omega).
        """

        self.v = (v_right + v_left) / 2.0
        self.omega = (v_right - v_left) / self.L

    def update(self, dt):
        """
        Atualiza a posição e orientação do robô.
        """

        # Atualiza orientação
        self.theta += self.omega * dt

        # Mantém theta entre -pi e pi
        self.theta = (self.theta + math.pi) % (2 * math.pi) - math.pi

        # Atualiza posição
        self.x += self.v * math.cos(self.theta) * dt
        self.y += self.v * math.sin(self.theta) * dt

        # Guarda trajetória
        if (
            len(self.history) == 0
            or np.hypot(
                self.x - self.history[-1][0],
                self.y - self.history[-1][1]
            ) > 5
        ):
            self.history.append((self.x, self.y))

            if len(self.history) > 500:
                self.history.pop(0)

    def draw(self, surface):

        # ------------------------------------------
        # 1. Desenha o rastro
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
        # 2. Desenha o corpo
        # ------------------------------------------

        pos_int = (int(self.x), int(self.y))

        pygame.draw.circle(
            surface,
            COR_ROBO,
            pos_int,
            int(self.radius)
        )

        # ------------------------------------------
        # 3. Desenha direção do robô
        # ------------------------------------------

        linha_frente_x = (
            self.x
            + (self.radius + 10) * math.cos(self.theta)
        )

        linha_frente_y = (
            self.y
            + (self.radius + 10) * math.sin(self.theta)
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
        (LARGURA_TELA, ALTURA_TELA)
    )

    pygame.display.set_caption(
        "Exercício 1 - Controle por Rodas"
    )

    clock = pygame.time.Clock()

    font = pygame.font.SysFont(
        "monospace",
        14
    )

    # ------------------------------------------
    # Criação do robô
    # ------------------------------------------

    robot = DiffDriveRobot(
        x=LARGURA_TELA // 2,
        y=ALTURA_TELA // 2,
        theta=0.0
    )

    running = True

    while running:

        # Delta time
        dt = clock.tick(FPS) / 1000.0

        # ------------------------------------------
        # Eventos
        # ------------------------------------------

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

        # ==========================================
        # CONTROLE INDIVIDUAL DAS RODAS
        # ==========================================

        keys = pygame.key.get_pressed()

        # Velocidade inicial das rodas
        v_left = 0.0
        v_right = 0.0

        VELOCIDADE_RODA = 40.0

        # ------------------------------------------
        # RODA ESQUERDA
        # ------------------------------------------

        # W = roda esquerda para frente
        if keys[pygame.K_w]:
            v_left = VELOCIDADE_RODA

        # S = roda esquerda para trás
        if keys[pygame.K_s]:
            v_left = -VELOCIDADE_RODA

        # ------------------------------------------
        # RODA DIREITA
        # ------------------------------------------

        # I = roda direita para frente
        if keys[pygame.K_i]:
            v_right = VELOCIDADE_RODA

        # K = roda direita para trás
        if keys[pygame.K_k]:
            v_right = -VELOCIDADE_RODA

        # ==========================================
        # ENVIA VELOCIDADES PARA O ROBÔ
        # ==========================================

        robot.set_wheel_velocities(
            v_left,
            v_right
        )

        # Atualiza posição e orientação
        robot.update(dt)

        # ==========================================
        # RENDERIZAÇÃO
        # ==========================================

        screen.fill(COR_FUNDO)

        robot.draw(screen)

        # ==========================================
        # PAINEL DE TELEMETRIA
        # ==========================================

        info_txt = [

            f"Pose X: {robot.x:.1f} px | "
            f"Y: {robot.y:.1f} px | "
            f"Theta: {math.degrees(robot.theta):.1f} deg",

            f"Comandos: v = {robot.v:.1f} px/s | "
            f"omega = {robot.omega:.2f} rad/s",

            "W/S = Roda Esquerda | I/K = Roda Direita",

            "W + I = Frente | W + K = Giro no proprio eixo",

            "I sozinho = Giro na roda esquerda | "
            "W sozinho = Giro na roda direita"
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
# EXECUTA O PROGRAMA
# ==========================================

if __name__ == "__main__":
    main()
