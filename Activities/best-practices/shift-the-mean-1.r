# Shift that mean
# See Cheng 1995 for details
# Replace data below with whatever data you want to use

S <- matrix(c(rnorm(200, 2,  1),  rnorm(200,  -1,  1)),  200,  2)
T <- cbind(runif(50, 0, 4), runif(50, -3, 1))
h0 <- 1.06 * sd(as.vector(S)) * 200^-0.2
K <- function(x) dnorm(x[1], 0, h0) * dnorm(x[2], 0, h0)
w = rep(1, 200)

its <- 15
co = 1

results <- array(0, dim=c(50, 2, its+1))
results[,,1] <- T
                 
for( i in 1:its )
{
  for( iT in 1:nrow(T) ) {
    x = results[iT, , i]   # results at iT x i
    de <- c(0, 0)
    tt <- 0.0
    for( iS in 1:200 )
    {
      kv <- K(x - S[iS,])             # get value of K
      de <- de + kv * w[iS] * S[iS,]  # update de
      tt = tt + kv * w[iS]
    }
    results[iT, , i+1] <- de/tt
    }
  co <- 1 + (co %% 7)
  }

plot(range(T[, 1]), range(T[, 2]), type='n', xlab="x", ylab="y")
points(T[, 1], T[, 2], pch=20)
co <- 1
for( i in 1:nrow(results ) )
    {
        matlines(results[i, 1, ], results[i, 2, ],  col=co)
        co <- 1 + (co %% 7)
    }
# Done! Use the results

      

    


