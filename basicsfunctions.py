
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

def inter(vectA, vectB):
    if len(vectA) != len(vectB):
        raise ValueError("Les vecteurs doivent avoir la même longueur")
    count = 0
    for i in range(len(vectA)):
        if ((vectA[i] == vectB[i]) and (vectA[i] != 0)):    
            count += 1
    return count

def union(vectA, vectB):
    if len(vectA) != len(vectB):
        raise ValueError("Les vecteurs doivent avoir la même longueur")
    count = 0
    for i in range(len(vectA)):
        if (vectA[i] != 0 or vectB[i] != 0):
            count += 1
    return count

def distEucl(vectA, vectB):
    if len(vectA) != len(vectB):
        raise ValueError("Les vecteurs doivent avoir la même longueur")
    res = 0
    for i in range(len(vectA)):
        res+= (vectA[i] - vectB[i])**2
    return math.sqrt(res)


# fonctions de similarité

def simCos(vectA, vectB):
    normA = norm(vectA)
    normB = norm(vectB)
    if normA == 0 or normB == 0:
        raise ValueError("La norme d'un vecteur ne peut pas être zéro")
    return prodScal(vectA, vectB) / (normA * normB)

def simEucl1(vectA, vectB):
    return 1 / (1 + distEucl(vectA, vectB))

def simEucl2(vectA, vectB):
    return math.exp(-distEucl(vectA, vectB))

def jacc(vectA, vectB):
    u = union(vectA, vectB)
    if u == 0:
        return 0  
    return inter(vectA, vectB) / u


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


# tester l'item-based sur chaque musique que l'utilisateur n'a pas écouté et recommander les musiques avec la prédiction la plus élevée
def recommend(u, matr, items, n):
    predictions = []

    for i in range(len(items)):
        if matr[u][i] == 0:   # l’utilisateur n’a pas noté l’item
            pred = itemBased(u, i, matr, items)
            predictions.append((i, pred))

    predictions.sort(key=lambda x: x[1], reverse=True) # trier pour pouvoir renvoyer les n meilleures

    return predictions[:n]  # retourner les K meilleurs

# recommend(user, matr, echonest, 5)

def simcosinus(set1, set2):
    """Calcule la similarité cosinus entre deux ensembles d'éléments."""
    if not set1 or not set2:
        return 0.0
    
    # Créer des vecteurs binaires pour les ensembles
    all_items = list(set1.union(set2))
    vec1 = [1 if item in set1 else -1 for item in all_items]
    vec2 = [1 if item in set2 else -1 for item in all_items]
    
    # Calculer la similarité cosinus
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return dot_product / (norm1 * norm2)