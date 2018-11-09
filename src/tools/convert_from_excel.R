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
library(rjson)
library(dplyr)

convert_questionaire <- function(filename, outfile) {
  # read the file
  data <- as.data.frame(read_excel(filename, col_names = F))[, 1:5]
  
  names(data) <- data[1, ]
  data <- data[-1, , drop=F]
    
  data <- select(data, QuestionID, Type, SpeakerCode, Transcription, Translation)
  data <- data[complete.cases(data), ]
  
  # create subids
  # data <- group_by(data, QuestionID, Type) %>%
  # mutate(
  #   subid = if(n()==1) '' else LETTERS[1:n()]
  # )
  
  # convert the data to list and stuff
  spans = list()
  for(i in 1:nrow(data)) {
    row = data[i, ]
    
    #prepare the span
    span = list()
    
    # extract the tokens
    span$tokens = unlist(strsplit(row$Transcription, '[[:space:]]+'))
    
    # build the spanid
    spaninfo = list()
    spaninfo$id    <- row$QuestionID
    # spaninfo$subid <- row$subid
    spaninfo$speakerCode <- row$SpeakerCode
    spaninfo$type <- row$Type
    spaninfo$translation <- row$Translation
    
    span$spanInfo <- spaninfo
    
    spans[[i]] <- span
  }
  
  # get the variety
  if(grepl('^ALT', basename(filename)))
    variety <- 'Altamura'
  else if(grepl('^PTN', basename(filename)))
    variety <- 'Pantelleria'
  else if(grepl('^VER', basename(filename)))
    variety <- 'Verbicaro'
  else
    variety <- 'Unknown'

  # write a temporaty json file
  data <- list(spans = spans, documentType = 'Questionnaire', variety = variety)  
  writeLines(toJSON(data), '/tmp/tempanno.json')
  
  system(paste0('/Users/tzakharko/Documents/Projects/Loporcaro/virtualenv/bin/pywrapper.sh /Users/tzakharko/Documents/Projects/Loporcaro/Annotator/src/model/build_from_json.py /tmp/tempanno.json "', outfile, '"'))
}

convert_picture_story <- function(filename, outfile) {
  # read the file
  data <- select(read_excel(filename), UtteranceID, SpeakerCode, Transcription, Translation)
  data <- data[complete.cases(data), ]
    
  # convert the data to list and stuff
  spans = list()
  for(i in 1:nrow(data)) {
    row = data[i, ]
    
    #prepare the span
    span = list()
    
    # extract the tokens
    span$tokens = unlist(strsplit(row$Transcription, '[[:space:]]+'))
    
    # build the spanid
    spaninfo = list()
    spaninfo$id    <- row$UtteranceID
    spaninfo$speakerCode <- row$SpeakerCode
    spaninfo$translation <- row$Translation
    
    span$spanInfo <- spaninfo
    
    spans[[i]] <- span
  }
  
  # get the variety
  if(grepl('^ALT', basename(filename)))
    variety <- 'Altamura'
  else if(grepl('^PTN', basename(filename)))
    variety <- 'Pantelleria'
  else
    variety <- 'Unknown'

  # write a temporaty json file
  data <- list(spans = spans, documentType = 'Picture story', variety = variety)  
  writeLines(toJSON(data), '/tmp/tempanno.json')
  
  system(paste0('/Users/tzakharko/Documents/Projects/Loporcaro/virtualenv/bin/pywrapper.sh /Users/tzakharko/Documents/Projects/Loporcaro/Annotator/src/model/build_from_json.py /tmp/tempanno.json "', outfile, '"'))
}


convert_questionaire(
  '/Users/tzakharko/Documents/Projects/Loporcaro/Data Conversion/04.08.2016/VER_KaRu_21_synt_agreement_participle_transcription.xlsx',
  '/Users/tzakharko/Documents/Projects/Loporcaro/Data Conversion/04.08.2016/VER_KaRu_21_synt_agreement_participle_transcription.anno'
)

convert_picture_story(
  '/Users/tzakharko/Documents/Projects/Loporcaro/Data Conversion/04.08.2016/VER_LuTu_71_story_ver_transcription.xlsx',
  '/Users/tzakharko/Documents/Projects/Loporcaro/Data Conversion/04.08.2016/VER_LuTu_71_story_ver_transcription.anno'
)


