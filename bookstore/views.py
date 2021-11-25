

from django.shortcuts import redirect, render
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views import generic
from bootstrap_modal_forms.mixins import PassRequestMixin
from .models import User, Book, Chat, DeleteRequest, Feedback
from django.contrib import messages
from django.db.models import Sum
from django.views.generic import CreateView, DetailView, DeleteView, UpdateView, ListView
from .forms import ChatForm, BookForm
from . import models
import operator
import itertools
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import authenticate, logout
from django.contrib import auth, messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils import timezone




# Shared Views
def login_form(request):
	return render(request, 'bookstore/login.html')


def logoutView(request):
	logout(request)
	return redirect('home')


def loginView(request):
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(request, username=username, password=password)
		if user is not None and user.is_active:
			auth.login(request, user)
			if user.is_superuser:
				return redirect('dashboard')
			else:
			    return redirect('student')
		else:
		    messages.info(request, "Invalid username or password")
		    return redirect('home')


def register_form(request):
	return render(request, 'bookstore/register.html')


def registerView(request):
	if request.method == 'POST':
		username = request.POST['username']
		email = request.POST['email']
		password = request.POST['password']
		password = make_password(password)

		a = User(username=username, email=email, password=password)
		a.save()
		messages.success(request, 'Account was created successfully')
		return redirect('home')
	else:
	    messages.error(request, 'Registration fail, try again later')
	    return redirect('regform')



















			


# Student views
@login_required
def student(request):
	return render(request, 'student/home.html')


@login_required
def uabook_form(request):
	return render(request, 'student/add_book.html')


@login_required
def request_form(request):
	return render(request, 'student/delete_request.html')


@login_required
def feedback_form(request):
	return render(request, 'student/send_feedback.html')

@login_required
def about(request):
	return render(request, 'student/about.html')	


@login_required
def usearch(request):
    query = request.GET['query']
    print(type(query))


    #data = query.split()
    data = query
    print(len(data))
    if( len(data) == 0):
        return redirect('student')
    else:
                a = data

                # Searching for It
                qs5 =models.Book.objects.filter(id__iexact=a).distinct()
                qs6 =models.Book.objects.filter(id__exact=a).distinct()

                qs7 =models.Book.objects.all().filter(id__contains=a)
                qs8 =models.Book.objects.select_related().filter(id__contains=a).distinct()
                qs9 =models.Book.objects.filter(id__startswith=a).distinct()
                qs10 =models.Book.objects.filter(id__endswith=a).distinct()
                qs11 =models.Book.objects.filter(id__istartswith=a).distinct()
                qs12 =models.Book.objects.all().filter(id__icontains=a)
                qs13 =models.Book.objects.filter(id__iendswith=a).distinct()




                files = itertools.chain(qs5, qs6, qs7, qs8, qs9, qs10, qs11, qs12, qs13)

                res = []
                for i in files:
                    if i not in res:
                        res.append(i)


                # word variable will be shown in html when user click on search button
                word="Searched Result :"
                print("Result")

                print(res)
                files = res




                page = request.GET.get('page', 1)
                paginator = Paginator(files, 10)
                try:
                    files = paginator.page(page)
                except PageNotAnInteger:
                    files = paginator.page(1)
                except EmptyPage:
                    files = paginator.page(paginator.num_pages)
   


                if files:
                    return render(request,'student/result.html',{'files':files,'word':word})
                return render(request,'student/result.html',{'files':files,'word':word})



@login_required
def delete_request(request):
	if request.method == 'POST':
		book_id = request.POST['delete_request']
		current_user = request.user
		user_id = current_user.id
		username = current_user.username
		user_request = username + "  want book with id  " + book_id + " to be deleted"

		a = DeleteRequest(delete_request=user_request)
		a.save()
		messages.success(request, 'Request was sent')
		return redirect('request_form')
	else:
	    messages.error(request, 'Request was not sent')
	    return redirect('request_form')



@login_required
def send_feedback(request):
	if request.method == 'POST':
		feedback = request.POST['feedback']
		current_user = request.user
		user_id = current_user.id
		username = current_user.username
		feedback = username + " " + " says " + feedback

		a = Feedback(feedback=feedback)
		a.save()
		messages.success(request, 'Feedback was sent')
		return redirect('feedback_form')
	else:
	    messages.error(request, 'Feedback was not sent')
	    return redirect('feedback_form')

class UBookListView(LoginRequiredMixin,ListView):
	model = Book
	template_name = 'student/book_list.html'
	context_object_name = 'books'
	paginate_by = 2

	def get_queryset(self):
		return Book.objects.order_by('-id')

@login_required
def uabook(request):
	if request.method == 'POST':
		title = request.POST['title']
		author = request.POST['author']
		year = request.POST['year']
		publisher = request.POST['publisher']
		desc = request.POST['desc']
		cover = request.FILES['cover']
		pdf = request.FILES['pdf']
		current_user = request.user
		user_id = current_user.id
		username = current_user.username

		a = Book(title=title, author=author, year=year, publisher=publisher, 
			desc=desc, cover=cover, pdf=pdf, uploaded_by=username, user_id=user_id)
		a.save()
		messages.success(request, 'Book was uploaded successfully')
		return redirect('student')
	else:
	    messages.error(request, 'Book was not uploaded successfully')
	    return redirect('uabook_form')	


