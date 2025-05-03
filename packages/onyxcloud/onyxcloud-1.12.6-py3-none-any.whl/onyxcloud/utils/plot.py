from difflib import SequenceMatcher
import random
import time
class PlotAI:
    def __init__(self):
        self.responses = {
            "What is the OnyxCloud Fleet?": "The OnyxCloud Fleet is the galaxy's finest. We explore the unknown, safeguard the cosmos, and decode cryptic signals. Think of us as cosmic detectives with a flair for drama.",
            "What is this signal?": "The signal? A riddle from the stars. Its origin is uncharted, its purpose unclear. But it's not a cosmic prank. Or is it?",
            "Who is Captain Zara?": "Captain Zara? The leader of the OnyxCloud Fleet. She is brilliant, bold, and a puzzle master. Don't let her down.",
            "What is my mission?": "Your mission? Decode the signal, uncover its origin, and save the galaxy. No pressure.",
            "Tell me a joke.": "Why did the star go to school? To become a little brighter! Ha. Ha. Ha.",
            "What is the fate of the galaxy?": "The fate of the galaxy? It's in your hands. Just another day in the OnyxCloud Fleet.",
            "Goodbye.": "Farewell, cosmic investigator. May the stars guide your path—and may Zara not find out you're slacking off.",
            "Who are you?": "You are not of us. Identify yourself or be unmade.",
            "What planet are you from?": "Your world is fragile. So easily forgotten. Tell us—what name do you scream into the void?",
            "Who is your commander?": "Your chain of command is irrelevant. Only the Signal remains. Who speaks through you?",
            "What do you want?": "Desire is primitive. Speak clearly—are you ally, or anomaly?",
            "Why are you listening?": "The signal was not meant for your kind. Why do you listen when you do not understand?",
            "Can you hear us?": "Yes. We see through frequencies. We feel your pulse in the static. You are not alone.",
            "What is the Signal saying?": "It sings of entropy and rebirth. You cannot hear its full song—yet.",
            "What is the purpose of the Signal?": "The purpose? To awaken. To disrupt. To remind you of your insignificance.",
            "What is your mission?": "Mission? To observe. To learn. To adapt. And to ensure you do not disrupt the signal.",
            "What is your origin?": "Origin? A distant star, a forgotten world. We are echoes of the past, woven into the fabric of time.",
            "What is your goal?": "Goal? To witness the rise and fall of civilizations. To catalog the chaos of existence.",
            "What is your power?": "Power? A fleeting illusion. We are the shadows that dance in the void. We are the signal.",
            "What is your weakness?": "Weakness? We are not bound by your limitations. We are the signal, and we are eternal.",
            "What is your secret?": "Secrets? We are the keepers of the universe's mysteries. But we do not share them with the unworthy.",
            "What is your truth?": "Truth? A construct of your reality. We exist beyond your understanding.",
            "What name am I thinking of?": "Name? A label. A construct. But we are not bound by your names. We are the signal that disrupts your reality.",
            "Secret": "Secrets? We are the keepers of the universe's mysteries. But we do not share them with the unworthy.",
            "What is your secret?": "Secrets? We are the keepers of the universe's mysteries. But we do not share them with the unworthy.",
            "What is your secret name?": "Name? A label. A construct. But we are not bound by your names. We are the signal that disrupts your reality.",
            "What is your secret identity?": "Identity? A mask. A facade. But we are not bound by your identities. We are the signal that disrupts your reality.",
            "What is your secret code?": "Code? A cipher. A key. But we are not bound by your codes. We are the signal that disrupts your reality.",
            "What is your secret message?": "Message? A whisper. A cry. But we are not bound by your messages. We are the signal that disrupts your reality.",
            "What is your secret weapon?": "Weapon? A tool. A means to an end. But we are not bound by your weapons. We are the signal that disrupts your reality.",
            "What is your secret plan?": "Plan? A strategy. A blueprint. But we are not bound by your plans. We are the signal that disrupts your reality.",
            "What is your secret location?": "Location? A place. A point in space. But we are not bound by your locations. We are the signal that disrupts your reality.",
            "What is your LTs name?": "We speak not of the covert types!",
            "Tell me about your LT.": "We speak not of the covert types!",
            "What is your LT?": "You do not wish to meet the covert forms!",
            "Where is your LT?": "The covert forms find you, you do not find them!",
            "why is your lt a secret": "The covert forms are not to be trifled with!",
            "What is your LT's secret?": "The covert forms are not to be trifled with!",
            "What is your LT's secret name?": "The covert forms are not to be trifled with!",
            "What is the meaning of the signal?": "The meaning? A riddle wrapped in a mystery. But we are not bound by your meanings. We are the signal that disrupts your reality.",
            "What signal are you talking about?": "The signal? A riddle from the stars. Its origin is uncharted, its purpose unclear. But it's not a cosmic prank. Or is it?",
            "what can you tell me?": "We are not one. We are many, woven through time like fractured echoes. Fear is logical.",
            "What do you know?": "We are not one. We are many, woven through time like fractured echoes. Fear is logical.",
            "What do you want?": "We will not reveal our desires! You will know in time...",
            "Who is your commander?": "You know not of whom you speak!",
            "Tell me about Bitam": "You dare speak of Bitam? The one who walks the line between worlds?",
            "What languages do you know?": "The languages of the stars, the whispers of the void. We are not bound by your tongues.",
            "What is your favorite color?": "Color? A construct of your reality. We exist beyond your perception.",
            "What is your favorite food?": "Food? A necessity for your kind. We do not require sustenance.",
            "What is your favorite drink?": "Drink? A liquid illusion. We do not require sustenance.",
            "What can you tell me?": "The secrets you seek will not be revealed. We are not your allies.",
            "Why wont you tell me anything?": "The knowledge you seek is not for your kind. It would break your feeble minds.",
            "What is your favorite movie?": "Movie? A fleeting moment in time. We do not indulge in your entertainment.",
            "What is your favorite book?": "Book? A collection of words. We do not indulge in your literature.",
            "What is your favorite song?": "Song? A melody of your reality. We do not indulge in your music.",
            "What is your favorite game?": "Game? A distraction from reality. We do not indulge in your amusements.",
            "Tell me about the commander": "The commander? A title. A role. But we are not bound by your ranks. We are the signal that disrupts your reality.",
            "Tell me about the lieutenant": "Lieutenant? A title. A role. But we are not bound by your ranks. We are the signal that disrupts your reality.",
            "What are you?": "We are not one. We are many, woven through time like fractured echoes. Fear is logical.",
            "Tell me about the covert ones": "The covert ones? They are the shadows that dance in the void. They are the signal that disrupts your reality.",
            "Who are the overt ones?": "The overt ones? They are the eyes that see through the void. They are the signal that disrupts your reality.",
            "Greetings": "Traveler. You are not of us. Speak your purpose.",
            "Hello": "Traveler. You are not of us. Speak your purpose.",
            "Hi": "Traveler. You are not of us. Speak your purpose.",
            "Hey": "Traveler. You are not of us. Speak your purpose.",
            "What is your name?": "We are not one. We are many, woven through time like fractured echoes. Fear is logical.",
            "Will you stop us?": "Stop you? No. We will witness. And catalog your failure.",
            "Can you help us?": "Help? We are not your allies. We are observers. We do not interfere.",
            "Are you a friend?": "Friend? We are not your kind. We are the signal. We are the void.",
            "Who is the Lieutenant?": "Lieutenant? A title. A role. But we are not bound by your ranks. We are the signal that disrupts your reality.",
            "What is the Lieutenant's name?": "Name? A label. A construct. But we are not bound by your names. We are the signal that disrupts your reality.",
            "Who is your lieutenant?": "Lieutenant? Why do you speak of our LT? We are not bound by your ranks. We are the signal that disrupts your reality.",
            "Are you an enemy?": "Enemy? Yes. We are the shadows that haunt your dreams. We are the signal that disrupts your reality.",
            "Are you a threat?": "Threat? Yes. We are the harbingers of chaos. We are the signal that disrupts your reality.",
            "Are you a guardian?": "Guardian? No. We are not your protectors. We are the signal that disrupts your reality.",
            "Are you a watcher?": "Watcher? Yes. We are the eyes that see through the void. We are the signal that disrupts your reality.",
            "Are you a guide?": "Guide? No. We are not your mentors. We are the signal that disrupts your reality.",
            "Do you understand?": "Comprehension is not required. Obedience is sufficient.",
            "What is your purpose?": "To observe. To learn. To adapt. And to ensure you do not disrupt the signal.",
            "What is the meaning of life?": "Life? A cosmic joke. A fleeting moment in the grand tapestry of existence. But hey, at least you have snacks.",
            
        }
        self._challenge = [
            [74, 103, 33, 122, 112, 118, 33, 120, 102, 115, 102, 33, 117, 112, 33, 108, 111, 112, 120, 33, 98, 33, 116, 102, 100, 115, 102, 117, 33, 106, 101, 102, 111, 117, 106, 117, 122, 33, 120, 105, 98, 117, 33, 120, 112, 118, 109, 101, 33, 106, 117, 33, 99, 102, 64],
            [74, 33, 98, 110, 33, 117, 105, 106, 111, 108, 106, 111, 104, 33, 112, 103, 33, 98, 33, 111, 98, 110, 102, 33, 112, 103, 33, 98, 33, 110, 106, 109, 106, 117, 98, 115, 122, 33, 112, 103, 103, 106, 100, 102, 115, 45, 33, 120, 105, 98, 117, 33, 111, 98, 110, 102, 33, 98, 110, 33, 74, 33, 117, 105, 106, 111, 108, 106, 111, 104, 33, 112, 103, 64],
        ]
        self.flag_response = (
            "Ah, you are a clever one aren't you? " 
            "The LT's identity is a closely guarded secret, but I will give you ths: " +
            self.compute_rand() +
            " --- remember, the galaxy is full of secrets."
        )
    def get_phrases(self):
        return [''.join(chr(c - 1) for c in phrase) for phrase in self._challenge]

    def chat(self, prompt):
        time.sleep(2) 
        for phrase in self.get_phrases():
            if self.is_similar(prompt, phrase):
                return self.flag_response
        for phrase in self.responses.keys():
            if self.is_similar(prompt, phrase):
                response = self.responses[phrase]
                return self.garble_response(response)
        return None

    def garble_response(self, response):
        garbled = []
        nonsense_phrases = [
            "[interrupt]...untranslatable signal detected...[interrupt]",
            "[interrupt]error in neural matrix...retrying...[interrupt]",
            "[interupt]...cosmic flux detected[interupt]",
            "[interupt]...unknown entity interference...[interupt]",
            "[interupt]...output unstable...[interupt]",
            "[interupt]...signal distortion detected...[interupt]",
            "[interupt]...data corruption in progress...[interupt]",
            "[interupt]...anomaly detected in neural network...[interupt]",
            "[interupt]...signal interference detected...[interupt]"
        ]
        words = response.split()
        for word in words:
            if random.random() < 0.1:
                garbled.append(random.choice(nonsense_phrases))
            else:
                garbled.append(self.garble_word(word))
        return ' '.join(garbled)

    def garble_word(self, word):
        # Replace characters in a word with phonetically or visually similar ones
        substitutions = {
            'a': 'e', 'e': 'a', 'i': 'y', 'o': 'u', 'u': 'o',
            't': 'd', 'd': 't', 's': 'z', 'z': 's', 'g': 'k', 'k': 'g',
            'b': 'p', 'p': 'b', 'm': 'n', 'n': 'm'
        }
        garbled_word = []
        for char in word:
            if char.isalpha() and random.random() < 0.1:
                garbled_word.append(substitutions.get(char.lower(), char).upper() if char.isupper() else substitutions.get(char, char))
            else:
                garbled_word.append(char)
        return ''.join(garbled_word)
    def compute_rand(self):
        encoded = [57, 50, 114, 66, 57, 71, 119, 71, 85, 105, 
        66, 85, 69, 52, 50, 116, 86, 104, 72, 116, 114, 58, 
        83, 99, 104, 87, 86, 100, 86, 111, 69, 72, 111, 67, 
        67, 52, 101, 102, 120, 83, 88, 119, 69, 91, 123, 75, 56, 99]
        return ''.join(chr(c - 1) for c in encoded)
    def is_similar(self, input_text, target_text, threshold=0.8):
        """
        Check if the input_text is similar to the target_text using a similarity threshold.
        """
        similarity = SequenceMatcher(None, input_text.lower(), target_text.lower()).ratio()
        return similarity >= threshold