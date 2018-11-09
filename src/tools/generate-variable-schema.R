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



library(readxl)
library(dplyr)

options(width=600)

latest <- 'doc/new_variable_format/variables-latest.xlsx'

# read the variables
variables <- read_excel(latest, col_names = T)[, 1:4]

strip <- function(x) gsub('^[[:space:]]+', '', gsub('[[:space:]]+$', '', x))


process_conditions <- function(conditions) {
  conditions <- sapply(unlist(strsplit(conditions, "\n")), strip)
  conditions <- conditions[conditions != ""]
  conditions <- gsub("\\[", "variables[", conditions)
  
  conditions <- sapply(conditions, function(condition) {
    ab <- unlist(strsplit(condition, "#"))
    stopifnot(length(ab) >= 1 && length(ab) <= 2)
    if(length(ab)==1) {
      ab[1]
    } else {
      paste(strip(ab[1]), "and", process_varieties(ab[2]))
    }
  })  
  conditions <- paste("(", conditions, ")", collapse = " or ", sep="")
  
  conditions
}


process_varieties <- function(varieties) {
  varieties <- unique(sapply(unlist(strsplit(varieties, ",")), strip))
  varieties <- paste0('"', varieties, '"', collapse=", ")
  
  paste0("(variety in [", varieties, "])")
}

generate_variables_for_sheet <- function(sheet, constant_condition) {
  variables <- read_excel(latest, sheet = sheet, col_names = T)[, 1:5]
  
  variables <- transmute(variables,
    Sheet = sheet,
    Key=Key,
    Value=Value,
    Mnemonic = ifelse(is.na(Mnemonic), "", Mnemonic),
    Mnemonic = paste0('"', strip(Mnemonic), '"'),
    Variety  = ifelse(is.na(Variety), NA, sapply(Variety, process_varieties)),
    Condition = gsub('[“”„]', '"', strip(Condition)),
    Condition = ifelse(is.na(Condition), "True", Condition),
    Condition = gsub("^(.+)(#.+)?$", "\\1", Condition),
    Condition = sapply(Condition, process_conditions),
    Condition = paste0(constant_condition, " and (", Condition, ")"),
    Condition = ifelse(is.na(Variety), Condition, paste0(Condition, " and ", Variety)),
    Condition = gsub(" and \\(\\(True\\)\\)", "", Condition)
  )
  
  # a <- filter(variables, Key == "Focus", Value == "yes")
  # writeLines(a$Condition)
  
  variables
}


make_variable_order <- function() {
  varorder <- na.omit(read_excel(latest, sheet = "VariableOrder"))
  varorder
}

#
# head(xx)
#
# # check if all things are there
#
#
#
# stop()
#
# make_variable_order <- function() {
#   word_order <- na.omit(read_excel(latest, sheet = "WordTagOrder")[[1]])
#   depednency_order <- na.omit(read_excel(latest, sheet = "Dependencies")[[1]])
#   constituent_order <- na.omit(read_excel(latest, sheet = "Contsituencies")[[1]])
#
#   oo <- c(word_order, depednency_order, constituent_order)
#   oo <- paste0('"', strip(oo), '"')
#
#   unique(oo)
# }



variables <- bind_rows(
    generate_variables_for_sheet("Words", "isToken"),
    generate_variables_for_sheet("Dependencies", "isDependency"),
    generate_variables_for_sheet("Contsituencies", "isConstituent")
)
  
# make sure that all the variables are mentioned only once
variables <- group_by(variables, Sheet, Key, Value, Mnemonic) %>%
  summarize(Condition = paste0("(", Condition, ")", collapse=" or ")) %>%
  ungroup()
  
  
if(any(duplicated(select(variables, Key, Value)))) {
  X <- select(variables, Key, Value)
  print(X[duplicated(X), ] %>% unique())
  
  stop("have duplicated vars")
}
  
variables$PythonLambda <- paste0('((lambda: ', variables$Condition, ').__code__)')


gen_js_function <- function(conditions) {
  #conditions <- sapply(unlist(strsplit(conditions, "or")), strip)
  
  # remove all the variety conditions
  #writeLines(conditions)
    
  conditions <- gsub(" and \\(variety in \\[[^]]+\\]\\)", "", conditions)
  
  # cat("-----\n")
  #
  # writeLines(conditions)
  
  #stop()
  
  conditions <- conditions[conditions != ""]
  conditions <- gsub("\\<and\\>", " && ", conditions)
  conditions <- gsub("\\<or\\>", " || ", conditions)
  #conditions <- paste("(", conditions, ")", collapse = " || ")
  
  #conditions <- paste(conditions, collapse = " || ")
  
  conditions <- gsub("isToken", "true", conditions)
  conditions <- gsub("isConstituent", "true", conditions)
  conditions <- gsub("isDependency", "true", conditions)
  
  paste0("function(variables) { return ", conditions, "; }")
}

# xx <- filter(variables, Key == "Neutralization (phonological)")
#
# a <- gen_js_function(xx$Condition[1])
#
# writeLines(a)
#
# stop()


variables$JSLambda <- sapply(variables$Condition, gen_js_function)

# order the varibles
order <- make_variable_order()

variables <- local({
  order_keyvals <- paste(order$Key, order$Value, sep="\t")
  vars_keyval <- paste(variables$Key, variables$Value, sep="\t")
  
  if(!setequal(order_keyvals, vars_keyval)) {
    cat("Missing key-values in the order data:\n")
    for(e in setdiff(vars_keyval, order_keyvals)) {
      cat("  - ", e, "\n", sep="")
    }
    cat("Extra key-values in the order data:\n")
    for(e in setdiff(order_keyvals, vars_keyval)) {
      cat("  - ", e, "\n", sep="")
    }
    stop()
  }
  
  
  variables[match(order_keyvals, vars_keyval), ]
})

variables <- mutate(variables, 
  Condition = gsub("\r", "", Condition)
)



# Python variable model

# transform them into variable declaractions
varDecl <- paste0('Value("', variables$Key, '", "', variables$Value, '", ', variables$Mnemonic, ', ', variables$PythonLambda, ')', collapse=',\n')

allkeys <- unique(variables$Key)


# The template
out <- c(
'# This file is generated automatically',
'# Please do not edit',
'',
'from collections import namedtuple',
'',
'Value = namedtuple("Value", ("key", "value", "mnemonic", "condition"))',
'', 
'',
'Variables = (',
varDecl,
')',
'', 
paste0('VariableKeys = [', paste0('"', unique(variables$Key), '"', collapse=", "), "]"),
'',
'__all__ = ["Variables", "VariableKeys"]', 
'')

writeLines(out)

writeLines(out, 'src/model/variables.py')

# JS variable model
varDecl <- lapply(c("Words", "Dependencies", "Contsituencies"), function(sheet) {
  sheetdata <- filter(variables, Sheet == sheet, Key != "Head")
  
  descriptions <- paste0("    { 'variable':'", sheetdata$Key, "', 'value':'", sheetdata$Value, "', 'is_enabled':", sheetdata$JSLambda, " }")
  descriptions <- paste0(descriptions, ifelse(seq_along(descriptions)<length(descriptions), "," , ""))
  
  c(
    paste0("  '", sheet, "': ["),
    descriptions,
    ifelse(sheet =="Contsituencies", "  ]", "  ],")
  )
}) %>% unlist()

#varDecl <- paste0(varDecl, c(",", ",", ""))

# The template
out <- c(
  '// This file is generated automatically',
  '// Please do not edit',
  'var variable_dictionary  = {',
  varDecl,
  '}'
)

writeLines(out)

writeLines(out, 'src/model/variable_dictionary.js')

