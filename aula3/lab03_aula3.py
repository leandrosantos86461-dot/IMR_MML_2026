import pygame
import math
import numpy as np

LARGURA, ALTURA = 900, 650
FPS = 60
COR_FUNDO = (20, 24, 30)
COR_ROBO = (0, 200, 255)
COR_OBSTACULO = (180, 50, 50)
COR_RAIO_LIVRE = (0, 255, 100)
COR_RAIO_COLISAO = (255, 200, 0)

# Parâmetros do ruído gaussiano
RUIDO_MEDIA = 0.0
RUIDO_DESVIO = 2.0


class SensorArrayRobot:
    def __init__(self, x, y, theta=0.0):
        self.x = float(x)
        self.y = float(y)
        self.theta = float(theta)
        # 5 feixes: -90°, -45°, 0°, 45°, 90° (em relação à frente do robô)
        self.sensor_angles = [-math.pi / 2, -math.pi / 4, 0.0, math.pi / 4, math.pi / 2]
        self.sensor_labels = ["Esq90", "Esq45", "Frente", "Dir45", "Dir90"]
        self.sensor_range = 200.0
        self.sensor_readings = [self.sensor_range] * 5  # com ruído
        self.sensor_readings_raw = [self.sensor_range] * 5  # sem ruído, usado pra desenhar o raio

    def cast_rays(self, obstacles):
        """Calcula colisão dos 5 feixes com obstáculos retangulares e bordas da janela,
        depois aplica ruído gaussiano na leitura reportada."""
        leituras_raw = []
        for beta in self.sensor_angles:
            angle = self.theta + beta
            min_dist = self.sensor_range

            for step in range(5, int(self.sensor_range), 4):
                rx = self.x + step * math.cos(angle)
                ry = self.y + step * math.sin(angle)

                # Colisão com as paredes externas da janela
                if rx <= 0 or rx >= LARGURA or ry <= 0 or ry >= ALTURA:
                    min_dist = float(step)
                    break

                # Colisão com múltiplos retângulos de obstáculos
                hit = False
                for obs in obstacles:
                    if obs.collidepoint(rx, ry):
                        min_dist = float(step)
                        hit = True
                        break
                if hit:
                    break

            leituras_raw.append(min_dist)

        self.sensor_readings_raw = leituras_raw

        # Aplica ruído gaussiano simulado na medição reportada (não no raio desenhado)
        leituras_com_ruido = []
        for dist in leituras_raw:
            ruido = np.random.normal(RUIDO_MEDIA, RUIDO_DESVIO)
            dist_ruidosa = dist + ruido
            dist_ruidosa = max(0.0, min(dist_ruidosa, self.sensor_range))
            leituras_com_ruido.append(dist_ruidosa)

        self.sensor_readings = leituras_com_ruido

    def draw(self, surface, font):
        for i, beta in enumerate(self.sensor_angles):
            angle = self.theta + beta
            dist_raw = self.sensor_readings_raw[i]
            dist_ruido = self.sensor_readings[i]

            rx = self.x + dist_raw * math.cos(angle)
            ry = self.y + dist_raw * math.sin(angle)
            cor = COR_RAIO_COLISAO if dist_raw < self.sensor_range else COR_RAIO_LIVRE

            pygame.draw.line(surface, cor, (int(self.x), int(self.y)), (int(rx), int(ry)), 2)
            pygame.draw.circle(surface, cor, (int(rx), int(ry)), 4)

            # Renderiza o valor da leitura (com ruído) ao lado da ponta do raio
            texto = font.render(f"{dist_ruido:.1f}", True, (255, 255, 255))
            surface.blit(texto, (int(rx) + 6, int(ry) - 6))

        pos = (int(self.x), int(self.y))
        pygame.draw.circle(surface, COR_ROBO, pos, 16)
        fx = self.x + 24 * math.cos(self.theta)
        fy = self.y + 24 * math.sin(self.theta)
        pygame.draw.line(surface, (255, 50, 50), pos, (int(fx), int(fy)), 3)


def main():
    pygame.init()
    screen = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("LAB-3: Percepção com Múltiplos Sensores de Feixe")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("monospace", 14)
    font_hud = pygame.font.SysFont("monospace", 14)

    robot = SensorArrayRobot(150, 300, 0.0)
    obstacles = [
        pygame.Rect(350, 150, 100, 350),
        pygame.Rect(600, 100, 150, 100),
        pygame.Rect(600, 400, 150, 150),
        pygame.Rect(150, 500, 120, 80),
    ]

    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Robô segue a posição do mouse para demonstrar a varredura sensorial
        mx, my = pygame.mouse.get_pos()
        dx, dy = mx - robot.x, my - robot.y
        robot.theta = math.atan2(dy, dx)
        robot.x += dx * 0.03
        robot.y += dy * 0.03

        robot.cast_rays(obstacles)

        screen.fill(COR_FUNDO)
        for obs in obstacles:
            pygame.draw.rect(screen, COR_OBSTACULO, obs)
            pygame.draw.rect(screen, (255, 100, 100), obs, 2)

        robot.draw(screen, font)

        leituras = [
            f"{robot.sensor_labels[i]}: {dist:6.1f} px"
            for i, dist in enumerate(robot.sensor_readings)
        ]
        for i, l in enumerate(leituras):
            screen.blit(font_hud.render(l, True, (220, 220, 220)), (20, 20 + i * 20))
        screen.blit(
            font_hud.render(
                "Mova o mouse para testar a detecção dos 5 sensores (ruido gaussiano ativo).",
                True,
                (255, 215, 0),
            ),
            (20, 130),
        )

        pygame.display.flip()
    pygame.quit()


if __name__ == "__main__":
    main()
