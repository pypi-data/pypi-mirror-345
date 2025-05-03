#Graphite version 0.4.1
import threading
import time
import tkinter as tk
from tkinter import  Checkbutton, Entry, Frame, IntVar, Label, OptionMenu, Radiobutton, StringVar, Text, ttk
from PIL import Image, ImageTk
import json
from tkinter import Button
from tkinter import messagebox
from tkinterweb import HtmlFrame  # Importação de tkinterweb sem a verificação
from lxml import etree
from tkinter import PhotoImage
import tempfile
import os
import requests
import re
import configparser
import ctypes
import inspect

class GraphiteInter:
    created_buttons = set()  # Conjunto para armazenar IDs dos botões criados
    _root = None
    _bg_image_label = None
    _buttons = {}
    _texts = []
    _comboboxes = {}
    _sliders = {}
    _inputs = {} 
    _texts = {}  # Usado para armazenar os textos com seus IDs
    _state = {}  # Variável para armazenar o estado
    _width = 800
    _height = 600
    _bgi = None
    _tabs = {}
    _widgets = {}
    _loading_label = None
    _loading_running = False
    _html_frame = None 
    _Functions={}
    _buttons = {}  # Dicionário para armazenar botões pelo ID
    _icons = {}  # Dicionário para armazenar os ícones dos botões
    _loading_labels = {}  # Dicionário para armazenar labels de loading
    _windows = {}

    @staticmethod
    def create_window(title="GraphiteInter App"):
        """Cria uma janela principal."""
        GraphiteInter._root = tk.Tk()
        GraphiteInter._root.title(title)
        GraphiteInter._root.geometry("800x600")
        GraphiteInter._windows[title] = GraphiteInter._root

    @staticmethod
    def closewindow(windowname):
        """Fecha uma janela específica pelo nome."""
        if windowname in GraphiteInter._windows:
            GraphiteInter._windows[windowname].destroy()
            del GraphiteInter._windows[windowname]
        else:
            print(f"⚠️ A janela '{windowname}' não foi encontrada.")

    @staticmethod
    def setdimensions(width, height):
        """Define as dimensões da janela e armazena nas variáveis de classe."""
        if GraphiteInter._root:
            GraphiteInter._root.geometry(f"{width}x{height}")
            
            # Armazenar as dimensões nas variáveis de classe
            GraphiteInter._width = width
            GraphiteInter._height = height
            
            return width, height
        else:
            raise RuntimeError("A janela principal ainda não foi criada. Use GraphiteInter.create_window() primeiro.")

    @staticmethod
    def setbackground(color):
        """Define a cor de fundo da janela."""
        if GraphiteInter._root:
            GraphiteInter._root.configure(bg=color)
        else:
            raise RuntimeError("A janela principal ainda não foi criada. Use GraphiteInter.create_window() primeiro.")
    @staticmethod
    def parseword(from_word, to_word):
     """
     Retorna uma função que substitui 'from_word' por 'to_word' em uma string.
 
     Exemplo de uso:
         f = graphiteinter.parseword("dor de cabeça", "dor_cabeça")
         f("tenho dor de cabeça") -> "tenho dor_cabeça"
     """
     def converter(texto):
         return texto.replace(from_word, to_word)
     return converter

    @staticmethod
    def setbgimage(image_path):
        """Define uma imagem de fundo na janela."""
        
        if GraphiteInter._root:
        
            try:
                image = Image.open(image_path)
                bg_image = ImageTk.PhotoImage(image)
                
                if GraphiteInter._bg_image_label:
                    GraphiteInter._bg_image_label.destroy()  # Remove o antigo label da imagem

                # Criar e posicionar a imagem de fundo
                GraphiteInter._bg_image_label = tk.Label(GraphiteInter._root, image=bg_image)
                GraphiteInter._bg_image_label.image = bg_image  # Mantém uma referência para a imagem
                GraphiteInter._bg_image_label.place(x=0, y=0, relwidth=1, relheight=1)  # Preenche toda a janela
                GraphiteInter._bgi=image_path
            except Exception as e:
                raise RuntimeError(f"Erro ao carregar a imagem: {e}")
        else:
            raise RuntimeError("A janela principal ainda não foi criada. Use GraphiteInter.create_window() primeiro.")

    @staticmethod
    def create_button(text, button_id, command):
     """Cria um botão e adiciona ao estado."""
     if GraphiteInter._root:
        if button_id in GraphiteInter._buttons:
            raise ValueError(f"Já existe um botão com o ID '{button_id}'.")
        
        # Cria o botão
        button = tk.Button(GraphiteInter._root, text=text, command=command)
        GraphiteInter._buttons[button_id] = button
        
        # Inicializa o botão no estado
        GraphiteInter._state.setdefault("buttons", {})
        GraphiteInter._state["buttons"][button_id] = {
            "text": text,
            "bg": button.cget("bg"),
            "fg": button.cget("fg"),
            "position": [0, 0]  # Posição padrão inicial
        }
     else:
        raise RuntimeError("A janela principal ainda não foi criada. Use GraphiteInter.create_window() primeiro.")

    @staticmethod
    def buttonposition(button_id, x, y):
     """Define a posição de um botão na interface."""
     if button_id in GraphiteInter._buttons:
        button = GraphiteInter._buttons[button_id]
        button.place(x=x, y=y)  # Altera a posição visual do botão
        GraphiteInter._state["buttons"][button_id]["position"] = [x, y]  # Atualiza a posição no estado interno
     else:
        raise KeyError(f"Botão com ID '{button_id}' não encontrado.")

    @staticmethod
    def inserttext(text_id, text, font_size, position, color):
        """Insere texto em uma posição específica com uma cor personalizada e tamanho de fonte, agora com ID."""
        if GraphiteInter._root:
            x, y = position
            label = tk.Label(GraphiteInter._root, text=text, fg=color, font=("Arial", font_size))
            label.place(x=x, y=y)
            GraphiteInter._texts[text_id] = label  # Armazena o texto com o ID especificado
        else:
            raise RuntimeError("A janela principal ainda não foi criada. Use GraphiteInter.create_window() primeiro.")

    @staticmethod
    def update_text(text_id, new_text):
        """Atualiza o texto de um Label existente, dado o ID."""
        if text_id in GraphiteInter._texts:
            GraphiteInter._texts[text_id].config(text=new_text)
        else:
            raise ValueError(f"O texto com ID '{text_id}' não foi encontrado.")
      
    @staticmethod
    def insertcombo(combo_id, options, position, size=(20, 3)):
     """Cria uma ComboBox (caixa de seleção) e a armazena com seu ID."""
     if GraphiteInter._root:
        if combo_id in GraphiteInter._comboboxes:
            raise ValueError(f"A ComboBox com ID '{combo_id}' já existe.")
        
        # Cria a ComboBox
        combo = ttk.Combobox(GraphiteInter._root, values=options.split(','), width=size[0], height=size[1])
        x, y = position
        combo.place(x=x, y=y)
        
        # Armazena a ComboBox no dicionário com seu ID
        GraphiteInter._comboboxes[combo_id] = combo
     else:
        raise RuntimeError("A janela principal ainda não foi criada. Use GraphiteInter.create_window() primeiro.")
    @staticmethod
    def get_combo_value(combo_id):
     """Retorna o valor selecionado da ComboBox com o ID especificado."""
     if combo_id in GraphiteInter._comboboxes:
        return GraphiteInter._comboboxes[combo_id].get()
     else:
        raise ValueError(f"A ComboBox com ID '{combo_id}' não foi encontrada.")
    @staticmethod
    def update_combo_options(combo_id, new_options):
     """Atualiza as opções de uma ComboBox existente."""
     if combo_id in GraphiteInter._comboboxes:
        combo = GraphiteInter._comboboxes[combo_id]
        combo['values'] = new_options.split(',')
     else:
        raise ValueError(f"A ComboBox com ID '{combo_id}' não foi encontrada.")
    @staticmethod
    def remove_combo(combo_id):
     """Remove uma ComboBox da interface."""
     if combo_id in GraphiteInter._comboboxes:
        GraphiteInter._comboboxes[combo_id].destroy()
        del GraphiteInter._comboboxes[combo_id]
     else:
        raise ValueError(f"A ComboBox com ID '{combo_id}' não foi encontrada.")

    @staticmethod
    def insertslider(slider_id, position, orient="horizontal", sliderlength=20, slider_color="blue", width=10):
        """Cria um slider e o armazena no dicionário com seu ID."""
        if GraphiteInter._root:
            slider = tk.Scale(GraphiteInter._root, orient=orient, sliderlength=sliderlength, length=300, width=width)
            x, y = position
            slider.place(x=x, y=y)
            GraphiteInter._sliders[slider_id] = slider
            # Estilo para o slider (cor)
            slider.config(troughcolor="lightgray", sliderrelief="solid", bg=slider_color)
        else:
            raise RuntimeError("A janela principal ainda não foi criada. Use GraphiteInter.create_window() primeiro.")
    @staticmethod
    def Getslidervalue(slider_id):
        """Obtém o valor atual do slider."""
        if slider_id in GraphiteInter._sliders:
            return GraphiteInter._sliders[slider_id].get()
        else:
            raise ValueError(f"O slider com ID '{slider_id}' não foi encontrado.")
    @staticmethod
    def setmaximum(slider_id, max_value):
        """Define o valor máximo de um slider."""
        if GraphiteInter._root:
            if slider_id in GraphiteInter._sliders:
                GraphiteInter._sliders[slider_id].config(to=max_value)  # Corrigir para 'to' em vez de 'max'
            else:
                raise ValueError(f"O slider com ID '{slider_id}' não foi encontrado.")
        else:
            raise RuntimeError("A janela principal ainda não foi criada. Use GraphiteInter.create_window() primeiro.")
    @staticmethod
    def sliderpos(slider_id, position):
        """Define a posição do slider."""
        if slider_id in GraphiteInter._sliders:
            GraphiteInter._sliders[slider_id].set(position)
        else:
            raise ValueError(f"O slider com ID '{slider_id}' não foi encontrado.")
    @staticmethod
    def removebutton(button_id):
        """Remove um botão da interface."""
        if button_id in GraphiteInter._buttons:
            GraphiteInter._buttons[button_id].destroy()
            del GraphiteInter._buttons[button_id]
    @staticmethod
    def removeslider(Slider_id):
        """Remove um slider da interface."""
        if Slider_id in GraphiteInter._sliders:
            GraphiteInter._sliders[Slider_id].destroy()
            del GraphiteInter._sliders[Slider_id]
    @staticmethod
    def removeText(_texts):
        """Remove um texto da interface."""
        if _texts in GraphiteInter._texts:
            GraphiteInter._texts[_texts].destroy()
            del GraphiteInter._texts[_texts]
    @staticmethod
    def removeInput(_inputs):
        """Remove um input da interface."""
        if _inputs in GraphiteInter._inputs:
            GraphiteInter._inputs[_inputs].destroy()
            del GraphiteInter._inputs[_inputs]
    @staticmethod
    def removeBgImage():
      """Remove a imagem de fundo da interface."""
      if GraphiteInter._bg_image_label:
          GraphiteInter._bg_image_label.destroy()  # Remove o widget da imagem de fundo
          GraphiteInter._bg_image_label = None
      else:
          raise ValueError("Nenhuma imagem de fundo foi definida.")         
    @staticmethod
    def sliderOrientation(slider_id, orientation):
        """Define a orientação do slider (horizontal ou vertical)."""
        if slider_id in GraphiteInter._sliders:
            GraphiteInter._sliders[slider_id].config(orient=orientation)
        else:
            raise ValueError(f"O slider com ID '{slider_id}' não foi encontrado.")
    @staticmethod
    def sliderthickness(slider_id, thickness):
        """Define a espessura do slider."""
        if GraphiteInter._root:
            if slider_id in GraphiteInter._sliders:
                GraphiteInter._sliders[slider_id].config(width=thickness)  # Corrigir para 'width' em vez de 'thickness'
            else:
                raise ValueError(f"O slider com ID '{slider_id}' não foi encontrado.")
        else:
            raise RuntimeError("A janela principal ainda não foi criada. Use GraphiteInter.create_window() primeiro.")
    @staticmethod
    def slidercolor(slider_id, color):
        """Define a cor do slider."""
        if slider_id in GraphiteInter._sliders:
            GraphiteInter._sliders[slider_id].config(bg=color)
        else:
            raise ValueError(f"O slider com ID '{slider_id}' não foi encontrado.")
    @staticmethod
    def addtextinput(input_id, position, size=(20, 3)):
        """Cria uma caixa de entrada de texto (Text) e a armazena com seu ID."""
        if GraphiteInter._root:
            text = tk.Text(GraphiteInter._root, width=size[0], height=size[1])
            x, y = position
            text.place(x=x, y=y)
            GraphiteInter._inputs[input_id] = text  # Armazena a entrada criada
        else:
            raise RuntimeError("A janela principal ainda não foi criada. Use GraphiteInter.create_window() primeiro.")
    @staticmethod
    def inputposition(input_id, position):
        """Define a posição de um campo de entrada."""
        if input_id in GraphiteInter._inputs:
            entry = GraphiteInter._inputs[input_id]
            x, y = position
            entry.place(x=x, y=y)
        else:
            raise ValueError(f"O campo de entrada com ID '{input_id}' não foi encontrado.")
    @staticmethod
    def inputsize(input_id, size):
        """Define o tamanho do campo de entrada (largura, altura)."""
        if input_id in GraphiteInter._inputs:
            entry = GraphiteInter._inputs[input_id]
            entry.config(width=size[0], height=size[1])
        else:
            raise ValueError(f"O campo de entrada com ID '{input_id}' não foi encontrado.")
    @staticmethod
    def buttonaction(button_id, command):
        """Define a ação de um botão."""
        if GraphiteInter._root:
            if button_id in GraphiteInter._buttons:
                button = GraphiteInter._buttons[button_id]
                button.config(command=command)
            else:
                raise ValueError(f"O botão com ID '{button_id}' não foi encontrado.")
        else:
            raise RuntimeError("A janela principal ainda não foi criada. Use GraphiteInter.create_window() primeiro.")
    
    @staticmethod
    def run():
        """Inicia o loop principal da interface gráfica."""
        if GraphiteInter._root:
            GraphiteInter._root.mainloop()
        else:
            raise RuntimeError("A janela principal ainda não foi criada. Use GraphiteInter.create_window() primeiro.")
  
    @staticmethod
    def show_notification(message, duration, color, font):
     """
    Exibe uma notificação temporária na janela principal.
    :param message: Texto da notificação.
    :param duration: Duração em milissegundos (default: 3000ms).
    :param color: Cor de fundo da notificação (default: "yellow").
    :param font: Fonte do texto (default: "Arial", 12).
    """
     if GraphiteInter._root:
        notification_label = tk.Label(
            GraphiteInter._root,
            text=message,
            bg=color,
            fg="black",
            font=font,
            relief="solid",
            padx=10,
            pady=5,
        )
        notification_label.place(relx=0.5, rely=0, anchor="n")
        
        # Remove a notificação após o tempo definido
        GraphiteInter._root.after(duration, notification_label.destroy)
     else:
        raise RuntimeError("A janela principal ainda não foi criada. Use GraphiteInter.create_window() primeiro.")

    @staticmethod
    def create_tab(tab_id, label):
        """
        Cria uma nova aba com o rótulo especificado.
        :param tab_id: ID único para a aba.
        :param label: Rótulo visível da aba.
        """
        if not hasattr(GraphiteInter, "_notebook"):
            GraphiteInter._notebook = ttk.Notebook(GraphiteInter._root)
            GraphiteInter._notebook.pack(expand=True, fill="both")
            GraphiteInter._tabs = {}
    
        if tab_id in GraphiteInter._tabs:
            raise ValueError(f"Uma aba com o ID '{tab_id}' já existe.")
    
        tab_frame = tk.Frame(GraphiteInter._notebook)
        GraphiteInter._notebook.add(tab_frame, text=label)
        GraphiteInter._tabs[tab_id] = tab_frame
    @staticmethod
    def tabwidget(tab_id, widget):
     """
    Adiciona um widget a uma aba específica.
    :param tab_id: ID da aba onde o widget será adicionado.
    :param widget: Widget a ser adicionado.
    """
     if tab_id in GraphiteInter._tabs:
        widget.pack(in_=GraphiteInter._tabs[tab_id], padx=10, pady=5)
     else:
        raise ValueError(f"A aba com ID '{tab_id}' não foi encontrada.")
    @staticmethod
    def remove_tab(tab_id):
        """
        Remove uma aba existente.
        :param tab_id: ID da aba a ser removida.
        """
        if tab_id in GraphiteInter._tabs:
            tab_frame = GraphiteInter._tabs[tab_id]
            GraphiteInter._notebook.forget(tab_frame)  # Remove a aba do Notebook
            del GraphiteInter._tabs[tab_id]  # Remove a referência
        else:
            raise ValueError(f"A aba com ID '{tab_id}' não foi encontrada.")
    @staticmethod
    def create_tab_button(tab_id, button_id, button_text, buttonposx, buttonposy, action, button_color=None, text_color=None):
        """
        Cria um botão dentro de uma aba específica.
        :param tab_id: ID da aba onde o botão será adicionado.
        :param button_id: ID único para o botão.
        :param button_text: Texto exibido no botão.
        :param buttonposx: Espaçamento horizontal do botão.
        :param buttonposy: Espaçamento vertical do botão.
        :param action: Função que será executada quando o botão for clicado.
        :param button_color: Cor de fundo do botão.
        :param text_color: Cor do texto do botão.
        """
        if tab_id not in GraphiteInter._tabs:
            raise ValueError(f"A aba com ID '{tab_id}' não foi encontrada.")

        if button_id in GraphiteInter._buttons:
            raise ValueError(f"Já existe um botão com o ID '{button_id}'.")

        # Criar o botão
        button = tk.Button(GraphiteInter._tabs[tab_id], text=button_text, command=action, bg=button_color, fg=text_color)
        button.pack(padx=buttonposx, pady=buttonposy)  # Posiciona o botão dentro da aba

        # Armazenar o botão com seu ID
        GraphiteInter._buttons[button_id] = button

    @staticmethod
    def tabbackground(tab_id, background):
        """
        Define o plano de fundo de uma aba específica.
        :param tab_id: ID da aba onde o plano de fundo será alterado.
        :param background: Cor (ex.: "blue") ou caminho para uma imagem (ex.: "path/to/image.png").
        """
        if tab_id not in GraphiteInter._tabs:
            raise ValueError(f"A aba com ID '{tab_id}' não foi encontrada.")
    
        tab = GraphiteInter._tabs[tab_id]
    
        # Se for uma cor, define como fundo da aba
        if isinstance(background, str) and not background.endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            tab.configure(bg=background)
        else:
            # Caso seja uma imagem, carrega e define como fundo
            try:
                image = Image.open(background)
                bg_image = ImageTk.PhotoImage(image)
    
                # Cria um label com a imagem de fundo
                bg_label = tk.Label(tab, image=bg_image)
                bg_label.image = bg_image  # Mantém a referência à imagem
                bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    
                # Coloca o label como fundo da aba
                bg_label.lower()  # Move para trás de outros widgets
            except Exception as e:
                raise RuntimeError(f"Erro ao carregar a imagem: {e}")
            
