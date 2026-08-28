from django.test import TestCase
from django.urls import reverse

from listings.models import Owner, Team, User, KeyType


class VisiteurLectureSeuleTests(TestCase):
    """
    Le visiteur consulte et exporte, rien d'autre.

    Le masquage des boutons n'est qu'un confort d'affichage : ces tests
    verifient le serveur, parce qu'une URL se tape a la main.
    """

    @classmethod
    def setUpTestData(cls):
        cls.visiteur = Owner.objects.create_user(
            username='visiteur', password='motdepasse-test', role='visitor',
            first_name='Vi', last_name='Siteur')
        cls.editeur = Owner.objects.create_user(
            username='editeur', password='motdepasse-test', role='editor',
            first_name='Edi', last_name='Teur')

        cls.equipe = Team.objects.create(name='Accueil')
        cls.membre = User.objects.create(
            name='Dupont', firstname='Marie', team=cls.equipe)
        cls.type_cle = KeyType.objects.create(
            number=1, name='Porte principale', place='Entree',
            total_quantity=2, in_cabinet=2, in_safe=0)

    # ── Ecriture refusee ────────────────────────────────────────────

    def test_visiteur_ne_peut_pas_creer_une_cle(self):
        self.client.login(username='visiteur', password='motdepasse-test')
        avant = KeyType.objects.count()
        reponse = self.client.post(reverse('key_create'), {
            'number': 99, 'name': 'Clé test', 'place': 'Nulle part',
            'total_quantity': 1, 'in_cabinet': 1, 'in_safe': 0,
        })
        self.assertEqual(KeyType.objects.count(), avant)
        self.assertIn(reponse.status_code, (302, 403))

    def test_visiteur_ne_peut_pas_supprimer_une_cle(self):
        self.client.login(username='visiteur', password='motdepasse-test')
        self.client.post(
            reverse('key_delete', args=[self.type_cle.id]))
        self.assertTrue(KeyType.objects.filter(pk=self.type_cle.pk).exists())

    def test_visiteur_ne_peut_pas_supprimer_un_membre(self):
        self.client.login(username='visiteur', password='motdepasse-test')
        self.client.post(reverse('user_delete', args=[self.membre.id]))
        self.assertTrue(User.objects.filter(pk=self.membre.pk).exists())

    def test_visiteur_ne_peut_pas_supprimer_une_equipe(self):
        self.client.login(username='visiteur', password='motdepasse-test')
        self.client.post(reverse('team_delete', args=[self.equipe.id]))
        self.assertTrue(Team.objects.filter(pk=self.equipe.pk).exists())

    def test_visiteur_ne_peut_pas_attribuer_de_cles(self):
        """L'endpoint d'attribution repond 403 JSON, pas une redirection."""
        self.client.login(username='visiteur', password='motdepasse-test')
        reponse = self.client.post(
            reverse('assign_keys'),
            data='{"user_id": %d, "selected_keys": []}' % self.membre.id,
            content_type='application/json')
        self.assertEqual(reponse.status_code, 403)

    def test_visiteur_na_pas_acces_a_la_page_attribution(self):
        self.client.login(username='visiteur', password='motdepasse-test')
        reponse = self.client.get(reverse('user_keys'))
        self.assertIn(reponse.status_code, (302, 403))

    # ── Menus masques ───────────────────────────────────────────────

    def test_le_menu_attribution_est_masque_au_visiteur(self):
        self.client.login(username='visiteur', password='motdepasse-test')
        contenu = self.client.get(reverse('home')).content.decode()
        self.assertNotIn('id="menu-user_keys"', contenu)
        self.assertNotIn('Gestion des clés attribuées', contenu)

    def test_le_menu_administration_est_masque_au_visiteur(self):
        self.client.login(username='visiteur', password='motdepasse-test')
        contenu = self.client.get(reverse('home')).content.decode()
        # On teste les liens, pas les libelles : ceux-ci apparaissent aussi
        # dans le CSS et les traces console du gabarit, toujours rendus.
        self.assertNotIn(reverse('owner_management'), contenu)
        self.assertNotIn(reverse('history_view'), contenu)
        self.assertNotIn(reverse('history_stats'), contenu)
        # La synthese, elle, reste offerte : c'est de la consultation.
        self.assertIn(reverse('synthesis_table'), contenu)

    def test_le_visiteur_garde_son_profil(self):
        self.client.login(username='visiteur', password='motdepasse-test')
        contenu = self.client.get(reverse('home')).content.decode()
        self.assertIn('Gérer mon profile', contenu)
        self.assertEqual(self.client.get(reverse('profile')).status_code, 200)

    def test_les_boutons_daction_sont_masques_au_visiteur(self):
        self.client.login(username='visiteur', password='motdepasse-test')
        contenu = self.client.get(reverse('key_list')).content.decode()
        # Ni les classes CSS ni les selecteurs JS ne disparaissent de la page :
        # on verifie l'absence des boutons eux-memes, via leur libelle accessible.
        self.assertNotIn('aria-label="Ajouter une nouvelle clé"', contenu)
        self.assertNotIn('aria-label="Modifier clé', contenu)
        self.assertNotIn('aria-label="Retirer clé', contenu)
        # ... et la ligne de la cle de test est bien affichee : c'est une page
        # en lecture, pas une page vide.
        self.assertIn('Porte principale', contenu)

    def test_le_visiteur_voit_la_page_detenteurs_sans_les_actions(self):
        self.client.login(username='visiteur', password='motdepasse-test')
        contenu = self.client.get(reverse('home')).content.decode()
        self.assertIn('id="menu-user_list"', contenu)

        reponse = self.client.get(reverse('user_list'))
        self.assertEqual(reponse.status_code, 200)
        page = reponse.content.decode()
        self.assertIn('Dupont', page)           # la liste est bien lisible
        self.assertNotIn('aria-label="Ajouter un nouvel utilisateur"', page)
        self.assertNotIn('aria-label="Modifier Dupont"', page)
        self.assertNotIn('aria-label="Supprimer Dupont"', page)

    def test_le_visiteur_consulte_et_exporte_la_synthese(self):
        self.client.login(username='visiteur', password='motdepasse-test')
        self.assertEqual(
            self.client.get(reverse('synthesis_table')).status_code, 200)
        self.assertEqual(
            self.client.get(reverse('synthesis_export')).status_code, 200)

    # ── L'editeur, lui, garde la main ───────────────────────────────

    def test_lediteur_peut_toujours_ecrire(self):
        self.client.login(username='editeur', password='motdepasse-test')
        avant = Team.objects.count()
        self.client.post(reverse('team_create'), {'name': 'Louange'})
        self.assertEqual(Team.objects.count(), avant + 1)

    def test_lediteur_garde_la_page_attribution(self):
        self.client.login(username='editeur', password='motdepasse-test')
        self.assertEqual(self.client.get(reverse('user_keys')).status_code, 200)


