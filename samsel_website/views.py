from samsel_website.models import School, Books, Purchase, PurchaseItems
import json
import os
from django.conf import settings
from django.shortcuts import render , redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from .services.paper_generator import generate_question_paper
from django.http import HttpResponse
from django.template.loader import render_to_string
#from xhtml2pdf import pisa
from django.template.loader import get_template
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import connection
import uuid
from datetime import date, timedelta


from samsel_project.settings import EMAIL_HOST_USER
from functools import wraps

def super_admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('is_super_admin', False):
            return redirect('super_admin_login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def our_story(request):
    return render(request, 'our_story.html')

def request_demo_page(request):
    return render(request, 'request_demo.html')



from .models import School, Purchase

def school_login(request):
    if request.method == "POST":
        school_name = request.POST.get("school_name", "").strip()
        school_id = request.POST.get("school_id", "").strip()
        password = request.POST.get("password", "")

        try:
            school = School.objects.get(school_id=school_id, school_name__iexact=school_name)
            if school.password_hash == password:
                request.session['school_id'] = school.school_id
                return redirect('school_dashboard')
            else:
                return render(request, 'school_login.html', {"error": "Invalid Password"})
        except School.DoesNotExist:
            return render(request, 'school_login.html', {"error": "Invalid School Name or School ID"})

    return render(request, 'school_login.html')

def school_dashboard(request):
    school_id = request.session.get('school_id')
    if not school_id:
        return redirect('school_login')
    
    try:
        school = School.objects.get(school_id=school_id)
        
        # Fetch purchases and group by series for Profile
        from .models import PurchaseItems
        from datetime import date
        purchases = PurchaseItems.objects.filter(
            purchase__school=school,
            valid_upto__gte=date.today(),
            sent_to_school=True
        ).select_related('book')
        grouped_books = {}
        for p in purchases:
            if not p.book: continue
            series = p.book.series_name
            cls = p.book.class_field
            if series not in grouped_books:
                grouped_books[series] = []
            grouped_books[series].append(cls)
        
        books_data = []
        for series, classes in grouped_books.items():
            books_data.append({
                'series': series,
                'class_num': ", ".join(sorted(list(set(classes))))
            })
            
        # Specific list for E-books section
        ebooks_list = []
        seen_books = set()
        for p in purchases:
            if p.book and p.book.path:
                book_key = f"{p.book.series_name} - Class {p.book.class_field}"
                if book_key not in seen_books:
                    seen_books.add(book_key)
                    ebooks_list.append({
                        'title': book_key,
                        'view_url': p.book.path
                    })

        context = {
            'school': school,
            'books': books_data,
            'ebooks': ebooks_list
        }
        
        return render(request, 'school_dashboard.html', context)
        
    except School.DoesNotExist:
        return redirect('school_login')

def school_logout(request):
    request.session.flush()
    return redirect('school_login')

def student_login(request):
    return render(request, 'student_login.html')

def contact(request):
    return render(request, 'contact.html')

def products(request):
    return render(request, 'products.html')

# --- Product Data ---
BOOKS_DATA = {
    'ibot-series': {
        'title': 'I-BOT SERIES',
        'logo': 'images/ibotlogo.png',
        'tagline': 'Shaping Future Innovators in AI and Robotics',
        'description': "A comprehensive collection of 9 titles, the iBot series is designed to equip students with future-ready skills in AI, robotics, and programming. Covering the latest AI and robotics syllabus, the series also introduces core programming concepts in C, C++, HTML5, and Python, building a strong technical foundation for learners. For higher classes, students explore advanced topics such as cybersecurity, emerging technologies, wireless networking, and IoT, helping them stay aligned with the evolving digital world. At the primary level, the series focuses on strengthening logical thinking through algorithms, flowcharts, and hands-on coding using ScratchJr and Scratch 3.0. With a well-structured, progressive approach, the iBot series ensures a seamless learning journey to empower students at every stage to understand, apply, and excel in AI, robotics, and programming languages.",
        'bullets': [
            "A comprehensive collection of 9 titles, the iBot series is designed to equip students with future-ready skills in AI, robotics, and programming.",
            "Covering the latest AI and robotics syllabus, the series also introduces core programming concepts in C, C++, HTML5, and Python, building a strong technical foundation for learners.",
            "For higher classes, students explore advanced topics such as cybersecurity, emerging technologies, wireless networking, and IoT, helping them stay aligned with the evolving digital world.",
            "At the primary level, the series focuses on strengthening logical thinking through algorithms, flowcharts, and hands-on coding using ScratchJr and Scratch 3.0.",
            "With a well-structured, progressive approach, the iBot series ensures a seamless learning journey to empower students at every stage to understand, apply, and excel in AI, robotics, and programming languages."
        ],
        'books': {
            'class-1': {'title': 'i-Bot Class 1', 'image': 'images/ibot1.jpg', 'desc': 'Introduces young learners to smart machines, basic computer parts, and early coding concepts using ScratchJr.', 'details': ['Introduces young learners to smart machines, basic computer parts, and early coding concepts using ScratchJr.', 'Build a strong foundation in this topic, ideal for real-world application and academic excellence.']},
            'class-2': {'title': 'i-Bot Class 2', 'image': 'images/ibot2.jpg', 'desc': 'Building on basics, exploring input/output devices, and intermediate creative projects.', 'details': ['Building on basics, exploring input/output devices, and intermediate creative projects.', 'Empower students with practical skills in this topic, designed to foster creativity and logical thinking.']},
            'class-3': {'title': 'i-Bot Class 3', 'image': 'images/ibot3.jpg', 'desc': 'Understanding OS environments, word processing, and an introduction to computational thinking.', 'details': ['Understanding OS environments, word processing, and an introduction to computational thinking.', 'Empower students with practical skills in this topic, perfect for building modern digital fluency.']},
            'class-4': {'title': 'i-Bot Class 4', 'image': 'images/ibot4.jpg', 'desc': 'Advanced word processing, safe internet browsing, and block-based programming exercises.', 'details': ['Advanced word processing, safe internet browsing, and block-based programming exercises.', 'Empower students with practical skills in this topic, equipping students with tools for future success.']},
            'class-5': {'title': 'i-Bot Class 5', 'image': 'images/ibot5.jpg', 'desc': 'Presentations, spreadsheets basics, and developing algorithms using visual coding tools.', 'details': ['Presentations, spreadsheets basics, and developing algorithms using visual coding tools.', 'Interactive, hands-on activities covering this topic, encouraging problem-solving and critical reasoning.']},
            'class-6': {'title': 'i-Bot Class 6', 'image': 'images/ibot6.jpg', 'desc': 'Deep dive into robotics principles, electronics basics, and intro to Python syntax.', 'details': ['Deep dive into robotics principles, electronics basics, and intro to Python syntax.', 'Step-by-step guidance on this topic, equipping students with tools for future success.']},
            'class-7': {'title': 'i-Bot Class 7', 'image': 'images/ibot7.jpg', 'desc': 'AI concepts, intermediate Python programming, and hardware integration projects.', 'details': ['AI concepts, intermediate Python programming, and hardware integration projects.', 'Comprehensive coverage of this topic, designed to foster creativity and logical thinking.']},
            'class-8': {'title': 'i-Bot Class 8', 'image': 'images/ibot8.jpg', 'desc': 'Advanced robotics, IoT fundamentals, and machine learning basics.', 'details': ['Advanced robotics, IoT fundamentals, and machine learning basics.', 'Engaging lessons tailored for this topic, encouraging problem-solving and critical reasoning.']},
            'class-9': {'title': 'i-Bot Class 9', 'image': 'images/ibot9.jpg', 'desc': 'Comprehensive IT matrix, app development, and specialized AI/ML problem solving.', 'details': ['Comprehensive IT matrix, app development, and specialized AI/ML problem solving.', 'Build a strong foundation in this topic, creating an enjoyable and engaging learning environment.']},
        }
    },
    'ismart-series': {
        'title': 'I-SMART SERIES',
        'logo': 'images/iSmart Logo.png',
        'tagline': 'Smart Learning for a Digital Generation',
        'description': 'The i-Smart Series is a thoughtfully designed collection of 9 course titles that introduces students to a modern, tech-driven, and academic curriculum.\n\nAt the primary level, learners build strong fundamentals through topics such as Windows 10, MS Paint, Logo Programming, and Microsoft Office tools (Word, PowerPoint, and Excel 2010).\n\nAs students progress to higher grades, the series expands into advanced concepts, including HTML, C++ programming, JavaScript, MySQL, and Python, equipping them with essential coding and digital skills.\n\nWhat sets the i-Smart Series apart is its learner-friendly approach, featuring "Hint" sections and interactive "Do You Know?" and "Do It Yourself (DIY)" activities designed to reinforce understanding through practical application.\n\nWith a structured and progressive learning path, the i-Smart Series empowers students to build confidence, think logically, and stay ahead in today’s digital world.',
        'bullets': [
            'The i-Smart Series is a thoughtfully designed collection of 9 course titles that introduces students to a modern, tech-driven, and academic curriculum.',
            'At the primary level, learners build strong fundamentals through topics such as Windows 10, MS Paint, Logo Programming, and Microsoft Office tools (Word, PowerPoint, and Excel 2010).',
            'As students progress to higher grades, the series expands into advanced concepts, including HTML, C++ programming, JavaScript, MySQL, and Python, equipping them with essential coding and digital skills.',
            'What sets the i-Smart Series apart is its learner-friendly approach, featuring "Hint" sections and interactive "Do You Know?" and "Do It Yourself (DIY)" activities designed to reinforce understanding through practical application.',
            'With a structured and progressive learning path, the i-Smart Series empowers students to build confidence, think logically, and stay ahead in today’s digital world.'
        ],
        'books': {
            'level-1': {'title': 'ISMART Level 1', 'image': 'images/ism1.jpg', 'desc': 'Foundations of smart learning and digital literacy.', 'details': ['Foundations of smart learning and digital literacy.', 'A fun, comprehensive approach to this topic, helping learners grasp complex topics with ease.']},
            'level-2': {'title': 'ISMART Level 2', 'image': 'images/ism2.jpg', 'desc': 'Interactive exercises building core IT competencies.', 'details': ['Interactive exercises building core IT competencies.', 'Dive deep into this topic, perfect for building modern digital fluency.']},
            'level-3': {'title': 'ISMART Level 3', 'image': 'images/ism3.jpg', 'desc': 'Exploring creative software and basic problem solving.', 'details': ['Exploring creative software and basic problem solving.', 'Step-by-step guidance on this topic, perfect for building modern digital fluency.']},
            'level-4': {'title': 'ISMART Level 4', 'image': 'images/ism4.jpg', 'desc': 'Introduction to connected devices and cyber safety.', 'details': ['Introduction to connected devices and cyber safety.', 'Master the essentials of this topic, creating an enjoyable and engaging learning environment.']},
            'level-5': {'title': 'ISMART Level 5', 'image': 'images/ism5.jpg', 'desc': 'Advanced office tools and beginner coding loops.', 'details': ['Advanced office tools and beginner coding loops.', 'A fun, comprehensive approach to this topic, designed to foster creativity and logical thinking.']},
            'level-6': {'title': 'ISMART Level 6', 'image': 'images/ism6.jpg', 'desc': 'Structuring ideas and intermediate algorithmic logic.', 'details': ['Structuring ideas and intermediate algorithmic logic.', 'Empower students with practical skills in this topic, ideal for real-world application and academic excellence.']},
            'level-7': {'title': 'ISMART Level 7', 'image': 'images/ism7.jpg', 'desc': 'Web technologies and introductory networking.', 'details': ['Web technologies and introductory networking.', 'Step-by-step guidance on this topic, designed to foster creativity and logical thinking.']},
            'level-8': {'title': 'ISMART Level 8', 'image': 'images/ism8.jpg', 'desc': 'Data handling, analysis, and programming constructs.', 'details': ['Data handling, analysis, and programming constructs.', 'Comprehensive coverage of this topic, encouraging problem-solving and critical reasoning.']},
            'level-9': {'title': 'ISMART Level 9', 'image': 'images/ism9.jpg', 'desc': 'Comprehensive system design and applied technology projects.', 'details': ['Comprehensive system design and applied technology projects.', 'Dive deep into this topic, perfect for building modern digital fluency.']},
        }
    },
    'iwhizz-series': {
        'title': 'I-WHIZZ SERIES',
        'logo': 'images/iWhizz Logo.png',
        'tagline': 'Accelerating Skills for a Tech-Driven World',
        'description': 'The i-Whizz Series features a collection of 9 courses, designed to build strong technical foundations across different grade levels.\n\nStudents begin with essential concepts such as computer fundamentals, Windows 7 OS, and the Office 2007 Suite, gaining a solid understanding of everyday digital tools.\n\nAs they progress, learners explore creative and technical skills through hands-on exposure to Photoshop, along with foundational programming in C and HTML.\n\nWith a structured, level-based approach, the i-Whizz Series helps students gradually develop practical knowledge, technical confidence, and the skills needed to thrive in a digital-first environment.',
        'bullets': [
            'The i-Whizz Series features a collection of 9 courses, designed to build strong technical foundations across different grade levels.',
            'Students begin with essential concepts such as computer fundamentals, Windows 7 OS, and the Office 2007 Suite, gaining a solid understanding of everyday digital tools.',
            'As they progress, learners explore creative and technical skills through hands-on exposure to Photoshop, along with foundational programming in C and HTML.',
            'With a structured, level-based approach, the i-Whizz Series helps students gradually develop practical knowledge, technical confidence, and the skills needed to thrive in a digital-first environment.'
        ],
        'books': {
            'class-1': {'title': 'i-Whizz Class 1', 'image': 'images/iwhizz1.jpg', 'desc': 'Early steps into the world of tech and logic.', 'details': ['Early steps into the world of tech and logic.', 'A fun, comprehensive approach to this topic, designed to foster creativity and logical thinking.']},
            'class-2': {'title': 'i-Whizz Class 2', 'image': 'images/iwhizz2.jpg', 'desc': 'Building foundational computer operation skills.', 'details': ['Building foundational computer operation skills.', 'Step-by-step guidance on this topic, equipping students with tools for future success.']},
            'class-3': {'title': 'i-Whizz Class 3', 'image': 'images/iwhizz3.jpg', 'desc': 'Logical puzzles and introducing digital creativity.', 'details': ['Logical puzzles and introducing digital creativity.', 'Master the essentials of this topic, equipping students with tools for future success.']},
            'class-4': {'title': 'i-Whizz Class 4', 'image': 'images/iwhizz4.jpg', 'desc': 'Word processing and exploring the internet safely.', 'details': ['Word processing and exploring the internet safely.', 'Dive deep into this topic, ensuring students stay ahead in today\'s tech-driven landscape.']},
            'class-5': {'title': 'i-Whizz Class 5', 'image': 'images/iwhizz5.jpg', 'desc': 'Presentation tools and beginning programming principles.', 'details': ['Presentation tools and beginning programming principles.', 'Build a strong foundation in this topic, designed to foster creativity and logical thinking.']},
            'class-6': {'title': 'i-Whizz Class 6', 'image': 'images/iwhizz6.jpg', 'desc': 'Deeper dive into software apps and coding techniques.', 'details': ['Deeper dive into software apps and coding techniques.', 'Empower students with practical skills in this topic, ensuring students stay ahead in today\'s tech-driven landscape.']},
            'class-7': {'title': 'i-Whizz Class 7', 'image': 'images/iwhizz7.jpg', 'desc': 'Advanced digital tools and structured logic building.', 'details': ['Advanced digital tools and structured logic building.', 'Interactive, hands-on activities covering this topic, ideal for real-world application and academic excellence.']},
            'class-8': {'title': 'i-Whizz Class 8', 'image': 'images/iwhizz8.jpg', 'desc': 'Web design basics and advanced conceptual frameworks.', 'details': ['Web design basics and advanced conceptual frameworks.', 'Interactive, hands-on activities covering this topic, perfect for building modern digital fluency.']},
            'class-9': {'title': 'i-Whizz Class 9', 'image': 'images/iwhizz9.jpg', 'desc': 'Comprehensive studies in modern computing architectures.', 'details': ['Comprehensive studies in modern computing architectures.', 'Step-by-step guidance on this topic, equipping students with tools for future success.']},
        }
    },
    'young-wizard-series': {
        'title': 'YOUNG WIZARD SERIES',
        'logo': 'images/younglogo.jpg',
        'tagline': 'Where Young Minds Learn, Create, and Explore',
        'description': 'The Young Wizard Series is a vibrant collection of 5 course titles, specially designed for primary learners across Levels 1 to 5.\n\nWith its colorful, activity-based approach, the series makes learning fun and engaging while building strong digital foundations. Students are introduced to essential concepts such as the Windows 7 operating system, MS Word 2007, and Paint, along with basic graphical and animation skills.\n\nAs learners progress, they gain hands-on experience in working across platforms, exploring multimedia tools, internet browsing, and creative applications like SwishMax and Macromedia Flash.\n\nBlending creativity with technology, the Young Wizard Series offers a well-rounded digital-first learning experience, helping young minds develop confidence, curiosity, and essential computer skills from an early age.',
        'bullets': [
            'The Young Wizard Series is a vibrant collection of 5 course titles, specially designed for primary learners across Levels 1 to 5.',
            'With its colorful, activity-based approach, the series makes learning fun and engaging while building strong digital foundations. Students are introduced to essential concepts such as the Windows 7 operating system, MS Word 2007, and Paint, along with basic graphical and animation skills.',
            'As learners progress, they gain hands-on experience in working across platforms, exploring multimedia tools, internet browsing, and creative applications like SwishMax and Macromedia Flash.',
            'Blending creativity with technology, the Young Wizard Series offers a well-rounded digital-first learning experience, helping young minds develop confidence, curiosity, and essential computer skills from an early age.'
        ],
        'books': {
            'level-1': {'title': 'Young Wizard Level 1', 'image': 'images/young1.jpg', 'desc': 'Magical introduction to computers.', 'details': ['Magical introduction to computers.', 'Master the essentials of this topic, equipping students with tools for future success.']},
            'level-2': {'title': 'Young Wizard Level 2', 'image': 'images/young2.jpg', 'desc': 'Exploring creative tech tools.', 'details': ['Exploring creative tech tools.', 'Build a strong foundation in this topic, helping learners grasp complex topics with ease.']},
            'level-3': {'title': 'Young Wizard Level 3', 'image': 'images/young3.jpg', 'desc': 'Building logic through fun exercises.', 'details': ['Building logic through fun exercises.', 'A fun, comprehensive approach to this topic, ideal for real-world application and academic excellence.']},
            'level-4': {'title': 'Young Wizard Level 4', 'image': 'images/young4.jpg', 'desc': 'Intermediate magical computing tasks.', 'details': ['Intermediate magical computing tasks.', 'Engaging lessons tailored for this topic, encouraging problem-solving and critical reasoning.']},
            'level-5': {'title': 'Young Wizard Level 5', 'image': 'images/young5.jpg', 'desc': 'Advanced puzzles and digital mastery.', 'details': ['Advanced puzzles and digital mastery.', 'Comprehensive coverage of this topic, creating an enjoyable and engaging learning environment.']},
        }
    },
    'little-wizard-series': {
        'title': 'LITTLE WIZARD SERIES',
        'logo': 'images/little wizard series.png',
        'tagline': 'First Steps into the Digital World.',
        'description': 'The Little Wizard Series has been specially designed for early learners, featuring 2 course levels tailored for KG students.\n\nCreated to support teachers, students, and parents, the series delivers an interactive, fun, and engaging digital-first learning experience. With a focus on simple concepts and hands-on activities, it introduces young minds to the basics of technology in an enjoyable and accessible way.\n\nBlending learning with play, the Little Wizard Series offers a well-rounded foundation through practical exposure and engaging content, helping children take their first confident steps into the digital world.',
        'bullets': [
            'The Little Wizard Series has been specially designed for early learners, featuring 2 course levels tailored for KG students.',
            'Created to support teachers, students, and parents, the series delivers an interactive, fun, and engaging digital-first learning experience. With a focus on simple concepts and hands-on activities, it introduces young minds to the basics of technology in an enjoyable and accessible way.',
            'Blending learning with play, the Little Wizard Series offers a well-rounded foundation through practical exposure and engaging content, helping children take their first confident steps into the digital world.'
        ],
        'books': {
            'level-1': {'title': 'Little Wizard Level 1', 'image': 'images/Kids level 1 wrapper.jpg', 'desc': 'Colorful shapes and mouse control.', 'details': ['Colorful shapes and mouse control.', 'Interactive, hands-on activities covering this topic, creating an enjoyable and engaging learning environment.']},
            'level-2': {'title': 'Little Wizard Level 2', 'image': 'images/Kids level 2 wrapper.jpg', 'desc': 'Typing games and early logic.', 'details': ['Typing games and early logic.', 'Interactive, hands-on activities covering this topic, ensuring students stay ahead in today\'s tech-driven landscape.']},
        }
    },
    'app2016-series': {
        'title': 'APPLICATION SERIES 2016',
        'logo': 'images/NEW APPLICATION SERIES.png',
        'tagline': 'From Basics to Brilliance in Office Tools. Learn. Apply. Excel.',
        'description': 'Designed to build practical digital skills, the Application Series 2016 offers an in-depth understanding of widely used application tools such as Microsoft Word, Excel, and PowerPoint 2016.\n\nEach application is explored individually through real-world illustrations and hands-on practice activities, making it easier for learners to grasp concepts and apply them confidently.\n\nThe series also provides strong conceptual coverage of MS Office tools, including Word, Excel, PowerPoint, and Access (2007 editions), ensuring a well-rounded foundation in productivity software.\n\nWith a structured and practical approach, this series helps learners develop both technical proficiency and real-world application skills essential for academic and professional success.',
        'bullets': [
            'Designed to build practical digital skills, the Application Series 2016 offers an in-depth understanding of widely used application tools such as Microsoft Word, Excel, and PowerPoint 2016.',
            'Each application is explored individually through real-world illustrations and hands-on practice activities, making it easier for learners to grasp concepts and apply them confidently.',
            'The series also provides strong conceptual coverage of MS Office tools, including Word, Excel, PowerPoint, and Access (2007 editions), ensuring a well-rounded foundation in productivity software.',
            'With a structured and practical approach, this series helps learners develop both technical proficiency and real-world application skills essential for academic and professional success.'
        ],
        'books': {
            'word': {'title': 'Word 2016', 'image': 'images/2016 word.png', 'desc': 'Professional document creation and formatting.', 'details': ['Professional document creation and formatting.', 'Dive deep into this topic, ensuring students stay ahead in today\'s tech-driven landscape.']},
            'excel': {'title': 'Excel 2016', 'image': 'images/2016 excel.png', 'desc': 'Data analysis, charting, and advanced functions.', 'details': ['Data analysis, charting, and advanced functions.', 'A fun, comprehensive approach to this topic, equipping students with tools for future success.']},
            'ppt': {'title': 'PowerPoint 2016', 'image': 'images/2016 ppt.png', 'desc': 'Create stunning presentations with modern tools.', 'details': ['Create stunning presentations with modern tools.', 'A fun, comprehensive approach to this topic, ideal for real-world application and academic excellence.']},
        }
    },
    'app2007-series': {
        'title': 'APPLICATION SERIES 2007',
        'logo': 'images/NEW APPLICATION SERIES.png',
        'tagline': 'Comprehensive guide to the classic Office 2007 suite.',
        'description': 'The Application Series 2016 is designed to develop practical digital skills by offering a clear understanding of widely used tools like Microsoft Office, Word, Excel, PowerPoint, and Access.\n\nEach application is covered individually through real-world examples and hands-on exercises, helping learners grasp concepts easily and apply them with confidence. The series also builds a strong foundation in MS Office (including 2007 editions) with a structured, practical approach that supports both academic and professional success.',
        'books': {
            'office-2007': {'title': 'Office 2007', 'image': 'images/App4.jpg', 'desc': 'Foundations of Office 2007 applications.', 'details': ['Foundations of Office 2007 applications.', 'Master the essentials of this topic, ensuring students stay ahead in today\'s tech-driven landscape.']},
            'word-2007': {'title': 'Word 2007', 'image': 'images/App1.jpg', 'desc': 'Intermediate skills in Word and formatting.', 'details': ['Intermediate skills in Word formatting.', 'Dive deep into this topic, ensuring students stay ahead in today\'s tech-driven landscape.']},
            'excel-2007': {'title': 'Excel 2007', 'image': 'images/App3.jpg', 'desc': 'Advanced formulas and spreadsheets.', 'details': ['Advanced formulas and spreadsheets.', 'Master the essentials of this topic, ideal for real-world application and academic excellence.']},
            'ppt-2007': {'title': 'PowerPoint 2007', 'image': 'images/App5.jpg', 'desc': 'Creating dynamic presentations.', 'details': ['Creating dynamic presentations.', 'Unlock your potential with this topic, ensuring students stay ahead in today\'s tech-driven landscape.']},
            'access-2007': {'title': 'Access 2007', 'image': 'images/App2.jpg', 'desc': 'Database management introduction.', 'details': ['Database management introduction.', 'Empower students with practical skills in this topic, designed to foster creativity and logical thinking.']},
        }
    },
    'programming-series': {
        'title': 'PROGRAMMING SERIES',
        'logo': 'images/programming series logo.jpeg',
        'tagline': 'Master the Code. Build the Future',
        'description': 'The Programming Series features a focused collection of single-color titles that’s designed to build strong programming fundamentals through hands-on learning.\n\nCovering key languages and tools such as HTML, Macromedia Flash, Microsoft Visual Basic, C, and C++, each book emphasizes practical exercises and real-world applications to help learners understand and apply concepts effectively.\n\nWith a clear, practice-driven approach, the series enables students to develop coding confidence and problem-solving skills essential for today’s digital landscape.',
        'bullets': [
            'The Programming Series features a focused collection of single-color titles that’s designed to build strong programming fundamentals through hands-on learning.',
            'Covering key languages and tools such as HTML, Macromedia Flash, Microsoft Visual Basic, C, and C++, each book emphasizes practical exercises and real-world applications to help learners understand and apply concepts effectively.',
            'With a clear, practice-driven approach, the series enables students to develop coding confidence and problem-solving skills essential for today’s digital landscape.'
        ],
        'books': {
            'level-1': {'title': 'Programming Level 1', 'image': 'images/Pro1 New.jpg', 'desc': 'The fundamentals of coding and syntax.', 'details': ['The fundamentals of coding and syntax.', 'Interactive, hands-on activities covering this topic, creating an enjoyable and engaging learning environment.']},
            'level-2': {'title': 'Programming Level 2', 'image': 'images/Pro2.jpg', 'desc': 'Data structures and algorithms introduction.', 'details': ['Data structures and algorithms introduction.', 'A fun, comprehensive approach to this topic, designed to foster creativity and logical thinking.']},
            'level-3': {'title': 'Programming Level 3', 'image': 'images/Pro3.jpg', 'desc': 'Object-oriented concepts and design.', 'details': ['Object-oriented concepts and design.', 'Engaging lessons tailored for this topic, encouraging problem-solving and critical reasoning.']},
            'level-4': {'title': 'Programming Level 4', 'image': 'images/Pro4 New.jpg', 'desc': 'Advanced applied programming techniques.', 'details': ['Advanced applied programming techniques.', 'Build a strong foundation in this topic, helping learners grasp complex topics with ease.']},
        }
    },
    'my-computer-series': {
        'title': 'MY COMPUTER SERIES',
        'logo': 'images/MyComputer Series (Grade).jpg',
        'tagline': 'Building Digital Foundations from Day One',
        'description': 'The My Computer Series is a thoughtfully designed set of 5 course titles for primary learners, covering Grades 1 to 5.\n\nWith vibrant visuals and activity-based workbooks, this series makes early computer learning fun, interactive, and easy to understand. Students are introduced to essential digital concepts, including the Windows operating system (with versions like XP) and its everyday applications.\n\nLearners also gain hands-on experience with tools such as MS Paint and WordPad and basic web design skill sets, helping them build confidence in using computers from an early stage.\n\nOver a strong focus on foundational skills and practical learning, the My Computer Series sets the stage for a smooth and engaging digital learning journey.',
        'bullets': [
            'The My Computer Series is a thoughtfully designed set of 5 course titles for primary learners, covering Grades 1 to 5.',
            'With vibrant visuals and activity-based workbooks, this series makes early computer learning fun, interactive, and easy to understand. Students are introduced to essential digital concepts, including the Windows operating system (with versions like XP) and its everyday applications.',
            'Learners also gain hands-on experience with tools such as MS Paint and WordPad and basic web design skill sets, helping them build confidence in using computers from an early stage.',
            'Over a strong focus on foundational skills and practical learning, the My Computer Series sets the stage for a smooth and engaging digital learning journey.'
        ],
        'books': {
            'level-1': {'title': 'My Computer Level 1', 'image': 'images/my1.jpg', 'desc': 'Exploring your first PC.', 'details': ['Exploring your first PC.', 'Unlock your potential with this topic, ensuring students stay ahead in today\'s tech-driven landscape.']},
            'level-2': {'title': 'My Computer Level 2', 'image': 'images/my2.jpg', 'desc': 'Handling files and folders safely.', 'details': ['Handling files and folders safely.', 'Unlock your potential with this topic, creating an enjoyable and engaging learning environment.']},
            'level-3': {'title': 'My Computer Level 3', 'image': 'images/my3.jpg', 'desc': 'Navigating operating systems.', 'details': ['Navigating operating systems.', 'Unlock your potential with this topic, encouraging problem-solving and critical reasoning.']},
            'level-4': {'title': 'My Computer Level 4', 'image': 'images/my4.jpg', 'desc': 'Settings, customization, and tools.', 'details': ['Settings, customization, and tools.', 'Interactive, hands-on activities covering this topic, encouraging problem-solving and critical reasoning.']},
            'level-5': {'title': 'My Computer Level 5', 'image': 'images/my5.jpg', 'desc': 'System maintenance and troubleshooting.', 'details': ['System maintenance and troubleshooting.', 'Master the essentials of this topic, ideal for real-world application and academic excellence.']},
        }
    },
    'right-click-series': {
        'title': 'RIGHT CLICK SERIES',
        'logo': 'images/right click series.png',
        'logo_margin': '0px',
        'tagline': 'Click into The World of ICT',
        'description': 'The Right Click Series is designed to build strong foundations in Information and Communication Technology (ICT) for students from Grades 3 to 9.\n\nCovering the Windows operating system, essential application tools, and key programming concepts, the series introduces learners to basic programming, Visual fundamentals, and practical IT applications.\n\nWith a structured, curriculum-aligned approach, the Right Click Series helps students develop essential digital skills, logical thinking, and real-world computer proficiency, preparing them for today’s technology-driven environment.',
        'bullets': [
            'The Right Click Series is designed to build strong foundations in Information and Communication Technology (ICT) for students from Grades 3 to 9.',
            'Covering the Windows operating system, essential application tools, and key programming concepts, the series introduces learners to basic programming, Visual fundamentals, and practical IT applications.',
            'With a structured, curriculum-aligned approach, the Right Click Series helps students develop essential digital skills, logical thinking, and real-world computer proficiency, preparing them for today’s technology-driven environment.'
        ],
        'books': {
            'level-6': {'title': 'i-ICT Level 6', 'image': 'images/ict6.jpg', 'desc': 'Information and Communication Tech basics.', 'details': ['Information and Communication Tech basics.', 'Step-by-step guidance on this topic, designed to foster creativity and logical thinking.']},
            'level-7': {'title': 'i-ICT Level 7', 'image': 'images/ict7.jpg', 'desc': 'Networks and data communication.', 'details': ['Networks and data communication.', 'Interactive, hands-on activities covering this topic, ideal for real-world application and academic excellence.']},
            'level-8': {'title': 'i-ICT Level 8', 'image': 'images/ict8.jpg', 'desc': 'Applied IT systems in the real world.', 'details': ['Applied IT systems in the real world.', 'Empower students with practical skills in this topic, encouraging problem-solving and critical reasoning.']},
            'level-9': {'title': 'i-ICT Level 9', 'image': 'images/ict9.jpg', 'desc': 'Comprehensive technology integration.', 'details': ['Comprehensive technology integration.', 'Dive deep into this topic, designed to foster creativity and logical thinking.']},
        }
    },
    'cursive-writing-books': {
        'title': 'MY FIRST STROKE SERIES',
        'logo': 'images/cursive writing.png',
        'tagline': 'Enriching Cursive Hands With Linguistic Differentiations. One Stroke at a Time.',
        'description': 'My First Stroke Series is a thoughtfully designed collection of 7 cursive writing books in English and Tamil, crafted for learners from LKG to Grade 5.\n\nWith a step-by-step approach, the series helps students develop clear, neat, and confident handwriting. It covers everything from lowercase and uppercase letters to word formation and sentence writing, inclusive of Tamil letters, in both short and long forms.\n\nThrough guided practice and structured exercises, the series builds strong writing habits—making learning cursive both effective and enjoyable for young learners.',
        'bullets': [
            'My First Stroke Series is a thoughtfully designed collection of 7 cursive writing books in English and Tamil, crafted for learners from LKG to Grade 5.',
            'With a step-by-step approach, the series helps students develop clear, neat, and confident handwriting. It covers everything from lowercase and uppercase letters to word formation and sentence writing, inclusive of Tamil letters, in both short and long forms.',
            'Through guided practice and structured exercises, the series builds strong writing habits—making learning cursive both effective and enjoyable for young learners.'
        ],
        'books': {
            'lkg': {'title': 'Cursive Writing LKG', 'image': 'images/cursive-lkg.jpg', 'desc': 'Introduction to strokes and basic patterns.', 'details': ['Introduction to strokes and basic patterns.', 'Build a strong foundation in this topic, equipping students with tools for future success.']},
            'ukg': {'title': 'Cursive Writing UKG', 'image': 'images/cursive-ukg.jpg', 'desc': 'Building letter forms and simple connections.', 'details': ['Building letter forms and simple connections.', 'Engaging lessons tailored for this topic, designed to foster creativity and logical thinking.']},
            'level-1': {'title': 'Cursive Writing Level 1', 'image': 'images/Level 1.jpg', 'desc': 'Fluid word formation and sentence structure.', 'details': ['Fluid word formation and sentence structure.', 'A fun, comprehensive approach to this topic, helping learners grasp complex topics with ease.']},
            'level-2': {'title': 'Cursive Writing Level 2', 'image': 'images/Level 2.jpg', 'desc': 'Advanced penmanship and consistent spacing.', 'details': ['Advanced penmanship and consistent spacing.', 'Interactive, hands-on activities covering this topic, ensuring students stay ahead in today\'s tech-driven landscape.']},
            'level-3': {'title': 'Cursive Writing Level 3', 'image': 'images/Level 3.jpg', 'desc': 'Perfecting the elegant cursive script.', 'details': ['Perfecting the elegant cursive script.', 'A fun, comprehensive approach to this topic, creating an enjoyable and engaging learning environment.']},
            'level-4': {'title': 'Cursive Writing Level 4', 'image': 'images/Level 4.jpg', 'desc': 'Creative writing in professional cursive.', 'details': ['Creative writing in professional cursive.', 'Build a strong foundation in this topic, perfect for building modern digital fluency.']},
            'level-5': {'title': 'Cursive Writing Level 5', 'image': 'images/Level 5.jpg', 'desc': 'Mastery of decorative and formal penmanship.', 'details': ['Mastery of decorative and formal penmanship.', 'A fun, comprehensive approach to this topic, helping learners grasp complex topics with ease.']},
        }
    },
    'tamil-writing-books': {
        'title': 'TAMIL COPY WRITING',
        'logo': 'images/my first.jpeg',
        'tagline': 'A beautiful journey into Tamil calligraphy and structured writing practice.',
        'description': 'At the basic level, Tamil copywriting books are often designed for students and beginners to learn letter formation, improve handwriting, and develop sentence construction skills. These books provide structured exercises that help readers practice Tamil scripts, join letters into words, and gradually build fluency in writing.\n\nOverall, Tamil copywriting books serve as a bridge between language proficiency and creative communication, enabling individuals to write effectively in Tamil—whether for education, storytelling, or business-driven content.',
        'books': {
            'level-1': {'title': 'Tamil Writing Level 1', 'image': 'images/tamil1.jpg', 'desc': 'Basic Tamil characters and stroke techniques.', 'details': ['Basic Tamil characters and stroke techniques.', 'Master the essentials of this topic, creating an enjoyable and engaging learning environment.']},
            'level-2': {'title': 'Tamil Writing Level 2', 'image': 'images/tamil2.jpg', 'desc': 'Building words and understanding letter structures.', 'details': ['Building words and understanding letter structures.', 'Build a strong foundation in this topic, designed to foster creativity and logical thinking.']},
            'level-3': {'title': 'Tamil Writing Level 3', 'image': 'images/tamil3.jpg', 'desc': 'Intermediate word formation and sentence patterns.', 'details': ['Intermediate word formation and sentence patterns.', 'Engaging lessons tailored for this topic, ensuring students stay ahead in today\'s tech-driven landscape.']},
            'level-4': {'title': 'Tamil Writing Level 4', 'image': 'images/tamil4.jpg', 'desc': 'Enhancing writing speed and letter consistency.', 'details': ['Enhancing writing speed and letter consistency.', 'Unlock your potential with this topic, encouraging problem-solving and critical reasoning.']},
            'level-5': {'title': 'Tamil Writing Level 5', 'image': 'images/tamil5.jpg', 'desc': 'Advanced copy writing and literary phrases.', 'details': ['Advanced copy writing and literary phrases.', 'A fun, comprehensive approach to this topic, equipping students with tools for future success.']},
            'level-6': {'title': 'Tamil Writing Level 6', 'image': 'images/tamil6.jpg', 'desc': 'Perfecting the flow of Tamil script.', 'details': ['Perfecting the flow of Tamil script.', 'A fun, comprehensive approach to this topic, encouraging problem-solving and critical reasoning.']},
            'level-7': {'title': 'Tamil Writing Level 7', 'image': 'images/tamil7.jpg', 'desc': 'Mastery of formal Tamil calligraphy.', 'details': ['Mastery of formal Tamil calligraphy.', 'Engaging lessons tailored for this topic, ideal for real-world application and academic excellence.']},
        }
    }
}

def series_detail(request, series_slug):
    series = BOOKS_DATA.get(series_slug)
    if not series:
        return redirect('products')
    
    context = {
        'series_slug': series_slug,
        'series': series,
    }
    return render(request, 'series_detail.html', context)

def book_detail(request, series_slug, book_slug):
    series = BOOKS_DATA.get(series_slug)
    if not series:
        return redirect('products')
    
    book = series['books'].get(book_slug)
    if not book:
        return redirect('series_detail', series_slug=series_slug)
    
    context = {
        'series_slug': series_slug,
        'series': series,
        'book_slug': book_slug,
        'book': book,
    }
    return render(request, 'book_detail.html', context)


def admin_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if username == "roshan" and password == "123456":
            request.session['admin_user'] = username
            return redirect("admin_dashboard")
        else:
            return render(request, "admin_login.html", {
                "error": "Invalid credentials"
            })

    return render(request, "admin_login.html")


def super_admin_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if username == "admin" and password == "admin789":
            request.session['is_super_admin'] = True
            return redirect("super_admin")
        else:
            return render(request, "super_admin_login.html", {
                "error": "Invalid credentials for Super Admin"
            })

    return render(request, "super_admin_login.html")


def super_admin_logout(request):
    if 'is_super_admin' in request.session:
        del request.session['is_super_admin']
    return redirect("super_admin_login")


def admin_dashboard(request):
    if not request.session.get('admin_user'):
        return redirect('admin_login')
    
    # Fetch all purchases for the Purchase Info section
    from .models import PurchaseItems, School, Books
    from django.db.models import Count
    import json
    
    purchases = PurchaseItems.objects.all().select_related('purchase__school', 'book').order_by('-purchase__purchase_date')
    
    # ---- Analytics & Metrix ----
    total_schools = School.objects.count()
    total_books_assigned = purchases.count()
    
    # Advanced Series Popularity (Pie Chart)
    series_distribution = PurchaseItems.objects.values('book__series_name').annotate(
        count=Count('id')
    ).order_by('-count')
    
    series_labels = [s['book__series_name'] for s in series_distribution if s['book__series_name']]
    series_data = [s['count'] for s in series_distribution if s['book__series_name']]
    
    # Recent Assignment Trends (Line Chart)
    date_trends = PurchaseItems.objects.values('purchase__purchase_date').annotate(
        count=Count('id')
    ).order_by('purchase__purchase_date')
    
    trend_labels = [d['purchase__purchase_date'].strftime("%Y-%m-%d") for d in date_trends if d['purchase__purchase_date']]
    trend_data = [d['count'] for d in date_trends if d['purchase__purchase_date']]

    # Search and Pagination for the Table
    from django.core.paginator import Paginator
    from django.db.models import Q
    
    table_purchases = purchases
    search_query = request.GET.get('search', '').strip()
    if search_query:
        table_purchases = table_purchases.filter(
            Q(purchase__school__school_name__icontains=search_query) |
            Q(purchase__school__school_id__icontains=search_query) |
            Q(book__series_name__icontains=search_query)
        )
        
    # Group by school
    grouped_purchases = {}
    for p in table_purchases:
        school = p.purchase.school
        if school.school_id not in grouped_purchases:
            grouped_purchases[school.school_id] = {
                'school_id': school.school_id,
                'school_name': school.school_name,
                'series': {}
            }
        
        series_name = p.book.series_name
        class_val = p.book.class_field
        
        if series_name not in grouped_purchases[school.school_id]['series']:
            grouped_purchases[school.school_id]['series'][series_name] = []
            
        if class_val not in grouped_purchases[school.school_id]['series'][series_name]:
            grouped_purchases[school.school_id]['series'][series_name].append(class_val)
            
    grouped_list = list(grouped_purchases.values())
    for item in grouped_list:
        for series in item['series']:
            item['series'][series].sort(key=lambda x: str(x))
            
    paginator = Paginator(grouped_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # All schools for autocomplete
    schools_data = list(School.objects.values('school_id', 'school_name', 'branch'))
    
    context = {
        'page_obj': page_obj,
        'total_schools': total_schools,
        'total_books_assigned': total_books_assigned,
        'series_labels': json.dumps(series_labels),
        'series_data': json.dumps(series_data),
        'trend_labels': json.dumps(trend_labels),
        'trend_data': json.dumps(trend_data),
        'schools_autocomplete': json.dumps(schools_data)
    }

    return render(request, 'admin_dashboard.html', context)


@require_POST
def delete_purchase(request, pk):
    """Admin deletes a purchase record."""
    if not request.session.get('admin_user'):
        return JsonResponse({'success': False, 'error': 'Not authenticated'}, status=403)
    
    try:
        from .models import PurchaseItems
        deleted, _ = PurchaseItems.objects.filter(id=pk).delete()
        if deleted == 0:
            return JsonResponse({'success': False, 'error': 'Record not found'})
            
        return JsonResponse({'success': True, 'message': 'Purchase record deleted successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_POST
def delete_school_purchases_admin(request, school_id):
    """Admin deletes all purchase records for a specific school."""
    if not request.session.get('admin_user'):
        return JsonResponse({'success': False, 'error': 'Not authenticated'}, status=403)
    
    try:
        from .models import Purchase, PurchaseItems
        purchases = Purchase.objects.filter(school__school_id=school_id)
        count = 0
        for p in purchases:
            items_deleted, _ = PurchaseItems.objects.filter(purchase=p).delete()
            count += items_deleted
        # Optinally delete the Purchase parents too
        purchases.delete()
        
        return JsonResponse({'success': True, 'message': f'Deleted {count} books assigned to this school.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_POST
def assign_books(request):
    """Admin assigns selected books to a school → creates Purchase records."""
    if not request.session.get('admin_user'):
        return JsonResponse({'success': False, 'error': 'Not authenticated'}, status=403)

    school_id = request.POST.get('school_id', '').strip()
    book_ids = request.POST.getlist('book_ids')  # list of book_id values

    if not school_id:
        return JsonResponse({'success': False, 'error': 'School ID is required'})
    if not book_ids:
        return JsonResponse({'success': False, 'error': 'No books selected'})

    # Validate school exists
    try:
        school = School.objects.get(school_id=school_id)
    except School.DoesNotExist:
        return JsonResponse({'success': False, 'error': f'School with ID "{school_id}" not found'})

    # Validate books exist
    valid_books = Books.objects.filter(book_id__in=book_ids)
    if not valid_books.exists():
        return JsonResponse({'success': False, 'error': 'None of the selected books were found in the database'})

    # Create purchase records (using raw SQL since table is managed=False)
    purchase_id = f"p-{date.today().strftime('%d%m%y')}-{school_id}"
    valid_upto = date.today() + timedelta(days=365)
    created_count = 0

    with connection.cursor() as cursor:
        # Ensure a parent purchase record exists or create one
        cursor.execute("SELECT purchase_id FROM purchase WHERE purchase_id = %s", [purchase_id])
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO purchase (purchase_id, school_id, purchase_date) VALUES (%s, %s, %s)",
                [purchase_id, school_id, date.today()]
            )

        for book in valid_books:
            # Check if this school already has this book
            cursor.execute(
                """
                SELECT COUNT(*) FROM purchase_items pi
                JOIN purchase p ON p.purchase_id = pi.purchase_id
                WHERE p.school_id = %s AND pi.book_id = %s
                """,
                [school_id, book.book_id]
            )
            if cursor.fetchone()[0] == 0:
                cursor.execute(
                    "INSERT INTO purchase_items (purchase_id, book_id, valid_upto, sent_to_school) VALUES (%s, %s, %s, TRUE)",
                    [purchase_id, book.book_id, valid_upto]
                )
                created_count += 1
            else:
                # Book already exists for this school, just mark it as sent
                cursor.execute(
                    """
                    UPDATE purchase_items SET sent_to_school = TRUE
                    FROM purchase
                    WHERE purchase_items.purchase_id = purchase.purchase_id
                    AND purchase.school_id = %s AND purchase_items.book_id = %s
                    """,
                    [school_id, book.book_id]
                )
                created_count += 1

    skipped = len(book_ids) - created_count
    msg = f"Successfully assigned {created_count} book(s) to {school.school_name}."
    if skipped > 0:
        msg += f" ({skipped} already assigned, skipped)"

    return JsonResponse({'success': True, 'message': msg, 'created': created_count})



from .forms import SchoolForm, BookForm
from django.shortcuts import get_object_or_404
from django.contrib import messages

@super_admin_required
def delete_purchase_super(request, pk):
    try:
        from .models import PurchaseItems
        deleted, _ = PurchaseItems.objects.filter(id=pk).delete()
        if deleted > 0:
            messages.success(request, 'Purchase record deleted successfully.')
        else:
            messages.error(request, 'Purchase record not found.')
    except Exception as e:
        messages.error(request, f'Failed to delete purchase record: {str(e)}')
    return redirect('super_admin')

@super_admin_required
def assign_purchase_super(request):
    if request.method == "POST":
        purchase_id = request.POST.get('purchase_id')
        school_id = request.POST.get('school_id')
        book_id = request.POST.get('book_id')
        valid_upto_str = request.POST.get('valid_upto')

        if not all([purchase_id, school_id, book_id, valid_upto_str]):
            messages.error(request, "All fields are required.")
            return redirect('super_admin')

        try:
            from datetime import datetime
            valid_upto = datetime.strptime(valid_upto_str, '%Y-%m-%d').date()
            school = School.objects.get(school_id=school_id)
            book = Books.objects.get(book_id=book_id)

            from django.db import connection
            with connection.cursor() as cursor:
                # 1. Check if the purchase_id exists, create if not
                cursor.execute("SELECT purchase_id FROM purchase WHERE purchase_id = %s", [purchase_id])
                if not cursor.fetchone():
                    cursor.execute(
                        "INSERT INTO purchase (purchase_id, school_id, purchase_date) VALUES (%s, %s, %s)",
                        [purchase_id, school_id, date.today()]
                    )

                # 2. Add item to purchase_items (sent_to_school=FALSE, admin must send it)
                cursor.execute(
                    "INSERT INTO purchase_items (purchase_id, book_id, valid_upto, sent_to_school) VALUES (%s, %s, %s, FALSE)",
                    [purchase_id, book_id, valid_upto]
                )
            messages.success(request, f"Successfully assigned book {book_id} to {school.school_name} (Purchase ID: {purchase_id}).")
        except School.DoesNotExist:
            messages.error(request, f"School with ID '{school_id}' not found.")
        except Books.DoesNotExist:
            messages.error(request, f"Book with ID '{book_id}' not found.")
        except Exception as e:
            messages.error(request, f"Database error occurred: {str(e)}")

    return redirect('super_admin')

@super_admin_required
def super_admin(request):
    from .models import School
    from django.db.models import Count
    from django.contrib.postgres.aggregates import StringAgg
    
    schools = School.objects.annotate(
        purchased_count=Count('purchase__purchaseitems__book__series_name', distinct=True),
        purchase_ids=StringAgg('purchase__purchase_id', delimiter=', ', distinct=True)
    )
    books = Books.objects.all()
    
    # Group books by series for the Series table
    series_data = {}
    for book in books:
        if book.series_name not in series_data:
            series_data[book.series_name] = {
                'name': book.series_name,
                'books': [],
                'classes': set()
            }
        series_data[book.series_name]['books'].append(book)
        series_data[book.series_name]['classes'].add(book.class_field)
    
    # Format series data for template
    formatted_series = []
    for s_name, data in series_data.items():
        classes_list = sorted(list(data['classes']))
        class_range = f"Class {classes_list[0]} - {classes_list[-1]}" if classes_list else "N/A"
        formatted_series.append({
            'name': s_name,
            'books': data['books'],
            'count': len(data['books']),
            'class_range': class_range
        })

    # Fetch all purchases for the new Purchase Management table
    from .models import PurchaseItems
    purchases = PurchaseItems.objects.all().select_related('purchase__school', 'book').order_by('-purchase__purchase_date')

    context = {
        'series': formatted_series,
        'books': books,
        'schools': schools,
        'purchases': purchases,
        'school_form': SchoolForm(),
        'book_form': BookForm(),
    }
    return render(request, "super_admin.html", context)

# --- School CRUD Direct Database ---
@super_admin_required
def add_school(request):
    if request.method == "POST":
        form = SchoolForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "School added successfully!")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error in {field}: {error}")
            messages.error(request, "Failed to add school. Please check your inputs.")
    return redirect('super_admin')

@super_admin_required
def edit_school(request, pk):
    from .models import School
    school = get_object_or_404(School, pk=pk)
    if request.method == "POST":
        form = SchoolForm(request.POST, instance=school)
        if form.is_valid():
            form.save()
            messages.success(request, "School updated successfully!")
    return redirect('super_admin')

@super_admin_required
def delete_school(request, pk):
    from .models import School, Purchase, PurchaseItems
    
    # Since foreign keys are DO_NOTHING and managed=False, manually delete associated records 
    # to prevent a new school with the same ID from inheriting ghost purchases
    purchases = Purchase.objects.filter(school_id=pk)
    for p in purchases:
        PurchaseItems.objects.filter(purchase=p).delete()
    purchases.delete()
    
    School.objects.filter(school_id=pk).delete()
    messages.success(request, "School and associated records deleted successfully!")
    return redirect('super_admin')

# --- CRUD for Book ---
@super_admin_required
def add_book(request):
    if request.method == "POST":
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Book added successfully!")
    return redirect('super_admin')

@super_admin_required
def edit_book(request, pk):
    book = get_object_or_404(Books, pk=pk)
    if request.method == "POST":
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, "Book updated successfully!")
    return redirect('super_admin')

@super_admin_required
def delete_book(request, pk):
    book = get_object_or_404(Books, pk=pk)
    book.delete()
    messages.success(request, "Book deleted successfully!")
    return redirect('super_admin')


def admin_logout(request):
    request.session.flush()
    return redirect("admin_login")

def request_demo(request):
    if request.method == "POST":
        contact_name = request.POST.get("contact_name")
        organization = request.POST.get("organization")
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        message_text = request.POST.get("message")

        message = f"""
New Demo Request – SAMSEL

Contact Person: {contact_name}
Organization   : {organization}
Phone Number   : {phone}
Email          : {email}

Message / Requirement:
{message_text}
"""

        send_mail(
            subject="New Demo Request - SAMSEL",
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=["indhumurugan593@gmail.com"],
            #reply_to=[EMAIL_HOST_USER],   # 👈 IMPORTANT
            fail_silently=False,
        )

        return redirect("/#demo")

def generate_paper(request):
    if request.method == "POST":

        selected_chapters = request.POST.getlist("chapters")
        total_marks = request.POST.get("total_marks", 20)
        standard = request.POST.get("standard", "1")

        json_path = os.path.join(
            settings.BASE_DIR,
            "samsel_website",
            "data",
            "question_bank.json"
        )

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 🔑 IMPORTANT FIX: access the chapters list
        all_chapters = data["chapters"]

        chosen_chapters = [
            ch for ch in all_chapters
            if str(ch["chapter_id"]) in selected_chapters
        ]

        paper = generate_question_paper(chosen_chapters, total_marks=total_marks, standard=standard)
        paper['standard'] = standard

        return render(request, "generated_paper.html", {
            "paper": paper
        })

def download_paper_pdf(request):
    json_path = os.path.join(
        settings.BASE_DIR,
        "samsel_website",
        "data",
        "question_bank.json"
    )

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    chapters = data["chapters"]
    total_marks = request.GET.get("marks", 20)
    standard = request.GET.get("standard", "1")
    paper = generate_question_paper(chapters, total_marks=total_marks, standard=standard)
    paper['standard'] = standard

    html = render_to_string("generated_paper.html", {"paper": paper})

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="question_paper_{total_marks}_marks.pdf"'
    )

    pisa.CreatePDF(html, dest=response)
    return response