#acabei de criar abaixo

    @staticmethod
    def insert_text_in_tab(tab_id, text_id, text, font_size, position, color):
     """Insere um texto em uma aba específica com um ID.""" 
     if tab_id in GraphiteInter._tabs:
        x, y = position
        try:
            # Forçar conversão correta de cor hexadecimal
            if color.startswith("#") and len(color) == 7:
                tk_color = color.upper()  # Algumas versões do Tkinter podem exigir maiúsculas
            else:
                tk_color = color.lower()  # Garantir que cores por nome sejam minúsculas
                
            label = tk.Label(GraphiteInter._tabs[tab_id], text=text, fg=tk_color, font=("Arial", font_size))
            label.place(x=x, y=y)
            GraphiteInter._texts[text_id] = label
        except tk.TclError:
            raise ValueError(f"Cor '{color}' inválida. Use um nome de cor válido ou um código hexadecimal no formato #RRGGBB.")
     else:
        raise ValueError(f"A aba com ID '{tab_id}' não foi encontrada.")

    @staticmethod
    def update_text_in_tab(tab_id, text_id, new_text):
        """Atualiza o texto de um Label dentro de uma aba específica, dado o ID."""
        if tab_id in GraphiteInter._tabs:
            if text_id in GraphiteInter._texts:
                GraphiteInter._texts[text_id].config(text=new_text)
            else:
                raise ValueError(f"O texto com ID '{text_id}' não foi encontrado.")
        else:
            raise ValueError(f"A aba com ID '{tab_id}' não foi encontrada.")
  
    @staticmethod
    def remove_text_from_tab(tab_id, text_id):
        """Remove um texto de uma aba específica."""
        if tab_id in GraphiteInter._tabs:
            if text_id in GraphiteInter._texts:
                GraphiteInter._texts[text_id].destroy()
                del GraphiteInter._texts[text_id]
            else:
                raise ValueError(f"O texto com ID '{text_id}' não foi encontrado na aba '{tab_id}'.")
        else:
            raise ValueError(f"A aba com ID '{tab_id}' não foi encontrada.")
  
    @staticmethod
    def insert_slider_in_tab(tab_id, slider_id, position, orient="horizontal", sliderlength=20, slider_color="blue", width=10):
        """Insere um slider em uma aba específica."""
        if tab_id in GraphiteInter._tabs:
            slider = tk.Scale(GraphiteInter._tabs[tab_id], orient=orient, sliderlength=sliderlength, length=300, width=width)
            x, y = position
            slider.place(x=x, y=y)
            GraphiteInter._sliders[slider_id] = slider
            slider.config(troughcolor="lightgray", sliderrelief="solid", bg=slider_color)
        else:
            raise ValueError(f"A aba com ID '{tab_id}' não foi encontrada.")
  
    @staticmethod
    def remove_slider_from_tab(tab_id, slider_id):
        """Remove um slider de uma aba específica."""
        if tab_id in GraphiteInter._tabs:
            if slider_id in GraphiteInter._sliders:
                GraphiteInter._sliders[slider_id].destroy()
                del GraphiteInter._sliders[slider_id]
            else:
                raise ValueError(f"O slider com ID '{slider_id}' não foi encontrado na aba '{tab_id}'.")
        else:
            raise ValueError(f"A aba com ID '{tab_id}' não foi encontrada.")
  
    @staticmethod
    def insert_combo_in_tab(tab_id, combo_id, options, position, size=(20, 3)):
        """Insere uma ComboBox em uma aba específica."""
        if tab_id in GraphiteInter._tabs:
            if combo_id in GraphiteInter._comboboxes:
                raise ValueError(f"A ComboBox com ID '{combo_id}' já existe.")
            combo = ttk.Combobox(GraphiteInter._tabs[tab_id], values=options.split(','), width=size[0], height=size[1])
            x, y = position
            combo.place(x=x, y=y)
            GraphiteInter._comboboxes[combo_id] = combo
        else:
            raise ValueError(f"A aba com ID '{tab_id}' não foi encontrada.")
  
    @staticmethod
    def remove_combo_from_tab(tab_id, combo_id):
        """Remove uma ComboBox de uma aba específica."""
        if tab_id in GraphiteInter._tabs:
            if combo_id in GraphiteInter._comboboxes:
                GraphiteInter._comboboxes[combo_id].destroy()
                del GraphiteInter._comboboxes[combo_id]
            else:
                raise ValueError(f"A ComboBox com ID '{combo_id}' não foi encontrada na aba '{tab_id}'.")
        else:
            raise ValueError(f"A aba com ID '{tab_id}' não foi encontrada.")
  
    @staticmethod
    def insert_input_in_tab(tab_id, input_id, position, size=(20, 3)):
        """Insere uma caixa de entrada de texto (Input) em uma aba específica."""
        if tab_id in GraphiteInter._tabs:
            input_field = tk.Text(GraphiteInter._tabs[tab_id], width=size[0], height=size[1])
            x, y = position
            input_field.place(x=x, y=y)
            GraphiteInter._inputs[input_id] = input_field  # Armazena o input com o ID especificado
        else:
            raise ValueError(f"A aba com ID '{tab_id}' não foi encontrada.")
  
    @staticmethod
    def remove_input_from_tab(tab_id, input_id):
        """Remove uma caixa de entrada de texto de uma aba específica."""
        if tab_id in GraphiteInter._tabs:
            if input_id in GraphiteInter._inputs:
                GraphiteInter._inputs[input_id].destroy()
                del GraphiteInter._inputs[input_id]
            else:
                raise ValueError(f"O input com ID '{input_id}' não foi encontrado na aba '{tab_id}'.")
        else:
            raise ValueError(f"A aba com ID '{tab_id}' não foi encontrada.")
    widgets = {}
    scheduled_events = {}

    @staticmethod
    def schedule_event(event_id, action, delay_ms):
        """Agenda a execução de uma função após um tempo definido."""
        def delayed_execution():
            time.sleep(delay_ms / 1000)
            action()
        
        thread = threading.Thread(target=delayed_execution)
        thread.start()
        GraphiteInter.scheduled_events[event_id] = thread
    
    
    
    @staticmethod
    def create_form(form_id, fields, x=0, y=0, buttonaction=None, width=None, height=None):
     """Cria um formulário com base em um dicionário de campos e permite definir a posição e dimensões."""
     form_frame = Frame()
 
     if width or height:
         form_frame.config(width=width, height=height)
 
     GraphiteInter.widgets[form_id] = form_frame
 
     for i, (label_text, field_type) in enumerate(fields.items()):
         label = Label(form_frame, text=label_text)
         label.grid(row=i, column=0, padx=5, pady=5)
 
         entry = None
 
         if field_type == "text":
             entry = Entry(form_frame)
         elif field_type == "password":
             entry = Entry(form_frame, show="*")
         elif field_type == "email":
             entry = Entry(form_frame)
         elif field_type == "number":
             entry = Entry(
                 form_frame,
                 validate="key",
                 validatecommand=(form_frame.register(lambda char: char.isdigit()), "%P"),
             )
         elif field_type == "date":
             entry = Entry(form_frame)
         elif field_type == "checkbox":
             var = IntVar()
             entry = Checkbutton(form_frame, text=label_text, variable=var)
             GraphiteInter.widgets[f"{form_id}_{label_text}_var"] = var
         elif field_type == "radio":
             var = IntVar()
             entry = Frame(form_frame)
             options = ["Option 1", "Option 2", "Option 3"]
             for j, option in enumerate(options):
                 radio = Radiobutton(entry, text=option, variable=var, value=j)
                 radio.grid(row=j, column=0)
             GraphiteInter.widgets[f"{form_id}_{label_text}_var"] = var
         elif field_type == "textarea":
             entry = Text(form_frame, height=4, width=30)
         elif field_type == "file":
             entry = Entry(form_frame)
         elif field_type == "hidden":
             entry = Entry(form_frame, show="")
         elif field_type.lower() == "button":
             entry = Button(form_frame, text=label_text, command=buttonaction or (lambda: print("Botão pressionado!")))
 
         if entry:
             entry.grid(row=i, column=1, padx=5, pady=5)
             GraphiteInter.widgets[f"{form_id}_{label_text}"] = entry
 
     form_frame.place(x=x, y=y)

    @staticmethod
    def get_form_data(form_id):
        """Obtém os dados preenchidos no formulário com base no form_id."""
        form_data = {}
        
        for widget_key, widget in GraphiteInter.widgets.items():
            if widget_key.startswith(f"{form_id}_"):
                label_text = widget_key.replace(f"{form_id}_", "")
                if isinstance(widget, Entry):
                    form_data[label_text] = widget.get()
                elif isinstance(widget, Text):
                    form_data[label_text] = widget.get("1.0", "end-1c")
                elif isinstance(widget, Checkbutton):
                    var = GraphiteInter.widgets.get(f"{form_id}_{label_text}_var")
                    form_data[label_text] = var.get() if var else None
                elif isinstance(widget, Frame):
                    var = GraphiteInter.widgets.get(f"{form_id}_{label_text}_var")
                    form_data[label_text] = var.get() if var else None
        
        return form_data
    @staticmethod
    def save_in_file(file_name, form_data):
        """Salva os dados do formulário em um arquivo, adicionando ao final do arquivo."""
        try:
            with open(file_name, 'a') as file:  # Modo 'a' para adicionar ao final do arquivo
                file.write(",")  # Linha de separação entre formulários
                for key, value in form_data.items():
                    file.write(f"{key}: {value}\n")
                file.write("\n")  # Adiciona uma linha em branco ao final
            print(f"Dados salvos no arquivo: {file_name}")
        except Exception as e:
            print(f"Erro ao salvar dados no arquivo: {e}")

    @staticmethod
    def read_file(file_name):
     """Lê o conteúdo de um arquivo e retorna como uma string."""
     try:
        with open(file_name, 'r') as file:
            content = file.read()  # Lê todo o conteúdo do arquivo
        return content
     except FileNotFoundError:
        return f"Arquivo '{file_name}' não encontrado."
     except Exception as e:
        return f"Erro ao ler o arquivo: {e}"
     

    @staticmethod
    def compare(item1, item2):
     """Compara dois valores e retorna o resultado da comparação."""
     if item1 == item2:
        return True  # Os valores são iguais
     else:
        return False  # Os valores são diferentes

    @staticmethod
    def load_addon(json_path):
     """Carrega um addon em formato JSON e cria elementos dinamicamente."""
     try:
         with open(json_path, "r", encoding="utf-8") as f:
             addon_data = json.load(f)
 
         elements = addon_data.get("elements", [])
         actions = addon_data.get("actions", [])
 
         # Criar um dicionário de ações baseadas em arquivos de código
         action_functions = {action['name']: action for action in actions}
 
         # Função para criar ação de execução
         def create_action(action_name):
             def action():
                 # Se for uma função declarada no JSON como type: Function
                 if action_name in GraphiteInter._Functions:
                     for act in GraphiteInter._Functions[action_name]:
                         tipo = act.get("action_type")
                         if tipo == "create_window":
                             GraphiteInter.create_window(act["name"])
                         elif tipo == "setbackground":
                             GraphiteInter.setbackground(act["color"])
                         # (adicione aqui outros tipos de ações conforme precisar)
                 # Se for uma função associada a um script Python externo
                 elif action_name in action_functions:
                     action_func = action_functions[action_name]
                     code_file = action_func['parameters'][0].get('code_file')
                     function_name = action_func['parameters'][0].get('functionname')
                     if code_file:
                         try:
                             with open(code_file, 'r', encoding='utf-8') as f:
                                 code = f.read()  # Lê o código do arquivo
                             exec(code, globals())  # Executa o código lido
 
                             # Chama a função especificada, se encontrada
                             if function_name:
                                 if function_name in globals():
                                     func = globals()[function_name]
                                     if callable(func):
                                         func()  # Chama a função específica
                                     else:
                                         print(f"Erro: '{function_name}' não é uma função válida.")
                                 else:
                                     print(f"Erro: Função '{function_name}' não encontrada no arquivo.")
                         except FileNotFoundError:
                             print(f"Erro: Arquivo '{code_file}' não encontrado.")
                         except Exception as e:
                             print(f"Erro ao executar o código do arquivo '{code_file}': {e}")
                     else:
                         print(f"Ação {action_name} não possui um arquivo de código válido.")
                 else:
                     print(f"Ação {action_name} não encontrada.")
             return action
 
         # Processar os elementos
         for element in elements:
             element_type = element.get("type")
 
             if element_type == "Function":
                 function_name = element.get("name")
                 action_list = element.get("actions", [])
                 GraphiteInter._Functions[function_name] = action_list
 
             elif element_type == "button":
                 button_id = element.get("id")
                 button_text = element.get("text", "Botão")
                 position = element.get("position", [0, 0])
                 action_names = element.get("action", [])
 
                 if button_id in GraphiteInter.created_buttons:
                     print(f"Erro: Já existe um botão com o ID '{button_id}'.")
                     continue
 
                 for action_name in action_names:
                     action_func = create_action(action_name)
                     GraphiteInter.create_button(button_text, button_id, action_func)
                     GraphiteInter.buttonposition(button_id, position[0], position[1])
 
             elif element_type == "text":
                 text_id = element.get("id")
                 text_content = element.get("text", "Texto Padrão")
                 font_size = element.get("font_size", 12)
                 color = element.get("color", "black")
                 position = element.get("position", [0, 0])
                 GraphiteInter.inserttext(text_id, text_content, font_size, position, color)
 
             elif element_type == "combobox":
                 combo_id = element.get("id")
                 options = element.get("options", "").split(",")
                 position = element.get("position", [0, 0])
                 GraphiteInter.insertcombo(combo_id, ",".join(options), position)
 
             elif element_type == "slider":
                 slider_id = element.get("id")
                 position = element.get("position", [0, 0])
                 max_value = element.get("max", 100)
                 GraphiteInter.insertslider(slider_id, position)
                 GraphiteInter.setmaximum(slider_id, max_value)
 
             elif element_type == "input":
                 input_id = element.get("id")
                 position = element.get("position", [0, 0])
                 GraphiteInter.addtextinput(input_id, position)
 
             elif element_type == "background":
                 color = element.get("color")
                 image = element.get("image")
                 if image:
                     GraphiteInter.setbgimage(image)
                 elif color:
                     GraphiteInter.setbackground(color)
 
             elif element_type == "tab":
                 Tab_id = element.get("id")
                 Tab_Text = element.get("text")
                 GraphiteInter.create_tab(Tab_id, Tab_Text)
 
             elif element_type == "xmlcontainer":
                 XML = element.get("XMLFile")
                 XSLT = element.get("XSLTFile")
                 if XML and XSLT:
                     if os.path.exists(XML) and os.path.exists(XSLT):
                         GraphiteInter.CreateXMLBasedContainer(XML, XSLT)
                     else:
                         print("Erro: Um ou ambos os arquivos XML/XSLT não foram encontrados.")
                 else:
                     print("Erro: Caminho do arquivo XML ou XSLT não fornecido.")
 
             elif element_type == "container":
                 HTML = element.get("HTMLFile")
                 if HTML:
                     if os.path.exists(HTML):
                         GraphiteInter.createHtmlContainer(HTML)
                     else:
                         print("Erro: HTML não foi encontrado.")
                 else:
                     print("Erro: Caminho do HTML não fornecido.")
 
             elif element_type == "tbutton":
                 Tid = element.get("tabid")
                 BID = element.get("bid")
                 BTEXT = element.get("btext")
                 XPOS = element.get("posx")
                 YPOS = element.get("posy")
                 ACTION = element.get("action")
                 BCOLOR = element.get("bcolor")
                 BTEXTCOLOR = element.get("btextcolor")
                 GraphiteInter.create_tab_button(Tid, BID, BTEXT, XPOS, YPOS, ACTION, BCOLOR, BTEXTCOLOR)
 
             elif element_type == "ttext":
                 TABID = element.get("tabid")
                 TEXTID = element.get("textid")
                 TEXT = element.get("text")
                 FONTSIZE = element.get("fontsize")
                 POSITION = element.get("position")
                 COLOR = element.get("color")
                 GraphiteInter.insert_text_in_tab(TABID, TEXTID, TEXT, FONTSIZE, POSITION, COLOR)
 
             elif element_type == "tbackground":
                 TAB = element.get("tabid")
                 BG = element.get("tabbackground")
                 GraphiteInter.tabbackground(tab_id=TAB, background=BG)
 
             elif element_type == "ComboTab":
                 TABID = element.get("tabid")
                 COMBOID = element.get("comboid")
                 OPTIONS = element.get("options")
                 POSITION = element.get("position")
                 SIZE = element.get("size")
                 GraphiteInter.insert_combo_in_tab(TABID, COMBOID, OPTIONS, POSITION, SIZE)
 
             elif element_type == "InputTab":
                 TABID = element.get("tabid")
                 INPUTID = element.get("inputid")
                 POSITION = element.get("position")
                 SIZE = element.get("size")
                 GraphiteInter.insert_input_in_tab(TABID, INPUTID, POSITION, SIZE)
 
             elif element_type == "SliderTab":
                 TABID = element.get("tabid")
                 SLIDERID = element.get("sliderid")
                 POSITION = element.get("position")
                 ORIENTATION = element.get("orientation")
                 LENGTH = element.get("length")
                 COLOR = element.get("color")
                 WIDTH = element.get("width")
                 GraphiteInter.insert_slider_in_tab(TABID, SLIDERID, POSITION, ORIENTATION, LENGTH, COLOR, WIDTH)
 
         print(f"✅ Addon '{json_path}' carregado com sucesso!")
 
     except Exception as e:
         print(f"❌ Erro ao carregar o addon: {e}")



    @staticmethod
    def execute_function(function_name):
        """Executa uma função carregada do JSON."""
        if function_name in GraphiteInter._Functions:
            actions = GraphiteInter._Functions[function_name]
            for action in actions:
                if isinstance(action, dict):
                    action_type = action.get("action_type")

                    if action_type == "print":
                        print(action.get("message", "[Mensagem Vazia]"))
                    elif action_type == "show_message":
                        messagebox.showinfo(action.get("title", "Info"), action.get("message", "[Mensagem Vazia]"))
                    elif action_type =="compare":
                        COMPARATOR1=action.get("comparator1")
                        COMPARATOR2=action.get("comparator2")
                        GraphiteInter.compare(COMPARATOR1,COMPARATOR2)
                    elif action_type =="remove_form":
                     FID=action.get("FormId")
                     GraphiteInter.remove_form(FID)

                    elif action_type =="separate_graphite":
                     ITEM=action.get("Separate")
                     SEPARATOR=action.get("Separator")
                     GraphiteInter.separate_graphite(ITEM,SEPARATOR)

                    elif action_type =="create_menu":
                     MENUITEMS=action.get("items")
                     GraphiteInter.create_menu(MENUITEMS)

                    elif action_type =="Show_External_Notification":
                     TITLE=action.get("Title")
                     MESSAGE=action.get("Message")
                     TYPE=action.get("Type")
                     GraphiteInter.Show_External_Notification(TITLE,MESSAGE,TYPE)

                    elif action_type =="enable_drag":
                     ITEMID=action.get("id")
                     GraphiteInter.enable_drag(ITEMID)

                    elif action_type=="CreateXMLBasedContainer":
                     XML=action.get("xml_path")
                     XSLT=action.get("xslt_path")
                     GraphiteInter.CreateXMLBasedContainer(XML,XSLT)

                    elif action_type=="createHtmlContainer":
                     HTMLFILE=action.get("html_file")
                     GraphiteInter.createHtmlContainer(HTMLFILE)
                     
                    elif action_type=="removeHtmlContainer":
                     GraphiteInter.removeHtmlContainer()

                    elif action_type=="load_webpage":
                     URL=action.get("url")
                     GraphiteInter.load_webpage(URL)

                    elif action_type=="create_tab_button":
                     TID=action.get("tab_id")
                     BID=action.get("button_id")
                     BTEXT=action.get("text")
                     BPOSX=action.get("posx")
                     BPOSY=action.get("posy")
                     BCOLOR=action.get("button_color")
                     TEXTCOLOR=action.get("text_color")
                     GraphiteInter.create_tab_button(TID,BID,BTEXT,BPOSX,BPOSY,None,BCOLOR,TEXTCOLOR)
                   
                    elif action_type=="read_file":
                     FNAME=action.get("fileName")
                     GraphiteInter.read_file(FNAME)

                    elif action_type=="create_form":
                     ID=action.get("id")
                     FIELDS=action.get("fields")
                     BACTION=action.get("button action")
                     X=action.get("posx")
                     Y=action.get("posy")
                     GraphiteInter.create_form(ID,FIELDS,X,Y,BACTION)

                    elif action_type=="schedule_event":
                     ACTION=action.get("action")
                     EVEID=action.get("event_id")
                     DELAY=action.get("Delay")
                     GraphiteInter.schedule_event(EVEID,ACTION,DELAY)
                    elif action_type=="remove_input_from_tab":
                     TABID=action.get("tab_id")
                     INPUTID=action.get("input_id")
                     GraphiteInter.remove_input_from_tab(TABID,INPUTID)
                    elif action_type=="insert_input_in_tab":
                     TABID=action.get("tab_id")
                     INPUTID=action.get("input_id")
                     POSITION=action.get("position")
                     SIZE=action.get("size")
                     GraphiteInter.insert_input_in_tab(TABID,INPUTID,POSITION,SIZE)
                    elif action_type=="remove_combo_from_tab":
                     TABID=action.get("tab_id")
                     COMBOID=action.get("combo_id")
                     GraphiteInter.remove_combo_from_tab(TABID,COMBOID)
                    elif action_type=="insert_combo_in_tab":
                     TABID=action.get("tab_id")
                     COMBOID=action.get("combo_id")
                     OPTIONS=action.get("options")
                     GraphiteInter.insert_combo_in_tab(TABID,COMBOID,OPTIONS)
                    elif action_type=="remove_slider_from_tab":
                     TABID=action.get("tab_id")
                     SLIDERID=action.get("slider_id")
                     GraphiteInter.remove_slider_from_tab(TABID,SLIDERID)

                    elif action_type=="insert_slider_in_tab":
                        FONTSIZE=action.get("fontsize")
                        POSITION=action.get("position")
                        TEXTID=action.get("text_id")
                        TABID=action.get("tab_id")
                        COLOR=action.get("color")
                        TEXT=action.get("text")
                        GraphiteInter.insert_text_in_tab(TABID,TEXTID,TEXT,FONTSIZE,POSITION,COLOR)

                    elif action_type=="insert_text_in_tab":
                      TABID=action.get("id")
                      TEXTID=action.get("text id")
                      TEXT=action.get("text")
                      FONTSIZE=action.get("fontsize")
                      POSITION=action.get("position")
                      COLOR=action.get("color")
                      GraphiteInter.insert_text_in_tab(TABID,TEXTID,TEXT,FONTSIZE,POSITION,COLOR)

                    elif action_type=="tabbackground":
                     TAB=action.get("id")
                     BG=action.get("color")
                     GraphiteInter.tabbackground(tab_id=TAB , background=BG)

                    elif action_type=="remove_tab":
                     TABID=action.get("id")
                     GraphiteInter.remove_tab(TABID)
                     
                    elif action_type == "show_notification":
                         GraphiteInter.show_notification(action.get("message", "Notificação"))

                    elif action_type == "addtextinput":
                        GraphiteInter.addtextinput(action.get("input_id"), (action.get("x", 50), action.get("y", 50)))

                    elif action_type == "slidercolor":
                        GraphiteInter.slidercolor(action.get("slider_id"), action.get("color", "blue"))

                    elif action_type == "sliderthickness":
                        GraphiteInter.sliderthickness(action.get("slider_id"), action.get("thickness", 10))

                    elif action_type == "sliderOrientation":
                        GraphiteInter.sliderOrientation(action.get("slider_id"), action.get("orientation"))

                    elif action_type == "removeBgImage":
                        GraphiteInter.removeBgImage()

                    elif action_type == "removeInput":
                        GraphiteInter.removeInput(action.get("input_id"))

                    elif action_type == "removeText":
                        GraphiteInter.removeText(action.get("text_id"))

                    elif action_type == "removeslider":
                        GraphiteInter.removeslider(action.get("slider_id"))
                        
                    elif action_type == "removebutton":
                        GraphiteInter.removebutton(action.get("button_id"))

                    elif action_type == "setmaximum":
                        GraphiteInter.setmaximum(action.get("slider_id"), action.get("max_value", 100))

                    elif action_type == "Getslidervalue":
                        GraphiteInter.Getslidervalue(action.get("slider_id"))

                    elif action_type == "insertslider":
                        GraphiteInter.insertslider(action.get("slider_id"), (action.get("x", 50), action.get("y", 50)))

                    elif action_type == "remove_combo":
                        GraphiteInter.remove_combo(action.get("combo_id"))

                    elif action_type == "get_combo_value":
                        GraphiteInter.get_combo_value(action.get("id"))
                    elif action_type == "insertcombo":
                        GraphiteInter.insertcombo(action.get("combo_id"), action.get("options", ""), (action.get("x", 50), action.get("y", 50)))

                    elif action_type=="inserttext":
                     TID=action.get("id")
                     TEXT=action.get("text")
                     FONTSIZE=action.get("fontsize")
                     POS=action.get("position")
                     COLOR=action.get("color")
                     GraphiteInter.inserttext(TID,TEXT,FONTSIZE,POS,COLOR)

                    elif action_type=="buttonposition":
                     BID=action.get("id")
                     X=action.get("posx")
                     Y=action.get("posy")
                     GraphiteInter.buttonposition(BID,X,Y)

                    elif action_type=="create_button":
                     TEXT=action.get("text") 
                     BID=action.get("id")
                     GraphiteInter.create_button(TEXT,BID,None)

                    elif action_type=="setbgimage":
                     PATH=action.get("path")
                     GraphiteInter.setbgimage(PATH)

                    elif action_type=="setbackground":
                     COLOR=action.get("color")
                     GraphiteInter.setbackground(COLOR)

                    elif action_type=="setdimensions":
                     WIDTH=action.get("width")
                     HEIGHT=action.get("height")
                     GraphiteInter.setdimensions(WIDTH,HEIGHT)

                    elif action_type=="create_window":
                     TITLE=action.get("title")
                     GraphiteInter.create_window(TITLE)
                    else:
                        print(f"⚠️ Tipo de ação desconhecido: {action_type}")
        else:
            print(f"⚠️ Função '{function_name}' não encontrada.")

    @staticmethod
    def remove_form(form_id):
     """Remove um formulário da interface gráfica."""
     form_frame = GraphiteInter.widgets.get(form_id)
     if form_frame:
        form_frame.destroy()  # Remove o frame do formulário
        del GraphiteInter.widgets[form_id]  # Remove da lista de widgets
        print(f"✅ Formulário '{form_id}' removido com sucesso!")
     else:
        print(f"⚠️ Formulário '{form_id}' não encontrado.")
    @staticmethod
    # Função para separar uma string ou lista com base em um separador
    def separate_graphite(Separate, separador):
    # Verifica se o 'o_que' é uma string e usa o método split para separar
     if isinstance(Separate, str):
        return Separate.split(separador)
    
    # Se for uma lista, tenta separar com base no separador fornecido
     elif isinstance(Separate, list):
        separated_list = []
        current_group = []
        for item in Separate:
            if item == separador:
                # Quando encontrar o separador, salva o grupo atual
                if current_group:
                    separated_list.append(current_group)
                    current_group = []
            else:
                current_group.append(item)
        
        # Adiciona o último grupo se houver algum
        if current_group:
            separated_list.append(current_group)
        
        return separated_list

     else:
        raise ValueError("O parâmetro 'o_que' deve ser uma string ou lista.")
     
    @staticmethod
    def create_menu(menu_items):
        """Cria um menu suspenso."""
        if not GraphiteInter._root:
            raise RuntimeError("A janela principal ainda não foi criada.")
        menu_bar = tk.Menu(GraphiteInter._root)
        for menu_name, commands in menu_items.items():
            menu = tk.Menu(menu_bar, tearoff=0)
            for item, action in commands.items():
                menu.add_command(label=item, command=action)
            menu_bar.add_cascade(label=menu_name, menu=menu)
        GraphiteInter._root.config(menu=menu_bar)

    @staticmethod
    def Show_External_Notification(title, message, alert_type="info"):
        """Exibe um pop-up de alerta."""
        if alert_type == "info":
            messagebox.showinfo(title, message)
        elif alert_type == "warn":
            messagebox.showwarning(title, message)
        elif alert_type == "err":
            messagebox.showerror(title, message)

    @staticmethod
    def enable_drag(itemid):
        """Permite arrastar e soltar qualquer widget baseado no itemid."""
        widget = None
        
        # Verifica se o itemid corresponde a algum tipo de widget
        if itemid in GraphiteInter._buttons:
            widget = GraphiteInter._buttons[itemid]
        elif itemid in GraphiteInter._texts:
            widget = GraphiteInter._texts[itemid]
        elif itemid in GraphiteInter._comboboxes:
            widget = GraphiteInter._comboboxes[itemid]
        elif itemid in GraphiteInter._sliders:
            widget = GraphiteInter._sliders[itemid]
        elif itemid in GraphiteInter._inputs:
            widget = GraphiteInter._inputs[itemid]

        if widget is None:
            raise ValueError(f"Widget com ID '{itemid}' não encontrado.")
        
        # Função de arrasto
        def on_drag(event):
            widget.place(x=event.x_root - GraphiteInter._root.winfo_x(), 
                         y=event.y_root - GraphiteInter._root.winfo_y())

        # Liga o evento de arrastar
        widget.bind("<B1-Motion>", on_drag)


    @staticmethod
    def CreateXMLBasedContainer(xml, xslt):
        """
        Função que cria um container HTML dentro de um programa Tkinter,
        aplicando uma transformação XSLT no XML e exibindo o resultado.
        
        Parâmetros:
        xml (str): Caminho para o arquivo XML.
        xslt (str): Caminho para o arquivo XSLT.
        """
        # Carregar XML e XSLT
        try:
            xml_tree = etree.parse(xml)
            xslt_tree = etree.parse(xslt)

            # Aplicar a transformação XSLT
            transform = etree.XSLT(xslt_tree)
            result = transform(xml_tree)  # O resultado da transformação é o HTML gerado

            # Converter o resultado para string
            result_html = etree.tostring(result, pretty_print=True, encoding="UTF-8").decode()

            # Criar um arquivo temporário para armazenar o HTML
            with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as temp_html:
                temp_html.write(result_html.encode("utf-8"))
                temp_html_path = temp_html.name  # Caminho do arquivo temporário

            # Criar o container HTML dentro da janela principal
            GraphiteInter.createHtmlContainer(temp_html_path)
            print(f"XML baseado no HTML carregado a partir de {temp_html_path}.")
        except Exception as e:
            print(f"Erro ao tentar criar o container XML baseado: {e}")

    @staticmethod
    def createHtmlContainer(HTMLFile):
        """
        Cria um container HTML dentro da janela principal criada com create_window.
        
        Parâmetro:
        HTMLFile (str): Caminho do arquivo HTML a ser carregado.
        """
        if GraphiteInter._root is None:
            print("Erro: A janela principal não foi criada. Chame 'create_window' primeiro.")
            return
        
        try:
            # Se já existir um frame HTML, remova-o primeiro
            if GraphiteInter._html_frame is not None:
                GraphiteInter._html_frame.destroy()
                print("Container HTML existente removido.")

            # Criar um novo frame HTML usando tkinterweb
            GraphiteInter._html_frame = HtmlFrame(GraphiteInter._root, horizontal_scrollbar=True)
            GraphiteInter._html_frame.pack(fill="both", expand=True)

            # Carregar o conteúdo do arquivo HTML no frame
            GraphiteInter._html_frame.load_file(HTMLFile)

            # Atualizar a janela para exibir o conteúdo HTML
            GraphiteInter._root.update_idletasks()
            print(f"Container HTML carregado a partir de {HTMLFile}.")
        except Exception as e:
            print(f"Erro ao tentar criar o container HTML: {e}")

    @staticmethod
    def removeHtmlContainer():
        """
        Remove o container HTML (HtmlFrame) da janela principal.
        """
        if GraphiteInter._html_frame is not None:
            try:
                # Destrói o HtmlFrame (remover o container da interface)
                GraphiteInter._html_frame.destroy()
                GraphiteInter._html_frame = None  # Limpa a variável
                GraphiteInter._root.update_idletasks()  # Atualiza a interface
                print("Container HTML removido com sucesso.")
            except Exception as e:
                print(f"Erro ao tentar remover o container HTML: {e}")
        else:
            print("Nenhum container HTML encontrado para remover.")

    @staticmethod
    def load_webpage(url):
        """Exibe um site e processa JS externamente."""
        if GraphiteInter._root is None:
            print("Erro: A janela principal não foi criada. Chame 'create_window' primeiro.")
            return
        
        try:
            if GraphiteInter._html_frame is not None:
                GraphiteInter._html_frame.destroy()
                print("Container HTML existente removido.")

            GraphiteInter._html_frame = HtmlFrame(GraphiteInter._root, horizontal_scrollbar=True)
            GraphiteInter._html_frame.pack(fill="both", expand=True)

            # Capturar HTML da página para buscar scripts JS
            response = requests.get(url)
            response.raise_for_status()
            html_content = response.text

            # Buscar scripts externos no HTML
            js_files = re.findall(r'<script src="(.*?)"', html_content)
            for js_file in js_files:
                js_url = url + "/" + js_file if not js_file.startswith("http") else js_file
                print(f"Processando JavaScript externo: {js_url}")
                GraphiteInter.fetch_and_execute_js(js_url)

            # Carregar a página no frame
            GraphiteInter._html_frame.load_url(url)
            GraphiteInter._root.update_idletasks()
            print(f"Site carregado: {url}")

        except Exception as e:
            print(f"Erro ao tentar carregar o site: {e}")
    @staticmethod
    def icon_dimensions(button_id, x, y):
        """
        Redimensiona o ícone de um botão.
        :param button_id: ID do botão que terá o ícone redimensionado.
        :param x: Largura desejada.
        :param y: Altura desejada.
        """
        if button_id in GraphiteInter._buttons and button_id in GraphiteInter._icons:
            button = GraphiteInter._buttons[button_id]
            icon = GraphiteInter._icons[button_id].subsample(
                GraphiteInter._icons[button_id].width() // x,
                GraphiteInter._icons[button_id].height() // y
            )
            button.config(image=icon)
            button.image = icon  # Mantém referência para evitar garbage collection
        else:
            raise ValueError(f"Botão ou ícone não encontrado para o ID '{button_id}'.")
    @staticmethod
    def add_icon_to_button(button_id, icon_path):
        """
        Adiciona um ícone a um botão pelo seu ID.
        :param button_id: ID do botão ao qual o ícone será adicionado.
        :param icon_path: Caminho do arquivo da imagem do ícone.
        """
        if button_id in GraphiteInter._buttons:
            button = GraphiteInter._buttons[button_id]
            icon = PhotoImage(file=icon_path)
            GraphiteInter._icons[button_id] = icon  # Salva o ícone original
            button.config(image=icon, compound="left")  # Ícone à esquerda do texto
            button.image = icon  # Mantém referência para evitar garbage collection
        else:
            raise ValueError(f"O botão com ID '{button_id}' não foi encontrado.")
        
    _loadings = {}

    @staticmethod
    def _get_root():
        """Obtém a referência da janela principal automaticamente."""
        if GraphiteInter._root is None:
            GraphiteInter._root = tk._default_root
            if GraphiteInter._root is None:
                GraphiteInter._root = tk.Tk()  # Cria root se não existir
        return GraphiteInter._root

    @staticmethod
    def _get_root():
        """Obtém a referência da janela principal automaticamente."""
        if GraphiteInter._root is None:
            GraphiteInter._root = tk._default_root
            if GraphiteInter._root is None:
                GraphiteInter._root = tk.Tk()  # Cria root se não existir
        return GraphiteInter._root

    @staticmethod
    def insertLoading(loadingId, pathtogif, speed=100, position=(0, 0)):
        """
        Insere um GIF animado de loading na tela.
        :param loadingId: ID do loading.
        :param pathtogif: Caminho do GIF.
        :param speed: Velocidade da animação (quanto menor, mais lento).
        :param position: Posição (x, y) do GIF na tela.
        """
        root = GraphiteInter._get_root()

        try:
            # Abrindo o GIF usando PIL
            gif = Image.open(pathtogif)
            frames = []
            
            try:
                while True:
                    frame = gif.copy()
                    frames.append(ImageTk.PhotoImage(frame))
                    gif.seek(len(frames))  # Avança para o próximo frame
            except EOFError:
                pass  # Quando chega ao fim dos frames

            if not frames:
                raise ValueError("Falha ao carregar frames do GIF.")

            # Criando Label para exibir o GIF
            label = Label(root)
            label.place(x=position[0], y=position[1])  # Define a posição

            # Armazena os dados do loading
            GraphiteInter._loadings[loadingId] = {
                "label": label,
                "frames": frames,
                "current_frame": 0,
                "speed": speed  # Armazena a velocidade
            }

            # Função para animar o GIF
            def update_frame():
                if loadingId in GraphiteInter._loadings:
                    data = GraphiteInter._loadings[loadingId]
                    frame_index = data["current_frame"]
                    data["label"].config(image=data["frames"][frame_index])
                    data["current_frame"] = (frame_index + 1) % len(data["frames"])

                    # Inverte a lógica: valores menores de speed resultam em mais lentidão
                    delay = 1000 // (data["speed"])  # Ajuste para que valores menores de speed sejam mais lentos
                    root.after(delay, update_frame)  # Atualiza conforme a nova velocidade

            update_frame()  # Inicia a animação
        except Exception as e:
            print(f"Erro ao carregar GIF: {e}")

    @staticmethod
    def removeLoading(loadingId):
        """
        Remove um loading animado.
        :param loadingId: ID do loading a ser removido.
        """
        if loadingId in GraphiteInter._loadings:
            GraphiteInter._loadings[loadingId]["label"].destroy()
            del GraphiteInter._loadings[loadingId]
        else:
            print(f"Loading '{loadingId}' não encontrado.")

    @staticmethod
    def changetodefault(json_path):
        """Destrói todos os elementos da interface e recria a partir do JSON."""
        if not GraphiteInter._root:
            raise RuntimeError("A janela principal ainda não foi criada. Use GraphiteInter.create_window() primeiro.")

        try:
            with open(json_path, "r", encoding="utf-8") as f:
                default_state = json.load(f)

            # Remover todos os elementos atuais
            for widget_dict in [GraphiteInter._buttons, GraphiteInter._texts, GraphiteInter._comboboxes, 
                                GraphiteInter._sliders, GraphiteInter._inputs, GraphiteInter._tabs]:
                for widget_id in list(widget_dict.keys()):
                    widget_dict[widget_id].destroy()
                widget_dict.clear()

            if GraphiteInter._bg_image_label:
                GraphiteInter._bg_image_label.destroy()
                GraphiteInter._bg_image_label = None

            # Restaurar estado default
            GraphiteInter.setdimensions(default_state.get("width", 800), default_state.get("height", 600))

            if "background" in default_state:
                GraphiteInter.setbackground(default_state["background"])

            if "bg_image" in default_state:
                GraphiteInter.setbgimage(default_state["bg_image"])

            for button in default_state.get("buttons", []):
                GraphiteInter.create_button(button["text"], button["id"], None)
                GraphiteInter.buttonposition(button["id"], *button["position"])

            for text in default_state.get("texts", []):
                GraphiteInter.inserttext(text["id"], text["text"], text["font_size"], text["position"], text["color"])

            for combo in default_state.get("comboboxes", []):
                GraphiteInter.insertcombo(combo["id"], ",".join(combo["options"]), combo["position"])

            for slider in default_state.get("sliders", []):
                GraphiteInter.insertslider(slider["id"], slider["position"])
                GraphiteInter.setmaximum(slider["id"], slider["max_value"])

            for input_field in default_state.get("inputs", []):
                GraphiteInter.addtextinput(input_field["id"], input_field["position"])

            for tab in default_state.get("tabs", []):
                GraphiteInter.create_tab(tab["id"], tab["label"])

            print(f"✅ Interface restaurada com sucesso a partir de '{json_path}'.")

        except Exception as e:
            print(f"Erro ao restaurar a interface: {e}")

    _config = configparser.ConfigParser()

    @staticmethod
    def ReadIniFile(ini_file, part_to_read, variable_to_read):
        """Lê um valor específico de um arquivo INI"""
        if not os.path.isfile(ini_file):
            raise FileNotFoundError(f"O arquivo '{ini_file}' não foi encontrado.")
        
        config = configparser.ConfigParser()
        config.read(ini_file, encoding="utf-8")

        if config.has_section(part_to_read) and config.has_option(part_to_read, variable_to_read):
            return config.get(part_to_read, variable_to_read)
        else:
            raise ValueError(f"A variável '{variable_to_read}' não foi encontrada na seção '{part_to_read}'.")

    @staticmethod
    def Change_ini(iniPath, part_to_change, variable, change_to):
     """Altera o valor de uma variável dentro de uma seção específica."""
     GraphiteInter.ReadIniFile(iniPath, part_to_change, variable)
 
     if not GraphiteInter._config.has_section(part_to_change):
         GraphiteInter._config.add_section(part_to_change)
 
     GraphiteInter._config.set(part_to_change, variable, change_to)
     
     # Correção aqui: passando os argumentos necessários
     GraphiteInter.Save_to_ini(iniPath, part_to_change, variable, change_to)

    @staticmethod
    def Save_to_ini(iniPath, Part_to_save, new_variable, value):
     """Adiciona ou atualiza uma variável em uma seção do INI e salva no disco."""
     # Lê o arquivo existente, se houver
     if os.path.isfile(iniPath):
         GraphiteInter._config.read(iniPath, encoding="utf-8")
 
     # Garante que a seção existe
     if not GraphiteInter._config.has_section(Part_to_save):
         GraphiteInter._config.add_section(Part_to_save)
 
     # Define a variável
     GraphiteInter._config.set(Part_to_save, new_variable, str(value))
 
     # Salva no disco
     with open(iniPath, 'w', encoding="utf-8") as configfile:
         GraphiteInter._config.write(configfile)

