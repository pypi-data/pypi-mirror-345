'''
ACECalculator
====
Fast calculate the cyclone ACE.
'''
__all__ = []

TROPICAL = 0
SUBTROPICAL = 1
ETROTRO = 2

__version__ = "0.1.0"

class ACECalculator:
    '''
    The ACECalculator class.
    '''
    def __init__(self):
        self.ACE_list = []
        self.now_mode = None

    def add_knot(self, knots:int, mode=None,index:int = None):
        '''
        Add the knots.

        :example:  
        >>> import ACE_calc
        >>> ACE_calc.set_mode(ACE_calc.TROPICAL)
        >>> ACE_calc.add_knot(50)
        >>> ACE_calc.add_knot(45, 2)
        >>> ACE_calc.add_knot(35, 2, 1)
        >>> ACE_calc.output_knot()
        >>> """index = 1, knots = 50, mode = tropical
        index = 2, knots = 35, mode = subtropical
        index = 3, knots = 45, mode = subtropical
        """
        
        :param int knots: The knots you want to add.
        :param mode=now_mode: The mode you want to add.
        :param index=len(ACE_list): The index you want to insert in the after.

        :raises ValueError: Your input or mode is invalid.

        '''
        mode = self.now_mode if mode is None else mode
        index = len(self.ACE_list) if index is None else index

        if mode is None:
            raise ValueError('Variable now_mode is not defined.')
        elif mode not in [i for i in range(3)]:
            raise ValueError('This mode is not defined.')
        elif knots < 0:
            raise ValueError('Variable knots connot < 0.')
        elif index < 0:
            raise ValueError('Variable index connot < 0.')
        else:
            self.ACE_list.insert(index,[knots,mode])
        return self

    def add_knots(self, knots:int, length:int, start:int=None, mode=None):
        '''
        Add the some knots.

        :example:  
        >>> import ACE_calc
        >>> ACE_calc.set_mode(ACE_calc.TROPICAL)
        >>> ACE_calc.add_knots(50, 3)
        >>> ACE_calc.output_knot()
        >>> """index = 1, knots = 50, mode = tropical
        index = 2, knots = 50, mode = tropical
        index = 3, knots = 50, mode = tropical
        """
        
        :param int knots: The knots you want to add.
        :param mode=now_mode: The mode you want to add.
        :param index=len(ACE_list): The index you want to insert in the after.

        :raises ValueError: Your input or mode is invalid.
        '''
        mode = self.now_mode if mode is None else mode
        start = len(self.ACE_list) if start is None else start
        for i in range(length):
            self.add_knot(knots, mode, start + i)
        return self

    def del_knot(self, index:int):
        del self.ACE_list[index+1]
        return self

    def del_knots(self, indexes:list[int]):
        for index in indexes:
            self.del_knot(index)
        return self

    def calc_ACE(self):
        ace = 0
        for i in self.ACE_list:
            if i[1] == TROPICAL and i[0] >= 35:
                ace += (10**-4 * (i[0]**2))
        return ace

    def upload(self, file_name):
        from sys import prefix
        from json import dump

        with open(f'{prefix}/ACE_calc/{file_name}.json', 'w') as f:
            dump(self.ACE_list, f)
        return self

    def download(self, file_name):
        from sys import prefix
        from json import load

        with open(f'{prefix}/ACE_calc/{file_name}.json', 'r') as f:
            self.ACE_list = load(f)
        
        for k,v in self.ACE_list.items():
            if (
                len(v) != 2 or 
                v[1] not in [i for i in range(3)] or
                v[0] < 0
                ):
                raise ValueError('This file is not valid.')
            self.add_knot(v[0], v[1], int(k))
        return self
            
    def output_knots(self):
        '''
        Format print your knot list.

        :exmanple: 
        >>> import ACE_calc
        >>> ACE_calc.set_mode(ACE_calc.TROPICAL)
        >>> ACE_calc.add_knot(50)
        >>> ACE_calc.output_knot()
        "index = 1, knots = 50, mode = tropical"
        '''
        out_texts = []
        index = 1
        for i in self.ACE_list:
            if i[1] == TROPICAL:
                mode_text = 'tropical'
            elif i[1] == SUBTROPICAL:
                mode_text = 'subtropical'
            elif i[1] == ETROTRO:
                mode_text = 'etrotro'
            else:
                mode_text = None

            out_texts.append(f'index = {index}, knots = {i[0]}, mode = {mode_text}')
            index += 1
        print('\n'.join(out_texts))
        return self

    def get_knots_indexes(self, knots) -> list[int]:
        '''
        Get all the ACE indexes (index starts from 1).

        :exmanple: 
        >>> ACE_calc.add_knot(50)
        >>> ACE_calc.add_knot(45, 2)
        >>> ACE_calc.add_knot(50, 2, 1)
        >>> get_ACE_indexes(50)
        "[1, 2]"

        :param int knots: The knots you want to search.

        :return list[int]: All the knots list.
        '''
        indexes = []
        for index in range(len(self.ACE_list)):
            if self.ACE_list[index][0] == knots:
                indexes.append(index + 1)
        return indexes

    def set_mode(self, mode):
        '''
        Set the cyclone mode.

        *If you not setting,you cannot add the knots.*
        
        :param mode: The cyclone mode.
        :raises ValueError: Your input is invalid.
        '''
        if mode in [i for i in range(3)]:
            self.now_mode = mode
            now_mode = mode
        else:
            raise ValueError('This mode is not defined.')
        return self

    def clear(self):
        self.ACE_list = []
        return self
    
    def __repr__(self):
        return f'ACECalculator(ACE_list={self.ACE_list}, now_mode={self.now_mode})'
    
    def __str__(self):
        return f'ACE_list={self.ACE_list}, now_mode={self.now_mode}'
    
    def __len__(self):
        return len(self.ACE_list)
    
    def __getitem__(self, index):
        return self.ACE_list[index]
    
    def __setitem__(self, index, value):
        self.ACE_list[index] = value
        return self
    
    def __delitem__(self, index):
        del self.ACE_list[index]
        return self
    
    def __iter__(self):
        return iter(self.ACE_list)
    
    def __add__(self, other):
        if isinstance(other, ACECalculator):
            return ACECalculator(ACE_list=self.ACE_list + other.ACE_list, now_mode=self.now_mode)
        else:
            raise TypeError('You can only add ACECalculator object.')

clacualtor = ACECalculator()

def main():
    pass

if __name__ == '__main__':
    main()