from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import render
from django.views import generic
from django.views.generic import ListView

from .models import Book, Author, BookInstance


class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 2

    def get_context_data(self, **kwargs):
        context = super(AuthorListView, self).get_context_data(**kwargs)
        return context

class AuthorDetailView(generic.DetailView):
    model = Author

    def author_detail_view(request, pk):
        try:

            author_id = Author.objects.get(pk=pk)
        except Author.DoesNotExist:
            raise Http404("Автора не существует")

        return render(
            request,
            'catalog/author_detail.html',
            context={"Автор": author_id}
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['books'] = Book.objects.filter(author=self.object)
        return context

class BookListView(generic.ListView):
    model = Book
    paginate_by = 2

    def get_context_data(self, **kwargs):
        context = super(BookListView, self).get_context_data(**kwargs)
        context['some_data'] = 'This is just some data'
        return context

class BookDetailView(generic.DetailView):
    model = Book

    def book_detail_view(request, pk):
        try:
            book_id = Book.objects.get(pk=pk)
        except Book.DoesNotExist:
            raise Http404("Книги не существует")

        return render(
            request,
            'catalog/book_detail.html',
            context={"book": book_id}
        )

def index(request):

    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    num_authors = Author.objects.count()

    search_word = request.GET.get('search_word','')
    search_word_lower = search_word.lower()

    if search_word:
        book_count = Book.objects.filter(title__icontains=search_word_lower).count()
    else:
        book_count = 0

    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    return render(
        request,
        'index.html',
        context={'num_books': num_books, 'num_instances': num_instances,
                 'num_instances_available': num_instances_available, 'num_authors': num_authors,
                 'num_visits': num_visits, 'book_count': book_count, 'search_word': search_word},
    )
from django.contrib.auth.mixins import PermissionRequiredMixin

class LoanedBooksAllListView(PermissionRequiredMixin, ListView):
    model = BookInstance
    permission_required = 'catalog.can_mark_returned'
    template_name = 'catalog/bookinstance_list_borrowed_all.html'
    paginate_by = 4

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')



class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')



from django.contrib.auth.decorators import permission_required

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime

from .forms import RenewBookForm

@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):

    book_inst = get_object_or_404(BookInstance, pk=pk)

    if request.method == 'POST':

        form = RenewBookForm(request.POST)

        if form.is_valid():

            book_inst.due_back = form.cleaned_data['renewal_date']
            book_inst.save()

            return HttpResponseRedirect(reverse('all-borrowed') )

    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date,})

    return render(request, 'catalog/book_renew_librarian.html', {'form': form, 'bookinst':book_inst})

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Author

class AuthorCreate(CreateView):
    model = Author
    fields = '__all__'
    initial={'date_of_death':'12/10/2016',}

class AuthorUpdate(UpdateView):
    model = Author
    fields = ['first_name','last_name','date_of_birth','date_of_death']

class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')

from .models import Book

class BookCreate(CreateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre']

class BookUpdate(UpdateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre']

class BookDelete(DeleteView):
    model = Book
    success_url = reverse_lazy('books')