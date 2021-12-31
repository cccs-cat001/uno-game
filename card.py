color_full = ['','Red','Yellow','Blue','Green']
color_repr = ['S','R','Y','B','G']
num_full = ['Zero','One','Two','Three','Four','Five','Six','Seven','Eight','Nine','Draw Two','Reverse','Skip','Draw Four','Wild','Blank']
num_repr = ['0','1','2','3','4','5','6','7','8','9','D2','R','S','D4','W','B']
index_d2 = 10
index_r = 11
index_s = 12
index_d4 = 13
index_w = 14
index_b = 15

class Card:
    def __init__(self,color: str,num: str):
        self.color: str = color
        self.num: str = num
        self.draw: int = 0
        if num == index_d2:
            self.draw = 2
        if num == index_d4:
            self.draw = 4

    def __repr__(self):
        return color_repr[self.color] + num_repr[self.num]

    def __str__(self):
        return (color_full[self.color] + ' ' + num_full[self.num]).strip()

    @property
    def is_special(self):
        return self.num > 9


class BlankCard(Card):
    def __init__(self,text: str):
        super().__init__(0,index_b)
        self.text: str = text

    def __repr__(self):
        return 'SB'

    def __str__(self):
        return 'Blank:\{{}\}'.format(self.text)
