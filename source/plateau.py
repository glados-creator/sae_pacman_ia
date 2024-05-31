"""
            SAE1.02 PACMAN IUT'O
         BUT1 Informatique 2023-2024

        Module plateau.py
        Ce module contient l'implémentation de la structure de données
        qui gère le plateau jeu aussi qu'un certain nombre de fonctions
        permettant d'observer le plateau et d'aider l'IA à prendre des décisions
"""
import const
import case
import random


def get_nb_lignes(plateau):
  """retourne le nombre de lignes du plateau

    Args:
        plateau (dict): le plateau considéré

    Returns:
        int: le nombre de lignes du plateau
    """
  return plateau['nb_lignes']


def get_nb_colonnes(plateau):
  """retourne le nombre de colonnes du plateau

    Args:
        plateau (dict): le plateau considéré

    Returns:
        int: le nombre de colonnes du plateau
    """
  return plateau['nb_colonnes']


def pos_ouest(plateau, pos):
  """retourne la position de la case à l'ouest de pos

    Args:
        plateau (dict): le plateau considéré
        pos (tuple): une paire d'entiers donnant la position
    Returns:
        int: un tuple d'entiers
    """
  nouvelle_pos = (pos[0], pos[1] - 1)
  if nouvelle_pos[1] < 0:
    return (nouvelle_pos[0], get_nb_colonnes(plateau) - 1)
  return nouvelle_pos


def pos_est(plateau, pos):
  """retourne la position de la case à l'est de pos

    Args:
        plateau (dict): le plateau considéré
        pos (tuple): une paire d'entiers donnant la position
    Returns:
        int: un tuple d'entiers
    """
  nouvelle_pos = (pos[0], pos[1] + 1)
  if nouvelle_pos[1] >= get_nb_colonnes(plateau):
    return (nouvelle_pos[0], 0)
  return nouvelle_pos


def pos_nord(plateau, pos):
  """retourne la position de la case au nord de pos

    Args:
        plateau (dict): le plateau considéré
        pos (tuple): une paire d'entiers donnant la position
    Returns:
        int: un tuple d'entiers
    """
  nouvelle_pos = (pos[0] - 1, pos[1])
  if nouvelle_pos[0] < 0:
    return (get_nb_lignes(plateau) - 1, nouvelle_pos[1])
  return nouvelle_pos


def pos_sud(plateau, pos):
  """retourne la position de la case au sud de pos

    Args:
        plateau (dict): le plateau considéré
        pos (tuple): une paire d'entiers donnant la position
    Returns:
        int: un tuple d'entiers
    """
  nouvelle_pos = (pos[0] + 1, pos[1])
  if nouvelle_pos[0] >= get_nb_lignes(plateau):
    return (0, nouvelle_pos[1])
  return nouvelle_pos


def get_case(plateau, pos):
  """retourne la case qui se trouveglob[ à la position pos du plateau

    Args:
        plateau (dict): le plateau considéré
        pos (tuple): une paire (lig,col) de deux int

    Returns:
        dict: La case qui se situe à la position pos du plateau
    """
  return plateau['valeurs'][plateau['nb_colonnes'] * pos[0] + pos[1]]


def pos_arrivee(plateau, pos, direction):
  """ calcule la position d'arrivée si on part de pos et qu'on va dans
    la direction indiquée en tenant compte que le plateau est un tore
    si la direction n'existe pas la fonction retourne None
    Args:
        plateau (dict): Le plateau considéré
        pos (tuple): une paire d'entiers qui donne la position de départ
        direction (str): un des caractère NSEO donnant la direction du déplacement

    Returns:
        None|tuple: None ou une paire d'entiers indiquant la position d'arrivée
    """
  if direction == "N":
    return pos_nord(plateau, pos)
  elif direction == "S":
    return pos_sud(plateau, pos)
  elif direction == "E":
    return pos_est(plateau, pos)
  elif direction == "O":
    return pos_ouest(plateau, pos)
  return None


def get_objet(plateau, pos):
  """retourne l'objet qui se trouve à la position pos du plateau

    Args:
        plateau (dict): le plateau considéré
        pos (tuple): une paire (lig,col) de deux int

    Returns:
        str: le caractère symbolisant l'objet
    """
  return get_case(plateau, pos)['objet']


