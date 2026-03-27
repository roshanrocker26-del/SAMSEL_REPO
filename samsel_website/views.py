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

def reviews_page(request):
    return render(request, 'reviews.html')

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
        'title': 'IBOT SERIES',
        'description': "Shaping Future Innovators in AI and Robotics. A comprehensive collection of 9 titles, the iBot series is designed to equip students with future-ready skills in AI, robotics, and programming. Covering the latest AI and robotics syllabus, the series also introduces core programming concepts in C, C++, HTML5, and Python, building a strong technical foundation for learners. For higher classes, students explore advanced topics such as cybersecurity, emerging technologies, wireless networking, and IoT, helping them stay aligned with the evolving digital world. At the primary level, the series focuses on strengthening logical thinking through algorithms, flowcharts, and hands-on coding using ScratchJr and Scratch 3.0. With a well-structured, progressive approach, the iBot series ensures a seamless learning journey to empower students at every stage to understand, apply, and excel in AI, robotics, and programming languages.",
        'books': {
            'class-1': {'title': 'IBOT Class 1', 'image': 'images/ibot1.jpg', 'desc': 'Introduces young learners to smart machines, basic computer parts, and early coding concepts using ScratchJr.'},
            'class-2': {'title': 'IBOT Class 2', 'image': 'images/ibot2.jpg', 'desc': 'Building on basics, exploring input/output devices, and intermediate creative projects.'},
            'class-3': {'title': 'IBOT Class 3', 'image': 'images/ibot3.jpg', 'desc': 'Understanding OS environments, word processing, and an introduction to computational thinking.'},
            'class-4': {'title': 'IBOT Class 4', 'image': 'images/ibot4.jpg', 'desc': 'Advanced word processing, safe internet browsing, and block-based programming exercises.'},
            'class-5': {'title': 'IBOT Class 5', 'image': 'images/ibot5.jpg', 'desc': 'Presentations, spreadsheets basics, and developing algorithms using visual coding tools.'},
            'class-6': {'title': 'IBOT Class 6', 'image': 'images/ibot6.jpg', 'desc': 'Deep dive into robotics principles, electronics basics, and intro to Python syntax.'},
            'class-7': {'title': 'IBOT Class 7', 'image': 'images/ibot7.jpg', 'desc': 'AI concepts, intermediate Python programming, and hardware integration projects.'},
            'class-8': {'title': 'IBOT Class 8', 'image': 'images/ibot8.jpg', 'desc': 'Advanced robotics, IoT fundamentals, and machine learning basics.'},
            'class-9': {'title': 'IBOT Class 9', 'image': 'images/ibot9.jpg', 'desc': 'Comprehensive IT matrix, app development, and specialized AI/ML problem solving.'},
        }
    },
    'ismart-series': {
        'title': 'ISMART SERIES',
        'description': "A comprehensive digital literacy program designed to bridge the gap between traditional learning and modern technology. The i-Smart series provides students with a solid foundation in essential IT skills, from basic computer operations to advanced system design and web technologies. Each level is carefully structured to build core competencies through interactive exercises, creative software exploration, and structured logic development, ensuring students are well-equipped for the digital challenges of the 21st century.",
        'books': {
            'level-1': {'title': 'ISMART Level 1', 'image': 'images/low 1 - Copy.png', 'desc': 'Foundations of smart learning and digital literacy.'},
            'level-2': {'title': 'ISMART Level 2', 'image': 'images/low 2.png', 'desc': 'Interactive exercises building core IT competencies.'},
            'level-3': {'title': 'ISMART Level 3', 'image': 'images/low 3.png', 'desc': 'Exploring creative software and basic problem solving.'},
            'level-4': {'title': 'ISMART Level 4', 'image': 'images/low 4.png', 'desc': 'Introduction to connected devices and cyber safety.'},
            'level-5': {'title': 'ISMART Level 5', 'image': 'images/low 5.png', 'desc': 'Advanced office tools and beginner coding loops.'},
            'level-6': {'title': 'ISMART Level 6', 'image': 'images/high 6.png', 'desc': 'Structuring ideas and intermediate algorithmic logic.'},
            'level-7': {'title': 'ISMART Level 7', 'image': 'images/high 7.png', 'desc': 'Web technologies and introductory networking.'},
            'level-8': {'title': 'ISMART Level 8', 'image': 'images/high 8.png', 'desc': 'Data handling, analysis, and programming constructs.'},
            'level-9': {'title': 'ISMART Level 9', 'image': 'images/high 9.png', 'desc': 'Comprehensive system design and applied technology projects.'},
        }
    },
    'iwhizz-series': {
        'title': 'I-WHIZZ SERIES',
        'description': "A versatile and practical computing series that focuses on the real-world application of technology and logical thinking. The i-Whizz series empowers students to master software applications, explore the digital world safely, and develop strong analytical skills. From early steps in tech to comprehensive studies in modern computing architectures, this series provides a seamless learning path that emphasizes hands-on experience and structured logic building.",
        'books': {
            'class-1': {'title': 'i-Whizz Class 1', 'image': 'images/iwhizz1.jpg', 'desc': 'Early steps into the world of tech and logic.'},
            'class-2': {'title': 'i-Whizz Class 2', 'image': 'images/iwhizz2.jpg', 'desc': 'Building foundational computer operation skills.'},
            'class-3': {'title': 'i-Whizz Class 3', 'image': 'images/iwhizz3.jpg', 'desc': 'Logical puzzles and introducing digital creativity.'},
            'class-4': {'title': 'i-Whizz Class 4', 'image': 'images/iwhizz4.jpg', 'desc': 'Word processing and exploring the internet safely.'},
            'class-5': {'title': 'i-Whizz Class 5', 'image': 'images/iwhizz5.jpg', 'desc': 'Presentation tools and beginning programming principles.'},
            'class-6': {'title': 'i-Whizz Class 6', 'image': 'images/iwhizz6.jpg', 'desc': 'Deeper dive into software apps and coding techniques.'},
            'class-7': {'title': 'i-Whizz Class 7', 'image': 'images/iwhizz7.jpg', 'desc': 'Advanced digital tools and structured logic building.'},
            'class-8': {'title': 'i-Whizz Class 8', 'image': 'images/iwhizz8.jpg', 'desc': 'Web design basics and advanced conceptual frameworks.'},
            'class-9': {'title': 'i-Whizz Class 9', 'image': 'images/iwhizz9.jpg', 'desc': 'Comprehensive studies in modern computing architectures.'},
        }
    },
    'young-wizard-series': {
        'title': 'YOUNG WIZARD SERIES',
        'description': 'Magical computing foundations for young curious minds.',
        'books': {
            'level-1': {'title': 'Young Wizard Level 1', 'image': 'images/young1.jpg', 'desc': 'Magical introduction to computers.'},
            'level-2': {'title': 'Young Wizard Level 2', 'image': 'images/young2.jpg', 'desc': 'Exploring creative tech tools.'},
            'level-3': {'title': 'Young Wizard Level 3', 'image': 'images/young3.jpg', 'desc': 'Building logic through fun exercises.'},
            'level-4': {'title': 'Young Wizard Level 4', 'image': 'images/young4.jpg', 'desc': 'Intermediate magical computing tasks.'},
            'level-5': {'title': 'Young Wizard Level 5', 'image': 'images/young5.jpg', 'desc': 'Advanced puzzles and digital mastery.'},
        }
    },
    'little-wizard-series': {
        'title': 'LITTLE WIZARD SERIES',
        'description': 'Early childhood computing basics for LKG and UKG.',
        'books': {
            'level-1': {'title': 'Little Wizard Level 1', 'image': 'images/Kids level 1 wrapper.jpg', 'desc': 'Colorful shapes and mouse control.'},
            'level-2': {'title': 'Little Wizard Level 2', 'image': 'images/Kids level 2 wrapper.jpg', 'desc': 'Typing games and early logic.'},
        }
    },
    'app2016-series': {
        'title': 'APPLICATION SERIES 2016',
        'description': 'Mastering modern office applications with the 2016 suite.',
        'books': {
            'ppt': {'title': 'PowerPoint 2016', 'image': 'images/2016 ppt.png', 'desc': 'Create stunning presentations with modern tools.'},
            'excel': {'title': 'Excel 2016', 'image': 'images/2016 excel.png', 'desc': 'Data analysis, charting, and advanced functions.'},
            'word': {'title': 'Word 2016', 'image': 'images/2016 word.png', 'desc': 'Professional document creation and formatting.'},
        }
    },
    'app2007-series': {
        'title': 'APPLICATION SERIES 2007',
        'description': 'Comprehensive guide to the classic Office 2007 suite.',
        'books': {
            'level-1': {'title': 'App Series 2007 Level 1', 'image': 'images/App1.jpg', 'desc': 'Foundations of Office 2007 applications.'},
            'level-2': {'title': 'App Series 2007 Level 2', 'image': 'images/App2.jpg', 'desc': 'Intermediate skills in Word and Excel formatting.'},
            'level-3': {'title': 'App Series 2007 Level 3', 'image': 'images/App3.jpg', 'desc': 'Advanced presentations and formulas.'},
            'level-4': {'title': 'App Series 2007 Level 4', 'image': 'images/App4.jpg', 'desc': 'Database management introduction.'},
            'level-5': {'title': 'App Series 2007 Level 5', 'image': 'images/App5.jpg', 'desc': 'Mastering the Office 2007 suite.'},
        }
    },
    'programming-series': {
        'title': 'PROGRAMMING SERIES',
        'description': 'Step-by-step programming curriculum from basics to advanced OOP.',
        'books': {
            'level-1': {'title': 'Programming Level 1', 'image': 'images/Pro1 New.jpg', 'desc': 'The fundamentals of coding and syntax.'},
            'level-2': {'title': 'Programming Level 2', 'image': 'images/Pro2.jpg', 'desc': 'Data structures and algorithms introduction.'},
            'level-3': {'title': 'Programming Level 3', 'image': 'images/Pro3.jpg', 'desc': 'Object-oriented concepts and design.'},
            'level-4': {'title': 'Programming Level 4', 'image': 'images/Pro4 New.jpg', 'desc': 'Advanced applied programming techniques.'},
        }
    },
    'my-computer-series': {
        'title': 'MY COMPUTER SERIES',
        'description': 'Foundational computer knowledge and system maintenance.',
        'books': {
            'level-1': {'title': 'My Computer Level 1', 'image': 'images/my1.jpg', 'desc': 'Exploring your first PC.'},
            'level-2': {'title': 'My Computer Level 2', 'image': 'images/my2.jpg', 'desc': 'Handling files and folders safely.'},
            'level-3': {'title': 'My Computer Level 3', 'image': 'images/my3.jpg', 'desc': 'Navigating operating systems.'},
            'level-4': {'title': 'My Computer Level 4', 'image': 'images/my4.jpg', 'desc': 'Settings, customization, and tools.'},
            'level-5': {'title': 'My Computer Level 5', 'image': 'images/my5.jpg', 'desc': 'System maintenance and troubleshooting.'},
        }
    },
    'right-click-series': {
        'title': 'RIGHT-CLICK SERIES (i-ICT)',
        'description': 'Information and Communication Technology for secondary levels.',
        'books': {
            'level-6': {'title': 'i-ICT Level 6', 'image': 'images/ict6.jpg', 'desc': 'Information and Communication Tech basics.'},
            'level-7': {'title': 'i-ICT Level 7', 'image': 'images/ict7.jpg', 'desc': 'Networks and data communication.'},
            'level-8': {'title': 'i-ICT Level 8', 'image': 'images/ict8.jpg', 'desc': 'Applied IT systems in the real world.'},
            'level-9': {'title': 'i-ICT Level 9', 'image': 'images/ict9.jpg', 'desc': 'Comprehensive technology integration.'},
        }
    },
    'cursive-writing-books': {
        'title': 'ENGLISH CURSIVE WRITING',
        'description': 'Master the art of elegant penmanship with our structured cursive writing series.',
        'books': {
            'lkg': {'title': 'Cursive Writing LKG', 'image': 'images/cursive-lkg.jpg', 'desc': 'Introduction to strokes and basic patterns.'},
            'ukg': {'title': 'Cursive Writing UKG', 'image': 'images/cursive-ukg.jpg', 'desc': 'Building letter forms and simple connections.'},
            'level-1': {'title': 'Cursive Writing Level 1', 'image': 'images/cursive1.jpg', 'desc': 'Fluid word formation and sentence structure.'},
            'level-2': {'title': 'Cursive Writing Level 2', 'image': 'images/cursive2.jpg', 'desc': 'Advanced penmanship and consistent spacing.'},
            'level-3': {'title': 'Cursive Writing Level 3', 'image': 'images/cursive3.jpg', 'desc': 'Perfecting the elegant cursive script.'},
            'level-4': {'title': 'Cursive Writing Level 4', 'image': 'images/cursive4.jpg', 'desc': 'Creative writing in professional cursive.'},
            'level-5': {'title': 'Cursive Writing Level 5', 'image': 'images/cursive5.jpg', 'desc': 'Mastery of decorative and formal penmanship.'},
        }
    },
    'tamil-writing-books': {
        'title': 'TAMIL COPY WRITING',
        'description': 'A beautiful journey into Tamil calligraphy and structured writing practice.',
        'books': {
            'level-1': {'title': 'Tamil Writing Level 1', 'image': 'images/tamil1.jpg', 'desc': 'Basic Tamil characters and stroke techniques.'},
            'level-2': {'title': 'Tamil Writing Level 2', 'image': 'images/tamil2.jpg', 'desc': 'Building words and understanding letter structures.'},
            'level-3': {'title': 'Tamil Writing Level 3', 'image': 'images/tamil3.jpg', 'desc': 'Intermediate word formation and sentence patterns.'},
            'level-4': {'title': 'Tamil Writing Level 4', 'image': 'images/tamil4.jpg', 'desc': 'Enhancing writing speed and letter consistency.'},
            'level-5': {'title': 'Tamil Writing Level 5', 'image': 'images/tamil5.jpg', 'desc': 'Advanced copy writing and literary phrases.'},
            'level-6': {'title': 'Tamil Writing Level 6', 'image': 'images/tamil6.jpg', 'desc': 'Perfecting the flow of Tamil script.'},
            'level-7': {'title': 'Tamil Writing Level 7', 'image': 'images/tamil7.jpg', 'desc': 'Mastery of formal Tamil calligraphy.'},
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