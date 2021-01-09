import PySimpleGUI as sg


# Blocking form that doesn't close
def ChatBot():
    form = sg.FlexForm('Chat Window', auto_size_text=True, default_element_size=(30, 2))
    layout = [[(sg.Text('This is where standard out is being routed', size=[40, 1]))],
              [sg.Output(size=(80, 20))],
              [sg.Multiline(size=(70, 5), enter_submits=True),
               sg.ReadFormButton('SEND', button_color=(sg.YELLOWS[0], sg.BLUES[0])),
               sg.SimpleButton('EXIT', button_color=(sg.YELLOWS[0], sg.GREENS[0]))]]
    # notice this is NOT the usual LayoutAndRead call because you don't yet want to read the form
    # if you call LayoutAndRead from here, then you will miss the first button click
    form.Layout(layout)
    # ---===--- Loop taking in user input and using it to query HowDoI web oracle --- #
    while True:
        button, value = form.Read()
        if button == 'SEND':
            print(value)
        else:
            break

ChatBot()