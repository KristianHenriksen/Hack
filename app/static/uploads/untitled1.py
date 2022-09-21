#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 27 12:55:18 2021

@author: kristianhenriksen
"""

"""
dette programmet skal finne ut hvor langt et objekt har falt etter en gitt tid
"""

#a)

tid = float(input("hvor lenge har objektet falt:" ))
print(tid)

print()

#b)

fart = round(tid*9.81,2)



#c)

distanse = round(0.5*fart*tid,2)


#d)


print("sluttfart =", fart ,"m/s")
print("distanse =", distanse , "m")



