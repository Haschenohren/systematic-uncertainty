#!/usr/bin/python3
#utility module

tables= {
    'AuAu': ((.09, .09, .11, .11, .10, .10),
             (.10, .10, .11, .11, .11, .11),
             (.14, .14, '-', '-', .14, .14)),
    'dAu': ((.08, .08, .13, .13, .09, .09),
            (.09, .09, .13, .13, .11, .11))
}

def systematic_uncertainty(
        collision_system,
        particle_species,
        particle_charge,
        transverse_momentum,
        value):
    '''calculates systematic uncertainty using table 4 of the paper'''
    col = 0
    if particle_species == 'kaon':
        col = 2
    elif particle_species == 'prot':
        col = 4
    if particle_charge == 'neg':
        col += 1
    
    row = 2
    if transverse_momentum < 5 or collision_system == 'dAu':
        row = 1
    if transverse_momentum < 3:
        row = 0
    
    return tables[collision_system][row][col] * value