# created on the 10th of October 2020 by Adrien Leleu
# updated on the 18th of January 2021 by Adrien Leleu 
# updated on the 19th of February 2021 by Adrien Leleu 
# updated on the 22nd of May 2021 by Adrien Leleu : now using the csv from the Notion page
# updated on the 2nd of June by C. Broeg: Now allowing for multiple entries in the ID column. 
#                                         Working with full name instead of surname to allow duplicates of surnames
#                                         fully in line with publication policy: added ESAPA, EO (ex officio), MA (mission architect)
#                                         works with MA nominees in Notion table

import numpy as np
import pandas as pd
import unicodedata
import csv


# Ask C. Broeg for the spreadsheet
# if any bug occurs : adrien.leleu@unige.ch


# Lead Author 
lead_author=['Willy Benz']

# up to 4 Major contributors 
major_contirbutors_list=['Anders Erikson',
                         'Sébastien Charnoz',
                         'Andrea Fortier',
                         'Tom Wilson']


# exactly 4 Science Enablers - rotating from the full list of SE
science_enablers_list=['Attila Simon',
                       'Christopher Broeg',
                       'Hans-Gustav Florén',
                       'Sérgio Sousa'] 
                       
science_enablers_list_full=['Mathias Beck','Anja Bekkelien', 'Willy Benz', 'Nicolas Billot', 'Christopher Broeg', 'Andrew Collier Cameron', 
                            'Adrien Deline', 'David Ehrenreich', 'Hans-Gustav Florén', 
                            'Andrea Fortier', 'David Futyan', 'Pascal Guterman', 'Sergio Hoyer', 'Pierre Maxted', 'Göran Olofsson', 
                            'Didier Queloz', 'Attila Simon', 'Sérgio Sousa']

#significant contributors (max 15%) 
significant_contributors_list=['Valérie Van Grootel',
                               'Vincent Bourrier',
                               'Gwenaël Boué', 
                               'Adrien Leleu',
                               'Alain Lecavelier des Etangs']
                               

# ID to add to all papers
List_of_ID_to_add = ['CST','Associate','Board', 'EO', 'MA', 'ESAPS']

# Additional people to add in the alphabetical order (this example is anyway on the paper)
selected_list=[ 'Alexis Brandeker','Tamas Bárczy','Alexis M. S. Smith'] 

# separate list for people nominated by the mission architects:
MA_nominees = ['Federico Biondi', 'Francesco Ratti', 'G. Polenta']

selected_list.extend(MA_nominees)

# initials : True; Full name : False
flag_initials=True

########################################################################
########################################################################
########################################################################

#initialisation of the lists
first_names=[]
institutes=[]
Family_names=[]
authors_institutes=[]
acknowledgements=["CHEOPS is an ESA mission in partnership with Switzerland with important contributions to the payload and the ground segment "+
                   "from Austria, Belgium, France, Germany, Hungary, Italy, Portugal, Spain, Sweden, and the United Kingdom. "+
                   "The CHEOPS Consortium would like to gratefully acknowledge the support received by all the agencies, offices, "+
                   "universities, and industries involved. Their flexibility and willingness to explore new approaches were essential to the success of this mission."]
institutes_Id=[]


# Non-alphabetical list
authors_nonalpha=[lead_author]
authors_nonalpha.append(major_contirbutors_list)
authors_nonalpha.append(science_enablers_list)
authors_nonalpha.append(significant_contributors_list)

flatten = lambda l: [item for sublist in l for item in sublist]

authors_nonalpha=flatten(authors_nonalpha)



#ensure that all written authors are in the list
selected_list=[selected_list,authors_nonalpha]
selected_list=flatten(selected_list)

#load the spreadsheet
df_list1 = pd.read_csv('CHEOPS_Science_Team_new.csv')

# fix list by changing ID string to list:
for i,a in df_list1.iterrows(): 
    #print (i) 
    df_list1['ID'][i] = df_list1['ID'][i].split(',') 


df_selected=df_list1[df_list1['Ref name'].isin(selected_list)]

#check if all entries were found
for refname in selected_list:
    if df_selected['Ref name'].str.contains(refname).any()==False:
        input('missing '+refname+' in the csv file')

#add all the members of the listed IDs (for exemple : CST, Board, etc.)
#for ID in List_of_ID_to_add:
#    df_selected=df_selected.append(df_list1[df_list1['ID']==ID])