def poser_pacman(plateau, pacman, pos):
  """pose un pacman en position pos sur le plateau

    Args:
        plateau (dict): le plateau considéré
        pacman (str): la lettre représentant le pacman
        pos (tuple): une paire (lig,col) de deux int
    """
  get_case(plateau, pos)['pacmans_presents'].add(pacman)


def poser_fantome(plateau, fantome, pos):
  """pose un fantome en position pos sur le plateau

    Args:
        plateau (dict): le plateau considéré
        fantome (str): la lettre représentant le fantome
        pos (tuple): une paire (lig,col) de deux int
    """
  get_case(plateau, pos)['fantomes_presents'].add(fantome)


def poser_objet(plateau, objet, pos):
  """Pose un objet en position pos sur le plateau. Si cette case contenait déjà
        un objet ce dernier disparait

    Args:
        plateau (dict): le plateau considéré
        objet (int): un entier représentant l'objet. const.AUCUN indique aucun objet
        pos (tuple): une paire (lig,col) de deux int
    """
  if not get_case(plateau, pos)["mur"]:
    get_case(plateau, pos)['objet'] = objet


def Plateau(la_chaine, complet=True):
  """Construit un plateau à partir d'une chaine de caractère contenant les informations
        sur le contenu du plateau (voir sujet)

    Args:
        la_chaine (str): la chaine de caractères décrivant le plateau

    Returns:
        dict: le plateau correspondant à la chaine. None si l'opération a échoué
  """
  lines = la_chaine.split('\n')
  # Extract dimensions
  dimensions = lines[0].split(';')
  nb_lignes = int(dimensions[0])
  nb_colonnes = int(dimensions[1])

  plateau = {
      "nb_lignes": nb_lignes,
      "nb_colonnes": nb_colonnes,
      "valeurs": [case.Case() for i in range(nb_lignes * nb_colonnes)]
  }

  for i, line in enumerate(lines[1:nb_lignes + 1]):
    for j, char in enumerate(line):
      if char == const.MUR:
        get_case(plateau, (i, j))['mur'] = True
      else:
        poser_objet(plateau, char, (i, j))

  nb_pac = int(lines[nb_lignes + 1])
  for pac in lines[nb_lignes + 2:nb_lignes + 2 + nb_pac]:
    (nom, x, y) = pac.split(';')
    poser_pacman(plateau, nom, (int(x), int(y)))

  for fan in lines[nb_lignes + nb_pac + 3:]:
    if not fan:
      break
    (nom, x, y) = fan.split(';')
    poser_fantome(plateau, nom, (int(x), int(y)))

  return plateau


def set_case(plateau, pos, une_case):
  """remplace la case qui se trouve en position pos du plateau par une_case

    Args:
        plateau (dict): le plateau considéré
        pos (tuple): une paire (lig,col) de deux int
        une_case (dict): la nouvelle case
    """
  plateau['valeurs'][plateau['nb_colonnes'] * pos[0] + pos[1]] = une_case


def enlever_pacman(plateau, pacman, pos):
  """enlève un joueur qui se trouve en position pos sur le plateau

    Args:
        plateau (dict): le plateau considéré
        pacman (str): la lettre représentant le joueur
        pos (tuple): une paire (lig,col) de deux int

    Returns:
        bool: True si l'opération s'est bien déroulée, False sinon
    """
  if pacman in get_case(plateau, pos)['pacmans_presents']:
    get_case(plateau, pos)['pacmans_presents'].remove(pacman)
    return True
  return False


def enlever_fantome(plateau, fantome, pos):
  """enlève un fantome qui se trouve en position pos sur le plateau

    Args:
        plateau (dict): le plateau considéré
        fantome (str): la lettre représentant le fantome
        pos (tuple): une paire (lig,col) de deux int

    Returns:
        bool: True si l'opération s'est bien déroulée, False sinon
  """

  if fantome in get_case(plateau, pos)['fantomes_presents']:
    get_case(plateau, pos)["fantomes_presents"].remove(fantome)
    return True
  return False


def prendre_objet(plateau, pos):
  """Prend l'objet qui se trouve en position pos du plateau et retourne l'entier
        représentant cet objet. const.AUCUN indique qu'aucun objet se trouve sur case

    Args:
        plateau (dict): Le plateau considéré
        pos (tuple): une paire (lig,col) de deux int

    Returns:
        int: l'entier représentant l'objet qui se trouvait sur la case.
        const.AUCUN indique aucun objet
    """
  objet = get_objet(plateau, pos)
  set_case(plateau, pos, case.Case(objet=const.AUCUN))
  return objet


