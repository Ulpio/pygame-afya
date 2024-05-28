import pygame
import os
import random
# Variaveis globais
tela_largura = 500
tela_altura = 800

img_cano = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs','pipe.png')))
img_chao = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs','base.png')))
img_bg = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs','bg.png')))
imgs_passaro = [
  pygame.transform.scale2x(pygame.image.load(os.path.join('imgs','bird1.png'))),
  pygame.transform.scale2x(pygame.image.load(os.path.join('imgs','bird2.png'))),
  pygame.transform.scale2x(pygame.image.load(os.path.join('imgs','bird3.png')))
]

pygame.font.init()
fonte_global = pygame.font.SysFont('arial',35)

class Passaro:
  IMGS = imgs_passaro
  rotacao_max = 25
  velocidade_rotacao = 20
  tempo_animacao = 5

  def __init__(self,x,y):
    self.x = x
    self.y = y
    self.angulo = 0
    self.velocidade = 0
    self.altura = y
    self.tempo = 0
    self.contagem_imagem = 0
    self.imagem = self.IMGS[0]

  def pular(self):
    self.velocidade = -10.5
    self.altura = self.y

  def mover(self):
    self.tempo +=1
    deslocamento = 1.5 * (self.tempo**2) + self.velocidade * self.tempo

    if deslocamento > 16:
      deslocamento = 16
    elif deslocamento < 0:
      deslocamento -2

    self.y +=deslocamento

    # Rotação 
    if deslocamento < 0 or self.y < (self.altura + 50):
      if self.angulo < self.rotacao_max:
        self.angulo = self.rotacao_max
    else:
      if self.angulo > -90:
        self.angulo -= self.velocidade_rotacao
  
  def desenhar(self,tela):
    self.contagem_imagem +=1

    if self.contagem_imagem < self.tempo_animacao:
      self.imagem = self.IMGS[0]
    elif self.contagem_imagem < self.tempo_animacao*2:
      self.imagem = self.IMGS[1]
    elif self.contagem_imagem < self.tempo_animacao*3:
      self.imagem = self.IMGS[2]
    elif self.contagem_imagem < self.tempo_animacao*4:
      self.imagem = self.IMGS[1]
    elif self.contagem_imagem < self.tempo_animacao*4+1:
      self.imagem = self.IMGS[0]  

    if self.angulo < -80:
      self.imagem = self.IMGS[1]
      self.contagem_imagem = self.tempo_animacao*2

    imagem_rotacionada = pygame.transform.rotate(self.imagem,self.angulo)
    pos_centro_img = self.imagem.get_rect(topleft=(self.x,self.y)).center
    retangulo = imagem_rotacionada.get_rect(center=pos_centro_img)
    tela.blit(imagem_rotacionada,retangulo.topleft)

  def get_mask(self):
    return pygame.mask.from_surface(self.imagem)
  
class Cano:
  distancia = 200
  velocidade = 5

  def __init__(self,x):
    self.x = x
    self.altura = 0
    self.pos_top =0
    self.pos_base =0
    self.cano_topo = pygame.transform.flip(img_cano,False,True)
    self.cano_base = img_cano
    self.passou = False
    self.definir_altura()

  def definir_altura(self):
    self.altura = random.randrange(50,450)
    self.pos_top = self.altura - self.cano_topo.get_height()
    self.pos_base = self.altura + self.distancia

  def mover(self):
    self.x -= self.velocidade

  def desenhar(self,tela):
    tela.blit(self.cano_topo,(self.x,self.pos_top))
    tela.blit(self.cano_base,(self.x,self.pos_base))

  def colidir(self,passaro):
    passaro_mask = passaro.get_mask()
    topo_mask = pygame.mask.from_surface(self.cano_topo)
    base_mask = pygame.mask.from_surface(self.cano_base)

    distancia_topo = (self.x - passaro.x,self.pos_top - round(passaro.y))
    distancia_base = (self.x - passaro.x,self.pos_base - round(passaro.y))

    topo_ponto = passaro.mask.overlap(topo_mask,distancia_topo)
    base_ponto = passaro.mask.overlap(base_mask,distancia_base)

    if base_ponto or topo_ponto:
      return True
    else:
        return False