class EditeurTests(TestCase):
    """
    L'editeur fait tout, sauf administrer les comptes et consulter
    l'historique des actions du portail (statistiques comprises).
    """

    @classmethod
    def setUpTestData(cls):
        cls.editeur = Owner.objects.create_user(
            username='editeur2', password='motdepasse-test', role='editor',
            first_name='Edi', last_name='Teur')
        cls.equipe = Team.objects.create(name='Accueil')
        cls.membre = User.objects.create(
            name='Dupont', firstname='Marie', team=cls.equipe)

    def setUp(self):
        self.client.login(username='editeur2', password='motdepasse-test')

    # ── Ce qui lui est ferme ────────────────────────────────────────

    def test_lediteur_na_pas_acces_a_la_gestion_des_comptes(self):
        for nom in ('owner_management', 'add_owner'):
            reponse = self.client.get(reverse(nom))
            self.assertIn(reponse.status_code, (302, 403), nom)

    def test_lediteur_na_pas_acces_a_lhistorique(self):
        for nom in ('history_view', 'history_stats', 'export_history_csv'):
            reponse = self.client.get(reverse(nom))
            self.assertIn(reponse.status_code, (302, 403), nom)

    def test_les_menus_dadministration_lui_sont_masques(self):
        contenu = self.client.get(reverse('home')).content.decode()
        self.assertNotIn(reverse('owner_management'), contenu)
        self.assertNotIn(reverse('history_view'), contenu)
        self.assertNotIn(reverse('history_stats'), contenu)

    # ── Ce qui lui reste ouvert ─────────────────────────────────────

    def test_lediteur_consulte_la_synthese(self):
        contenu = self.client.get(reverse('home')).content.decode()
        self.assertIn(reverse('synthesis_table'), contenu)
        self.assertEqual(
            self.client.get(reverse('synthesis_table')).status_code, 200)
        self.assertEqual(
            self.client.get(reverse('synthesis_export')).status_code, 200)

    def test_lediteur_ecrit_partout_ailleurs(self):
        self.client.post(reverse('key_create'), {
            'number': 42, 'name': 'Sacristie', 'place': 'Fond',
            'total_quantity': 1, 'in_cabinet': 1, 'in_safe': 0,
        })
        self.assertTrue(KeyType.objects.filter(number=42).exists())

        self.client.post(reverse('team_create'), {'name': 'Louange'})
        self.assertTrue(Team.objects.filter(name='Louange').exists())

        self.client.post(reverse('user_delete', args=[self.membre.id]))
        self.assertFalse(User.objects.filter(pk=self.membre.pk).exists())

    def test_lediteur_garde_les_menus_de_gestion(self):
        contenu = self.client.get(reverse('home')).content.decode()
        self.assertIn('id="menu-user_keys"', contenu)
        self.assertIn('id="menu-user_list"', contenu)


class ProtectionCsrfTests(TestCase):
    """
    L'attribution des cles doit exiger le jeton anti-CSRF : sans lui, une page
    tierce ouverte dans un autre onglet pourrait attribuer des cles au nom du
    gestionnaire connecte.
    """

    @classmethod
    def setUpTestData(cls):
        cls.admin = Owner.objects.create_user(
            username='admin-csrf', password='motdepasse-test', role='admin',
            first_name='Ad', last_name='Min')

    def test_lattribution_refuse_une_requete_sans_jeton(self):
        from django.test import Client
        client = Client(enforce_csrf_checks=True)
        client.login(username='admin-csrf', password='motdepasse-test')
        reponse = client.post(
            reverse('assign_keys'),
            data='{"user_id": 1, "selected_keys": []}',
            content_type='application/json')
        self.assertEqual(reponse.status_code, 403)
