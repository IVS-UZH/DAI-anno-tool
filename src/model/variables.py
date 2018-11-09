# This file is generated automatically
# Please do not edit

# Copyright 2018 Taras Zakharko (taras.zakharko)
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.



from collections import namedtuple

Value = namedtuple("Value", ("key", "value", "mnemonic", "condition"))


Variables = (
Value("PoS", "Noun", "N", ((lambda: (isToken)).__code__)),
Value("PoS", "Adjective", "Adj", ((lambda: (isToken)).__code__)),
Value("PoS", "Verb", "V", ((lambda: (isToken)).__code__)),
Value("PoS", "Adverb", "Adv", ((lambda: (isToken)).__code__)),
Value("PoS", "Determiner", "Det", ((lambda: (isToken)).__code__)),
Value("PoS", "Pronoun", "Pro", ((lambda: (isToken)).__code__)),
Value("PoS", "Negation", "Neg", ((lambda: (isToken)).__code__)),
Value("PoS", "Conjunction", "Conj", ((lambda: (isToken)).__code__)),
Value("PoS", "Preposition", "Prep", ((lambda: (isToken)).__code__)),
Value("PoS", "Numeral", "Num", ((lambda: (isToken)).__code__)),
Value("PoS", "Quantifier", "Qnt", ((lambda: (isToken)).__code__)),
Value("PoS", "Interjection", "Intj", ((lambda: (isToken)).__code__)),
Value("PoS", "Dummy", "Dummy", ((lambda: (isToken)).__code__)),
Value("Type", "proper", "", ((lambda: (isToken and ((variables["PoS"] == "Noun")))).__code__)),
Value("Type", "common", "", ((lambda: (isToken and ((variables["PoS"] == "Noun")))).__code__)),
Value("Type", "attributive", "", ((lambda: (isToken and ((variables["PoS"]  == "Adjective") or (variables["PoS"]  == "Numeral") or (variables["PoS"]  == "Quantifier")))).__code__)),
Value("Type", "predicative", "", ((lambda: (isToken and ((variables["PoS"]  == "Adjective") or (variables["PoS"]  == "Numeral") or (variables["PoS"]  == "Quantifier")))).__code__)),
Value("Type", "article", "ART", ((lambda: (isToken and ((variables["PoS"] == "Determiner")))).__code__)),
Value("Type", "demonstrative", "DEM", ((lambda: (isToken and ((variables["PoS"] == "Determiner") or (variables["PoS"] == "Pronoun")))).__code__)),
Value("Type", "possessive", "POSS", ((lambda: (isToken and ((variables["PoS"] == "Determiner")))).__code__)),
Value("Type", "distributive", "", ((lambda: (isToken and ((variables["PoS"] == "Pronoun")))).__code__)),
Value("Type", "personal", "", ((lambda: (isToken and ((variables["PoS"] == "Pronoun")))).__code__)),
Value("Type", "reciprocal", "", ((lambda: (isToken and ((variables["PoS"] == "Pronoun")))).__code__)),
Value("Type", "indefinite", "", ((lambda: (isToken and ((variables["PoS"] == "Pronoun")))).__code__)),
Value("Type", "interrogative", "", ((lambda: (isToken and ((variables["PoS"] == "Pronoun"))) or (isToken and ((variables["PoS"] == "Adjective")))).__code__)),
Value("Type", "relative", "", ((lambda: (isToken and ((variables["PoS"] == "Pronoun")))).__code__)),
Value("Type", "reflexive", "REFL", ((lambda: (isToken and ((variables["PoS"] == "Pronoun")))).__code__)),
Value("Type", "impersonal", "", ((lambda: (isToken and ((variables["PoS"] == "Pronoun")))).__code__)),
Value("Type", "genitive/partitive (It. ne)", "", ((lambda: (isToken and ((variables["PoS"] == "Pronoun")))).__code__)),
Value("Type", "locative/existential (It. ci)", "", ((lambda: (isToken and ((variables["PoS"] == "Pronoun")))).__code__)),
Value("Type", "lexical", "", ((lambda: (isToken and ((variables["PoS"] == "Verb")))).__code__)),
Value("Type", "auxiliary HAVE", "have", ((lambda: (isToken and ((variables["PoS"] == "Verb")))).__code__)),
Value("Type", "auxiliary venire", "venire", ((lambda: (isToken and ((variables["PoS"] == "Verb")))).__code__)),
Value("Type", "auxiliary stare", "stare", ((lambda: (isToken and ((variables["PoS"] == "Verb")))).__code__)),
Value("Type", "auxiliary BE", "be", ((lambda: (isToken and ((variables["PoS"] == "Verb")))).__code__)),
Value("Type", "modal", "", ((lambda: (isToken and ((variables["PoS"] == "Verb")))).__code__)),
Value("Type", "causative", "", ((lambda: (isToken and ((variables["PoS"] == "Verb")))).__code__)),
Value("Type", "support verb", "", ((lambda: (isToken and ((variables["PoS"] == "Verb")))).__code__)),
Value("Type", "copular verb", "", ((lambda: (isToken and ((variables["PoS"] == "Verb")))).__code__)),
Value("Type", "existential", "", ((lambda: (isToken and ((variables["PoS"] == "Verb")))).__code__)),
Value("Type", "interrogative", "", ((lambda: (isToken and ((variables["PoS"] == "Pronoun"))) or (isToken and ((variables["PoS"] == "Adjective")))).__code__)),
Value("Type", "exclamative", "", ((lambda: (isToken and ((variables["PoS"] == "Adjective")))).__code__)),
Value("Head", "yes", "", ((lambda: (isToken and ((variables["PoS"] == "Noun") or (variables["PoS"] == "Pronoun") or (variables["PoS"] == "Quantifier") or (variables["PoS"] == "Numeral") or (variables["PoS"] == "Verb") or (variables["PoS"] == "Dummy")))).__code__)),
Value("Head", "no", "", ((lambda: (isToken and ((variables["PoS"] == "Noun") or (variables["PoS"] == "Pronoun") or (variables["PoS"] == "Quantifier") or (variables["PoS"] == "Numeral") or (variables["PoS"] == "Verb")))).__code__)),
Value("Lexical subtype", "unaccusative", "", ((lambda: (isToken and ((variables["PoS"] == "Verb" and variables["Type"] == "lexical")))).__code__)),
Value("Lexical subtype", "reflexive", "REFL", ((lambda: (isToken and ((variables["PoS"] == "Verb" and variables["Type"] == "lexical")))).__code__)),
Value("Lexical subtype", "unergative", "", ((lambda: (isToken and ((variables["PoS"] == "Verb" and variables["Type"] == "lexical")))).__code__)),
Value("Lexical subtype", "transitive", "", ((lambda: (isToken and ((variables["PoS"] == "Verb" and variables["Type"] == "lexical")))).__code__)),
Value("Reflexive subtype", "retroherent", "", ((lambda: (isToken and ((variables["PoS"] == "Verb" and variables["Type"] == "lexical" and variables["Lexical subtype"] == "reflexive")))).__code__)),
Value("Reflexive subtype", "direct transitive", "", ((lambda: (isToken and ((variables["PoS"] == "Verb" and variables["Type"] == "lexical" and variables["Lexical subtype"] == "reflexive")))).__code__)),
Value("Reflexive subtype", "indirect unergative", "", ((lambda: (isToken and ((variables["PoS"] == "Verb" and variables["Type"] == "lexical" and variables["Lexical subtype"] == "reflexive")))).__code__)),
Value("Reflexive subtype", "indirect transitive", "", ((lambda: (isToken and ((variables["PoS"] == "Verb" and variables["Type"] == "lexical" and variables["Lexical subtype"] == "reflexive")))).__code__)),
Value("Reflexive subtype", "antipassive", "", ((lambda: (isToken and ((variables["PoS"] == "Verb" and variables["Type"] == "lexical" and variables["Lexical subtype"] == "reflexive")))).__code__)),
Value("Mode", "indicative", "IND", ((lambda: (isToken and ((variables["PoS"] == "Verb")))).__code__)),
Value("Mode", "subjunctive", "SBJV", ((lambda: (isToken and ((variables["PoS"] == "Verb")))).__code__)),
Value("Mode", "conditional", "COND", ((lambda: (isToken and ((variables["PoS"] == "Verb")))).__code__)),
Value("Mode", "imperative", "IMP", ((lambda: (isToken and ((variables["PoS"] == "Verb")))).__code__)),
Value("Mode", "infinitive", "INF", ((lambda: (isToken and ((variables["PoS"] == "Verb")))).__code__)),
Value("Mode", "participle", "PTCP", ((lambda: (isToken and ((variables["PoS"] == "Verb")))).__code__)),
Value("Mode", "gerund", "GER", ((lambda: (isToken and ((variables["PoS"] == "Verb")))).__code__)),
Value("Participle subtype", "periphrastic", "", ((lambda: (isToken and ((variables["PoS"] == "Verb" and variables["Mode"] == "participle")))).__code__)),
Value("Participle subtype", "non periphrastic", "", ((lambda: (isToken and ((variables["PoS"] == "Verb" and variables["Mode"] == "participle")))).__code__)),
Value("Participle class", "strong", "", ((lambda: (isToken and ((variables["PoS"] == "Verb" and variables["Mode"] == "participle")))).__code__)),
Value("Participle class", "weak", "", ((lambda: (isToken and ((variables["PoS"] == "Verb" and variables["Mode"] == "participle")))).__code__)),
Value("Proximity", "proximal", "PROX", ((lambda: (isToken and ((variables["Type"] == "demonstrative")))).__code__)),
Value("Proximity", "medial", "MED", ((lambda: (isToken and ((variables["Type"] == "demonstrative")))).__code__)),
Value("Proximity", "distal", "DIST", ((lambda: (isToken and ((variables["Type"] == "demonstrative")))).__code__)),
Value("Tense/Aspect", "present", "PRS", ((lambda: (isToken and ((variables["PoS"] == "Verb")))).__code__)),
Value("Tense/Aspect", "perfect", "PRF", ((lambda: (isToken and ((variables["PoS"] == "Verb" and variables["Mode"] == "indicative") or (variables["PoS"] == "Verb" and variables["Mode"] == "subjunctive") or (variables["PoS"] == "Verb" and variables["Mode"] == "conditional") or (variables["PoS"] == "Verb" and variables["Mode"] == "imperative") or (variables["PoS"] == "Verb" and variables["Mode"] == "infinitive")))).__code__)),
Value("Tense/Aspect", "past", "PAST", ((lambda: (isToken and ((variables["PoS"] == "Verb" and variables["Mode"] == "participle")))).__code__)),
Value("Tense/Aspect", "future", "FUT", ((lambda: (isToken and ((variables["PoS"] == "Verb" and variables["Mode"] == "indicative") or (variables["PoS"] == "Verb" and variables["Mode"] == "subjunctive") or (variables["PoS"] == "Verb" and variables["Mode"] == "conditional") or (variables["PoS"] == "Verb" and variables["Mode"] == "imperative") or (variables["PoS"] == "Verb" and variables["Mode"] == "infinitive")))).__code__)),
Value("Tense/Aspect", "imperfect", "IMPF", ((lambda: (isToken and ((variables["PoS"] == "Verb" and variables["Mode"] == "indicative") or (variables["PoS"] == "Verb" and variables["Mode"] == "subjunctive") or (variables["PoS"] == "Verb" and variables["Mode"] == "conditional") or (variables["PoS"] == "Verb" and variables["Mode"] == "imperative") or (variables["PoS"] == "Verb" and variables["Mode"] == "infinitive")))).__code__)),
Value("Realisation", "overt", "", ((lambda: (isToken and ((variables["PoS"] == "Pronoun")))).__code__)),
Value("Realisation", "non overt", "", ((lambda: (isToken and ((variables["PoS"] == "Pronoun")))).__code__)),
Value("Realisation", "clitic", "", ((lambda: (isToken and ((variables["PoS"] == "Pronoun")))).__code__)),
Value("Person", "1st", "1", ((lambda: (isToken and ((variables["PoS"] == "Verb"  and variables["Mode"] != "participle") or (variables["PoS"] == "Pronoun") or (variables["PoS"] == "Determiner" and variables["Type"] == "possessive")))).__code__)),
Value("Person", "2nd", "2", ((lambda: (isToken and ((variables["PoS"] == "Verb"  and variables["Mode"] != "participle") or (variables["PoS"] == "Pronoun") or (variables["PoS"] == "Determiner" and variables["Type"] == "possessive")))).__code__)),
Value("Person", "3rd", "3", ((lambda: (isToken and ((variables["PoS"] == "Verb"  and variables["Mode"] != "participle") or (variables["PoS"] == "Pronoun") or (variables["PoS"] == "Determiner" and variables["Type"] == "possessive") or (variables["PoS"] == "Dummy")))).__code__)),
Value("PersonNumber", "singular", "SG", ((lambda: (isToken and ((variables["PoS"] == "Determiner" and variables["Type"] == "possessive")))).__code__)),
Value("PersonNumber", "plural", "PL", ((lambda: (isToken and ((variables["PoS"] == "Determiner" and variables["Type"] == "possessive")))).__code__)),
Value("Sex", "masculine", "", ((lambda: (isToken and ((variables["PoS"] == "Pronoun" and variables["Type"] == "personal")))).__code__)),
Value("Sex", "feminine", "", ((lambda: (isToken and ((variables["PoS"] == "Pronoun" and variables["Type"] == "personal")))).__code__)),
Value("Subtype", "definite", "DEF", ((lambda: (isToken and ((variables["PoS"] == "Determiner" and variables["Type"] == "article")))).__code__)),
Value("Subtype", "indefinite", "INDF", ((lambda: (isToken and ((variables["PoS"] == "Determiner" and variables["Type"] == "article")))).__code__)),
Value("Position", "prenominal", "", ((lambda: (isToken and ((variables["PoS"] == "Adjective") or (variables["PoS"] == "Determiner") or (variables["PoS"] == "Numeral") or (variables["PoS"] == "Quantifier")))).__code__)),
Value("Position", "postnominal", "", ((lambda: (isToken and ((variables["PoS"] == "Adjective") or (variables["PoS"] == "Determiner") or (variables["PoS"] == "Numeral") or (variables["PoS"] == "Quantifier")))).__code__)),
Value("Position", "preverbal", "", ((lambda: (isToken and ((variables["PoS"] == "Adverb")))).__code__)),
Value("Position", "postverbal", "", ((lambda: (isToken and ((variables["PoS"] == "Adverb")))).__code__)),
Value("Position", "preparticipial", "", ((lambda: (isToken and ((variables["PoS"] == "Adverb")))).__code__)),
Value("Position", "postparticipial", "", ((lambda: (isToken and ((variables["PoS"] == "Adverb")))).__code__)),
Value("Countness", "count", "", ((lambda: (isToken and ((variables["PoS"] == "Noun")))).__code__)),
Value("Countness", "non count", "", ((lambda: (isToken and ((variables["PoS"] == "Noun")))).__code__)),
Value("Hybrid", "hybrid", "", ((lambda: (isToken and ((variables["PoS"] == "Noun")))).__code__)),
Value("Hybrid", "non hybrid", "", ((lambda: (isToken and ((variables["PoS"] == "Noun")))).__code__)),
Value("Committee", "committee", "", ((lambda: (isToken and ((variables["PoS"] == "Noun")))).__code__)),
Value("Committee", "non committee", "", ((lambda: (isToken and ((variables["PoS"] == "Noun")))).__code__)),
Value("Animacy", "animate", "", ((lambda: (isToken and ((variables["PoS"]  == "Noun") or (variables["PoS"]  == "Pronoun")))).__code__)),
Value("Animacy", "inanimate", "", ((lambda: (isToken and ((variables["PoS"]  == "Noun") or (variables["PoS"]  == "Pronoun")))).__code__)),
Value("Human", "yes", "", ((lambda: (isToken and ((variables["PoS"]  == "Noun") or (variables["PoS"]  == "Pronoun")))).__code__)),
Value("Human", "no", "", ((lambda: (isToken and ((variables["PoS"]  == "Noun") or (variables["PoS"]  == "Pronoun")))).__code__)),
Value("Unspecified human subject", "yes", "", ((lambda: (isToken and ((variables["PoS"] == "Pronoun" and variables["Type"] == "personal" and variables["Realisation"] =="non overt")))).__code__)),
Value("Unspecified human subject", "no", "", ((lambda: (isToken and ((variables["PoS"] == "Pronoun" and variables["Type"] == "personal" and variables["Realisation"] =="non overt")))).__code__)),
Value("Abstract", "yes", "", ((lambda: (isToken and ((variables["PoS"]  == "Noun") or (variables["PoS"]  == "Pronoun")))).__code__)),
Value("Abstract", "no", "", ((lambda: (isToken and ((variables["PoS"]  == "Noun") or (variables["PoS"]  == "Pronoun")))).__code__)),
Value("Gender", "masculine", "M", ((lambda: (isToken and ((variables["PoS"] == "Noun") or (variables["PoS"] == "Adjective") or (variables["PoS"] == "Adverb") or (variables["PoS"] == "Determiner") or (variables["PoS"] == "Numeral") or (variables["PoS"] == "Pronoun") or (variables["PoS"] == "Quantifier") or (variables["PoS"] == "Verb") or (variables["PoS"] == "Preposition" and (variety in ["Ripatransone"])) or (variables["PoS"] == "Conjunction" and (variety in ["Ripatransone"])) or (variables["PoS"] == "Dummy")))).__code__)),
Value("Gender", "feminine", "F", ((lambda: (isToken and ((variables["PoS"] == "Noun") or (variables["PoS"] == "Adjective") or (variables["PoS"] == "Adverb") or (variables["PoS"] == "Determiner") or (variables["PoS"] == "Numeral") or (variables["PoS"] == "Pronoun") or (variables["PoS"] == "Quantifier") or (variables["PoS"] == "Verb") or (variables["PoS"] == "Preposition" and (variety in ["Ripatransone"])) or (variables["PoS"] == "Conjunction" and (variety in ["Ripatransone"]))))).__code__)),
Value("Gender", "(mass) neuter", "N", ((lambda: (isToken and ((variables["PoS"] == "Noun") or (variables["PoS"] == "Adjective") or (variables["PoS"] == "Adverb") or (variables["PoS"] == "Determiner") or (variables["PoS"] == "Numeral") or (variables["PoS"] == "Pronoun") or (variables["PoS"] == "Quantifier") or (variables["PoS"] == "Verb") or (variables["PoS"] == "Preposition" and (variety in ["Ripatransone"])) or (variables["PoS"] == "Conjunction" and (variety in ["Ripatransone"]))))).__code__)),
Value("Gender", "neuter", "N", ((lambda: (isToken and ((variables["PoS"] == "Noun") or (variables["PoS"] == "Adjective") or (variables["PoS"] == "Adverb") or (variables["PoS"] == "Determiner") or (variables["PoS"] == "Numeral") or (variables["PoS"] == "Pronoun") or (variables["PoS"] == "Quantifier") or (variables["PoS"] == "Verb") or (variables["PoS"] == "Preposition" and (variety in ["Ripatransone"])) or (variables["PoS"] == "Conjunction" and (variety in ["Ripatransone"])) or (variables["PoS"] == "Dummy")))).__code__)),
Value("Gender", "non autonomous neuter", "NAN", ((lambda: (isToken and ((variables["PoS"] == "Noun")))).__code__)),
Value("Gender", "non feminine", "nonF", ((lambda: (isToken and ((variables["PoS"] == "Noun") or (variables["PoS"] == "Adjective") or (variables["PoS"] == "Adverb") or (variables["PoS"] == "Determiner") or (variables["PoS"] == "Numeral") or (variables["PoS"] == "Pronoun") or (variables["PoS"] == "Quantifier") or (variables["PoS"] == "Verb") or (variables["PoS"] == "Preposition" and (variety in ["Ripatransone"])) or (variables["PoS"] == "Conjunction" and (variety in ["Ripatransone"]))))).__code__)),
Value("Gender", "non feminine singular", "nonF.sg", ((lambda: (isToken and ((variables["PoS"] == "Noun") or (variables["PoS"] == "Adjective") or (variables["PoS"] == "Adverb") or (variables["PoS"] == "Determiner") or (variables["PoS"] == "Numeral") or (variables["PoS"] == "Pronoun") or (variables["PoS"] == "Quantifier") or (variables["PoS"] == "Verb") or (variables["PoS"] == "Preposition" and (variety in ["Ripatransone"])) or (variables["PoS"] == "Conjunction" and (variety in ["Ripatransone"]))))).__code__)),
Value("Gender", "non masculine", "nonM", ((lambda: (isToken and ((variables["PoS"] == "Noun") or (variables["PoS"] == "Adjective") or (variables["PoS"] == "Adverb") or (variables["PoS"] == "Determiner") or (variables["PoS"] == "Numeral") or (variables["PoS"] == "Pronoun") or (variables["PoS"] == "Quantifier") or (variables["PoS"] == "Verb") or (variables["PoS"] == "Preposition" and (variety in ["Ripatransone"])) or (variables["PoS"] == "Conjunction" and (variety in ["Ripatransone"]))))).__code__)),
Value("Number", "singular", "SG", ((lambda: (isToken and ((variables["PoS"] == "Noun") or (variables["PoS"] == "Adjective") or (variables["PoS"] == "Adverb") or (variables["PoS"] == "Determiner") or (variables["PoS"] == "Numeral") or (variables["PoS"] == "Pronoun") or (variables["PoS"] == "Quantifier") or (variables["PoS"] == "Verb") or (variables["PoS"] == "Preposition" and (variety in ["Ripatransone"])) or (variables["PoS"] == "Conjunction" and (variety in ["Ripatransone"])) or (variables["PoS"] == "Dummy")))).__code__)),
Value("Case", "Subject", "SBJ", ((lambda: (isToken and ((variables["PoS"] == "Pronoun" and variables["Type"] == "personal")))).__code__)),
Value("Case", "Direct object", "DO", ((lambda: (isToken and ((variables["PoS"] == "Pronoun" and variables["Type"] == "personal")))).__code__)),
Value("Case", "Indirect object", "IO", ((lambda: (isToken and ((variables["PoS"] == "Pronoun" and variables["Type"] == "personal")))).__code__)),
Value("Case", "DO+IO", "DO+IO", ((lambda: (isToken and ((variables["PoS"] == "Pronoun")) and (variety in ["Urbino"]))).__code__)),
Value("Case", "Comitative", "COM", ((lambda: (isToken and ((variables["PoS"] == "Pronoun" and variables["Type"] == "personal")))).__code__)),
Value("Number", "plural", "PL", ((lambda: (isToken and ((variables["PoS"] == "Noun") or (variables["PoS"] == "Adjective") or (variables["PoS"] == "Adverb") or (variables["PoS"] == "Determiner") or (variables["PoS"] == "Numeral") or (variables["PoS"] == "Pronoun") or (variables["PoS"] == "Quantifier") or (variables["PoS"] == "Verb") or (variables["PoS"] == "Preposition" and (variety in ["Ripatransone"])) or (variables["PoS"] == "Conjunction" and (variety in ["Ripatransone"]))))).__code__)),
Value("Default", "yes", "", ((lambda: (isToken and ((variables["PoS"] == "Adjective") or (variables["PoS"] == "Adverb") or (variables["PoS"] == "Pronoun") or (variables["PoS"] == "Verb") or (variables["PoS"] == "Quantifier") or (variables["PoS"] == "Preposition" and (variety in ["Ripatransone"])) or (variables["PoS"] == "Conjunction" and (variety in ["Ripatransone"]))))).__code__)),
Value("Default", "no", "", ((lambda: (isToken and ((variables["PoS"] == "Adjective") or (variables["PoS"] == "Adverb") or (variables["PoS"] == "Pronoun") or (variables["PoS"] == "Verb") or (variables["PoS"] == "Quantifier") or (variables["PoS"] == "Preposition" and (variety in ["Ripatransone"])) or (variables["PoS"] == "Conjunction" and (variety in ["Ripatransone"]))))).__code__)),
Value("IC", "I", "I", ((lambda: (isToken and ((variables["PoS"] == "Noun") or (variables["PoS"] == "Quantifier") or (variables["PoS"] == "Adjective") or (variables["PoS"] == "Adverb") or (variables["PoS"] == "Numeral") or (variables["PoS"] == "Verb") or (variables["PoS"] == "Preposition" and (variety in ["Ripatransone"])) or (variables["PoS"] == "Conjunction" and (variety in ["Ripatransone"]))))).__code__)),
Value("IC", "II", "II", ((lambda: (isToken and ((variables["PoS"] == "Noun") or (variables["PoS"] == "Quantifier") or (variables["PoS"] == "Adjective") or (variables["PoS"] == "Adverb") or (variables["PoS"] == "Numeral") or (variables["PoS"] == "Verb") or (variables["PoS"] == "Preposition" and (variety in ["Ripatransone"])) or (variables["PoS"] == "Conjunction" and (variety in ["Ripatransone"]))))).__code__)),
Value("IC", "III", "III", ((lambda: (isToken and ((variables["PoS"] == "Noun") or (variables["PoS"] == "Quantifier") or (variables["PoS"] == "Adjective") or (variables["PoS"] == "Adverb") or (variables["PoS"] == "Numeral") or (variables["PoS"] == "Verb")))).__code__)),
Value("IC", "IV", "IV", ((lambda: (isToken and ((variables["PoS"] == "Noun") or (variables["PoS"] == "Adjective") or (variables["PoS"] == "Verb")))).__code__)),
Value("IC", "V", "V", ((lambda: (isToken and ((variables["PoS"] == "Noun") or (variables["PoS"] == "Adjective") or (variables["PoS"] == "Verb")))).__code__)),
Value("IC", "VI", "VI", ((lambda: (isToken and ((variables["PoS"] == "Noun") or (variables["PoS"] == "Adjective") or (variables["PoS"] == "Verb")))).__code__)),
Value("IC", "VII", "VII", ((lambda: (isToken and ((variables["PoS"] == "Noun") or (variables["PoS"] == "Adjective") or (variables["PoS"] == "Verb")))).__code__)),
Value("IC", "VIII", "VIII", ((lambda: (isToken and ((variables["PoS"] == "Noun") or (variables["PoS"] == "Adjective") or (variables["PoS"] == "Verb")))).__code__)),
Value("IC", "IX", "IX", ((lambda: (isToken and ((variables["PoS"] == "Noun") or (variables["PoS"] == "Verb")))).__code__)),
Value("IC", "X", "X", ((lambda: (isToken and ((variables["PoS"] == "Noun") or (variables["PoS"] == "Verb")))).__code__)),
Value("IC", "XI", "XI", ((lambda: (isToken and ((variables["PoS"] == "Noun")) and (variety in ["Agnone"]))).__code__)),
Value("IC", "XII", "XII", ((lambda: (isToken and ((variables["PoS"] == "Noun")) and (variety in ["Agnone"]))).__code__)),
Value("IC", "XIII", "XIII", ((lambda: (isToken and ((variables["PoS"] == "Noun")) and (variety in ["Agnone"]))).__code__)),
Value("Inflection Subtype", "full", "", ((lambda: (isToken and ((variables["PoS"] == "Noun") or (variables["PoS"] == "Quantifier") or (variables["PoS"] == "Adjective") or (variables["PoS"] == "Adverb") or (variables["PoS"] == "Numeral") or (variables["PoS"] == "Verb") or (variables["PoS"] == "Preposition") or (variables["PoS"] == "Conjunction")) and (variety in ["Ripatransone"]))).__code__)),
Value("Inflection Subtype", "reduced", "", ((lambda: (isToken and ((variables["PoS"] == "Noun") or (variables["PoS"] == "Quantifier") or (variables["PoS"] == "Adjective") or (variables["PoS"] == "Adverb") or (variables["PoS"] == "Numeral") or (variables["PoS"] == "Verb") or (variables["PoS"] == "Preposition") or (variables["PoS"] == "Conjunction")) and (variety in ["Ripatransone"]))).__code__)),
Value("Stem Alternation", "yes", "", ((lambda: (isToken and ((variables["PoS"] == "Noun") or (variables["PoS"] == "Adjective") or (variables["PoS"] == "Adverb") or (variables["PoS"] == "Numeral") or (variables["PoS"] == "Quantifier") or (variables["PoS"] == "Verb") or (variables["PoS"] == "Preposition" and (variety in ["Ripatransone"])) or (variables["PoS"] == "Conjunction" and (variety in ["Ripatransone"]))))).__code__)),
Value("Stem Alternation", "no", "", ((lambda: (isToken and ((variables["PoS"] == "Noun") or (variables["PoS"] == "Adjective") or (variables["PoS"] == "Adverb") or (variables["PoS"] == "Numeral") or (variables["PoS"] == "Quantifier") or (variables["PoS"] == "Verb") or (variables["PoS"] == "Preposition" and (variety in ["Ripatransone"])) or (variables["PoS"] == "Conjunction" and (variety in ["Ripatransone"]))))).__code__)),
Value("Contextual", "yes", "", ((lambda: (isToken and ((variables["PoS"] == "Noun")))).__code__)),
Value("Contextual", "no", "", ((lambda: (isToken and ((variables["PoS"] == "Noun")))).__code__)),
Value("Gender Contextual", "masculine", "M", ((lambda: (isToken and ((variables["PoS"] == "Noun")) and (variety in ["Ripatransone"]))).__code__)),
Value("Gender Contextual", "feminine", "F", ((lambda: (isToken and ((variables["PoS"] == "Noun")) and (variety in ["Ripatransone"]))).__code__)),
Value("Gender Contextual", "(mass) neuter", "N", ((lambda: (isToken and ((variables["PoS"] == "Noun")) and (variety in ["Ripatransone"]))).__code__)),
Value("Gender Contextual", "non autonomous neuter", "NAN", ((lambda: (isToken and ((variables["PoS"] == "Noun")) and (variety in ["Ripatransone"]))).__code__)),
Value("Number Contextual", "singular", "SG", ((lambda: (isToken and ((variables["PoS"] == "Noun")) and (variety in ["Ripatransone"]))).__code__)),
Value("Number Contextual", "plural", "PL", ((lambda: (isToken and ((variables["PoS"] == "Noun")) and (variety in ["Ripatransone"]))).__code__)),
Value("IC Contextual", "I", "I", ((lambda: (isToken and ((variables["PoS"] == "Noun")) and (variety in ["Ripatransone"]))).__code__)),
Value("IC Contextual", "II", "II", ((lambda: (isToken and ((variables["PoS"] == "Noun")) and (variety in ["Ripatransone"]))).__code__)),
Value("IC Contextual", "III", "III", ((lambda: (isToken and ((variables["PoS"] == "Noun")) and (variety in ["Ripatransone"]))).__code__)),
Value("IC Contextual", "IV", "IV", ((lambda: (isToken and ((variables["PoS"] == "Noun")) and (variety in ["Ripatransone"]))).__code__)),
Value("IC Contextual", "V", "V", ((lambda: (isToken and ((variables["PoS"] == "Noun")) and (variety in ["Ripatransone"]))).__code__)),
Value("IC Contextual", "VI", "VI", ((lambda: (isToken and ((variables["PoS"] == "Noun")) and (variety in ["Ripatransone"]))).__code__)),
Value("IC Contextual", "VII", "VII", ((lambda: (isToken and ((variables["PoS"] == "Noun")) and (variety in ["Ripatransone"]))).__code__)),
Value("IC Contextual", "VIII", "VIII", ((lambda: (isToken and ((variables["PoS"] == "Noun")) and (variety in ["Ripatransone"]))).__code__)),
Value("IC Contextual", "IX", "IX", ((lambda: (isToken and ((variables["PoS"] == "Noun")) and (variety in ["Ripatransone"]))).__code__)),
Value("IC Contextual", "X", "X", ((lambda: (isToken and ((variables["PoS"] == "Noun")) and (variety in ["Ripatransone"]))).__code__)),
Value("Neutralization (phonological)", "yes", "", ((lambda: (isToken and ((variables["PoS"] == "Noun") or (variables["PoS"] == "Quantifier") or (variables["PoS"] == "Adjective") or (variables["PoS"] == "Verb") or (variables["PoS"] == "Numeral") or (variables["PoS"] == "Preposition" and (variety in ["Ripatransone"])) or (variables["PoS"] == "Conjunction" and (variety in ["Ripatransone"]))) and (variety in ["Verbicaro", "Ripatransone", "Urbino"])) or (isToken and ((variables["PoS"] == "Adverb")))).__code__)),
Value("Neutralization (phonological)", "no", "", ((lambda: (isToken and ((variables["PoS"] == "Noun") or (variables["PoS"] == "Quantifier") or (variables["PoS"] == "Adjective") or (variables["PoS"] == "Verb") or (variables["PoS"] == "Numeral") or (variables["PoS"] == "Preposition" and (variety in ["Ripatransone"])) or (variables["PoS"] == "Conjunction" and (variety in ["Ripatransone"]))) and (variety in ["Verbicaro", "Ripatransone", "Urbino"])) or (isToken and ((variables["PoS"] == "Adverb")))).__code__)),
Value("Scope", "wide", "", ((lambda: (isToken and ((variables["PoS"] == "Numeral") or (variables["PoS"] == "Quantifier")))).__code__)),
Value("Scope", "narrow", "", ((lambda: (isToken and ((variables["PoS"] == "Numeral") or (variables["PoS"] == "Quantifier")))).__code__)),
Value("Focus", "yes", "", ((lambda: (isToken and ((variables["PoS"] == "Noun" and variables["Realisation"] != "non overt") or (variables["PoS"] == "Adjective" and variables["Realisation"] != "non overt") or (variables["PoS"] == "Adverb" and variables["Realisation"] != "non overt") or (variables["PoS"] == "Determiner" and variables["Realisation"] != "non overt") or (variables["PoS"] == "Numeral" and variables["Realisation"] != "non overt") or (variables["PoS"] == "Pronoun" and variables["Realisation"] != "non overt") or (variables["PoS"] == "Quantifier"and variables["Realisation"] != "non overt") or (variables["PoS"] == "Verb" and variables["Realisation"] != "non overt") or (variables["PoS"] == "Preposition" and (variety in ["Ripatransone"])) or (variables["PoS"] == "Conjunction" and (variety in ["Ripatransone"]))))).__code__)),
Value("Focus", "no", "", ((lambda: (isToken and ((variables["PoS"] == "Noun" and variables["Realisation"] != "non overt") or (variables["PoS"] == "Adjective" and variables["Realisation"] != "non overt") or (variables["PoS"] == "Adverb" and variables["Realisation"] != "non overt") or (variables["PoS"] == "Determiner" and variables["Realisation"] != "non overt") or (variables["PoS"] == "Numeral" and variables["Realisation"] != "non overt") or (variables["PoS"] == "Pronoun" and variables["Realisation"] != "non overt") or (variables["PoS"] == "Quantifier"and variables["Realisation"] != "non overt") or (variables["PoS"] == "Verb" and variables["Realisation"] != "non overt") or (variables["PoS"] == "Preposition" and (variety in ["Ripatransone"])) or (variables["PoS"] == "Conjunction" and (variety in ["Ripatransone"]))))).__code__)),
Value("PhraseType", "NP", "NP", ((lambda: (isConstituent)).__code__)),
Value("PhraseType", "PP", "PP", ((lambda: (isConstituent)).__code__)),
Value("PhraseType", "AP", "AP", ((lambda: (isConstituent)).__code__)),
Value("PhraseType", "Clause", "Clause", ((lambda: (isConstituent)).__code__)),
Value("PhraseType", "Conjoined NPs", "Conjoined NPs", ((lambda: (isConstituent)).__code__)),
Value("PhraseType", "AdvP", "AdvP", ((lambda: (isConstituent)).__code__)),
Value("PhraseType", "QP", "QP", ((lambda: (isConstituent)).__code__)),
Value("GrammRel", "Subject", "Subject", ((lambda: (isConstituent)).__code__)),
Value("GrammRel", "Direct object", "Direct object", ((lambda: (isConstituent)).__code__)),
Value("GrammRel", "Indirect object", "Indirect object", ((lambda: (isConstituent)).__code__)),
Value("Position", "Preverbal", "", ((lambda: (isConstituent and ((variables["GrammRel"]  == "Subject") or (variables["GrammRel"]  == "Object")))).__code__)),
Value("Position", "Postverbal", "", ((lambda: (isConstituent and ((variables["GrammRel"]  == "Subject") or (variables["GrammRel"]  == "Object")))).__code__)),
Value("Compound Tenses", "Compound perfect", "Compound perfect", ((lambda: (isConstituent)).__code__)),
Value("Compound Tenses", "Compound future", "Compound future", ((lambda: (isConstituent)).__code__)),
Value("Compound Tenses", "Pluperfect", "Compound tense (pluperfect)", ((lambda: (isConstituent)).__code__)),
Value("Compound Tenses", "Passive", "Compound tense (passive)", ((lambda: (isConstituent)).__code__)),
Value("Periphrases", "progressive", "progressive", ((lambda: (isConstituent)).__code__)),
Value("Periphrases", "comparative", "comparative", ((lambda: (isConstituent)).__code__)),
Value("Periphrases", "superlative", "superlative", ((lambda: (isConstituent)).__code__)),
Value("Type", "NP Agreement", "NP Agreement", ((lambda: (isDependency)).__code__)),
Value("Type", "Antecedent-Relative", "Antecedent-Relative", ((lambda: (isDependency)).__code__)),
Value("Type", "Part Agreement", "", ((lambda: (isDependency)).__code__)),
Value("Type", "Infl Agreement", "Infl Agreement", ((lambda: (isDependency)).__code__)),
Value("Type", "Predicative Agreement", "Predicative Agreement", ((lambda: (isDependency)).__code__)),
Value("Type", "Quantifier Agreement", "Quantifier Agreement", ((lambda: (isDependency)).__code__)),
Value("Type", "Gerund Agreement", "Gerund Agreement", ((lambda: (isDependency and (variety in ["Ripatransone"]))).__code__)),
Value("Type", "Infinitive Agreement", "Infinitive Agreement", ((lambda: (isDependency and (variety in ["Ripatransone"]))).__code__)),
Value("Type", "Possessor-Possessed", "Possessor-Possessed", ((lambda: (isDependency)).__code__)),
Value("Type", "Antecedent-Anaphor", "Antecedent-Anaphor", ((lambda: (isDependency)).__code__)),
Value("Type", "Antecedent-Reflexive", "Antecedent-Reflexive", ((lambda: (isDependency)).__code__)),
Value("Type", "Adverbial Agreement", "Adverbial Agreement", ((lambda: (isDependency)).__code__)),
Value("Type", "Subject-Adjunct", "Subject-Adjunct", ((lambda: (isDependency)).__code__)),
Value("Subtype", "Subject-Part(Predicate)", "Subject-Part(Predicate)", ((lambda: (isDependency and ((variables["Type"]== "Part Agreement")))).__code__)),
Value("Subtype", "Direct Object-Part(Predicate)", "Direct Object-Part(Predicate)", ((lambda: (isDependency and ((variables["Type"]== "Part Agreement")))).__code__)),
Value("Subtype", "Indirect Object-Part(Predicate)", "Indirect Object-Part(Predicate)", ((lambda: (isDependency and ((variables["Type"]== "Part Agreement")))).__code__))
)

VariableKeys = ["PoS", "Type", "Head", "Lexical subtype", "Reflexive subtype", "Mode", "Participle subtype", "Participle class", "Proximity", "Tense/Aspect", "Realisation", "Person", "PersonNumber", "Sex", "Subtype", "Position", "Countness", "Hybrid", "Committee", "Animacy", "Human", "Unspecified human subject", "Abstract", "Gender", "Number", "Case", "Default", "IC", "Inflection Subtype", "Stem Alternation", "Contextual", "Gender Contextual", "Number Contextual", "IC Contextual", "Neutralization (phonological)", "Scope", "Focus", "PhraseType", "GrammRel", "Compound Tenses", "Periphrases"]

__all__ = ["Variables", "VariableKeys"]
