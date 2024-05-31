# coding: utf-8
"""
            SAE1.02 PACMAN IUT'O
         BUT1 Informatique 2023-2024

        Module client_joueur.py
        Ce module contient le programme principal d'un joueur
        il s'occupe des communications avec le serveur
            - envois des ordres
            - recupération de l'état du jeu
        la fonction mon_IA est celle qui contient la stratégie de
        jeu du joueur.

"""
import argparse
import random
import client
import const
import plateau
import case
import joueur

# prec = 'X'

# NOUS = set()
# MAX_COUP_FUTURE = 2
# MAX_TIME = 0.995

# v0 = originale done
# v1 = go to done
# v2 = esquive fantome
# v3 = fantôme get objective joueur
# v4 = not target self play
# v5 = min max
# v6 = opti beta
# v7 = opti tree prunning

# V1
# pass get_score
# 1 parsing info les_joueurs
# 2 get_objective
# 3 do goto objective


def analyse_recherche(plat, pos):
  """prend tout les items du plateau

      Args:
          plateau (dict): le plateau considéré
          pos (tuple): une paire d'entiers indiquant la postion de calcul des distances
      Returns:
          dict: pos -> case
      """
  glob = {}

  for i in range(plateau.get_nb_lignes(plat)):
    for j in range(plateau.get_nb_colonnes(plat)):
      glob[(i,j)] = plateau.get_case(plat,(i,j))
  return glob

  # explore = [pos]
  # deja_vu = set()
  # while explore:
  #   origine = explore.pop()
  #   if origine in deja_vu:
  #     continue
  #   deja_vu.add(origine)
  #   empl = plateau.get_case(plat, origine)
  #   glob[origine] = empl
  #   direction = plateau.directions_possibles(plat, origine)
  #   for direct in direction:
  #     voisin = plateau.pos_arrivee(plat, origine, direct)
  #     explore.append(voisin)
  # return glob


def chemin_plus_court(plat, calc, pos_depart, pos_arrivee,passemuraille=False):
  """Donne toute les posiions donnant le chemin le plus court

  Args : plat (dict) : le plateau 
        calc (plateau) : un calc de plateau pour le score de chaque case
        pos_depart (tuple) : une paire d'entiers indiquant la position de départ
        pos_arrivee (tuple) : une paire d'entiers indiquant la position d'arriver
        passemuraille (bool) : si le pacman a passemuraille

  Returns : list : une liste de toutes les positions du chemin le plus court
  """
  queue = [(pos_depart, [pos_depart])]
  finished = []
  visited = set([pos_depart])

  def ratio(path):
    lscore = list(map(lambda pos:plateau.get_case(calc,pos),path))
    return sum(lscore) / len(lscore)

  while queue:
    current_pos, current_path = queue.pop(0)
    if current_pos == pos_arrivee:
      finished.append(current_path)

    directions = plateau.directions_possibles(plat, current_pos,passemuraille)
    for direction in directions:
      neighbor = plateau.pos_arrivee(plat, current_pos, direction)
      if neighbor not in visited:
        visited.add(neighbor)
        queue.append((neighbor, current_path + [neighbor]))

  if not finished:
    return []
  return max(finished,key=ratio)


