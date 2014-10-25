from bot import Bot


class HumanBot(Bot):
    def turn(self):
        # Does not work
        action = input('Action: ').split()
        if action[0] == 'raise':
            return self.action('raise', amount=int(action[1]))
        elif action[0] == 'check' or action[0] == 'call':
            return self.action(action[0])
        else:
            return self.action('fold')