import json
class Data:
    def __init__(self, ui):
        self.ui = ui
        with open('data.txt') as data_file:
            data = json.load(data_file)
            data_file.close()
        self._coins = data['coins']
        self._health = data['health']
        self.ui.create_hearts(self._health)

        self.unlocked_level = data['unlocked_level']
        self.current_level = data['current_level']

    @property
    def health(self):
        return self._health

    @health.setter
    def health(self, value):
        self._health = value
        self.ui.create_hearts(value)

    @property
    def coins(self):
        return self._coins

    @coins.setter
    def coins(self, value):
        self._coins = value
        if self.coins >= 100:
            self.coins -= 100
            self.health +=1
        self.ui.display_coins(self.coins)