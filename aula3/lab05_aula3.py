import pygame
import math
import numpy as np

# ============================================================
# CONFIGURAÇÕES DA SIMULAÇÃO
# ============================================================

LARGURA, ALTURA = 900, 650
FPS = 60

COR_FUNDO = (20, 24, 30)
COR_ROBO = (0, 200, 255)
COR_ROBO_CONTORNO = (100, 230, 255)
COR_OBSTACULO = (180, 50, 50)
COR_OBSTACULO_BORDA = (255, 100, 100)

COR_RAIO_LIVRE = (0, 255, 100)
COR_RAIO_COLISAO = (255, 200, 0)

COR_ALVO = (255, 255, 255)
COR_TEXTO = (230, 230, 230)

# ============================================================
# PARÂMETROS DO ROBÔ
# ============================================================

RAIO_ROBO = 16

# Cinco sensores: esquerda, diagonal esquerda,
# frente, diagonal direita e direita
ANGULOS_SENSORES = [
    -math.pi / 2,
    -math.pi / 4,
    0.0,
    math.pi / 4,
    math.pi / 2
]

ALCANCE_SENSOR = 150.0

# Distância que ativa o modo de emergência
DISTANCIA_EMERGENCIA = 50.0

# Distância para considerar o objetivo atingido
DISTANCIA_ALVO = 15.0

# Velocidade linear máxima
VELOCIDADE_MAX = 2.5

# Ganho proporcional de orientação
K_ANGULAR = 2.5

# Ganho do torque repulsivo
K_REPULSAO = 2.0

# Velocidade angular máxima
OMEGA_MAX = 0.12


# ============================================================
# CLASSE DO ROBÔ
# ============================================================

