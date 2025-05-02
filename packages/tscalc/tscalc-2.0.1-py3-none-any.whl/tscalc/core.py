import numpy as np
from datetime import datetime
import json
from tabulate import tabulate
from colorama import init, Fore, Style

# Initialize colorama for colored terminal output
init()

class ToughnessSuccessCalculator:
    """
    A comprehensive assessment tool to evaluate personal attributes related to toughness,
    success potential, and personality type across various domains for professionals.

    Badge Links can be found in terminal after the results are generated. 
    Please share this badge with your network on linkedin with the tag #tscalc and 
    tag me in the post @Craig Michael Dsouza so that I can view and repost your results!

    Made by: Craig ML Dsouza
    LinkedIn: https://www.linkedin.com/in/craig-ml-dsouza/
    Email: dsouzacraigmichael@gmail.com
    
    """
    
    # Class constants
    VERSION = "2.0"
    PERSONALITY_TYPES = {
        "Visionary Pioneer": {
            "description": "Innovative thinkers who drive forward with bold ideas and strategic vision",
            "strengths": ["Innovation", "Strategic thinking", "Risk tolerance", "Big-picture focus"],
            "challenges": ["May overlook details", "Can be impatient with process", "Potential overwhelm others"],
            "ideal_environments": ["Startups", "Research & Development", "Strategic leadership", "Innovation hubs"],
            "development_paths": ["Implementation skills", "Collaborative approaches", "Detail management"],
            "link" : "https://ik.imagekit.io/craigmldsouza05/Visionary.jpeg?updatedAt=1746043993302"
        },
        "Disciplined Achiever": {
            "description": "Methodical, consistent performers who excel through structure and persistence",
            "strengths": ["Consistency", "Reliability", "Process orientation", "Detail management"],
            "challenges": ["May resist change", "Can be rigid", "Sometimes risk-averse"],
            "ideal_environments": ["Project management", "Operations", "Quality control", "Process-driven roles"],
            "development_paths": ["Adaptability", "Innovation", "Comfort with ambiguity"],
            "link": "https://ik.imagekit.io/craigmldsouza05/disciplined.jpg?updatedAt=1746044332321"
        },
        "Analytical Problem-Solver": {
            "description": "Data-driven thinkers who excel at breaking down complex problems",
            "strengths": ["Critical thinking", "Objectivity", "Logical reasoning", "Precision"],
            "challenges": ["May overthink decisions", "Can appear detached", "Potential analysis paralysis"],
            "ideal_environments": ["Research", "Data analysis", "Technical roles", "Strategic planning"],
            "development_paths": ["Decisive action", "Emotional intelligence", "Practical implementation"],
            "link" : "https://ik.imagekit.io/craigmldsouza05/problem.jpg?updatedAt=1746043993086"
        },
        "Relationship Catalyst": {
            "description": "Connection-focused individuals who drive success through networking and influence",
            "strengths": ["Networking", "Persuasion", "Emotional intelligence", "Team building"],
            "challenges": ["May prioritize relationships over results", "Can be conflict-avoidant", "Potential people-pleasing"],
            "ideal_environments": ["Sales", "Team leadership", "Client relations", "Collaborative projects"],
            "development_paths": ["Direct communication", "Objective decision-making", "Strategic focus"],
            "link" : "https://ik.imagekit.io/craigmldsouza05/relation.jpg?updatedAt=1746043993810"
        },
        "Resilient Adaptor": {
            "description": "Flexible, stress-tolerant individuals who thrive amid change and pressure",
            "strengths": ["Adaptability", "Stress tolerance", "Quick recovery", "Solution focus"],
            "challenges": ["May change direction too frequently", "Can undervalue stability", "Potential burnout risk"],
            "ideal_environments": ["Crisis management", "Startup environments", "Change management", "Competitive fields"],
            "development_paths": ["Consistency building", "Strategic long-term planning", "Self-care routines"],
            "link" : "https://ik.imagekit.io/craigmldsouza05/resilient.jpg?updatedAt=1746044263550"
        },
        "Strategic Influencer": {
            "description": "Persuasive communicators who excel at navigating complex social dynamics",
            "strengths": ["Communication", "Social intelligence", "Strategic relationship building", "Perception management"],
            "challenges": ["May appear manipulative", "Can over-rely on persuasion", "Potential authenticity concerns"],
            "ideal_environments": ["Leadership", "Negotiation", "Diplomacy", "Public relations"],
            "development_paths": ["Authentic connection", "Direct value creation", "Technical skill development"],
            "link" : "https://ik.imagekit.io/craigmldsouza05/strategic.jpg?updatedAt=1746043993154"
        },
        "Growth Master": {
            "description": "Learning-oriented achievers who continuously develop and adapt their capabilities",
            "strengths": ["Learning agility", "Self-reflection", "Improvement mindset", "Skill acquisition"],
            "challenges": ["May focus too much on development vs. results", "Can be self-critical", "Potential shiny object syndrome"],
            "ideal_environments": ["Rapidly evolving fields", "Learning organizations", "Mentorship roles", "Innovation teams"],
            "development_paths": ["Results focus", "Specialization", "Self-compassion"],
            "link" : "https://ik.imagekit.io/craigmldsouza05/growth.jpg?updatedAt=1746043993816"
        },
        "Balanced Leader": {
            "description": "Well-rounded performers who balance diverse skills with practical execution",
            "strengths": ["Versatility", "Balanced perspective", "Practical focus", "Steady performance"],
            "challenges": ["May lack standout specialization", "Can be reluctant to take extreme positions", "Potential indecisiveness"],
            "ideal_environments": ["General management", "Cross-functional roles", "Team coordination", "Small businesses"],
            "development_paths": ["Deep expertise development", "Bold decision-making", "Distinctive positioning"],
            "link" : "https://ik.imagekit.io/craigmldsouza05/balanced.jpg?updatedAt=1746043993702"
        }
    }
    
    SKILL_MASTERY_LEVELS = {
        "Novice": (0.0, 0.2),
        "Advanced Beginner": (0.2, 0.4),
        "Competent": (0.4, 0.6),
        "Proficient": (0.6, 0.8),
        "Expert": (0.8, 0.95),
        "Master": (0.95, 1.0),
    }
    
    DEVELOPMENT_STAGES = {
        "Foundation Building": (0.0, 0.3),
        "Skill Development": (0.3, 0.5),
        "Competency Integration": (0.5, 0.7),
        "Excellence Pursuit": (0.7, 0.85),
        "Mastery & Innovation": (0.85, 1.0),
    }
    
    def __init__(self):
        """Initialize the calculator with default values"""
        self.user_data = {}
        self.results = {}
        self.assessment_date = datetime.now()
        self.numpy_fields = []  # Placeholder for any numpy-specific fields
    
    def determine_level(self, value, level_mapping):
        """Determine the appropriate level based on a value and level mapping"""
        for level, (lower, upper) in level_mapping.items():
            if lower <= value <= upper:
                return level
        return "Unknown"
        
    def _print_section_header(self, title):
        """Print a formatted section header"""
        print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{Style.BRIGHT}{title.center(80)}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        
    def _print_subsection_header(self, title):
        """Print a formatted subsection header"""
        print(f"\n{Fore.YELLOW}{'-'*80}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{title}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'-'*80}{Style.RESET_ALL}")
    
    def take_assessment(self):
        """Takes user input via a comprehensive assessment to gather necessary data."""
        self._print_section_header(f"TOUGHNESS & SUCCESS CALCULATOR v{self.VERSION}")
        print(f"""{Fore.GREEN}
Welcome to the Toughness & Success Calculator!
This comprehensive assessment evaluates your attributes, skills, 
and potential across multiple domains.

Answer each question honestly for the most accurate results. 
For numerical ratings, use values between 0.0 and 1.0.

Badge Links can be found in terminal after the results are generated. 
{Fore.YELLOW}Please share this badge on linkedin with the tag {Fore.BLUE}#tscalc {Fore.YELLOW}and tag 
me in the post {Fore.BLUE}@Craig Michael Dsouza {Fore.YELLOW}so that I can view and repost your results!**
{Fore.GREEN}
Made by: Craig ML Dsouza
LinkedIn: https://www.linkedin.com/in/craig-ml-dsouza/
Email: dsouzacraigmichael@gmail.com
            {Style.RESET_ALL}""")

        
        self.user_data = {}
        
        # Basic Information
        self._print_subsection_header("PERSONAL INFORMATION")
        self.user_data['individual_id'] = input("Enter your unique Individual ID: ")
        self.user_data['name'] = input("Enter your name (optional): ")
        self.user_data['domain'] = input("Enter the primary domain/field you're interested in assessing: ")
        
        # Domain Expertise
        self._print_subsection_header("DOMAIN EXPERTISE & SKILLS")
        self.user_data['knowledge_level'] = self._get_float_input("Rate your theoretical knowledge level in this domain")
        self.user_data['skill_level'] = self._get_float_input("Rate your practical skill level in this domain")
        self.user_data['learning_rate'] = self._get_float_input("Rate how quickly you learn new concepts in this domain")
        self.user_data['practice_hours'] = self._get_int_input("Enter your average weekly practice hours in this domain")
        self.user_data['years_experience'] = self._get_int_input("Enter your years of experience in this domain")
        self.user_data['formal_education'] = self._get_float_input("Rate your level of formal education in this domain")
        self.user_data['problem_solving'] = self._get_float_input("Rate your problem-solving ability in this domain")
        self.user_data['creativity_level'] = self._get_float_input("Rate your creativity and innovation in this domain")
        self.user_data['technical_aptitude'] = self._get_float_input("Rate your technical aptitude in this domain")
        
        # Consistency and Task Management
        self._print_subsection_header("CONSISTENCY & TASK MANAGEMENT")
        self.user_data['consistency_score'] = self._get_float_input("Rate your consistency in completing tasks on time and to standard")
        self.user_data['task_management_efficiency'] = self._get_float_input("Rate your efficiency in managing multiple tasks and deadlines")
        self.user_data['focus_ability'] = self._get_float_input("Rate your ability to maintain focus during extended work periods")
        self.user_data['distraction_resistance'] = self._get_float_input("Rate your resistance to distractions")
        self.user_data['work_quality_standards'] = self._get_float_input("Rate your personal standards for work quality")
        self.user_data['deadline_adherence'] = self._get_float_input("Rate your ability to consistently meet deadlines")
        self.user_data['organization_level'] = self._get_float_input("Rate your level of organization and structure in your work")
        
        # Networking and Social Capital
        self._print_subsection_header("NETWORKING & SOCIAL CAPITAL")
        self.user_data['domain_pool_reach'] = self._get_float_input("Rate the size of your professional network relative to your local domain")
        self.user_data['networking_effort'] = self._get_float_input("Rate your active effort in building and maintaining connections")
        self.user_data['visibility_score'] = self._get_float_input("Rate your visibility and recognition for contributions in your domain")
        self.user_data['relationship_nurturing'] = self._get_float_input("Rate how well you nurture and maintain professional relationships")
        self.user_data['network_diversity'] = self._get_float_input("Rate the diversity of your professional network")
        self.user_data['social_listening'] = self._get_float_input("Rate your ability to understand others' needs and perspectives")
        self.user_data['reciprocity_level'] = self._get_float_input("Rate your level of giving back to your network")
        self.user_data['strategic_alliances'] = self._get_float_input("Rate your ability to form strategic alliances and partnerships")
        
        # Resource Utilization
        self._print_subsection_header("RESOURCE UTILIZATION")
        self.user_data['resource_access'] = self._get_float_input("Rate your access to relevant resources in your domain")
        self.user_data['resource_efficiency'] = self._get_float_input("Rate your efficiency in utilizing available resources")
        self.user_data['information_seeking'] = self._get_float_input("Rate your active information seeking behavior")
        self.user_data['tool_utilization'] = self._get_float_input("Rate your ability to leverage tools and technology effectively")
        self.user_data['financial_resource_mgmt'] = self._get_float_input("Rate your management of financial resources")
        self.user_data['time_resource_mgmt'] = self._get_float_input("Rate your management of time as a resource")
        self.user_data['opportunity_recognition'] = self._get_float_input("Rate your ability to recognize and seize opportunities")
        
        # Interpersonal Skills and Influence
        self._print_subsection_header("INTERPERSONAL SKILLS & INFLUENCE")
        self.user_data['agreeableness'] = self._get_float_input("Rate your agreeableness (0.0 = highly disagreeable, 1.0 = highly agreeable)")
        self.user_data['communication_style'] = self._get_float_input("Rate your communication style directness (0.0 = indirect, 1.0 = highly direct)")
        self.user_data['feedback_style'] = self._get_float_input("Rate how critical your feedback is (0.0 = gentle, 1.0 = highly critical)")
        self.user_data['cooperation_level'] = self._get_float_input("Rate your cooperation level with others")
        self.user_data['verbal_success_rate'] = self._get_float_input("Rate your verbal communication success rate")
        self.user_data['nonverbal_awareness'] = self._get_float_input("Rate your awareness and skill with nonverbal communication")
        self.user_data['conflict_resolution'] = self._get_float_input("Rate your conflict resolution skills")
        self.user_data['persuasion_ability'] = self._get_float_input("Rate your ability to persuade others")
        self.user_data['leadership_capacity'] = self._get_float_input("Rate your leadership capacity")
        self.user_data['empathy_level'] = self._get_float_input("Rate your empathy level with others")
        self.user_data['boundary_setting'] = self._get_float_input("Rate your ability to set and maintain healthy boundaries")
        self.user_data['verbal_skill_success_events'] = self._get_int_input("Estimate the number of successful outcomes from your verbal skills")
        
        # Resilience and Psychological Capital
        self._print_subsection_header("RESILIENCE & PSYCHOLOGICAL CAPITAL")
        self.user_data['stress_tolerance'] = self._get_float_input("Rate your ability to handle stress and pressure")
        self.user_data['adaptability'] = self._get_float_input("Rate your adaptability to changing circumstances")
        self.user_data['failure_recovery'] = self._get_float_input("Rate your ability to recover from setbacks and failures")
        self.user_data['uncertainty_tolerance'] = self._get_float_input("Rate your comfort with uncertainty and ambiguity")
        self.user_data['emotional_regulation'] = self._get_float_input("Rate your ability to regulate your emotions effectively")
        self.user_data['perseverance'] = self._get_float_input("Rate your perseverance when facing obstacles")
        self.user_data['optimism_level'] = self._get_float_input("Rate your level of realistic optimism")
        
        # Mindset and Self-Perception
        self._print_subsection_header("MINDSET & SELF-PERCEPTION")
        self.user_data['proactive_ness'] = self._get_float_input("Rate your proactiveness and initiative-taking")
        self.user_data['self_efficacy'] = self._get_float_input("Rate your belief in your ability to succeed")
        self.user_data['growth_mindset'] = self._get_float_input("Rate your belief that abilities can be developed through dedication and work")
        self.user_data['positive_image'] = self._get_float_input("Rate your positive self-image/confidence")
        self.user_data['general_consistency'] = self._get_float_input("Rate your general consistency across all relevant domains")
        self.user_data['general_reach'] = self._get_float_input("Rate your general influence across all relevant domains")
        self.user_data['self_awareness'] = self._get_float_input("Rate your understanding of your own strengths and weaknesses")
        self.user_data['goal_clarity'] = self._get_float_input("Rate how clear your goals are in this domain")
        self.user_data['purpose_alignment'] = self._get_float_input("Rate how aligned your work is with your sense of purpose")
        
        # Additional Context
        self._print_subsection_header("DOMAIN CONTEXT")
        self.user_data['domain_competition'] = self._get_float_input("Rate how competitive your domain is")
        self.user_data['domain_growth'] = self._get_float_input("Rate how rapidly your domain is growing/changing")
        self.user_data['domain_hierarchy'] = self._get_float_input("Rate how hierarchical your domain is")
        self.user_data['domain_collaboration'] = self._get_float_input("Rate how collaborative your domain is")
        
        return self.user_data

    def _get_float_input(self, question):
        """Gets and validates float input from the user."""
        while True:
            try:
                value = float(input(f"{question} (0.0 to 1.0): "))
                if 0.0 <= value <= 1.0:
                    return value
                else:
                    print(f"{Fore.RED}Please enter a value between 0.0 and 1.0.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}Invalid input. Please enter a numerical value.{Style.RESET_ALL}")

    def _get_int_input(self, question):
        """Gets and validates integer input from the user."""
        while True:
            try:
                return int(input(f"{question}: "))
            except ValueError:
                print(f"{Fore.RED}Invalid input. Please enter an integer.{Style.RESET_ALL}")

    def calculate_results(self):
        """Calculate all metrics based on user data"""
        self.results = {
            'domain_expertise': 0,
            'consistency_reliability': 0,
            'network_influence': 0,
            'resource_utilization': 0,
            'interpersonal_effectiveness': 0,
            'resilience': 0,
            'mindset_quality': 0,
            'merit_score': 0,
            'disagreeable_quotient': 0,
            'perceived_disagreeableness': 0,
            'verbal_skill': 0,
            'influence_potential': 0,
            'internal_validation': 0,
            'external_validation': 0,
            'adaptability_index': 0,
            'success_potential': 0,
            'mastery_trajectory': 0,
            'momentum_score': 0,
            'primary_type': '',
            'secondary_type': '',
            'domain_expertise_level': '',
            'success_potential_level': '',
            'development_stage': '',
            'primary_strengths': [],
            'primary_challenges': [],
            'target_improvements': [],
            'recommended_focus_areas': [],
            'next_level_requirements': {},
            'five_year_projection': 0,
        }
        
        self.results['domain_expertise'] = self._calculate_domain_expertise()
        self.results['consistency_reliability'] = self._calculate_consistency_reliability()
        self.results['network_influence'] = self._calculate_network_influence()
        self.results['resource_utilization'] = self._calculate_resource_utilization()
        self.results['interpersonal_effectiveness'] = self._calculate_interpersonal_effectiveness()
        self.results['resilience'] = self._calculate_resilience()
        self.results['mindset_quality'] = self._calculate_mindset_quality()
        
        self.results['merit_score'] = self._calculate_merit()
        self.results['disagreeable_quotient'] = self._calculate_disagreeable_quotient()
        self.results['perceived_disagreeableness'] = self._calculate_perceived_disagreeableness()
        self.results['verbal_skill'] = self._calculate_verbal_skill()
        self.results['influence_potential'] = self._calculate_influence_potential()
        self.results['internal_validation'] = self._calculate_internal_validation()
        self.results['external_validation'] = self._calculate_external_validation()
        self.results['adaptability_index'] = self._calculate_adaptability_index()
        
        self.results['success_potential'] = self._calculate_success_potential()
        self.results['mastery_trajectory'] = self._calculate_mastery_trajectory()
        self.results['momentum_score'] = self._calculate_momentum_score()
        
        personality_scores = self._calculate_personality_type_scores()
        sorted_types = sorted(personality_scores.items(), key=lambda x: x[1], reverse=True)
        self.results['primary_type'] = sorted_types[0][0]
        self.results['secondary_type'] = sorted_types[1][0]
        
        self.results['domain_expertise_level'] = self.determine_level(self.results['domain_expertise'], self.SKILL_MASTERY_LEVELS)
        self.results['success_potential_level'] = self.determine_level(self.results['success_potential'], self.SKILL_MASTERY_LEVELS)
        self.results['development_stage'] = self.determine_level(self.results['mastery_trajectory'], self.DEVELOPMENT_STAGES)
        
        self.results['primary_strengths'] = self._identify_strengths()
        self.results['primary_challenges'] = self._identify_challenges()
        self.results['target_improvements'] = self._identify_improvements()
        self.results['recommended_focus_areas'] = self._recommend_focus_areas()
        self.results['next_level_requirements'] = self._calculate_next_level_requirements()
        self.results['five_year_projection'] = self._calculate_five_year_projection()
        
        return self.results

    def _calculate_domain_expertise(self):
        """Calculate domain expertise composite score"""
        weights = {
            'knowledge_level': 0.20,
            'skill_level': 0.25,
            'learning_rate': 0.15,
            'practice_hours': 0.05,
            'years_experience': 0.05,
            'formal_education': 0.10,
            'problem_solving': 0.15,
            'creativity_level': 0.05
        }
        
        normalized_practice = min(self.user_data['practice_hours'] / 40.0, 1.0)
        normalized_experience = min(self.user_data['years_experience'] / 20.0, 1.0)
        
        score = (
            weights['knowledge_level'] * self.user_data['knowledge_level'] +
            weights['skill_level'] * self.user_data['skill_level'] +
            weights['learning_rate'] * self.user_data['learning_rate'] +
            weights['practice_hours'] * normalized_practice +
            weights['years_experience'] * normalized_experience +
            weights['formal_education'] * self.user_data['formal_education'] +
            weights['problem_solving'] * self.user_data['problem_solving'] +
            weights['creativity_level'] * self.user_data['creativity_level']
        )
        
        return min(max(score, 0.0), 1.0)

    def _calculate_consistency_reliability(self):
        """Calculate consistency and reliability composite score"""
        weights = {
            'consistency_score': 0.20,
            'task_management_efficiency': 0.15,
            'focus_ability': 0.15,
            'distraction_resistance': 0.10,
            'work_quality_standards': 0.15,
            'deadline_adherence': 0.15,
            'organization_level': 0.10
        }
        
        score = sum(weights[key] * self.user_data[key] for key in weights)
        return min(max(score, 0.0), 1.0)

    def _calculate_network_influence(self):
        """Calculate network and influence composite score"""
        weights = {
            'domain_pool_reach': 0.15,
            'networking_effort': 0.15,
            'visibility_score': 0.15,
            'relationship_nurturing': 0.15,
            'network_diversity': 0.10,
            'social_listening': 0.10,
            'reciprocity_level': 0.10,
            'strategic_alliances': 0.10
        }
        
        score = sum(weights[key] * self.user_data[key] for key in weights)
        return min(max(score, 0.0), 1.0)

    def _calculate_resource_utilization(self):
        """Calculate resource utilization composite score"""
        weights = {
            'resource_access': 0.15,
            'resource_efficiency': 0.20,
            'information_seeking': 0.15,
            'tool_utilization': 0.15,
            'financial_resource_mgmt': 0.10,
            'time_resource_mgmt': 0.15,
            'opportunity_recognition': 0.10
        }
        
        score = sum(weights[key] * self.user_data[key] for key in weights)
        return min(max(score, 0.0), 1.0)

    def _calculate_interpersonal_effectiveness(self):
        """Calculate interpersonal effectiveness composite score"""
        disagreeableness = 1 - self.user_data['agreeableness']
        disagreeableness_optimality = 1 - 2 * abs(disagreeableness - 0.4)
        
        weights = {
            'disagreeableness_optimality': 0.10,
            'communication_style': 0.15,
            'verbal_success_rate': 0.15,
            'nonverbal_awareness': 0.10,
            'conflict_resolution': 0.10,
            'persuasion_ability': 0.15,
            'leadership_capacity': 0.10,
            'empathy_level': 0.10,
            'boundary_setting': 0.05
        }
        
        temp_data = self.user_data.copy()
        temp_data['disagreeableness_optimality'] = disagreeableness_optimality
        
        score = sum(weights[key] * temp_data[key] for key in weights)
        return min(max(score, 0.0), 1.0)

    def _calculate_resilience(self):
        """Calculate resilience composite score"""
        weights = {
            'stress_tolerance': 0.20,
            'adaptability': 0.20,
            'failure_recovery': 0.15,
            'uncertainty_tolerance': 0.15,
            'emotional_regulation': 0.10,
            'perseverance': 0.15,
            'optimism_level': 0.05
        }
        
        score = sum(weights[key] * self.user_data[key] for key in weights)
        return min(max(score, 0.0), 1.0)

    def _calculate_mindset_quality(self):
        """Calculate mindset quality composite score"""
        weights = {
            'proactive_ness': 0.15,
            'self_efficacy': 0.15,
            'growth_mindset': 0.20,
            'positive_image': 0.10,
            'self_awareness': 0.15,
            'goal_clarity': 0.15,
            'purpose_alignment': 0.10
        }
        
        score = sum(weights[key] * self.user_data[key] for key in weights)
        return min(max(score, 0.0), 1.0)

    def _calculate_merit(self):
        """Calculate overall merit score"""
        component_weights = {
            'domain_expertise': 0.25,
            'consistency_reliability': 0.15,
            'network_influence': 0.15,
            'resource_utilization': 0.10,
            'interpersonal_effectiveness': 0.15,
            'resilience': 0.10,
            'mindset_quality': 0.10
        }
        
        score = sum(component_weights[key] * self.results[key] for key in component_weights)
        return min(max(score, 0.0), 1.0)

    def _calculate_disagreeable_quotient(self):
        """Calculate the disagreeable quotient"""
        return 1 - self.user_data['agreeableness']

    def _calculate_perceived_disagreeableness(self):
        """Calculate the perceived disagreeableness"""
        base = self._calculate_disagreeable_quotient()
        modifiers = (
            (self.user_data['communication_style'] * 0.5) + 
            (self.user_data['feedback_style'] * 0.7) - 
            (self.user_data['cooperation_level'] * 0.6) -
            (self.user_data['empathy_level'] * 0.4)
        )
        perceived = base + (modifiers * 0.3)
        return min(max(perceived, 0.0), 1.0)

    def _calculate_verbal_skill(self):
        """Calculate verbal skill based on success events and other factors"""
        base_verbal = self.user_data['verbal_success_rate']
        events_contribution = min(self.user_data['verbal_skill_success_events'] * 0.01, 0.3)
        disagreeable_q = self._calculate_disagreeable_quotient()
        disagreeable_modifier = 0.2 * (1 - 2 * abs(disagreeable_q - 0.4))
        directness_contribution = self.user_data['communication_style'] * 0.1
        verbal_skill = (
            base_verbal * 0.6 + 
            events_contribution * 0.2 +
            disagreeable_modifier + 
            directness_contribution
        )
        return min(max(verbal_skill, 0.0), 1.0)

    def _calculate_influence_potential(self):
        """Calculate influence potential"""
        verbal_skill = self.results['verbal_skill']
        network_score = self.results['network_influence']
        
        factors = {
            'verbal_skill': self.results['verbal_skill'] * 0.20,
            'persuasion_ability': self.user_data['persuasion_ability'] * 0.15,
            'leadership_capacity': self.user_data['leadership_capacity'] * 0.10,
            'network_influence': self.results['network_influence'] * 0.15,
            'resource_utilization': self.results['resource_utilization'] * 0.10,
            'social_listening': self.user_data['social_listening'] * 0.05,
            'adaptability': self.user_data['adaptability'] * 0.05,
            'self_efficacy': self.user_data['self_efficacy'] * 0.10,
            'goal_clarity': self.user_data['goal_clarity'] * 0.10
        }
        
        influence_score = sum(factors.values())
        return min(max(influence_score, 0.0), 1.0)

    def _calculate_internal_validation(self):
        """Calculate internal validation score"""
        external_dependency = (
            (1 - self.user_data['self_efficacy']) * 0.4 +
            (1 - self.user_data['growth_mindset']) * 0.3 +
            (1 - self.user_data['positive_image']) * 0.3
        )
        internal_validation = 1 - (external_dependency * 0.7)
        alignment_boost = (
            self.user_data['goal_clarity'] * 0.15 +
            self.user_data['purpose_alignment'] * 0.15
        )
        score = internal_validation + alignment_boost
        return min(max(score, 0.0), 1.0)

    def _calculate_external_validation(self):
        """Calculate external validation score"""
        network_contribution = (
            self.user_data['domain_pool_reach'] * 0.2 +
            self.user_data['visibility_score'] * 0.3 +
            self.user_data['networking_effort'] * 0.2
        )
        agreeableness_factor = self.user_data['agreeableness'] * 0.3
        score = network_contribution * 0.7 + agreeableness_factor
        return min(max(score, 0.0), 1.0)

    def _calculate_adaptability_index(self):
        """Calculate adaptability index"""
        adaptability_factors = {
            'adaptability': self.user_data['adaptability'] * 0.25,
            'learning_rate': self.user_data['learning_rate'] * 0.20,
            'uncertainty_tolerance': self.user_data['uncertainty_tolerance'] * 0.15,
            'stress_tolerance': self.user_data['stress_tolerance'] * 0.15,
            'failure_recovery': self.user_data['failure_recovery'] * 0.15,
            'growth_mindset': self.user_data['growth_mindset'] * 0.10
        }
        score = sum(adaptability_factors.values())
        return min(max(score, 0.0), 1.0)

    def _calculate_success_potential(self):
        """Calculate overall success potential"""
        factors = {
            'merit_score': self.results['merit_score'] * 0.30,
            'adaptability_index': self.results['adaptability_index'] * 0.15,
            'influence_potential': self.results['influence_potential'] * 0.15,
            'internal_validation': self.results['internal_validation'] * 0.10,
            'resilience': self.results['resilience'] * 0.15,
            'mindset_quality': self.results['mindset_quality'] * 0.15
        }
        
        domain_competitiveness = self.user_data['domain_competition']
        domain_growth = self.user_data['domain_growth']
        
        if domain_competitiveness > 0.7:
            factors['merit_score'] *= 1.1
            factors['influence_potential'] *= 1.2
            factors['resilience'] *= 1.2
        
        if domain_growth > 0.7:
            factors['adaptability_index'] *= 1.3
            factors['influence_potential'] *= 1.1
        
        base_potential = sum(factors.values())
        return min(max(base_potential, 0.0), 1.0)

    def _calculate_mastery_trajectory(self):
        """Calculate mastery trajectory"""
        current_expertise = self.results['domain_expertise']
        
        growth_potential = (
            self.user_data['learning_rate'] * 0.25 +
            self.user_data['growth_mindset'] * 0.20 +
            self.user_data['practice_hours'] / 40.0 * 0.20 +
            self.user_data['consistency_score'] * 0.20 +
            self.user_data['proactive_ness'] * 0.15
        )
        
        trajectory = (current_expertise * 0.6) + (growth_potential * 0.4)
        return min(max(trajectory, 0.0), 1.0)

    def _calculate_momentum_score(self):
        """Calculate momentum score"""
        practice_intensity = min(self.user_data['practice_hours'] / 40.0, 1.0)
        
        factors = {
            'practice_intensity': practice_intensity * 0.30,
            'consistency_score': self.user_data['consistency_score'] * 0.20,
            'learning_rate': self.user_data['learning_rate'] * 0.20,
            'proactive_ness': self.user_data['proactive_ness'] * 0.15,
            'resource_utilization': self.results['resource_utilization'] * 0.15
        }
        
        score = sum(factors.values())
        return min(max(score, 0.0), 1.0)

    def _calculate_personality_type_scores(self):
        """Calculate scores for each personality type"""
        personality_scores = {}
        
        personality_scores["Visionary Pioneer"] = (
            self.user_data['creativity_level'] * 0.25 +
            self.user_data['uncertainty_tolerance'] * 0.20 +
            self.user_data['proactive_ness'] * 0.20 +
            self.user_data['adaptability'] * 0.15 +
            self.user_data['problem_solving'] * 0.20
        )
        
        personality_scores["Disciplined Achiever"] = (
            self.user_data['consistency_score'] * 0.30 +
            self.user_data['task_management_efficiency'] * 0.20 +
            self.user_data['work_quality_standards'] * 0.20 +
            self.user_data['deadline_adherence'] * 0.15 +
            self.user_data['organization_level'] * 0.15
        )
        
        personality_scores["Analytical Problem-Solver"] = (
            self.user_data['problem_solving'] * 0.35 +
            self.user_data['knowledge_level'] * 0.20 +
            self.user_data['technical_aptitude'] * 0.20 +
            (1 - self.user_data['agreeableness']) * 0.10 +
            self.user_data['information_seeking'] * 0.15
        )
        
        personality_scores["Relationship Catalyst"] = (
            self.user_data['domain_pool_reach'] * 0.20 +
            self.user_data['relationship_nurturing'] * 0.25 +
            self.user_data['empathy_level'] * 0.20 +
            self.user_data['reciprocity_level'] * 0.15 +
            self.user_data['strategic_alliances'] * 0.20
        )
        
        personality_scores["Resilient Adaptor"] = (
            self.user_data['stress_tolerance'] * 0.25 +
            self.user_data['adaptability'] * 0.25 +
            self.user_data['failure_recovery'] * 0.20 +
            self.user_data['uncertainty_tolerance'] * 0.15 +
            self.user_data['emotional_regulation'] * 0.15
        )
        
        personality_scores["Strategic Influencer"] = (
            self.user_data['persuasion_ability'] * 0.25 +
            self.user_data['verbal_success_rate'] * 0.20 +
            self.user_data['strategic_alliances'] * 0.20 +
            self.user_data['leadership_capacity'] * 0.20 +
            self.user_data['social_listening'] * 0.15
        )
        
        personality_scores["Growth Master"] = (
            self.user_data['learning_rate'] * 0.30 +
            self.user_data['growth_mindset'] * 0.25 +
            self.user_data['self_awareness'] * 0.15 +
            self.user_data['goal_clarity'] * 0.15 +
            self.user_data['information_seeking'] * 0.15
        )
        
        personality_scores["Balanced Leader"] = (
            self.user_data['task_management_efficiency'] * 0.25 +
            self.user_data['problem_solving'] * 0.20 +
            self.user_data['cooperation_level'] * 0.20 +
            self.user_data['verbal_success_rate'] * 0.15 +
            self.user_data['resource_efficiency'] * 0.20
        )
        
        return personality_scores

    def _identify_strengths(self):
        """Identify the individual's top strengths"""
        all_metrics = {
            'Domain Knowledge': self.user_data['knowledge_level'],
            'Practical Skills': self.user_data['skill_level'],
            'Problem-Solving': self.user_data['problem_solving'],
            'Creativity': self.user_data['creativity_level'],
            'Technical Aptitude': self.user_data['technical_aptitude'],
            'Consistency': self.user_data['consistency_score'],
            'Task Management': self.user_data['task_management_efficiency'],
            'Focus': self.user_data['focus_ability'],
            'Quality Standards': self.user_data['work_quality_standards'],
            'Networking': self.user_data['domain_pool_reach'],
            'Visibility': self.user_data['visibility_score'],
            'Relationship Building': self.user_data['relationship_nurturing'],
            'Resource Management': self.user_data['resource_efficiency'],
            'Information Seeking': self.user_data['information_seeking'],
            'Tool Utilization': self.user_data['tool_utilization'],
            'Communication': self.user_data['verbal_success_rate'],
            'Persuasion': self.user_data['persuasion_ability'],
            'Leadership': self.user_data['leadership_capacity'],
            'Empathy': self.user_data['empathy_level'],
            'Stress Tolerance': self.user_data['stress_tolerance'],
            'Adaptability': self.user_data['adaptability'],
            'Failure Recovery': self.user_data['failure_recovery'],
            'Proactiveness': self.user_data['proactive_ness'],
            'Self-Efficacy': self.user_data['self_efficacy'],
            'Growth Mindset': self.user_data['growth_mindset']
        }
        
        sorted_metrics = sorted(all_metrics.items(), key=lambda x: x[1], reverse=True)
        top_strengths = [metric[0] for metric in sorted_metrics[:5]]
        return top_strengths

    def _identify_challenges(self):
        """Identify the individual's top challenges"""
        all_metrics = {
            'Domain Knowledge': self.user_data['knowledge_level'],
            'Practical Skills': self.user_data['skill_level'],
            'Problem-Solving': self.user_data['problem_solving'],
            'Creativity': self.user_data['creativity_level'],
            'Technical Aptitude': self.user_data['technical_aptitude'],
            'Consistency': self.user_data['consistency_score'],
            'Task Management': self.user_data['task_management_efficiency'],
            'Focus': self.user_data['focus_ability'],
            'Quality Standards': self.user_data['work_quality_standards'],
            'Networking': self.user_data['domain_pool_reach'],
            'Visibility': self.user_data['visibility_score'],
            'Relationship Building': self.user_data['relationship_nurturing'],
            'Resource Management': self.user_data['resource_efficiency'],
            'Information Seeking': self.user_data['information_seeking'],
            'Tool Utilization': self.user_data['tool_utilization'],
            'Communication': self.user_data['verbal_success_rate'],
            'Persuasion': self.user_data['persuasion_ability'],
            'Leadership': self.user_data['leadership_capacity'],
            'Empathy': self.user_data['empathy_level'],
            'Stress Tolerance': self.user_data['stress_tolerance'],
            'Adaptability': self.user_data['adaptability'],
            'Failure Recovery': self.user_data['failure_recovery'],
            'Proactiveness': self.user_data['proactive_ness'],
            'Self-Efficacy': self.user_data['self_efficacy'],
            'Growth Mindset': self.user_data['growth_mindset']
        }
        
        sorted_metrics = sorted(all_metrics.items(), key=lambda x: x[1])
        top_challenges = [metric[0] for metric in sorted_metrics[:5]]
        return top_challenges

    def _identify_improvements(self):
        """Identify the highest impact areas for improvement"""
        impact_weights = {
            'Domain Knowledge': 0.08,
            'Practical Skills': 0.10,
            'Problem-Solving': 0.07,
            'Consistency': 0.07,
            'Task Management': 0.06,
            'Networking': 0.05,
            'Visibility': 0.04,
            'Resource Management': 0.04,
            'Communication': 0.07,
            'Persuasion': 0.05,
            'Leadership': 0.05,
            'Adaptability': 0.06,
            'Failure Recovery': 0.05,
            'Proactiveness': 0.06,
            'Self-Efficacy': 0.04,
            'Growth Mindset': 0.05,
            'Stress Tolerance': 0.06
        }
        
        current_scores = {
            'Domain Knowledge': self.user_data['knowledge_level'],
            'Practical Skills': self.user_data['skill_level'],
            'Problem-Solving': self.user_data['problem_solving'],
            'Consistency': self.user_data['consistency_score'],
            'Task Management': self.user_data['task_management_efficiency'],
            'Networking': self.user_data['domain_pool_reach'],
            'Visibility': self.user_data['visibility_score'],
            'Resource Management': self.user_data['resource_efficiency'],
            'Communication': self.user_data['verbal_success_rate'],
            'Persuasion': self.user_data['persuasion_ability'],
            'Leadership': self.user_data['leadership_capacity'],
            'Adaptability': self.user_data['adaptability'],
            'Failure Recovery': self.user_data['failure_recovery'],
            'Proactiveness': self.user_data['proactive_ness'],
            'Self-Efficacy': self.user_data['self_efficacy'],
            'Growth Mindset': self.user_data['growth_mindset'],
            'Stress Tolerance': self.user_data['stress_tolerance']
        }
        
        improvement_potential = {}
        for attribute, weight in impact_weights.items():
            current = current_scores[attribute]
            gap = max(0, 0.85 - current)
            improvement_potential[attribute] = gap * weight
        
        sorted_improvements = sorted(improvement_potential.items(), key=lambda x: x[1], reverse=True)
        top_improvements = [metric[0] for metric in sorted_improvements[:3]]
        return top_improvements

    def _recommend_focus_areas(self):
        """Recommend specific focus areas"""
        primary_type = self.results['primary_type']
        secondary_type = self.results['secondary_type']
        challenges = self.results['primary_challenges']
        
        primary_dev_paths = self.PERSONALITY_TYPES[primary_type]['development_paths']
        secondary_dev_paths = self.PERSONALITY_TYPES[secondary_type]['development_paths']
        
        focus_areas = []
        focus_areas.append(primary_dev_paths[0])
        
        for path in secondary_dev_paths:
            if any(challenge.lower() in path.lower() for challenge in challenges):
                focus_areas.append(path)
                break
        else:
            focus_areas.append(secondary_dev_paths[0])
        
        skill_recommendations = {
            'Domain Knowledge': 'Structured learning in core domain concepts',
            'Practical Skills': 'Deliberate practice with feedback loops',
            'Problem-Solving': 'Systematic problem-solving frameworks',
            'Consistency': 'Habit formation and routine development',
            'Task Management': 'Task prioritization and time blocking systems',
            'Networking': 'Strategic relationship building',
            'Visibility': 'Content creation and thought leadership',
            'Resource Management': 'Resource optimization techniques',
            'Communication': 'Structured communication frameworks',
            'Persuasion': 'Influence psychology and applications',
            'Leadership': 'Situational leadership approaches',
            'Adaptability': 'Comfort zone expansion exercises',
            'Failure Recovery': 'Resilience building practices',
            'Proactiveness': 'Initiative-taking frameworks',
            'Self-Efficacy': 'Evidence-based confidence building',
            'Growth Mindset': 'Learning orientation development',
            'Stress Tolerance': 'Stress management techniques'
        }
        
        for challenge in challenges[:2]:
            if challenge in skill_recommendations:
                focus_areas.append(skill_recommendations[challenge])
        
        return focus_areas[:4]

    def _calculate_next_level_requirements(self):
        """Calculate requirements to reach the next level of mastery"""
        current_level = self.results['domain_expertise_level']
        
        requirements = {}
        
        if current_level == "Novice":
            requirements = {
                "Practice Hours": "15-20 hours/week of deliberate practice",
                "Knowledge Expansion": "Master foundational concepts and principles",
                "Skill Focus": "Develop basic technical skills with supervision",
                "Networking": "Connect with peers for knowledge sharing"
            }
        elif current_level == "Advanced Beginner":
            requirements = {
                "Practice Hours": "20-25 hours/week of deliberate practice",
                "Knowledge Expansion": "Deepen understanding of intermediate concepts",
                "Skill Focus": "Apply skills with decreasing guidance",
                "Networking": "Build relationships with experienced practitioners",
                "Projects": "Complete structured projects with feedback"
            }
        elif current_level == "Competent":
            requirements = {
                "Practice Hours": "25-30 hours/week of deliberate practice",
                "Knowledge Expansion": "Integrate specialized knowledge areas",
                "Skill Focus": "Develop situational problem-solving",
                "Networking": "Connect with domain experts and mentors",
                "Projects": "Lead increasingly complex projects",
                "Teaching": "Begin teaching/mentoring beginners"
            }
        elif current_level == "Proficient":
            requirements = {
                "Practice Hours": "30+ hours/week of deliberate practice",
                "Knowledge Expansion": "Develop nuanced understanding of domain",
                "Skill Focus": "Intuitive application of principles",
                "Innovation": "Contribute novel approaches to problems",
                "Visibility": "Establish thought leadership",
                "Teaching": "Formalize knowledge through teaching/writing"
            }
        elif current_level == "Expert":
            requirements = {
                "Practice Hours": "30+ hours/week of targeted improvement",
                "Knowledge Expansion": "Integrate cross-disciplinary insights",
                "Skill Focus": "Refine intuitive expertise",
                "Innovation": "Create original contributions to the field",
                "Visibility": "Establish recognized authority",
                "Teaching": "Develop systems for knowledge transfer"
            }
        elif current_level == "Master":
            requirements = {
                "Practice Hours": "Maintain deliberate practice routines",
                "Knowledge Expansion": "Pioneer new directions in the field",
                "Legacy": "Develop frameworks and schools of thought",
                "Teaching": "Create systematic approaches to developing others"
            }
        
        return requirements

    def _calculate_five_year_projection(self):
        """Project potential growth over five years"""
        current_expertise = self.results['domain_expertise']
        
        learning_rate = self.user_data['learning_rate']
        practice_intensity = min(self.user_data['practice_hours'] / 40.0, 1.0)
        consistency = self.user_data['consistency_score']
        growth_mindset = self.user_data['growth_mindset']
        domain_growth = self.user_data['domain_growth']
        
        base_growth_rate = 0.10 * (1 - current_expertise * 0.5)
        
        adjusted_growth_rate = base_growth_rate * (
            1 + 
            (learning_rate - 0.5) * 0.4 +
            (practice_intensity - 0.5) * 0.3 +
            (consistency - 0.5) * 0.2 +
            (growth_mindset - 0.5) * 0.2 +
            (domain_growth - 0.5) * 0.1
        )
        
        annual_growth_rate = max(min(adjusted_growth_rate, 0.20), 0.02)
        
        projection = current_expertise
        for _ in range(5):
            growth_this_year = annual_growth_rate * (1 - projection * 0.5)
            projection += growth_this_year
            annual_growth_rate *= 0.95
        
        return min(projection, 1.0)

    def display_results(self):
        """Display the calculated results"""
        self._print_section_header("ASSESSMENT RESULTS")
        print(f"\n{Fore.GREEN}Assessment for: {self.user_data.get('name', 'Anonymous')}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Individual ID: {self.user_data.get('individual_id', 'Not provided')}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Domain: {self.user_data.get('domain', 'General')}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Assessment Date: {self.assessment_date.strftime('%Y-%m-%d %H:%M')}{Style.RESET_ALL}")
        
        self._print_subsection_header("PRIMARY METRICS")
        metrics_data = [
            ["Domain Expertise", f"{self.results['domain_expertise']:.2f}", self.results['domain_expertise_level']],
            ["Consistency & Reliability", f"{self.results['consistency_reliability']:.2f}", ""],
            ["Network & Influence", f"{self.results['network_influence']:.2f}", ""],
            ["Resource Utilization", f"{self.results['resource_utilization']:.2f}", ""],
            ["Interpersonal Effectiveness", f"{self.results['interpersonal_effectiveness']:.2f}", ""],
            ["Resilience", f"{self.results['resilience']:.2f}", ""],
            ["Mindset Quality", f"{self.results['mindset_quality']:.2f}", ""]
        ]
        print(tabulate(metrics_data, headers=["Metric", "Score", "Level"], tablefmt="simple"))
        
        self._print_subsection_header("SECONDARY METRICS")
        secondary_data = [
            ["Merit Score", f"{self.results['merit_score']:.2f}"],
            ["Disagreeable Quotient", f"{self.results['disagreeable_quotient']:.2f}"],
            ["Perceived Disagreeableness", f"{self.results['perceived_disagreeableness']:.2f}"],
            ["Verbal Skill", f"{self.results['verbal_skill']:.2f}"],
            ["Influence Potential", f"{self.results['influence_potential']:.2f}"],
            ["Internal Validation", f"{self.results['internal_validation']:.2f}"],
            ["External Validation", f"{self.results['external_validation']:.2f}"],
            ["Adaptability Index", f"{self.results['adaptability_index']:.2f}"]
        ]
        print(tabulate(secondary_data, headers=["Metric", "Score"], tablefmt="simple"))
        
        self._print_subsection_header("SUCCESS METRICS")
        success_data = [
            ["Success Potential", f"{self.results['success_potential']:.2f}", self.results['success_potential_level']],
            ["Mastery Trajectory", f"{self.results['mastery_trajectory']:.2f}", self.results['development_stage']],
            ["Momentum Score", f"{self.results['momentum_score']:.2f}", ""],
            ["Five-Year Projection", f"{self.results['five_year_projection']:.2f}", ""]
        ]
        print(tabulate(success_data, headers=["Metric", "Score", "Level"], tablefmt="simple"))
        
        self._print_subsection_header("PERSONALITY PROFILE")
        print(f"{Fore.CYAN}Primary Type: {Fore.WHITE}{self.results['primary_type']}{Style.RESET_ALL}")
        print(self.PERSONALITY_TYPES[self.results['primary_type']]['description'])
        print(f"{Fore.CYAN}Primary Badge Link: {Fore.WHITE}{Style.RESET_ALL}")
        print(self.PERSONALITY_TYPES[self.results['primary_type']]['link'])
        print(f"\n{Fore.CYAN}Secondary Type: {Fore.WHITE}{self.results['secondary_type']}{Style.RESET_ALL}")
        print(self.PERSONALITY_TYPES[self.results['secondary_type']]['description'])
        print(f"{Fore.CYAN}Secondary Badge Link: {Fore.WHITE}{Style.RESET_ALL}")
        print(self.PERSONALITY_TYPES[self.results['secondary_type']]['link'])
        
        self._print_subsection_header("TOP STRENGTHS")
        for i, strength in enumerate(self.results['primary_strengths'], 1):
            print(f"{Fore.GREEN}{i}. {strength}{Style.RESET_ALL}")
        
        self._print_subsection_header("PRIMARY CHALLENGES")
        for i, challenge in enumerate(self.results['primary_challenges'], 1):
            print(f"{Fore.YELLOW}{i}. {challenge}{Style.RESET_ALL}")
        
        self._print_subsection_header("RECOMMENDED FOCUS AREAS")
        for i, area in enumerate(self.results['recommended_focus_areas'], 1):
            print(f"{Fore.CYAN}{i}. {area}{Style.RESET_ALL}")
        
        self._print_subsection_header("REQUIREMENTS FOR NEXT LEVEL")
        for requirement, description in self.results['next_level_requirements'].items():
            print(f"{Fore.MAGENTA}{requirement}: {Fore.WHITE}{description}{Style.RESET_ALL}")
        
        self._print_subsection_header("PERSONALITY TYPE INSIGHTS")
        primary_type = self.results['primary_type']
        print(f"{Fore.GREEN}Strengths:{Style.RESET_ALL}")
        for strength in self.PERSONALITY_TYPES[primary_type]['strengths']:
            print(f"  • {strength}")
        print(f"\n{Fore.YELLOW}Challenges:{Style.RESET_ALL}")
        for challenge in self.PERSONALITY_TYPES[primary_type]['challenges']:
            print(f"  • {challenge}")
        print(f"\n{Fore.CYAN}Ideal Environments:{Style.RESET_ALL}")
        for environment in self.PERSONALITY_TYPES[primary_type]['ideal_environments']:
            print(f"  • {environment}")

    def save_results(self, filename=None):
        """Save assessment results to a JSON file"""
        if filename is None:
            individual_id = self.user_data.get('individual_id', 'anonymous')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"assessment_{individual_id}_{timestamp}.json"
        
        save_data = {
            'metadata': {
                'version': self.VERSION,
                'date': self.assessment_date.strftime("%Y-%m-%d %H:%M:%S"),
                'individual_id': self.user_data.get('individual_id', 'anonymous'),
                'name': self.user_data.get('name', 'Anonymous'),
                'domain': self.user_data.get('domain', 'General')
            },
            'user_data': self.user_data,
            'results': self.results
        }
        
        for key, value in save_data['results'].items():
            if isinstance(value, np.ndarray):
                save_data['results'][key] = value.tolist()
        
        try:
            with open(filename, 'w') as f:
                json.dump(save_data, f, indent=4)
            print(f"\n{Fore.GREEN}Results saved to {filename}{Style.RESET_ALL}")
            return True
        except Exception as e:
            print(f"\n{Fore.RED}Error saving results: {e}{Style.RESET_ALL}")
            return False

    def load_results(self, filename):
        """Load assessment results from a JSON file"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            self.user_data = data['user_data']
            self.results = data['results']
            
            for key, value in self.results.items():
                if isinstance(value, list) and key in self.numpy_fields:
                    self.results[key] = np.array(value)
            
            self.assessment_date = datetime.strptime(data['metadata']['date'], "%Y-%m-%d %H:%M:%S")
            print(f"\n{Fore.GREEN}Results successfully loaded from {filename}{Style.RESET_ALL}")
            
            self.display_results()
            return True
        except FileNotFoundError:
            print(f"\n{Fore.RED}File not found: {filename}{Style.RESET_ALL}")
            return False
        except json.JSONDecodeError:
            print(f"\n{Fore.RED}Invalid JSON format in file: {filename}{Style.RESET_ALL}")
            return False
        except Exception as e:
            print(f"\n{Fore.RED}Error loading results: {e}{Style.RESET_ALL}")
            return False

    def export_pdf_report(self, filename=None):
        """Export assessment results to a PDF file"""
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        
        if filename is None:
            individual_id = self.user_data.get('individual_id', 'anonymous')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"assessment_report_{individual_id}_{timestamp}.pdf"
        
        try:
            doc = SimpleDocTemplate(filename, pagesize=letter)
            styles = getSampleStyleSheet()
            
            title_style = ParagraphStyle(
                'Title',
                parent=styles['Title'],
                fontSize=16,
                alignment=1,
                spaceAfter=12
            )
            
            heading_style = ParagraphStyle(
                'Heading',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=6,
                spaceBefore=12
            )
            
            subheading_style = ParagraphStyle(
                'Subheading',
                parent=styles['Heading3'],
                fontSize=12,
                spaceAfter=6,
                spaceBefore=8
            )
            
            content = []
            
            content.append(Paragraph(f"Assessment Report: {self.user_data.get('name', 'Anonymous')}", title_style))
            content.append(Spacer(1, 12))
            
            metadata = [
                ["Individual ID", self.user_data.get('individual_id', 'Not provided')],
                ["Domain", self.user_data.get('domain', 'General')],
                ["Assessment Date", self.assessment_date.strftime('%Y-%m-%d %H:%M')]
            ]
            
            metadata_table = Table(metadata, colWidths=[150, 350])
            metadata_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
            ]))
            content.append(metadata_table)
            content.append(Spacer(1, 20))
            
            content.append(Paragraph("PRIMARY METRICS", heading_style))
            
            metrics_data = [["Metric", "Score", "Level"]]
            metrics_data.extend([
                ["Domain Expertise", f"{self.results['domain_expertise']:.2f}", self.results['domain_expertise_level']],
                ["Consistency & Reliability", f"{self.results['consistency_reliability']:.2f}", ""],
                ["Network & Influence", f"{self.results['network_influence']:.2f}", ""],
                ["Resource Utilization", f"{self.results['resource_utilization']:.2f}", ""],
                ["Interpersonal Effectiveness", f"{self.results['interpersonal_effectiveness']:.2f}", ""],
                ["Resilience", f"{self.results['resilience']:.2f}", ""],
                ["Mindset Quality", f"{self.results['mindset_quality']:.2f}", ""]
            ])
            
            metrics_table = Table(metrics_data, colWidths=[200, 100, 200])
            metrics_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
            ]))
            content.append(metrics_table)
            content.append(Spacer(1, 15))
            
            content.append(Paragraph("SECONDARY METRICS", heading_style))
            
            secondary_data = [["Metric", "Score"]]
            secondary_data.extend([
                ["Merit Score", f"{self.results['merit_score']:.2f}"],
                ["Disagreeable Quotient", f"{self.results['disagreeable_quotient']:.2f}"],
                ["Perceived Disagreeableness", f"{self.results['perceived_disagreeableness']:.2f}"],
                ["Verbal Skill", f"{self.results['verbal_skill']:.2f}"],
                ["Influence Potential", f"{self.results['influence_potential']:.2f}"],
                ["Internal Validation", f"{self.results['internal_validation']:.2f}"],
                ["External Validation", f"{self.results['external_validation']:.2f}"],
                ["Adaptability Index", f"{self.results['adaptability_index']:.2f}"]
            ])
            
            secondary_table = Table(secondary_data, colWidths=[250, 250])
            secondary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
            ]))
            content.append(secondary_table)
            content.append(Spacer(1, 15))
            
            content.append(Paragraph("SUCCESS METRICS", heading_style))
            
            success_data = [["Metric", "Score", "Level"]]
            success_data.extend([
                ["Success Potential", f"{self.results['success_potential']:.2f}", self.results['success_potential_level']],
                ["Mastery Trajectory", f"{self.results['mastery_trajectory']:.2f}", self.results['development_stage']],
                ["Momentum Score", f"{self.results['momentum_score']:.2f}", ""],
                ["Five-Year Projection", f"{self.results['five_year_projection']:.2f}", ""]
            ])
            
            success_table = Table(success_data, colWidths=[200, 100, 200])
            success_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
            ]))
            content.append(success_table)
            content.append(Spacer(1, 15))
            
            content.append(Paragraph("PERSONALITY PROFILE", heading_style))
            content.append(Paragraph(f"Primary Type: {self.results['primary_type']}", subheading_style))
            content.append(Paragraph(self.PERSONALITY_TYPES[self.results['primary_type']]['description'], styles['Normal']))
            content.append(Paragraph(f"Primary Badge Link:", subheading_style))
            content.append(Paragraph(self.PERSONALITY_TYPES[self.results['primary_type']]['link'], styles['Normal']))
            content.append(Spacer(1, 10))
            content.append(Paragraph(f"Secondary Type: {self.results['secondary_type']}", subheading_style))
            content.append(Paragraph(self.PERSONALITY_TYPES[self.results['secondary_type']]['description'], styles['Normal']))
            content.append(Paragraph(f"Secondary Badge Link:", subheading_style))
            content.append(Paragraph(self.PERSONALITY_TYPES[self.results['secondary_type']]['link'], styles['Normal']))
            content.append(Spacer(1, 15))
            
            content.append(Paragraph("STRENGTHS AND CHALLENGES", heading_style))
            
            content.append(Paragraph("Top Strengths:", subheading_style))
            strengths_list = ""
            for strength in self.results['primary_strengths']:
                strengths_list += f"• {strength}<br/>"
            content.append(Paragraph(strengths_list, styles['Normal']))
            content.append(Spacer(1, 10))
            
            content.append(Paragraph("Primary Challenges:", subheading_style))
            challenges_list = ""
            for challenge in self.results['primary_challenges']:
                challenges_list += f"• {challenge}<br/>"
            content.append(Paragraph(challenges_list, styles['Normal']))
            content.append(Spacer(1, 15))
            
            content.append(Paragraph("RECOMMENDATIONS", heading_style))
            
            content.append(Paragraph("Recommended Focus Areas:", subheading_style))
            focus_list = ""
            for area in self.results['recommended_focus_areas']:
                focus_list += f"• {area}<br/>"
            content.append(Paragraph(focus_list, styles['Normal']))
            content.append(Spacer(1, 10))
            
            content.append(Paragraph("Requirements for Next Level:", subheading_style))
            requirements_list = ""
            for requirement, description in self.results['next_level_requirements'].items():
                requirements_list += f"• <b>{requirement}</b>: {description}<br/>"
            content.append(Paragraph(requirements_list, styles['Normal']))
            
            doc.build(content)
            print(f"\n{Fore.GREEN}PDF report saved to {filename}{Style.RESET_ALL}")
            return True
        except Exception as e:
            print(f"\n{Fore.RED}Error creating PDF report: {e}{Style.RESET_ALL}")
            return False

def take_quiz():
    """Function to initialize the calculator and execute the quiz."""
    calculator = ToughnessSuccessCalculator()
    user_data = calculator.take_assessment()
    results = calculator.calculate_results()
    calculator.display_results()

    save_choice = input("\nWould you like to save the results to a file? (yes/no): ").strip().lower()
    if save_choice in ['yes', 'y']:
        calculator.save_results()

    export_choice = input("\nWould you like to export the results to a PDF? (yes/no): ").strip().lower()
    if export_choice in ['yes', 'y']:
        calculator.export_pdf_report()