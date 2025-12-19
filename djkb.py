# -*- coding: utf-8 -*-
from fpdf import FPDF

class MaintenanceReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.set_text_color(0, 0, 0)
        self.cell(0, 10, 'Projet de Recherche Operationnelle - Rapport', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, num, label):
        self.set_font('Arial', 'B', 12)
        self.set_text_color(0)
        label = self._clean_text(label)
        self.cell(0, 10, f'{num}. {label}', 0, 1, 'L')
        self.ln(2)

    def body_text(self, text):
        self.set_font('Arial', '', 11)
        text = self._clean_text(text)
        self.multi_cell(0, 6, text)
        self.ln()

    def bullet_text(self, text):
        self.set_font('Arial', '', 11)
        text = self._clean_text(text)
        self.cell(10, 6, '-', 0, 0)
        self.multi_cell(0, 6, text)

    def section_subtitle(self, text):
        self.set_font('Arial', 'B', 11)
        text = self._clean_text(text)
        self.cell(0, 8, text, 0, 1)
        self.set_font('Arial', '', 11)
    
    def _clean_text(self, text):
        """Replace accented characters with ASCII equivalents"""
        replacements = {
            'à': 'a', 'â': 'a', 'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
            'î': 'i', 'ï': 'i', 'ô': 'o', 'ù': 'u', 'û': 'u', 'ç': 'c',
            'À': 'A', 'Â': 'A', 'É': 'E', 'È': 'E', 'Ê': 'E', 'Ë': 'E',
            'Î': 'I', 'Ï': 'I', 'Ô': 'O', 'Ù': 'U', 'Û': 'U', 'Ç': 'C',
            ''': "'", ''': "'", '"': '"', '"': '"', '—': '-', '–': '-',
            '…': '...', '°': ' degres', '≤': '<=', '≥': '>=',
            'œ': 'oe', 'Œ': 'OE', 'æ': 'ae', 'Æ': 'AE',
            'ñ': 'n', 'Ñ': 'N', 'ü': 'u', 'Ü': 'U'
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        text = text.encode('latin-1', errors='ignore').decode('latin-1')
        return text

def generate_maintenance_pdf():
    pdf = MaintenanceReport()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # --- 1. Introduction ---
    pdf.chapter_title(1, 'Introduction')
    pdf.body_text(
        "Ce projet presente une application permettant de modeliser et resoudre un "
        "probleme de tournees de techniciens de maintenance avec contraintes de competences "
        "(Technician Routing and Scheduling Problem - TRSP). L'objectif est de determiner "
        "les tournees optimales pour une flotte de techniciens en respectant les competences "
        "requises pour chaque intervention. L'application est developpee en Python (PySide6) "
        "et utilise Gurobi pour resoudre un modele PLNE."
    )

    # --- 2. Objectifs du Projet ---
    pdf.chapter_title(2, 'Objectifs du Projet')
    pdf.bullet_text("Modeliser correctement un probleme de tournees avec contraintes de competences.")
    pdf.bullet_text("Optimiser les trajets et minimiser les couts operationnels.")
    pdf.bullet_text("Integrer contraintes de competences, fenetres de temps et duree de travail.")
    pdf.bullet_text("Fournir une interface simple pour generer et resoudre des instances.")

    # --- 3. Modélisation du Problème ---
    pdf.chapter_title(3, 'Modelisation du Probleme')
    
    pdf.section_subtitle("Ensembles :")
    pdf.bullet_text("K : ensemble des techniciens (k = 1,...,m)")
    pdf.bullet_text("V : ensemble des noeuds (0=depot, 1...n=interventions)")
    pdf.bullet_text("S : ensemble des competences (ex: electricite, gaz, reseau)")
    pdf.ln(2)
    
    pdf.section_subtitle("Variables de decision :")
    pdf.bullet_text("x_ijk (element de) {0,1} : 1 si le technicien k va du site i vers j.")
    pdf.bullet_text("t_ik : heure d'arrivee du technicien k au site i.")
    pdf.ln(2)

    pdf.section_subtitle("Parametres :")
    pdf.bullet_text("c_ij : cout/distance de trajet entre le site i et j (km)")
    pdf.bullet_text("d_i : duree de l'intervention i (min)")
    pdf.bullet_text("req_i : ensemble des competences requises pour l'intervention i")
    pdf.bullet_text("skill_k : ensemble des competences possedees par le technicien k")
    pdf.bullet_text("[e_i, l_i] : fenetre de temps pour le debut du service")
    pdf.bullet_text("T_max : duree maximale de travail par technicien")
    pdf.bullet_text("M : grande constante (big M)")
    pdf.ln(2)

    pdf.section_subtitle("Fonction objectif :")
    pdf.body_text("Min Z = Sum_k Sum_i Sum_j c_ij * x_ijk")
    pdf.ln(2)

    pdf.section_subtitle("Contraintes :")
    pdf.body_text("1. Affectation unique : Sum_k Sum_j x_ijk = 1  pour tout i")
    pdf.body_text("2. Depart du depot : Sum_j x_0jk = 1  pour tout k")
    pdf.body_text("3. Conservation du flux : Sum_i x_ihk - Sum_j x_hjk = 0  pour tout h,k")
    pdf.body_text("4. Contrainte de competences : x_ijk = 0 si req_j n'est pas inclus dans skill_k")
    pdf.body_text("5. Contraintes temporelles : t_ik + d_i + c_ij <= t_jk + M(1 - x_ijk)")
    pdf.body_text("6. Fenetres de temps : e_i <= t_ik <= l_i  pour tout i,k")
    pdf.body_text("7. Duree maximale : t_ik <= T_max  pour tout i,k")
    pdf.body_text("8. Domaines : x_ijk (element de) {0,1}, t_ik >= 0")

    # --- 4. Développement de l'IHM ---
    pdf.add_page()
    pdf.chapter_title(4, "Developpement de l'IHM")
    pdf.body_text("L'interface PySide6 permet :")
    pdf.bullet_text("La generation d'instances (techniciens, interventions, competences).")
    pdf.bullet_text("La configuration : temps limite, MIP gap, nombre de techniciens.")
    pdf.bullet_text("La definition des competences par technicien et par intervention.")
    pdf.bullet_text("L'execution du solveur Gurobi (QThread).")
    pdf.bullet_text("L'affichage automatique des tournees optimales.")

    # --- 5. Résolution et Tests ---
    pdf.chapter_title(5, 'Resolution et Tests')
    pdf.body_text(
        "Des tests ont ete effectues sur 5-20 interventions et 2-5 techniciens."
    )
    pdf.bullet_text("Respect des contraintes : competences, fenetres de temps, duree maximale.")
    pdf.bullet_text("Affectations correctes : chaque intervention realisee par un technicien qualifie.")
    pdf.bullet_text("Temps de calcul acceptable (< 5 secondes pour instances moyennes).")

    # --- 6. Analyse des Résultats ---
    pdf.chapter_title(6, 'Analyse des Resultats')
    pdf.bullet_text("L'affectation depend fortement de la disponibilite des competences.")
    pdf.bullet_text("Les interventions proches sont naturellement regroupees dans une meme tournee.")
    pdf.bullet_text("Les fenetres de temps et competences rares influencent la structure des tournees.")
    pdf.bullet_text("L'equilibrage de charge entre techniciens est observe dans les solutions.")

    # --- 7. Conclusion ---
    pdf.chapter_title(7, 'Conclusion')
    pdf.body_text(
        "Le projet combine modelisation PLNE, implementation Python, interface graphique "
        "et optimisation Gurobi. Il constitue une base solide pour des extensions futures "
        "(multi-periode, preferences clients, optimisation multi-objectif, integration de "
        "donnees reelles d'entreprises de maintenance)."
    )

    output_filename = "Rapport_Maintenance_Routage.pdf"
    pdf.output(output_filename)
    print(f"PDF genere avec succes : {output_filename}")

if __name__ == '__main__':
    generate_maintenance_pdf()