def get_objectif_pac(plat, player, ma_couleur, glob):
  """ Donne l'objectif le plus proche de la position pos.

  Args : pla (dict) : le plateau considéré
         player (tuple) : le joueur
         ma_couleur (str) : la couleur de notre joueur
         glob (dict) : un dictionnaire de pos->case.

  Returns : tuple : tuple position (int,int)
  """

  obj_pac = player[ma_couleur]
  pos_pac = joueur.get_pos_pacman(obj_pac)
  passemuraille = bool(joueur.get_duree(obj_pac,const.PASSEMURAILLE))
  dure_gloutton = joueur.get_duree(obj_pac,const.GLOUTON)
  def get_score(plat, player, empl):
    """Donne le score de la case

    Args : plat (dict) : le plateau
           player (dict) : les joueurs couleur -> joueur
           empl (tuple) : (pos , case)

    Returns : int : le score de la case
    """
    if case.get_fantomes(empl[1]):
      if any(element != ma_couleur for element in case.get_fantomes(empl[1])):
        chemin = chemin_plus_court(plat,calc,pos_pac,empl[0],passemuraille)
        if chemin and dure_gloutton >= len(chemin):
          return 20
        return -20
    if empl[0] == joueur.get_pos_pacman(player[ma_couleur]):
      return -1
    poid, tours = const.PROP_OBJET.get(empl[1]["objet"], (0, 0))
    return int(poid * (1 + (tours / 19)))

  calc =  {
      "nb_lignes":
      plateau.get_nb_lignes(plat),
      "nb_colonnes":
      plateau.get_nb_colonnes(plat),
      "valeurs": [
          0 for i in range(
              plateau.get_nb_lignes(plat) * plateau.get_nb_colonnes(plat))
      ]
  }
  for pos in glob.keys():
    # assert plateau.get_case(plat,pos) == glob[pos]
    plateau.set_case(calc,pos,get_score(plat, player, (pos, glob[pos])))
    # print(pos,case.get_objet(plateau.get_case(plat,pos)) ,glob[pos]["objet"],get_score(plat, player, (pos, glob[pos])),calc[plat["nb_colonnes"] * pos[0] + pos[1]])
    # assert calc[plat["nb_colonnes"] * pos[0] + pos[1]] == get_score(plat, player, (pos, glob[pos])) , f"{calc[plat['nb_colonnes'] * pos[0] + pos[1]]} != {get_score(plat, player, (pos, glob[pos]))}"
  return calc, max(glob.keys(), key=lambda x: plateau.get_case(calc, x))


def affiche(plat, calc):
  for i in range(plat["nb_lignes"]):
    print()
    for j in range(plat["nb_colonnes"]):
      # print("###|" if case.est_mur(plateau.get_case(plat, (i, j))) else str(plateau.get_case(calc, (i, j))).rjust(3, " ") + "|", end="")
      print(str(plateau.get_case(calc, (i, j))).rjust(3, " ") + "|", end="")
      # print(str(calc[plat["nb_colonnes"] * i + j]).rjust(3, " ") + "|", end="")
  print()



def get_objectif_fan(plat, player, ma_couleur, glob):
  """Donne la posiion du pacman le plus proche du fantome

  Args : plat (dict) : le plateau 
         player (dict) : le joueur
         glob (dict) : un dictionnaire de pos->case.

  Returns : tuple : tuple position (int,int)
  """

  pos_fan = joueur.get_pos_fantome(player[ma_couleur])

  def get_pacman(pos_etud):
    ici, empl = pos_etud
    ret = 0
    if case.get_nb_pacmans(empl):
      if any(element != ma_couleur for element in case.get_pacmans(empl)):
        for color in player.keys():
          # see if pac can eat me
          passemuraille = bool(joueur.get_duree(player[color],const.PASSEMURAILLE))
          chemin = chemin_plus_court(plat,calc,ici,pos_fan,passemuraille)
          if chemin and joueur.get_duree(player[color],const.GLOUTON) >= len(chemin):
            for pos in chemin:
              plateau.set_case(calc,pos,plateau.get_case(calc,pos)-10)
            ret += -20
          else:
            ret += 20
    ret -= case.get_nb_fantomes(empl)
    
    return ret

  calc =  {
      "nb_lignes":
      plateau.get_nb_lignes(plat),
      "nb_colonnes":
      plateau.get_nb_colonnes(plat),
      "valeurs": [
          0 for i in range(
              plateau.get_nb_lignes(plat) * plateau.get_nb_colonnes(plat))
      ]
  }
  for pos in glob.keys():
    # assert plateau.get_case(plat,pos) == glob[pos]
    plateau.set_case(calc,pos,get_pacman((pos, glob[pos])))
    # print(pos,case.get_objet(plateau.get_case(plat,pos)) ,glob[pos]["objet"],get_score(plat, player, (pos, glob[pos])),calc[plat["nb_colonnes"] * pos[0] + pos[1]])
    # assert calc[plat["nb_colonnes"] * pos[0] + pos[1]] == get_score(plat, player, (pos, glob[pos])) , f"{calc[plat['nb_colonnes'] * pos[0] + pos[1]]} != {get_score(plat, player, (pos, glob[pos]))}"
  return calc, max(glob.keys(), key=lambda x: plateau.get_case(calc, x))


