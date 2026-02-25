"""
Management command to seed the database with sample data.
Run: python manage.py seed_data

This creates:
- Sample opportunities from various Ivy League universities
- Domain groups for the community
- A demo admin user
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = 'Seed database with sample opportunities, groups, and a demo admin'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding database...')

        # ── Create admin user ──────────────────────────────────────
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser('admin', 'admin@ivy.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('  ✓ Admin user: admin / admin123'))
        else:
            self.stdout.write('  - Admin already exists')

        # ── Create demo student user ───────────────────────────────
        if not User.objects.filter(username='student1').exists():
            student = User.objects.create_user('student1', 'student1@lpu.edu', 'student123',
                                               first_name='Arjun', last_name='Sharma')
            profile = student.studentprofile
            profile.university = 'Lovely Professional University'
            profile.year_of_study = '3'
            profile.cgpa = 8.5
            profile.bio = 'Passionate about AI and machine learning. Looking for research opportunities.'
            profile.domains_of_interest = ['AI', 'CS']
            profile.skills = ['Python', 'Machine Learning', 'Django', 'TensorFlow']
            profile.save()
            self.stdout.write(self.style.SUCCESS('  ✓ Student user: student1 / student123'))

        # ── Create sample opportunities ────────────────────────────
        from apps.opportunities.models import Opportunity

        sample_opportunities = [
            {
                'title': 'Harvard Summer Research Program in Artificial Intelligence',
                'university': 'HARVARD',
                'domain': 'AI',
                'opportunity_type': 'INTERNSHIP',
                'description': 'Join Harvard\'s SEAS AI Lab for a 10-week summer research program. Work alongside faculty and PhD students on cutting-edge machine learning projects. Topics include deep learning, natural language processing, and computer vision.',
                'deadline': date.today() + timedelta(days=45),
                'source_url': 'https://seas.harvard.edu/research/ai-summer-2025',
                'location': 'Cambridge, MA',
                'stipend': '$4,000/month',
                'tags': 'AI, Machine Learning, Research, Summer Program',
            },
            {
                'title': 'MIT HackMIT 2025 — Annual Hackathon',
                'university': 'MIT',
                'domain': 'CS',
                'opportunity_type': 'HACKATHON',
                'description': 'HackMIT is MIT\'s annual hackathon bringing together over 1,000 students from around the world. 24 hours to build something amazing. Prizes include internship offers, cash, and hardware.',
                'deadline': date.today() + timedelta(days=30),
                'source_url': 'https://hackmit.org/2025',
                'location': 'Cambridge, MA',
                'stipend': 'Travel grants available',
                'tags': 'Hackathon, Programming, Innovation',
            },
            {
                'title': 'Yale Law School International Law Fellowship',
                'university': 'YALE',
                'domain': 'LAW',
                'opportunity_type': 'FELLOWSHIP',
                'description': 'The Yale Law School International Law Fellowship supports outstanding students to pursue research in international law, human rights, and global governance. Fellows receive a full stipend and mentorship from Yale faculty.',
                'deadline': date.today() + timedelta(days=60),
                'source_url': 'https://law.yale.edu/fellowships/international',
                'location': 'New Haven, CT',
                'stipend': '$6,000/month',
                'tags': 'Law, International Law, Fellowship, Human Rights',
            },
            {
                'title': 'Stanford Biomedical Engineering Research Internship',
                'university': 'STANFORD',
                'domain': 'BIO',
                'opportunity_type': 'INTERNSHIP',
                'description': 'Work in Stanford\'s biomedical engineering labs on projects spanning drug delivery systems, medical imaging, and tissue engineering. Open to undergraduate and graduate students with a strong background in biology and engineering.',
                'deadline': date.today() + timedelta(days=25),
                'source_url': 'https://bioengineering.stanford.edu/research/internships',
                'location': 'Stanford, CA',
                'stipend': '$3,500/month',
                'tags': 'Biomedical, Engineering, Research, Healthcare',
            },
            {
                'title': 'Princeton AI Policy Workshop',
                'university': 'PRINCETON',
                'domain': 'AI',
                'opportunity_type': 'WORKSHOP',
                'description': 'A 3-day intensive workshop at Princeton\'s Center for Information Technology Policy (CITP). Explore the intersection of AI, ethics, and public policy. Participants from CS, Law, Economics, and Social Sciences are welcome.',
                'deadline': date.today() + timedelta(days=15),
                'source_url': 'https://citp.princeton.edu/workshop/ai-policy-2025',
                'location': 'Princeton, NJ',
                'stipend': 'Travel support provided',
                'tags': 'AI, Policy, Workshop, Ethics',
            },
            {
                'title': 'Columbia University Medical Research Scholarship',
                'university': 'COLUMBIA',
                'domain': 'BIO',
                'opportunity_type': 'SCHOLARSHIP',
                'description': 'The Columbia Medical Research Scholarship supports undergraduate students from underrepresented backgrounds to pursue medical research. Recipients receive tuition support, lab access, and a $2,000 monthly stipend for 12 months.',
                'deadline': date.today() + timedelta(days=50),
                'source_url': 'https://medicine.columbia.edu/scholarships/research-2025',
                'location': 'New York, NY',
                'stipend': '$2,000/month + tuition',
                'tags': 'Medical, Scholarship, Research, Healthcare',
            },
            {
                'title': 'Cornell Tech Startup Competition — $100K Prize',
                'university': 'CORNELL',
                'domain': 'BUSINESS',
                'opportunity_type': 'COMPETITION',
                'description': 'Cornell Tech\'s annual startup pitch competition. Teams of 2-4 students pitch their startup idea to a panel of VCs and industry experts. The winning team receives $100,000 in seed funding and 6 months of mentorship.',
                'deadline': date.today() + timedelta(days=40),
                'source_url': 'https://tech.cornell.edu/startup-competition-2025',
                'location': 'New York City, NY / Remote',
                'stipend': '$100,000 prize',
                'tags': 'Startup, Entrepreneurship, Competition, Business',
            },
            {
                'title': 'Harvard Environmental Sciences Summer Institute',
                'university': 'HARVARD',
                'domain': 'ENV',
                'opportunity_type': 'WORKSHOP',
                'description': 'An 8-week summer institute exploring climate change science, environmental policy, and sustainability engineering. Lectures by leading Harvard faculty, field trips, and a research project.',
                'deadline': date.today() + timedelta(days=35),
                'source_url': 'https://environment.harvard.edu/summer-institute-2025',
                'location': 'Cambridge, MA',
                'stipend': 'Merit scholarships available',
                'tags': 'Environment, Climate Change, Research, Summer',
            },
            {
                'title': 'MIT EECS Research Internship Program (UROP)',
                'university': 'MIT',
                'domain': 'ECE',
                'opportunity_type': 'INTERNSHIP',
                'description': 'MIT\'s Undergraduate Research Opportunities Program (UROP) in EECS. Work on projects in quantum computing, photonics, signal processing, and embedded systems with MIT professors.',
                'deadline': date.today() + timedelta(days=20),
                'source_url': 'https://urop.mit.edu/eecs-2025',
                'location': 'Cambridge, MA',
                'stipend': '$18/hour',
                'tags': 'ECE, Electronics, Research, UROP',
            },
            {
                'title': 'Dartmouth NLP and Computational Linguistics Conference',
                'university': 'DARTMOUTH',
                'domain': 'AI',
                'opportunity_type': 'CONFERENCE',
                'description': 'Present your research in NLP, computational linguistics, or human-computer interaction at this selective student research conference hosted by Dartmouth. Travel grants available for accepted presenters.',
                'deadline': date.today() + timedelta(days=55),
                'source_url': 'https://nlp.dartmouth.edu/conference-2025',
                'location': 'Hanover, NH',
                'stipend': 'Travel grants for presenters',
                'tags': 'NLP, AI, Conference, Research',
            },
            {
                'title': 'Brown University AI in Healthcare Hackathon',
                'university': 'BROWN',
                'domain': 'AI',
                'opportunity_type': 'HACKATHON',
                'description': 'Build AI solutions for healthcare challenges in this 48-hour hackathon at Brown University. Partner hospitals provide real datasets. Winners get internship interviews at Partner health systems.',
                'deadline': date.today() + timedelta(days=28),
                'source_url': 'https://brown.edu/ai-healthcare-hackathon-2025',
                'location': 'Providence, RI',
                'stipend': 'Prize pool $25,000',
                'tags': 'AI, Healthcare, Hackathon, Innovation',
            },
            {
                'title': 'Penn Wharton Social Impact Scholarship',
                'university': 'PENN',
                'domain': 'BUSINESS',
                'opportunity_type': 'SCHOLARSHIP',
                'description': 'The Wharton Social Impact Scholarship supports students passionate about using business for social good. Recipients participate in the Wharton Social Impact Initiative and receive $5,000.',
                'deadline': date.today() + timedelta(days=42),
                'source_url': 'https://socialimpact.wharton.upenn.edu/scholarship',
                'location': 'Philadelphia, PA',
                'stipend': '$5,000',
                'tags': 'Business, Social Impact, Scholarship, Leadership',
            },
        ]

        created_count = 0
        for opp_data in sample_opportunities:
            obj, created = Opportunity.objects.get_or_create(
                source_url=opp_data['source_url'],
                defaults=opp_data
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {created_count} sample opportunities'))

        # ── Create Domain Groups ───────────────────────────────────
        from apps.community.models import DomainGroup

        groups_data = [
            {'name': 'AI Research Circle', 'domain': 'AI', 'description': 'Connect with AI/ML researchers, share papers, discuss projects, and find collaborators.'},
            {'name': 'Law Society Network', 'domain': 'LAW', 'description': 'For aspiring lawyers and policy professionals. Discuss cases, opportunities, and legal developments.'},
            {'name': 'Biomedical Innovators', 'domain': 'BIO', 'description': 'Healthcare and biomedical engineering students. Share research, lab tips, and career advice.'},
            {'name': 'ECE Technical Hub', 'domain': 'ECE', 'description': 'Electronics, circuits, embedded systems, and signal processing enthusiasts.'},
            {'name': 'Computer Science Guild', 'domain': 'CS', 'description': 'Software engineering, algorithms, cybersecurity, and systems. Hackathon teams welcome!'},
            {'name': 'Business & Entrepreneurship Club', 'domain': 'BUSINESS', 'description': 'Connect founders, MBA aspirants, and business leaders. Share startup ideas and funding news.'},
            {'name': 'Environmental Action Group', 'domain': 'ENV', 'description': 'Climate change, sustainability, and environmental policy advocates.'},
        ]

        admin_user = User.objects.filter(is_superuser=True).first()
        group_count = 0
        for g in groups_data:
            obj, created = DomainGroup.objects.get_or_create(
                name=g['name'],
                defaults={**g, 'created_by': admin_user}
            )
            if created:
                group_count += 1

        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {group_count} domain groups'))

        # ── Train Classifier ──────────────────────────────────────
        self.stdout.write('  Training AI domain classifier...')
        from apps.opportunities.classifier import train_model
        success = train_model()
        if success:
            self.stdout.write(self.style.SUCCESS('  ✓ Classifier trained'))
        else:
            self.stdout.write(self.style.WARNING('  ⚠ Classifier training failed (check sklearn install)'))

        self.stdout.write(self.style.SUCCESS('\n✅ Database seeded successfully!'))
        self.stdout.write('\nLogin credentials:')
        self.stdout.write('  Admin:   admin / admin123')
        self.stdout.write('  Student: student1 / student123')
        self.stdout.write('\nRun the server: python manage.py runserver')