mask = np.zeros(df_list1.shape[0], dtype=bool)    
for id in List_of_ID_to_add: 
     mask2 = [] 
     for i,r in df_list1.iterrows(): 
         mask2.append( id in r['ID']  ) 
     mask = mask | np.array(mask2) 
df_selected = df_selected.append(df_list1[mask])   

#create the list of all authors of the paper
all_authors=df_selected['Ref name'].tolist()

# sort all authors from the spreadsheets in alphabetical order, thanks to P. Maxted!
for ref_name in all_authors:
    name = df_list1[df_list1['Ref name'] == ref_name].Surname.tolist()[0] 
    Family_names.append(name.split('.')[-1])

nfkd = [unicodedata.normalize('NFKD', s) for s in Family_names] 
no_diacrit = [s.encode('ASCII', 'ignore') for s in nfkd]
Id_sort=sorted(range(len(Family_names)), key=lambda k: no_diacrit[k])
all_authors_sorted=[all_authors[i] for i in Id_sort]


# create the author list
authors=authors_nonalpha
for author in all_authors_sorted:
    if author not in authors:
        authors.append(author)

# Return intials of first names 
def get_initials(fullname):
  xs = (fullname)
  name_list = xs.split()

  initials = ""

  for name in name_list:  # go through each name
    comp=name.split('-')
    if len(comp)>1:
        initials += comp[0][0].upper()+'.-'+comp[1][0]+'. '
    else:
        initials += name[0].upper()+'. '  # append the initial

  return initials

for author in authors:
    print('author',author)
    
    
    author_insistutes_f=df_selected[df_selected['Ref name']==author]
    
    
    if flag_initials:
        first_names.append(get_initials(author_insistutes_f.iloc[0]['First Name']))
    else:
        first_names.append(author_insistutes_f.iloc[0]['First Name'])
    
    author_institutes_list=author_insistutes_f.iloc[0]['Adress']
    author_institutes_fnn = author_institutes_list.split(';')
   
    #create the list for the institute indices next to the name
    author_institutes=[]
    for institute in author_institutes_fnn:
        # if the institute is already in the list, add its index next to the author name
        if institute.strip() in institutes: 
            author_institutes.append(institutes.index(institute.strip()))
        #if not, create a new entry in the institute list
        else:
            institutes.append(institute.strip())
            author_institutes.append(institutes.index(institute.strip()))
            
    authors_institutes.append(author_institutes)
    
    #acknowledgments list following the order of the author list
    author_acknow_list=author_insistutes_f.iloc[0]['Acknow']
    
    if str(author_acknow_list) != 'nan' :
        author_acknow_fnn = author_acknow_list.split(';')
        for acknow in author_acknow_fnn:
            if acknow.strip() not in acknowledgements:
                acknowledgements.append(acknow.strip())
               

# get all surnames

surnames = []    
for ref_name in authors:
    name = df_list1[df_list1['Ref name'] == ref_name].Surname.tolist()[0].strip()
    surnames.append(name)
   

 
# write the author list, with the institutes indexes, on a column
outF = open("authors.txt", "w")
for l,line in zip(range(len(authors)),authors):
  line_str=first_names[l]+surnames[l]+"$^{"
  if len(authors_institutes[l])==0:
      line_str+=str(0)+","
  else:
      for k in range(len(authors_institutes[l])):
          line_str+=str(authors_institutes[l][k]+1)+","
  line_str=line_str[:-1]+"}$, "
  outF.writelines(line_str)
  outF.write("\n")

outF.close()


# write the author list, with the institutes indexes, in a line
outF = open("authors_lin.txt", "w")
for l,line in zip(range(len(surnames)),surnames):
  outF.writelines(first_names[l]+line+", ")

outF.close()


# write the institute list
outF = open("institutes.txt", "w")
for l,line in zip(range(len(institutes)),institutes):
  line_str="$^{"+str(l+1)+"}$ "+line.rstrip()+"\\\\"
  outF.writelines(line_str)
  outF.write("\n")

outF.close()


# write the acknowledgement list
outF = open("acknowledgements.txt", "w")
for l,line in zip(range(len(acknowledgements)),acknowledgements):
  toprint=line.rstrip()
  if toprint[-1]=='.':
      outF.writelines(line.rstrip()+" ")
  else:
      outF.writelines(line.rstrip()+". ")
  outF.write("\n")

outF.close()

