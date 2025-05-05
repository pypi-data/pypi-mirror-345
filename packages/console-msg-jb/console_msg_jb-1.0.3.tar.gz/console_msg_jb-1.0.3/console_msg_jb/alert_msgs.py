from enum import Enum

class BGColor(Enum):
  BLACK= ';40m'
  RED= ';41m'
  GREEN= ';42m'
  YELLOW= ';43m'
  BLUE= ';44m'
  MAGENTA= ';45m'
  CYAN= ';46m'
  WHITE= ';47m'


def emsg(msg, bg_color:BGColor = None):
  """
  Exibe mensagem na cor vermelha
  msg: Mensagem a ser exibida
    => str: Mensagem de erro
  bg_color: Cor de fundo da mensagem
    => BGColor: Cor de fundo
  """
  bg_code = bg_color.value if bg_color is not None else 'm'
  print(f"\033[31{bg_code}{msg}\033[00m")

def smsg(msg, bg_color:BGColor = None):
  """
  Exibe mensagem na cor verde
  msg: Mensagem a ser exibida
    => str: Mensagem de sucesso
  bg_color: Cor de fundo da mensagem
    => BGColor: Cor de fundo
  """
  bg_code = bg_color.value if bg_color is not None else 'm'
  print(f"\033[32{bg_code}{msg}\033[00m")
  
def almsg(msg, bg_color:BGColor = None):
  """
  Exibe mensagem na cor amarela
  msg: Mensagem a ser exibida
    => str: Mensagem de alerta
  bg_color: Cor de fundo da mensagem
    => BGColor: Cor de fundo
  """
  bg_code = bg_color.value if bg_color is not None else 'm'
  print(f"\033[33{bg_code}{msg}\033[00m")

def imsg(msg, bg_color:BGColor = None):
  """
  Exibe mensagem na cor azul
  msg: Mensagem a ser exibida
    => str: Mensagem de informação
  bg_color: Cor de fundo da mensagem
    => BGColor: Cor de fundo
  """
  bg_code = bg_color.value if bg_color is not None else 'm'
  print(f"\033[34{bg_code}{msg}\033[00m")

