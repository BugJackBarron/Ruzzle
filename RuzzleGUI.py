from random import choice
import pygame as pg
from pygame.locals import * 
import pickle
import  GestDicoArbre as gda
LARGEUR=1000
HAUTEUR=600
TPSMAX=60000 #temps max d'une partie en millisecondes


class Player :
    def __init__(self,score,nom,niveau) :
        self.score=score
        self.nom=nom
        self.niveau=niveau
    
    
        

class GuiGrille :
    def __init__(self,grille):
        self.grille=grille
        #Chargement des images des cases
        self.taille_base= 400//self.grille.taille
        taille_image=(self.taille_base,self.taille_base)
        self.ImgCase={'base' :pg.transform.scale(pg.image.load("Images/CaseRuzzle.png").convert(),taille_image),
                      'selected':pg.transform.scale(pg.image.load("Images/CaseRuzzleSelected.png").convert(),taille_image),
                      'correct' : pg.transform.scale(pg.image.load("Images/CaseRuzzleCorrect.png").convert(),taille_image),
                      'erreur':pg.transform.scale(pg.image.load("Images/CaseRuzzleErreur.png").convert(),taille_image),
                      'bonus' :pg.transform.scale(pg.image.load("Images/CaseRuzzleBonus.png").convert(),taille_image)
                      }
        #Initialisation des types de cases de la grille
        self.caseType={i: 'base' for i in range(self.grille.taille**2)}
        self.listeBonus=[None]*self.grille.taille**2 + [n for n in range(self.grille.taille**2)]
        self.caseBonus=choice(self.listeBonus)
        if self.caseBonus != None :
            self.caseType[self.caseBonus]='bonus'
        #Met les images à l'échelle ( en fonction de la taille de la grille)
        
        #Creation des objets Rect de la grille, et des zones cliquables ( hitBox )
        self.caseRects={i : self.ImgCase['base'].get_rect() for i in range(grille.taille**2)}
        self.hitBox={i : pg.Surface((int(self.taille_base*0.7),int(self.taille_base*0.7))) for i in range(grille.taille**2)}
        self.hitBoxRect={i:self.hitBox[i].get_rect()  for i in range(grille.taille**2)}
        #Coordonneees des objets rects 
        for i in range(grille.taille**2):
            self.caseRects[i].left=100+self.caseRects[i].width*(i%grille.taille)
            self.caseRects[i].top=100+self.caseRects[i].height*(i//grille.taille)
            self.hitBoxRect[i].center=self.caseRects[i].center
        #liste des cases sélectionnées
        self.selected=[]
        #Mise en place des lettres dans les cases
        self.fonte=pg.font.SysFont('Arial',int(self.taille_base*0.7))
        self.texteCase=dict()
        self.texteCaseRect=dict()
        for i in range(grille.taille**2) :
            self.texteCase[i]=self.fonte.render(self.grille.lettres[i],False,(0, 255, 255))
            self.texteCaseRect[i]=self.texteCase[i].get_rect()
            self.texteCaseRect[i].center=self.caseRects[i].center
        #Chargement des sons
        self.listSnd=[pg.mixer.Sound(f"Sounds/{Note}_{Octave}.wav") 
        for Octave in [1,2,3]
        for Note in ['Do','Re','Mi','Fa','Sol','La','Si']
        ]
        self.errorSnd=pg.mixer.Sound("Sounds/Erreur.wav")
        self.correctSnd=pg.mixer.Sound("Sounds/Correct.wav")
        self.bonusSnd=pg.mixer.Sound("Sounds/Bonus.wav")
      
    def afficheGrille(self):
        #Affichage de la grille dans la fenetre
        for i in range(self.grille.taille**2) :
            fenetre.blit(self.hitBox[i],self.hitBoxRect[i])
            fenetre.blit(self.ImgCase[self.caseType[i]],self.caseRects[i])
            fenetre.blit(self.texteCase[i],self.texteCaseRect[i])

class GuiInfo :
    """Classe décrivant tous les comportements annexes au jeu :
    affichage du score, du temps restant, du nombre de mots restants,
    de l'aide avec un mot suggéré, de l'aide avec la liste des mots déjà trouvés"""
    def __init__(self,guiGrille) :
        #initialisation
        self.score=0
        self.guiGrille=guiGrille
        self.fonte=pg.font.SysFont('scheherazade',int(400//self.guiGrille.grille.taille*0.5))
        #Initialisation de l'affichage du score
        self.ScoreFix=self.fonte.render(f"SCORE : {self.score:03d}",False,(0, 255, 255))
        self.ScoreFixRect=self.ScoreFix.get_rect()
        self.ScoreFixRect.center=(750,100)
        #Initialisation de l'affichage du nombre de mots restants
        self.MotsRestantsFix=self.fonte.render(f"""MOTS RESTANTS :  {len(self.guiGrille.grille.motsRestants):03d}""",False,(0, 255, 255))
        self.MotsRestantsFixRect=self.MotsRestantsFix.get_rect()
        self.MotsRestantsFixRect.center=(750,200)
        #Initialisation des suggestions ( mots de longueur >4 )
        self.listePossibles=[mot for mot in self.guiGrille.grille.motsRestants if len(mot)>=5 and mot not in self.guiGrille.grille.motsTrouves]
        self.suggestion=None
        self.suggestionClair=None
        self.newSuggestion()
        self.suggestionFix =self.fonte.render(f"""{self.suggestion}""",False,(0, 255, 255))
        self.suggestionFixRect=self.suggestionFix.get_rect()
        self.suggestionFixRect.center=(300,550)
        #Initialisation du temps restant
        self.tpsDepart = TPSMAX
        self.timeFix=self.fonte.render(f"""TEMPS RESTANT : {self.tpsDepart//1000}""",False,(0, 255, 255))
        self.timeFixRect=self.timeFix.get_rect()
        self.timeFixRect.midbottom=(750,500)
        
        
    def augmenteScore(self,valeur):
        #Augmente le score de la valeur passée en argument
        #et actualise l'affichage
        self.MotsRestantsFix=self.fonte.render(f"""MOTS RESTANTS : {len(self.guiGrille.grille.motsRestants):03d}""",False,(0, 255, 255))
        self.score+=valeur
        self.ScoreFix=self.fonte.render(f"SCORE : {self.score:03d}",False,(0, 255, 255))
       
    def newSuggestion(self) :
        #Génère une nouvelle suggestion,
        #En prenant éventuellement en compte le fait que la liste puisse être vide.
        self.listePossibles=[mot for mot in self.guiGrille.grille.motsRestants if len(mot)>=5 and mot not in self.guiGrille.grille.motsTrouves]
        if self.listePossibles != [] :
            self.suggestionClair=choice(self.listePossibles)
            self.conversionAffichageSuggestion()
        else :
            self.suggestion="Pas de suggestions possibles !"
            self.suggestionFix =self.fonte.render(f"""{self.suggestion}""",False,(0, 255, 255))
            
        
    def conversionAffichageSuggestion(self) :
        #Génère l'affichage de la suggestion
        #en actualisant en fonction de la sélection en cours.
        if self.listePossibles != [] :
            caracteres=list(self.suggestionClair[::len(self.suggestionClair) - 1])
            [caracteres.insert(-1,'-') for i in self.suggestionClair[1:-1]]
            for i,case in enumerate(self.guiGrille.selected) :
                if i<len(self.suggestionClair) and self.guiGrille.grille.lettres[case] == self.suggestionClair[i] :
                    caracteres[i]=self.suggestionClair[i]
                else :
                    break
            self.suggestion="".join(caracteres)
        self.suggestionFix =self.fonte.render(f"""{self.suggestion}""",False,(0, 255, 255))
    
    def AffichageHelp(self) :
        #Affichage d'un message si les suggestion ne sont pas actives
        Help=self.fonte.render("F1 pour une aide",False,(0, 255, 255))
        HelpRect=Help.get_rect()
        HelpRect.center=(300,550)
        fenetre.blit(Help,HelpRect)

    def affichageTempsRestant(self,tpsrestant) :
        #actualisation de l'affichage du temps
        if tpsrestant>1000 :
            self.timeFix=self.fonte.render(f"""TEMPS RESTANT : {tpsrestant//1000}""",False,(0, 255, 255))
        else :
            if (tpsrestant//100)%10<=5 :
                self.timeFix=self.fonte.render(f"""TEMPS RESTANT : {tpsrestant//1000}""",False,(0, 255, 255))
            else :
                self.timeFix=self.fonte.render(f"""TEMPS RESTANT : {tpsrestant//1000}""",False,(255, 0, 0))
    
       
    def affiche(self,aide=False) :
        #Actualisation de la fenetre
        fenetre.blit(self.ScoreFix,self.ScoreFixRect)
        fenetre.blit(self.MotsRestantsFix,self.MotsRestantsFixRect)
        fenetre.blit(self.timeFix,self.timeFixRect)
        if aide :
            fenetre.blit(self.suggestionFix,self.suggestionFixRect)
        else :
            self.AffichageHelp()
    
    def afficheListe(self,montreAffichage) :
        #Génère un affichage de la liste des mots déjà trouvés, et agrandit ou rapetisse
        # la fenêtre pour montrer ou cacher cette liste
        global fenetre
        if montreAffichage :
            fenetre=pg.display.set_mode((LARGEUR+200,HAUTEUR))
        else :
            fenetre=pg.display.set_mode((LARGEUR,HAUTEUR))
        fonte2=pg.font.SysFont('scheherazade',20)
        titre=fonte2.render("Liste des mots déjà trouvés :",False,(0, 255, 255))
        titreRect=titre.get_rect()
        titreRect.center=(LARGEUR+100,50)
        fenetre.blit(titre,titreRect)
        for pos,mot in enumerate(self.guiGrille.grille.motsTrouves) :
            affMot=fonte2.render(mot,False,(0,255,255))
            affMotRect=affMot.get_rect()
            affMotRect.center=(LARGEUR+50+100*(pos%2),100+30*(pos//2))
            fenetre.blit(affMot,affMotRect)


###############################
# FIN DES CLASSES             #
# DEBUT DES FONCTIONS DE JEU  #
###############################

def  game(grille,isThereSnd=True):
    # Fonction gérant une partie, utilisant une grille passée en argument,
    # et éventuellement un argument booléen pour gérer la présence du son
    Continuer=True
    #Chargement des images et création des rects correspondants
    ImgFond=pg.image.load("Images/FondRuzzle.png").convert()
    # Création des affichages grille et info
    guiGrille=GuiGrille(grille)
    guiInfo=GuiInfo(guiGrille)
    #Initialisation des variables utilisées
    enSelection=True
    lastSelected=None
    persistenceAffichageDebut=None
    persistenceAffichageEcoulee=None
    erreurMot=False
    aide=False
    listeMots=False
    #Initialisation du temps
    debutPartie=pg.time.get_ticks()
    #Boucle principale
    while Continuer :
        #Gestionnaire d'événements
        for evenement in pg.event.get() :
            if evenement.type == QUIT :
                # Clique sur croix de fermeture de la fenetre
                Continuer=False
            if evenement.type == KEYDOWN :
                #Appuis sur F1 ou F2 pour les aides
                if evenement.key==K_F1 :                    
                    aide=not(aide)
                    if not(aide ) :
                        guiInfo.suggestion="F1 pour une suggestion !"
                    if aide :
                        guiInfo.newSuggestion()
                if evenement.key==K_F2 :
                    listeMots=not(listeMots)    
                    guiInfo.afficheListe(listeMots)
        # Récupération de l'état de la souris, particuliètrement quand le bouton gauche
        # est cliqué.
        if pg.mouse.get_pressed()[0]==1 :
            persistenceAffichageDebut=None
            persistenceAffichageEcoulee=None
            actual_pos=pg.mouse.get_pos()
            if enSelection :
                # SI la souris est en mode sélection
                for i in range(grille.taille**2) :                    
                    if guiGrille.hitBoxRect[i].collidepoint(actual_pos) :
                        # si collision du pointeur de souris avec la hitBox de la case n° i
                        if i==lastSelected :
                            pass #Rien ne se passe si le pointeur de souris reste sur la même case
                        elif lastSelected !=None and i not in grille.listeVoisins[lastSelected] :
                            pass #Rien ne se passe si le pointeur n'est pas sur une
                        #case adjacente à la dernière case
                        elif len(guiGrille.selected)>1 and i==guiGrille.selected[-2] :
                            # Désélection de la dernière case dans le cas d'un retour arrière
                            guiGrille.caseType[lastSelected]='base'
                            guiGrille.selected.remove(lastSelected)
                            lastSelected=i
                        elif i not in guiGrille.selected or guiGrille.selected==[] :
                            # Ajout d'une case dans le cas normal
                            lastSelected=i
                            guiGrille.caseType[i]='selected'
                            guiGrille.selected.append(i)
                            if isThereSnd :
                                guiGrille.listSnd[len(guiGrille.selected)-1].play()
                            
                        else :
                            # Dernier cas : collision avec une case déjà sélectionnée
                            enSelection=False
                            for k in guiGrille.selected :
                                guiGrille.caseType[k]='erreur'
                            guiGrille.selected=[]
                            if isThereSnd :
                                guiGrille.errorSnd.play()
                                guiGrille.errorSnd.fadeout(1000)
                            erreurMot=True
                    
            
        else :#Si le clique droit n'est pas appuyé
            
            if len(guiGrille.selected)>1 :#On cherche des mots de taille >1
                #Création du mot
                mot="".join([grille.lettres[i] for i in guiGrille.selected])
                if persistenceAffichageEcoulee== None :#Gestion de la persistence de l'affichage
                    persistenceAffichageDebut = pg.time.get_ticks()
                    if mot in grille.motsRestants :
                        # Vérification de la présence du mot dans la liste des mots à trouver
                        grille.motsTrouves.append(mot)
                        guiInfo.afficheListe(listeMots)
                        grille.motsRestants = set(grille.motsRestants)-set([mot])
                        #calcul des points en fonction de la présence d'une case bonus
                        if guiGrille.caseBonus != None and guiGrille.caseBonus in guiGrille.selected :
                            guiInfo.augmenteScore(2*len(mot))
                            guiInfo.tpsDepart+=2*len(mot)*1000
                            if isThereSnd :
                                guiGrille.bonusSnd.play()
                                guiGrille.bonusSnd.fadeout(2000)
                        else :
                            guiInfo.augmenteScore(len(mot))
                            guiInfo.tpsDepart+=len(mot)*1000
                            if isThereSnd :
                                guiGrille.correctSnd.play()
                                guiGrille.correctSnd.fadeout(1000)
                        guiInfo.newSuggestion()
                        for i in guiGrille.selected :
                            guiGrille.caseType[i]='correct'

                    else :#Si le mot n'est pas dans la liste des mots restants :
                        for i in guiGrille.selected :
                            guiGrille.caseType[i]='erreur'
                        if isThereSnd :
                            guiGrille.errorSnd.play()
                            guiGrille.errorSnd.fadeout(1000)
                        guiInfo.augmenteScore(-2)
                        
                        
                    persistenceAffichageEcoulee=pg.time.get_ticks()-persistenceAffichageDebut
                else :#Si la persistence est en cours, on calcule juste le temps actuel
                    persistenceAffichageEcoulee=pg.time.get_ticks()-persistenceAffichageDebut
            elif erreurMot==True :
                if persistenceAffichageEcoulee== None : 
                    persistenceAffichageDebut = pg.time.get_ticks()
                persistenceAffichageEcoulee=pg.time.get_ticks()-persistenceAffichageDebut
                
            if (persistenceAffichageEcoulee != None and persistenceAffichageEcoulee > 500) or 0<len(guiGrille.selected)<2:
            # Réinitialisation de la grille après persistence ou dans le cas d'une sélection
            # d'une seule lettre
                enSelection=True
                lastSelected=None
                persistenceAffichageEcoulee=None
                erreurMot=False
                guiGrille.selected=[]
                for i in range(grille.taille**2) :
                    guiGrille.caseType[i]= 'base'
                guiGrille.caseBonus=choice(guiGrille.listeBonus)
                if guiGrille.caseBonus != None :
                    guiGrille.caseType[guiGrille.caseBonus]='bonus'
        if aide :
            guiInfo.conversionAffichageSuggestion()      
                    
                
        # Calcul du temps de jeu restant         
        tpsrestant=guiInfo.tpsDepart - (pg.time.get_ticks() -debutPartie)
        if tpsrestant<=0 :
            Continuer=False
        guiInfo.affichageTempsRestant(tpsrestant)
        
        
        fenetre.blit(ImgFond,(0,0))
        guiGrille.afficheGrille()
        guiInfo.affiche(aide)
        pg.display.update()
    # renvoie le score de la partie pour gestion du HighScore
    return guiInfo.score

def presentation():
    """Fonction créant et gérant l'écran de présentation"""
    #Chargement des images et création des rects
    imgGrille=pg.image.load('Images/grille_presentation.png').convert_alpha()
    imgFond=pg.image.load("Images/FondRuzzle.png").convert_alpha()
    imgSnd={True :pg.transform.scale(pg.image.load("Images/SndOn.png").convert_alpha(),(50,50)),
    False :pg.transform.scale(pg.image.load("Images/SndOff.png").convert_alpha(),(50,50))}
    imgSndRect=imgSnd[True].get_rect()
    imgSndRect.center=(300,550)
    imgBouton=pg.image.load("Images/imgBouton.png").convert_alpha()
    imgBoutonRect={i : imgBouton.get_rect() for i in [4,5,6]}
    
    fonte=pg.font.SysFont('scheherazade',50)
    txtBouton={i:fonte.render(f"Grille {i}x{i}",False,(255, 0, 0)) for i in [4,5,6]}
    txtBoutonRect={i:txtBouton[i].get_rect() for i in [4,5,6]}
    for i in [4,5,6]:
        imgBoutonRect[i].center=(650,150+(i-4)*150)
        txtBoutonRect[i].center=imgBoutonRect[i].center
    selectSnd=True
    
    
    while True :
        #Boucle principale et gestionnaire d'événement
        for evenement in pg.event.get() :
            if evenement.type == QUIT :
                return None,True
            if evenement.type ==  MOUSEBUTTONUP:
                actual_pos=pg.mouse.get_pos()
                for i in [4,5,6] :                    
                    if imgBoutonRect[i].collidepoint(actual_pos) :
                        # Si clique sur un des trois choix de taille de grille
                        # Renvoie la taille de la grille et l'état du son
                        return i,selectSnd
                if imgSndRect.collidepoint(actual_pos) :
                    selectSnd=not(selectSnd)
        
        fenetre.blit(imgFond,(0,0))
        
        fenetre.blit(imgGrille,(100,100))
        fenetre.blit(imgSnd[selectSnd],imgSndRect)
        for i in [4,5,6] :
            fenetre.blit(imgBouton,imgBoutonRect[i])
            fenetre.blit(txtBouton[i],txtBoutonRect[i])
        pg.display.update()
        
        


def chargement():
    """ Fonction générant un écran d'attente, le temps de charger
    le dictionnaire et de le convertir en Trie"""
    fonte=pg.font.SysFont('scheherazade',50)
    imgFond=pg.image.load("Images/FondRuzzle.png").convert_alpha()
    txtCharge=fonte.render("Chargement du dictionnaire",False,(0,255,255))
    txtChargeRect=txtCharge.get_rect()
    txtChargeRect.center=(LARGEUR/2,150)
    txtHelpF1=fonte.render("F1 pour obtenir une suggestion",False,(0,255,255))
    txtHelpF1Rect=txtHelpF1.get_rect()
    txtHelpF1Rect.center=(LARGEUR/2,350)
    txtHelpF2=fonte.render("F2 pour la liste des mots trouvés",False,(0,255,255))
    txtHelpF2Rect=txtHelpF2.get_rect()
    txtHelpF2Rect.center=(LARGEUR/2,425)
    fenetre.blit(imgFond,(0,0))
    fenetre.blit(txtCharge,txtChargeRect)
    fenetre.blit(txtHelpF1,txtHelpF1Rect)
    fenetre.blit(txtHelpF2,txtHelpF2Rect)
    pg.display.update()
    
    Dico=gda.genereDico("dico.txt")
    pg.time.wait(500)
    txtCharge=fonte.render("Construction de l'arbre",False,(0,255,255))
    txtChargeRect=txtCharge.get_rect()
    txtChargeRect.center=(LARGEUR/2,150)
    fenetre.blit(imgFond,(0,0))
    fenetre.blit(txtCharge,txtChargeRect)
    fenetre.blit(txtHelpF1,txtHelpF1Rect)
    fenetre.blit(txtHelpF2,txtHelpF2Rect)
    pg.display.update()
    
    Trie=gda.Noeud()
    gda.genereArbre(Dico,Trie)
    pg.time.wait(500)
    return Trie


def HighScore(score):
    """ Fonction gérant l'écran de fin, et éventuellement l'intégration au tableau de HighScore"""
    def ajouteHighScore():
        pass
        
    fonte=pg.font.SysFont('scheherazade',40)
    fenetre=pg.display.set_mode((LARGEUR,HAUTEUR))
    imgFond=pg.image.load("Images/FondRuzzle.png").convert_alpha()
    imgBouton=pg.image.load("Images/imgBouton.png").convert_alpha()
    imgBoutonRejouer=imgBouton.get_rect()
    imgBoutonRejouer.center=(200,200)
    rejouerTxt=fonte.render("Rejouer",False,(255,0,0))
    rejouerTxtRect=rejouerTxt.get_rect()
    rejouerTxtRect.center=imgBoutonRejouer.center
    imgBoutonQuit=imgBouton.get_rect()
    quitTxt=fonte.render("Quitter",False,(255,0,0))
    imgBoutonQuit.center=(200,400)
    quitTxtrect=quitTxt.get_rect()
    quitTxtrect.center=imgBoutonQuit.center

    
    with open("highscore.ruz",'br') as file :
        #par défaut, HS est une liste des scores par ordre croissant
        HS = pickle.load(file)
    if  score>HS[0].score :
        ajouteHighScore()
    while True :
        for evenement in pg.event.get() :
            if evenement.type == QUIT :
                return False
            if evenement.type ==  MOUSEBUTTONUP:
                actual_pos=pg.mouse.get_pos()
                if imgBoutonQuit.collidepoint(actual_pos) :
                        return False
                if imgBoutonRejouer.collidepoint(actual_pos) :
                    return True
        
            
        
        for i,p in enumerate(HS) :
            plTxt=fonte.render(f"{p.nom} : {p.score}",False,(0,255,255))
            fenetre.blit(plTxt,(LARGEUR//2-100,500-(i*45)))
        fenetre.blit(imgFond,(0,0))
        fenetre.blit(imgBouton,imgBoutonRejouer)
        fenetre.blit(imgBouton,imgBoutonQuit)
        fenetre.blit(rejouerTxt,rejouerTxtRect)
        fenetre.blit(quitTxt,quitTxtrect)        
        pg.display.update()
    
    

                

    

if  __name__  ==  "__main__" :
    pg.init()
    fenetre=pg.display.set_mode((LARGEUR,HAUTEUR))
    jouer=True 
    while jouer :
        taille_grille,selectSnd=presentation()
        if taille_grille !=None :
            Trie=chargement()
            grille=gda.Grille(Trie,taille=taille_grille)
            Score=game(grille,isThereSnd=selectSnd)
            jouer=HighScore(Score)
        else :
            jouer=False
    pg.quit()