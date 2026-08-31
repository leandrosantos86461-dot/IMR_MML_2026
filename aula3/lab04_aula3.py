
import pygame
import math

LARGURA, ALTURA = 900, 650
FPS = 60
COR_FUNDO = (20, 24, 30)
COR_ROBO = (0, 200, 255)
COR_OBSTACULO = (180, 50, 50)
COR_PAREDE = (90, 90, 100)
COR_RAIO_LIVRE = (0, 255, 100)
COR_RAIO_COLISAO = (255, 200, 0)
COR_RAIO_PANICO = (255, 60, 60)

# --- Parâmetros do controle de Braitenberg ---
V_BASE = 60.0          # velocidade de cruzeiro (px/s)
GANHO_K = 90.0          # ganho da lei de desvio diferencial
EIXO_L = 24.0           # distância entre as rodas (px), usado na cinemática
DIST_PANICO = 30.0      # limiar de distância do sensor central pra giro imediato
DIST_MAX = 150.0        # alcance máximo dos sensores (D_max)


class BraitenbergRobot:
    def __init__(self, x, y, theta=0.0):
        self.x = float(x)
        self.y = float(y)
        self.theta = float(theta)
        # 3 sensores: Esquerdo, Frente, Direito
        self.sensor_angles = [-math.pi / 4, 0.0, math.pi / 4]
        self.sensor_range = DIST_MAX
        self.sensor_readings = [self.sensor_range] * 3
        self.v_l = 0.0
        self.v_r = 0.0
        self.em_panico = False

    def cast_rays(self, obstacles):
        """Mede a distância dos 3 sensores até obstáculos ou paredes."""
        leituras = []
        for beta in self.sensor_angles:
            angle = self.theta + beta
            min_dist = self.sensor_range

            for step in range(3, int(self.sensor_range), 3):
                rx = self.x + step * math.cos(angle)
                ry = self.y + step * math.sin(angle)

                if rx <= 0 or rx >= LARGURA or ry <= 0 or ry >= ALTURA:
                    min_dist = float(step)
                    break

                hit = False
                for obs in obstacles:
                    if obs.collidepoint(rx, ry):
                        min_dist = float(step)
                        hit = True
                        break
                if hit:
                    break

            leituras.append(min_dist)
        self.sensor_readings = leituras

    def _proximidade(self, dist):
        """Converte distância em proximidade normalizada [0, 1].
        Quanto mais perto do obstáculo, maior o valor."""
        prox = 1.0 - (dist / self.sensor_range)
        return max(0.0, min(prox, 1.0))

    def calcular_velocidades(self):
        """Lei de desvio diferencial de Braitenberg (veículo do 'medo'):
        sensor da DIREITA acelera a roda ESQUERDA, sensor da ESQUERDA acelera
        a roda DIREITA -> o robô sempre gira PRA LONGE do obstáculo mais próximo."""
        dist_esq, dist_frente, dist_dir = self.sensor_readings

        prox_esq = self._proximidade(dist_esq)
        prox_dir = self._proximidade(dist_dir)

        v_l = V_BASE + GANHO_K * prox_dir   # roda esquerda reage ao sensor direito
        v_r = V_BASE + GANHO_K * prox_esq   # roda direita reage ao sensor esquerdo

        self.em_panico = dist_frente < DIST_PANICO

        if self.em_panico:
            # Giro imediato no próprio eixo: inverte uma das rodas
            v_l = -V_BASE
            v_r = V_BASE

        self.v_l = v_l
        self.v_r = v_r

    def mover(self, dt):
        """Cinemática direta do robô diferencial a partir de v_L e v_R."""
        v = (self.v_r + self.v_l) / 2.0
        omega = (self.v_r - self.v_l) / EIXO_L

        self.theta += omega * dt
        self.x += v * math.cos(self.theta) * dt
        self.y += v * math.sin(self.theta) * dt

        # Segurança: mantém o robô dentro da janela mesmo em caso de erro numérico
        self.x = max(10, min(self.x, LARGURA - 10))
        self.y = max(10, min(self.y, ALTURA - 10))

    def draw(self, surface, font):
        for i, beta in enumerate(self.sensor_angles):
            angle = self.theta + beta
            dist = self.sensor_readings[i]
            rx = self.x + dist * math.cos(angle)
            ry = self.y + dist * math.sin(angle)

            if self.em_panico:
                cor = COR_RAIO_PANICO
            elif dist < self.sensor_range:
                cor = COR_RAIO_COLISAO
            else:
                cor = COR_RAIO_LIVRE

            pygame.draw.line(surface, cor, (int(self.x), int(self.y)), (int(rx), int(ry)), 2)
            pygame.draw.circle(surface, cor, (int(rx), int(ry)), 4)

        pos = (int(self.x), int(self.y))
        cor_corpo = (255, 60, 60) if self.em_panico else COR_ROBO
        pygame.draw.circle(surface, cor_corpo, pos, 16)
        fx = self.x + 24 * math.cos(self.theta)
        fy = self.y + 24 * math.sin(self.theta)
        pygame.draw.line(surface, (255, 255, 255), pos, (int(fx), int(fy)), 3)


def criar_sala_fechada():
    """Paredes internas formando uma sala fechada + obstáculos fixos."""
    espessura = 20
    paredes = [
        pygame.Rect(0, 0, LARGURA, espessura),                      # topo
        pygame.Rect(0, ALTURA - espessura, LARGURA, espessura),     # base
        pygame.Rect(0, 0, espessura, ALTURA),                       # esquerda
        pygame.Rect(LARGURA - espessura, 0, espessura, ALTURA),     # direita
    ]
    obstaculos_internos = [
        pygame.Rect(250, 120, 40, 250),
        pygame.Rect(450, 350, 220, 40),
        pygame.Rect(650, 100, 40, 200),
        pygame.Rect(150, 450, 180, 40),
        pygame.Rect(550, 500, 40, 120),
    ]
    return paredes + obstaculos_internos, paredes


def main():
    pygame.init()
    screen = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("LAB-4: Veiculo de Braitenberg (Medo Puro)")
    clock = pygame.time.Clock()
    font_hud = pygame.font.SysFont("monospace", 14)

    todos_obstaculos, paredes = criar_sala_fechada()
    robot = BraitenbergRobot(120, 100, math.pi / 6)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Navegação 100% autônoma e reativa, sem alvo e sem controle do usuário
        robot.cast_rays(todos_obstaculos)
        robot.calcular_velocidades()
        robot.mover(dt)

        screen.fill(COR_FUNDO)
        for p in paredes:
            pygame.draw.rect(screen, COR_PAREDE, p)
        for obs in todos_obstaculos[len(paredes):]:
            pygame.draw.rect(screen, COR_OBSTACULO, obs)
            pygame.draw.rect(screen, (255, 100, 100), obs, 2)

        robot.draw(screen, font_hud)

        status = "PANICO / GIRO" if robot.em_panico else "NAVEGANDO"
        linhas = [
            f"Status: {status}",
            f"v_L: {robot.v_l:6.1f}  v_R: {robot.v_r:6.1f}",
            f"Sensor Esq: {robot.sensor_readings[0]:5.1f}",
            f"Sensor Frt: {robot.sensor_readings[1]:5.1f}",
            f"Sensor Dir: {robot.sensor_readings[2]:5.1f}",
        ]
        for i, l in enumerate(linhas):
            screen.blit(font_hud.render(l, True, (220, 220, 220)), (30, 30 + i * 20))

        pygame.display.flip()
    pygame.quit()


if __name__ == "__main__":
    main()