def deplacer_pacman(plateau, pacman, pos, direction, passemuraille=False):
  """Déplace dans la direction indiquée un joueur se trouvant en position pos
        sur le plateau si c'est possible

    Args:
        plateau (dict): Le plateau considéré
        pacman (str): La lettre identifiant le pacman à déplacer
        pos (tuple): une paire (lig,col) d'int
        direction (str): une lettre parmie NSEO indiquant la direction du déplacement
        passemuraille (bool): un booléen indiquant si le pacman est passemuraille ou non

    Returns:
        (int,int): une paire (lig,col) indiquant la position d'arrivée du pacman 
                   (None si le pacman n'a pas pu se déplacer)
    """
  new_pos = pos_arrivee(plateau, pos, direction)
  if (not passemuraille
      and get_case(plateau, new_pos)['mur']) or pacman not in get_case(
          plateau, pos)["pacmans_presents"]:
    return None
  enlever_pacman(plateau, pacman, pos)
  poser_pacman(plateau, pacman, new_pos)
  return new_pos


def deplacer_fantome(plateau, fantome, pos, direction):
  """Déplace dans la direction indiquée un fantome se trouvant en position pos
        sur le plateau

    Args:
        plateau (dict): Le plateau considéré
        fantome (str): La lettre identifiant le fantome à déplacer
        pos (tuple): une paire (lig,col) d'int
        direction (str): une lettre parmie NSEO indiquant la direction du déplacement

    Returns:
        (int,int): une paire (lig,col) indiquant la position d'arrivée du fantome
                   None si le joueur n'a pas pu se déplacer
    """
  new_pos = pos_arrivee(plateau, pos, direction)
  if new_pos == pos or get_case(plateau, new_pos)['mur']:
    return None
  enlever_fantome(plateau, fantome, pos)
  poser_fantome(plateau, fantome, new_pos)
  return new_pos


def case_vide(plateau):
  """choisi aléatoirement sur la plateau une case qui n'est pas un mur et qui
       ne contient ni pacman ni fantome ni objet

    Args:
        plateau (dict): le plateau

    Returns:
        (int,int): la position choisie
    """
  nb_ligne = get_nb_lignes(plateau)
  nb_colonnes = get_nb_colonnes(plateau)
  pos = (random.randint(0, nb_ligne - 1), random.randint(0, nb_colonnes - 1))
  while get_case(plateau, pos) != case.Case():
    pos = (random.randint(0, nb_ligne - 1), random.randint(0, nb_colonnes - 1))
  return pos


def directions_possibles(plateau, pos, passemuraille=False):
  """ retourne les directions vers où il est possible de se déplacer à partir
        de la position pos

    Args:
        plateau (dict): le plateau considéré
        pos (tuple): un couple d'entiers (ligne,colonne) indiquant la position de départ
        passemuraille (bool): indique si on s'autorise à passer au travers des murs
    
    Returns:
        str: une chaine de caractères indiquant les directions possibles
              à partir de pos
    """
  directions = ""
  tent = pos_nord(plateau, pos)
  if tent != pos and (passemuraille
                      or not case.est_mur(get_case(plateau, tent))):
    directions += "N"
  tent = pos_est(plateau, pos)
  if tent != pos and (passemuraille
                      or not case.est_mur(get_case(plateau, tent))):
    directions += "E"
  tent = pos_sud(plateau, pos)
  if tent != pos and (passemuraille
                      or not case.est_mur(get_case(plateau, tent))):
    directions += "S"
  tent = pos_ouest(plateau, pos)
  if tent != pos and (passemuraille
                      or not case.est_mur(get_case(plateau, tent))):
    directions += "O"
  return directions


#---------------------------------------------------------#


