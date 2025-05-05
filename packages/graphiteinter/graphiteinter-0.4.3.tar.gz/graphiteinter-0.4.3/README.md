# GraphiteInter

GraphiteInter é uma estrutura simples para a criação de interfaces gráficas interativas usando o tkinter em Python.

## Como Usar

```python
from Graphite import GraphiteInter

# Função para exibir a contagem regressiva e a mensagem final
def start_countdown():
    GraphiteInter._root.after(0,GraphiteInter.removebutton("countdown"))
    GraphiteInter._root.after(1000,GraphiteInter.removebutton("rstrt"))
    # Insere a contagem de 10 a 0
    for i in range(60, -1, -1):  # De 10 até 0
        GraphiteInter._root.after((60 - i) * 1000, lambda i=i: GraphiteInter.inserttext(f"counter{i}", str(i), 50, (400, 250), "red"))
        GraphiteInter._root.after((60 - i) * 1000 + 500, lambda i=i: GraphiteInter.removeText(f"counter{i}"))

    # Insere a mensagem após a contagem regressiva
    GraphiteInter._root.after(61 * 1000, lambda: GraphiteInter.inserttext("EndTrial", "Sua licença expirou, reabra o programa", 30, (50, 250), "red"))
    GraphiteInter._root.after(61*1000,lambda:GraphiteInter.create_button("Reiniciar","rstrt",restart)) 
    GraphiteInter._root.after(61*1000,lambda:GraphiteInter.buttonposition("rstrt",0,0)) 
# Cria a janela
def restart():
 GraphiteInter._root.after(61*1000,lambda:GraphiteInter.removebutton("rstrt"))
 GraphiteInter._root.after(0,lambda:GraphiteInter.removeText("EndTrial"))
 GraphiteInter.create_button("Iniciar Contagem","countdown",start_countdown)
 GraphiteInter.buttonposition("countdown",0,0)
 GraphiteInter.removeBgImage()
#criando a janela
GraphiteInter.create_window("teste")

# Define o fundo da janela e a imagem de fundo
GraphiteInter.setbackground("blue")
GraphiteInter.setbgimage("C:\\Users\\leona\\Desktop\\imagem.jpg")

GraphiteInter.create_button("Iniciar Contagem","countdown",start_countdown)
GraphiteInter.buttonposition("countdown",0,0)

# Exibe a janela
GraphiteInter.run()
