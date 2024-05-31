# Importando as bibliotecas necessárias
import pygame # Biblioteca para desenvolvimento de jogos
import os # Biblioteca para manipulação de arquivos
import random # Biblioteca para gerar números aleatórios
import neat # Biblioteca para implementar o NEAT

# Variáveis globais
ai_jogando = True # Define se a IA está jogando
geracao = 0  # Contador de gerações

# Definindo as dimensões da tela
TELA_LARGURA = 500
TELA_ALTURA = 800

# Carregando imagens e redimensionando-as
IMAGEM_CANO = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'pipe.png')))
IMAGEM_CHAO = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'base.png')))
IMAGEM_BACKGROUND = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bg.png')))
IMAGENS_PASSARO = [
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird1.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird2.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird3.png'))),
]

# Inicializando a fonte do PyGame
pygame.font.init()  
FONTE_PONTOS = pygame.font.SysFont('arial', 30)  # Fonte para a pontuação

# Classe que representa o pássaro
class Passaro:
    IMGS = IMAGENS_PASSARO  # Imagens do pássaro
    ROTACAO_MAXIMA = 25  # Ângulo máximo de rotação
    VELOCIDADE_ROTACAO = 20  # Velocidade de rotação
    TEMPO_ANIMACAO = 5  # Tempo de animação entre imagens

    def __init__(self, x, y):
        self.x = x  # Posição x inicial do pássaro
        self.y = y  # Posição y inicial do pássaro
        self.angulo = 0  # Ângulo inicial do pássaro
        self.velocidade = 0  # Velocidade inicial do pássaro
        self.altura = self.y  # Altura inicial
        self.tempo = 0  # Tempo de movimento
        self.contagem_imagem = 0  # Contador para animação das imagens
        self.imagem = self.IMGS[0]  # Imagem inicial do pássaro

    def pular(self):
        self.velocidade = -10.5  # Velocidade para pular
        self.tempo = 0  # Reseta o tempo de movimento
        self.altura = self.y  # Define a nova altura

    def mover(self):
        self.tempo += 1  # Incrementa o tempo de movimento
        deslocamento = 1.5 * (self.tempo**2) + self.velocidade * self.tempo  # Calcula o deslocamento

        if deslocamento > 16:
            deslocamento = 16  # Limita o deslocamento máximo
        elif deslocamento < 0:
            deslocamento -= 2  # Ajusta o deslocamento para cima

        self.y += deslocamento  # Atualiza a posição y do pássaro

        if deslocamento < 0 or self.y < (self.altura + 50):
            if self.angulo < self.ROTACAO_MAXIMA:
                self.angulo = self.ROTACAO_MAXIMA  # Ajusta o ângulo ao subir
        else:
            if self.angulo > -90:
                self.angulo -= self.VELOCIDADE_ROTACAO  # Ajusta o ângulo ao descer

    def desenhar(self, tela):
        self.contagem_imagem += 1  # Incrementa o contador de animação

        # Alterna as imagens para animação do pássaro batendo asas
        if self.contagem_imagem < self.TEMPO_ANIMACAO:
            self.imagem = self.IMGS[0]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO*2:
            self.imagem = self.IMGS[1]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO*3:
            self.imagem = self.IMGS[2]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO*4:
            self.imagem = self.IMGS[1]
        elif self.contagem_imagem >= self.TEMPO_ANIMACAO*4 + 1:
            self.imagem = self.IMGS[0]
            self.contagem_imagem = 0

        # Se o pássaro estiver caindo, não bate as asas
        if self.angulo <= -80:
            self.imagem = self.IMGS[1]
            self.contagem_imagem = self.TEMPO_ANIMACAO*2

        # Desenha a imagem rotacionada
        imagem_rotacionada = pygame.transform.rotate(self.imagem, self.angulo)
        pos_centro_imagem = self.imagem.get_rect(topleft=(self.x, self.y)).center
        retangulo = imagem_rotacionada.get_rect(center=pos_centro_imagem)
        tela.blit(imagem_rotacionada, retangulo.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.imagem)  # Retorna a máscara para detecção de colisões

