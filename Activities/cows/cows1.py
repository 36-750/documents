
def cow_proximity(breed_ids, threshold):
    pass

def cow_proximity_l(breed_ids, threshold):
    biggest = -1
    seen = {}

    for index, breed in enumerate(breed_ids):
        if breed > biggest:
            if breed in seen:
                if index - seen[breed] <= threshold:
                    biggest = breed
                    del seen[breed]
                else:
                    seen[breed] = index
            else:
                seen[breed] = index
    return biggest

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
