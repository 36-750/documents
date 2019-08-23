# first need to do:
# import numpy as np
# uses X, y, and n

d = np.ones(n) * 1.0e10 # big
w = np.zeros(n)
for i in range(X.shape[0]):  # for every point:
    x = 0


    for j in X.shape[1]:
        x = x + (X[i,j] - y[j]) * (X[i,j] - y[j]) 
    k = 1  # insert
    while x > d[k] and k < n:
        k = k + 1  
        
    if k < n:  # otherwise ignore
        if k == 0:   # watch the boundaries
            d = np.concatenate([np.array([x]), d[:-1]])
            w = np.concatenate([np.array([i]), w[:-1]])
        elif k < n:
            d = np.concatenate([d[0:(k-1)], np.array([x]), d[k:-1]])
            w = np.concatenate([w[0:(k-1)], np.array([i]), w[k:-1]])
        else: 
            d = np.concatenate([d[:-1], np.array[x]))
            w = np.concatenate([w[:-1], np.array[i]))
        

print(w[n], d[n], X[w[n],])

# Try
# X = np.arange(16, dtype='float64').reshape(8,2)
# y = np.array([5.0, 14.0])
# n = 3
# execfile('nnk.py')