# Classe que representa o cano
class Cano:
    DISTANCIA = 170  # Distância entre os canos
    VELOCIDADE = 8  # Velocidade de movimento dos canos

    def __init__(self, x):
        self.x = x  # Posição x inicial do cano
        self.altura = 0  # Altura inicial do cano
        self.pos_topo = 0  # Posição y do topo do cano
        self.pos_base = 0  # Posição y da base do cano
        self.CANO_TOPO = pygame.transform.flip(IMAGEM_CANO, False, True)  # Imagem do cano de cabeça para baixo
        self.CANO_BASE = IMAGEM_CANO  # Imagem do cano normal
        self.passou = False  # Indica se o pássaro passou pelo cano
        self.definir_altura()  # Define a altura do cano

    def definir_altura(self):
        self.altura = random.randrange(50, 450)  # Define uma altura aleatória para o cano
        self.pos_topo = self.altura - self.CANO_TOPO.get_height()  # Calcula a posição do topo do cano
        self.pos_base = self.altura + self.DISTANCIA  # Calcula a posição da base do cano

    def mover(self):
        self.x -= self.VELOCIDADE  # Move o cano para a esquerda

    def desenhar(self, tela):
        tela.blit(self.CANO_TOPO, (self.x, self.pos_topo))  # Desenha o cano de cabeça para baixo
        tela.blit(self.CANO_BASE, (self.x, self.pos_base))  # Desenha o cano normal

    def colidir(self, passaro):
        passaro_mask = passaro.get_mask()  # Obtém a máscara do pássaro
        topo_mask = pygame.mask.from_surface(self.CANO_TOPO)  # Obtém a máscara do topo do cano
        base_mask = pygame.mask.from_surface(self.CANO_BASE)  # Obtém a máscara da base do cano

        distancia_topo = (self.x - passaro.x, self.pos_topo - round(passaro.y))  # Calcula a distância até o topo do cano
        distancia_base = (self.x - passaro.x, self.pos_base - round(passaro.y))  # Calcula a distância até a base do cano

        topo_ponto = passaro_mask.overlap(topo_mask, distancia_topo)  # Verifica colisão com o topo do cano
        base_ponto = passaro_mask.overlap(base_mask, distancia_base)  # Verifica colisão com a base do cano

        return base_ponto or topo_ponto  # Retorna se houve colisão

# Classe que representa o chão
class Chao:
    VELOCIDADE = 5  # Velocidade de movimento do chão
    LARGURA = IMAGEM_CHAO.get_width()  # Largura da imagem do chão
    IMAGEM = IMAGEM_CHAO  # Imagem do chão

    def __init__(self, y):
        self.y = y  # Posição y inicial do chão
        self.x1 = 0  # Posição x do primeiro segmento do chão
        self.x2 = self.LARGURA  # Posição x do segundo segmento do chão

    def mover(self):
        self.x1 -= self.VELOCIDADE  # Move o primeiro segmento para a esquerda
        self.x2 -= self.VELOCIDADE  # Move o segundo segmento para a esquerda

        if self.x1 + self.LARGURA < 0:
            self.x1 = self.x2 + self.LARGURA  # Reposiciona o primeiro segmento se sair da tela
        if self.x2 + self.LARGURA < 0:
            self.x2 = self.x1 + self.LARGURA  # Reposiciona o segundo segmento se sair da tela

    def desenhar(self, tela):
        tela.blit(self.IMAGEM, (self.x1, self.y))  # Desenha o primeiro segmento do chão
        tela.blit(self.IMAGEM, (self.x2, self.y))  # Desenha o segundo segmento do chão

# Função para desenhar a tela do jogo
def desenhar_tela(tela, passaros, canos, chao, pontos):
    tela.blit(IMAGEM_BACKGROUND, (0, 0))  # Desenha o fundo

    for passaro in passaros:
        passaro.desenhar(tela)  # Desenha cada pássaro

    for cano in canos:
        cano.desenhar(tela)  # Desenha cada cano

    texto = FONTE_PONTOS.render(f"Pontuação: {pontos}", 1, (255, 255, 255))  # Renderiza a pontuação
    tela.blit(texto, (TELA_LARGURA - 10 - texto.get_width(), 10))  # Desenha a pontuação na tela

    if ai_jogando:
        texto = FONTE_PONTOS.render(f"Geração: {geracao}", 1, (255, 255, 255))  # Renderiza a geração
        texto2 = FONTE_PONTOS.render(f"Passaros: {len(passaros)}", 1, (255, 255, 255))  # Renderiza o número de pássaros
        tela.blit(texto, (10, 10))  # Desenha a geração na tela
        tela.blit(texto2, (10, 50))  # Desenha o número de pássaros na tela

    chao.desenhar(tela)  # Desenha o chão
    pygame.display.update()  # Atualiza a tela

