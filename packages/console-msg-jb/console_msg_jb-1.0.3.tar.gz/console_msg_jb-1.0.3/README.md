# Console Msg

Descrição.  
O pacote console-msg é utilizado para:
	- Exibir mensagens personalizadas no terminal
    - Mensagem de erro (vermelho)
    - Mensagem de sucesso (verde)
    - Mensagem de alerta (amarelo)
    - Mensagem de informação (azul)

## Instalação

Use o gerenciador de pacotes [pip](https://pip.pypa.io/en/stable/) para instalar console-msg-jb

```bash
pip install console-msg-jb
```

## Uso

```python
from console_msg_jb.alert_msgs import *
# or 
# from console_msg_jb.alert_msgs import emsg, imsg, smsg, almsg

almsg("Alerta")
imsg("informação")
smsg("Sucesso")
emsg("Erro")
```
![img1](image.png)

```python
from console_msg_jb.alert_msgs import *
# or 
# from console_msg_jb.alert_msgs import emsg, imsg, smsg, almsg, BGColor

almsg("Alerta", BGColor.BLUE)
imsg("informação", BGColor.YELLOW))
smsg("Sucesso", BGColor.RED)
emsg("Erro", BGColor.CYAN)
```
![img2](image-1.png)


## Autor
JB Silva

## Licença
[MIT](https://choosealicense.com/licenses/mit/)
