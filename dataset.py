#!/usr/bin/python3

class dataset:
    '''Represents a 2D array of string data, with column headers'''
    
    def __init__(self, data, headers, delimiter='\t'):
        '''data is either delimited string, or 2d list, must have same number of
           column headers as columns in data. Headers must be 2d list'''
        if type(data) == str:
            self.data = [line.split(delimiter) for line in data.split('\n')]
        else:
            self.data = data
        self.headers = headers
    
    
    def __str__(self):
        '''str representation as a formatted table'''
        table = [self.headers] + self.data
        num_cols = len(self.headers)
        col_widths = [0] * num_cols
        #Determine column widths by max widths of each field in each column
        for row in table:
            for c, field in enumerate(row):
                col_widths[c] = max(col_widths[c], len(field))
        #construct string with padded fields
        s = '\n'.join(
                '  '.join(f'{field:{col_widths[c]}}' 
                    for c, field in enumerate(row))
                for row in table)
        return s
    
    
    def create_column(self, col_name, field_func):
        '''creates a new column of data using the given function.
           The field function takes the current row as an argument (varargs),
           and returns the *string* value of the new field'''
        self.headers.append(col_name)
        for row in self.data:
            row.append(field_func(*row))