class Robot:
    def __init__(self, x, y, theta=0.0):
        self.x = float(x)
        self.y = float(y)
        self.theta = float(theta)

        self.sensor_readings = [
            ALCANCE_SENSOR
        ] * len(ANGULOS_SENSORES)

        self.modo = "GO-TO-GOAL"
        self.alvo = None
        self.chegou = False

    # --------------------------------------------------------
    # NORMALIZAÇÃO DE ÂNGULO
    # --------------------------------------------------------

    def normalizar_angulo(self, angulo):
        """
        Mantém o ângulo no intervalo [-pi, pi].
        """
        return (angulo + math.pi) % (2 * math.pi) - math.pi

    # --------------------------------------------------------
    # RAYCASTING
    # --------------------------------------------------------

    def cast_rays(self, obstacles):
        """
        Calcula a distância entre o robô e o primeiro obstáculo
        encontrado por cada sensor.

        São consideradas:
        - paredes externas da janela;
        - obstáculos retangulares;
        - alcance máximo do sensor.
        """

        self.sensor_readings = []

        for beta in ANGULOS_SENSORES:

            angle = self.theta + beta

            min_dist = ALCANCE_SENSOR

            # Amostragem do raio
            for step in np.arange(2, ALCANCE_SENSOR + 1, 2):

                rx = self.x + step * math.cos(angle)
                ry = self.y + step * math.sin(angle)

                # --------------------------------------------
                # PAREDES DA JANELA
                # --------------------------------------------

                if (
                    rx <= 0
                    or rx >= LARGURA
                    or ry <= 0
                    or ry >= ALTURA
                ):
                    min_dist = float(step)
                    break

                # --------------------------------------------
                # OBSTÁCULOS
                # --------------------------------------------

                ponto = (int(rx), int(ry))

                colisao = False

                for obs in obstacles:
                    if obs.collidepoint(ponto):
                        min_dist = float(step)
                        colisao = True
                        break

                if colisao:
                    break

            self.sensor_readings.append(min_dist)

    # --------------------------------------------------------
    # CÁLCULO DO CONTROLE GO-TO-GOAL
    # --------------------------------------------------------

    def controle_go_to_goal(self):

        if self.alvo is None:
            return 0.0, 0.0

        dx = self.alvo[0] - self.x
        dy = self.alvo[1] - self.y

        distancia = math.hypot(dx, dy)

        # ----------------------------------------------------
        # VERIFICA SE CHEGOU AO ALVO
        # ----------------------------------------------------

        if distancia <= DISTANCIA_ALVO:
            self.chegou = True
            return 0.0, 0.0

        self.chegou = False

        # Direção desejada
        theta_desejado = math.atan2(dy, dx)

        # Erro angular
        erro = self.normalizar_angulo(
            theta_desejado - self.theta
        )

        # Controle proporcional angular
        omega = K_ANGULAR * erro

        # Limitação da velocidade angular
        omega = max(
            -OMEGA_MAX,
            min(OMEGA_MAX, omega)
        )

        # Velocidade linear proporcional à distância
        v = min(
            VELOCIDADE_MAX,
            0.025 * distancia
        )

        return v, omega

    # --------------------------------------------------------
    # CONTROLE REPULSIVO
    # --------------------------------------------------------

    def controle_desvio(self):

        """
        Calcula um torque repulsivo utilizando os cinco sensores.

        Obstáculos à esquerda produzem uma rotação para a direita.
        Obstáculos à direita produzem uma rotação para a esquerda.

        O sensor frontal possui maior influência.
        """

        omega_repulsivo = 0.0

        # Pesos dos sensores
        pesos = [
            1.0,   # esquerda
            1.5,   # diagonal esquerda
            2.5,   # frente
            1.5,   # diagonal direita
            1.0    # direita
        ]

        for i, distancia in enumerate(self.sensor_readings):

            if distancia < DISTANCIA_EMERGENCIA:

                # Proximidade normalizada
                proximidade = (
                    DISTANCIA_EMERGENCIA - distancia
                ) / DISTANCIA_EMERGENCIA

                # ------------------------------------------------
                # Sensores da esquerda:
                # girar para a direita
                # ------------------------------------------------

                if i in [0, 1]:
                    omega_repulsivo += (
                        K_REPULSAO
                        * proximidade
                        * pesos[i]
                    )

                # ------------------------------------------------
                # Sensor frontal:
                # escolhe o lado de escape
                # ------------------------------------------------

                elif i == 2:

                    # Compara os sensores laterais
                    esquerda = self.sensor_readings[1]
                    direita = self.sensor_readings[3]

                    if esquerda < direita:
                        omega_repulsivo += (
                            K_REPULSAO
                            * proximidade
                            * pesos[i]
                        )
                    else:
                        omega_repulsivo -= (
                            K_REPULSAO
                            * proximidade
                            * pesos[i]
                        )

                # ------------------------------------------------
                # Sensores da direita:
                # girar para a esquerda
                # ------------------------------------------------

                elif i in [3, 4]:
                    omega_repulsivo -= (
                        K_REPULSAO
                        * proximidade
                        * pesos[i]
                    )

        # Limita a velocidade angular
        omega_repulsivo = max(
            -OMEGA_MAX,
            min(OMEGA_MAX, omega_repulsivo)
        )

        # Durante o desvio, mantém pequena velocidade
        # para frente
        v = 1.0

        return v, omega_repulsivo

    # --------------------------------------------------------
    # ATUALIZAÇÃO DO ROBÔ
    # --------------------------------------------------------

    def update(self, obstacles):

        # Atualiza sensores
        self.cast_rays(obstacles)

        # ----------------------------------------------------
        # VERIFICAÇÃO DE EMERGÊNCIA
        # ----------------------------------------------------

        menor_distancia = min(self.sensor_readings)

        if menor_distancia < DISTANCIA_EMERGENCIA:

            self.modo = "DESVIO DE EMERGENCIA"

            v, omega = self.controle_desvio()

        else:

            self.modo = "GO-TO-GOAL"

            v, omega = self.controle_go_to_goal()

        # ----------------------------------------------------
        # ATUALIZA CINEMÁTICA
        # ----------------------------------------------------

        if not self.chegou:

            self.theta += omega

            self.theta = self.normalizar_angulo(
                self.theta
            )

            self.x += v * math.cos(self.theta)
            self.y += v * math.sin(self.theta)

        # ----------------------------------------------------
        # LIMITAÇÃO DENTRO DA JANELA
        # ----------------------------------------------------

        self.x = max(
            RAIO_ROBO,
            min(LARGURA - RAIO_ROBO, self.x)
        )

        self.y = max(
            RAIO_ROBO,
            min(ALTURA - RAIO_ROBO, self.y)
        )

    # --------------------------------------------------------
    # DESENHO
    # --------------------------------------------------------

    def draw(self, surface, font):

        # ----------------------------------------------------
        # DESENHA SENSORES
        # ----------------------------------------------------

        for i, beta in enumerate(ANGULOS_SENSORES):

            angle = self.theta + beta

            distancia = self.sensor_readings[i]

            rx = (
                self.x
                + distancia * math.cos(angle)
            )

            ry = (
                self.y
                + distancia * math.sin(angle)
            )

            if distancia < DISTANCIA_EMERGENCIA:
                cor = COR_RAIO_COLISAO
            else:
                cor = COR_RAIO_LIVRE

            pygame.draw.line(
                surface,
                cor,
                (int(self.x), int(self.y)),
                (int(rx), int(ry)),
                2
            )

            pygame.draw.circle(
                surface,
                cor,
                (int(rx), int(ry)),
                4
            )

            # Texto da leitura
            texto = font.render(
                f"{distancia:5.1f}",
                True,
                cor
            )

            tx = int(rx) + 5
            ty = int(ry) - 8

            surface.blit(
                texto,
                (tx, ty)
            )

        # ----------------------------------------------------
        # CORPO DO ROBÔ
        # ----------------------------------------------------

        pos = (
            int(self.x),
            int(self.y)
        )

        pygame.draw.circle(
            surface,
            COR_ROBO,
            pos,
            RAIO_ROBO
        )

        pygame.draw.circle(
            surface,
            COR_ROBO_CONTORNO,
            pos,
            RAIO_ROBO,
            2
        )

        # ----------------------------------------------------
        # DIREÇÃO DO ROBÔ
        # ----------------------------------------------------

        fx = (
            self.x
            + 25 * math.cos(self.theta)
        )

        fy = (
            self.y
            + 25 * math.sin(self.theta)
        )

        pygame.draw.line(
            surface,
            (255, 50, 50),
            pos,
            (int(fx), int(fy)),
            3
        )


