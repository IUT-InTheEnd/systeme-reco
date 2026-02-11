import math
import pandas as pd 

# fonctions de base sur les vecteurs

def prodScal(a, b):
    if len(a) != len(b):
        raise ValueError("Les vecteurs doivent avoir la même longueur")
    res = 0
    for i in range(len(a)):
        res += a[i] * b[i]
    return res

def norm(vect):
    res = 0
    for x in vect:
        res += x**2
    return math.sqrt(res)

def inter(vect_a, vect_b):
    if len(vect_a) != len(vect_b):
        raise ValueError("Les vecteurs doivent avoir la même longueur")
    count = 0
    for i in range(len(vect_a)):
        if ((vect_a[i] == vect_b[i]) and (vect_a[i] != 0)):    
            count += 1
    return count

def union(vect_a, vect_b):
    if len(vect_a) != len(vect_b):
        raise ValueError("Les vecteurs doivent avoir la même longueur")
    count = 0
    for i in range(len(vect_a)):
        if (vect_a[i] != 0 or vect_b[i] != 0):
            count += 1
    return count

def distEucl(vect_a, vect_b):
    if len(vect_a) != len(vect_b):
        raise ValueError("Les vecteurs doivent avoir la même longueur")
    res = 0
    for i in range(len(vect_a)):
        res+= (vect_a[i] - vect_b[i])**2
    return math.sqrt(res)


# fonctions de similarité

def simCos(vect_a, vect_b):
    normA = norm(vect_a)
    normB = norm(vect_b)
    if normA == 0 or normB == 0:
        raise ValueError("La norme d'un vecteur ne peut pas être zéro")
    return prodScal(vect_a, vect_b) / (normA * normB)

def simEucl1(vect_a, vect_b):
    return 1 / (1 + distEucl(vect_a, vect_b))

def simEucl2(vect_a, vect_b):
    return math.exp(-distEucl(vect_a, vect_b))

def jacc(vect_a, vect_b):
    u = union(vect_a, vect_b)
    if u == 0:
        return 0  
    return inter(vect_a, vect_b) / u


# fonction de prédiction item-based 

def itemBased(u, i, matr, items):
    sNumerateur = 0
    sDenominateur = 0

    # calcul des similarités entre l'item i et tous les autres items
    sim = [0] * len(items)
    for j in range(len(items)):
        if j != i:
            sim[j] = simCos(items[i], items[j]) 
        else:
            sim[j] = 0

    # calcul de la prédiction
    for j in range(len(items)):
        if matr[u][j] != 0:               
            sNumerateur += matr[u][j] * sim[j] # somme du produit entre la note de u pour chaque item et la similarité de l'item et i
            sDenominateur += abs(sim[j]) # somme des similarités entre les tous les items et i

    if sDenominateur == 0: # eviter la division par zero
        return 0  

    return sNumerateur / sDenominateur


def jaccard_similarity(set1, set2):
    """Calcule la similarité de Jaccard entre deux ensembles"""
    union = set1 | set2
    if len(union) == 0:
        return 0.0
    intersection = set1 & set2
    return len(intersection) / len(union)