# Função principal do jogo
def main(genomas, config):
    global geracao # Define a variável global geracao
    geracao += 1  # Incrementa a geração

    if ai_jogando: # Se a IA estiver jogando
        redes = [] # Lista de redes neurais
        lista_genomas = [] # Lista de genomas
        passaros = [] # Lista de pássaros

        for _, genoma in genomas: # Para cada genoma
            rede = neat.nn.FeedForwardNetwork.create(genoma, config)  # Cria a rede neural 
            redes.append(rede) # Adiciona a rede à lista
            genoma.fitness = 0 # Inicializa a fitness
            lista_genomas.append(genoma) # Adiciona o genoma à lista
            passaros.append(Passaro(230, 350)) # Adiciona um pássaro à lista

    else:
        passaros = [Passaro(230, 350)] 

    chao = Chao(730)  # Cria o chão
    canos = [Cano(600)]  # Cria os canos
    tela = pygame.display.set_mode((TELA_LARGURA, TELA_ALTURA))  # Define as dimensões da tela
    pontos = 0  # Inicializa a pontuação
    relogio = pygame.time.Clock()  # Cria um relógio para controlar o FPS

    rodando = True
    while rodando:
        relogio.tick(30)  # Define o FPS
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
                pygame.quit()
                quit()
            if not ai_jogando: # Se a IA não estiver jogando
                if evento.type ==  pygame.KEYDOWN: # Se uma tecla for pressionada
                    if evento.key == pygame.K_SPACE: # Se a tecla for a barra de espaço
                        for passaro in passaros: # Para cada pássaro
                            passaro.pular() # O pássaro pula

        indice_cano = 0  
        if len(passaros) > 0:
            if len(canos) > 1 and passaros[0].x > (canos[0].x + canos[0].CANO_TOPO.get_width()):
                indice_cano = 1
        else:
            rodando = False
            break

        for i, passaro in enumerate(passaros):
            passaro.mover()
            if ai_jogando:
                lista_genomas[i].fitness += 0.1
                output = redes[i].activate((passaro.y, abs(passaro.y - canos[indice_cano].altura), abs(passaro.y - canos[indice_cano].pos_base)))
                if output[0] > 0.5:
                    passaro.pular()

        chao.mover()
        adicionar_cano = False
        remover_canos = []

        for cano in canos:
            for i, passaro in enumerate(passaros):
                if cano.colidir(passaro):
                    passaros.pop(i)
                    if ai_jogando:
                        lista_genomas[i].fitness -= 1
                        lista_genomas.pop(i)
                        redes.pop(i)

                if not cano.passou and passaro.x > cano.x:
                    cano.passou = True
                    adicionar_cano = True

            cano.mover()
            if cano.x + cano.CANO_TOPO.get_width() < 0:
                remover_canos.append(cano)

        if adicionar_cano:# Se o pássaro passou pelo cano
            pontos += 1  # Incrementa a pontuação
            canos.append(Cano(600)) # Adiciona um novo cano
            if ai_jogando: # Se a IA estiver jogando
                for genoma in lista_genomas: # Para cada genoma
                    genoma.fitness += 5 # Incrementa a fitness

        for cano in remover_canos:
            canos.remove(cano)

        for i, passaro in enumerate(passaros): # Para cada pássaro
            if (passaro.y + passaro.imagem.get_height()) > chao.y or passaro.y < 0: # Se o pássaro colidir com o chão ou o teto
                passaros.pop(i) # Remove o pássaro
                if ai_jogando: # Se a IA estiver jogando
                    lista_genomas.pop(i) # Remove o genoma
                    redes.pop(i) # Remove a rede

        desenhar_tela(tela, passaros, canos, chao, pontos)
# Função para rodar a IA com o NEAT
def rodar(caminho_config):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, caminho_config) # Carrega o arquivo de configuração

    populacao = neat.Population(config) # Cria a população
    populacao.add_reporter(neat.StdOutReporter(True)) # Adiciona um reporter
    populacao.add_reporter(neat.StatisticsReporter()) # Adiciona um reporter

    if ai_jogando:
        populacao.run(main, 50) # Roda a população, main é a função principal, 50 é o número de gerações
    else:
        main(None, None) # Roda o jogo normalmente

# Função principal
if __name__ == '__main__':
    caminho_config = 'config.txt' # Define o caminho do arquivo de configuração
    rodar(caminho_config) # Roda a IA com o NEAT