# ============================================================
# FUNÇÃO PRINCIPAL
# ============================================================

def main():

    pygame.init()

    screen = pygame.display.set_mode(
        (LARGURA, ALTURA)
    )

    pygame.display.set_caption(
        "LAB-5 - Go-to-Goal com Desvio Reativo"
    )

    clock = pygame.time.Clock()

    font = pygame.font.SysFont(
        "monospace",
        14
    )

    font_grande = pygame.font.SysFont(
        "monospace",
        18,
        bold=True
    )

    # --------------------------------------------------------
    # CRIA ROBÔ
    # --------------------------------------------------------

    robot = Robot(
        120,
        325,
        0.0
    )

    # --------------------------------------------------------
    # OBSTÁCULOS
    # --------------------------------------------------------

    obstacles = [

        pygame.Rect(
            300, 100,
            80, 350
        ),

        pygame.Rect(
            500, 50,
            100, 180
        ),

        pygame.Rect(
            500, 400,
            100, 180
        ),

        pygame.Rect(
            700, 180,
            120, 100
        ),

        pygame.Rect(
            700, 420,
            120, 100
        )
    ]

    running = True

    while running:

        clock.tick(FPS)

        # ====================================================
        # EVENTOS
        # ====================================================

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            # ------------------------------------------------
            # CLIQUE DO MOUSE = NOVO ALVO
            # ------------------------------------------------

            elif event.type == pygame.MOUSEBUTTONDOWN:

                if event.button == 1:

                    robot.alvo = event.pos
                    robot.chegou = False

        # ====================================================
        # ATUALIZA ROBÔ
        # ====================================================

        robot.update(obstacles)

        # ====================================================
        # DESENHA FUNDO
        # ====================================================

        screen.fill(COR_FUNDO)

        # ====================================================
        # DESENHA OBSTÁCULOS
        # ====================================================

        for obs in obstacles:

            pygame.draw.rect(
                screen,
                COR_OBSTACULO,
                obs
            )

            pygame.draw.rect(
                screen,
                COR_OBSTACULO_BORDA,
                obs,
                2
            )

        # ====================================================
        # DESENHA ALVO
        # ====================================================

        if robot.alvo is not None:

            alvo_x, alvo_y = robot.alvo

            pygame.draw.circle(
                screen,
                COR_ALVO,
                (int(alvo_x), int(alvo_y)),
                10,
                2
            )

            pygame.draw.line(
                screen,
                COR_ALVO,
                (int(alvo_x) - 15, int(alvo_y)),
                (int(alvo_x) + 15, int(alvo_y)),
                1
            )

            pygame.draw.line(
                screen,
                COR_ALVO,
                (int(alvo_x), int(alvo_y) - 15),
                (int(alvo_x), int(alvo_y) + 15),
                1
            )

        # ====================================================
        # DESENHA ROBÔ
        # ====================================================

        robot.draw(
            screen,
            font
        )

        # ====================================================
        # PAINEL DE INFORMAÇÕES
        # ====================================================

        menor_distancia = min(
            robot.sensor_readings
        )

        texto_modo = font_grande.render(
            f"Modo: {robot.modo}",
            True,
            (
                255,
                200,
                0
            )
            if "DESVIO" in robot.modo
            else (
                0,
                255,
                150
            )
        )

        screen.blit(
            texto_modo,
            (20, 20)
        )

        texto_dist = font.render(
            f"Menor leitura: {menor_distancia:.1f} px",
            True,
            COR_TEXTO
        )

        screen.blit(
            texto_dist,
            (20, 50)
        )

        if robot.alvo is None:

            mensagem = (
                "Clique com o mouse para definir o alvo."
            )

        elif robot.chegou:

            mensagem = (
                "ALVO ALCANCADO!"
            )

        else:

            mensagem = (
                "Perseguindo alvo - "
                "desvio automatico de obstaculos."
            )

        screen.blit(
            font.render(
                mensagem,
                True,
                COR_TEXTO
            ),
            (20, 75)
        )

        # ----------------------------------------------------
        # LEITURAS DOS CINCO SENSORES
        # ----------------------------------------------------

        nomes = [
            "Esq",
            "Diag Esq",
            "Frente",
            "Diag Dir",
            "Dir"
        ]

        for i, distancia in enumerate(
            robot.sensor_readings
        ):

            texto = font.render(
                f"{nomes[i]:9s}: {distancia:6.1f} px",
                True,
                COR_TEXTO
            )

            screen.blit(
                texto,
                (
                    20,
                    110 + i * 20
                )
            )

        # ====================================================
        # ATUALIZA TELA
        # ====================================================

        pygame.display.flip()

    pygame.quit()


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":
    main()
