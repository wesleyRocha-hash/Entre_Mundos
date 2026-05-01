# 🌍 Entre Mundos - RPG Ultimate

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Pygame](https://img.shields.io/badge/pygame-black?style=for-the-badge&logo=python&logoColor=white)

**Entre Mundos** é um jogo de plataforma e ação RPG com geração procedural de níveis, sistema de classes, inventário, chefes épicos e dificuldade escalável, desenvolvido inteiramente em Python utilizando a biblioteca Pygame.

---

## 📖 A História

Desde o princípio dos tempos, o equilíbrio do universo era mantido por quatro pilares fundamentais, cada um isolado em sua própria dimensão. No entanto, uma força sombria fraturou os selos que separavam essas realidades, criando anomalias dimensionais e espalhando armadilhas mortais por toda parte. Agora, as barreiras entre as dimensões caíram, e o caos ameaça engolir tudo em *Entre Mundos*.

Apenas a lendária Liga dos Heróis pode restaurar a ordem. Você deve assumir o manto de um campeão e atravessar os perigosos portais dimensionais. Sua missão é sobreviver às hordas de inimigos, desviar de armadilhas mortais e recuperar relíquias de poder imensurável, como o místico Selo do Abismo e a lendária Coroa dos Deuses, para reerguer as fronteiras da realidade.

---

## ✨ Funcionalidades

* **Geração Procedural:** Plataformas, armadilhas, inimigos e decorações são gerados dinamicamente, garantindo que cada run seja única.
* **Sistema de Progressão (RPG):** Ganhe XP derrotando inimigos para subir de nível, aumentando seu HP máximo e Dano base.
* **Inventário e Loot:** Encontre poções para curar, livros de XP e anéis mágicos para aumentar permanentemente seus atributos.
* **4 Biomas Distintos:** Viaje pela Floresta, Masmorra (Caverna), Vulcão e Tempestade (Elétrico), cada um com suas próprias armadilhas de bioma (espinhos, estalactites, gêiseres e raios).
* **Batalhas contra Chefes:** Enfrente guardiões colossais a cada 4 níveis (Ent Ancião, Golias de Cristal, Senhor das Cinzas, Arcano Supremo).
* **Tábua de Glória:** Sistema de Ranking local que salva as maiores pontuações em um arquivo `save_data.json`.
* **4 Dificuldades:** Fácil, Normal, Difícil e Pesadelo, ajustando a vida, velocidade e dano dos inimigos.

---

## ⚔️ As Classes

Escolha o herói que melhor se adapta ao seu estilo de jogo:

* 🛡️ **Cavaleiro (Warrior):** Muita vida e dano corpo-a-corpo. **Especial:** *Impacto Meteoro* (Esmaga o chão causando dano em área).
* 🔮 **Mago (Mage):** Baixa vida, mas ataca à distância com magia. **Especial:** *Singularidade Arcana* (Esfera teleguiada e perfurante de alto dano).
* 🏹 **Arqueiro (Rogue):** Muito rápido e com alta chance de dano crítico. **Especial:** *Tempestade Esmeralda* (Dispara rajadas de vento em múltiplas direções).

---

## 🎮 Controles

| Ação | Tecla |
| :--- | :--- |
| **Movimento** | `Setas Direcionais` ou `A` / `D` |
| **Pulo** | `Seta Cima`, `W` ou `Espaço` *(Suporta Pulo Duplo)* |
| **Agachar** | `Seta Baixo` ou `S` |
| **Ataque Básico** | `Botão Esquerdo do Mouse` (Mira com o cursor) |
| **Ataque Especial**| `Botão Direito do Mouse` (Possui tempo de recarga) |
| **Inventário** | `I` ou `E` |
| **Pausar** | `P` ou `ESC` |

> **Dica:** O Inventário possui um modo "Lixeira" que permite descartar itens para liberar espaço para loots melhores!

---

## 🛠️ Tecnologias Utilizadas
* Python
* Pygame

## 🚀 Como Executar
1. Clone o repositório: `git clone https://github.com/wesleyRocha-hash/Entre_Mundos.git`
2. Instale as dependências: `pip install pygame`
3. Execute o jogo: `py main.py` 