"""
Début de programme nayant pas été utilisé :

# def go_to(plat, calc, depart, fin):
#   Donne la directon vers laqelle aller pour atteindre la case fin

#   Args : plat (dict) : le plateau 
#          depart (tuple) : une paire d'entiers indiquant la position de départ
#          fin (tuple) : une paire d'entiers indiquant la position d'arrivée

#   Returns : str : un caractère indiquant la direction à suivre
#   
#   chemin = chemin_plus_court(plat, calc, depart, fin)
#   print("goto",depart,fin,"chemin",len(chemin))
#   if len(chemin) < 2:
#     return random.choice(plateau.directions_possibles(plat, depart))
#   coord = chemin[1]
#   for direct in 'NESO':
#     if coord == plateau.pos_arrivee(plat, depart, direct):
#       return direct
#   return random.choice(plateau.directions_possibles(plat, depart))

def minmax(plat, joueurs):
  # min max calculer toute les possibiliter
  # alpha beta filter , enlever tout les score negatif
  # tree prunning , enlever les possibiliter non pris
  # -> algorithm gloutton , on suppose que les autres aussi font le plus haut score
  # -> pour 1 tour 1 solutions
  # mais du coup ca peut pas etre parralleliser
  # mais pas grave c'est pas si chere que ca

  # probleme
  # il faut un bien mieux calculer score
  # on va pass le fait que on peut store téléportation
  glob = analyse_recherche(plat,
                           joueur.get_pos_pacman(list(joueurs.values())[0]))
  ret = {}
  for couleur, player in joueurs.items():
    pos_pac = joueur.get_pos_pacman(player)
    pos_fant = joueur.get_pos_fantome(player)
    coord_pac = get_objectif(plat, pos_pac, glob)
    coord_fan = get_objectif_fan(plat, pos_fant, glob)
    dir_p = go_to(plat, pos_pac, coord_pac)
    dir_f = go_to(plat, pos_fant, coord_fan)
    plateau.deplacer_pacman(plat, joueur.get_nom(player), pos_pac, dir_p,
                            const.PASSEMURAILLE in joueur.get_objets(player))
    plateau.deplacer_fantome(plat,
                             joueur.get_nom(player).lower(), pos_fant,
                             dir_f)  # RAISE
    # UPDATE GLOB
    glob[pos_pac] = plateau.get_case(plat, pos_pac)
    glob[pos_fant] = plateau.get_case(plat, pos_fant)
    glob[coord_pac] = plateau.get_case(plat, coord_pac)
    glob[coord_fan] = plateau.get_case(plat, coord_fan)
    # UPDATE joueur

    ret[couleur] = (dir_p, coord_pac, dir_f, coord_fan)
  return ret


def until_time(plat,joueurs):
     #run min max a maximum of time in MAX_TIME
     #Args:
     #  plat (dict) : le plateau
     #  joueurs (dict) : tout les joueurs
     #Return:
     #  dict : couleur : ((pos,score) joueur,(pos,score) fantome)

     start_time = time.perf_counter()
     moves = []
     while time.perf_counter() - start_time < MAX_TIME:
         plat,joueurs,player_moves = minmax(plat,joueurs)
         moves.append(player_moves)
     return moves

def threaded(dic):
     #run the function until time wiht nb of core-1
     threads = []
     for _ in range(os.cpu_count() - 2):
         thread = multiprocessing.Pro-99

     for thread in threads:
         thread.join()
"""


