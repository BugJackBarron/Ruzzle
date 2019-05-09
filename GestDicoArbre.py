import unidecode
import datetime
from contextlib import ContextDecorator
now=datetime.datetime.now

class Time(ContextDecorator) :
    # Décorateur pour afficher le temps d'exécution d'une fonction    
    def __enter__(self):
        self.debut=now()
        print("----- Entrée dans la fonction -----")
    def __exit__(self,t,v,tr):
        duree = now() - self.debut
        
        print(duree.total_seconds())
        print("---- Sortie de la fonction-----")
              
def genereDico(fichier) :
    """Genere le dictionnaire a partir du fichier fourni
    en parametres"""
    with open(fichier,'r',encoding='utf-8') as file : #encoding necessaire sous windows 
        Dictionnaire=file.readlines()
    #traitement du fichier pour éliminer les lignes inutiles
    Dictionnaire=[unidecode.unidecode(m.strip("\n").upper()) for m in Dictionnaire
                  if ("%" not in m) and (m != "\n")]
    #Dictionnaire.sort()
    return Dictionnaire
    
class Noeud:#Noeud du Trie
    def __init__(self,finMot=False) :
        self.finMot=finMot
        self.enfants={}

def ajouteMot(mot,trie) :
    if mot=='':
        if trie is not None :
            trie.finMot=True
            return trie
        else :
            return Noeud(True)
    else :
        if mot[0] in trie.enfants.keys() :
            trie.enfants[mot[0]]=ajouteMot(mot[1:],trie.enfants[mot[0]])
            return trie
        else :
            trie.enfants[mot[0]]=ajouteMot(mot[1:],Noeud())
            return trie
                
        
            
    
@Time()
def genereArbre(dico,Trie):
    for mot in dico :
        mot=mot
        ajouteMot(mot,Trie)
        

def estDansTrie(mot,trie) :
    """Recherche si le mot est dans le Dictionnaire (extérieur)
    >>> estDansTrie('ABACULE',Trie)
    True
    >>> estDansTrie('ZOO',Trie)
    True
    >>> estDansTrie('BIDDULE',Trie)
    False
    >>> estDansTrie('ABAC',Trie)
    False
    >>> estDansTrie('SUPPLEMENTAIRE',Trie)
    True
    """
    if mot == '' :
        return trie.finMot
    else :
        if  mot[0] in trie.enfants :
            return estDansTrie(mot[1:],trie.enfants[mot[0]])
        else :
            return False
        
def rechercheTriePrefixeMot(mot,trie) :
    if mot == '' :
        return (True,trie.finMot)
    else :
        if  mot[0] in trie.enfants :
            return rechercheTriePrefixeMot(mot[1:],trie.enfants[mot[0]])
        else :
            return (False,False)

class Grille :
    def __init__(self,Trie,taille=4) :
        self.taille=taille#taille de la grille
        self.Trie=Trie
        from random import choice
        #Dictionnaire contenant les fréquences pour 10 000 d'apparition
        #des lettres
        frequences ={'A':840,'N':713,
        'B':106,'O':526,
        'C':303,'P':301,
        'D':418,'Q':99,
        'E':1726,'R':655,
        'F':112,'S':808,
        'G':127,'T':707,
        'H':92,'U':574,
        'I':734,'V':132,
        'J':31,'W':4,
        'K':5,'X':45,
        'L':601,'Y':30,
        'M':296,'Z':12}
        chaine=''.join([k*v for k,v in frequences.items()])
        self.lettres={i:choice(chaine) for i in range(self.taille**2)}
        self.listeVoisins={c:self._genereListeVoisin(c) 
                            for c in range(self.taille**2)}
        self.caseVisitees=[]
        self.motsTrouves=[]
        self.listeMotsGrille=set()
        self._ChercheTouslesMots()
        self.motsRestants=self.listeMotsGrille
        
    def _genereListeVoisin(self,c) :
        """genre la liste des voisins de la case c"""
        t=self.taille
        
        absc=c%t
        ordc=c//t
        if absc==0 : 
            vx=(0,+1)
        elif absc==t-1 :
            vx=(0,-1)
        else :
            vx=(-1,0,1)
        if ordc==0 :
            vy=(0,+1)
        elif ordc==t-1 :
            vy=(0,-1)
        else :
            vy=(-1,0,1)
        return[c+x++y*t for y in vy for x in vx if( x!=0 or y!=0 )]
        
    def motInGrille(self,mot,origine=None) :
        mot=mot.upper()
        if origine==None : #cas de début de recherche
            if mot=='' :
                return False
            elif mot[0] not in self.lettres.values() :
                return False#Cas où la première lettre n'est pas dans la grille
            else :
                cases_origines=[c for c in self.lettres.keys() if self.lettres[c]==mot[0]]
                for c in cases_origines :
                    self.caseVisitees.append(c)
                    if self.motInGrille(mot[1:],c) :        
                        return True
                    self.caseVisitees.remove(c)
                return False
        else :
            if mot=='':
                return True
            else :
                cases_possibles = [c for c in self.listeVoisins[origine] 
                                    if c not in self.caseVisitees
                                    and self.lettres[c]==mot[0]]
                if cases_possibles==[] :
                    return False
                else :
                    for c in cases_possibles :
                        self.caseVisitees.append(c)
                        if self.motInGrille(mot[1:],c) :
                            return True
                        self.caseVisitees.remove(c)
                    return False
    
    def _ChercheTouslesMots(self):
        for c in range(self.taille**2) :
            self.caseVisitees.append(c)
            self._chercheLettreSuivante(self.lettres[c],c)
            self.caseVisitees.remove(c)
        self.caseVisitees=[]
    
    def _chercheLettreSuivante(self,motActuel,origine):
        cases_possibles=[c for c in self.listeVoisins[origine] 
                                    if c not in self.caseVisitees]
        if cases_possibles==[] :
            pass
        else :
            for c in cases_possibles :
                self.caseVisitees.append(c)
                motNouveau=motActuel+self.lettres[c]
                chaineDansArbre,motReel=rechercheTriePrefixeMot(motNouveau,self.Trie)
                if chaineDansArbre :
                    if motReel : 
                        self.listeMotsGrille.add(motNouveau)
                    self._chercheLettreSuivante(motNouveau,c)
                self.caseVisitees.remove(c)
        
        
                
        
        
        
                
            
        
    def afficheShell(self) :
        for i in range(self.taille) :
            print("|".join([f"{self.lettres[j+i*self.taille]}" for j in range(self.taille)]))
            print("-"*(2*self.taille-1))


if __name__ == "__main__" :
    Trie=Noeud()
    genereArbre(genereDico("dico.txt"),Trie)
    import doctest
    doctest.testmod()
    grille=Grille(Trie)
      
#    Score=0
#    while True :
#        print(f"Nombre de mots restant à trouver : {len(grille.listeMotsGrilleV2)-len(grille.motsTrouves)}")
#        print(f"Score : {Score}")
#        mot=input('Entrez un mot :').upper()
#        if mot=='' : break
#        if mot in grille.motsTrouves :
#            print("Déjà proposé !")
#        elif grille.motInGrille(mot) and mot in grille.listeMotsGrilleV2 :
#            
#            grille.motsTrouves.append(mot)
#            
#            print(f"Mot correct ! +{len(mot)} points !")
#            Score+=len(mot)
#        else :
#            print("Mot incorrect ! -2 points !")
#            Score-=2
#        grille.caseVisitees=[]
#        grille.afficheShell()
#    print("Fin du jeu")