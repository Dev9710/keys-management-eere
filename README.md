# keys-management-eere

A. Demarrer le server : python manage.py runserver

B. Lors de la modification du shema de la base de donnée ( modification du model , ou nouvelle population de la base ) il faut migrer ses modification avec deux commandes : 

  a. python manage.py makemigrations 
  b. python manage.py migrate

C. Importer les données(inserer les données des fichiers excel dans la base de donée et dans les tables associés Django) dans la table :
  a. key : python manage.py import_key repertoire_perso_local\keys-management-eere\merchex\listings\data\keys.xlsx
  b. team : python manage.py import_team repertoire_perso_local\keys-management-eere\merchex\listings\data\teams.xlsx
  c. user : python manage.py import_team_members repertoire_perso_local\keys-management-eere\merchex\listings\data\userbyteams.xlsx

NB :  repertoire_perso_local\keys-management-eere\merchex\listings\data\userbyteams.xlsx correspond au chemin ou se trouve le fichier excel dans le projet.Il faut donc le modofier en fonction du repertoire du  projet de chacun.