def mon_IA(ma_couleur, carac_jeu, plan, les_joueurs):
  """ Cette fonction permet de calculer les deux actions du joueur de couleur ma_couleur
          en fonction de l'état du jeu décrit par les paramètres. 
          Le premier caractère est parmi XSNOE X indique pas de peinture et les autres
          caractères indique la direction où peindre (Nord, Sud, Est ou Ouest)
          Le deuxième caractère est parmi SNOE indiquant la direction où se déplacer.

      Args:
          ma_couleur (str): un caractère en majuscule indiquant la couleur du jeur
          carac_jeu (str): une chaine de caractères contenant les caractéristiques
                                     de la partie séparées par des ;
               duree_act;duree_tot;reserve_init;duree_obj;penalite;bonus_touche;bonus_rechar;bonus_objet           
          plan (str): le plan du plateau comme comme indiqué dans le sujet
          les_joueurs (str): le liste des joueurs avec leur caractéristique (1 joueur par ligne)
          couleur;reserve;nb_cases_peintes;objet;duree_objet;ligne;colonne;nom_complet

      Returns:
          str: une chaine de deux caractères en majuscules indiquant la direction de peinture
              et la direction de déplacement
      """
  joueurs = {}
  for ligne in les_joueurs.split('\n'):
    personne = joueur.joueur_from_str(ligne)
    joueurs[joueur.get_couleur(personne)] = personne
  le_plateau = plateau.Plateau(plan)
  lejoueur = joueurs[ma_couleur]
  pos_pac = joueur.get_pos_pacman(lejoueur)
  pos_fan = joueur.get_pos_fantome(lejoueur)

  glob = analyse_recherche(le_plateau, joueur.get_pos_pacman(lejoueur))
  calc_pac, coord_pac = get_objectif_pac(le_plateau, joueurs, ma_couleur, glob)
  # print("start")
  # print()
  # affiche(le_plateau, calc_pac)
  passemuraille = bool(joueur.get_duree(lejoueur,const.PASSEMURAILLE))

  chemin_pac = chemin_plus_court(le_plateau, calc_pac, pos_pac, coord_pac,passemuraille)
  # print("goto pac",pos_pac,coord_pac,"chemin",len(chemin_pac),chemin_pac)
  if len(chemin_pac) < 2:
    poss = plateau.directions_possibles(le_plateau, pos_pac,passemuraille)
    if not poss:
      poss = const.DIRECTIONS
    dir_p = random.choice(poss)
  else:
    coord = chemin_pac[1]
    for direct in 'NESO':
      if coord == plateau.pos_arrivee(le_plateau, pos_pac, direct):
        dir_p = direct
        break

  # dir_p = go_to(le_plateau, calc_pac, pos_pac, coord_pac)
  calc_fan, coord_fan = get_objectif_fan(le_plateau, joueurs, ma_couleur, glob)
  # print()
  # affiche(le_plateau, calc_fan)
  
  chemin_fant = chemin_plus_court(le_plateau, calc_fan, pos_fan, coord_fan)
  # print("goto",pos_fan,coord_fan,"chemin",len(chemin_fant))
  if len(chemin_fant) < 2:
    poss = plateau.directions_possibles(le_plateau, pos_fan)
    if not poss:
      poss = const.DIRECTIONS
    dir_f = random.choice(poss)
  else:
    coord = chemin_fant[1]
    for direct in 'NESO':
      if coord == plateau.pos_arrivee(le_plateau, pos_fan, direct):
        dir_f = direct
        break

  # dir_f = go_to(le_plateau, calc_fan, pos_fan, coord_fan)
  # print(dir_p,dir_f)
  # print()
  # exit(0)
  # input()
  return dir_p + dir_f


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--equipe",
                      dest="nom_equipe",
                      help="nom de l'équipe",
                      type=str,
                      default='Non fournie')
  parser.add_argument("--serveur",
                      dest="serveur",
                      help="serveur de jeu",
                      type=str,
                      default='localhost')
  parser.add_argument("--port",
                      dest="port",
                      help="port de connexion",
                      type=int,
                      default=1111)

  args = parser.parse_args()
  le_client = client.ClientCyber()
  le_client.creer_socket(args.serveur, args.port)
  le_client.enregistrement(args.nom_equipe, "joueur")
  ok = True
  while ok:
    ok, id_joueur, le_jeu = le_client.prochaine_commande()
    if ok:
      carac_jeu, le_plateau, les_joueurs = le_jeu.split(
          "--------------------\n")
      actions_joueur = mon_IA(id_joueur, carac_jeu, le_plateau,
                              les_joueurs[:-1])
      le_client.envoyer_commande_client(actions_joueur)
      # le_client.afficher_msg("sa reponse  envoyée "+str(id_joueur)+args.nom_equipe)
  le_client.afficher_msg("terminé")
