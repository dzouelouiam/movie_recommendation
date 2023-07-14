from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
#from django.contrib.auth.models import User 
from django.contrib.auth import authenticate, login, logout
#from django.contrib.auth.forms import UserCreationForm
from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm, MyUserCreationForm
from base import data
import numpy as np 
import pandas as pd 
from sklearn.feature_extraction.text import TfidfVectorizer
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import linear_kernel
# Create your views here.

#rooms = [
 #   {'id' : 1, 'name' : 'action'},
  #  {'id' : 2, 'name' : 'adventure'},
   # {'id' : 3, 'name' : 'drama'},
#]

def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        #we get the username and password
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        #we check if the user exist
        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, "User does not exist")

        #we check if correct

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
             messages.error(request, "Email or Password does not exist")

            
    context = {'page': page}
    return render(request,'base/login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    form = MyUserCreationForm()
    #we pass in the user data
    if request.method == 'POST' : 
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            #we get the username and we make sure that the username is lowercase
            user.username = user.username.lower()
            #we save the user
            user.save()
            #we log the user in
            #user that just registred we're going to log them and send them to home page
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, ' Your password must have at least 8 characters long 1 uppercase & 1 lowercase character 1 number ')

    return render(request,'base/login_register.html',{'form' : form})

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q) 

    )
    #icontains = To search for all products whose name contains a word like ho its horror 
    topics = Topic.objects.all()[0:5]
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))

    context = {'rooms': rooms, 'topics': topics,
    'room_count': room_count, 'room_messages': room_messages}
    return render(request, 'base/home.html',context )

@login_required(login_url='login')
def room(request,pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()

    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)
    
    context = {'room': room, 'room_messages': room_messages, 
    'participants': participants}
    return render(request, 'base/room.html',context)
    


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user': user, 'rooms':rooms, 
        'room_messages': room_messages, 'topics': topics}
    return render(request, 'base/profile.html', context)




@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic,created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )
       # form = RoomForm(request.POST)
        #if form.is_valid():
          # room = form.save(commit = False)
          # room.host = request.user
         # room.save()
        return redirect('home')

    context={'form': form, 'topics': topics, 'room':room}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    if request.user != room.host:
        return HttpResponse('You are not allowed here!!')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic,created = Topic.objects.get_or_create(name=topic_name)
        #form = RoomForm(request.POST, instance=room)
        #if form.is_valid():
        #   form.save()
        room.name= request.POST.get('name')
        room.topic= topic
        room.description= request.POST.get('description')
        room.save()
        return redirect('home')

    context = {'form': form, 'topics': topics }
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('You are not allowed here!!')

    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': room})

@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('You are not allowed here!!')

    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': message})

@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)

    return render(request, 'base/update-user.html', {'form': form})



def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    return render(request,'base/topics.html', {'topics': topics})



def activityPage(request):
    room_messages = Message.objects.all()
    return render(request, 'base/activity.html', {'room_messages':room_messages})


# Reading ratings file
ratings = pd.read_csv('/Users/dzouelouiam/Downloads/RecSystem/ratings.csv', sep='\t', encoding='latin-1', usecols=['user_id', 'movie_id', 'rating'])

# Reading users file
users = pd.read_csv('/Users/dzouelouiam/Downloads/RecSystem/users.csv', sep='\t', encoding='latin-1', usecols=['user_id', 'gender', 'zipcode', 'age_desc', 'occ_desc'])

# Reading movies file
movies = pd.read_csv('/Users/dzouelouiam/Downloads/moviesup.csv', sep='\t', encoding='latin-1', usecols=['movie_id', 'title', 'genres','image'])

def moviesPage(request):
    
    movies_head = movies.head(50)  # Get the first 50 rows of the DataFrame
    users_head = users.head(50)  # Get the first 50 rows of the DataFrame
    ratings_head = ratings.head(50)  # Get the first 50 rows of the DataFrame
    context = {
        'movies': movies_head.to_dict(orient='records') , # Convert DataFrame rows to a list of dictionaries
        'users': users_head.to_dict(orient='records'),  # Convert DataFrame rows to a list of dictionaries
        'ratings': ratings_head.to_dict(orient='records')  # Convert DataFrame rows to a list of dictionaries
    }

    return render(request, 'base/moviesPage.html', context)


def recommendation(request):
        recommendation = []
        movie_title = request.POST.get('movie.title')
        dataset = pd.merge(pd.merge(movies, ratings),users)
    # Break up the big genre string into a string array
        movies['genres'] = movies['genres'].str.split('|')
# Convert genres to string value
        movies['genres'] = movies['genres'].fillna("").astype('str')
        tf = TfidfVectorizer(analyzer='word',ngram_range=(1, 2),min_df=0, stop_words='english')
        tfidf_matrix = tf.fit_transform(movies['genres'])
        cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
    # Build a 1-dimensional array with movie titles
        titles = movies['title']
        images = movies['image']
        indices = pd.Series(movies.index, index=movies['title'])
    # Function that get movie recommendations based on the cosine similarity score of movie genres
        def genre_recommendations(title):
            idx = indices[title]
            sim_scores = list(enumerate(cosine_sim[idx]))
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
            sim_scores = sim_scores[1:21]
            movie_indices = [i[0] for i in sim_scores]
            recommendations = []
            for index in movie_indices:
                recommendation = {'title': titles.iloc[index], 'image': images.iloc[index]}
                recommendations.append(recommendation)
            return recommendations
        # Call your recommendation algorithm using the clicked movie title
        recommendation = genre_recommendations(movie_title)
        print(recommendation)
    
        context = {
            'recommendations': recommendation,
            'images': [rec['image'] for rec in recommendation]
        }
        return render(request, 'base/recommendation.html',context)


def searchByTitle(request):
    if request.method == 'POST':
        search_title = request.POST.get('search_title')
        print(search_title)
        
        if search_title:
            # Filter movies by title using a case-insensitive match
            search_results = movies[movies['title'].str.contains(search_title, case=False)]
        else:
            search_results = movies
        
        context = {
            'movies': search_results.to_dict(orient='records'),
            'search_title': search_title
        }

        return render(request, 'base/resultsByTitle.html', context)

    else:
        movies_head = movies.head(10)  # Get the first 10 rows of the DataFrame

        context = {
            'movies': movies_head.to_dict(orient='records'),
            'search_title': ''  # Set initial search_title value as empty string
        }

        return render(request, 'base/resultsByTitle.html', context)
    
    
def searchByGenre(request):
    if request.method == 'POST':
        search_genre= request.POST.get('search_genre')
        print(search_genre)
        
        if search_genre:
            # Filter movies by title using a case-insensitive match
            search_results = movies[movies['genres'].str.contains(search_genre, case=False)]
        else:
            search_results = movies
        
        context = {
            'movies': search_results.to_dict(orient='records'),
            'search_genre': search_genre
        }

        return render(request, 'base/moviesPage.html', context)

    else:
        movies_head = movies.head(10)  # Get the first 10 rows of the DataFrame

        context = {
            'movies': movies_head.to_dict(orient='records'),
            'search_genre': ''  # Set initial search_title value as empty string
        }

        return render(request, 'base/resultsByGenre.html', context)