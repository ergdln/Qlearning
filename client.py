import connection as cn
import random
import numpy

MATRIX = None
BOT_ACTIONS = ['left','right','jump']
BOT_DIRECTIONS = ['north','east','south','west']

def converting_states(state_in_binary: str):
    plat_mask = 0b1111100
    direction_mask = 0b0000011

    int_state = int(state_in_binary, 2) #converte de binário pra decimal
    #aplica uma mascara de bits e faz um shift right pra que os bits fiquem no local correto
    platform = (int_state & plat_mask) >> 2
    direction = (int_state & direction_mask)

    #acha o estado entre 0-95 a partir da direção e plataforma
    state = platform * 4 + direction
    return state
    
def checker(socket, times: int, start: int):
    current_state = start * 4
    total_reward = 0

    aux = 0
    while True:
        #busca na tabela a melhor ação pra esse estado
        current_action = numpy.where(MATRIX[current_state] == max(MATRIX[current_state]))[0][0]

        #recebe a recompensa e o estado novos a partir da ação escolhida
        bit_state, reward = cn.get_state_reward(socket, BOT_ACTIONS[current_action])
        new_state = converting_states(bit_state)

        total_reward += reward
        current_state = new_state

        aux += 1
        if aux >= times:
            break

def exploration(socket, movements: int, start: int):
    current_state = start * 4 # *4, pois cada plataforma tem 4 estados possíveis e sempre respawna virado pro norte

    for step in range(movements):
        print('Step: ' , step)

        #busca na tabela a melhor ação para o estado atual
        best_known = numpy.where(MATRIX[current_state] == max(MATRIX[current_state]))[0][0]
        random_action = random.randint(0, 2)

        # seleciona se vai utilizar acao aleatoria ou nao
        if step % 5 > 1:
            current_action = best_known
        else:
            current_action = random_action

        #recebe a recompensa e o estado novos a partir da ação escolhida
        bit_state, reward  = cn.get_state_reward(socket, BOT_ACTIONS[current_action])
        new_state = converting_states(bit_state)
        main_equation(reward, current_state, current_action, new_state)
        current_state = new_state

        #Atualiza a tabela a partir da equacao
def main_equation(rec: int, #recompensa
                 ps: int, #estado anterior
                 pa: int, #acao realizada
                 cs: int, #estado atual
                 lr: float = 0.2, #learning rate; alfa
                 d: float = 0.9): #discount; gamma 
   
    MATRIX[ps][pa] += lr * (rec + d * max(MATRIX[cs]) - MATRIX[ps][pa])
    return MATRIX[ps][pa]

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