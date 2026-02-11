use std::collections::HashSet;
use ordered_float::OrderedFloat;

macro_rules! vector_size_err {
    () => {Err("Les vecteurs doivent avoir la même longueur")};
}
pub fn prod_scal(a: Vec<f64>, b: Vec<f64>) -> Result<f64, &'static str> {
    if a.len() != b.len() {
        vector_size_err!()
    } else {
        let mut res = 0.0;
        for i in 0..a.len() {
            res += a[i] * b[i];
        }
        Ok(res)
    }
}

pub fn norm(vect: &Vec<f64>) -> f64 {
    let mut res = 0.0;
    for i in 0..vect.len() {
        res += vect[i].powi(2);
    }
    res.sqrt()
}

// START: fonctions ne fonctionnant que pour les vecteurs binaires
/// intersection pour des ensembles binaires
pub fn inter_bin(vect_a: Vec<u8>, vect_b: Vec<u8>) -> Result<u8, &'static str> {
    if vect_a.len() != vect_b.len() {
        vector_size_err!()
    } else {
        let mut count = 0;
        for i in 0..vect_a.len() {
            if vect_a[i] == vect_b[i] && vect_a[i] != 0 {
                count += 1;
            }
        }
        Ok(count)
    }
}

/// union pour des ensembles binaires
pub fn union_bin(vect_a: &Vec<u8>, vect_b: &Vec<u8>) -> Result<u8, &'static str> {
    if vect_a.len() != vect_b.len() {
        vector_size_err!()
    } else {
        let mut count = 0;
        for i in 0..vect_a.len() {
            if vect_a[i] != 0 || vect_b[i] != 0 {
                count += 1;
            }
        }
        Ok(count)
    }
}
// END

pub fn dist_eucl(vect_a: Vec<f64>, vect_b: Vec<f64>) -> Result<f64, &'static str> {
    if vect_a.len() != vect_b.len() {
        vector_size_err!()
    } else {
        let mut res = 0.0;
        for i in 0..vect_a.len() {
            res += (vect_a[i] * vect_b[i]).powi(2);
        }
        Ok(res.sqrt())
    }
}

pub fn sim_cos(vect_a: Vec<f64>, vect_b: Vec<f64>) -> Result<f64, &'static str> {
    let norm_a = norm(&vect_a);
    let norm_b = norm(&vect_b);
    if norm_a == 0.0 || norm_b == 0.0 {
        Err("La norme d'un vecteur ne peut pas être zéro")
    } else {
        Ok(prod_scal(vect_a, vect_b)? / (norm_a * norm_b))
    }
}

pub fn sim_eucl1(vect_a: Vec<f64>, vect_b: Vec<f64>) -> Result<f64, &'static str> {
    Ok(1.0 / (1.0 + dist_eucl(vect_a, vect_b)?))
}

pub fn sim_eucl2(vect_a: Vec<f64>, vect_b: Vec<f64>) -> Result<f64, &'static str> {
    Ok((-dist_eucl(vect_a, vect_b)?).exp())
}

/// simmilarité de Jaccard uniquement pour les ensembles binaires
pub fn jaccard_bin(vect_a: Vec<u8>, vect_b: Vec<u8>) -> Result<u8, &'static str> {
    let u = union_bin(&vect_a, &vect_b)?;
    if u == 0 {
        Ok(0)
    } else {
        Ok(inter_bin(vect_a, vect_b)? / u)
    }
}

/// simmilarité de Jaccard en deux ensembles
pub fn jaccard_set(set1: HashSet<OrderedFloat<f64>>, set2: HashSet<OrderedFloat<f64>>) -> Result<f64, &'static str> {
    let union: HashSet<_> = set1.union(&set2).collect();
    if union.len() == 0 {
        Ok(0.0)
    } else {
        let intersection: HashSet<_> = set1.intersection(&set2).collect();
        Ok(intersection.len() as f64 / union.len() as f64)
    }
}

