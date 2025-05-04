class length:
    _num = 0

    @classmethod
    def num(cls, value):
        cls._num = value

    @classmethod
    def text(cls):
        if cls._num <= 0:
            return "you don't have a zipp"
        elif cls._num <= 3:
            return "too short"
        elif cls._num < 7:
            return "short"
        elif cls._num <= 10:
            return "medium"
        elif cls._num <= 15:
            return "good"
        elif cls._num <= 20:
            return "perfect"
        else:
            return "tall"
