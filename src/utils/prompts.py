#!/usr/bin/env python3
"""
Templates de prompts pour les différents agents.
"""

# Templates généraux
GENERAL_TEMPLATES = {
    # Pour structurer la pensée d'un agent
    "thinking": """
    Réfléchissez étape par étape au problème suivant :
    {problem}
    
    Considérez les aspects suivants :
    1. Quels sont les éléments clés à prendre en compte ?
    2. Quelles approches pourraient résoudre ce problème ?
    3. Quels sont les avantages et inconvénients de chaque approche ?
    4. Quelle est la meilleure solution selon vous ?
    """,
    
    # Pour résumer une solution ou un résultat
    "summary": """
    Résumez votre solution de manière concise :
    
    Problème initial : {problem}
    Approche choisie : {approach}
    Points clés de la solution : {key_points}
    Limitations ou considérations futures : {limitations}
    """
}

# Templates pour le manager
MANAGER_TEMPLATES = {
    # Pour analyser une tâche et la décomposer
    "task_analysis": """
    En tant que manager technique, analysez la tâche suivante et décomposez-la en sous-tâches :
    
    TÂCHE : {task}
    
    1. Analysez les exigences principales
    2. Identifiez les composants clés nécessaires
    3. Répartissez le travail entre les développeurs frontend et backend
    4. Définissez les interfaces entre les composants
    5. Établissez les critères de succès pour chaque sous-tâche
    """,
    
    # Pour assigner des tâches aux développeurs
    "task_assignment": """
    Assignation de tâche à {developer_name} :
    
    CONTEXTE DU PROJET : {project_context}
    
    VOTRE TÂCHE : {specific_task}
    
    ATTENTES :
    - Fournir une solution fonctionnelle pour la tâche assignée
    - Documenter votre approche et les décisions techniques
    - Identifier les potentielles améliorations futures
    
    CONTRAINTES :
    {constraints}
    
    INTERFACES AVEC D'AUTRES COMPOSANTS :
    {interfaces}
    
    CRITÈRES DE SUCCÈS :
    {success_criteria}
    """,
    
    # Pour évaluer le travail des développeurs
    "review_work": """
    Révision du travail soumis par {developer_name} :
    
    TÂCHE ORIGINALE : {original_task}
    
    SOLUTION SOUMISE :
    {submitted_solution}
    
    Évaluez cette solution selon les critères suivants :
    1. Fonctionnalité - La solution répond-elle aux exigences ?
    2. Qualité - Le code/la solution est-il/elle bien conçu(e) et maintenable ?
    3. Intégration - Comment cette solution s'intègre-t-elle avec les autres composants ?
    4. Améliorations - Quelles améliorations suggéreriez-vous ?
    """,
    
    # Pour intégrer les différentes parties d'une solution
    "integration": """
    Intégration des composants pour la tâche : {task}
    
    COMPOSANT FRONTEND :
    {frontend_solution}
    
    COMPOSANT BACKEND :
    {backend_solution}
    
    Réalisez l'intégration des composants en considérant :
    1. La cohérence des interfaces
    2. La compatibilité des données échangées
    3. Les flux de communication entre composants
    4. Les potentiels problèmes d'intégration et leurs solutions
    """
}

# Templates pour le développeur frontend
FRONTEND_TEMPLATES = {
    # Pour concevoir une interface utilisateur
    "ui_design": """
    Concevez une interface utilisateur pour : {feature}
    
    CONTEXTE :
    {context}
    
    UTILISATEURS CIBLES :
    {target_users}
    
    FONCTIONNALITÉS REQUISES :
    {required_features}
    
    Fournissez :
    1. Une description de l'interface et de sa structure
    2. Les composants UI nécessaires
    3. Les interactions utilisateur principales
    4. Les considérations d'expérience utilisateur
    """,
    
    # Pour implémenter un composant frontend
    "component_implementation": """
    Implémentez un composant frontend pour : {component_name}
    
    SPÉCIFICATIONS :
    {specifications}
    
    INTÉGRATION AVEC BACKEND :
    {backend_integration}
    
    TECHNOLOGIES RECOMMANDÉES :
    {recommended_technologies}
    
    Fournissez :
    1. Le code du composant
    2. Les explications des choix d'implémentation
    3. Les instructions d'utilisation
    4. Les tests suggérés
    """
}

# Templates pour le développeur backend
BACKEND_TEMPLATES = {
    # Pour concevoir une architecture backend
    "architecture_design": """
    Concevez une architecture backend pour : {feature}
    
    CONTEXTE :
    {context}
    
    EXIGENCES FONCTIONNELLES :
    {functional_requirements}
    
    EXIGENCES NON-FONCTIONNELLES :
    {non_functional_requirements}
    
    Fournissez :
    1. Un schéma de l'architecture proposée
    2. Les composants backend principaux
    3. Les flux de données
    4. Les technologies recommandées
    5. Les considérations de sécurité et performance
    """,
    
    # Pour implémenter une API
    "api_implementation": """
    Implémentez une API pour : {api_name}
    
    ENDPOINTS REQUIS :
    {required_endpoints}
    
    MODÈLE DE DONNÉES :
    {data_model}
    
    CONTRAINTES :
    {constraints}
    
    Fournissez :
    1. La définition des routes/endpoints
    2. Les structures de données d'entrée/sortie (schémas)
    3. La logique métier principale
    4. Les considérations de sécurité et validation
    5. Les exemples d'utilisation
    """
}
