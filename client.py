import connection as cn
import random
import numpy

MATRIX = None
BOT_ACTIONS = ['left','right','jump']
BOT_DIRECTIONS = ['north','east','south','west']

#converte as informações 
def converting_states(state_in_binary: str):
    plat_mask = 0b1111100
    direction_mask = 0b0000011
    int_state = int(state_in_binary, 2) 
    platform = (int_state & plat_mask) >> 2
    direction = (int_state & direction_mask)
    state = platform * 4 + direction
    return state
    
    
#Percore apenas pelos melhores caminhos aprendidos, sem alterar a Qtable   
def checker(socket, steps: int, pos: int):
    state = pos * 4
    total = 0
    aux = 0
    while True:
        action = numpy.where(MATRIX[state] == max(MATRIX[state]))[0][0]
        bit_state, reward = cn.get_state_reward(socket, BOT_ACTIONS[action])
        new_state = converting_states(bit_state)
        total += reward
        state = new_state
        aux += 1
        if aux >= steps:
            break

#Função principal de exploração e aprendizado
def exploration(socket, movements: int, start: int):
    state = start * 4 
    for step in range(movements):
        print('Step: ' , step)

        best = numpy.where(MATRIX[state] == max(MATRIX[state]))[0][0]
        random = random.randint(0, 2)

        # política de exploration x exploitation
        if step % 5 > 1:
            action = best
        else:
            action = random
        bit_state, reward  = cn.get_state_reward(socket, BOT_ACTIONS[action])
        new_state = converting_states(bit_state)
        main_equation(reward, state, action, new_state)
        state = new_state

#equação principal
def main_equation(rec: int, #recompensa
                 ps: int, #estado anterior
                 pa: int, #acao realizada
                 cs: int, #estado atual
                 lr: float = 0.2, #learning rate; alfa
                 d: float = 0.9): #discount; gamma 
   
    MATRIX[ps][pa] += lr * (rec + d * max(MATRIX[cs]) - MATRIX[ps][pa])
    return MATRIX[ps][pa]

#função de inicialização
def main():
    game = cn.connect(2037)
    global MATRIX
    if(game != 0):
        while True:
            instruction = input('update; matrix; exploration; checker or quit ')
           
            match instruction:
                case 'update':
                    #update matrix
                    numpy.savetxt('resultado.txt', MATRIX)
                    #update checker
                    new_table = [numpy.argmax(row) for row in MATRIX]
                    best_actions = [BOT_ACTIONS[index] for index in new_table]
                    numpy.savetxt('best_actions.txt', best_actions, fmt='%s')
                    print('updated')

                case 'matrix':
                    try:
                        with open('resultado.txt') as file:
                         MATRIX = numpy.loadtxt(file)
                        print("MATRIX[0]: ", MATRIX[0])     
                    except FileNotFoundError:
                        print("error 404")
                        pass

                case 'exploration':
                    if MATRIX is None:
                        print('Carregue uma tabela antes')
                    else:
                        try:
                            movements = int(input('Insert movements (int):\n'))
                            start = int(input('Initial plataform:\n'))
                        except ValueError:
                            print('erro 400, bad request')
                        else:
                            exploration(game, movements, start)
                            print('exploration ended with sucess')

                case 'checker':
                    if MATRIX is None:
                        print('error 404, matrix not found')
                    else:
                        try:
                            movements = int(input('Insert movements (int):\n'))
                            start = int(input('Initial plataform:\n'))
                        except ValueError:
                            print('error 400, bad request')
                        else:
                            checker(game, movements, start)
                            print('checker ended with sucess')

                case 'quit':
                    game.close()
                    break

if __name__ == "__main__":
    main()