def analyse_plateau(plateau, pos, direction, distance_max):
  """calcul les distances entre la position pos et les différents objets et
        joueurs du plateau si on commence par partir dans la direction indiquée
        en se limitant à la distance max. Si il n'est pas possible d'aller dans la
        direction indiquée à partir de pos, la fonction doit retourner None

    Args:
        plateau (dict): le plateau considéré
        pos (tuple): une paire d'entiers indiquant la postion de calcul des distances
        distance_max (int): un entier indiquant la distance limite de la recherche
    Returns:
        dict: un dictionnaire de listes. 
                Les clés du dictionnaire sont 'objets', 'pacmans' et 'fantomes'
                Les valeurs du dictionnaire sont des listes de paires de la forme
                    (dist,ident) où dist est la distance de l'objet, du pacman ou du fantome
                                    et ident est l'identifiant de l'objet, du pacman ou du fantome
            S'il n'est pas possible d'aller dans la direction indiquée à partir de pos
            la fonction retourne None
    """

  objs = []
  pacs = []
  fants = []

  if "N" in direction:
    empl = pos_nord(plateau, pos)
  elif "E" in direction:
    empl = pos_est(plateau, pos)
  elif "S" in direction:
    empl = pos_sud(plateau, pos)
  elif "O" in direction:
    empl = pos_ouest(plateau, pos)

  if case.est_mur(get_case(plateau, empl)):
    return None

  explore = [(1, empl)]
  deja_vu = set()
  while explore:
    dist, origine = explore.pop(0)
    if origine in deja_vu:
      continue
    deja_vu.add(origine)
    empl = get_case(plateau, origine)
    if empl["objet"] != const.AUCUN:
      objs.append((dist, empl["objet"]))
    if empl["pacmans_presents"]:
      for pac in empl["pacmans_presents"]:
        pacs.append((dist, pac))
    if empl["fantomes_presents"]:
      for fan in empl["fantomes_presents"]:
        fants.append((dist, fan))
    if dist == distance_max:
      continue
    direction = directions_possibles(plateau, origine)
    for direct in direction:
      if "N" in direct:
        explore.append((dist + 1, pos_nord(plateau, origine)))
      elif "E" in direct:
        explore.append((dist + 1, pos_est(plateau, origine)))
      elif "S" in direct:
        explore.append((dist + 1, pos_sud(plateau, origine)))
      elif "O" in direct:
        explore.append((dist + 1, pos_ouest(plateau, origine)))

  return {'objets': objs, 'pacmans': pacs, 'fantomes': fants}


def get_dir_func(chaine):
  """retourne la fonction associée à la direction indiquée dans la chaine"""
  if "N" in chaine:
    return pos_nord
  elif "E" in chaine:
    return pos_est
  elif "S" in chaine:
    return pos_sud
  elif "O" in chaine:
    return pos_ouest


def prochaine_intersection(plateau, pos, direction):
  """calcule la distance de la prochaine intersection
      si on s'engage dans la direction indiquée

  Args:
      plateau (dict): le plateau considéré
      pos (tuple): une paire d'entiers donnant la position de départ
      direction (str): la direction choisie

  Returns:
      int: un entier indiquant la distance à la prochaine intersection
           -1 si la direction mène à un cul de sac.
  """
  distance = 0
  dir_func = get_dir_func(direction)
  pos = dir_func(plateau, pos)
  while len(directions_possibles(plateau, pos)) < 3:
    pos = dir_func(plateau, pos)
    distance += 1
    if len(directions_possibles(plateau, pos)) == "1":
      return -1

  return distance


# A NE PAS DEMANDER
def plateau_2_str(plateau):
  res = str(get_nb_lignes(plateau)) + ";" + str(
      get_nb_colonnes(plateau)) + "\n"
  pacmans = []
  fantomes = []
  for lig in range(get_nb_lignes(plateau)):
    ligne = ""
    for col in range(get_nb_colonnes(plateau)):
      la_case = get_case(plateau, (lig, col))
      if case.est_mur(la_case):
        ligne += "#"
        les_pacmans = case.get_pacmans(la_case)
        for pac in les_pacmans:
          pacmans.append((pac, lig, col))
      else:
        obj = case.get_objet(la_case)
        les_pacmans = case.get_pacmans(la_case)
        les_fantomes = case.get_fantomes(la_case)
        ligne += str(obj)
        for pac in les_pacmans:
          pacmans.append((pac, lig, col))
        for fantome in les_fantomes:
          fantomes.append((fantome, lig, col))
    res += ligne + "\n"
  res += str(len(pacmans)) + '\n'
  for pac, lig, col in pacmans:
    res += str(pac) + ";" + str(lig) + ";" + str(col) + "\n"
  res += str(len(fantomes)) + "\n"
  for fantome, lig, col in fantomes:
    res += str(fantome) + ";" + str(lig) + ";" + str(col) + "\n"
  return res


plateau_from_str = Plateau
