from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Bird, Location, Photo
from .forms import FeedingForm
import boto3
import uuid

S3_BASE_URL = 'https://s3.us-east-1.amazonaws.com/'
BUCKET = 'catcollector-pb-sei'

# Create your views here.
def home(request):
  return redirect('about')

def about(request):
  return render(request, 'about.html')

# Add new view
@login_required
def birds_index(request):
  birds = Bird.objects.filter(user=request.user)
  return render(request, 'birds/index.html', { 'birds': birds })

@login_required
def birds_detail(request,bird_id):
  bird = Bird.objects.get(id=bird_id)
  feeding_form = FeedingForm()
  locations_not_yet_registered = Location.objects.exclude(id__in = bird.locations.all().values_list('id'))
  return render(request, 'birds/detail.html', {'bird':bird, 'feeding_form': feeding_form, 'locations': locations_not_yet_registered})

class BirdCreate(LoginRequiredMixin, CreateView):
  model = Bird
  fields = ['name', 'breed', 'description', 'age']

  def form_valid(self, form):
    # Assign the logged in user (self.request.user)
    form.instance.user = self.request.user  # form.instance is the cat
    # Let the CreateView do its job as usual
    return super().form_valid(form)

class BirdUpdate(LoginRequiredMixin, UpdateView):
  model = Bird
  # Let's disallow the renaming of a Bird by excluding the name field!
  fields = ['breed', 'description', 'age']

class BirdDelete(LoginRequiredMixin, DeleteView):
  model = Bird
  success_url = '/birds/'

class BirdsList(LoginRequiredMixin, ListView):
  model = Bird

@login_required
def add_feeding(request, bird_id):
  form = FeedingForm(request.POST)
  if form.is_valid():
    new_feeding = form.save(commit=False)
    new_feeding.bird_id = bird_id
    new_feeding.save()
  return redirect('detail', bird_id=bird_id)

class LocationList(LoginRequiredMixin, ListView):
  model = Location

class LocationDetail(LoginRequiredMixin, DetailView):
  model = Location

class LocationCreate(LoginRequiredMixin, CreateView):
  model = Location
  fields = '__all__'
  success_url = '/locations/'

class LocationUpdate(LoginRequiredMixin, UpdateView):
  model = Location
  fields = ['name', 'address']
  success_url = '/locations/'

class LocationDelete(LoginRequiredMixin, DeleteView):
  model = Location
  success_url = '/locations/'

@login_required
def assoc_location(request, bird_id, location_id):
  # Note that you can pass a toy's id instead of the whole object
  Bird.objects.get(id=bird_id).locations.add(location_id)
  return redirect('detail', bird_id=bird_id)

@login_required
def remove_location(request, bird_id, location_id):
  # Note that you can pass a toy's id instead of the whole object
  Bird.objects.get(id=bird_id).locations.remove(location_id)
  return redirect('detail', bird_id=bird_id)

@login_required
def add_photo(request, bird_id):
    # photo-file will be the "name" attribute on the <input type="file">
    photo_file = request.FILES.get('photo-file', None)
    if photo_file:
        s3 = boto3.client('s3')
        # need a unique "key" for S3 / needs image file extension too
        key = uuid.uuid4().hex[:6] + photo_file.name[photo_file.name.rfind('.'):]
        # just in case something goes wrong
        try: 
            s3.upload_fileobj(photo_file, BUCKET, key)
            # build the full url string
            url = f"{S3_BASE_URL}{BUCKET}/{key}"
            # we can assign to cat_id or cat (if you have a cat object)
            photo = Photo(url=url, bird_id=bird_id)
            photo.save()
        except Exception as err:
          print(err)
          print('An error occurred uploading file to S3')
    return redirect('detail', bird_id=bird_id)

def signup(request):
  error_message = ''
  if request.method == 'POST':
    # This is how to create a 'user' form object
    # that includes the data from the browser
    form = UserCreationForm(request.POST)
    if form.is_valid():
      # This will add the user to the database
      user = form.save()
      # This is how we log a user in via code
      login(request, user)
      return redirect('index')
    else:
      error_message = 'Invalid sign up - try again'
  # A bad POST or a GET request, so render signup.html with an empty form
  form = UserCreationForm()
  context = {'form': form, 'error_message': error_message}
  return render(request, 'registration/signup.html', context)