class Chao:
  velocidade = 5
  largura = img_chao.get_width()
  imagem = img_chao

  def __init__(self,y):
    self.y = y
    self.x1 = 0
    self.x2 = self.largura
  
  def mover(self):
    self.x1 -= self.velocidade
    self.x2 -= self.velocidade

    if self.x1 + self.largura < 0:
      self.x1 = self.x1 + self.largura
    if self.x2 + self.largura < 0:
      self.x2 = self.x1 + self.largura
    
  def desenhar(self,tela):
    tela.blit(self.imagem,(self.x1,self.y))
    tela.blit(self.imagem,(self.x2,self.y))

def desenhar_tela(tela,passaros,canos,chao,pontos):
  tela.blit(img_bg,(0,0))
  for passaro in passaros:
    passaro.desenhar(tela)
  for cano in canos:
    cano.desenhar(tela)
  
  texto = fonte_global.render(f"Pontuação: {pontos}",1,(255,255,255))
  tela.blit(texto,(tela_largura-10 - texto.get_width(),10))

  chao.desenhar(tela)
  pygame.display.update()

def main():  
    # Inicializa os elementos do jogo  
    passaros = [Passaro(230, 350)] #230 é a posição do pássaro na tela (eixo x), 350 é a posição do pássaro na tela (eixo y)  
    chao = Chao(730) #730 é a posição do chão na tela (eixo y)  
    canos = [Cano(700)] #700 é a posição do cano na tela (eixo x)  
    tela = pygame.display.set_mode((tela_largura, tela_altura))  
    pontos = 0  
    relogio = pygame.time.Clock()  
  
    rodando = True  
    while rodando:  
        # Define a taxa de quadros por segundo  
        relogio.tick(30)  
  
        # Verifica as interações do usuário  
        for evento in pygame.event.get():  
            if evento.type == pygame.QUIT:  
                rodando = False  
                pygame.quit()  
                quit()  
            if evento.type == pygame.KEYDOWN:  
                if evento.key == pygame.K_SPACE:  
                    for passaro in passaros:  
                        passaro.pular()  
  
        # Move os elementos do jogo  
        for passaro in passaros:  
            passaro.mover()  
        chao.mover()  
  
        # Adiciona e remove os canos conforme necessário  
        adicionar_cano = False  
        remover_canos = []  
        for cano in canos:  
            for i, passaro in enumerate(passaros): # enumerate retorna o índice e o valor do elemento  
                # Verifica se houve colisão com os pássaros                if cano.colidir(passaro):  
                    passaros.pop(i)  
                # Verifica se o pássaro passou pelo cano  
            if not cano.passou and passaro.x > cano.x:  
                    cano.passou = True  
                    adicionar_cano = True  
            # Move o cano  
            cano.mover()  
            # Verifica se o cano saiu completamente da tela  
            if cano.x + cano.cano_topo.get_width() < 0:  
                remover_canos.append(cano)  
  
        # Adiciona um novo cano à medida que o pássaro passa por eles  
        if adicionar_cano:  
            pontos += 1  
            canos.append(Cano(600))  
        # Remove os canos que saíram completamente da tela  
        for cano in remover_canos:  
            canos.remove(cano)  
  
        # Remove os pássaros que colidiram com o chão ou ultrapassaram os limites superior/inferior da tela  
        for i, passaro in enumerate(passaros):  
            if (passaro.y + passaro.imagem.get_height()) > chao.y or passaro.y < 0:  
                passaros.pop(i)  
                rodando = False  
  
        # Desenha os elementos na tela  
        desenhar_tela(tela, passaros, canos, chao, pontos)  



if __name__ == '__main__':
  main()