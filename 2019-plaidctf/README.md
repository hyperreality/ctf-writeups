Project Eulernt (40 solves)
---

We have to find a number that is a divisor of 333! as well as close to its square root.

Our solution takes advantage of the integer series making up the factorial of 333. Each of these integers is trivially a divisor of 333!. 

First we build larger factorials towards 333! until we find the one that is closest to the square root of N (sN). This turns out to be 188!.

188! is smaller than sN but not within an acceptable error margin for the solution, so we add multiples of 187! while the error reduces, until the error increases. We then subtract multiples of 186!, further reducing the error, until it increases... etc. Very soon we hit a number that is within the relative error margin that is also a divisor of N.

The solution works by getting closer and closer approximations to the correct answer, reducing the step each time. In the worst case, it would wind all the way down to step of 1, and search every number until hitting a divisor. 
