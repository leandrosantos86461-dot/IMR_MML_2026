import pygame
import math

LARGURA, ALTURA = 900, 650
FPS = 60

COR_FUNDO = (20, 24, 30)
COR_ROBO = (0, 200, 255)
COR_DIRECAO = (255, 50, 50)


class Robot:
    def __init__(self, x, y, theta=0.0):
        self.x = float(x)
        self.y = float(y)
        self.theta = float(theta)

        # Velocidade angular em rad/s
        self.omega = 0.5


    def atualizar(self, dt):
        """
        Rotação in-place.

        A posição x,y permanece fixa.
        Apenas theta é alterado.
        """
        self.theta += self.omega * dt


    def draw(self, surface):
        # Corpo do robô
        pygame.draw.circle(
            surface,
            COR_ROBO,
            (int(self.x), int(self.y)),
            30
        )

        # Indicador da orientação
        tamanho = 45

        fx = self.x + tamanho * math.cos(self.theta)
        fy = self.y + tamanho * math.sin(self.theta)

        pygame.draw.line(
            surface,
            COR_DIRECAO,
            (int(self.x), int(self.y)),
            (int(fx), int(fy)),
            5
        )


def main():

    pygame.init()

    screen = pygame.display.set_mode(
        (LARGURA, ALTURA)
    )

    pygame.display.set_caption(
        "Laboratório 2 - Rotação In-Place"
    )

    clock = pygame.time.Clock()

    font = pygame.font.SysFont(
        "monospace",
        18
    )

    # --------------------------------------------------
    # CONFIGURAÇÃO DO EXPERIMENTO
    # --------------------------------------------------

    x_inicial = 450
    y_inicial = 325

    angulo_graus = 90.0

    # rad/s
    velocidade_angular = -0.5

    angulo_desejado = -math.radians(
        angulo_graus
    )

    # t = theta / omega
    tempo_giro = abs(
        angulo_desejado /
        velocidade_angular
    )

    print("=== LABORATÓRIO 2 ===")
    print(f"Ângulo: {angulo_graus} graus")
    print(f"Ângulo: {angulo_desejado:.3f} rad")
    print(f"Velocidade angular: {velocidade_angular} rad/s")
    print(f"Tempo de giro: {tempo_giro:.3f} segundos")


    # --------------------------------------------------
    # CRIA ROBÔ
    # --------------------------------------------------

    robot = Robot(
        x_inicial,
        y_inicial,
        theta=0.0
    )

    robot.omega = velocidade_angular


    # --------------------------------------------------
    # CONTROLE DO EXPERIMENTO
    # --------------------------------------------------

    tempo_decorrido = 0.0

    executando_giro = True

    running = True

    while running:

        dt = clock.tick(FPS) / 1000.0

        # Eventos
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False


        # --------------------------------------------------
        # EXECUTA ROTAÇÃO
        # --------------------------------------------------

        if executando_giro:

            tempo_decorrido += dt

            if tempo_decorrido < tempo_giro:

                robot.atualizar(dt)

            else:

                # Garante exatamente o ângulo desejado
                robot.theta = angulo_desejado

                # Para a rotação
                robot.omega = 0.0

                executando_giro = False

                print("Rotação concluída.")
                print("Velocidade angular = 0")


        # --------------------------------------------------
        # DESENHO
        # --------------------------------------------------

        screen.fill(COR_FUNDO)

        robot.draw(screen)


        # Informações
        theta_graus = math.degrees(
            robot.theta
        )

        textos = [
            f"X: {robot.x:.1f} px",
            f"Y: {robot.y:.1f} px",
            f"Theta: {theta_graus:.1f} graus",
            f"Omega: {robot.omega:.2f} rad/s",
            f"Tempo: {min(tempo_decorrido, tempo_giro):.2f} s",
        ]


        for i, texto in enumerate(textos):

            imagem = font.render(
                texto,
                True,
                (230, 230, 230)
            )

            screen.blit(
                imagem,
                (20, 20 + i * 25)
            )


        if not executando_giro:

            texto = font.render(
                "ROTACAO CONCLUIDA",
                True,
                (0, 255, 100)
            )

            screen.blit(
                texto,
                (20, 170)
            )


        pygame.display.flip()


    pygame.quit()


if __name__ == "__main__":
    main()