class DllManager:
    dll = None
    default_parameters = []
    loaded_funcname = None

    @staticmethod
    def ReadDll(dll_path):
        try:
            DllManager.dll = ctypes.WinDLL(dll_path)
            print(f"✅ DLL carregada: {dll_path}")
        except Exception as e:
            print(f"❌ Erro ao carregar DLL: {e}")

    @staticmethod
    def SetParametersAuto(funcname, *args):
        if DllManager.dll is None:
            print("❌ Nenhuma DLL carregada.")
            return

        try:
            func = getattr(DllManager.dll, funcname)
            DllManager.loaded_funcname = funcname

            # Tentativa de dedução (caso argtypes não esteja definido)
            if not hasattr(func, 'argtypes') or func.argtypes is None:
                # Suponha todos como ponteiro genérico se não houver argtypes
                func.argtypes = [ctypes.c_void_p] * len(args)

            converted_args = []
            for i, argtype in enumerate(func.argtypes):
                raw_value = args[i]

                # Conversão automática básica
                if argtype == ctypes.c_void_p:
                    if raw_value == "None":
                        converted_args.append(ctypes.c_void_p(None))
                    else:
                        converted_args.append(ctypes.c_void_p(int(raw_value)))
                elif argtype == ctypes.c_char_p:
                    converted_args.append(ctypes.c_char_p(str(raw_value).encode('utf-8')))
                elif argtype == ctypes.c_wchar_p:
                    converted_args.append(ctypes.c_wchar_p(str(raw_value)))
                elif argtype == ctypes.c_int:
                    converted_args.append(ctypes.c_int(int(raw_value)))
                elif argtype == ctypes.c_uint:
                    converted_args.append(ctypes.c_uint(int(raw_value)))
                elif argtype == ctypes.c_bool:
                    converted_args.append(ctypes.c_bool(bool(raw_value)))
                else:
                    # fallback seguro
                    converted_args.append(argtype(raw_value))

            DllManager.default_parameters = converted_args
            print("✅ Parâmetros definidos com sucesso.")

        except Exception as e:
            print(f"❌ Erro ao definir parâmetros automaticamente: {e}")

    @staticmethod
    def UseDllFunction(funcname=None, parameters=None):
        if DllManager.dll is None:
            print("❌ Nenhuma DLL carregada.")
            return

        try:
            funcname = funcname or DllManager.loaded_funcname
            func = getattr(DllManager.dll, funcname)
            func.restype = ctypes.c_int  # Valor padrão de retorno

            args = parameters if parameters else DllManager.default_parameters
            result = func(*args)
            print(f"✅ Função '{funcname}' chamada. Resultado: {result}")
            return result

        except Exception as e:
            print(f"❌ Erro ao chamar função: {e}")
            
