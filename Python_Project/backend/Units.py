from csv import *
import random
import math
class Unit():
    """
    Crée une classe générale Unit avec l'ensemble des statistiques me semblant interressantes (n'hesitez pas à me dire si quelque chose
    ne convient pas parmi les stats indiquées), les coordonnées ainsi que la cible des attaques. Les 2 dernières étant simplement en 
    figuration pour l'instant
    """
    def __init__(self,nomUnite):
        self.Unit = self.def_stat('Unit',nomUnite)
        self.HP = int(self.def_stat('HP',nomUnite))
        #self.Type_Attack = self.def_stat('Type_Attack',nomUnite)
        #self.Attack = self.def_stat('Attack',nomUnite)
        #self.Armor = self.def_stat('Armor',nomUnite)
        #self.Pierce_Armor = self.def_stat('Pierce_Armor',nomUnite)
        self.Min_Range = self.def_stat('Min_Range',nomUnite)
        self.Max_Range = self.def_stat('Max_Range',nomUnite)
        self.Line_of_Sight = self.def_stat('Line_of_Sight',nomUnite)
        self.Speed = self.def_stat('Speed',nomUnite)
        self.Attack_Delay = self.def_stat('Attack_Delay',nomUnite)
        self.Reload_Time = self.def_stat('Reload_Time',nomUnite)
        self.Accuracy = self.def_stat('Accuracy',nomUnite)
        self.Blast_Radius = self.def_stat('Blast_Radius',nomUnite)
        self.Garrison = self.def_stat('Garrison',nomUnite)
        
        
        self.Attack = self.def_stat('Attack',nomUnite)
        self.Armor = self.def_stat('Armor',nomUnite)
        self.id=None
        self.equipe = None
        self.coords = None
        self.hitbox=0.25
        self.target = None
        self.alive = True
        self.timer=0

    def def_stat(self, stat, nomUnite):
        """
        Methode definissant la statistique en entrée en prenant en compte le nom de l'unité 
        """
        if stat=='Attack' or stat=='Armor':
            liste=[]
            with open(f'{stat}.csv', 'r') as csvfile:
                file = list(DictReader(csvfile, delimiter='\t'))
                for row in file:
                    if row['Unit']==nomUnite:
                        statistique = row
            del statistique['Unit']
            for k in statistique:
                if statistique[k]=='None' or statistique[k]==nomUnite:
                    liste.append(k)
                else:
                    statistique[k]=float(statistique[k])
            for i in range(len(liste)):
                del statistique[liste[i]]
            # return row
            return statistique

        else:
            with open('Stats_Units.csv', 'r') as csvfile:
                file = DictReader(csvfile, delimiter='\t')
                for row in file:
                    if row['Unit']==nomUnite:
                        if (stat=='Unit' or stat=='Type_Attack') or row[stat]=='None':
                            return row[stat]
                        return float(row[stat]) #retourne un flottant pour pouvoir réaliser des opérations (ex: HP)
                
    def inflict_damage(self):
        assert type(self.target)!= "<class 'Classes.Unit'>", type(self.target)
        damage=0
        for k in self.Attack:
            for l in self.target.Armor:
                if k == l:
                    damage += max(0,self.Attack[k]-self.target.Armor[l])

        damage=max(1,damage)
        if random.random()<self.Accuracy:
            self.target.take_damage(damage)
        self.timer=0
        return damage

    def take_damage(self, damage):
        self.HP-=damage
        if self.HP<=0:
            self.alive=False

    def can_attack(self):
        return float(self.timer)>=(self.Attack_Delay+self.Reload_Time)

    def find_closest_target(self, all_units):
        
        if self.coords is None:
            return None

        x, y = self.coords
        cible_proche = None
        distance_min = float('inf')

        for autre in all_units:
            if autre is self:
                continue  
            if not autre.alive or autre.HP <= 0:
                continue  
            if not hasattr(autre, 'coords') or autre.coords is None:
                continue  

            dist = math.sqrt((x - autre.coords[0])**2 + (y - autre.coords[1])**2)    
            if dist<= distance_min:
                cible_proche = autre
                distance_min = dist

        self.target = cible_proche
        return cible_proche
    

    def se_deplacer(self, destination, delta_t=1.0):
       
    
        if self.coords is None:
            print(f"L'unité {self.Unit} n'a pas de position initiale.")
            return

        x, y = self.coords
        dest_x, dest_y = destination

        dx = dest_x - x
        dy = dest_y - y
        distance = math.sqrt(dx**2 + dy**2)

        if distance == 0:
            return

        distance_max = self.Speed * delta_t

        if distance <= distance_max:
            self.coords = (dest_x, dest_y)
        else:
           
            ratio = distance_max / distance
            new_x = x + dx * ratio
            new_y = y + dy * ratio
            self.coords = (new_x, new_y)

