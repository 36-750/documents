# uses X, y, and n

d = rep(1e10,n) # big
w = rep(0,n)
for(i in 1:nrow(X))  # for every point:
{
    x <- 0
    for( j in 1:ncol(X) ) {
      x = x + (X[i,j] - y[j]) * (X[i,j] - y[j]) }
      k = 1  # insert
    while(x > d[k] && k <= n)
        {
          k <- k + 1  
        }
    if(k <= n)  # otherwise ignore
    {
        if(k == 1) {  # watch the boundaries
            d <- c(x, d[-n])
            w <- c(i, w[-n])
        }
        else if (  k < n  ) 
        {
            d = c(d[1:(k-1)], x, d[k:(n-1)])
            w = c(w[1:(k-1)], i, w[k:(n-1)])
        } else {
            d <- c(d[-n], x)
            w <- c(w[-n], i)
        }
    }
}

print(c(w[n], d[n], X[w[n],]))

# Try
# X <- matrix(1:16,8,2)
# y <- c(5, 14)
# n <- 3
# source("nnk.r")



