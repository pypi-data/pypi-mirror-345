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
![image](https://github.com/user-attachments/assets/be686756-0fbf-482b-b2a4-3617de09c0bd)

```python
from console-msg.alert_msgs import *

almsg("Alerta", BGColor.RED)
imsg("informação", BGColor.BLUE))
smsg("Sucesso", BGColor.CYAN)
emsg("Erro", BGColor.YELLOW)
```
![image](https://github.com/user-attachments/assets/e49949c1-233c-4950-acd7-3649dd5323d9)


## Autor
Meu_nome

## Licença
[MIT](https://choosealicense.com/licenses/mit/)