#
#
# # convert seris of questionaires
# convert_questionaire(
#   '/Users/tzakharko/Documents/Projects/Loporcaro/Source Data/ALT_AnCa_11_morf_gen_gramm_transcription.xlsx',
#   '/Users/tzakharko/Documents/Projects/Loporcaro/Source Data/db/ALT_AnCa_11_morf_gen_gramm_transcription.anno'
# )
#
# convert_questionaire(
#   '/Users/tzakharko/Documents/Projects/Loporcaro/Source Data/ALT_FrBa_21_synt_agremment_transcription.xlsx',
#   '/Users/tzakharko/Documents/Projects/Loporcaro/Source Data/db/ALT_FrBa_21_synt_agremment_transcription.anno'
# )
#
# convert_questionaire(
#   '/Users/tzakharko/Documents/Projects/Loporcaro/Source Data/ALT_ToFa_11_morf_gen_gramm_transcription.xlsx',
#   '/Users/tzakharko/Documents/Projects/Loporcaro/Source Data/db/ALT_ToFa_11_morf_gen_gramm_transcription.anno'
# )
#
# convert_questionaire(
#   '/Users/tzakharko/Documents/Projects/Loporcaro/Source Data/ALT_LiVe_SaLo_MaMo_11_morf_gen_gramm_transcription.xlsx',
#   '/Users/tzakharko/Documents/Projects/Loporcaro/Source Data/db/ALT_LiVe_SaLo_MaMo_11_morf_gen_gramm_transcription.anno'
# )
#
#
# convert_questionaire(
#   '/Users/tzakharko/Documents/Projects/Loporcaro/Source Data/ALT_LoBa_11_morf_gen_gramm_transcription.xlsx',
#   '/Users/tzakharko/Documents/Projects/Loporcaro/Source Data/db/ALT_LoBa_11_morf_gen_gramm_transcription.anno'
# )
#
# convert_questionaire(
#   '/Users/tzakharko/Documents/Projects/Loporcaro/Source Data/VER_LuTu_21_synt_agreement_participle_transcription.xlsx',
#   '/Users/tzakharko/Documents/Projects/Loporcaro/Source Data/db/VER_LuTu_21_synt_agreement_participle_transcription.anno'
# )
#
#
# convert_questionaire(
#   '/Users/tzakharko/Documents/Projects/Loporcaro/Source Data/VER_KaRu_21_synt_agreement_participle_transcription_2505.xlsx',
#   '/Users/tzakharko/Documents/Projects/Loporcaro/Source Data/db/VER_KaRu_21_synt_agreement_participle_transcription_2505.anno'
# )
#
# convert_questionaire(
#   '/Users/tzakharko/Documents/Projects/Loporcaro/Source Data/VER_KaRu_21_synt_agreement_participle_transcription.xlsx',
#   '/Users/tzakharko/Documents/Projects/Loporcaro/Source Data/db/VER_KaRu_21_synt_agreement_participle_transcription.anno'
# )

# convert_questionaire(
#   '/Users/tzakharko/Documents/Projects/Loporcaro/Source Data/VER_GiRu_21_synt_agreement_participle_transcription.xlsx',
#   '/Users/tzakharko/Documents/Projects/Loporcaro/Source Data/db/VER_GiRu_21_synt_agreement_participle_transcription.anno'
# )





# convert_questionaire(
#   '/Users/tzakharko/Documents/Projects/Loporcaro/Source Data/22.06/VER_ErRu_21_synt_agreement_participle_transcription .xlsx',
#   '/Users/tzakharko/Documents/Projects/Loporcaro/Source Data/22.06/VER_ErRu_21_synt_agreement_participle_transcription.anno'
# )
#
# convert_questionaire(
#   '/Users/tzakharko/Documents/Projects/Loporcaro/Source Data/22.06/VER_MFRa_21_synt_agreement_participle_transcription.xlsx',
#   '/Users/tzakharko/Documents/Projects/Loporcaro/Source Data/22.06/VER_MFRa_21_synt_agreement_participle_transcription.anno'
# )
#
# convert_picture_story(
#   '/Users/tzakharko/Documents/Projects/Loporcaro/Source Data/22.06/VER_LuTu_71_story_ver_transcription.xlsx',
#   '/Users/tzakharko/Documents/Projects/Loporcaro/Source Data/22.06/VER_LuTu_71_story_ver_transcription.anno'
# )
#
#
#
#
# stop()
# # convert picture stories
#
# convert_picture_story(
#   '/Users/tzakharko/Documents/Projects/Loporcaro/Source Data/ALT_MaMo_71_picture_story_alt_transcription.xlsx',
#   '/Users/tzakharko/Documents/Projects/Loporcaro/Source Data/db/ALT_MaMo_71_picture_story_alt_transcription.anno'
# )
#
# convert_picture_story(
#   '/Users/tzakharko/Documents/Projects/Loporcaro/Source Data/PNT_ARDA_71_picture_story_pnt_transcription.xlsx',
#   '/Users/tzakharko/Documents/Projects/Loporcaro/Source Data/db/PNT_ARDA_71_picture_story_pnt_transcriptio.anno'
# )
#
# convert_picture_story(
#   '/Users/tzakharko/Documents/Projects/Loporcaro/Source Data/PNT_VeGa_71_picture_story_pnt_transcription.xlsx',
#   '/Users/tzakharko/Documents/Projects/Loporcaro/Source Data/db/PNT_VeGa_71_picture_story_pnt_transcription.anno'
# )
#
#
