#program edge(k,j).
e(k,j).
#program base.
vertex(X):-e(X,_).
vertex(X):-e(_,X).

%Specify the minimization
#minimize{1,X : vc(X), vertex(X)}.

% Property of the Vertex Cover
:- e(X,Y), not vc(X), not vc(Y).
% Generate Vertex Covers
e(X,Y) :- e(Y,X).

{vc(X); vc(Y)} :- e(X,Y), e(Y,Z), X != Z.
{vc(Y); vc(Z)} :- e(X,Y), e(Y,Z), X != Z.

{vc(X); vc(Y)} :- e(X,Y), e(X1,Y), X != X1.
{vc(X); vc(Y)} :- e(X,Y), e(X1,X), X != X1.

#show vc/1.