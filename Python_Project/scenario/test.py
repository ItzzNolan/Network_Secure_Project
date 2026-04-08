import os
import sys
parent_dir=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
sys.path.append(parent_dir)
from backend.jeu import Jeu
from ia.general import make_general

def end_fight(generaux:list, list_unite:list):
    # faire tout les trucs d'affichage
    partie= initialiser(generaux, list_unite)

    return partie

def initialiser(generaux:list, list_unite:dict):
    if len(generaux)==1:
        partie = Jeu(generaux[0], generaux[0])
    else:
        partie = Jeu(generaux[1], generaux[0])
    h=partie.carte.hauteur
    mid=h//2
    x=0
    cpt=0
    dict={}
    for unite in list_unite:
        if list_unite[unite]>h:
            if list_unite[unite]%2==1:
                dict[f"{unite}2"]=list_unite[unite]//2 +1
                list_unite[unite]//=2
            else:
                dict[f"{unite}2"]=list_unite[unite]//2
                list_unite[unite]//=2
    list_unite.update(dict)
    for unite in list_unite:
        for y in range(mid-list_unite[unite]//2,mid-(list_unite[unite]//2) + list_unite[unite]):
            partie.ajouter_unite(f"{unite}",x,y,0)
            partie.ajouter_unite(f"{unite}",partie.carte.largeur-x-1,y,1)
            cpt+=1
        # print(partie.carte.largeur-x)
        x+=1
    # print(list_unite)
    # print(cpt)
    # print([u.Unit for u in partie.unites],[u.equipe for u in partie.unites] )
    return partie


def tournoi(generaux:list, list_unite:dict,nb_combat=100):
    partie=initialiser(generaux, list_unite)
    for g1 in generaux:
        partie.generaux[0]=make_general(f"{g1}",0)
        for g2 in generaux:
            partie.generaux[1]=make_general(f"{g2}",1)
            print(f"combat :{partie.generaux[0]} vs {partie.generaux[1]}")
            print(f"nb unite : {len(partie.unites)}")
            for i in range(nb_combat):
                print(f"combat n°{i+1}")
                while partie.check_victory()==None:
                    partie.mettre_a_jour()
                    # print(f"tour: {partie._tour} , unite:{len(partie.unites)}")
                if partie.check_victory()==1:
                    print(f"vainqueur: {partie.generaux[0].name}1 avec {len(partie.unites)} unites")
                else:
                    print(f"vainqueur: {partie.generaux[1].name}2 avec {len(partie.unites)} unites")
                # print([g.name for g in partie.generaux.values()])
                partie = end_fight([g.name for g in partie.generaux.values()], list_unite)


if __name__ == "__main__":
    tournoi(["braindead"],{"Pikeman":10,"Knight":10})