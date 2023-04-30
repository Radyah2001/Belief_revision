# Propositional Logic Engine

This project was made as part of the course 02180 Introduction to Artificial Intelligence at the Technical Univeristy of Denmark. The project is an engine for propositional logic.

# Features

## Parsing

The module _Logic.py_ contains functionality for lexing and parsing a string written in propositional logic. It takes the string and converts it into an AST which is much easier to work with than a string. The engine only works with ASTs. To convert a string into an AST use the function _logicFromString_ which takes a string as input which is a sentence in propositional logic. The syntax for the sentences can be found further down. The AST consists of different classes, one for each symbol in the syntax, which are located at the top of the module. The AST will always start with the class _LogicalSentence_ to ensure all ASTs have the same starting point.

### Examples of ASTs

- LogicalSentence(Biimplication(Symbol("a"), Disjunction(Symbol("b), Symbol("c))))
- LogicalSentence(Conjunction(Symbol("a"), Negation(Bracket(Implication(Symbol("b), Symbol("c))))))
- LogicalSentence(Conjunction(Negation(Symbol("a")), Conjunction(Symbol("B"), Disjunction(Symbol("c"), Symbol("d")))))

## Entailment

The engine can check entailment by using the truth-table method. Given a sentence it can check if it logically entails given the beliefs in the _BeliefBase_. It is also possible to check entailment by using a forward-chaining algorithm if both the belief base and the conclusion only contain definite clauses.

## Conjunctive Normal Form

The engine can convert any sentence in propositional logic into CNF. This makes it easier for many algorithms to work though none in the engine currently take advantage of this. The CNF method works by continously rewriting the sentences by using laws for distributivity, elimination and De Morgan's laws.

## Contraction of Belief Base

The engine can contract the belief base given a new belief. This works by implementing partial meet contraction.

# Syntax

- If-then-else: <=>
- Implication: =>
- Conjunction: &
- Disjunction: |
- Brackets: ()
- Negation: !
- Literal: A string starting with a letter followed by either letters or numbers

## Examples

- "a <=> b | c"
- "a & !(b => c)"
- "!a & b & c | d"
