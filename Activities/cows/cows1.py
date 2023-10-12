
def cow_proximity(breed_ids, threshold):
    pass

def cow_proximity_brute_force(breed_ids, threshold):
    biggest = -1
    n = len(breed_ids)
    for i in range(n):
        breed = breed_ids[i]
        for j in range(threshold):
            i_prime = i + j + 1
            if i_prime < n and breed == breed_ids[i + j + 1]:
                biggest = max(biggest, breed)
    return biggest
