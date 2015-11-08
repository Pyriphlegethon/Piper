# Piper
```
“And it’s whispered that soon if we all call the tune
Then the piper will lead us to reason”
```

The goal of this project was to develop and maintain a computer algebra system (commonly abbreviated as CAS), that is capable of manipulating formal expressions to produce new expressions. A CAS can be thought of as a system that is trying to automatically derive expressions from the input the user gave. As an example consider the following interaction between Piper and the user:

```
In[1] := 2 + 2
Out[1] = 4
In[2] := Sin[2 * Pi]
Out[2] = 0
In[3] := Sin[2]
Out[3] = Sin[2]
```

For every input the user gives Piper will output an expression that is equivalent, but (when possible) in a simpler form. The input in this example wasn't of great complexity and the standard rules of Piper are pretty poor, but it is possible to add new rules to make Piper suitable for more advanced computations.

## Purpose
Piper is primarily used for educational purposes and not as a fully featured CAS. It shows how such systems (especially Mathematica) work on the inside. 
With a bit of work (on the term rewriter specifically) one might get Piper to do useful work. A rewrite in another language will presumably be inevitable, because Python is generally a slow language and Piper could be written to make use of threads if Python wouldn’t prevent that with the GIL.

## Future work
This probably won't happen, since I don't have much time to work on it.
* Add parsing and rework printing
* Add testing
* Optimize the term rewriter
* Add some more rules for simplification
* Add algorithms for calculating limits, integrals, etc.
* Add some sort of front-end
* Eventually rewrite the project in a faster language with native threading support (maybe Rust)

## Other software
There are many projects that are similar (and more advanced). The code in this repository is heavily influenced by the [Elision Term Rewriter](https://github.com/elision/elision).

## Contributing
Feel free to send pull requests with bug fixes, improvements and so on.