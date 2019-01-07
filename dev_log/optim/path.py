# Etape 1: clustering
# Etape 2: recherche d'un plus court chemin 

import random

WITHINWALKINGDISTANCE = 10

def distance(pos1, pos2):
    """
    
    """

def chemin(patients):
    """
    @param patients: a dict of the patients to be seen.
    k = patient_id
    v = position (latitude, longitude)
    
    @return tour: an hamiltonian tour on these positions.
    tour is a list representing a permutation on the patient ids
    """

    return list(patients.keys())

def clustering(patients, threshold):
    """
    @param patients: a dict of the patients to be seen.
    k = patient_id
    v = position (latitude, longitude)

    @return clusters: a dictionnary clustering the points such that all 
    distances are within the threshold.
    k = center (patient id)
    v = id of patients in the cluster
    """
    p = patients.copy()
    ids = list(p.keys())

    clusters = dict()

    while p:
        center_id = random.randint(0,len(ids)-1)
        center_pos = p[ids[center_id]]
        cluster = []
        for patient_id, patient_pos in p.items():
            pass

if __name__ == "__main__":
    patients = dict()
    for k in range(1,15,2):
        patients[k] = (180. * (random.random()-.5), 360. * (random.random()-.5))
    print(chemin(patients))