class Locator:
    @staticmethod
    def Locate_File(diskletter, fileName):
        search_root = f"{diskletter.upper()}:\\"
        fileNameLower = fileName.lower()

        for root, dirs, files in os.walk(search_root):
            for f in files:
                if f.lower() == fileNameLower:
                    return os.path.join(root, f)
        
        return ""
    
    @staticmethod
    def Locate_multiple(dependencies_source, section=None, numberoffiles=None):
        """
        Localiza múltiplos arquivos definidos em um arquivo INI ou dicionário.

        Args:
            dependencies_source (str/dict): Caminho para o arquivo INI ou um dicionário com as dependências.
            section (str, opcional): Seção do arquivo INI que contém as dependências, caso seja passado um arquivo INI.
            numberoffiles (int, opcional): Número total de arquivos a procurar, caso seja passado um arquivo INI, deve ser passado um a mais (6 arquivos -> 7).
        
        Returns:
            list: Lista com os caminhos encontrados ou "Não encontrado".
        """
        dependencias_encontradas = []

        # Caso o parâmetro seja um arquivo INI
        if isinstance(dependencies_source, str):
            import configparser
            config = configparser.ConfigParser()
            config.read(dependencies_source)

            for i in range(1, numberoffiles + 1):  # Inclui o último número
                chave = str(i)
                valor = config.get(section, chave)

                caminho = Locator.Locate_File("C", valor)

                dependencias_encontradas.append(caminho if caminho else "Não encontrado")
        
        # Caso o parâmetro seja um dicionário
        elif isinstance(dependencies_source, dict):
            for chave, valor in dependencies_source.items():
                caminho = Locator.Locate_File("C", valor)

                dependencias_encontradas.append(caminho if caminho else "Não encontrado")

        return dependencias_encontradas