# Aula 02 — Fundamentos de Robótica Móvel

Este documento apresenta a compreensão da dupla/trio sobre os principais conceitos estudados na **Aula 02 de Robótica Móvel**.

## 1. Estado do Robô e Pose 2D

O **estado do robô** representa as informações necessárias para saber onde o robô está e qual é sua orientação.

Em um ambiente 2D, podemos representar a pose do robô por:

```text
[x, y, θ]
```

Onde:

* `x` → posição do robô no eixo X;
* `y` → posição do robô no eixo Y;
* `θ` → orientação do robô em relação ao eixo X, normalmente medida em radianos.

Por exemplo:

```text
[x, y, θ] = [300, 200, π/2]
```

Significa que o robô está na posição `(300, 200)` e está orientado a **90°**.

A pose é importante porque não basta saber apenas a posição do robô. Para controlar seu movimento, também precisamos saber **para qual direção ele está apontando**.

---

## 2. Cinemática Diferencial

A **cinemática diferencial** descreve o movimento de um robô que possui duas rodas independentes, como o robô utilizado nas atividades.

Cada roda pode possuir uma velocidade diferente:

```text
vL = velocidade da roda esquerda
vR = velocidade da roda direita
```

A partir dessas velocidades, podemos calcular a velocidade linear e angular do robô.

A velocidade linear é:

```text
v = (vR + vL) / 2
```

A velocidade angular é:

```text
ω = (vR - vL) / L
```

Onde `L` representa a distância entre as duas rodas.

### Comportamentos possíveis

Quando:

```text
vR = vL
```

as duas rodas possuem a mesma velocidade e o robô se movimenta em linha reta.

Quando:

```text
vR ≠ vL
```

o robô realiza uma curva.

Quando:

```text
vR = -vL
```

as rodas giram em sentidos opostos e o robô gira em torno do próprio eixo.

Essa relação entre as velocidades das rodas permite controlar a trajetória do robô.

---

## 3. Odometria Discreta

A **odometria** é utilizada para estimar a posição do robô a partir do movimento realizado pelas rodas.

Como o robô é atualizado em pequenos intervalos de tempo, utilizamos uma forma discreta de integração.

Considerando:

```text
x = posição no eixo X
y = posição no eixo Y
θ = orientação
v = velocidade linear
ω = velocidade angular
dt = intervalo de tempo
```

A orientação é atualizada por:

```text
θ(t + dt) = θ(t) + ω · dt
```

E as posições são atualizadas por:

```text
x(t + dt) = x(t) + v · cos(θ) · dt

y(t + dt) = y(t) + v · sin(θ) · dt
```

Dessa forma, a cada ciclo do programa o robô calcula sua nova posição com base na velocidade e na orientação atuais.

No nosso simulador, esse processo é realizado dentro da função `update(dt)`.

### Exemplo

Se o robô estiver orientado para a direita:

```text
θ = 0
```

e estiver se movimentando para frente, teremos:

```text
cos(0) = 1
sin(0) = 0
```

Portanto, o robô aumentará sua posição em `X`, enquanto `Y` permanecerá praticamente constante.

A odometria é uma estimativa, portanto erros podem se acumular ao longo do tempo devido a diferenças nas rodas, discretização e outros fatores.

---

## 4. Navegação GO-TO-GOAL

A navegação **GO-TO-GOAL** tem como objetivo fazer o robô sair de sua posição atual e chegar a um ponto de destino definido pelo usuário.

No exercício realizado, o usuário seleciona um ponto na tela utilizando o mouse.

O programa então calcula o ângulo necessário para que o robô fique orientado em direção ao destino:

```text
θdesejado = atan2(yalvo - y, xalvo - x)
```

Depois calculamos o erro de orientação:

```text
erroθ = θdesejado - θ
```

Esse erro é utilizado por um **controlador proporcional (P)**:

```text
ω = Kp · erroθ
```

Onde:

* `Kp` → ganho proporcional;
* `erroθ` → diferença entre a direção desejada e a direção atual;
* `ω` → velocidade angular utilizada para corrigir a orientação.

Assim, quanto maior for o erro de orientação, maior será a correção aplicada ao robô.

### Distância até o objetivo

Também é necessário calcular a distância entre o robô e o ponto de destino:

```text
d = √((xalvo - x)² + (yalvo - y)²)
```

Quando a distância fica menor ou igual a **10 pixels**, o robô considera que chegou ao destino e para automaticamente.

```text
se d <= 10:
    parar robô
```

### Funcionamento geral

O processo pode ser resumido da seguinte forma:

```text
Usuário escolhe o alvo
        ↓
Calcula distância até o alvo
        ↓
Calcula θ desejado
        ↓
Calcula erro de orientação
        ↓
Controlador proporcional
        ↓
Calcula velocidade angular
        ↓
Robô se movimenta
        ↓
Distância <= 10 pixels?
        ↓
      SIM → Para
```

---

## Conclusão

Os conceitos estudados estão diretamente relacionados ao funcionamento do robô implementado na atividade.

O **estado e a pose 2D** permitem representar a posição e orientação do robô. A **cinemática diferencial** relaciona as velocidades das rodas com o movimento do robô. A **odometria discreta** permite atualizar sua posição ao longo do tempo. Por fim, a navegação **GO-TO-GOAL** utiliza essas informações para fazer o robô se orientar e se deslocar automaticamente até um ponto determinado.

Com esses conceitos, conseguimos construir uma simulação de um robô móvel capaz de conhecer sua pose, movimentar-se, estimar sua trajetória e navegar até um objetivo.
