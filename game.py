import random
from google import genai

POS_OUTCOME=1
NEU_OUTCOME=0
NEG_OUTCOME=-1

class Game:
    def __init__(self):
        self.completion_meter=3
        self.win_condition=7
        self.loss_condition=0
        self.current_scene=''
        self.tempo=0
        self.game_context=[]
        self.client = genai.Client()
        self.chat = self.client.chats.create(model="gemini-2.5-flash")
        
    def initialize_game(self):
        # set he inintial scene
        response = self.chat.send_message("You are the narrator for a classic dungeon crawler style text based RPG.  You will guide the player through a series of scenes while they make decisions that lead to their ultimate success or failure. Begin by providing a two to three brief sentences to set the stage for the player, followed by one or two sentences describing the objective at the end of the dungeon")
        print(response.text)
        self.game_context.append(response.text)
        return
    
    def play_game(self):
        while self.completion_meter not in [self.win_condition, self.loss_condition]:
            scene=self.request_scene()
            print(scene,'\n')
            #
            options=self.request_options()
            print('1. ', options[0])
            print('2. ', options[1])
            print('\n')
            selection=''
            while selection not in ['1','2']:
                selection=input("Make a selection: ")
            selected_option=options[int(selection)-1]

            # act on the choice made by the player
            # currently just random, TODO game logic later
            self.tempo=self.calculate_result()
            self.completion_meter+=self.tempo
            text_result=self.request_result(self.tempo)
            print(text_result,'\n')
        if self.completion_meter==self.win_condition:
            print("you win :)")
        else:
            print("you lose :(")
        return
    def calculate_result(self):
        # choose a result randomly from [-1,0,1]
        # corresponding to negative, neutral, and positive outcome
        return random.choice([POS_OUTCOME,NEU_OUTCOME,NEG_OUTCOME])
    
    def request_scene(self):
        background = ' '.join(self.game_context)
        
        scene='placeholder_scene ({})'.format(self.completion_meter) 
        return scene
    def request_options(self):
        return ['option 1','option 2']
    def request_result(self,num_result):
        result='placeholder result ({})'.format(num_result)
        return result
    def render(self,text):
        print(text)
    
def main():
    random.seed()
    g = Game()
    g.initialize_game()
    g.play_game()
    return

if __name__=="__main__":
    main()

# part 1: silly little dungeon crawler
#
# basic game loop
#  - determine objective by prompting LLM
#  - while game is not won or lost:
#    - present player with (n) options:
#    - player makes decision.
#      - outcome of decision determined using dice roll
#      - outcome moves the needle on the win/loss meter
#    - if game is won/lost
#      end game

# each step should go: [scene, options->decision, result]

