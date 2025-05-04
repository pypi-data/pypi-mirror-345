# Console Msg

Descrição.  
O pacote console-msg é utilizado para:
	- Exibir mensagens personalizadas no terminal
    - Mensagem de erro (vermelho)
    - Mensagem de sucesso (verde)
    - Mensagem de alerta (amarelo)
    - Mensagem de informação (azul)

## Instalação

Use o gerenciador de pacotes [pip](https://pip.pypa.io/en/stable/) para instalar nome_do_pacote

```bash
pip install console-msg
```

## Uso

```python
from console-msg.alert_msgs import *

almsg("Alerta")
imsg("informação")
smsg("Sucesso")
emsg("Erro")
```
![img1](image.png)

```python
from console-msg.alert_msgs import *

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