# Admin views

def dashboard(request):
	book = Book.objects.all().count()
	user = User.objects.all().count()

	context = {'book':book, 'user':user}

	return render(request, 'dashboard/home.html', context)



class ADeleteUser(SuccessMessageMixin, DeleteView):
    model = User
    template_name='dashboard/confirm_delete_user.html'
    success_url = reverse_lazy('aluser')
    success_message = "Data successfully deleted"


class ListUserView(generic.ListView):
    model = User
    template_name = 'dashboard/list_users.html'
    context_object_name = 'users'
    paginate_by = 4

    def get_queryset(self):
        return User.objects.order_by('-id')



class ALViewUser(DetailView):
    model = User
    template_name='dashboard/user_detail.html'


@login_required
def aabook_form(request):
	return render(request, 'dashboard/add_book.html')


@login_required
def aabook(request):
	if request.method == 'POST':
		title = request.POST['title']
		author = request.POST['author']
		year = request.POST['year']
		publisher = request.POST['publisher']
		desc = request.POST['desc']
		cover = request.FILES['cover']
		pdf = request.FILES['pdf']
		current_user = request.user
		user_id = current_user.id
		username = current_user.username

		a = Book(title=title, author=author, year=year, publisher=publisher, 
			desc=desc, cover=cover, pdf=pdf, uploaded_by=username, user_id=user_id)
		a.save()
		messages.success(request, 'Book was uploaded successfully')
		return redirect('albook')
	else:
	    messages.error(request, 'Book was not uploaded successfully')
	    return redirect('aabook_form')


class ABookListView(LoginRequiredMixin,ListView):
	model = Book
	template_name = 'dashboard/book_list.html'
	context_object_name = 'books'
	paginate_by = 3

	def get_queryset(self):
		return Book.objects.order_by('-id')




class AManageBook(LoginRequiredMixin,ListView):
	model = Book
	template_name = 'dashboard/manage_books.html'
	context_object_name = 'books'
	paginate_by = 3

	def get_queryset(self):
		return Book.objects.order_by('-id')




class ADeleteBook(LoginRequiredMixin,DeleteView):
	model = Book
	template_name = 'dashboard/confirm_delete_book.html'
	success_url = reverse_lazy('ambook')
	success_message = 'Data was deleted successfully'


class ADeleteBookk(LoginRequiredMixin,DeleteView):
	model = Book
	template_name = 'dashboard/confirm_delete_book.html'
	success_url = reverse_lazy('dashboard')
	success_message = 'Data was deleted successfully'


class AViewBook(LoginRequiredMixin,DetailView):
	model = Book
	template_name = 'dashboard/book_detail.html'




class AEditView(LoginRequiredMixin,UpdateView):
	model = Book
	form_class = BookForm
	template_name = 'dashboard/edit_book.html'
	success_url = reverse_lazy('ambook')
	success_message = 'Data was updated successfully'




class ADeleteRequest(LoginRequiredMixin,ListView):
	model = DeleteRequest
	template_name = 'dashboard/delete_request.html'
	context_object_name = 'feedbacks'
	paginate_by = 3

	def get_queryset(self):
		return DeleteRequest.objects.order_by('-id')



class AFeedback(LoginRequiredMixin,ListView):
	model = Feedback
	template_name = 'dashboard/feedback.html'
	context_object_name = 'feedbacks'
	paginate_by = 3

	def get_queryset(self):
		return Feedback.objects.order_by('-id')



@login_required
def asearch(request):
    query = request.GET['query']
    print(type(query))


    #data = query.split()
    data = query
    print(len(data))
    if( len(data) == 0):
        return redirect('dashborad')
    else:
                a = data

                # Searching for It
                qs5 =models.Book.objects.filter(id__iexact=a).distinct()
                qs6 =models.Book.objects.filter(id__exact=a).distinct()

                qs7 =models.Book.objects.all().filter(id__contains=a)
                qs8 =models.Book.objects.select_related().filter(id__contains=a).distinct()
                qs9 =models.Book.objects.filter(id__startswith=a).distinct()
                qs10 =models.Book.objects.filter(id__endswith=a).distinct()
                qs11 =models.Book.objects.filter(id__istartswith=a).distinct()
                qs12 =models.Book.objects.all().filter(id__icontains=a)
                qs13 =models.Book.objects.filter(id__iendswith=a).distinct()




                files = itertools.chain(qs5, qs6, qs7, qs8, qs9, qs10, qs11, qs12, qs13)

                res = []
                for i in files:
                    if i not in res:
                        res.append(i)


                # word variable will be shown in html when user click on search button
                word="Searched Result :"
                print("Result")

                print(res)
                files = res




                page = request.GET.get('page', 1)
                paginator = Paginator(files, 10)
                try:
                    files = paginator.page(page)
                except PageNotAnInteger:
                    files = paginator.page(1)
                except EmptyPage:
                    files = paginator.page(paginator.num_pages)
   


                if files:
                    return render(request,'dashboard/result.html',{'files':files,'word':word})
                return render(request,'dashboard/result.html',{'files':files,'word':word})


















