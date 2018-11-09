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


def make_gloss_for_token(token):
  # some basic variables
  var = token.variables
  lemma = token.gloss
  variety = token.__db__.document.variety
  starts_with_equal = token.transcription.startswith("=")
  
  
  
  # a helper function that chains a number of variables
  def glossify(*keys):
    return "".join(var.getMnemonicForKey(key)  for key in keys)
  
  # a direct translation from the supplied excel
  # would be nice to have a configurable system, but 
  # I am very short on time, so its just some dumb code
  # 1. OTHER POS 
  if var["PoS"] == "Noun" and var["Type"] == "common":
    if variety == "Ripatransone":
      return u"%s%s%s" % (lemma, var.getMnemonicForKey("Gender", "(", ")"), glossify("Contextual gender", "Number"))
    else:
      return u"%s%s%s" % (lemma, var.getMnemonicForKey("Gender", "(", ")"), var.getMnemonicForKey("Number"))
  
  if var["PoS"] == "Noun" and var["Type"] == "proper":
    return u"%s%s" % (lemma, var.getMnemonicForKey("Gender", "(", ")"))
    
  if var["PoS"] == "Adjective":
    return u"%s%s" % (lemma, glossify("Gender",  "Number"))
    
  if var["PoS"] == "Adverb":
    return u"%s%s" % (lemma, glossify("Gender",  "Number"))
  
  if var["PoS"] == "Quantifier":
    return u"%s%s" % (lemma, glossify("Gender",  "Number"))
    
  # if var["PoS"] == "Preposition":
  #   if variety == "Ripatransone":
  #     return u"%s%s" % (lemma, glossify("Gender",  "Number"))
  #   else:
  #     return u"%s" % (lemma,)
    
  if var["PoS"] == "Interjection":
    return u"INTERJ"
    
  if var["PoS"] == "Numeral":
    return u"%s%s" % (lemma, glossify("Gender",  "Number"))
  
  if var["PoS"] == "Conjunction":
    if variety == "Ripatransone":
      return u"%s%s" % (lemma, glossify("Gender",  "Number"))
    else:
      return u"%s" % (lemma,)

  if var["PoS"] == "Negation":
    return u"NEG"
    
  # 2.  POS determiner
  if var["PoS"] == "Determiner" and var["Type"] == "article" and var["Subtype"] == "definite":
     return u"DEF%s" % (glossify("Gender",  "Number"),)
  if var["PoS"] == "Determiner" and var["Type"] == "article" and var["Subtype"] == "indefinite":
     return u"INDF%s" % (glossify("Gender",  "Number"),)
  if var["PoS"] == "Determiner" and var["Type"] == "possessive":
     return u"POSS%s%s%s" % (glossify("Person"), var.getMnemonicForKey("PersonNumber", "", ""), glossify("Gender",  "Number"))
  if var["PoS"] == "Determiner" and var["Type"] == "demonstrative":
     return u"DEM%s" % (glossify("Proximity", "Gender",  "Number"))

  
  # 3. PoS Pronoun
  if var["PoS"] == "Pronoun" and var["Type"] == "personal" and var["Realisation"] == "overt" and var["Person"] == "3rd": 
    return u"%s%s%s" % (var.getMnemonicForKey("Person", "", ""), var.getMnemonicForKey("Gender", "", ""), var.getMnemonicForKey("Number"))
  if var["PoS"] == "Pronoun" and var["Type"] == "personal" and var["Realisation"] == "overt" and var["Person"] == "1st": 
    return u"%s%s" % (var.getMnemonicForKey("Person", "", ""), var.getMnemonicForKey("Number", "", ""))
  if var["PoS"] == "Pronoun" and var["Type"] == "personal" and var["Realisation"] == "overt" and var["Person"] == "2nd": 
    return u"%s%s" % (var.getMnemonicForKey("Person", "", ""), var.getMnemonicForKey("Number", "", ""))


        
  if var["PoS"] == "Pronoun" and var["Type"] == "personal" and var["Realisation"] == "clitic" and var["Case"] == "Subject" and (not starts_with_equal): 
    return u"SBJ%s%s%s=" % (var.getMnemonicForKey("Person", "", ""), var.getMnemonicForKey("Gender", "", ""), var.getMnemonicForKey("Number"))
  if var["PoS"] == "Pronoun" and var["Type"] == "personal" and var["Realisation"] == "clitic" and var["Case"] == "Direct object" and (not starts_with_equal): 
    return u"DO%s%s%s=" % (var.getMnemonicForKey("Person", "", ""), var.getMnemonicForKey("Gender", "", ""), var.getMnemonicForKey("Number"))  
  if var["PoS"] == "Pronoun" and var["Type"] == "personal" and var["Realisation"] == "clitic" and var["Case"] == "Subject" and starts_with_equal: 
    return u"=SBJ%s%s%s" % (var.getMnemonicForKey("Person", "", ""), var.getMnemonicForKey("Gender", "", ""), var.getMnemonicForKey("Number"))
  if var["PoS"] == "Pronoun" and var["Type"] == "personal" and var["Realisation"] == "clitic" and var["Case"] == "Direct object" and starts_with_equal: 
    return u"=DO%s%s%s" % (var.getMnemonicForKey("Person", "", ""), var.getMnemonicForKey("Gender", "", ""), var.getMnemonicForKey("Number"))
  if var["PoS"] == "Pronoun" and var["Type"] == "personal" and var["Realisation"] == "clitic" and var["Case"] == "Indirect object" and (not starts_with_equal): 
    return u"IO%s%s%s=" % (var.getMnemonicForKey("Person", "", ""), var.getMnemonicForKey("Gender", "", ""), var.getMnemonicForKey("Number"))  
  if var["PoS"] == "Pronoun" and var["Type"] == "personal" and var["Realisation"] == "clitic" and var["Case"] == "Indirect object" and starts_with_equal: 
    return u"=IO%s%s%s" % (var.getMnemonicForKey("Person", "", ""), var.getMnemonicForKey("Gender", "", ""), var.getMnemonicForKey("Number"))
  if var["PoS"] == "Pronoun" and var["Type"] == "personal" and var["Realisation"] == "clitic" and var["Case"] == "DO+IO" and (not starts_with_equal): 
    return u"DO+IO%s%s%s=" % (var.getMnemonicForKey("Person", "", ""), var.getMnemonicForKey("Gender", "", ""), var.getMnemonicForKey("Number"))  
  if var["PoS"] == "Pronoun" and var["Type"] == "personal" and var["Realisation"] == "clitic" and var["Case"] == "DO+IO" and starts_with_equal: 
    return u"=DO+IO%s%s%s" % (var.getMnemonicForKey("Person", "", ""), var.getMnemonicForKey("Gender", "", ""), var.getMnemonicForKey("Number"))
    
  # end of clitic nonsence
  if var["PoS"] == "Pronoun" and var["Type"] == "personal" and var["Realisation"] == "non overt": 
    return u"%s%s%s" % (var.getMnemonicForKey("Person", "", ""), var.getMnemonicForKey("Gender", "", ""), var.getMnemonicForKey("Number"))

  if var["PoS"] == "Pronoun" and var["Type"] == "demonstrative": 
    return u"DEM%s" % (glossify("Proximity", "Gender"),)

  if var["PoS"] == "Pronoun" and var["Type"] == "reciprocal": 
    return u"%s%s" % (lemma, glossify("Gender", "Number"))
  
  if var["PoS"] == "Pronoun" and var["Type"] == "indefinite": 
    return u"%s%s" % (lemma, glossify("Gender", "Number"))

  if var["PoS"] == "Pronoun" and var["Type"] == "interrogative": 
    return u"%s%s" % (lemma, glossify("Gender", "Number")) # added this

  if var["PoS"] == "Pronoun" and var["Type"] == "relative": 
    return u"REL"

  if var["PoS"] == "Pronoun" and var["Type"] == "reflexive" and starts_with_equal: 
    return u"=REFL%s%s" % (var.getMnemonicForKey("Person"), var.getMnemonicForKey("Number", "", ""))
  if var["PoS"] == "Pronoun" and var["Type"] == "reflexive" and (not starts_with_equal): 
    return u"REFL%s%s=" % (var.getMnemonicForKey("Person"), var.getMnemonicForKey("Number", "", ""))


  if var["PoS"] == "Pronoun" and var["Type"] == "impersonal" and var["Realisation"] == "clitic" and starts_with_equal: 
    return u"=IMPRS"
  if var["PoS"] == "Pronoun" and var["Type"] == "impersonal" and var["Realisation"] == "clitic" and (not starts_with_equal): 
    return u"IMPRS="
  if var["PoS"] == "Pronoun" and var["Type"] == "impersonal":
    return u"IMPRS%s%s%s" % (var.getMnemonicForKey("Person", "", ""), var.getMnemonicForKey("Gender", "", ""), var.getMnemonicForKey("Number"))

  if var["PoS"] == "Pronoun" and var["Type"] == "genitive/partitive (It. ne)" and starts_with_equal: 
    return u"=PARTTV"
  if var["PoS"] == "Pronoun" and var["Type"] == "genitive/partitive (It. ne)" and (not starts_with_equal): 
    return u"PARTTV="

  if var["PoS"] == "Pronoun" and var["Type"] == "locative/existential (It. ci)" and starts_with_equal: 
    #return u"=LOC"
    return u"=LOC%s" % (glossify("Gender", "Number"),) # added this
    
  if var["PoS"] == "Pronoun" and var["Type"] == "locative/existential (It. ci)" and (not starts_with_equal): 
    return u"LOC="
    
    

    
  # Dummy
  if var["PoS"] == "Dummy":
    return u"Dummy%s%s%s" % (var.getMnemonicForKey("Person"), var.getMnemonicForKey("Gender", "", ""), var.getMnemonicForKey("Number"))
    
    
  # PoS Verb (oh horror)
  if variety != "Ripatransone" and var["PoS"] == "Verb":
    if var["Type"] == "lexical" and var["Mode"] == "indicative":
      return u"%s%s%s%s" % (lemma, glossify("Tense/Aspect"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Number", "", ""))

    if var["Type"] == "lexical" and var["Mode"] == "subjunctive":
      return u"%s%s%s%s" % (lemma, glossify("Tense/Aspect", "Mode"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Number", "", ""))

    if var["Type"] == "lexical" and var["Mode"] == "conditional":
      return u"%s%s%s%s" % (lemma, glossify("Tense/Aspect", "Mode"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Number", "", ""))

    if var["Type"] == "lexical" and var["Mode"] == "imperative":
      return u"%s%s%s%s" % (lemma, glossify("Mode"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Number", "", ""))
    
    if var["Type"] == "lexical" and var["Mode"] == "infinitive":
      return u"%s%s" % (lemma, glossify("Mode"))

    if var["Type"] == "lexical" and var["Mode"] == "gerund":
      return u"%s%s" % (lemma, glossify("Mode"))

    # have
    if var["Type"] == "auxiliary HAVE" and var["Mode"] == "indicative":
      return u"%s%s%s%s" % ("have", glossify("Tense/Aspect"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Number", "", ""))

    if var["Type"] == "auxiliary HAVE" and var["Mode"] == "subjunctive":
      return u"%s%s%s%s" % ("have", glossify("Tense/Aspect", "Mode"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Number", "", ""))

    if var["Type"] == "auxiliary HAVE" and var["Mode"] == "conditional":
      return u"%s%s%s%s" % ("have", glossify("Tense/Aspect", "Mode"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Number", "", ""))

    if var["Type"] == "auxiliary HAVE" and var["Mode"] == "imperative":
      return u"%s%s%s%s" % ("have", glossify("Mode"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Number", "", ""))
    
    if var["Type"] == "auxiliary HAVE" and var["Mode"] == "infinitive":
      return u"%s%s" % ("have", glossify("Mode"))

    if var["Type"] == "auxiliary HAVE" and var["Mode"] == "gerund":
      return u"%s%s" % ("have", glossify("Mode"))

    # BE
    if var["Type"] == "auxiliary BE" and var["Mode"] == "indicative":
      return u"%s%s%s%s" % ("be", glossify("Tense/Aspect"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Number", "", ""))

    if var["Type"] == "auxiliary BE" and var["Mode"] == "subjunctive":
      return u"%s%s%s%s" % ("be", glossify("Tense/Aspect", "Mode"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Number", "", ""))

    if var["Type"] == "auxiliary BE" and var["Mode"] == "conditional":
      return u"%s%s%s%s" % ("be", glossify("Tense/Aspect", "Mode"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Number", "", ""))

    if var["Type"] == "auxiliary BE" and var["Mode"] == "imperative":
      return u"%s%s%s%s" % ("be", glossify("Mode"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Number", "", ""))
    
    if var["Type"] == "auxiliary BE" and var["Mode"] == "infinitive":
      return u"%s%s" % ("be", glossify("Mode"))

    if var["Type"] == "auxiliary BE" and var["Mode"] == "gerund":
      return u"%s%s" % ("be", glossify("Mode"))

    # venire
    if var["Type"] == "auxiliary venire" and var["Mode"] == "indicative":
      return u"%s%s%s%s" % ("come", glossify("Tense/Aspect"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Number", "", ""))

    if var["Type"] == "auxiliary venire" and var["Mode"] == "subjunctive":
      return u"%s%s%s%s" % ("come", glossify("Tense/Aspect", "Mode"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Number", "", ""))

    if var["Type"] == "auxiliary venire" and var["Mode"] == "conditional":
      return u"%s%s%s%s" % ("come", glossify("Tense/Aspect", "Mode"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Number", "", ""))

    if var["Type"] == "auxiliary venire" and var["Mode"] == "imperative":
      return u"%s%s%s%s" % ("come", glossify("Mode"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Number", "", ""))
    
    if var["Type"] == "auxiliary venire" and var["Mode"] == "infinitive":
      return u"%s%s" % ("come", glossify("Mode"))

    if var["Type"] == "auxiliary venire" and var["Mode"] == "gerund":
      return u"%s%s" % ("come", glossify("Mode"))

    # stare
    if var["Type"] == "auxiliary stare" and var["Mode"] == "indicative":
      return u"%s%s%s%s" % ("stay", glossify("Tense/Aspect"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Number", "", ""))

    if var["Type"] == "auxiliary stare" and var["Mode"] == "subjunctive":
      return u"%s%s%s%s" % ("stay", glossify("Tense/Aspect", "Mode"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Number", "", ""))

    if var["Type"] == "auxiliary stare" and var["Mode"] == "conditional":
      return u"%s%s%s%s" % ("stay", glossify("Tense/Aspect", "Mode"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Number", "", ""))

    if var["Type"] == "auxiliary stare" and var["Mode"] == "imperative":
      return u"%s%s%s%s" % ("stay", glossify("Mode"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Number", "", ""))
    
    if var["Type"] == "auxiliary stare" and var["Mode"] == "infinitive":
      return u"%s%s" % ("stay", glossify("Mode"))

    if var["Type"] == "auxiliary stare" and var["Mode"] == "gerund":
      return u"%s%s" % ("stay", glossify("Mode"))
  
    # modals
    if var["Type"] == "modal" and var["Mode"] == "indicative":
      return u"%s%s%s%s" % (lemma, glossify("Tense/Aspect"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Number", "", ""))

    if var["Type"] == "modal" and var["Mode"] == "subjunctive":
      return u"%s%s%s%s" % (lemma, glossify("Tense/Aspect", "Mode"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Number", "", ""))

    if var["Type"] == "modal" and var["Mode"] == "conditional":
      return u"%s%s%s%s" % (lemma, glossify("Tense/Aspect", "Mode"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Number", "", ""))

    if var["Type"] == "modal" and var["Mode"] == "imperative":
      return u"%s%s%s%s" % (lemma, glossify("Mode"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Number", "", ""))
  
    if var["Type"] == "modal" and var["Mode"] == "infinitive":
      return u"%s%s" % (lemma, glossify("Mode"))

    if var["Type"] == "modal" and var["Mode"] == "gerund":
      return u"%s%s" % (lemma, glossify("Mode"))
    
    # causative
    if var["Type"] == "causative" and var["Mode"] == "indicative":
      return u"%s%s%s%s" % (lemma, glossify("Tense/Aspect"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Number", "", ""))

    if var["Type"] == "causative" and var["Mode"] == "subjunctive":
      return u"%s%s%s%s" % (lemma, glossify("Tense/Aspect", "Mode"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Number", "", ""))

    if var["Type"] == "causative" and var["Mode"] == "conditional":
      return u"%s%s%s%s" % (lemma, glossify("Tense/Aspect", "Mode"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Number", "", ""))

    if var["Type"] == "causative" and var["Mode"] == "imperative":
      return u"%s%s%s%s" % (lemma, glossify("Mode"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Number", "", ""))
  
    if var["Type"] == "causative" and var["Mode"] == "infinitive":
      return u"%s%s" % (lemma, glossify("Mode"))

    if var["Type"] == "causative" and var["Mode"] == "gerund":
      return u"%s%s" % (lemma, glossify("Mode"))
    
    # support verb
    if var["Type"] == "support verb" and var["Mode"] == "indicative":
      return u"%s%s%s%s" % (lemma, glossify("Tense/Aspect"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Number", "", ""))

    if var["Type"] == "support verb" and var["Mode"] == "subjunctive":
      return u"%s%s%s%s" % (lemma, glossify("Tense/Aspect", "Mode"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Number", "", ""))

    if var["Type"] == "support verb" and var["Mode"] == "conditional":
      return u"%s%s%s%s" % (lemma, glossify("Tense/Aspect", "Mode"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Number", "", ""))

    if var["Type"] == "support verb" and var["Mode"] == "imperative":
      return u"%s%s%s%s" % (lemma, glossify("Mode"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Number", "", ""))
  
    if var["Type"] == "support verb" and var["Mode"] == "infinitive":
      return u"%s%s" % (lemma, glossify("Mode"))

    if var["Type"] == "support verb" and var["Mode"] == "gerund":
      return u"%s%s" % (lemma, glossify("Mode"))
  
    # copular verb
    if var["Type"] == "copular verb" and var["Mode"] == "indicative":
      return u"%s%s%s%s" % (lemma, glossify("Tense/Aspect"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Number", "", ""))

    if var["Type"] == "copular verb" and var["Mode"] == "subjunctive":
      return u"%s%s%s%s" % (lemma, glossify("Tense/Aspect", "Mode"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Number", "", ""))

    if var["Type"] == "copular verb" and var["Mode"] == "conditional":
      return u"%s%s%s%s" % (lemma, glossify("Tense/Aspect", "Mode"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Number", "", ""))

    if var["Type"] == "copular verb" and var["Mode"] == "imperative":
      return u"%s%s%s%s" % (lemma, glossify("Mode"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Number", "", ""))
  
    if var["Type"] == "copular verb" and var["Mode"] == "infinitive":
      return u"%s%s" % (lemma, glossify("Mode"))

    if var["Type"] == "copular verb" and var["Mode"] == "gerund":
      return u"%s%s" % (lemma, glossify("Mode"))
   
    # existential
    if var["Type"] == "existential" and var["Mode"] == "indicative":
      return u"%s%s%s%s" % (lemma, glossify("Tense/Aspect"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Number", "", ""))

    if var["Type"] == "existential" and var["Mode"] == "subjunctive":
      return u"%s%s%s%s" % (lemma, glossify("Tense/Aspect", "Mode"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Number", "", ""))

    if var["Type"] == "existential" and var["Mode"] == "conditional":
      return u"%s%s%s%s" % (lemma, glossify("Tense/Aspect", "Mode"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Number", "", ""))

    if var["Type"] == "existential" and var["Mode"] == "imperative":
      return u"%s%s%s%s" % (lemma, glossify("Mode"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Number", "", ""))
  
    if var["Type"] == "existential" and var["Mode"] == "infinitive":
      return u"%s%s" % (lemma, glossify("Mode"))

    if var["Type"] == "existential" and var["Mode"] == "gerund":
      return u"%s%s" % (lemma, glossify("Mode"))

  	# past participles
    if var["Type"] == "lexical" and var["Mode"] == "participle":
      return u"%s.PTP%s" % (lemma, glossify("Gender", "Number"))

    if var["Type"] == "auxiliary HAVE" and var["Mode"] == "participle":
      return u"%s.PTP%s" % ("have", glossify("Gender", "Number"))

    if var["Type"] == "auxiliary BE" and var["Mode"] == "participle":
      return u"%s.PTP%s" % ("be", glossify("Gender", "Number"))
      
    if var["Type"] == "auxiliary stare" and var["Mode"] == "participle":
      return u"%s.PTP%s" % ("stay", glossify("Gender", "Number"))

    if var["Type"] == "auxiliary venire" and var["Mode"] == "participle":
      return u"%s.PTP%s" % ("come", glossify("Gender", "Number"))
      
    if var["Type"] == "modal" and var["Mode"] == "participle":
      return u"%s.PTP%s" % (lemma, glossify("Gender", "Number"))

    if var["Type"] == "causative" and var["Mode"] == "participle":
      return u"%s.PTP%s" % (lemma, glossify("Gender", "Number"))

    if var["Type"] == "support verb" and var["Mode"] == "participle":
      return u"%s.PTP%s" % (lemma, glossify("Gender", "Number"))

    if var["Type"] == "copular verb" and var["Mode"] == "participle":
      return u"%s.PTP%s" % (lemma, glossify("Gender", "Number"))

    if var["Type"] == "existential" and var["Mode"] == "participle":
      return u"%s.PTP%s" % (lemma, glossify("Gender", "Number"))
      
  if variety == "Ripatransone" and var["PoS"] == "Verb":
    if var["Type"] == "lexical" and var["Mode"] == "indicative":
      pg = u"%s%s" % (var.getMnemonicForKey("Person", "", ""), var.getMnemonicForKey("Gender", "", ""))
      if pg != "": 
        pg = u".%s" % (pg,)
      return u"%s%s%s%s" % (lemma, glossify("Tense/Aspect"), pg, glossify("Number"))

    if var["Type"] == "lexical" and var["Mode"] == "subjunctive":
      return u"%s%s%s%s%s" % (lemma, glossify("Tense/Aspect", "Mode"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Gender", "", ""), glossify("Number"))

    if var["Type"] == "lexical" and var["Mode"] == "conditional":
      return u"%s%s%s%s%s" % (lemma, glossify("Tense/Aspect",  "Mode"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Gender", "", ""), glossify("Number"))

    if var["Type"] == "lexical" and var["Mode"] == "imperative":
      return u"%s%s%s%s%s" % (lemma, glossify("Mode"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Gender", "", ""), glossify("Number"))
    
    if var["Type"] == "lexical" and var["Mode"] == "infinitive":
      return u"%s%s%s%s" % (lemma, glossify("Mode"), var.getMnemonicForKey("Gender"), glossify("Number"))

    if var["Type"] == "lexical" and var["Mode"] == "gerund":
      return u"%s%s%s%s" % (lemma, glossify("Mode"), var.getMnemonicForKey("Gender"), glossify("Number"))

    # auxiliary HAVE
    if var["Type"] == "auxiliary HAVE" and var["Mode"] == "indicative":
      return u"%s%s%s%s%s" % ("have", glossify("Tense/Aspect"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Gender", "", ""), glossify("Number"))

    if var["Type"] == "auxiliary HAVE" and var["Mode"] == "subjunctive":
      return u"%s%s%s%s%s" % ("have", glossify("Tense/Aspect", "Mode"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Gender", "", ""), glossify("Number"))

    if var["Type"] == "auxiliary HAVE" and var["Mode"] == "conditional":
      return u"%s%s%s%s%s" % ("have", glossify("Tense/Aspect",  "Mode"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Gender", "", ""), glossify("Number"))

    if var["Type"] == "auxiliary HAVE" and var["Mode"] == "imperative":
      return u"%s%s%s%s%s" % ("have", glossify("Mode"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Gender", "", ""), glossify("Number"))
    
    if var["Type"] == "auxiliary HAVE" and var["Mode"] == "infinitive":
      return u"%s%s" % ("have", glossify("Mode"))

    if var["Type"] == "auxiliary HAVE" and var["Mode"] == "gerund":
      return u"%s%s" % ("have", glossify("Mode"))

    # auxiliary BE
    if var["Type"] == "auxiliary BE" and var["Mode"] == "indicative":
      return u"%s%s%s%s%s" % ("be", glossify("Tense/Aspect"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Gender", "", ""), glossify("Number"))

    if var["Type"] == "auxiliary BE" and var["Mode"] == "subjunctive":
      return u"%s%s%s%s%s" % ("be", glossify("Tense/Aspect", "Mode"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Gender", "", ""), glossify("Number"))

    if var["Type"] == "auxiliary BE" and var["Mode"] == "conditional":
      return u"%s%s%s%s%s" % ("be", glossify("Tense/Aspect",  "Mode"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Gender", "", ""), glossify("Number"))

    if var["Type"] == "auxiliary BE" and var["Mode"] == "imperative":
      return u"%s%s%s%s%s" % ("be", glossify("Mode"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Gender", "", ""), glossify("Number"))
    
    if var["Type"] == "auxiliary BE" and var["Mode"] == "infinitive":
      return u"%s%s" % ("be", glossify("Mode"))

    if var["Type"] == "auxiliary BE" and var["Mode"] == "gerund":
      return u"%s%s%s%s" % ("be", glossify("Mode"), var.getMnemonicForKey("Gender", "", ""), glossify("Number"))
    
    # VENIRE
    if var["Type"] == "auxiliary venire" and var["Mode"] == "indicative":
      return u"%s%s%s%s%s" % ("come", glossify("Tense/Aspect"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Gender", "", ""), glossify("Number"))

    if var["Type"] == "auxiliary venire" and var["Mode"] == "subjunctive":
      return u"%s%s%s%s%s" % ("come", glossify("Tense/Aspect", "Mode"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Gender", "", ""), glossify("Number"))

    if var["Type"] == "auxiliary venire" and var["Mode"] == "conditional":
      return u"%s%s%s%s%s" % ("come", glossify("Tense/Aspect",  "Mode"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Gender", "", ""), glossify("Number"))

    if var["Type"] == "auxiliary venire" and var["Mode"] == "imperative":
      return u"%s%s%s%s%s" % ("come", glossify("Mode"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Gender", "", ""), glossify("Number"))
    
    if var["Type"] == "auxiliary venire" and var["Mode"] == "infinitive":
      return u"%s%s" % ("come", glossify("Mode"))

    if var["Type"] == "auxiliary venire" and var["Mode"] == "gerund":
      return u"%s%s%s%s" % ("come", glossify("Mode"), var.getMnemonicForKey("Gender", "", ""), glossify("Number"))
    
    # STARE
    if var["Type"] == "auxiliary stare" and var["Mode"] == "indicative":
      return u"%s%s%s%s%s" % ("stare", glossify("Tense/Aspect"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Gender", "", ""), glossify("Number"))

    if var["Type"] == "auxiliary stare" and var["Mode"] == "subjunctive":
      return u"%s%s%s%s%s" % ("stare", glossify("Tense/Aspect", "Mode"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Gender", "", ""), glossify("Number"))

    if var["Type"] == "auxiliary stare" and var["Mode"] == "conditional":
      return u"%s%s%s%s%s" % ("stare", glossify("Tense/Aspect",  "Mode"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Gender", "", ""), glossify("Number"))

    if var["Type"] == "auxiliary stare" and var["Mode"] == "imperative":
      return u"%s%s%s%s%s" % ("stare", glossify("Mode"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Gender", "", ""), glossify("Number"))
    
    if var["Type"] == "auxiliary stare" and var["Mode"] == "infinitive":
      return u"%s%s" % ("stare", glossify("Mode"))

    if var["Type"] == "auxiliary stare" and var["Mode"] == "gerund":
      return u"%s%s%s%s" % ("stare", glossify("Mode"), var.getMnemonicForKey("Gender", "", ""), glossify("Number"))
    
    # modal
    if var["Type"] == "modal" and var["Mode"] == "indicative":
      return u"%s%s%s%s%s" % (lemma, glossify("Tense/Aspect"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Gender", "", ""), glossify("Number"))

    if var["Type"] == "modal" and var["Mode"] == "subjunctive":
      return u"%s%s%s%s%s" % (lemma, glossify("Tense/Aspect", "Mode"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Gender", "", ""), glossify("Number"))

    if var["Type"] == "modal" and var["Mode"] == "conditional":
      return u"%s%s%s%s%s" % (lemma, glossify("Tense/Aspect",  "Mode"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Gender", "", ""), glossify("Number"))

    if var["Type"] == "modal" and var["Mode"] == "imperative":
      return u"%s%s%s%s%s" % (lemma, glossify("Mode"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Gender", "", ""), glossify("Number"))
    
    if var["Type"] == "modal" and var["Mode"] == "infinitive":
      return u"%s%s" % (lemma, glossify("Mode"))

    if var["Type"] == "modal" and var["Mode"] == "gerund":
      return u"%s%s%s%s" % (lemma, glossify("Mode"), var.getMnemonicForKey("Gender", "", ""), glossify("Number"))

    # causative
    if var["Type"] == "causative" and var["Mode"] == "indicative":
      return u"%s%s%s%s%s" % (lemma, glossify("Tense/Aspect"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Gender", "", ""), glossify("Number"))

    if var["Type"] == "causative" and var["Mode"] == "subjunctive":
      return u"%s%s%s%s%s" % (lemma, glossify("Tense/Aspect", "Mode"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Gender", "", ""), glossify("Number"))

    if var["Type"] == "causative" and var["Mode"] == "conditional":
      return u"%s%s%s%s%s" % (lemma, glossify("Tense/Aspect",  "Mode"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Gender", "", ""), glossify("Number"))

    if var["Type"] == "causative" and var["Mode"] == "imperative":
      return u"%s%s%s%s%s" % (lemma, glossify("Mode"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Gender", "", ""), glossify("Number"))
    
    if var["Type"] == "causative" and var["Mode"] == "infinitive":
      return u"%s%s" % (lemma, glossify("Mode"))

    if var["Type"] == "causative" and var["Mode"] == "gerund":
      return u"%s%s%s%s" % (lemma, glossify("Mode"), var.getMnemonicForKey("Gender", "", ""), glossify("Number"))

    # support verb
    if var["Type"] == "support verb" and var["Mode"] == "indicative":
      return u"%s%s%s%s%s" % (lemma, glossify("Tense/Aspect"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Gender", "", ""), glossify("Number"))

    if var["Type"] == "support verb" and var["Mode"] == "subjunctive":
      return u"%s%s%s%s%s" % (lemma, glossify("Tense/Aspect", "Mode"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Gender", "", ""), glossify("Number"))

    if var["Type"] == "support verb" and var["Mode"] == "conditional":
      return u"%s%s%s%s%s" % (lemma, glossify("Tense/Aspect",  "Mode"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Gender", "", ""), glossify("Number"))

    if var["Type"] == "support verb" and var["Mode"] == "imperative":
      return u"%s%s%s%s%s" % (lemma, glossify("Mode"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Gender", "", ""), glossify("Number"))
    
    if var["Type"] == "support verb" and var["Mode"] == "infinitive":
      return u"%s%s" % (lemma, glossify("Mode"))

    if var["Type"] == "support verb" and var["Mode"] == "gerund":
      return u"%s%s%s%s" % (lemma, glossify("Mode"), var.getMnemonicForKey("Gender", "", ""), glossify("Number"))
    
    # copular verb
    if var["Type"] == "copular verb" and var["Mode"] == "indicative":
      return u"%s%s%s%s%s" % (lemma, glossify("Tense/Aspect"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Gender", "", ""), glossify("Number"))

    if var["Type"] == "copular verb" and var["Mode"] == "subjunctive":
      return u"%s%s%s%s%s" % (lemma, glossify("Tense/Aspect", "Mode"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Gender", "", ""), glossify("Number"))

    if var["Type"] == "copular verb" and var["Mode"] == "conditional":
      return u"%s%s%s%s%s" % (lemma, glossify("Tense/Aspect",  "Mode"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Gender", "", ""), glossify("Number"))

    if var["Type"] == "copular verb" and var["Mode"] == "imperative":
      return u"%s%s%s%s" % (lemma, glossify("Mode"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Number", "", ""))
    
    if var["Type"] == "copular verb" and var["Mode"] == "infinitive":
      return u"%s%s" % (lemma, glossify("Mode"))

    if var["Type"] == "copular verb" and var["Mode"] == "gerund":
      return u"%s%s" % (lemma, glossify("Mode"))

    # existential
    if var["Type"] == "existential" and var["Mode"] == "indicative":
      return u"%s%s%s%s%s" % (lemma, glossify("Tense/Aspect"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Gender", "", ""), glossify("Number"))

    if var["Type"] == "existential" and var["Mode"] == "subjunctive":
      return u"%s%s%s%s%s" % (lemma, glossify("Tense/Aspect", "Mode"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Gender", "", ""), glossify("Number"))

    if var["Type"] == "existential" and var["Mode"] == "conditional":
      return u"%s%s%s%s%s" % (lemma, glossify("Tense/Aspect",  "Mode"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Gender", "", ""), glossify("Number"))

    if var["Type"] == "existential" and var["Mode"] == "imperative":
      return u"%s%s%s%s%s" % (lemma, glossify("Mode"), var.getMnemonicForKey("Person"), var.getMnemonicForKey("Gender", "", ""), glossify("Number"))
    
    if var["Type"] == "existential" and var["Mode"] == "infinitive":
      return u"%s%s" % (lemma, glossify("Mode"))

    if var["Type"] == "existential" and var["Mode"] == "gerund":
      return u"%s%s" % (lemma, glossify("Mode"))
      
    # past participles
    if var["Type"] == "lexical" and var["Mode"] == "participle":
      return u"%s.PTP%s" % (lemma, glossify("Gender", "Number"))
    
    if var["Type"] == "auxiliary HAVE" and var["Mode"] == "participle":
      return u"%s.PTP%s" % ("have", glossify("Gender", "Number"))
    
    if var["Type"] == "auxiliary BE" and var["Mode"] == "participle":
      return u"%s.PTP%s" % ("be", glossify("Gender", "Number"))
      
    if var["Type"] == "auxiliary stare" and var["Mode"] == "participle":
      return u"%s.PTP%s" % ("stay", glossify("Gender", "Number"))
    
    if var["Type"] == "auxiliary venire" and var["Mode"] == "participle":
      return u"%s.PTP%s" % ("come", glossify("Gender", "Number"))
      
    if var["Type"] == "modal" and var["Mode"] == "participle":
      return u"%s.PTP%s" % (lemma, glossify("Gender", "Number"))
    
    if var["Type"] == "causative" and var["Mode"] == "participle":
      return u"%s.PTP%s" % (lemma, glossify("Gender", "Number"))
    
    if var["Type"] == "support verb" and var["Mode"] == "participle":
      return u"%s.PTP%s" % (lemma, glossify("Gender", "Number"))
    
    if var["Type"] == "copular verb" and var["Mode"] == "participle":
      return u"%s.PTP%s" % (lemma, glossify("Gender", "Number"))
    
    if var["Type"] == "existential" and var["Mode"] == "participle":
      return u"%s.PTP%s" % (lemma, glossify("Gender", "Number"))
            
    
      
  return None
